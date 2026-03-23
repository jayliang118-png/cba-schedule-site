"""
Deployment verification tests for Flask CBA schedule application.

These tests verify deployment readiness and post-deployment validation:
- WSGI export verification
- Required files exist
- Static file serving works
- Cold start simulation
- Environment compatibility
- Production URL verification (optional)
"""

import pytest
import json
import sys
import time
from pathlib import Path
from importlib import import_module, reload


class TestWSGIExport:
    """Test 1: WSGI export verification"""

    def test_app_is_importable(self):
        """Verify app.py can be imported"""
        import app
        assert app is not None

    def test_app_is_flask_instance(self):
        """Verify app is a Flask instance"""
        from flask import Flask
        import app
        assert isinstance(app.app, Flask)

    def test_app_is_callable(self):
        """Verify app is callable (WSGI requirement)"""
        import app
        assert callable(app.app)

    def test_app_has_wsgi_interface(self):
        """Verify app has WSGI interface"""
        import app
        # WSGI apps must be callable with (environ, start_response)
        assert hasattr(app.app, '__call__')


class TestRequiredFiles:
    """Test 2: Required files exist"""

    def test_vercel_json_exists(self):
        """Verify vercel.json exists"""
        assert Path('vercel.json').exists()

    def test_requirements_txt_exists(self):
        """Verify requirements.txt exists"""
        assert Path('requirements.txt').exists()

    def test_requirements_contains_flask(self):
        """Verify requirements.txt contains Flask"""
        content = Path('requirements.txt').read_text()
        assert 'Flask' in content or 'flask' in content

    def test_app_py_exists(self):
        """Verify app.py exists"""
        assert Path('app.py').exists()

    def test_templates_directory_exists(self):
        """Verify templates/ directory exists"""
        assert Path('templates').is_dir()

    def test_schedule_template_exists(self):
        """Verify templates/schedule.html exists"""
        assert Path('templates/schedule.html').exists()

    def test_static_directory_exists(self):
        """Verify static/ directory exists"""
        assert Path('static').is_dir()

    def test_schedule_json_exists(self):
        """Verify data/schedule.json exists"""
        assert Path('data/schedule.json').exists()

    def test_schedule_json_is_valid(self):
        """Verify data/schedule.json is valid JSON"""
        with open('data/schedule.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert isinstance(data, dict)
        assert 'schedule' in data


class TestStaticFileServing:
    """Test 3: Static file serving (local)"""

    @pytest.fixture
    def client(self):
        """Create Flask test client"""
        import app
        app.app.config['TESTING'] = True
        with app.app.test_client() as client:
            yield client

    def test_homepage_returns_200(self, client):
        """Request GET / and verify 200 response"""
        response = client.get('/')
        assert response.status_code == 200

    def test_homepage_contains_cba_content(self, client):
        """Verify response contains CBA content"""
        response = client.get('/')
        assert response.status_code == 200
        content = response.data.decode('utf-8')
        assert 'CBA' in content or 'cba' in content.lower()

    def test_api_schedule_returns_json(self, client):
        """Request GET /api/schedule and verify JSON response"""
        response = client.get('/api/schedule')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

    def test_api_schedule_has_correct_structure(self, client):
        """Verify /api/schedule returns correct JSON structure"""
        response = client.get('/api/schedule')
        data = json.loads(response.data)
        assert 'success' in data
        assert 'data' in data
        assert 'count' in data
        assert isinstance(data['data'], list)


class TestColdStartSimulation:
    """Test 4: Cold start simulation"""

    def test_app_import_time(self):
        """Verify import time < 2 seconds (cold start requirement)"""
        import sys
        # Remove app from cache to simulate cold start
        if 'app' in sys.modules:
            del sys.modules['app']

        start_time = time.time()
        import app
        import_time = time.time() - start_time

        assert import_time < 2.0, f"Import time {import_time:.2f}s exceeds 2s cold start requirement"

    def test_schedule_data_loads_successfully(self):
        """Verify schedule data loads successfully on import"""
        import app
        assert hasattr(app, 'SCHEDULE_DATA')
        assert isinstance(app.SCHEDULE_DATA, list)
        assert len(app.SCHEDULE_DATA) > 0, "Schedule data is empty"


class TestEnvironmentCompatibility:
    """Test 5: Environment compatibility"""

    def test_python_version(self):
        """Check Python version >= 3.11"""
        assert sys.version_info >= (3, 11), f"Python {sys.version_info.major}.{sys.version_info.minor} < 3.11"

    def test_flask_importable(self):
        """Verify Flask is importable"""
        import flask
        assert flask is not None

    def test_requests_importable(self):
        """Verify requests is importable"""
        import requests
        assert requests is not None

    def test_chardet_importable(self):
        """Verify chardet is importable"""
        import chardet
        assert chardet is not None

    def test_beautifulsoup_importable(self):
        """Verify beautifulsoup4 is importable"""
        from bs4 import BeautifulSoup
        assert BeautifulSoup is not None

    def test_no_missing_imports(self):
        """Verify no missing imports in app.py"""
        try:
            import app
            # If import succeeds, no missing imports
            assert True
        except ImportError as e:
            pytest.fail(f"Missing import in app.py: {e}")


class TestProductionURLVerification:
    """Test 6: Production URL verification (optional, requires deployment)"""

    @pytest.mark.skipif(
        'VERCEL_URL' not in __import__('os').environ,
        reason="VERCEL_URL environment variable not set"
    )
    def test_deployed_homepage_returns_200(self):
        """Make HTTP request to deployed URL"""
        import os
        import requests
        url = os.environ['VERCEL_URL']
        if not url.startswith('http'):
            url = f'https://{url}'
        response = requests.get(url, timeout=10)
        assert response.status_code == 200

    @pytest.mark.skipif(
        'VERCEL_URL' not in __import__('os').environ,
        reason="VERCEL_URL environment variable not set"
    )
    def test_deployed_api_returns_valid_json(self):
        """Verify /api/schedule returns valid JSON"""
        import os
        import requests
        url = os.environ['VERCEL_URL']
        if not url.startswith('http'):
            url = f'https://{url}'
        response = requests.get(f'{url}/api/schedule', timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert 'success' in data
        assert 'data' in data

    @pytest.mark.skipif(
        'VERCEL_URL' not in __import__('os').environ,
        reason="VERCEL_URL environment variable not set"
    )
    def test_deployed_schedule_count(self):
        """Verify schedule count > 0"""
        import os
        import requests
        url = os.environ['VERCEL_URL']
        if not url.startswith('http'):
            url = f'https://{url}'
        response = requests.get(f'{url}/api/schedule', timeout=10)
        data = response.json()
        assert data['count'] > 0, "Deployed schedule has no games"
