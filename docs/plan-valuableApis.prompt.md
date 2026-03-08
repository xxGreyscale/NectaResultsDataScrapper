# NECTA API + Multi-Instance Plan

## Goals
- Expose valuable APIs mapped to current usecases/services.
- Support background collection jobs with idempotency and deduplication.
- Run multiple API instances and multiple workers safely and consistently.

## API Surface (v1)
### Ingestion / Jobs
- POST `/v1/jobs/results` - trigger collection; body: `{ examType, years[], sourceUrl?, priority? }`.
- GET `/v1/jobs/{jobId}` - job status, progress, error.
- GET `/v1/jobs` - filter by type/status/year/examType.
- POST `/v1/jobs/{jobId}/cancel` - best-effort cancel.

### Results
- GET `/v1/results/{examType}` - list results with filters: year, centerId, region, council, sex, division.
- GET `/v1/results/{examType}/{centerId}` - center results for a year.
- GET `/v1/results/{examType}/{year}/aggregate` - aggregated results (existing aggregation pipeline).

### Summaries
- GET `/v1/summaries/{examType}` - yearly summaries (from result_summary_repository).
- GET `/v1/summaries/{examType}/{year}` - summary for a year.
- GET `/v1/summaries/{examType}/{year}/{centerId}` - summary for a center.

### Centers
- GET `/v1/centers` - list centers, filters: region, council, ownership.
- GET `/v1/centers/{centerId}` - center details.
- GET `/v1/centers/{centerId}/results/{examType}` - center results by year.
- GET `/v1/centers/{centerId}/summaries/{examType}` - center summary by year.

### CSV Export
- POST `/v1/exports/results/{examType}` - generate results CSV (async job).
- POST `/v1/exports/summaries/{examType}` - generate summaries CSV (async job).
- GET `/v1/exports/{exportId}` - status + download URL.

### Utilities
- POST `/v1/parse/table` - parse HTML table payload (for debugging/QA).
- POST `/v1/extract/html` - fetch and extract tables from URL (admin).
- GET `/v1/meta/years` - available years.
- GET `/v1/meta/exam-types` - enum values.
- GET `/v1/health` - DB connectivity + uptime.

## Data Model Changes (MongoDB)
### Results
- Create unique index on `identifiers.index_number` for both ACSEE/CSEE collections.
- Consider compound index: `{ current.year, identifiers.index_number }` for faster year scans.

### Result Summaries
- Add unique index on `{ year, centerId }` per summary collection.
- Add index on `{ year }` for year queries.

### Jobs Collection
- `jobs` collection schema:
  - `_id`, `type`, `payload`, `status`, `priority`, `createdAt`, `updatedAt`.
  - `idempotencyKey`, `lockedBy`, `lockExpiresAt`, `progress`, `error`.
- Unique index on `idempotencyKey` to dedupe.
- TTL index on `lockExpiresAt` if desired for cleanup of abandoned locks.

### Exports Collection
- `exports` collection schema:
  - `_id`, `type`, `params`, `status`, `filePath`, `gridFsId`, `createdAt`, `updatedAt`, `error`.
- Unique index on `(type, params.year?, params.examType?)` if needed.

## Job Orchestration and Idempotency
- Use `idempotencyKey = hash(type + examType + years + sourceUrl)`.
- POST `/v1/jobs/results` performs upsert on `jobs` by `idempotencyKey`.
- Worker claims job via `findOneAndUpdate` with status `queued` and `lockExpiresAt` <= now.
- Worker updates `progress` and `status` (`running`, `completed`, `failed`).
- For dedupe of saved results, rely on unique index on `identifiers.index_number` and use ordered=false bulk insert or upsert.

## Multi-Instance Synchronization
- All instances share MongoDB; job locking ensures only one worker processes a job.
- Writes are idempotent due to unique indexes.
- Use versioned writes for summary docs if updates are expected.

## Worker Strategy
- Implement a separate worker process that polls `jobs`.
- Allow multiple workers: each claims jobs using atomic `findOneAndUpdate`.
- Use concurrency limits per worker instance (e.g., max 2 years at once).
- For scraping, add rate limits per host to avoid duplicate downloads.

## Export Storage
- Write CSVs to local disk and upload the same artifact into GridFS.
- Store both `filePath` and `gridFsId` in the `exports` collection.
- Provide download endpoints for disk and GridFS retrieval.

## Rebuild Strategy
- Use full rebuilds only; job type `full_rebuild` clears existing results/summary for the scope.
- Rebuild jobs run with exclusive locks to prevent concurrent writes.

## Scheduler
- Use an internal scheduler (in-process or sidecar) to enqueue jobs on a cadence.
- API exposes job submission and status; scheduler is bundled with the service.

## Implementation Steps
1. Add FastAPI app with routes mapped to existing usecases and storage clients.
2. Add Mongo indexes for dedupe and faster queries.
3. Implement `jobs` collection and worker claiming logic.
4. Wire background tasks to invoke `get_and_save_*` and CSV generators.
5. Add pagination, filtering, and structured error responses.
6. Add health and meta endpoints.
7. Add tests for job idempotency and multi-worker claiming.

## Testing and Observability
- Unit tests for job claim, dedupe, and result insert idempotency.
- Integration test: run two workers against same queue.
- Log job lifecycle and errors; expose metrics (jobs queued/running/failed).

## Open Questions
- None yet; external orchestrator and full rebuilds confirmed.
