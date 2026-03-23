"""
Sina Sports CBA Schedule Scraper
Handles HTTP fetching and GBK encoding conversion (DATA-01)
"""

import requests
import chardet
from config import SINA_CBA_URL, SINA_USER_AGENT, REQUEST_TIMEOUT, REQUEST_RETRY_COUNT, REQUEST_RETRY_DELAY
from time import sleep
from typing import Optional


def fetch_sina_schedule() -> Optional[str]:
    """
    Fetch CBA schedule HTML from Sina Sports.

    Returns:
        str: Decoded HTML content (UTF-8) if successful
        None: If all retry attempts fail

    Raises:
        RuntimeError: If encoding detection or decoding fails
    """
    for attempt in range(1, REQUEST_RETRY_COUNT + 1):
        try:
            print(f"[Attempt {attempt}/{REQUEST_RETRY_COUNT}] Fetching from {SINA_CBA_URL}")

            # Fetch with proper headers
            headers = {
                'User-Agent': SINA_USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            }

            response = requests.get(
                SINA_CBA_URL,
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )

            response.raise_for_status()

            # Get raw bytes
            content_bytes = response.content

            if not content_bytes:
                print(f"[Attempt {attempt}] Empty response received")
                if attempt < REQUEST_RETRY_COUNT:
                    sleep(REQUEST_RETRY_DELAY)
                    continue
                return None

            # Try explicit GBK decode first (Sina Sports uses GBK encoding)
            try:
                html = content_bytes.decode('gbk')
                print(f"[Attempt {attempt}] Successfully decoded {len(html)} characters using GBK")
                return html
            except UnicodeDecodeError as gbk_error:
                # Fallback to chardet auto-detection
                print(f"[Attempt {attempt}] GBK decode failed: {gbk_error}, trying chardet...")

                detected = chardet.detect(content_bytes)
                detected_encoding = detected.get('encoding')
                confidence = detected.get('confidence', 0)

                if not detected_encoding:
                    raise RuntimeError("Could not detect encoding")

                print(f"[Attempt {attempt}] Detected encoding: {detected_encoding} (confidence: {confidence:.2f})")

                try:
                    html = content_bytes.decode(detected_encoding)
                    print(f"[Attempt {attempt}] Successfully decoded using {detected_encoding}")
                    return html
                except (UnicodeDecodeError, LookupError) as decode_error:
                    raise RuntimeError(f"Failed to decode with {detected_encoding}: {decode_error}")

        except requests.exceptions.Timeout as e:
            print(f"[Attempt {attempt}] Request timeout: {e}")
        except requests.exceptions.ConnectionError as e:
            print(f"[Attempt {attempt}] Connection error: {e}")
        except requests.exceptions.HTTPError as e:
            print(f"[Attempt {attempt}] HTTP error: {e}")
        except requests.exceptions.RequestException as e:
            print(f"[Attempt {attempt}] Request failed: {e}")
        except RuntimeError as e:
            print(f"[Attempt {attempt}] Encoding error: {e}")

        # Sleep between retries (except after last attempt)
        if attempt < REQUEST_RETRY_COUNT:
            print(f"[Attempt {attempt}] Retrying in {REQUEST_RETRY_DELAY} seconds...")
            sleep(REQUEST_RETRY_DELAY)

    print(f"[Failed] All {REQUEST_RETRY_COUNT} attempts exhausted")
    return None


if __name__ == '__main__':
    print("Testing Sina Sports CBA Schedule Scraper...")
    print("=" * 60)

    html = fetch_sina_schedule()

    if html:
        print("=" * 60)
        print("SUCCESS: HTML fetched and decoded")
        print(f"Total length: {len(html)} characters")
        print("=" * 60)
        print("First 500 characters:")
        print("-" * 60)
        print(html[:500])
        print("-" * 60)

        # Check for Chinese characters
        chinese_chars = [c for c in html[:1000] if '\u4e00' <= c <= '\u9fff']
        if chinese_chars:
            print(f"\nChinese character verification: PASSED ({len(chinese_chars)} characters found)")
            print(f"Sample: {''.join(chinese_chars[:20])}")
        else:
            print("\nWARNING: No Chinese characters found in first 1000 characters")
    else:
        print("=" * 60)
        print("FAILURE: Could not fetch HTML")
        print("=" * 60)
