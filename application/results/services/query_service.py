"""Read-only query service for results and summaries, used by the HTTP layer."""

from __future__ import annotations

from typing import Optional

from application.results.services.storage_client import ResultStorageClient
from infastructure import settings


class ResultsQueryService:
    """Thin orchestration layer between routers and storage/repository."""

    def __init__(self) -> None:
        self._storage = ResultStorageClient()

    # ------------------------------------------------------------------
    # Individual results (explorer)
    # ------------------------------------------------------------------

    def list_results(
        self,
        exam_type: str,
        year: Optional[int] = None,
        center: Optional[str] = None,
        subject: Optional[str] = None,
        sex: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[dict], int]:
        """Return a paginated list of aggregated result dicts and total count."""
        if exam_type.upper() == "ACSEE":
            cursor, total = self._storage.aggregated_acsee_results(
                year=year, center=center, subject=subject, sex=sex,
                page=page, page_size=page_size,
            )
        else:
            cursor, total = self._storage.aggregated_csee_results(
                year=year, center=center, subject=subject, sex=sex,
                page=page, page_size=page_size,
            )
        items = list(cursor) if cursor else []
        return items, total

    # ------------------------------------------------------------------
    # Summaries (multi-center comparison)
    # ------------------------------------------------------------------

    @staticmethod
    def _standardise_pass_rate(value) -> float:
        """Clamp a raw passRate value to [0.0, 1.0] with 4-decimal precision."""
        try:
            raw = float(value)
        except (TypeError, ValueError):
            return 0.0
        return round(min(max(raw, 0.0), 1.0), 4)

    @staticmethod
    def _compute_rank_scores(items: list[dict]) -> None:
        """Enrich each item with a rankScore that blends passRate and school size.

        rankScore = α × passRate + (1 - α) × (totalCandidates / maxCandidates)

        Schools with higher pass rates rank first; among similar pass rates,
        larger schools get precedence.  α comes from settings.PASS_RATE_ALPHA.
        """
        if not items:
            return

        alpha = settings.PASS_RATE_ALPHA

        max_candidates = max(
            (item.get("totalCandidates", 0) for item in items), default=1
        )
        if max_candidates <= 0:
            max_candidates = 1

        for item in items:
            pass_rate = item.get("passRate", 0.0)
            total = item.get("totalCandidates", 0)
            normalised_size = total / max_candidates
            item["rankScore"] = round(
                alpha * pass_rate + (1 - alpha) * normalised_size, 4
            )

    def list_summaries(
        self,
        exam_type: str,
        year: Optional[int] = None,
        center_id: Optional[str] = None,
        region: Optional[str] = None,
        sort_by: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[dict], int]:
        """Return a paginated list of summary dicts and total count."""
        if exam_type.upper() == "ACSEE":
            cursor, total = self._storage.get_all_acsee_centers_results_summary(
                year=year, center_id=center_id, region=region,
                sort_by=sort_by, page=page, page_size=page_size,
            )
        else:
            cursor, total = self._storage.get_all_csee_centers_results_summary(
                year=year, center_id=center_id, region=region,
                sort_by=sort_by, page=page, page_size=page_size,
            )
        items = list(cursor) if cursor else []

        # Ensure every summary carries a standardised passRate in [0.0, 1.0]
        for item in items:
            item["passRate"] = self._standardise_pass_rate(item.get("passRate"))

        # Compute composite rank score (passRate + school-size bias)
        self._compute_rank_scores(items)

        # Re-sort by rankScore when sorting by pass rate is requested
        if sort_by and sort_by.lower() == "passrate":
            items.sort(key=lambda x: x.get("rankScore", 0.0), reverse=True)

        return items, total

    # ------------------------------------------------------------------
    # All-years aggregated summaries (one record per center)
    # ------------------------------------------------------------------

    def list_all_years_summaries(
        self,
        exam_type: str,
        region: Optional[str] = None,
        sort_by: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[dict], int]:
        """Return summaries aggregated across all years, one record per center.
        Each year's passRate is computed individually, then averaged for the overall."""
        cursor, total = self._storage.get_all_years_summary(
            exam_type=exam_type, region=region,
            sort_by=sort_by, page=page, page_size=page_size,
        )
        items = list(cursor) if cursor else []

        # Standardise overall passRate to [0.0, 1.0]
        for item in items:
            item["passRate"] = self._standardise_pass_rate(item.get("passRate"))
            # Also standardise each year's passRate in the breakdown
            for year_entry in item.get("yearlyBreakdown", []):
                year_entry["passRate"] = self._standardise_pass_rate(year_entry.get("passRate"))

        # Compute composite rank score (passRate + school-size bias)
        self._compute_rank_scores(items)

        # Re-sort by rankScore when sorting by pass rate is requested
        if sort_by and sort_by.lower() == "passrate":
            items.sort(key=lambda x: x.get("rankScore", 0.0), reverse=True)

        return items, total

    # ------------------------------------------------------------------
    # Meta helpers
    # ------------------------------------------------------------------

    def get_available_years(self, exam_type: str) -> list[int]:
        """Merge distinct years from both results and summary collections."""
        result_years = set(self._storage.get_distinct_result_years(exam_type))
        summary_years = set(self._storage.get_distinct_summary_years(exam_type))
        return sorted(result_years | summary_years)

