# Milestone 8: Redis Caching and API Optimization

Redis caches admin statistics/search, company dashboard counts and approved student drive listings for 300 seconds. Authentication is never cached. Relevant cache keys are cleared after approvals, drive changes, application changes and account activation changes. If Redis is unavailable, APIs safely use SQLite.

`get_cache`, `set_cache` and `clear_cache` are in `backend/cache.py`. Cached endpoints can be compared by calling the same GET twice while Redis is running; the second call avoids SQL queries.

Viva questions: What is cache? Why expiry? Why invalidate? Why not cache login? What happens if Redis stops? Answers: temporary fast copy, freshness, prevent stale data, security, graceful database fallback.

Live changes: change expiry to 60 seconds; cache another read-only statistics endpoint.
