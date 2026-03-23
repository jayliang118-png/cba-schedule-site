"""
Configuration for CBA Schedule Flask Application
"""

# Sina Sports scraping configuration
SINA_CBA_URL = 'https://cba.sports.sina.com.cn/cba/schedule/all/'
SINA_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Request timeout and retry settings
REQUEST_TIMEOUT = 10  # seconds
REQUEST_RETRY_COUNT = 3
REQUEST_RETRY_DELAY = 2  # seconds between retries

# Flask configuration
DEBUG = True
TEMPLATES_AUTO_RELOAD = True
