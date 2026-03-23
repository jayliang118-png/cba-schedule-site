# Codebase Structure

**Analysis Date:** 2026-03-23

## Directory Layout

```
cba-schedule-site/
├── cba_schedule.html        # Main HTML entry point
├── cba_script.js            # All JavaScript logic and embedded data
├── cba_style.css            # Responsive styling (desktop + mobile)
├── update_schedule.js       # Manual data update script
├── vercel.json              # Deployment config for Vercel
├── package.json             # Dependencies (only iconv-lite for local updates)
├── api/
│   └── schedule.js          # Vercel serverless endpoint for live data
├── .github/
│   └── workflows/
│       └── update-schedule.yml  # GitHub Actions daily schedule update
├── .planning/
│   └── codebase/            # This documentation directory
└── node_modules/            # Dependencies (after npm install)
```

## Directory Purposes

**Root:**
- Purpose: Frontend static site files + configuration
- Contains: HTML, CSS, JavaScript, Vercel config
- Key files: `cba_schedule.html`, `cba_script.js`, `cba_style.css`

**api/**
- Purpose: Serverless backend functions (Vercel only)
- Contains: One API handler for schedule data fetching
- Key files: `schedule.js` - GBK HTML parsing and CORS proxy

**.github/workflows/**
- Purpose: CI/CD automation on GitHub
- Contains: Scheduled tasks
- Key files: `update-schedule.yml` - Daily data refresh at 20:00 Beijing time

## Key File Locations

**Entry Points:**

- `cba_schedule.html`: Main UI page (lines 1-59)
  - Defines HTML structure: filter controls, data table, modal placeholder
  - Loads stylesheets and scripts
  - Entry point for browser: displays on root `/`

- `cba_script.js`: Application bootstrap (lines 546-561)
  - `initCBA()` called on page load
  - Initializes state, filters, display
  - Sets up auto-refresh interval

**Configuration:**

- `vercel.json`: Deployment routing (lines 1-11)
  - Rewrites `/api/schedule` to API handler
  - All other routes serve `cba_schedule.html`

- `package.json`: Node.js dependencies
  - `iconv-lite`: Required for manual `update_schedule.js` CLI tool

- `.github/workflows/update-schedule.yml`: GitHub Actions schedule
  - Runs daily at 20:00 UTC (same as Beijing time 4 hours offset)
  - Executes `npm install && node update_schedule.js`

**Core Logic:**

- `cba_script.js` (lines 1-571): Entire application
  - Lines 6-33: Data constants (teams, full names, venues)
  - Lines 39-96: Data fetching layer (`fetchRealSchedule()`, `processScheduleData()`)
  - Lines 104-225: Embedded schedule data + transformation
  - Lines 248-314: Display/rendering (`displaySchedule()`, `getStatusClass()`, `getActionButtons()`)
  - Lines 351-384: Filter functions (`filterByDate()`, `filterByTeam()`, `filterByStatus()`)
  - Lines 389-456: Detail/modal handlers
  - Lines 471-514: Filter initialization and UI binding
  - Lines 519-558: Refresh and lifecycle management

**Testing:**

- No dedicated test files present
- Manual testing via `cba_schedule.html` in browser
- API testing: `curl http://localhost:3000/api/schedule` when run locally

**Styling:**

- `cba_style.css` (lines 1-249): All CSS
  - Lines 1-50: Base styles (fonts, table, headers)
  - Lines 51-100: Filter section layout
  - Lines 102-150: Mobile responsive (max-width: 768px)
  - Lines 152-249: Component-specific styles (status badges, buttons, date cells)

## Naming Conventions

**Files:**

- Pattern: `lowercase_with_underscores.js/css/html`
- Examples: `cba_schedule.html`, `cba_script.js`, `cba_style.css`, `update_schedule.js`
- Exception: `vercel.json`, `package.json` (config standards)

**Functions:**

- Pattern: `camelCase`
- Examples: `fetchRealSchedule()` (line 52), `displaySchedule()` (line 248), `filterByTeam()` (line 363)
- Prefixes: `get*` for accessors, `fetch*` for async data, `filter*` for filtering, `show*` for modal display
- Global exported: Lines 564-571 expose functions to `window` namespace for HTML onclick handlers

**Variables:**

- Pattern: `camelCase` for local variables, `UPPER_SNAKE_CASE` for constants
- Examples:
  - Constants: `CBA_TEAMS` (line 6), `TEAM_FULL_NAMES` (line 14), `TEAM_VENUES` (line 25)
  - State: `cbaSchedule` (line 39)
  - Temp: `tableBody`, `filtered`, `row`, `game`

**CSS Classes:**

- Pattern: `kebab-case`
- Examples: `.filter-section`, `.team-name`, `.status.ended`, `.btn-detail`
- Prefix patterns: `.status.*` for game status, `.btn-*` for buttons, `.*-cell` for table cells

**Game Object Properties:**

```javascript
{
  id: number,              // Unique game ID
  round: string,          // '第N轮' format
  date: string,           // 'YYYY-MM-DD' format
  time: string,           // 'HH:MM' 24-hour format
  homeTeam: string,       // Team abbreviation
  awayTeam: string,       // Team abbreviation
  venue: string,          // Full venue name or '待定场馆'
  status: string,         // '已结束', '进行中', or '未开始'
  homeScore: number|null, // null if game not played
  awayScore: number|null, // null if game not played
  quarter: string|null,   // '第二节' or null
  weekDay: string         // '周一' through '周日'
}
```

## Where to Add New Code

**New Feature:**
- Primary code: `cba_script.js` (add function before `initCBA()` at line 546)
- Tests: Create `cba_script.test.js` (not currently present)
- UI: Add HTML controls to `cba_schedule.html` lines 16-34 (filter section)

**New Component/Module:**
- Implementation: Add as function in `cba_script.js`
- Don't create separate files unless it becomes >500 lines
- Respect immutability patterns: return new data, don't mutate `cbaSchedule`

**New Filter Type:**
- Add select/input to filter section (lines 18-31 in HTML)
- Create function following pattern at line 351-384
- Call function from event listener (lines 481-500)
- Update reset handler (lines 503-513)

**Utilities:**
- Shared helpers: Add to `cba_script.js` with `get*` or `format*` prefix
- Example: `getWeekDay()` (line 240), `formatDate()` (line 230)

**Styling New Components:**
- Add to `cba_style.css` following naming convention
- Include mobile responsive variant in `@media screen and (max-width: 768px)` block

**API Enhancement:**
- Modify `api/schedule.js` only if upstream data source format changes
- Update parsing regex (line 97) if Sina Sports HTML structure changes
- Maintain backward compatibility with embedded data format

## Special Directories

**api/**
- Purpose: Vercel serverless functions (backend)
- Generated: No (manually maintained)
- Committed: Yes (source code)
- Deployment: Only active when deployed to Vercel, not used locally

**.github/workflows/**
- Purpose: GitHub Actions CI/CD
- Generated: No (manually maintained)
- Committed: Yes
- Runtime: Executes on schedule (daily at 20:00 UTC)

**node_modules/**
- Purpose: Installed dependencies
- Generated: Yes (via `npm install`)
- Committed: No (in .gitignore)
- Contents: Only `iconv-lite` package for `update_schedule.js`

**.planning/codebase/**
- Purpose: Architecture and structure documentation (this folder)
- Generated: No (manually maintained)
- Committed: Yes (reference for other Claude instances)

---

*Structure analysis: 2026-03-23*
