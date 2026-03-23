# Coding Conventions

**Analysis Date:** 2026-03-23

## Naming Patterns

**Files:**
- Lowercase with underscores: `cba_script.js`, `cba_style.css`, `cba_schedule.html`
- API handlers in `api/` directory follow lowercase naming: `api/schedule.js`

**Functions:**
- camelCase: `fetchRealSchedule()`, `displaySchedule()`, `filterByDate()`, `initFilters()`, `getStatusClass()`
- Action verbs as prefixes: `fetch*`, `display*`, `filter*`, `init*`, `get*`, `show*`, `set*`, `close*`, `process*`
- Private/helper functions don't use underscore prefix - all functions are global scope

**Variables:**
- camelCase: `cbaSchedule`, `tableBody`, `teamSelect`, `gameId`, `dateStr`, `statusClass`
- Constants in UPPERCASE_SNAKE_CASE: `CBA_TEAMS`, `TEAM_FULL_NAMES`, `TEAM_VENUES`, `ALL_VENUES`, `SINA_CBA_API`, `USE_LIVE_API`, `SINA_CBA_URL`, `SCRIPT_PATH`
- Boolean flags start with `is*`, `has*`, or verb forms: `hasScore`, `USE_LIVE_API`

**Types/Objects:**
- Object keys use camelCase: `homeTeam`, `awayTeam`, `weekDay`, `homeScore`, `awayScore`, `statusClass`
- Game object structure: `{ id, round, date, time, homeTeam, awayTeam, venue, status, homeScore, awayScore, quarter, weekDay }`
- API response: `{ success, data, error, updated }`

## Code Style

**Formatting:**
- No linter/formatter configured (project uses vanilla HTML/CSS/JS)
- Manual spacing: 4 spaces for indentation (visible in function bodies)
- Line breaks between function definitions
- Block comments for major sections: `/**\n * Description\n */`

**Comments:**
- JSDoc-style comments for all major functions
- Example in `cba_script.js`:
  ```javascript
  /**
   * 从新浪体育获取实时赛程数据
   */
  async function fetchRealSchedule() {
  ```

**Function Documentation:**
- All functions have JSDoc header with purpose
- Chinese language for comments (matching project locale)
- No parameter or return type annotations

## Import Organization

**Browser Environment (`cba_script.js`, `cba_schedule.html`):**
- Single HTML file includes inline script via `<script src="cba_script.js"></script>`
- No module imports or export system
- Global function exports at end of file: `window.filterByDate = filterByDate;`
- Global constants at module top: `CBA_TEAMS`, `TEAM_FULL_NAMES`, `TEAM_VENUES`

**Node.js Environment (`update_schedule.js`):**
- Node.js `require()` at top: `const https = require('https');`
- Standard library imports first: `https`, `fs`, `path`
- Conditional dependency handling with try/catch:
  ```javascript
  let iconv;
  try {
    iconv = require('iconv-lite');
  } catch (e) {
    console.error('错误: 需要安装 iconv-lite');
    process.exit(1);
  }
  ```

**Vercel Serverless (`api/schedule.js`):**
- ES6 export: `export default async function handler(req, res) {}`
- No explicit imports needed (built-in functions like `fetch`, `TextDecoder`)

## Error Handling

**Patterns:**
- Try/catch blocks for async operations:
  ```javascript
  try {
    const response = await fetch('/api/schedule');
    if (response.ok) {
      const result = await response.json();
      if (result.success && result.data) {
        return processScheduleData(result.data);
      }
    }
  } catch (error) {
    console.warn('API获取失败，使用本地数据:', error);
  }
  ```

- Graceful fallback to embedded data when API fails
- Status code checks: `if (response.ok)` and `if (!response.ok)`
- Process termination on critical failures: `process.exit(1)`
- User-facing alerts for errors in browser (temporary, not optimal)

**Error Messages:**
- Chinese messages matching UI language: `'错误: 需要安装 iconv-lite'`
- Logs include context: `'从API获取到实时数据:', result.data.length, '场比赛'`

## Logging

**Framework:** No dedicated logging library. Uses:
- `console.log()` for informational logs: `console.log('CBA赛程管理系统已加载 (数据源: 新浪体育)');`
- `console.warn()` for warnings: `console.warn('API获取失败，使用本地数据:', error);`
- `console.error()` for errors: `console.error('未找到scheduleBody元素');`

**Patterns:**
- Logs include context about operation: `'从API获取到实时数据:', length, '场比赛'`
- Timestamp added by browser console automatically
- Update frequency logged: `console.log('数据已自动更新');`

## Function Design

**Size:**
- Typical function: 20-50 lines
- Large functions: `getEmbeddedScheduleData()` (120 lines - data mapping)
- `processScheduleData()` uses map/sort: 20 lines
- Single responsibility mostly observed

**Parameters:**
- Functions use single object parameter for data: `processScheduleData(rawData)`
- Filter functions accept string parameter: `filterByDate(dateStr)`, `filterByTeam(teamName)`
- Event handlers receive event object: `(e) => filterByTeam(e.target.value)`

**Return Values:**
- Data transformation functions return arrays: `processScheduleData()` returns sorted array
- Filter functions call display functions as side effect, no return
- Async functions return promises: `fetchRealSchedule()` returns Promise

## Module Design

**Exports:**
- Browser environment: Functions exported to `window` object at module end
- All user-interactive functions exported globally: `window.filterByDate = filterByDate;`
- Non-exported internal functions: `getStatusClass()`, `getActionButtons()`, `updateStats()`

**Barrel Files:** Not used (single script file architecture)

**Global State:**
- Single global array: `let cbaSchedule = [];`
- Global namespace accessed throughout: `document.getElementById()`, `window.location`

## HTML/CSS Conventions

**HTML Structure:**
- Semantic HTML5: `<thead>`, `<tbody>`, `<table>` for data
- Accessibility attributes: `data-label` on table cells for mobile rendering

**CSS Organization:**
- Responsive design with media query breakpoint at 768px
- Color scheme: Blue primary (#4a90d9), grays for borders
- BEM-like naming for CSS classes: `.filter-section`, `.status`, `.team-name`

## Input Validation

**Current State:** Minimal validation
- Checks for element existence: `if (!tableBody)`, `if (!modal)`
- Type coercion on form inputs: `parseInt(scoreParts[0])`
- No schema validation (could benefit from addition)

---

*Convention analysis: 2026-03-23*
