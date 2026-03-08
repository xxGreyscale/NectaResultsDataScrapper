# NECTA API

Minimal FastAPI service for NECTA data ingestion, results access, and exports.

## Quick start

```zsh
python -m pip install -r requirements.txt
uvicorn adopter.api.main:app --reload
```

## Worker

```zsh
python worker.py --worker-id worker-1 --poll-interval 5
```

## Scheduler

Internal scheduler is off by default. Enable with env vars:

```zsh
export NECTA_SCHEDULER_ENABLED=true
export NECTA_SCHEDULER_INTERVAL_SECONDS=3600
export NECTA_SCHEDULER_EXAM_TYPES=ACSEE,CSEE
export NECTA_SCHEDULER_YEARS=2022,2023,2024
uvicorn adopter.api.main:app --reload
```

## Mongo

Defaults use `mongodb://root:admin@localhost:27018/` and database `necta`.
Override with:

```zsh
export NECTA_MONGO_URI="mongodb://user:pass@host:27017/"
export NECTA_DB_NAME="necta"
```
