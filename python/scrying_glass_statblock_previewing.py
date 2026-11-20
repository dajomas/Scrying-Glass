"""Statblock preview for Add Monster before the monster exists (SG-TODO-022.15).

``POST /api/statblocks/preview`` takes the signed lookup selection the Add
Monster form holds (``selection_token``) and its species. The selection's exact
source identity (the same ``monster_source_*`` fields Add Monster would store) is
prepared in the shared scheduler and isolated workers; the job is followed with
the existing ``/api/statblocks/jobs/{id}`` routes and its completed payload
carries the preview. Nothing is stored: a preview is not a selection and cannot
be applied. The conversion cache makes the statblock collected after the add
(``scrying_glass_statblock_collecting``) reuse the same preparation. One preview
per session at a time; a new one cancels the previous one.
"""
from __future__ import annotations

from .scrying_glass_statblock_contract import StatblockAPIError
from .scrying_glass_statblock_discovery import original_identity
from .scrying_glass_statblock_jobs import Job, JobCapacity

PREVIEW_UNAVAILABLE = frozenset(('not_found', 'statblock_unavailable', 'selected_unavailable', 'identity_mismatch'))


class PreviewingMixin:
    def _read_selection(self, token, species):
        """-> source fields of a signed Add Monster selection; ValueError when expired or invalid."""
        from .scrying_glass_monster_selection import selected_snapshot
        return selected_snapshot(token, species)[1]

    def preview_begin(self, principal, body):
        if (type(body) is not dict or set(body) != {'selection_token', 'species'}
                or type(body['selection_token']) is not str or type(body['species']) is not str
                or not 1 <= len(body['species'].strip()) <= 100):
            raise StatblockAPIError(422, 'invalid_request', 'Expected selection_token and species.')
        try:
            fields = self._read_selection(body['selection_token'], body['species'].strip())
        except ValueError:
            raise StatblockAPIError(410, 'selection_expired',
                                    'The monster selection expired; repeat the lookup.') from None
        config = self.config()
        original = original_identity(fields, config) if fields else None
        if original is None:
            raise StatblockAPIError(422, 'no_source', 'This monster was not chosen from a statblock source.')
        provider, identity = original
        if not config.enabled.get(provider):
            raise StatblockAPIError(409, 'provider_disabled', f'{provider} is disabled.')
        self._purge_jobs()
        with self._jobs_lock:
            previous = [job for job in self._jobs.values()
                        if job.owner == principal.session and job.info.get('preview') and not job.finished()]
        for job in previous:
            self.scheduler.cancel(job)
        info = {'preview': True, 'provider': provider, 'identity': identity, 'config': config, 'file_bytes': None}
        job = Job(principal.session, self._work, deadline=self.clock() + self.limits.preparation_seconds, info=info)
        try:
            self.scheduler.submit(job)
        except JobCapacity:
            raise StatblockAPIError(429, 'queue_full', 'Too many preparations are waiting; try again shortly.') from None
        with self._jobs_lock:
            self._jobs[job.id] = job
        return self._job_payload(job)

    def _preview_finished(self, job, state, result, error):
        """Scheduler callback: keep the validated snapshot on the job (never in the selection store)."""
        if state != 'completed':
            from .scrying_glass_statblock_contract import FAILURE_MESSAGES
            if error is not None and error[0] in FAILURE_MESSAGES:
                error = (error[0], FAILURE_MESSAGES[error[0]], None)
            elif error is not None:
                error = (error[0], error[1], None)
            return state, None, error
        from .scrying_glass_statblock_model import StatblockError, validate_snapshot
        import copy
        snapshot = copy.deepcopy(result['snapshot'])
        snapshot.pop('revision', None)
        try:
            snapshot = validate_snapshot(snapshot, self.limits.model())
        except StatblockError as exc:
            return 'failed', None, (exc.code, 'The statblock is not valid.', None)
        return state, {'preview': snapshot, 'source_label': snapshot['source_label'], 'source': self._source(snapshot),
                       'completeness': snapshot['completeness']}, error
