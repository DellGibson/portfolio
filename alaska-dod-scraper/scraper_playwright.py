#!/usr/bin/env python3
"""
Alaska DoD Scraper - Playwright Version

Enhanced scraper using Playwright for better success rate against bot detection.
Playwright uses real browser automation, making it much harder to detect.

Installation:
    pip install playwright playwright-stealth
    playwright install chromium

Usage:
    python scraper_playwright.py
"""

import json
import re
import time
import random
from datetime import datetime
from typing import Dict, List, Optional
import logging

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠ Playwright not installed. Install with: pip install playwright && playwright install chromium")

from bs4 import BeautifulSoup
import pandas as pd


# Configuration
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
]

TARGET_KEYWORDS = [
    'adventure', 'outdoor', 'wilderness', 'unique', 'remote',
    'tight-knit', 'community', 'alaska', 'frontier', 'mission',
    'camaraderie', 'stability', 'flexibility'
]

TARGET_URLS = {
    'Coast Guard': [
        'https://www.gocoastguard.com/active-duty-careers/enlisted-opportunities/view-job-descriptions',
        'https://www.gocoastguard.com/about-the-coast-guard/discover-our-roles-missions/alaska-region',
    ],
    'Air Force': [
        'https://www.airforce.com/find-a-recruiter',
        'https://www.jber.jb.mil/News/',
    ],
    'Navy': [
        'https://www.navy.com/local',
    ],
    'Marines': [
        'https://www.marines.com/contact-a-recruiter',
    ],
}

ALASKA_DUTY_STATIONS = [
    'JBER', 'Joint Base Elmendorf-Richardson', 'Elmendorf', 'Richardson',
    'Kodiak', 'Sitka', 'Ketchikan', 'Juneau', 'Fairbanks', 'Anchorage',
    'Eielson', 'Fort Wainwright', 'Fort Greely', 'Clear Space Force Station',
]


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping_errors.txt'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PlaywrightScraper:
    """Enhanced scraper using Playwright for better bot evasion."""

    def __init__(self, headless: bool = True, slow_mo: int = 100):
        """
        Initialize Playwright scraper.

        Args:
            headless: Run browser in headless mode (True) or visible (False for debugging)
            slow_mo: Milliseconds to slow down operations (helps avoid detection)
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright not installed")

        self.headless = headless
        self.slow_mo = slow_mo
        self.results = {
            'scrape_metadata': {
                'date': datetime.now().isoformat(),
                'target_state': 'Alaska',
                'branches_scraped': [],
                'total_pages': 0,
                'successful_scrapes': 0,
                'failed_scrapes': 0,
                'scraper_version': 'Playwright v1.0'
            },
            'competitors': []
        }
        self.errors = []

    def fetch_page(self, url: str, wait_for: str = 'networkidle') -> Optional[str]:
        """
        Fetch page using Playwright with anti-detection measures.

        Args:
            url: URL to fetch
            wait_for: Wait condition ('networkidle', 'load', 'domcontentloaded')

        Returns:
            HTML content or None if failed
        """
        try:
            logger.info(f"Fetching {url} with Playwright...")

            with sync_playwright() as p:
                # Launch browser with stealth settings
                browser = p.chromium.launch(
                    headless=self.headless,
                    slow_mo=self.slow_mo,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                    ]
                )

                # Create context with realistic settings
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent=random.choice(USER_AGENTS),
                    locale='en-US',
                    timezone_id='America/Anchorage',
                    geolocation={'latitude': 61.2181, 'longitude': -149.9003},  # Anchorage
                    permissions=['geolocation'],
                    color_scheme='light',
                )

                # Additional stealth measures
                context.add_init_script("""
                    // Override navigator.webdriver
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });

                    // Mock plugins
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });

                    // Mock languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });

                    // Chrome-specific
                    window.chrome = {
                        runtime: {}
                    };
                """)

                page = context.new_page()

                # Set extra headers
                page.set_extra_http_headers({
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                })

                # Increase timeout for .mil sites
                timeout = 30000 if '.mil' in url else 20000

                try:
                    # Navigate to page
                    response = page.goto(url, wait_until=wait_for, timeout=timeout)

                    if response.status >= 400:
                        logger.error(f"✗ HTTP {response.status} for {url}")
                        browser.close()
                        return None

                    # Random human-like delay
                    time.sleep(random.uniform(2, 4))

                    # Scroll page to trigger lazy-loaded content
                    page.evaluate("""
                        window.scrollTo(0, document.body.scrollHeight / 3);
                    """)
                    time.sleep(0.5)

                    page.evaluate("""
                        window.scrollTo(0, document.body.scrollHeight * 2 / 3);
                    """)
                    time.sleep(0.5)

                    page.evaluate("""
                        window.scrollTo(0, document.body.scrollHeight);
                    """)
                    time.sleep(1)

                    # Scroll back to top
                    page.evaluate("window.scrollTo(0, 0);")
                    time.sleep(0.5)

                    # Get final HTML
                    html = page.content()

                    browser.close()

                    logger.info(f"✓ Successfully fetched {url}")
                    return html

                except PlaywrightTimeout:
                    logger.error(f"✗ Timeout fetching {url}")
                    browser.close()
                    self.errors.append({
                        'url': url,
                        'error': 'Timeout',
                        'timestamp': datetime.now().isoformat()
                    })
                    return None

        except Exception as e:
            logger.error(f"✗ Error fetching {url}: {str(e)}")
            self.errors.append({
                'url': url,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            return None

    def extract_data(self, html: str, url: str) -> Dict:
        """Extract all intelligence data from HTML (same as original scraper)."""
        soup = BeautifulSoup(html, 'lxml')

        return {
            'url': url,
            'page_title': soup.title.string if soup.title else 'No title',
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'alaska_mentions': self.extract_alaska_mentions(html, url),
            'bonuses': self.extract_bonuses(html),
            'duty_stations_listed': self.extract_duty_stations(html),
            'lifestyle_messaging': self.extract_lifestyle_messaging(html),
            'headlines': self.extract_headlines(html),
            'ctas': self.extract_ctas(html, url),
            'testimonials': self.extract_testimonials(html),
            'keyword_frequencies': self.extract_keywords(html)
        }

    # Copy extraction methods from original scraper
    def extract_alaska_mentions(self, html: str, url: str) -> Dict:
        soup = BeautifulSoup(html, 'lxml')
        for script in soup(['script', 'style']):
            script.decompose()
        text = soup.get_text(separator=' ', strip=True)
        alaska_pattern = re.compile(r'([^.!?]*\balaska\b[^.!?]*[.!?])', re.IGNORECASE)
        contexts = alaska_pattern.findall(text)
        contexts = [c.strip() for c in contexts if len(c.strip()) > 10]
        return {'count': len(contexts), 'contexts': contexts[:20]}

    def extract_bonuses(self, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'lxml')
        bonuses = []
        dollar_pattern = re.compile(r'\$[\d,]+(?:\.\d{2})?')
        bonus_keywords = ['bonus', 'incentive', 'sign-on', 'enlistment', 'loan repayment']
        for paragraph in soup.find_all(['p', 'div', 'li']):
            para_text = paragraph.get_text(strip=True)
            if any(keyword in para_text.lower() for keyword in bonus_keywords):
                amounts = dollar_pattern.findall(para_text)
                if amounts:
                    alaska_specific = 'alaska' in para_text.lower()
                    bonuses.append({
                        'amount': amounts[0] if len(amounts) == 1 else 'varies',
                        'context': para_text[:200],
                        'alaska_specific': alaska_specific,
                        'needs_manual_review': len(amounts) > 3
                    })
        return bonuses

    def extract_duty_stations(self, html: str) -> List[str]:
        soup = BeautifulSoup(html, 'lxml')
        text = soup.get_text(separator=' ', strip=True).lower()
        found_stations = []
        for station in ALASKA_DUTY_STATIONS:
            if station.lower() in text:
                found_stations.append(station)
        return list(set(found_stations))

    def extract_keywords(self, html: str) -> Dict[str, int]:
        soup = BeautifulSoup(html, 'lxml')
        text = soup.get_text(separator=' ', strip=True).lower()
        frequencies = {}
        for keyword in TARGET_KEYWORDS:
            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            frequencies[keyword] = len(pattern.findall(text))
        return frequencies

    def extract_lifestyle_messaging(self, html: str) -> Dict[str, bool]:
        soup = BeautifulSoup(html, 'lxml')
        text = soup.get_text(separator=' ', strip=True).lower()
        return {
            'outdoor_emphasis': any(word in text for word in ['outdoor', 'hiking', 'fishing', 'wildlife', 'nature']),
            'remote_pay_mentioned': any(phrase in text for phrase in ['remote pay', 'cola', 'cost of living allowance', 'hardship pay']),
            'community_tight_knit': any(phrase in text for phrase in ['tight-knit', 'close community', 'small community', 'family-like']),
            'family_support': any(word in text for word in ['family', 'spouse', 'childcare', 'schools', 'housing']),
        }

    def extract_headlines(self, html: str) -> List[str]:
        soup = BeautifulSoup(html, 'lxml')
        headlines = []
        for tag in soup.find_all(['h1', 'h2']):
            text = tag.get_text(strip=True)
            if text and len(text) > 5:
                headlines.append(text)
        return headlines

    def extract_ctas(self, html: str, base_url: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'lxml')
        ctas = []
        cta_keywords = ['apply', 'join', 'talk', 'contact', 'recruiter', 'learn more', 'get started', 'enlist']
        for link in soup.find_all('a', href=True):
            text = link.get_text(strip=True)
            if any(keyword in text.lower() for keyword in cta_keywords):
                position = 'above_fold' if len(ctas) < 5 else 'below_fold'
                from urllib.parse import urljoin
                href = urljoin(base_url, link['href']) if not link['href'].startswith('http') else link['href']
                ctas.append({'text': text, 'url': href, 'position': position})
        return ctas[:10]

    def extract_testimonials(self, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'lxml')
        testimonials = []
        quote_elements = soup.find_all(['blockquote', 'div', 'p'], class_=re.compile(r'testimonial|quote|review', re.I))
        for element in quote_elements:
            text = element.get_text(strip=True)
            if len(text) > 50:
                rank_pattern = re.compile(r'\b(Seaman|Petty Officer|Chief|Lieutenant|Captain|Major|Colonel|Sergeant|Corporal|Private|Airman)\b', re.I)
                rank_match = rank_pattern.search(text)
                alaska_related = 'alaska' in text.lower()
                testimonials.append({
                    'text': text[:300],
                    'rank_name': rank_match.group(0) if rank_match else 'Unknown',
                    'location': 'Alaska' if alaska_related else 'Unknown',
                    'alaska_related': alaska_related
                })
        return testimonials

    def scrape_branch(self, branch: str, urls: List[str]) -> Dict:
        """Scrape all URLs for a branch."""
        logger.info(f"\n{'='*60}")
        logger.info(f"Scraping {branch}")
        logger.info(f"{'='*60}")

        branch_data = {
            'branch': branch,
            'alaska_pages': [],
            'recruiter_contacts': []
        }

        for url in urls:
            self.results['scrape_metadata']['total_pages'] += 1

            # Random delay between requests
            time.sleep(random.uniform(3, 7))

            html = self.fetch_page(url)

            if html is None:
                self.results['scrape_metadata']['failed_scrapes'] += 1
                continue

            self.results['scrape_metadata']['successful_scrapes'] += 1

            # Extract data
            page_data = self.extract_data(html, url)
            branch_data['alaska_pages'].append(page_data)

        return branch_data

    def scrape_all_branches(self):
        """Main scraping workflow."""
        logger.info("Starting Alaska DoD Competitor Intelligence Scrape (Playwright)")
        logger.info(f"Target: {self.results['scrape_metadata']['target_state']}")
        logger.info(f"Date: {self.results['scrape_metadata']['date']}\n")

        for branch, urls in TARGET_URLS.items():
            branch_data = self.scrape_branch(branch, urls)
            self.results['competitors'].append(branch_data)
            self.results['scrape_metadata']['branches_scraped'].append(branch)

            # Save partial results
            self.save_json_output(filename='alaska_competitor_data_partial.json')

        logger.info(f"\n{'='*60}")
        logger.info("Scraping Complete!")
        logger.info(f"Total pages attempted: {self.results['scrape_metadata']['total_pages']}")
        logger.info(f"Successful: {self.results['scrape_metadata']['successful_scrapes']}")
        logger.info(f"Failed: {self.results['scrape_metadata']['failed_scrapes']}")
        logger.info(f"Success Rate: {(self.results['scrape_metadata']['successful_scrapes'] / self.results['scrape_metadata']['total_pages'] * 100):.1f}%")
        logger.info(f"{'='*60}\n")

    def save_json_output(self, filename: str = 'alaska_competitor_data.json'):
        """Save results to JSON."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Saved JSON output to {filename}")


def main():
    """Main execution."""
    print("="*60)
    print("Alaska DoD Scraper - Playwright Version")
    print("Using real browser automation for better success rate")
    print("="*60)
    print()

    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright not installed!")
        print("\nInstall with:")
        print("  pip install playwright")
        print("  playwright install chromium")
        print("\nThen run this script again.")
        return

    # Create scraper (set headless=False to watch browser in action)
    scraper = PlaywrightScraper(headless=True, slow_mo=100)

    # Execute scraping
    scraper.scrape_all_branches()

    # Save outputs
    print("\nGenerating outputs...")
    scraper.save_json_output('alaska_competitor_data.json')

    print("\n✓ Scraping complete!")
    print(f"✓ Success rate: {scraper.results['scrape_metadata']['successful_scrapes']}/{scraper.results['scrape_metadata']['total_pages']}")
    print("\nOutput files:")
    print("  - alaska_competitor_data.json")
    print("\nRun demo_scraper.py to generate markdown summary from this data.")


if __name__ == '__main__':
    main()
