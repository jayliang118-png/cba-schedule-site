# External Integrations

**Analysis Date:** 2026-03-23

## APIs & External Services

**Sina Sports CBA Data:**
- Service: Sina Sports (新浪体育)
- URL: `https://cba.sports.sina.com.cn/cba/schedule/all/`
- What it's used for: Real-time CBA game schedule, scores, team information, venues
  - SDK/Client: Native `fetch()` API (browser) and `https` module (Node.js)
  - Auth: None (public endpoint)
  - Encoding: GBK (Chinese character encoding)

## Data Storage

**Databases:**
- None - Fully static data application

**File Storage:**
- Local filesystem only
- Embedded schedule data: `cba_script.js` contains hardcoded `realSchedule` array (lines 109-202)
- Static assets hosted on Vercel or served locally

**Caching:**
- Client-side: Auto-refresh every 60 seconds (line 553-557 in `cba_script.js`)
- No persistent caching - All data loaded fresh on page load

## Authentication & Identity

**Auth Provider:**
- None - Public application, no user authentication
- No login system or session management

## Data Sources

**Primary Data Source:**
- Sina Sports HTML page (GBK-encoded)
- Parsed via HTML regex matching in `update_schedule.js` and `api/schedule.js`
- Flow: Sina Sports → Fetch → Parse HTML → Extract table data → Return JSON

**Fallback Data:**
- Embedded `realSchedule` array in `cba_script.js` (last updated: 2026-03-20)
- Used when: API unavailable, localhost deployment, or API errors

## Monitoring & Observability

**Error Tracking:**
- None - No dedicated error tracking service

**Logs:**
- Console logging via `console.log()` and `console.warn()` (development)
- GitHub Actions logs for scheduled update jobs (visible in Actions tab)

## CI/CD & Deployment

**Hosting:**
- Primary: Vercel (auto-deploy on git push)
- Fallback: GitHub Pages or static hosting

**CI Pipeline:**
- GitHub Actions: `.github/workflows/update-schedule.yml`
  - Trigger: Daily schedule (0 12 * * *) + manual trigger
  - Steps:
    1. Checkout repository
    2. Setup Node.js 20
    3. Install `iconv-lite` dependency
    4. Run `node update_schedule.js`
    5. Commit and push if changes detected
    6. Auto-commit message: "Auto-update CBA schedule data [skip ci]"

**API Endpoint:**
- Path: `/api/schedule` (Vercel serverless function)
- Handler: `api/schedule.js` (Node.js)
- Response: JSON with `{ success, data, updated }` structure
- CORS: Enabled for all origins (`*`)

## Environment Configuration

**Required env vars:**
- None currently enforced

**Secrets location:**
- No secrets in codebase (no `.env` file)
- Vercel environment configuration (if needed in future)

## Data Flow

**Real-time (Deployed):**
1. Browser loads `cba_schedule.html`
2. Script checks: Is this deployed (non-localhost)?
3. If yes: Call `/api/schedule` endpoint
4. Vercel serverless function:
   - Fetches from `https://cba.sports.sina.com.cn/cba/schedule/all/`
   - Decodes GBK-encoded HTML via `decodeGBK()` function
   - Parses table rows via regex matching
   - Returns JSON with schedule array
5. Browser displays data and auto-refreshes every 60s
6. If API fails: Falls back to embedded `realSchedule` array

**Local/Offline:**
1. Browser loads `cba_schedule.html`
2. Script checks: Is this localhost?
3. If yes or if `USE_LIVE_API = false`:
   - Use `getEmbeddedScheduleData()` function
   - Returns processed `realSchedule` array
   - No API call made

**Manual Update (CLI):**
1. Developer runs: `node update_schedule.js`
2. Script fetches from Sina Sports
3. Parses HTML and extracts game data
4. Overwrites `realSchedule` array in `cba_script.js`
5. Updates timestamp comment: `最后更新: YYYY-MM-DD`
6. Developer commits and pushes changes

**Scheduled Update (GitHub Actions):**
1. Workflow triggers daily at 12:00 UTC
2. Runs same flow as manual update
3. Auto-commits if data changed (with `[skip ci]` flag)
4. Auto-pushes to master branch

## Game Status Determination

**Status Logic:**
- If score contains `:` and not `VS`: Status = "已结束" (ended)
- Else if game date = today: Status = "进行中" (in progress)
- Else if game date > today: Status = "未开始" (not started)
- Else: Status = "已结束" (ended, for past dates)

## Content Encoding Handling

**Browser Client:**
- Fetch API automatically handles text encoding in modern browsers
- Alternative: Can use `TextDecoder('utf-8')` if needed

**Node.js Server:**
- Uses `iconv-lite` package: `iconv.decode(buffer, 'gbk')`
- Converts GBK bytes to UTF-8 string

**Vercel Serverless:**
- Implements custom GBK decoder using `TextDecoder('gbk')` where available
- Falls back to byte-by-byte character code mapping (lines 47-84 in `api/schedule.js`)

## API Response Format

```json
{
  "success": true,
  "data": [
    {
      "round": "第28轮",
      "datetime": "2026-03-20 19:35",
      "home": "江苏",
      "score": "34:34",
      "away": "广东",
      "status": "已结束"
    }
  ],
  "updated": "2026-03-23T12:34:56.789Z"
}
```

## Webhooks & Callbacks

**Incoming:**
- None - This is a read-only data aggregation app

**Outgoing:**
- None - No external service notifications

---

*Integration audit: 2026-03-23*
