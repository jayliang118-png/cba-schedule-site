# Architecture

**Analysis Date:** 2026-03-23

## Pattern Overview

**Overall:** Client-Server with Fallback, Static Site with Optional API Layer

**Key Characteristics:**
- Single-page static HTML application with zero build process
- Dual data source strategy: Live API when deployed, embedded fallback for local use
- Real-time schedule fetching from external sports data provider (Sina Sports)
- Responsive design supporting both desktop and mobile viewing
- Manual and automated data update pipelines

## Layers

**Presentation Layer:**
- Purpose: User interface for filtering and displaying CBA game schedules
- Location: `cba_schedule.html`, `cba_style.css`
- Contains: HTML structure, responsive CSS grid/flexbox, color schemes, mobile card layout
- Depends on: JavaScript in `cba_script.js`
- Used by: Browser rendering engine

**Business Logic Layer:**
- Purpose: Schedule data transformation, filtering, status determination, event handling
- Location: `cba_script.js` (lines 49-571)
- Contains: Data fetching, parsing, filtering functions, UI state management
- Depends on: External API at `/api/schedule` (deployed) or embedded data
- Used by: HTML event handlers, DOM manipulation functions

**Data Management Layer:**
- Purpose: Schedule data retrieval and normalization
- Location: `cba_script.js` (lines 49-225)
- Contains: `fetchRealSchedule()`, `getEmbeddedScheduleData()`, `processScheduleData()`
- Depends on: Sina Sports API via `/api/schedule` proxy (Vercel) or direct embedded array
- Used by: Application initialization and refresh functions

**API/Integration Layer:**
- Purpose: Server-side proxy to Sina Sports, handling GBK encoding and CORS
- Location: `api/schedule.js`
- Contains: HTTP request handler, GBK-to-UTF-8 conversion, HTML parsing
- Depends on: Sina Sports external API (`https://cba.sports.sina.com.cn/cba/schedule/all/`)
- Used by: Frontend when deployed on Vercel

**Data Update Pipeline:**
- Purpose: Offline schedule data refresh from Sina Sports
- Location: `update_schedule.js`
- Contains: HTTPS fetching, GBK decoding via iconv-lite, data extraction, file writing
- Depends on: External Sina Sports API, `iconv-lite` npm package
- Used by: Manual CLI invocation or GitHub Actions workflow

## Data Flow

**Frontend Initialization (Browser):**

1. HTML page loads (`cba_schedule.html`)
2. JavaScript loads (`cba_script.js`)
3. `DOMContentLoaded` event triggers `initCBA()` function (line 546)
4. `fetchRealSchedule()` called (line 548)
5. If deployed on Vercel: Fetch `/api/schedule` endpoint
   - Server (`api/schedule.js`) fetches Sina Sports HTML
   - Decodes GBK encoding to UTF-8
   - Parses schedule table using regex
   - Returns JSON with game objects
6. If local development: Use embedded `realSchedule` array (fallback)
7. Data normalized via `processScheduleData()` function
8. `initFilters()` populates team/date/status selectors
9. `displaySchedule()` renders table with all games
10. Auto-refresh set: every 60 seconds (line 553-557)

**Data Flow Diagram:**

```
Sina Sports HTML (GBK)
        ↓ (When deployed)
/api/schedule endpoint (Vercel)
        ↓
decodeGBK() + parseSchedule()
        ↓
JSON game objects
        ↓ (When offline/local)
Embedded realSchedule array
        ↓
processScheduleData() - normalize format
        ↓
displaySchedule() - render table
        ↓
HTML table with filtering
```

**State Management:**

- Global array `cbaSchedule` (line 39) holds normalized game objects
- Game object structure: `{ id, round, date, time, homeTeam, awayTeam, venue, status, homeScore, awayScore, quarter, weekDay }`
- Filters modify view of `cbaSchedule` without mutating it (line 356, 369, 382)
- Status values: '已结束' (ended), '进行中' (in progress), '未开始' (not started)
- Real-time status determination based on: score format ('VS' vs '##:##'), game date comparison with today

## Key Abstractions

**Schedule Game Object:**
- Purpose: Normalized representation of a single CBA game
- Examples: Lines 210-223 show transformation from raw data to game object
- Pattern: Immutable object with date/time/team/score normalized to consistent format

**Data Source Adapter:**
- Purpose: Abstraction over data source (API vs embedded)
- Examples: `fetchRealSchedule()` (line 52) decides between live API and fallback
- Pattern: `USE_LIVE_API` flag enables/disables API calls based on hostname

**Filter Functions:**
- Purpose: Pure functions that filter schedule without mutation
- Examples: `filterByDate()` (line 351), `filterByTeam()` (line 363), `filterByStatus()` (line 377)
- Pattern: Take filter criteria, return filtered view, call `displaySchedule()` to render

**Status Calculator:**
- Purpose: Determine game status from score format and date
- Examples: Lines 123-131 in `api/schedule.js`, lines 208 in `cba_script.js`
- Pattern: Score format detection ('VS' marker), date comparison against today

## Entry Points

**Main UI Page:**
- Location: `cba_schedule.html`
- Triggers: User visits domain root `/`
- Responsibilities: Render container divs, load stylesheets, script tags, button handlers

**Initialization Function:**
- Location: `cba_script.js`, line 546 `initCBA()`
- Triggers: `DOMContentLoaded` event
- Responsibilities: Load initial schedule, bind filter UI, start refresh interval

**API Endpoint:**
- Location: `api/schedule.js`
- Triggers: GET request to `/api/schedule` (when deployed on Vercel)
- Responsibilities: Fetch Sina Sports data, parse GBK HTML, return normalized JSON

**Refresh Handler:**
- Location: `cba_script.js`, line 519 `refreshSchedule()`
- Triggers: User clicks "刷新数据" button OR auto-refresh timer (every 60s)
- Responsibilities: Re-fetch data, re-display schedule

**Update Pipeline:**
- Location: `update_schedule.js`
- Triggers: Manual CLI invocation or GitHub Actions daily at 20:00 Beijing time
- Responsibilities: Fetch latest schedule, update embedded array in `cba_script.js`, commit

## Error Handling

**Strategy:** Graceful degradation - always show something even if API fails

**Patterns:**

- **API Failures (line 64-66):** Caught try-catch, silently falls back to embedded data
- **Missing DOM Elements (line 250-252):** Check existence before manipulation, return early
- **Invalid Data (line 117 in api/schedule.js):** Check cell count before processing
- **Encoding Issues (line 67-71 in api/schedule.js):** Catch TextDecoder errors, replace with '?'

## Cross-Cutting Concerns

**Logging:**
- Console logging only (no external service)
- Lines 60, 65, 520, 547, 556 show console messages for debugging
- Used to track API success/failure and data refresh events

**Validation:**
- Defensive checks for DOM element existence before manipulation
- Cell count validation before parsing table rows (line 117 in api/schedule.js)
- Score format detection to determine game status

**Date/Time Handling:**
- All dates standardized to ISO format: `YYYY-MM-DD`
- Time format: `HH:MM` (24-hour)
- Week day calculated from date using `getWeekDay()` function (line 240-243)
- Status determination uses date comparison: today's games = "in progress", past = "ended"

**Internationalization:**
- Hardcoded Chinese strings throughout (status, labels, button text)
- Team names have both abbreviated and full legal names (TEAM_FULL_NAMES map)
- Venue data maps team abbreviations to full venue names

---

*Architecture analysis: 2026-03-23*
