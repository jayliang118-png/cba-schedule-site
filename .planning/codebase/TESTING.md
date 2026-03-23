# Testing Patterns

**Analysis Date:** 2026-03-23

## Current State

**No automated tests detected.** The codebase has:
- No test framework installed (no Jest, Vitest, Mocha config)
- No `*.test.js` or `*.spec.js` files
- No test runner configured in package.json (package.json missing)
- Manual testing via browser or static server only

## Recommended Test Framework Setup

**Browser Testing (for `cba_script.js`):**
- Framework: Jest or Vitest
- Assertion Library: jest.expect or chai
- Run Commands:
  ```bash
  npm run test              # Run all tests
  npm run test:watch       # Watch mode
  npm run test:coverage    # Coverage report
  ```

**Node.js Testing (for `update_schedule.js`):**
- Framework: Jest with Node environment
- Mock dependencies: `https`, `fs`, `iconv-lite`

**Vercel API Testing:**
- Framework: Supertest or native Node.js test runner
- Environment: Node.js with mocked fetch API

## Components Requiring Tests

### Browser Module: `cba_script.js`

**Core Functions to Test:**

1. **Data Processing:**
   - `processScheduleData(rawData)` - Maps API response to game objects
     - Input: Array of raw schedule objects
     - Output: Sorted array of game objects
     - Test edge cases: missing fields, null values, invalid dates

   - `getEmbeddedScheduleData()` - Normalizes embedded data
     - Input: Internal realSchedule array
     - Output: Processed game objects with metadata
     - Test: All games get id, date parsing, week day calculation

2. **Date/Time Utilities:**
   - `formatDate(date)` - Returns YYYY-MM-DD format
     - Test: Single digits padded (01 not 1)
     - Test: Year/month/day extraction

   - `getWeekDay(date)` - Returns Chinese day name
     - Test: Sunday-Saturday mapping to 周日-周六
     - Test: All days of week

3. **Filtering Functions:**
   - `filterByDate(dateStr)` - Shows games for specific date
     - Test: Empty string shows all games
     - Test: Valid date filters correctly
     - Test: Invalid date returns empty array
     - Test: Calls displaySchedule as side effect

   - `filterByTeam(teamName)` - Shows home/away games for team
     - Test: Empty string shows all
     - Test: Team appears as home or away team
     - Test: Invalid team returns empty
     - Test: Multiple games per team

   - `filterByStatus(status)` - Filters by status
     - Test: "已结束", "进行中", "未开始" each return correct subset
     - Test: "全部" or empty returns all

4. **Display Functions:**
   - `displaySchedule(games)` - Renders table
     - Test: Clears tableBody
     - Test: Creates TR for each game
     - Test: Empty array shows "no results" message
     - Test: Calls updateStats with filtered games
     - Mock: document.getElementById, DOM manipulation

   - `getStatusClass(status)` - Returns CSS class
     - Test: Maps status strings to class names
     - Test: Unknown status defaults to 'upcoming'

5. **Game Interaction:**
   - `showGameDetail(gameId)` - Displays modal
     - Test: Finds correct game by id
     - Test: Updates modalContent HTML
     - Test: Sets modal.style.display = 'block'

   - `setReminder(gameId)` - Placeholder reminder function
     - Test: Finds game and shows alert with details

6. **Initialization:**
   - `initFilters()` - Sets up filter UI
     - Test: Populates team dropdown from CBA_TEAMS
     - Test: Binds change events to filter functions
     - Test: Reset button clears all inputs

   - `initCBA()` - Application startup
     - Test: Calls fetchRealSchedule
     - Test: Calls initFilters
     - Test: Calls displaySchedule
     - Test: Sets 60-second refresh interval

### Node.js Module: `update_schedule.js`

**Functions to Test:**

1. **Network Request Handling:**
   - Fetches from `https://cba.sports.sina.com.cn/cba/schedule/all/`
   - Test: HTTP headers include User-Agent
   - Test: Handles HTTPS connection
   - Mock: https.get, fs.readFileSync, fs.writeFileSync

2. **HTML Parsing:**
   - Regex pattern: `/<div class="part part02[^>]*>(.*?)<\/div>\s*<\/div>\s*<!-- part02 end/s`
   - Regex pattern: `/<tr[^>]*class="(odd|even)"[^>]*>(.*?)<\/tr>/gs`
   - Test: Extracts correct table section
   - Test: Parses all table rows
   - Test: Handles GBK encoding via iconv-lite

3. **Data Extraction:**
   - Splits game data into: round, datetime, home, score, away, status
   - Test: Correctly maps 5 columns
   - Test: Handles HTML entities: `&nbsp;`, `&#58;`
   - Test: Strips all HTML tags

4. **Status Determination:**
   - Logic: score with `:` = ended, today's date = live, future = upcoming
   - Test: Finished game has score (e.g., "85:93")
   - Test: Today's game marked as "进行中"
   - Test: Future game marked as "未开始"

5. **File Updates:**
   - Updates `cba_script.js` with new schedule
   - Regex replacement: `const realSchedule = [...];`
   - Regex replacement: Updates date comment `最后更新: YYYY-MM-DD`
   - Test: preserves file structure
   - Test: updates both date and data
   - Test: valid JavaScript output

### Vercel API: `api/schedule.js`

**Functions to Test:**

1. **Request Handler:**
   - `handler(req, res)` - Main entry point
   - Test: Only GET method allowed
   - Test: Returns 405 for POST/PUT/DELETE
   - Test: Sets CORS headers

2. **GBK Decoding:**
   - `decodeGBK(buffer)` - Converts GBK bytes to UTF-8 string
   - Test: ASCII bytes pass through (< 0x80)
   - Test: GBK multi-byte sequences decoded
   - Test: Invalid sequences produce "?"

3. **HTML Parsing:**
   - `parseSchedule(html)` - Identical to update_schedule.js
   - Test: Extracts table correctly
   - Test: Handles all row types
   - Test: Status logic matches Node version

## Test Data

**Embedded Test Schedule:**
Use subset of realSchedule array from `cba_script.js` (lines 109-203):

```javascript
const testGames = [
  { round: '第27轮', datetime: '2026-03-17 19:35', home: '广东', score: '111:89', away: '新疆', status: '已结束' },
  { round: '第28轮', datetime: '2026-03-21 19:35', home: '宁波', score: 'VS', away: '广州', status: '未开始' },
  { round: '第28轮', datetime: '2026-03-20 19:35', home: '江苏', score: '34:34', away: '广东', status: '已结束' }
];
```

**Fixtures Location:**
- Create `__tests__/fixtures/scheduleData.js`
- Create `__tests__/fixtures/htmlResponses.js` for mock Sina Sports HTML

## Mock Patterns

**Browser DOM Mocking:**
```javascript
// Mock document methods
const mockElement = {
  innerHTML: '',
  style: { display: 'block' },
  addEventListener: jest.fn(),
  appendChild: jest.fn()
};
document.getElementById = jest.fn(() => mockElement);
document.createElement = jest.fn(() => mockElement);
```

**Fetch Mocking:**
```javascript
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({
      success: true,
      data: testGames
    })
  })
);
```

**File System Mocking:**
```javascript
jest.mock('fs', () => ({
  readFileSync: jest.fn(() => scriptContent),
  writeFileSync: jest.fn()
}));
```

**HTTP Request Mocking:**
```javascript
jest.mock('https');
https.get = jest.fn((options, callback) => {
  callback({
    on: jest.fn((event, handler) => {
      if (event === 'data') handler(gzkBuffer);
      if (event === 'end') handler();
    })
  });
});
```

## Coverage Targets

**Current Coverage:** 0% (no tests)

**Target:** 80%+ before production deployment

**Priority Coverage:**
1. **CRITICAL** - Data processing: `processScheduleData()`, parsing logic
2. **CRITICAL** - Status determination (finished/live/upcoming logic)
3. **HIGH** - Filter functions (user-facing features)
4. **HIGH** - Display functions (DOM rendering)
5. **MEDIUM** - Utility functions (date formatting, week day)
6. **MEDIUM** - Error handling paths

**Excluded from Coverage:**
- Global initialization: `document.addEventListener('DOMContentLoaded', initCBA)`
- Browser-only APIs: exact DOM API calls in display functions
- Legacy browser compatibility

## Test Organization

**File Structure:**
```
__tests__/
├── unit/
│   ├── cba_script.test.js        # Browser module tests
│   ├── update_schedule.test.js   # Node.js script tests
│   └── api_schedule.test.js      # Vercel API tests
├── fixtures/
│   ├── scheduleData.js           # Test game data
│   └── htmlResponses.js          # Mock HTML from Sina Sports
└── setup.js                      # Jest configuration
```

**Configuration:**
- Jest config in `jest.config.js`:
  ```javascript
  module.exports = {
    testEnvironment: 'jsdom',     // For browser tests
    coverageThreshold: {
      global: { branches: 80, functions: 80, lines: 80, statements: 80 }
    }
  };
  ```

## Testing Edge Cases

**Date/Time Edge Cases:**
- Leap year dates (Feb 29)
- Year boundary transitions
- Timezone handling for game status

**Data Edge Cases:**
- Empty schedule array
- Duplicate games
- Games with missing fields
- Malformed datetime strings
- Invalid team names

**API Edge Cases:**
- Network timeout
- Partial response received
- Malformed JSON
- GBK encoding errors
- Missing table in HTML

---

*Testing analysis: 2026-03-23*
