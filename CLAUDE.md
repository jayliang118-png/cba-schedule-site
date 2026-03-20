# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CBA (Chinese Basketball Association) schedule query website - a static site displaying game schedules with filtering capabilities.

## Development

No build process required. This is a static site with vanilla HTML/CSS/JS.

**Local development:**
- Open `cba_schedule.html` directly in a browser, or
- Use any static server: `npx serve .` or `python -m http.server 8000`

## Architecture

- `cba_schedule.html` - Main page with filter controls and schedule table
- `cba_script.js` - All JavaScript logic including:
  - `CBA_TEAMS` - Array of 20 CBA team names
  - `TEAM_VENUES` - Maps teams to their home venues
  - `generateMockSchedule()` - Creates simulated game data
  - Filter functions: `filterByDate()`, `filterByTeam()`, `filterByStatus()`
  - Real-time update simulation via `setInterval(simulateLiveUpdate, 30000)`
- `cba_style.css` - Responsive styles with mobile card layout (breakpoint: 768px)
- `vercel.json` - Deployment config routing all paths to main HTML

## Deployment

Deployed to Vercel with GitHub auto-deploy. Push to `master` branch triggers automatic deployment.