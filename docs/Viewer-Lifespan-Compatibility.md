# Campaign viewer startup compatibility

Campaign viewer ACL initialization uses an APIRouter lifespan context manager
included into each FastAPI application. It does not call app.add_event_handler
or app.on_event. FastAPI composes included-router lifespans with the application's
lifespan, so unrelated initialization/shutdown and yielded lifespan state remain
under FastAPI's management.

The initializer runs at application startup, not while routes are registered.
This matters because scrying_glass_server.py constructs its applications before
it initializes STORAGE. ACL initialization still runs under operation_lock; the
existing CampaignViewers.initialize method keeps database installation idempotent
when admin and client applications start using the same storage.

Only startup registration changed. Viewer grants, endpoint authorization,
same-origin checks, campaign selection and per-viewer data filtering are unchanged.
No additional schema migration or dependency is introduced by this correction.

## Tests

```sh
python -m unittest discover -s tests -p 'test_campaign_viewer_routes.py' -v
python -m unittest discover -s tests -p 'test_campaign_viewer_lifespan_integration.py' -v
```

The first suite deliberately gives its app double no add_event_handler/on_event
methods. It tests registration, lifespan entry/failure and existing route guards.
The second uses actual FastAPI apps to check lifespan composition and yielded
state preservation; it skips explicitly when FastAPI is unavailable. Run it in
the application's environment before treating lifecycle integration as verified.

Official lifecycle reference: https://fastapi.tiangolo.com/advanced/events/
Router reference: https://fastapi.tiangolo.com/reference/apirouter/
