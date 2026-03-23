# Codebase Concerns

**Analysis Date:** 2026-03-23

## Tech Debt

**Fragile GBK Encoding Implementation:**
- Issue: Dual implementations of GBK decoding (Node.js in `update_schedule.js` and browser in `api/schedule.js`) with limited character coverage
- Files: `api/schedule.js` (lines 47-84), `update_schedule.js` (lines 36 via iconv-lite dependency)
- Impact: Incomplete GBK-to-UTF-8 mapping in Vercel function may corrupt Chinese characters for edge cases; browser decoder attempts TextDecoder('gbk') which has inconsistent support
- Fix approach:
  1. Use a complete GBK lookup table or proper library (e.g., `gbk` npm package)
  2. Unify decoding logic between Node and browser environments
  3. Add comprehensive tests for all CBA team names and special characters

**Hardcoded Data in JavaScript:**
- Issue: 100+ game records embedded directly in `cba_script.js` as a large array (lines 109-203)
- Files: `cba_script.js` (function `getEmbeddedScheduleData()`)
- Impact: File size bloat (~27KB), difficult to maintain and update, makes caching inefficient, creates merge conflicts on auto-updates
- Fix approach: Move embedded data to separate JSON file, load asynchronously to avoid main script bloat

**Manual Data Update Process Fragility:**
- Issue: `update_schedule.js` uses regex to replace data in source file; no rollback on failure
- Files: `update_schedule.js` (lines 105-117)
- Impact: Corrupted regex pattern could destroy cba_script.js file structure; no backup created; GitHub Actions runs daily with no failure recovery
- Fix approach:
  1. Create backup before updating
  2. Validate updated file syntax before commit
  3. Add pre-commit hook to verify JSON/JS validity

**Dual Data Source Management:**
- Issue: Same data parsed and managed in three places - update script, Vercel API, and embedded fallback
- Files: `update_schedule.js`, `api/schedule.js`, `cba_script.js`
- Impact: Inconsistencies when parsing rules differ; maintenance burden multiplied by 3; fallback data can become stale
- Fix approach: Single source of truth - store schedule data in JSON file, all three components read from it

## Known Bugs

**Incorrect Quarter Hardcoding:**
- Bug: Quarter is always set to '第二节' (second quarter) in embedded data
- Symptoms: Live games display "第二节" regardless of actual game progress
- Files: `cba_script.js` (line 221 in `getEmbeddedScheduleData()`)
- Trigger: Any game with status '进行中' (in progress)
- Workaround: API endpoint doesn't have this bug (line 93), so deployed version is correct; only affects local fallback
- Impact: Users testing locally see incorrect quarter information

**Malformed Scores in Embedded Data:**
- Bug: Lines 151-154 contain partial scores (e.g., '34:34', '41:26', '13:7') that appear truncated
- Symptoms: Displayed scores don't match expected final scores
- Files: `cba_script.js` (lines 151-154)
- Trigger: Viewing March 20-21, 2026 games
- Workaround: None - data is incorrect in source

**Date Parsing Edge Case:**
- Bug: If datetime string is missing space or malformed, `split(' ')` fails silently
- Symptoms: Game displays with empty time and date
- Files: `cba_script.js` (lines 78, 206), `api/schedule.js` (line 120)
- Trigger: Malformed API response or corrupted embedded data
- Workaround: Will fall back to embedded data if API fails
- Risk: Silent failure could show blank times to users

## Security Considerations

**No Input Validation on Parsed Data:**
- Risk: If HTML parsing extracts XSS payloads, they're displayed directly in `innerHTML`
- Files: `cba_script.js` (line 268), `api/schedule.js` (line 112-113 removes HTML but incompletely)
- Current mitigation: Basic HTML strip via regex replace, but inadequate for security
- Recommendations:
  1. Use DOMPurify or similar library for sanitization
  2. Avoid `innerHTML` - use `textContent` for team names and scores
  3. Validate team names against `CBA_TEAMS` whitelist

**CORS Misconfiguration:**
- Risk: `api/schedule.js` allows `Access-Control-Allow-Origin: '*'` - exposes internal endpoint to any origin
- Files: `api/schedule.js` (line 6)
- Current mitigation: None
- Recommendations:
  1. Restrict CORS to deployed domain only
  2. Remove or restrict in production: `res.setHeader('Access-Control-Allow-Origin', process.env.VERCEL_URL)`
  3. Disable for non-production environments

**User-Agent Spoofing:**
- Risk: `update_schedule.js` and `api/schedule.js` set fake User-Agent headers to access Sina Sports
- Files: `update_schedule.js` (line 30), `api/schedule.js` (line 17)
- Current mitigation: None
- Recommendations:
  1. Consider obtaining official data partnership with Sina Sports
  2. Document that this violates their terms of service
  3. Implement rate limiting to avoid abuse detection

**No Error Boundary on Critical Functions:**
- Risk: If fetch fails in `fetchRealSchedule()`, code silently falls back without logging adequate error context
- Files: `cba_script.js` (lines 52-71)
- Current mitigation: Logged to console
- Recommendations:
  1. Notify users that fallback data may be stale
  2. Show warning banner when using embedded data
  3. Add user-visible error logging with timestamp

## Performance Bottlenecks

**Automatic Refresh Every 60 Seconds:**
- Problem: `setInterval` at line 557 constantly fetches and re-renders regardless of user activity or data changes
- Files: `cba_script.js` (lines 553-557)
- Cause: No throttling, no change detection, no pause on background tabs
- Impact: Unnecessary API calls (1440 per day per user), increased battery drain on mobile
- Improvement path:
  1. Use `requestIdleCallback` or pause on `visibilitychange` event
  2. Add change detection - only re-render if data differs
  3. Implement exponential backoff for API failures
  4. Make interval configurable or respect user preference

**Full Table Re-render on Every Data Update:**
- Problem: `displaySchedule()` rebuilds entire table HTML even if no data changed (line 255)
- Files: `cba_script.js` (lines 248-302)
- Cause: No diffing or virtual DOM; full `innerHTML` replacement
- Impact: Jank on low-end devices, unnecessary DOM churn, CLS (Cumulative Layout Shift) issues
- Improvement path:
  1. Diff previous data before rendering
  2. Use document fragments to batch DOM updates
  3. Only update cells that actually changed

**No Index on Schedule Lookups:**
- Problem: `cbaSchedule.find()` is O(n) operation called repeatedly (lines 390, 442, 452)
- Files: `cba_script.js` (multiple locations)
- Cause: Games stored as array; lookups iterate through all games
- Impact: Scales poorly as schedule grows; 100+ games = multiple linear scans per user action
- Improvement path: Maintain `Map<gameId, game>` for O(1) lookups

**No Pagination on Large Datasets:**
- Problem: All 100+ games rendered in single table regardless of viewport
- Files: `cba_schedule.html` (lines 37-54)
- Cause: No pagination logic
- Impact: Large DOM tree slows rendering; users must scroll through entire season
- Improvement path: Implement pagination or virtual scrolling for games visible in viewport

## Fragile Areas

**HTML Parsing Regex-Based:**
- Files: `api/schedule.js` (line 91 main table extraction), `update_schedule.js` (line 39-52)
- Why fragile: Regex for HTML parsing breaks if Sina Sports changes markup; no CSS selector parsing
- Safe modification: Use a real HTML parser (cheerio) instead of regex
- Test coverage: No tests for parsing; only manual verification after updates

**Filter Logic Not Isolated:**
- Files: `cba_script.js` (lines 351-384)
- Why fragile: Global `cbaSchedule` state mutated indirectly; filters call display functions with side effects
- Safe modification: Extract filter functions to pure utilities with dependency injection
- Test coverage: No unit tests; only manual UI testing

**Modal Not Properly Cleaned Up:**
- Files: `cba_schedule.html` (not shown), `cba_script.js` (lines 393-436)
- Why fragile: Modal selector assumes specific HTML structure; no validation; relies on `getElementById`
- Safe modification: Create modal as web component; validate existence before use
- Test coverage: No tests; only works if HTML has correct element IDs

**Venue Mapping Incomplete:**
- Files: `cba_script.js` (lines 24-33)
- Why fragile: If new team or venue isn't in map, defaults to '待定场馆'; no error indication
- Safe modification: Validate all teams in data against whitelist on load
- Test coverage: No validation; untested edge case

## Scaling Limits

**Embedded Data Annual Growth:**
- Current capacity: ~100 games (one season)
- Limit: File size becomes problematic at 3+ seasons (~300 games = 60KB+ uncompressed)
- Scaling path:
  1. Move to external JSON endpoint
  2. Implement lazy loading (load only 30-day window)
  3. Compress with gzip (already done by Vercel)

**GitHub Actions Daily Runs:**
- Current capacity: 1 run/day per project
- Limit: If expanded to multiple sports, will hit workflow limits; Sina Sports may block frequent requests
- Scaling path:
  1. Request official CBA API access
  2. Implement request caching/CDN
  3. Increase update frequency to watch live scores in real-time (requires architecture change)

**Browser Tab Memory:**
- Current capacity: ~1-2MB per page load
- Limit: With 500+ games, DOM size could cause memory issues on low-end devices
- Scaling path: Virtual scrolling, pagination, or separate page per round

## Dependencies at Risk

**Manual `iconv-lite` Installation:**
- Risk: Dependency not in package.json; workflow manually installs it each run
- Impact: Adds ~2 minutes to every GitHub Actions run; could fail if package becomes unavailable
- Migration plan:
  1. Add package.json with locked version
  2. Use npm ci instead of install for faster, deterministic builds
  3. Consider switching to built-in TextEncoder/TextDecoder with proper GBK library

**No Package Lock File:**
- Risk: Future runs could install incompatible versions
- Impact: Silent failures, inconsistent behavior between local and CI environments
- Fix: Commit `package-lock.json` after first successful run

**Sina Sports API Dependency:**
- Risk: Not an official public API; terms of service likely prohibit scraping
- Impact: Endpoint could be blocked or change format at any time without notice
- Migration plan:
  1. Evaluate official CBA API offerings
  2. Consider partnership or official data source
  3. Implement fallback to ESPN or other aggregators

## Missing Critical Features

**No Live Score Updates:**
- Problem: System can't show real-time scores during games, only historical data
- Blocks: Real-time sports fan engagement feature; users must refresh manually
- Impact: Not competitive with native CBA apps or ESPN

**No User Preferences:**
- Problem: Filters reset on page reload; no favorited teams or notifications
- Blocks: Personalized experience; can't follow specific teams
- Impact: Limited retention; users must re-enter preferences each visit

**No Accessibility:**
- Problem: No ARIA labels, no keyboard navigation, no screen reader support
- Blocks: Compliance with a11y standards; excludes disabled users
- Impact: Legal liability; poor SEO

**No Offline Support:**
- Problem: Requires live internet; no service worker or cache strategy
- Blocks: Works offline or with poor connectivity
- Impact: Mobile users with spotty signal get blank screen

**No Error Recovery UI:**
- Problem: If API fails, silent fallback with no user notification
- Blocks: Users don't know data is stale or why screen looks different
- Impact: Confusion, lost trust in accuracy

## Test Coverage Gaps

**No Unit Tests:**
- Untested area: Date parsing, score parsing, status determination logic
- Files: `cba_script.js` (functions `processScheduleData`, `getWeekDay`, `formatDate`)
- Risk: Bugs in core logic go undetected until production; date edge cases (leap years, timezones) not verified
- Priority: HIGH - parsing bugs directly impact user experience

**No Integration Tests:**
- Untested area: Data fetch → parse → display pipeline; API endpoint
- Files: `api/schedule.js`, integration with `cba_script.js`
- Risk: Broken data flow silent failures; API changes not caught before deployment
- Priority: HIGH - core feature

**No E2E Tests:**
- Untested area: User filters, sort, table rendering on different screen sizes
- Files: `cba_schedule.html`, `cba_script.js` (filter functions)
- Risk: UI regressions on mobile; filters broken without detection
- Priority: MEDIUM - affects UX but fallbacks prevent complete failure

**No Regression Tests for HTML Parsing:**
- Untested area: Sina Sports HTML parsing logic after their site updates
- Files: `api/schedule.js` (lines 87-145), `update_schedule.js`
- Risk: Parsing breaks silently; users get outdated embedded data until next manual fix
- Priority: MEDIUM - only impacts when Sina updates

**No Testing for Malformed Data:**
- Untested area: Edge cases - missing teams, invalid dates, truncated scores
- Files: `cba_script.js` (processScheduleData, getEmbeddedScheduleData)
- Risk: Crashes or silent corruption with unexpected data format
- Priority: MEDIUM - defensive coding needed

---

*Concerns audit: 2026-03-23*
