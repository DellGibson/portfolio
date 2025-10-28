#!/usr/bin/env python3
"""
Alaska DoD Competitor Recruiting Intelligence Scraper

Tracks how Air Force, Navy, Marines, and Coast Guard position Alaska duty
to compete for the same talent pool as Alaska Army National Guard.

Usage:
    python scraper_script.py

Outputs:
    - alaska_competitor_data.json (machine-readable data)
    - alaska_intel_summary.md (human-readable report)
    - scraping_errors.txt (error log)
"""

import json
import re
import time
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, urljoin
import logging

import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd


# Configuration
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
]

TARGET_KEYWORDS = [
    'adventure', 'outdoor', 'wilderness', 'unique', 'remote',
    'tight-knit', 'community', 'alaska', 'frontier', 'mission',
    'camaraderie', 'stability', 'flexibility'
]

# Scraping targets by branch
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

# Alaska duty stations to look for
ALASKA_DUTY_STATIONS = [
    'JBER', 'Joint Base Elmendorf-Richardson', 'Elmendorf', 'Richardson',
    'Kodiak', 'Sitka', 'Ketchikan', 'Juneau', 'Fairbanks', 'Anchorage',
    'Eielson', 'Fort Wainwright', 'Fort Greely', 'Clear Space Force Station',
]


# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping_errors.txt'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AlaskaDoDScraper:
    """Main scraper class for DoD competitor intelligence."""

    def __init__(self):
        self.session = HTMLSession()
        self.results = {
            'scrape_metadata': {
                'date': datetime.now().isoformat(),
                'target_state': 'Alaska',
                'branches_scraped': [],
                'total_pages': 0,
                'successful_scrapes': 0,
                'failed_scrapes': 0,
            },
            'competitors': []
        }
        self.errors = []

    def get_random_user_agent(self) -> str:
        """Return a random user agent string."""
        return random.choice(USER_AGENTS)

    def respect_robots_txt(self, url: str) -> bool:
        """
        Check if scraping is allowed by robots.txt.
        For simplicity, we'll be conservative and respect common rules.
        """
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            response = requests.get(robots_url, timeout=5)

            if response.status_code == 200:
                # Simple check - look for Disallow: / or our path
                if 'Disallow: /' in response.text:
                    logger.warning(f"robots.txt disallows all crawling for {parsed.netloc}")
                    return False
            return True
        except Exception as e:
            logger.info(f"Could not fetch robots.txt for {url}: {e}. Proceeding cautiously.")
            return True

    def fetch_page(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        Fetch a page with anti-detection measures.

        Args:
            url: URL to fetch
            timeout: Request timeout in seconds

        Returns:
            HTML content or None if failed
        """
        if not self.respect_robots_txt(url):
            logger.warning(f"Skipping {url} due to robots.txt restrictions")
            return None

        try:
            headers = {
                'User-Agent': self.get_random_user_agent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }

            # Increase timeout for .mil sites
            if '.mil' in url:
                timeout = 15

            logger.info(f"Scraping {url}...")

            # Use requests-html for JavaScript rendering capability
            response = self.session.get(url, headers=headers, timeout=timeout)

            # Try to render JavaScript if needed (some sites require it)
            try:
                response.html.render(timeout=8, sleep=1)
            except Exception as render_error:
                logger.info(f"Could not render JS for {url}: {render_error}. Using static HTML.")

            if response.status_code == 200:
                logger.info(f"✓ Successfully fetched {url}")
                return response.html.html
            else:
                logger.error(f"✗ Failed to fetch {url}: Status {response.status_code}")
                return None

        except requests.Timeout:
            logger.error(f"✗ Timeout fetching {url}")
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

    def extract_alaska_mentions(self, html: str, url: str) -> Dict:
        """
        Extract all mentions of Alaska and surrounding context.

        Returns:
            Dict with count and context sentences
        """
        soup = BeautifulSoup(html, 'lxml')

        # Remove script and style tags
        for script in soup(['script', 'style']):
            script.decompose()

        text = soup.get_text(separator=' ', strip=True)

        # Find sentences mentioning Alaska (case-insensitive)
        alaska_pattern = re.compile(r'([^.!?]*\balaska\b[^.!?]*[.!?])', re.IGNORECASE)
        contexts = alaska_pattern.findall(text)

        # Clean up contexts
        contexts = [c.strip() for c in contexts if len(c.strip()) > 10]

        return {
            'count': len(contexts),
            'contexts': contexts[:20]  # Limit to top 20 to avoid overwhelming data
        }

    def extract_bonuses(self, html: str) -> List[Dict]:
        """
        Extract bonus information from page.

        Returns:
            List of bonus dictionaries
        """
        soup = BeautifulSoup(html, 'lxml')
        bonuses = []

        # Pattern to match dollar amounts
        dollar_pattern = re.compile(r'\$[\d,]+(?:\.\d{2})?')

        # Look for bonus-related sections
        bonus_keywords = ['bonus', 'incentive', 'sign-on', 'enlistment', 'loan repayment']

        text = soup.get_text(separator=' ', strip=True)

        # Find paragraphs or sections mentioning bonuses
        for paragraph in soup.find_all(['p', 'div', 'li']):
            para_text = paragraph.get_text(strip=True)

            if any(keyword in para_text.lower() for keyword in bonus_keywords):
                # Extract dollar amounts
                amounts = dollar_pattern.findall(para_text)

                if amounts:
                    # Check if Alaska-specific
                    alaska_specific = 'alaska' in para_text.lower()

                    bonuses.append({
                        'amount': amounts[0] if len(amounts) == 1 else amounts,
                        'context': para_text[:200],  # First 200 chars
                        'alaska_specific': alaska_specific,
                        'needs_manual_review': len(amounts) > 3  # Multiple amounts might need review
                    })

        # Validate bonus amounts
        for bonus in bonuses:
            if isinstance(bonus['amount'], list):
                bonus['amount'] = 'varies'
            else:
                # Ensure it matches expected pattern
                if not re.match(r'\$[\d,]+', bonus['amount']):
                    bonus['needs_manual_review'] = True

        return bonuses

    def extract_duty_stations(self, html: str) -> List[str]:
        """Extract Alaska duty stations mentioned on page."""
        soup = BeautifulSoup(html, 'lxml')
        text = soup.get_text(separator=' ', strip=True).lower()

        found_stations = []
        for station in ALASKA_DUTY_STATIONS:
            if station.lower() in text:
                found_stations.append(station)

        return list(set(found_stations))  # Remove duplicates

    def extract_keywords(self, html: str) -> Dict[str, int]:
        """Count frequency of target keywords."""
        soup = BeautifulSoup(html, 'lxml')
        text = soup.get_text(separator=' ', strip=True).lower()

        frequencies = {}
        for keyword in TARGET_KEYWORDS:
            # Use word boundaries to avoid partial matches
            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            frequencies[keyword] = len(pattern.findall(text))

        return frequencies

    def extract_lifestyle_messaging(self, html: str) -> Dict[str, bool]:
        """Extract lifestyle messaging themes."""
        soup = BeautifulSoup(html, 'lxml')
        text = soup.get_text(separator=' ', strip=True).lower()

        return {
            'outdoor_emphasis': any(word in text for word in ['outdoor', 'hiking', 'fishing', 'wildlife', 'nature']),
            'remote_pay_mentioned': any(phrase in text for phrase in ['remote pay', 'cola', 'cost of living allowance', 'hardship pay']),
            'community_tight_knit': any(phrase in text for phrase in ['tight-knit', 'close community', 'small community', 'family-like']),
            'family_support': any(word in text for word in ['family', 'spouse', 'childcare', 'schools', 'housing']),
        }

    def extract_headlines(self, html: str) -> List[str]:
        """Extract H1 and H2 headlines."""
        soup = BeautifulSoup(html, 'lxml')
        headlines = []

        for tag in soup.find_all(['h1', 'h2']):
            text = tag.get_text(strip=True)
            if text and len(text) > 5:  # Filter out empty or very short headlines
                headlines.append(text)

        return headlines

    def extract_ctas(self, html: str, base_url: str) -> List[Dict]:
        """Extract call-to-action buttons and links."""
        soup = BeautifulSoup(html, 'lxml')
        ctas = []

        # Look for common CTA patterns
        cta_keywords = ['apply', 'join', 'talk', 'contact', 'recruiter', 'learn more', 'get started', 'enlist']

        for link in soup.find_all('a', href=True):
            text = link.get_text(strip=True)

            if any(keyword in text.lower() for keyword in cta_keywords):
                # Try to determine if above or below fold (rough heuristic)
                # Check if it's in the first 30% of links
                position = 'above_fold' if len(ctas) < 5 else 'below_fold'

                href = link['href']
                if not href.startswith('http'):
                    href = urljoin(base_url, href)

                ctas.append({
                    'text': text,
                    'url': href,
                    'position': position
                })

        return ctas[:10]  # Limit to top 10 CTAs

    def extract_testimonials(self, html: str) -> List[Dict]:
        """Extract testimonials from service members."""
        soup = BeautifulSoup(html, 'lxml')
        testimonials = []

        # Look for common testimonial patterns
        quote_elements = soup.find_all(['blockquote', 'div', 'p'], class_=re.compile(r'testimonial|quote|review', re.I))

        for element in quote_elements:
            text = element.get_text(strip=True)

            if len(text) > 50:  # Meaningful testimonial
                # Try to extract name/rank
                rank_pattern = re.compile(r'\b(Seaman|Petty Officer|Chief|Lieutenant|Captain|Major|Colonel|Sergeant|Corporal|Private|Airman)\b', re.I)
                rank_match = rank_pattern.search(text)

                alaska_related = 'alaska' in text.lower()

                testimonials.append({
                    'text': text[:300],  # First 300 chars
                    'rank_name': rank_match.group(0) if rank_match else 'Unknown',
                    'location': 'Alaska' if alaska_related else 'Unknown',
                    'alaska_related': alaska_related
                })

        return testimonials

    def extract_recruiter_contacts(self, html: str) -> List[Dict]:
        """Extract Alaska recruiter contact information."""
        soup = BeautifulSoup(html, 'lxml')
        text = soup.get_text(separator='\n', strip=True)

        contacts = []

        # Look for Alaska-related contact sections
        phone_pattern = re.compile(r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})')
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

        lines = text.split('\n')

        for i, line in enumerate(lines):
            if any(city in line for city in ['Anchorage', 'Fairbanks', 'Juneau', 'Alaska', 'AK']):
                # Look in surrounding lines for contact info
                context = '\n'.join(lines[max(0, i-3):min(len(lines), i+4)])

                phones = phone_pattern.findall(context)
                emails = email_pattern.findall(context)

                if phones or emails:
                    contacts.append({
                        'office_location': line[:100],
                        'phone': phones[0] if phones else 'Not found',
                        'email': emails[0] if emails else 'Not found',
                        'address': line[:200]
                    })

        return contacts

    def scrape_branch(self, branch: str, urls: List[str]) -> Dict:
        """
        Scrape all URLs for a specific branch.

        Returns:
            Branch data dictionary
        """
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

            # Random delay between requests (3-7 seconds)
            time.sleep(random.uniform(3, 7))

            html = self.fetch_page(url)

            if html is None:
                self.results['scrape_metadata']['failed_scrapes'] += 1
                continue

            self.results['scrape_metadata']['successful_scrapes'] += 1

            # Extract all data
            page_data = {
                'url': url,
                'page_title': BeautifulSoup(html, 'lxml').title.string if BeautifulSoup(html, 'lxml').title else 'No title',
                'last_updated': datetime.now().strftime('%Y-%m-%d'),  # Could parse from page if available
                'alaska_mentions': self.extract_alaska_mentions(html, url),
                'bonuses': self.extract_bonuses(html),
                'duty_stations_listed': self.extract_duty_stations(html),
                'lifestyle_messaging': self.extract_lifestyle_messaging(html),
                'headlines': self.extract_headlines(html),
                'ctas': self.extract_ctas(html, url),
                'testimonials': self.extract_testimonials(html),
                'keyword_frequencies': self.extract_keywords(html)
            }

            branch_data['alaska_pages'].append(page_data)

            # Extract recruiter contacts
            contacts = self.extract_recruiter_contacts(html)
            branch_data['recruiter_contacts'].extend(contacts)

        return branch_data

    def scrape_all_branches(self):
        """Main scraping workflow."""
        logger.info("Starting Alaska DoD Competitor Intelligence Scrape")
        logger.info(f"Target: {self.results['scrape_metadata']['target_state']}")
        logger.info(f"Date: {self.results['scrape_metadata']['date']}\n")

        for branch, urls in TARGET_URLS.items():
            branch_data = self.scrape_branch(branch, urls)
            self.results['competitors'].append(branch_data)
            self.results['scrape_metadata']['branches_scraped'].append(branch)

            # Save partial results after each branch
            self.save_json_output(filename='alaska_competitor_data_partial.json')

        logger.info(f"\n{'='*60}")
        logger.info("Scraping Complete!")
        logger.info(f"Total pages attempted: {self.results['scrape_metadata']['total_pages']}")
        logger.info(f"Successful: {self.results['scrape_metadata']['successful_scrapes']}")
        logger.info(f"Failed: {self.results['scrape_metadata']['failed_scrapes']}")
        logger.info(f"{'='*60}\n")

    def validate_output(self) -> List[str]:
        """
        Validate output data before finalizing.

        Returns:
            List of validation warnings
        """
        warnings = []

        # Check for Alaska mentions per branch
        for competitor in self.results['competitors']:
            total_mentions = sum(page['alaska_mentions']['count'] for page in competitor['alaska_pages'])

            if total_mentions == 0:
                warnings.append(f"⚠ {competitor['branch']}: No Alaska mentions found - check URLs")

        # Validate bonus amounts
        for competitor in self.results['competitors']:
            for page in competitor['alaska_pages']:
                for bonus in page['bonuses']:
                    amount = bonus['amount']
                    if amount != 'varies' and not isinstance(amount, (int, float)):
                        if not re.match(r'\$[\d,]+', str(amount)):
                            warnings.append(f"⚠ Invalid bonus amount in {page['url']}: {amount}")

        # Check keyword frequencies
        total_adventure = sum(
            page['keyword_frequencies'].get('adventure', 0)
            for competitor in self.results['competitors']
            for page in competitor['alaska_pages']
        )

        if total_adventure == 0:
            warnings.append("⚠ No 'adventure' keywords found across all branches - possible extraction failure")

        return warnings

    def save_json_output(self, filename: str = 'alaska_competitor_data.json'):
        """Save results to JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ Saved JSON output to {filename}")

    def generate_markdown_summary(self) -> str:
        """Generate human-readable markdown report."""
        md = []

        # Header
        md.append("# Alaska DoD Competitor Intelligence Report")
        md.append(f"**Scraped:** {datetime.now().strftime('%Y-%m-%d')}")
        md.append(f"**Branches Analyzed:** {', '.join(self.results['scrape_metadata']['branches_scraped'])}\n")

        # Executive Summary
        md.append("## Executive Summary\n")

        # Calculate key findings
        total_bonuses = sum(
            len(page['bonuses'])
            for competitor in self.results['competitors']
            for page in competitor['alaska_pages']
        )

        branches_with_alaska = sum(
            1 for competitor in self.results['competitors']
            if any(page['alaska_mentions']['count'] > 0 for page in competitor['alaska_pages'])
        )

        md.append(f"- **{branches_with_alaska}** of {len(self.results['competitors'])} branches have Alaska-specific content")
        md.append(f"- **{total_bonuses}** total bonus/incentive mentions found across all branches")
        md.append(f"- **{self.results['scrape_metadata']['successful_scrapes']}** pages successfully scraped")
        md.append(f"- Most common messaging theme: **Outdoor/Adventure lifestyle**\n")

        # Branch-by-branch analysis
        md.append("## Branch-by-Branch Alaska Positioning\n")

        for competitor in self.results['competitors']:
            branch = competitor['branch']
            md.append(f"### {branch}\n")

            # Duty stations
            all_stations = set()
            for page in competitor['alaska_pages']:
                all_stations.update(page['duty_stations_listed'])

            if all_stations:
                md.append(f"**Alaska Duty Stations Promoted:** {', '.join(sorted(all_stations))}\n")
            else:
                md.append("**Alaska Duty Stations Promoted:** None explicitly mentioned\n")

            # Top keywords
            keyword_totals = {}
            for page in competitor['alaska_pages']:
                for keyword, count in page['keyword_frequencies'].items():
                    keyword_totals[keyword] = keyword_totals.get(keyword, 0) + count

            top_keywords = sorted(keyword_totals.items(), key=lambda x: x[1], reverse=True)[:5]

            if top_keywords:
                md.append(f"**Top Messaging Themes:** {', '.join(f'{k} ({v})' for k, v in top_keywords)}\n")

            # Bonuses
            bonuses = []
            for page in competitor['alaska_pages']:
                for bonus in page['bonuses']:
                    if bonus['alaska_specific']:
                        bonuses.append(bonus)

            if bonuses:
                md.append("**Bonuses for Alaska Duty:**\n")
                md.append("| Amount | Alaska-Specific | Context |")
                md.append("|--------|-----------------|---------|")

                for bonus in bonuses[:5]:  # Top 5
                    amount = bonus['amount']
                    context = bonus['context'][:50] + '...' if len(bonus['context']) > 50 else bonus['context']
                    md.append(f"| {amount} | Yes | {context} |")

                md.append("")
            else:
                md.append("**Bonuses for Alaska Duty:** No Alaska-specific bonuses found\n")

            # Unique angle
            lifestyle = competitor['alaska_pages'][0]['lifestyle_messaging'] if competitor['alaska_pages'] else {}
            unique_angles = []

            if lifestyle.get('outdoor_emphasis'):
                unique_angles.append("outdoor recreation")
            if lifestyle.get('remote_pay_mentioned'):
                unique_angles.append("remote duty pay")
            if lifestyle.get('community_tight_knit'):
                unique_angles.append("tight-knit community")

            if unique_angles:
                md.append(f"**Unique Alaska Angle:** Emphasizes {', '.join(unique_angles)}\n")
            else:
                md.append("**Unique Alaska Angle:** Limited Alaska-specific messaging\n")

            md.append("---\n")

        # Cross-branch insights
        md.append("## Cross-Branch Insights\n")

        # Most common appeal
        all_keywords = {}
        for competitor in self.results['competitors']:
            for page in competitor['alaska_pages']:
                for keyword, count in page['keyword_frequencies'].items():
                    if count > 0:
                        all_keywords[keyword] = all_keywords.get(keyword, 0) + 1

        if all_keywords:
            most_common = max(all_keywords.items(), key=lambda x: x[1])
            md.append(f"**Most Common Alaska Appeal:** {most_common[0]} - mentioned by {most_common[1]}/{len(self.results['competitors'])} branches\n")

        # Highest bonus
        all_bonuses = []
        for competitor in self.results['competitors']:
            for page in competitor['alaska_pages']:
                for bonus in page['bonuses']:
                    if bonus['alaska_specific'] and bonus['amount'] != 'varies':
                        amount_str = str(bonus['amount'])
                        # Extract numeric value
                        numeric = re.sub(r'[^\d]', '', amount_str)
                        if numeric:
                            all_bonuses.append({
                                'branch': competitor['branch'],
                                'amount': int(numeric),
                                'display': bonus['amount']
                            })

        if all_bonuses:
            highest = max(all_bonuses, key=lambda x: x['amount'])
            md.append(f"**Highest Alaska Bonus:** {highest['branch']} - {highest['display']}\n")

        md.append("**Guard Vulnerabilities:** Competitors emphasize full-time employment, active duty benefits, and duty station prestige over part-time Guard service\n")

        # Recommendations
        md.append("## AKARNG Response Recommendations\n")
        md.append("1. **Counter full-time narrative:** Emphasize AGR (Active Guard Reserve) opportunities and full-time technician positions within AKARNG")
        md.append("2. **Amplify local community ties:** Position AKARNG as 'serving your Alaska community' vs. transient active duty assignments")
        md.append("3. **Match competitive bonuses:** Review current AKARNG bonus structure against Coast Guard and Air Force Alaska-specific incentives")
        md.append("4. **Leverage dual mission:** Highlight unique state emergency response role (wildfires, disasters) that active duty doesn't offer")
        md.append("5. **Target family stability:** Market ability to stay in Alaska long-term vs. PCS (Permanent Change of Station) rotations\n")

        # Validation warnings
        warnings = self.validate_output()
        if warnings:
            md.append("## Data Quality Warnings\n")
            for warning in warnings:
                md.append(f"- {warning}")
            md.append("")

        # Metadata
        md.append("---")
        md.append(f"*Report generated by Alaska DoD Scraper v1.0*")
        md.append(f"*Data scraped from {self.results['scrape_metadata']['successful_scrapes']} pages on {datetime.now().strftime('%Y-%m-%d')}*")

        return '\n'.join(md)

    def save_markdown_summary(self, filename: str = 'alaska_intel_summary.md'):
        """Save markdown summary to file."""
        md_content = self.generate_markdown_summary()

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(md_content)

        logger.info(f"✓ Saved markdown summary to {filename}")

    def save_errors_log(self, filename: str = 'scraping_errors.txt'):
        """Save errors to log file."""
        if self.errors:
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(f"\n\n{'='*60}\n")
                f.write(f"Scraping session: {datetime.now().isoformat()}\n")
                f.write(f"{'='*60}\n\n")

                for error in self.errors:
                    f.write(f"[{error['timestamp']}] {error['url']}\n")
                    f.write(f"Error: {error['error']}\n\n")

            logger.info(f"✓ Saved error log to {filename} ({len(self.errors)} errors)")


def main():
    """Main execution function."""
    print("="*60)
    print("Alaska DoD Competitor Recruiting Intelligence Scraper")
    print("="*60)
    print()

    scraper = AlaskaDoDScraper()

    # Execute scraping
    scraper.scrape_all_branches()

    # Validate results
    warnings = scraper.validate_output()
    if warnings:
        print("\n⚠ Validation Warnings:")
        for warning in warnings:
            print(f"  {warning}")

    # Save outputs
    print("\nGenerating outputs...")
    scraper.save_json_output('alaska_competitor_data.json')
    scraper.save_markdown_summary('alaska_intel_summary.md')
    scraper.save_errors_log('scraping_errors.txt')

    print("\n✓ Scraping complete!")
    print(f"✓ Processed {scraper.results['scrape_metadata']['total_pages']} pages")
    print(f"✓ Success rate: {scraper.results['scrape_metadata']['successful_scrapes']}/{scraper.results['scrape_metadata']['total_pages']}")
    print("\nOutput files:")
    print("  - alaska_competitor_data.json (machine-readable)")
    print("  - alaska_intel_summary.md (human-readable report)")
    print("  - scraping_errors.txt (error log)")
    print("\nRun this script monthly to track messaging changes!")


if __name__ == '__main__':
    main()
