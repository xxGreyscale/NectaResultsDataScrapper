from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone

from pymongo.database import Database
from typing import cast

from adopter.api.export_service import process_export
from adopter.api.job_queue import claim_next_job, mark_job_complete, mark_job_failed
from infastructure import settings
from infastructure.database_config import get_database
from usecases.get_necta_results import get_and_save_acsee_results, get_and_save_csee_results


def _delete_results(db: Database, exam_type: str, years: list[int]) -> None:
    if exam_type == "ACSEE":
        db["necta_acsee_results"].delete_many({"current.year": {"$in": years}})
        db["acsee_result_summary"].delete_many({"year": {"$in": years}})
    elif exam_type == "CSEE":
        db["necta_csee_results"].delete_many({"current.year": {"$in": years}})
        db["csee_result_summary"].delete_many({"year": {"$in": years}})


def _run_results_job(exam_type: str, years: list[int], source_url: str) -> dict:
    years_list = cast(list[int], years)
    if exam_type == "ACSEE":
        get_and_save_acsee_results(source_url, "ACSEE", years_list)
    elif exam_type == "CSEE":
        get_and_save_csee_results(source_url, "CSEE", years_list)
    else:
        raise ValueError(f"Unknown exam type: {exam_type}")
    return {"examType": exam_type, "years": years_list}


def handle_job(db: Database, job: dict) -> dict:
    payload = job
    job_type = payload.get("type")
    exam_type = payload.get("examType")
    years = payload.get("years") or []
    source_url = payload.get("sourceUrl") or settings.SCHEDULER_SOURCE_URL

    if job_type == "full_rebuild":
        _delete_results(db, exam_type, years)
        return _run_results_job(exam_type, years, source_url)
    if job_type == "results":
        return _run_results_job(exam_type, years, source_url)
    if job_type == "export_results":
        return process_export(db, "results_acsee" if exam_type == "ACSEE" else "results_csee")
    if job_type == "export_summaries":
        return process_export(db, "summaries_acsee" if exam_type == "ACSEE" else "summaries_csee")

    raise ValueError(f"Unsupported job type: {job_type}")


def worker_loop(worker_id: str, poll_interval: int) -> None:
    db = get_database(settings.MONGO_URI, settings.DB_NAME)
    while True:
        job = claim_next_job(db, worker_id)
        if not job:
            time.sleep(poll_interval)
            continue
        job_id = job.get("_id")

        # Respect cancellation that arrived between enqueue and claim
        fresh = db["jobs"].find_one({"_id": job_id})
        if fresh and fresh.get("status") == "cancelled":
            print(f"[{datetime.now(timezone.utc).isoformat()}] job {job_id} was cancelled, skipping")
            continue

        try:
            result = handle_job(db, job)
            mark_job_complete(db, job_id, progress=result)
        except Exception as exc:
            mark_job_failed(db, job_id, str(exc))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NECTA job worker")
    parser.add_argument("--worker-id", required=True)
    parser.add_argument("--poll-interval", type=int, default=5)
    args = parser.parse_args()

    print(f"[{datetime.now(timezone.utc).isoformat()}] starting worker {args.worker_id}")
    worker_loop(args.worker_id, args.poll_interval)
