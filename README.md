# CBA Schedule Site (Flask Version)

A Flask-based CBA (Chinese Basketball Association) schedule query website with real-time data fetching, filtering capabilities, and automatic daily updates.

**Tech Stack:** Python 3.11+ | Flask 3.0.2 | Vercel Serverless | GitHub Actions

**Features:**
- Real-time schedule data from Sina Sports
- Multi-dimensional filtering (date, team, status)
- Responsive design (desktop table + mobile cards)
- Daily auto-updates via GitHub Actions
- RESTful JSON API endpoint

---

## Table of Contents

- [Local Development](#local-development)
- [Running Tests](#running-tests)
- [Deployment](#deployment)
- [Auto-Update Workflow](#auto-update-workflow)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Local Development

### Prerequisites

- **Python 3.11+** (required for compatibility)
- **pip** (Python package manager)
- **Virtual environment** (recommended)

### Setup

```bash
# Clone repository
git clone <repo-url>
cd cba-schedule-site

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Flask app
python app.py
# Or: flask run --port 5001

# Visit http://localhost:5001
```

### Development Server

The Flask development server runs on port 5001 by default:
- **Homepage:** `http://localhost:5001/`
- **API endpoint:** `http://localhost:5001/api/schedule`
- **API with filters:** `http://localhost:5001/api/schedule?team=广东&status=已结束`

### Project Structure

```
cba-schedule-site/
├── app.py                  # Flask application (main entry point)
├── config.py               # Configuration (Sina Sports URL, timeouts)
├── scraper.py              # Web scraper for Sina Sports
├── parser.py               # HTML parser for game data
├── filter_service.py       # Filtering logic (date/team/status)
├── update_schedule.py      # Manual schedule update script
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel deployment configuration
├── data/
│   └── schedule.json       # Embedded schedule data
├── templates/
│   ├── base.html           # Base template with common layout
│   └── schedule.html       # Main schedule page (Jinja2)
├── static/
│   ├── style.css           # Responsive styles (768px breakpoint)
│   └── script.js           # Client-side filtering logic
└── tests/
    ├── test_parser.py      # Parser unit tests
    ├── test_filtering.py   # Filtering integration tests
    └── test_deployment.py  # Deployment verification tests
```

---

## Running Tests

### Prerequisites

Tests use **pytest** and **pytest-cov** (included in requirements.txt).

### Run All Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=. --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

### Run Specific Test Suites

```bash
# Run parser tests only
pytest tests/test_parser.py -v

# Run filtering tests only
pytest tests/test_filtering.py -v

# Run deployment tests only
pytest tests/test_deployment.py -v

# Run tests by marker
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
```

### Test Coverage

Current coverage: **83%** (target: 80%+)
- `filter_service.py`: 100%
- `parser.py`: 100%
- `app.py`: 77%

### Deployment Verification Tests

The deployment test suite (`tests/test_deployment.py`) verifies:
- WSGI export and Flask instance
- Required files exist (vercel.json, requirements.txt, templates)
- Static file serving works
- Cold start performance (<2 seconds)
- Environment compatibility (Python 3.11+, all dependencies)
- Production URL verification (optional, requires `VERCEL_URL` env var)

Run deployment tests before deploying:
```bash
pytest tests/test_deployment.py -v
```

---

## Deployment

### Prerequisites

- **Vercel account** ([vercel.com](https://vercel.com))
- **Vercel CLI:** `npm install -g vercel`
- **Git repository** connected to GitHub

### First-Time Deployment

```bash
# Login to Vercel
vercel login

# Deploy to production
vercel --prod

# Follow prompts to link repository
# Choose defaults for most settings
```

### Automatic Deployment

**GitHub Integration (Recommended):**
- Push to `master` branch triggers automatic deployment
- Deployment takes ~1-2 minutes
- View status in Vercel dashboard

**Manual Deployment:**
```bash
# Deploy to preview environment
vercel

# Deploy to production
vercel --prod
```

### Deployment Configuration

See `vercel.json` for configuration details:

```json
{
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.11"
  },
  "regions": ["hkg1", "sin1"],
  "functions": {
    "app.py": {
      "maxDuration": 10,
      "memory": 1024
    }
  }
}
```

**Key Configuration:**
- **Python Runtime:** 3.11
- **Regions:** Hong Kong (`hkg1`) and Singapore (`sin1`) for optimal proximity to China
- **Timeout:** 10 seconds (allows time for Sina Sports scraping)
- **Memory:** 1GB (adequate for HTML parsing and data processing)

### Environment Variables

No environment variables are required for basic deployment. The application works out-of-the-box.

**Optional Environment Variables:**
- `VERCEL_URL`: Production URL (automatically set by Vercel, used for deployment tests)

### Verifying Deployment

After deployment completes:

1. **Check homepage:** Visit your Vercel URL (e.g., `https://cba-schedule.vercel.app`)
2. **Check API:** Visit `/api/schedule` endpoint
3. **Test filters:** Use query parameters: `/api/schedule?team=广东&status=已结束`
4. **Run production tests:** Set `VERCEL_URL` environment variable and run:
   ```bash
   export VERCEL_URL=https://your-app.vercel.app
   pytest tests/test_deployment.py -v
   ```

---

## Auto-Update Workflow

### GitHub Actions

Schedule updates run daily at **12:00 UTC (20:00 Beijing time)** via GitHub Actions.

**Workflow file:** `.github/workflows/update-schedule.yml`

**What it does:**
1. Fetches latest schedule from Sina Sports
2. Parses HTML and extracts game data
3. Updates `data/schedule.json`
4. Commits and pushes changes
5. Triggers automatic Vercel redeployment

### Manual Update

To manually update the schedule:

```bash
# Activate virtual environment
source venv/bin/activate

# Run update script
python update_schedule.py

# Commit and push changes
git add data/schedule.json
git commit -m "Update schedule data"
git push
```

The Vercel deployment will automatically trigger after pushing.

### Monitoring

**GitHub Actions:**
- Visit the **Actions** tab in your GitHub repository
- View workflow runs, logs, and status
- Debug failures by checking step-by-step logs

**Vercel:**
- Visit the **Vercel Dashboard**
- Check deployment status and logs
- View function invocation logs for debugging

**Data Freshness:**
- Check the `updated` timestamp in `/api/schedule` response
- Verify game count matches expected schedule length

---

## Architecture

### Data Flow

```
Sina Sports (GBK-encoded HTML)
    ↓
scraper.py (fetch + decode)
    ↓
parser.py (extract game data)
    ↓
data/schedule.json (embedded data)
    ↓
app.py (Flask routes)
    ↓
templates/schedule.html (Jinja2 rendering)
    ↓
User's Browser
```

### Flask Application Structure

**`app.py`** - Main Flask application
- **Route:** `/` - Homepage (renders `templates/schedule.html` with full schedule)
- **Route:** `/api/schedule` - JSON API with optional filtering
- **CORS:** Enabled for cross-origin requests
- **Error Handling:** 404 and 500 error handlers with JSON responses

**`config.py`** - Configuration centralization
- Sina Sports URL
- HTTP request timeouts and retries
- User agent configuration

**`scraper.py`** - Web scraping logic
- Fetches HTML from Sina Sports
- Handles GBK encoding (Chinese character support)
- Retry logic with exponential backoff
- Error handling for network failures

**`parser.py`** - HTML parsing logic
- BeautifulSoup CSS selectors for robust parsing
- Extracts: date, home team, away team, scores, venue
- Handles missing data gracefully
- Returns structured JSON format

**`filter_service.py`** - Filtering logic
- **Date filtering:** Exact date match (YYYY-MM-DD format)
- **Team filtering:** Matches home or away team (partial match)
- **Status filtering:** Filters by game status (未开始, 进行中, 已结束)
- **Combined filters:** AND logic (intersection of all filters)

**`update_schedule.py`** - Manual update script
- Fetches latest schedule from Sina Sports
- Updates `data/schedule.json`
- Used by GitHub Actions for daily auto-updates

### Frontend Architecture

**`templates/base.html`** - Base template
- Common layout, meta tags, CSS/JS includes
- Responsive design foundation

**`templates/schedule.html`** - Main schedule page
- Extends `base.html`
- Filter controls (date, team, status)
- Schedule table (desktop view) with responsive cards (mobile view)
- Client-side JavaScript for dynamic filtering

**`static/style.css`** - Responsive styles
- Desktop table layout (>768px)
- Mobile card layout (<768px)
- CBA branding colors

**`static/script.js`** - Client-side filtering
- Fetches data from `/api/schedule` with query parameters
- Async/await pattern for clean asynchronous flow
- Immutable DOM rendering (always rebuild from API response)
- URLSearchParams for query string construction

### Data Format

**`data/schedule.json`** structure:
```json
{
  "updated": "2026-03-23T10:30:00Z",
  "schedule": [
    {
      "date": "2025-10-20",
      "homeTeam": "广东",
      "awayTeam": "辽宁",
      "homeScore": 98,
      "awayScore": 92,
      "venue": "东莞篮球中心",
      "status": "已结束"
    }
  ]
}
```

### Filtering Logic

**Server-side filtering** (`/api/schedule?date=X&team=Y&status=Z`):
- Filters applied in `filter_service.py`
- Multiple filters use AND logic (intersection)
- Returns filtered JSON response

**Client-side filtering** (`static/script.js`):
- Reads filter form inputs
- Constructs API request with query parameters
- Renders filtered results in table/cards

---

## Troubleshooting

### Common Issues

#### Deployment Fails

**Symptom:** Vercel deployment fails with build errors

**Solutions:**
1. Check `vercel.json` syntax with `python3 -m json.tool vercel.json`
2. Verify `requirements.txt` lists all dependencies
3. Ensure `app.py` is at project root
4. Check Vercel build logs for specific error messages

#### Schedule Not Updating

**Symptom:** Auto-update workflow fails or schedule data is stale

**Solutions:**
1. Check GitHub Actions workflow logs in **Actions** tab
2. Verify Sina Sports URL is accessible: `curl https://cba.sports.sina.com.cn/cba/schedule/all/`
3. Run `python update_schedule.py` locally to test scraper
4. Check for HTML structure changes on Sina Sports website

#### 500 Errors on Deployed App

**Symptom:** Deployed app returns 500 Internal Server Error

**Solutions:**
1. Check Vercel function logs in **Vercel Dashboard → Functions → Logs**
2. Verify `data/schedule.json` is valid JSON: `python3 -m json.tool data/schedule.json`
3. Check for missing dependencies in `requirements.txt`
4. Test locally with `python app.py` and reproduce the error

#### Slow Response Times

**Symptom:** API endpoint takes >2 seconds to respond

**Solutions:**
1. Verify Vercel region configuration in `vercel.json` (should be `hkg1` or `sin1`)
2. Check if Sina Sports website is responding slowly
3. Consider increasing `maxDuration` in `vercel.json` if scraping takes longer
4. Monitor Vercel function execution time in dashboard

#### GBK Encoding Issues

**Symptom:** Chinese characters display as garbled text (乱码)

**Solutions:**
1. Verify `scraper.py` uses `.decode('gbk')` or `.decode('gb2312')`
2. Check `chardet` library is installed: `pip show chardet`
3. Test encoding detection locally: `python -c "import chardet; print(chardet.detect(html_bytes))"`
4. Ensure `data/schedule.json` is saved with UTF-8 encoding

#### Tests Failing

**Symptom:** `pytest` tests fail locally

**Solutions:**
1. Activate virtual environment: `source venv/bin/activate`
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python version: `python3 --version` (must be 3.11+)
4. Run specific failing test with verbose output: `pytest tests/test_file.py::test_name -vv`
5. Check if `data/schedule.json` exists and is valid

#### Cold Start Timeout

**Symptom:** First request after deployment times out

**Solutions:**
1. Verify `maxDuration` in `vercel.json` is at least 10 seconds
2. Check `memory` allocation is sufficient (1024 MB recommended)
3. Optimize imports in `app.py` (avoid heavy imports at module level)
4. Test cold start locally: `pytest tests/test_deployment.py::TestColdStartSimulation -v`

---

## API Reference

### GET `/api/schedule`

Returns CBA schedule data as JSON with optional filtering.

**Query Parameters:**
- `date` (optional): Filter by exact date in `YYYY-MM-DD` format
- `team` (optional): Filter by team name (matches home or away team)
- `status` (optional): Filter by game status (`未开始`, `进行中`, `已结束`)

**Response Format:**
```json
{
  "success": true,
  "data": [
    {
      "date": "2025-10-20",
      "homeTeam": "广东",
      "awayTeam": "辽宁",
      "homeScore": 98,
      "awayScore": 92,
      "venue": "东莞篮球中心",
      "status": "已结束"
    }
  ],
  "count": 1,
  "updated": "2026-03-23T10:30:00Z"
}
```

**Examples:**
```bash
# Get all games
curl https://your-app.vercel.app/api/schedule

# Filter by team
curl "https://your-app.vercel.app/api/schedule?team=广东"

# Filter by date
curl "https://your-app.vercel.app/api/schedule?date=2025-10-20"

# Filter by status
curl "https://your-app.vercel.app/api/schedule?status=已结束"

# Combine filters (AND logic)
curl "https://your-app.vercel.app/api/schedule?team=广东&status=已结束"
```

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Write tests** for new functionality (maintain 80%+ coverage)
4. **Run tests** locally: `pytest --cov=. --cov-report=term-missing`
5. **Commit** changes: `git commit -m "feat: add your feature"`
6. **Push** to branch: `git push origin feature/your-feature`
7. **Open** a Pull Request

### Code Quality Checklist

Before submitting PRs:
- [ ] All tests pass (`pytest`)
- [ ] Code coverage ≥80% (`pytest --cov`)
- [ ] Deployment tests pass (`pytest tests/test_deployment.py`)
- [ ] No console.log statements in production code
- [ ] Follows immutability patterns (no in-place mutations)
- [ ] Error handling for all external API calls
- [ ] Chinese characters display correctly (GBK encoding handled)

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Data Source:** [Sina Sports CBA Database](https://cba.sports.sina.com.cn/cba/)
- **Hosting:** [Vercel](https://vercel.com)
- **Framework:** [Flask](https://flask.palletsprojects.com/)
- **CI/CD:** [GitHub Actions](https://github.com/features/actions)

---

**Maintained by:** [Your Name/Organization]

**Questions?** Open an issue on GitHub.
