from __future__ import annotations

import math
from typing import Any

from adopter.api.models import ErrorDetail, ErrorResponse, PaginationMeta, SuccessResponse


def pagination_meta(
    page: int = 1,
    page_size: int = 50,
    total_items: int | None = None,
    # keep legacy compat -------
    limit: int | None = None,
    count: int | None = None,
) -> dict:
    """Build a pagination meta dict.

    Supports both the new (page/pageSize) and legacy (limit/count) call styles.
    """
    _page = page
    _page_size = limit if limit is not None else page_size
    _total = count if count is not None else total_items
    _total_pages = math.ceil(_total / _page_size) if _total is not None and _page_size else None
    return {
        "pagination": PaginationMeta(
            page=_page,
            pageSize=_page_size,
            totalItems=_total,
            totalPages=_total_pages,
        ).model_dump()
    }


def success_response(data: Any, meta: dict | None = None) -> SuccessResponse[Any]:
    return SuccessResponse(data=data, meta=meta)


def error_response(errors: list[ErrorDetail], meta: dict | None = None) -> ErrorResponse:
    return ErrorResponse(errors=errors, meta=meta)
