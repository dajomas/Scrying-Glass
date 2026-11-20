"""Bounded, fair statblock preparation jobs (SG-TODO-022.08).

- ``active_jobs`` preparations run at once (each in its own isolated worker
  process, started by the job's work function); ``queued_jobs`` more may wait.
  A full queue rejects new work explicitly; nothing is evicted.
- Waiting jobs are served round-robin by owner (one owner per session), so a
  bulk import cannot monopolize the queue.
- A job's deadline starts at acceptance: queue time consumes it. A job still
  queued at its deadline fails with ``deadline`` without running.
- Cancelling a queued job removes it; a running job sees ``cancelled()`` and
  its worker is stopped. A cancelled or expired job never produces a result.
"""
from __future__ import annotations

import logging
import secrets
import threading
import time
from collections import OrderedDict, deque


class JobCapacity(Exception):
    pass


class Job:
    """States: queued -> running -> completed | failed | cancelled."""

    def __init__(self, owner, work, *, deadline, info=None):
        self.id = secrets.token_urlsafe(24)
        self.owner, self.work, self.deadline = owner, work, deadline
        self.info = dict(info or {})
        self.state = 'queued'
        self.result = None
        self.error = None  # (code, message, retry_at)
        self.finished_at = None
        self._cancel = threading.Event()
        self.done = threading.Event()

    def cancelled(self):
        return self._cancel.is_set()

    def finished(self):
        return self.state in ('completed', 'failed', 'cancelled')


class JobScheduler:
    def __init__(self, *, active, queued, clock=time.monotonic, on_finish=None):
        self.active, self.queued, self.clock = active, queued, clock
        self.on_finish = on_finish
        self._cv = threading.Condition()
        self._queues = OrderedDict()  # owner -> deque(Job)
        self._waiting = 0
        self._running = set()
        self._threads = []
        self._stopped = False

    def counts(self):
        with self._cv:
            return {'running': len(self._running), 'queued': self._waiting}

    def submit(self, job):
        with self._cv:
            if self._stopped:
                raise JobCapacity('scheduler_stopped')
            if self._waiting >= self.queued:
                raise JobCapacity('queue_full')
            self._queues.setdefault(job.owner, deque()).append(job)
            self._waiting += 1
            self._threads = [thread for thread in self._threads if thread.is_alive()]
            while len(self._threads) < self.active:
                thread = threading.Thread(target=self._worker, name='statblock-preparation', daemon=True)
                self._threads.append(thread)
                thread.start()
            self._cv.notify()
        return job

    def cancel(self, job):
        """Cancel one job; returns True when it will never produce a result."""
        with self._cv:
            if job.finished():
                return job.state == 'cancelled'
            job._cancel.set()
            queue = self._queues.get(job.owner)
            if job.state == 'queued' and queue is not None and job in queue:
                queue.remove(job)
                self._waiting -= 1
                if not queue:
                    del self._queues[job.owner]
                self._finish(job, 'cancelled', None, ('cancelled', 'Preparation cancelled.', None))
            return True

    def stop(self):
        with self._cv:
            self._stopped = True
            for queue in self._queues.values():
                for job in queue:
                    job._cancel.set()
                    self._finish(job, 'cancelled', None, ('cancelled', 'Preparation cancelled.', None))
            self._queues.clear()
            self._waiting = 0
            for job in self._running:
                job._cancel.set()
            self._cv.notify_all()

    def _finish(self, job, state, result, error):
        """on_finish(job, state, result, error) may turn a result into the stored outcome."""
        if self.on_finish is not None:
            try:
                state, result, error = self.on_finish(job, state, result, error)
            except Exception:
                state, result, error = 'failed', None, ('preparation_failed', 'Preparation failed.', None)
        job.state, job.result, job.error = state, result, error
        job.finished_at = self.clock()
        job.done.set()

    def _next(self):
        owner, queue = next(iter(self._queues.items()))
        job = queue.popleft()
        del self._queues[owner]
        if queue:
            self._queues[owner] = queue  # back of the round-robin order
        self._waiting -= 1
        return job

    def _worker(self):
        while True:
            with self._cv:
                while not self._queues and not self._stopped:
                    self._cv.wait()
                if self._stopped:
                    return
                job = self._next()
                if self.clock() >= job.deadline:
                    self._finish(job, 'failed', None, ('deadline', 'The preparation deadline passed while queued.', None))
                    continue
                job.state = 'running'
                self._running.add(job)
            state, result, error = 'completed', None, None
            try:
                result = job.work(job)
            except Exception as exc:  # work functions translate their own failures
                code = getattr(exc, 'code', None) or 'preparation_failed'
                if code == 'preparation_failed':  # untranslated: keep the cause in the server log
                    logging.getLogger(__name__).exception('Statblock preparation failed unexpectedly')
                error = (code, getattr(exc, 'message', None) or 'Preparation failed.', getattr(exc, 'retry_at', None))
                state = 'failed'
            with self._cv:
                self._running.discard(job)
                if job.cancelled():
                    state, result, error = 'cancelled', None, ('cancelled', 'Preparation cancelled.', None)
                elif state == 'completed' and self.clock() >= job.deadline:
                    state, result, error = 'failed', None, ('deadline', 'The preparation deadline passed.', None)
                self._finish(job, state, result, error)
