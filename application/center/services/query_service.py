"""Read-only query service for centers, used by the HTTP layer."""

from __future__ import annotations

from typing import Optional

from application.center.repository.center_repository import CenterRepository
from application.center.services.center_mappers import CenterMapper
from application.results.services.storage_client import ResultStorageClient
from common.Enumerations.small_enumarations import DivisionEnum
from infastructure import settings


class CenterQueryService:
    """Thin orchestration layer between routers and storage/repository."""

    def __init__(self) -> None:
        self._center_repo = CenterRepository()
        self._center_mapper = CenterMapper()
        self._result_storage = ResultStorageClient()

    # ------------------------------------------------------------------
    # List / search
    # ------------------------------------------------------------------

    def list_centers(
        self,
        search: Optional[str] = None,
        region: Optional[str] = None,
        council: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[dict], int]:
        """Return serialisable center dicts and the total count."""
        docs, total = self._center_repo.search_centers(
            search=search, region=region, council=council,
            page=page, page_size=page_size,
        )
        centers = []
        for doc in docs:
            try:
                domain = self._center_mapper.to_domain(doc)
                centers.append(domain.to_dict())
            except Exception:
                # Gracefully skip malformed documents
                continue
        return centers, total

    # ------------------------------------------------------------------
    # Single center detail
    # ------------------------------------------------------------------

    def get_center(self, necta_reg_no: str) -> dict | None:
        raw = self._center_repo.get_center_by_necta_reg_no(necta_reg_no)
        if not raw:
            return None
        domain = self._center_mapper.to_domain(raw)
        return domain.to_dict()

    # ------------------------------------------------------------------
    # Center performance (aggregated)
    # ------------------------------------------------------------------

    def get_center_performance(
        self,
        necta_reg_no: str,
        exam_type: str,
        year: int,
    ) -> dict | None:
        """Compute KPIs for a single center / year / exam type.

        Uses the individual results collection so we can count divisions.
        """
        center = self.get_center(necta_reg_no)
        if not center:
            return None

        results = self._result_storage.get_results_for_center(
            exam_type=exam_type,
            center_reg_no=necta_reg_no,
            year=year,
        )

        # Count divisions from raw result documents
        division_counts: dict[str, dict[str, int]] = {}
        for div in DivisionEnum:
            division_counts[div.value] = {"males": 0, "females": 0, "total": 0}

        total_candidates = 0
        # Weighted score using global coefficients from settings.
        # Div 0, absent, withheld, etc. count as failure (weight 0).
        weighted_sum = 0

        for doc in results:
            current = doc.get("current", {})
            div_val = current.get("division")
            sex_val = current.get("sex")
            total_candidates += 1

            if div_val in division_counts:
                division_counts[div_val]["total"] += 1
                if sex_val == "M":
                    division_counts[div_val]["males"] += 1
                elif sex_val == "F":
                    division_counts[div_val]["females"] += 1

            weighted_sum += settings.DIVISION_WEIGHTS.get(div_val, 0)

        # Normalise to 0.0–1.0: all Div I → 1.0, all Div IV → 0.25, all failures → 0.0
        max_weight = settings.DIVISION_WEIGHT_I
        pass_rate = round(weighted_sum / (max_weight * total_candidates), 4) if total_candidates else 0.0

        return {
            "center": center,
            "year": year,
            "examType": exam_type.upper(),
            "candidatesCount": total_candidates,
            "passRate": pass_rate,
            "divisionDistribution": {
                "divisionOne": division_counts.get("I", {}),
                "divisionTwo": division_counts.get("II", {}),
                "divisionThree": division_counts.get("III", {}),
                "divisionFour": division_counts.get("IV", {}),
                "divisionZero": division_counts.get("0", {}),
                "absent": division_counts.get("ABS", {}),
                "resultWithheld": division_counts.get("*R", {}),
                "eStar": division_counts.get("*E", {}),
                "withdrawn": division_counts.get("*W", {}),
                "specialPass": division_counts.get("*S", {}),
            },
        }

    # ------------------------------------------------------------------
    # Helpers for meta / filters
    # ------------------------------------------------------------------

    def get_distinct_regions(self) -> list[str]:
        return self._center_repo.get_distinct_regions()

    def get_distinct_councils(self, region: Optional[str] = None) -> list[str]:
        return self._center_repo.get_distinct_councils(region)




