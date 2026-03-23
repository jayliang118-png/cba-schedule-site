# ROADMAP: CBA Schedule Site (Flask Conversion)

**Created:** 2026-03-23
**Depth:** Quick (4 phases)
**Coverage:** 20/20 v1 requirements mapped

---

## Phases

- [x] **Phase 1: Flask Foundation & UI** - Bootstrap Flask app with Jinja2 templates and responsive schedule display
- [x] **Phase 2: Data Layer & Scraping** - Implement Sina Sports data integration and /api/schedule endpoint (completed 2026-03-23)
- [ ] **Phase 3: Filtering & Testing** - Add filter logic and comprehensive integration tests
- [ ] **Phase 4: Auto-Update & Deployment** - Setup GitHub Actions auto-update workflow and Vercel deployment

---

## Phase Details

### Phase 1: Flask Foundation & UI

**Goal:** Users can see the CBA schedule with responsive layout on Flask application

**Depends on:** Nothing (first phase)

**Requirements mapped:**
- FRAME-01: Flask application serves HTML and JSON API from single codebase
- FRAME-02: Flask runs on Vercel serverless functions (cold start handling)
- UI-01: Jinja2 template renders schedule table with all game data
- UI-02: Mobile-responsive card layout (breakpoint 768px)
- UI-03: Filter controls for date, team, and status (UI layer only)
- UI-05: Styling matches current CSS (or updated for Jinja2)

**Success Criteria** (what must be TRUE):
1. Flask app starts without errors and serves HTML homepage at `/`
2. Jinja2 template renders schedule table with team names, venues, dates, and statuses visible
3. Page displays correctly on desktop (full table layout) and mobile (card layout at <768px)
4. Filter control inputs (date picker, team dropdown, status selector) are present and styled
5. All current CSS styling is applied or adapted for Jinja2 templates

**Plans:** 3 plans

Plans:
- [x] 01-01-PLAN.md — Flask application scaffold with serverless-compatible entry point (Commit: ebbe6ee)
- [x] 01-02-PLAN.md — Jinja2 templates and responsive styling for schedule display (Commit: a742a0e)
- [x] 01-03-PLAN.md — Client-side JavaScript scaffold for filter interactions (Commit: 3d8e0ef)

---

### Phase 2: Data Layer & Scraping

**Goal:** Schedule data is fetched from Sina Sports, parsed correctly, and served via JSON API

**Depends on:** Phase 1 (Flask app structure in place)

**Requirements mapped:**
- FRAME-03: Configuration management for Sina Sports scraping URL and schedules
- DATA-01: Scrape CBA schedule from Sina Sports HTML (GBK encoding)
- DATA-02: Parse game information (team, venue, date, status, score)
- DATA-03: Store parsed schedule as embedded JSON in application
- DATA-04: /api/schedule endpoint returns JSON with game list
- QA-01: Unit tests for Sina Sports HTML parser

**Success Criteria** (what must be TRUE):
1. Sina Sports data is successfully fetched and decoded from GBK encoding without errors
2. Parser correctly extracts team names, venues, dates, scores, and game status from HTML
3. Embedded schedule JSON is generated and stored in the Flask application
4. GET /api/schedule returns valid JSON with all game records in expected format
5. Unit tests verify parser handles edge cases (missing data, date formats, status determination)

**Plans:** 3/3 plans complete

Plans:
- [ ] 02-01-PLAN.md — Scraper setup with GBK handling and HTTP fetching
- [ ] 02-02-PLAN.md — Parser with BeautifulSoup and JSON storage
- [ ] 02-03-PLAN.md — /api/schedule endpoint and unit tests

---

### Phase 3: Filtering & Testing

**Goal:** Users can filter the displayed schedule by date, team, and status with accurate results

**Depends on:** Phase 2 (schedule data available)

**Requirements mapped:**
- UI-04: Filter logic preserved from current JavaScript implementation
- QA-02: Integration tests for /api/schedule endpoint
- QA-03: Tests verify filtering (by date, team, status)

**Success Criteria** (what must be TRUE):
1. Filter by date returns only games on selected date
2. Filter by team returns only games with selected team (home or away)
3. Filter by status returns correct games (not started, in progress, finished)
4. Multiple filters combined produce correct intersection of results
5. Integration tests verify /api/schedule endpoint with various filter parameters

**Plans:** 3 plans

Plans:
- [ ] 03-01-PLAN.md — Filter backend service and /api/schedule query parameters
- [ ] 03-02-PLAN.md — Client-side filter integration with API
- [ ] 03-03-PLAN.md — Integration tests for filtering (80%+ coverage)

---

### Phase 4: Auto-Update & Deployment

**Goal:** Schedule automatically updates daily via GitHub Actions and app is deployed to Vercel

**Depends on:** Phase 3 (full application complete)

**Requirements mapped:**
- AUTO-01: GitHub Actions workflow triggers schedule update on schedule (12:00 UTC)
- AUTO-02: Update script fetches Sina Sports data
- AUTO-03: Parse and embed updated schedule in Flask app
- AUTO-04: Commit and push updated schedule to repository
- QA-04: Deployment works on Vercel serverless

**Success Criteria** (what must be TRUE):
1. GitHub Actions workflow triggers at 12:00 UTC daily
2. Workflow successfully fetches latest schedule from Sina Sports
3. Workflow parses data, updates embedded JSON in Flask app, commits and pushes to master
4. Flask app successfully deploys to Vercel after push
5. Deployed app on Vercel serves schedule with live data and all filters working

**Plans:** TBD

---

## Progress Tracking

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Flask Foundation & UI | 3/3 | Complete ✓ | 2026-03-23 |
| 2. Data Layer & Scraping | 3/3 | Complete ✓ | 2026-03-23 |
| 3. Filtering & Testing | 0/3 | Planned | — |
| 4. Auto-Update & Deployment | 0/? | Not started | — |

---

## Coverage Validation

**Requirement Mapping:**

| Requirement | Phase | Category |
|-------------|-------|----------|
| FRAME-01 | 1 | Framework |
| FRAME-02 | 1 | Framework |
| FRAME-03 | 2 | Framework |
| DATA-01 | 2 | Data Integration |
| DATA-02 | 2 | Data Integration |
| DATA-03 | 2 | Data Integration |
| DATA-04 | 2 | Data Integration |
| UI-01 | 1 | Frontend |
| UI-02 | 1 | Frontend |
| UI-03 | 1 | Frontend |
| UI-04 | 3 | Frontend |
| UI-05 | 1 | Frontend |
| AUTO-01 | 4 | Auto-Update |
| AUTO-02 | 4 | Auto-Update |
| AUTO-03 | 4 | Auto-Update |
| AUTO-04 | 4 | Auto-Update |
| QA-01 | 2 | Testing |
| QA-02 | 3 | Testing |
| QA-03 | 3 | Testing |
| QA-04 | 4 | Testing |

**Coverage:** 20/20 v1 requirements mapped ✓

---

*Roadmap created: 2026-03-23*
*Last updated: 2026-03-23 - Phase 3 plans created*
