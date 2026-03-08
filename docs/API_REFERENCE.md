# NECTA Analytics API – Endpoint Reference

> **Base URL:** `/v1`  
> **Response envelope:** All endpoints return `{ "data": ..., "meta": { "pagination": {...} } }` unless noted.

---

## Meta (filter dropdowns)

| Method | Path | Query Params | Description |
|--------|------|-------------|-------------|
| GET | `/meta/exam-types` | — | `["CSEE","ACSEE"]` |
| GET | `/meta/subjects/acsee` | — | ACSEE subject catalogue with abbreviations |
| GET | `/meta/subjects/csee` | — | CSEE subject catalogue with abbreviations |
| GET | `/meta/sex` | — | `["M","F","None"]` |
| GET | `/meta/years` | — | Available years per exam type |
| GET | `/meta/regions` | — | Distinct region values |
| GET | `/meta/councils` | `region?` | Distinct council values, optionally filtered by region |

---

## Centers

| Method | Path | Query Params | Description |
|--------|------|-------------|-------------|
| GET | `/centers` | `search?`, `region?`, `council?`, `page=1`, `pageSize=50` | Paginated, filterable center list |
| GET | `/centers/{necta_reg_no}` | — | Single center detail |
| GET | `/centers/{necta_reg_no}/performance` | `examType` (required), `year` (required) | Center KPIs: pass rate, candidate count, division distribution |

### Example – Center performance

```
GET /v1/centers/S0100/performance?examType=ACSEE&year=2022
```

```json
{
  "data": {
    "center": { "id": "...", "name": "...", "nectaRegNo": "S0100", ... },
    "year": 2022,
    "examType": "ACSEE",
    "candidatesCount": 120,
    "passRate": 0.8333,
    "divisionDistribution": {
      "divisionOne":   { "males": 5, "females": 5, "total": 10 },
      "divisionTwo":   { "males": 20, "females": 20, "total": 40 },
      "divisionThree": { "males": 15, "females": 15, "total": 30 },
      "divisionFour":  { "males": 10, "females": 10, "total": 20 },
      "divisionZero":  { "males": 3, "females": 2, "total": 5 },
      "absent":        { "males": 2, "females": 3, "total": 5 },
      ...
    }
  },
  "meta": null
}
```

---

## Results Explorer

| Method | Path | Query Params | Description |
|--------|------|-------------|-------------|
| GET | `/results/{exam_type}` | `year?`, `center?`, `subject?`, `sex?`, `page=1`, `pageSize=50` | Individual results with center details joined |

- `exam_type`: path param, `ACSEE` or `CSEE`
- `center`: NECTA registration number (e.g. `S0100`)
- `subject`: partial match on subject name
- `sex`: `M` or `F`

---

## Summaries (multi-center comparison)

| Method | Path | Query Params | Description |
|--------|------|-------------|-------------|
| GET | `/summaries/{exam_type}` | `year?`, `centerId?`, `region?`, `page=1`, `pageSize=50` | Division-level summaries per center |

- `centerId`: internal center UUID (not NECTA reg no)
- `region`: partial match filter

---

## Pagination

All paginated endpoints return:

```json
{
  "meta": {
    "pagination": {
      "page": 1,
      "pageSize": 50,
      "totalItems": 1234,
      "totalPages": 25
    }
  }
}
```

---

## Jobs & Exports (existing, unchanged)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/jobs` | Create a scraping/rebuild job |
| GET | `/jobs` | List jobs (filter by `status`) |
| GET | `/jobs/{job_id}` | Get job status |
| POST | `/exports/{export_type}` | Queue an export |
| GET | `/exports/{export_id}` | Get export status |

