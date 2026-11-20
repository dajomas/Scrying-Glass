"""Statblock preparation jobs for the service (SG-TODO-022.08): accept under the lock, convert in isolated workers."""
from __future__ import annotations

import copy
import hashlib
import json

from .scrying_glass_statblock_contract import (
    ADAPTERS, FAILURE_MESSAGES, SELECTION_ERRORS, PreparationFailure, StatblockAPIError, _iso, _now_iso,
)
from .scrying_glass_statblock_discovery import DNDBEYOND, FILE, FIVETOOLS, OPEN5E, hosts
from .scrying_glass_statblock_fetching import FetchFailure
from .scrying_glass_statblock_jobs import Job, JobCapacity
from .scrying_glass_statblock_limits import FAILED_JOB_RECORDS, FAILED_JOB_SECONDS, MONSTER_FILE_BYTES
from .scrying_glass_statblock_selections import SelectionError, session_key


class PreparingMixin:
    # -- preparation ---------------------------------------------------------------
    def prepare(self, principal, body, *, file_bytes=None, filename=None):
        if type(body) is not dict:
            raise StatblockAPIError(422, 'invalid_request', 'Expected a JSON object.')
        allowed = {'campaign_id', 'encounter_token', 'monster_id', 'expected_statblock_revision', 'candidate_id'}
        if set(body) - allowed:
            raise StatblockAPIError(422, 'invalid_request', 'Unexpected preparation fields.')
        self._check_campaign(principal, body.get('campaign_id'))
        self._check_encounter(principal, body.get('encounter_token'))
        monster = self._target(body.get('monster_id'))
        expected = body.get('expected_statblock_revision')
        if type(expected) is not int or expected < 0:
            raise StatblockAPIError(422, 'invalid_request', 'expected_statblock_revision must be a nonnegative integer.')
        if expected != self.revision(monster['id']):
            raise StatblockAPIError(409, 'stale_revision', 'The statblock changed; reload before importing.',
                                    items=[{'monster_id': monster['id'], 'code': 'stale_revision',
                                            'message': 'The statblock changed.'}])
        scope = self._scope(principal, body['encounter_token'], monster)
        config = self.config()
        if file_bytes is not None:
            if 'candidate_id' in body:
                raise StatblockAPIError(422, 'invalid_request', 'Choose either a candidate or a file.')
            if type(file_bytes) is not bytes or not file_bytes:
                raise StatblockAPIError(422, 'invalid_request', 'Choose a .monster file.')
            if len(file_bytes) > MONSTER_FILE_BYTES:
                raise StatblockAPIError(413, 'file_too_large', FAILURE_MESSAGES['file_too_large'])
            provider = FILE
            identity = {'sha256': hashlib.sha256(file_bytes).hexdigest(),
                        'filename': filename if type(filename) is str else None}
        else:
            try:
                candidate = self.store.candidate(body.get('candidate_id'), principal.session)
            except SelectionError as exc:
                self._raise_selection(exc, monster['id'])
            if not candidate.scope.same_target(scope):
                raise StatblockAPIError(409, 'candidate_mismatch',
                                        'The candidate belongs to another monster or encounter state; repeat discovery.',
                                        items=[{'monster_id': monster['id'], 'code': 'candidate_mismatch',
                                                'message': 'Repeat discovery.'}])
            provider, identity = candidate.provider, candidate.identity
            if not config.enabled.get(provider):
                raise StatblockAPIError(409, 'provider_disabled', f'{provider} is disabled.',
                                        items=[{'monster_id': monster['id'], 'code': 'provider_disabled',
                                                'message': f'{provider} is disabled.'}])
            if ((provider == FIVETOOLS and identity.get('root') != config.fivetools_root)
                    or (provider == OPEN5E and identity.get('base_url') != config.open5e_base)):
                raise StatblockAPIError(409, 'provider_configuration_changed',
                                        'The source configuration changed; repeat discovery.')
        try:
            self.store.reserve(principal.session)
        except SelectionError as exc:
            self._raise_selection(exc, monster['id'])
        self._purge_jobs()
        info = {'provider': provider, 'identity': identity, 'scope': scope, 'expected': expected,
                'token': principal.token, 'config': config, 'file_bytes': file_bytes}
        job = Job(principal.session, self._work, deadline=self.clock() + self.limits.preparation_seconds, info=info)
        try:
            self.scheduler.submit(job)
        except JobCapacity:
            self.store.release(principal.session)
            raise StatblockAPIError(429, 'queue_full', 'Too many preparations are waiting; try again shortly.',
                                    retry_at=_iso(self.wall() + 1)) from None
        with self._jobs_lock:
            self._jobs[job.id] = job
        return self._job_payload(job)

    def _work(self, job):
        info = job.info
        provider, identity, config = info['provider'], info['identity'], info['config']
        cache_key = None
        if provider != FILE:
            cache_key = (provider, json.dumps(identity, sort_keys=True), config.fingerprint(provider),
                         ADAPTERS[provider], self.limits.fingerprint())
            hit = self.shared.cached_conversion(cache_key)
            if hit is not None:
                return json.loads(hit)
        snapshot, measurements = self.runner(provider, identity, job, info.get('file_bytes'), config)
        result = {'snapshot': snapshot, 'measurements': measurements}
        if cache_key is not None:
            raw = json.dumps(result, ensure_ascii=False, separators=(',', ':')).encode()
            self.shared.store_conversion(cache_key, raw, len(raw))
        return result

    def _run_isolated(self, provider, identity, job, file_bytes, config):
        """Default runner: the adapters inside their prlimit-bounded child processes."""
        from .scrying_glass_fivetools_fetch import FetchError
        from .scrying_glass_fivetools_preparation import PreparationError
        from .scrying_glass_fivetools_worker import WorkerError
        from .scrying_glass_statblock_worker import SourceWorkerError, prepare_source_isolated
        fetch = self._fetch(config, job.cancelled)
        try:
            if provider == FIVETOOLS:
                from .scrying_glass_fivetools_preparation_worker import prepare_isolated
                root = identity['root']
                def path_fetch(path, *, deadline):
                    try:
                        return fetch(FIVETOOLS, f'{root}/{path}', deadline)
                    except FetchFailure as exc:
                        if exc.code in ('deadline', 'cancelled'):
                            raise WorkerError(exc.code) from None
                        raise FetchError(exc.code) from None
                return prepare_isolated(identity['name'], identity['source'], fetch=path_fetch, deadline=job.deadline,
                                        limits=self.limits.preparation(), cancelled=job.cancelled,
                                        worker_memory_bytes=self.limits.worker_memory_bytes, data_root=root,
                                        site='https://5e.tools')
            kind = {OPEN5E: 'open5e', DNDBEYOND: 'dndbeyond', FILE: 'file'}[provider]
            request = ({'key': identity['key'], 'base_url': identity['base_url']} if provider == OPEN5E else
                       {'path': identity['path']} if provider == DNDBEYOND else {'filename': identity.get('filename')})
            return prepare_source_isolated(kind, request, fetch=lambda url, deadline: fetch(provider, url, deadline),
                                           hosts=hosts(provider, config), deadline=job.deadline,
                                           limits=self.limits.model(), response_bytes=self.limits.response_bytes,
                                           worker_memory_bytes=self.limits.worker_memory_bytes,
                                           cancelled=job.cancelled, file_bytes=file_bytes)
        except (PreparationError, SourceWorkerError) as exc:
            raise PreparationFailure(exc.code) from None
        except WorkerError as exc:
            raise PreparationFailure(str(exc) or 'worker_internal_error') from None
        except FetchFailure as exc:
            raise PreparationFailure(exc.code, exc.retry_at) from None

    def _finished(self, job, state, result, error):
        """Scheduler callback: store a completed preparation as a private selection."""
        info = job.info
        if info.get('auto'):
            return self._auto_finished(job, state, result, error)
        if info.get('collect'):
            return self._collect_finished(job, state, result, error)
        scope = info['scope']
        file_bytes, info['file_bytes'] = info.get('file_bytes'), None
        if state != 'completed':
            self.store.release(scope.session)
            if error is not None and error[2] is not None:
                error = (error[0], error[1], _iso(self.wall() + max(0.0, error[2] - self.clock())))
            if error is not None and error[0] in FAILURE_MESSAGES:
                error = (error[0], FAILURE_MESSAGES[error[0]], error[2])
            return state, None, error
        if not self.context.SESSIONS.get(info['token']):
            self.store.release(scope.session)
            return 'failed', None, ('session_revoked', FAILURE_MESSAGES['session_revoked'], None)
        snapshot = copy.deepcopy(result['snapshot'])
        snapshot.pop('revision', None)
        snapshot['prepared_at'] = _now_iso()
        try:
            from .scrying_glass_statblock_model import StatblockError, validate_snapshot
            snapshot = validate_snapshot(snapshot, self.limits.model())
        except StatblockError as exc:
            self.store.release(scope.session)
            return 'failed', None, (exc.code, FAILURE_MESSAGES.get(exc.code, 'The statblock is not valid.'), None)
        source = self._source(snapshot)
        if file_bytes is not None and info['identity'].get('sha256') != hashlib.sha256(file_bytes).hexdigest():
            self.store.release(scope.session)
            return 'failed', None, ('identity_mismatch', 'The file changed during preparation.', None)
        summary = {'provider': info['provider'], 'source': source, 'source_label': snapshot['source_label'],
                   'completeness': snapshot['completeness']}
        try:
            binding = self.store.complete(scope, info['expected'], snapshot, summary)
        except SelectionError as exc:
            status, message = SELECTION_ERRORS.get(exc.code, (429, 'Capacity reached.'))
            return 'failed', None, (exc.code, message, None)
        warnings = [{'code': row['code'], 'message': row['message'], **({'source_path': row['source_path']}
                     if row.get('source_path') else {})} for row in snapshot['warnings']]
        return 'completed', {'selection_id': binding.id, 'expires_at': _iso(binding.expires_wall),
                             'monster_id': scope.monster_id, 'source': source,
                             'source_label': snapshot['source_label'], 'completeness': snapshot['completeness'],
                             'warnings': warnings, 'measurements': result.get('measurements')}, None

    def _job_payload(self, job):
        payload = {'job_id': job.id, 'status': job.state, 'monster_id': job.info['scope'].monster_id,
                   'provider': job.info['provider'],
                   'deadline': _iso(self.wall() + max(0.0, job.deadline - self.clock()))}
        if job.state == 'completed':
            payload.update(copy.deepcopy(job.result))
            # The preview is read from the shared prepared store, never duplicated per job.
            try:
                binding = self.store.binding(job.result['selection_id'], job.owner)
                payload['preview'] = self.store.snapshot(binding)
            except SelectionError:
                payload['selection_status'] = 'expired_or_used'
        elif job.error is not None:
            payload['error'] = {'code': job.error[0], 'message': job.error[1],
                                **({'retry_at': job.error[2]} if job.error[2] else {})}
        return payload

    def _job(self, principal, job_id):
        with self._jobs_lock:
            job = self._jobs.get(job_id) if type(job_id) is str else None
        if job is None or job.owner != principal.session:
            raise StatblockAPIError(404, 'job_not_found', 'Preparation not found.')
        return job

    def job_status(self, principal, job_id):
        self._purge_jobs()
        return self._job_payload(self._job(principal, job_id))

    def job_cancel(self, principal, job_id):
        job = self._job(principal, job_id)
        self.scheduler.cancel(job)
        if job.state == 'completed' and job.result:
            self.store.discard(job.result['selection_id'], principal.session)
            job.state, job.result, job.error = 'cancelled', None, ('cancelled', 'Preparation cancelled.', None)
        return self._job_payload(job)

    def _purge_jobs(self):
        now = self.clock()
        with self._jobs_lock:
            failed = []
            for ident, job in list(self._jobs.items()):
                if not job.finished():
                    continue
                keep = self.limits.selection_seconds if job.state == 'completed' else FAILED_JOB_SECONDS
                if job.finished_at is not None and now - job.finished_at >= keep:
                    del self._jobs[ident]
                elif job.state != 'completed':
                    failed.append(ident)
            for ident in failed[:-FAILED_JOB_RECORDS] if len(failed) > FAILED_JOB_RECORDS else []:
                self._jobs.pop(ident, None)

    def revoke_session(self, token):
        session = session_key(token)
        self.store.revoke_session(session)
        with self._jobs_lock:
            jobs = [job for job in self._jobs.values() if job.owner == session]
        for job in jobs:
            self.scheduler.cancel(job)

