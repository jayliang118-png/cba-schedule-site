# Technology Stack

**Analysis Date:** 2026-03-23

## Languages

**Primary:**
- JavaScript (ES6+) - Client-side UI logic and data processing
- HTML5 - Page structure and semantic markup
- CSS3 - Responsive styling with flexbox and media queries

**Secondary:**
- Node.js JavaScript - Backend data fetching and parsing scripts

## Runtime

**Environment:**
- Web Browser (Client) - ES5+ support with Fetch API
- Node.js 20+ (Server) - For `update_schedule.js` CLI tool
- Vercel Serverless Functions (Production API)

**Package Manager:**
- npm 10+ (implied by Node.js 20 in GitHub Actions)
- Lockfile: Not present (`package-lock.json` or `yarn.lock` not committed)

## Frameworks

**Core:**
- Vanilla JavaScript - No framework used; all DOM manipulation via native APIs
- HTML/CSS only - No React, Vue, or other frontend framework

**Build/Dev:**
- No build process - Static files served directly
- GitHub Actions - CI/CD for scheduled data updates

## Key Dependencies

**Runtime:**
- `iconv-lite` (NPM package) - GBK encoding/decoding for Sina Sports HTML parsing
  - Used in: `update_schedule.js` (Node.js script), optional at runtime
  - Why critical: Sina Sports serves GBK-encoded Chinese content; iconv-lite handles conversion to UTF-8

**No other production dependencies** - Pure vanilla JS with Fetch API

## Configuration

**Environment:**
- No `.env` file required - No hardcoded API keys or secrets
- Configuration based on window location: `USE_LIVE_API` flag auto-enables when deployed to non-localhost

**Build:**
- `vercel.json` - Vercel routing configuration (rewrites for SPA and API endpoints)

## Platform Requirements

**Development:**
- Node.js 20+ (for running `update_schedule.js`)
- npm (for installing `iconv-lite`)
- Modern web browser with ES6+ support

**Production:**
- Vercel hosting platform (Node.js runtime for `/api/schedule` serverless function)
- No database required - All data embedded in `cba_script.js` or fetched from Sina Sports

## Local Development

**Static serving:**
- Open `cba_schedule.html` directly in browser, or
- Use any static server: `npx serve .` or `python -m http.server 8000`

**Data update:**
```bash
npm install iconv-lite
node update_schedule.js
# Updates embedded data in cba_script.js
```

## Deployment

**Vercel:**
- Configured via `vercel.json` with URL rewrites
- GitHub auto-deploy on push to `master` branch
- Serverless API endpoint: `/api/schedule` (Node.js handler at `api/schedule.js`)

**GitHub Actions:**
- Scheduled workflow: Daily at 12:00 UTC (20:00 Beijing time)
- Runs `npm install iconv-lite && node update_schedule.js`
- Auto-commits and pushes updates if schedule data changes

---

*Stack analysis: 2026-03-23*
