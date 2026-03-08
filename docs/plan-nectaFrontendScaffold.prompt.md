# Plan: NECTA Analytics Frontend Scaffold

> **Assumption:** The frontend lives in its own standalone repository / folder (e.g. `necta-frontend/`), completely independent of the Python backend. It communicates with the NECTA API exclusively over HTTP. Every API endpoint consumed is documented inline below so the frontend can be built without access to the backend source code.

Build a modern, interactive single-page application using **Next.js 14 (App Router)** + **TypeScript** + **Tailwind CSS** + **Framer Motion** that consumes every NECTA API endpoint. The site goes beyond a simple dashboard: it features a public landing page, an interactive results explorer, center deep-dive pages, multi-center comparison views, and an admin panel for jobs/exports — all with a minimal, inviting colour palette (soft whites, slate grays, and a teal/emerald accent) and smooth page/element animations.

---

## API Contract Reference

> **Base URL (env var `NEXT_PUBLIC_API_BASE`):** `http://localhost:8000/v1`
>
> **Response envelope** — all paginated endpoints return:
> ```jsonc
> { "data": T, "meta": { "pagination": { "page": 1, "pageSize": 50, "totalItems": 1234, "totalPages": 25 } } }
> ```
> Non-paginated endpoints return `{ "data": T, "meta": null }` or a bare value.

### A. Health

| # | Method | Path | Params | Response `data` |
|---|--------|------|--------|-----------------|
| A1 | `GET` | `/health` | — | `{ "status": "ok" }` |

### B. Meta (filter dropdowns)

| # | Method | Path | Query Params | Response `data` |
|---|--------|------|-------------|-----------------|
| B1 | `GET` | `/meta/exam-types` | — | `string[]` — `["CSEE","ACSEE"]` |
| B2 | `GET` | `/meta/subjects/acsee` | — | `SubjectInfo[]` — `{ value, abbreviation }` |
| B3 | `GET` | `/meta/subjects/csee` | — | `SubjectInfo[]` — `{ value, abbreviation }` |
| B4 | `GET` | `/meta/sex` | — | `string[]` — `["M","F","None"]` |
| B5 | `GET` | `/meta/years` | — | `YearInfo[]` — `{ examType, years: number[] }` (wrapped in envelope) |
| B6 | `GET` | `/meta/regions` | — | `string[]` (wrapped in envelope) |
| B7 | `GET` | `/meta/councils` | `region?` | `string[]` (wrapped in envelope) |

### C. Centers

| # | Method | Path | Query Params | Response `data` |
|---|--------|------|-------------|-----------------|
| C1 | `GET` | `/centers` | `search?`, `region?`, `council?`, `page=1`, `pageSize=50` | `CenterListItem[]` (paginated) |
| C2 | `GET` | `/centers/{necta_reg_no}` | — | `CenterDetail` |
| C3 | `GET` | `/centers/{necta_reg_no}/performance` | `examType` (required), `year` (required) | `CenterPerformance` |

**TypeScript types:**
```ts
interface CenterListItem {
  id: string | null; name: string | null; nectaRegNo: string | null;
  schoolRegistrationNumber: string | null; region: string | null;
  council: string | null; ward: string | null; ownership: string | null;
  institutionType: string | null;
}
interface CenterDetail extends CenterListItem {
  createdAt: string | null; updatedAt: string | null; metaData: Record<string,any>[] | null;
}
interface PerDivisionSummary { males: number; females: number; total: number; }
interface DivisionDistribution {
  divisionOne: PerDivisionSummary; divisionTwo: PerDivisionSummary;
  divisionThree: PerDivisionSummary; divisionFour: PerDivisionSummary;
  divisionZero: PerDivisionSummary; absent: PerDivisionSummary;
  resultWithheld: PerDivisionSummary; eStar: PerDivisionSummary;
  withdrawn: PerDivisionSummary; specialPass: PerDivisionSummary;
}
interface CenterPerformance {
  center: CenterDetail; year: number; examType: string;
  candidatesCount: number; passRate: number;
  divisionDistribution: DivisionDistribution;
}
```

### D. Results Explorer

| # | Method | Path | Query Params | Response `data` |
|---|--------|------|-------------|-----------------|
| D1 | `GET` | `/results/{exam_type}` | `year?`, `center?`, `subject?`, `sex?`, `page=1`, `pageSize=50` | `ResultItem[]` (paginated) |

- `exam_type` path param: `"ACSEE"` or `"CSEE"`
- `center`: NECTA registration number (e.g. `S0100`)
- `subject`: partial match on subject name
- `sex`: `"M"` or `"F"`

**TypeScript types:**
```ts
interface SubjectGradeItem { subject: string; grade: string; }
interface ResultItem {
  year: number | null; sex: string | null; aggregate: number | string | null;
  division: string | null; indexNumber: string | null;
  subjects: SubjectGradeItem[] | null; schoolName: string | null;
  nectaRegistration: string | null; region: string | null; council: string | null;
}
```

### E. Summaries

| # | Method | Path | Query Params | Response `data` |
|---|--------|------|-------------|-----------------|
| E1 | `GET` | `/summaries/{exam_type}` | `year?`, `centerId?`, `region?`, `sortBy?`, `page=1`, `pageSize=50` | `SummaryItem[]` (paginated) |
| E2 | `GET` | `/summaries/{exam_type}/all-years` | `region?`, `sortBy?`, `page=1`, `pageSize=50` | `SummaryItem[]` (paginated) |

**TypeScript types:**
```ts
interface SummaryItem {
  year: number | null; examType: string | null; name: string | null;
  nectaRegistration: string | null; region: string | null;
  council: string | null; ward: string | null; ownership: string | null;
  candidatesResultSummary: Record<string, any> | null;
}
```

### F. Jobs

| # | Method | Path | Body / Query Params | Response `data` |
|---|--------|------|---------------------|-----------------|
| F1 | `POST` | `/jobs/results` | Body: `{ examType, years: number[], sourceUrl?, priority? }` | `JobResponse` (201) |
| F2 | `POST` | `/jobs/full-rebuild` | Body: `{ examType, years: number[], sourceUrl?, priority? }` | `JobResponse` (201) |
| F3 | `POST` | `/jobs/export` | Body: `{ exportType: "results"\|"summaries", examType, priority? }` | `JobResponse` (201) |
| F4 | `POST` | `/jobs` | Body: `{ type, examType, years[], sourceUrl?, priority? }` | `JobResponse` (201, generic/legacy) |
| F5 | `GET` | `/jobs` | `status?`, `type?`, `examType?`, `year?`, `page=1`, `pageSize=50` | `JobResponse[]` (paginated) |
| F6 | `GET` | `/jobs/{job_id}` | — | `JobResponse` |
| F7 | `POST` | `/jobs/{job_id}/cancel` | — | `JobResponse` |

**TypeScript types:**
```ts
interface JobResponse {
  id: string; type: string; examType: string; years: number[];
  sourceUrl: string | null; priority: number | null; status: string;
  idempotencyKey: string | null; createdAt: string | null;
  updatedAt: string | null; lockedBy: string | null;
  progress: Record<string,any> | null; error: string | null;
  deduplicated: boolean;
}
```

### G. Exports

| # | Method | Path | Body / Query | Response |
|---|--------|------|-------------|----------|
| G1 | `POST` | `/exports/{export_type}` | — | Raw export doc (201) |
| G2 | `GET` | `/exports/{export_id}` | — | Raw export doc or `null` |

---

## Steps

### Step 1 — Scaffold the standalone project & install dependencies

Create the project in its own folder (e.g. `necta-frontend/`), independent of the backend repo.

```bash
npx create-next-app@14 necta-frontend --app --typescript --tailwind --eslint --src-dir
cd necta-frontend
npm install framer-motion @tanstack/react-query recharts axios lucide-react
```

- Configure Tailwind with a custom colour palette: `slate`, `emerald/teal`, `white`, `zinc`.
- Create `.env.local` with `NEXT_PUBLIC_API_BASE=http://localhost:8000/v1`.
- Set up path aliases in `tsconfig.json` (`@/*` → `src/*`).

### Step 2 — Build the API client layer

Create `src/lib/api/` with the following modules. Each module is self-contained and only needs the base URL from the env var.

#### `src/lib/api/client.ts` — shared Axios instance
- Create an Axios instance with `baseURL = process.env.NEXT_PUBLIC_API_BASE`.
- Add a response interceptor that unwraps the `{ data, meta }` envelope.
- Export generic helper: `unwrap<T>(res): { data: T; meta: PaginationMeta | null }`.
- Export shared types: `PaginationMeta`, `SuccessResponse<T>`, `ErrorResponse`.

#### `src/lib/api/meta.ts` — consumes APIs B1–B7
| Function | Endpoint | Return type |
|----------|----------|-------------|
| `getExamTypes()` | `GET /meta/exam-types` | `string[]` |
| `getAcseeSubjects()` | `GET /meta/subjects/acsee` | `SubjectInfo[]` |
| `getCseeSubjects()` | `GET /meta/subjects/csee` | `SubjectInfo[]` |
| `getSexOptions()` | `GET /meta/sex` | `string[]` |
| `getYears()` | `GET /meta/years` | `YearInfo[]` |
| `getRegions()` | `GET /meta/regions` | `string[]` |
| `getCouncils(region?)` | `GET /meta/councils?region=` | `string[]` |

#### `src/lib/api/centers.ts` — consumes APIs C1–C3
| Function | Endpoint | Return type |
|----------|----------|-------------|
| `listCenters({ search?, region?, council?, page?, pageSize? })` | `GET /centers` | `{ data: CenterListItem[]; meta: PaginationMeta }` |
| `getCenter(nectaRegNo)` | `GET /centers/{nectaRegNo}` | `CenterDetail` |
| `getCenterPerformance(nectaRegNo, examType, year)` | `GET /centers/{nectaRegNo}/performance?examType=&year=` | `CenterPerformance` |

#### `src/lib/api/results.ts` — consumes API D1
| Function | Endpoint | Return type |
|----------|----------|-------------|
| `listResults({ examType, year?, center?, subject?, sex?, page?, pageSize? })` | `GET /results/{examType}` | `{ data: ResultItem[]; meta: PaginationMeta }` |

#### `src/lib/api/summaries.ts` — consumes APIs E1–E2
| Function | Endpoint | Return type |
|----------|----------|-------------|
| `listSummaries({ examType, year?, centerId?, region?, sortBy?, page?, pageSize? })` | `GET /summaries/{examType}` | `{ data: SummaryItem[]; meta: PaginationMeta }` |
| `listAllYearsSummaries({ examType, region?, sortBy?, page?, pageSize? })` | `GET /summaries/{examType}/all-years` | `{ data: SummaryItem[]; meta: PaginationMeta }` |

#### `src/lib/api/jobs.ts` — consumes APIs F1–F7
| Function | Endpoint | Return type |
|----------|----------|-------------|
| `createResultsJob({ examType, years, sourceUrl?, priority? })` | `POST /jobs/results` | `JobResponse` |
| `createFullRebuildJob({ examType, years, sourceUrl?, priority? })` | `POST /jobs/full-rebuild` | `JobResponse` |
| `createExportJob({ exportType, examType, priority? })` | `POST /jobs/export` | `JobResponse` |
| `createJob(body)` | `POST /jobs` | `JobResponse` (legacy) |
| `listJobs({ status?, type?, examType?, year?, page?, pageSize? })` | `GET /jobs` | `{ data: JobResponse[]; meta: PaginationMeta }` |
| `getJob(jobId)` | `GET /jobs/{jobId}` | `JobResponse` |
| `cancelJob(jobId)` | `POST /jobs/{jobId}/cancel` | `JobResponse` |

#### `src/lib/api/exports.ts` — consumes APIs G1–G2
| Function | Endpoint | Return type |
|----------|----------|-------------|
| `createExport(exportType)` | `POST /exports/{exportType}` | `ExportDoc` |
| `getExport(exportId)` | `GET /exports/{exportId}` | `ExportDoc \| null` |

#### `src/lib/api/health.ts` — consumes API A1
| Function | Endpoint | Return type |
|----------|----------|-------------|
| `checkHealth()` | `GET /health` | `{ status: string }` |

### Step 3 — Create React Query hooks layer

Create `src/hooks/` with one file per API group (e.g. `useCenters.ts`, `useResults.ts`, `useMeta.ts`, `useSummaries.ts`, `useJobs.ts`, `useExports.ts`). Each hook wraps the corresponding API function with `useQuery` / `useMutation` / `useInfiniteQuery` from `@tanstack/react-query`.

Key hooks:

| Hook | API(s) | Notes |
|------|--------|-------|
| `useExamTypes()` | B1 | `staleTime: Infinity` (static) |
| `useSubjects(examType)` | B2, B3 | switches between ACSEE/CSEE |
| `useSexOptions()` | B4 | static |
| `useYears()` | B5 | static |
| `useRegions()` | B6 | static |
| `useCouncils(region?)` | B7 | re-fetches when region changes |
| `useCenters(filters)` | C1 | paginated, `keepPreviousData` |
| `useCenter(nectaRegNo)` | C2 | enabled when `nectaRegNo` is truthy |
| `useCenterPerformance(nectaRegNo, examType, year)` | C3 | enabled when all params present |
| `useResults(filters)` | D1 | paginated or `useInfiniteQuery` |
| `useSummaries(filters)` | E1 | paginated |
| `useAllYearsSummaries(filters)` | E2 | paginated |
| `useJobs(filters)` | F5 | `refetchInterval: 5000` for live status |
| `useJob(jobId)` | F6 | `refetchInterval: 3000` while running |
| `useCreateResultsJob()` | F1 | `useMutation` |
| `useCreateFullRebuildJob()` | F2 | `useMutation` |
| `useCreateExportJob()` | F3 | `useMutation` |
| `useCancelJob()` | F7 | `useMutation` |
| `useExport(exportId)` | G2 | polling while status !== complete |

### Step 4 — Create the landing page & shared layout

#### Root layout — `src/app/layout.tsx`
- Wrap children in `QueryClientProvider`.
- Responsive top nav: **Home · Centers · Results · Summaries · Admin**.
- Mobile: slide-in drawer (Framer Motion `AnimatePresence`).
- Minimal footer with links.

#### Landing page — `src/app/page.tsx`
- **Hero section**: animated headline ("Explore Tanzania's Exam Results") with Framer Motion `spring` entrance. Subtle gradient background (`slate-50` → `emerald-50`).
- **Quick-search bar**: typeahead input that calls `useCenters({ search: debounced })` (**API C1**) and shows a dropdown of matching centers.
- **Animated stat counters**: fetch total centers from `useCenters` meta and total summaries from `useSummaries` meta (**APIs C1, E1**). Use Framer Motion `useMotionValue` + `useTransform` for counting animation.
- **CTA cards**: three cards ("Browse Centers", "Explore Results", "Compare Schools") that route to `/centers`, `/results`, `/summaries` — with hover scale animation.
- **API health indicator**: tiny dot in the footer consuming `GET /health` (**API A1**).

### Step 5 — Implement the Centers section

#### Browse — `src/app/centers/page.tsx`
- Filter bar at top: region dropdown (**API B6**), council dropdown (**API B7**, re-fetches on region change), free-text search.
- Card grid or table view toggle. Each card shows name, NECTA reg no, region, council.
- Pagination controls at bottom driven by `PaginationMeta` from **API C1**.
- Framer Motion `layout` prop on cards for smooth reflow on filter change.

#### Detail — `src/app/centers/[nectaRegNo]/page.tsx`
- Header with center name, reg no, region, council, ward, ownership (**API C2**).
- **Performance panel**: exam-type toggle (`ACSEE`/`CSEE` from **API B1**) + year selector (**API B5**). Fetches **API C3**.
  - **Donut chart** (recharts `PieChart`) for division distribution.
  - **KPI cards**: pass rate (animated percentage), candidate count, per-division breakdowns with male/female split.
  - Framer Motion `AnimatePresence` for smooth panel transitions when year/exam type changes.

### Step 6 — Implement the Results Explorer

#### `src/app/results/page.tsx`
- **Sidebar filters**: exam type toggle (**API B1**), year multi-select (**API B5**), center search with autocomplete (**API C1**), subject dropdown (**API B2/B3**), sex radio (**API B4**).
- **Results table**: columns — Index Number, School, Division, Aggregate, Sex, Subjects (expandable). Data from **API D1**.
- Pagination or infinite scroll via `useInfiniteQuery`.
- **Subject detail expansion**: clicking a row reveals the `subjects[]` array as coloured grade pills.
- Framer Motion stagger animation on row entrance.

### Step 7 — Implement the Summaries Comparison page

#### `src/app/summaries/page.tsx`
- **Two tabs/views**: "By Year" (**API E1**) and "All Years" (**API E2**).
- **Filter bar**: exam type toggle, year selector (for "By Year"), region filter (**API B6**), sort-by dropdown.
- **Grouped bar chart** (recharts `BarChart`): X-axis = centers, grouped bars = divisions, animated transitions on filter change.
- **Region overview**: card grid where each card shows a region name and aggregated pass rate, styled as a heatmap (green → amber → red). Data derived from summaries filtered by region.
- **Comparison table**: sortable table of `SummaryItem[]` with sparkline-style inline bars for division counts.

### Step 8 — Build the Admin panel (Jobs & Exports)

#### `src/app/admin/page.tsx`
- **Tabs**: Jobs · Exports (animated underline indicator).

##### Jobs tab
- **Create job form**: radio for job type (Results / Full Rebuild), exam type toggle, year multi-select, optional source URL. Submit calls **API F1** or **API F2**.
- **Job list table**: auto-refreshing (5 s) via `useJobs` (**API F5**). Columns: ID, type, exam type, years, status (badge: green/yellow/red/grey), created at. Click row → detail drawer.
- **Job detail drawer**: fetches **API F6**, shows progress JSON, error message, cancel button (**API F7**, disabled unless `status === "queued"`).

##### Exports tab
- **Create export form**: export type radio (results / summaries), exam type toggle. Submit calls **API F3** (which internally uses `/jobs/export`) or **API G1** (`POST /exports/{type}`).
- **Export list**: shows recent exports with status polling (**API G2**). When complete, show download link.

### Step 9 — Animations & polish

- **Page transitions**: wrap `{children}` in layout with `AnimatePresence` and `motion.div` fade+slide.
- **Scroll-triggered entrances**: use Framer Motion `whileInView` for stat cards and charts.
- **Skeleton loaders**: shimmer placeholders while React Query is in `isLoading` state.
- **Dark mode toggle**: Tailwind `dark:` classes with `next-themes`. Palette: dark slate background, emerald accents remain.
- **Toast notifications**: for job creation success, export ready, API errors.

---

## Folder structure

```
necta-frontend/
├── .env.local                          # NEXT_PUBLIC_API_BASE
├── package.json
├── tailwind.config.ts
├── tsconfig.json
├── src/
│   ├── app/
│   │   ├── layout.tsx                  # Root layout, nav, QueryClientProvider
│   │   ├── page.tsx                    # Landing page (hero, search, stats)
│   │   ├── centers/
│   │   │   ├── page.tsx                # Center browse      → API C1, B6, B7
│   │   │   └── [nectaRegNo]/
│   │   │       └── page.tsx            # Center detail/perf  → API C2, C3, B1, B5
│   │   ├── results/
│   │   │   └── page.tsx                # Results explorer    → API D1, B1–B5, C1
│   │   ├── summaries/
│   │   │   └── page.tsx                # Summaries compare   → API E1, E2, B1, B5, B6
│   │   └── admin/
│   │       └── page.tsx                # Jobs & exports      → API F1–F7, G1, G2
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Navbar.tsx
│   │   │   ├── MobileDrawer.tsx
│   │   │   └── Footer.tsx
│   │   ├── ui/
│   │   │   ├── Badge.tsx
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Skeleton.tsx
│   │   │   ├── Tabs.tsx
│   │   │   └── Toast.tsx
│   │   ├── charts/
│   │   │   ├── DivisionDonut.tsx       # recharts PieChart
│   │   │   ├── PassRateBar.tsx         # recharts BarChart
│   │   │   └── StatCounter.tsx         # animated number
│   │   └── filters/
│   │       ├── ExamTypeToggle.tsx      # → API B1
│   │       ├── YearSelector.tsx        # → API B5
│   │       ├── RegionSelect.tsx        # → API B6
│   │       ├── CouncilSelect.tsx       # → API B7
│   │       ├── SubjectSelect.tsx       # → API B2/B3
│   │       ├── SexRadio.tsx            # → API B4
│   │       └── CenterSearch.tsx        # → API C1 (typeahead)
│   ├── hooks/
│   │   ├── useMeta.ts                  # B1–B7
│   │   ├── useCenters.ts              # C1–C3
│   │   ├── useResults.ts             # D1
│   │   ├── useSummaries.ts           # E1–E2
│   │   ├── useJobs.ts                # F1–F7
│   │   └── useExports.ts             # G1–G2
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts              # Axios instance + unwrap helper
│   │   │   ├── types.ts               # All shared TS interfaces
│   │   │   ├── health.ts              # A1
│   │   │   ├── meta.ts                # B1–B7
│   │   │   ├── centers.ts             # C1–C3
│   │   │   ├── results.ts             # D1
│   │   │   ├── summaries.ts           # E1–E2
│   │   │   ├── jobs.ts                # F1–F7
│   │   │   └── exports.ts             # G1–G2
│   │   └── utils/
│   │       ├── debounce.ts
│   │       └── formatters.ts           # percentages, dates, numbers
│   └── styles/
│       └── globals.css                 # Tailwind directives + custom vars
```

## Colour palette

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `bg-primary` | `slate-50` | `slate-900` | Page background |
| `bg-surface` | `white` | `slate-800` | Cards, panels |
| `accent` | `emerald-500` | `emerald-400` | CTAs, active states, chart highlights |
| `accent-soft` | `emerald-50` | `emerald-900/20` | Hover backgrounds, badges |
| `text-primary` | `slate-900` | `slate-50` | Headings |
| `text-secondary` | `slate-500` | `slate-400` | Body, descriptions |
| `border` | `slate-200` | `slate-700` | Dividers, card borders |
| `danger` | `rose-500` | `rose-400` | Errors, failed badges |
| `warning` | `amber-500` | `amber-400` | Queued/running badges |

## Further Considerations

1. **Framework choice** — Next.js 14 (App Router) is recommended for SSR, file-based routing, and React Server Components. Alternatively, Vite + React could be used if SSR is not needed. *Preference?*
2. **Chart library** — `recharts` is lightweight and React-native; `@nivo/bar` or `chart.js` are alternatives if richer chart types (treemaps, heatmaps) are desired.
3. **Authentication** — The current API has no auth (`allow_origins=["*"]`). If admin routes (Jobs/Exports) should be protected, a lightweight auth layer (e.g. NextAuth.js with a simple credentials provider) should be added in a follow-up phase.
