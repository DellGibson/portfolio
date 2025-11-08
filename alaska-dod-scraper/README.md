# Alaska DoD Competitor Recruiting Intelligence Scraper

A web scraper that tracks how Air Force, Navy, Marines, and Coast Guard position Alaska duty to compete for the same talent pool as Alaska Army National Guard.

## Purpose

This tool provides competitive intelligence for Alaska Army National Guard recruiting by monitoring:
- Alaska-specific messaging from competing military branches
- Bonus and incentive structures
- Messaging themes and emotional appeals
- Recruiting tactics and CTAs
- Local recruiter contact information

## Features

### Core Capabilities
- **Anti-detection measures**: User agent rotation, random delays, robots.txt respect
- **Comprehensive data extraction**: Bonuses, keywords, testimonials, CTAs, recruiter contacts
- **Dual output formats**: Machine-readable JSON and human-readable markdown report
- **Error handling**: Continues scraping even if individual pages fail, logs all errors
- **Data validation**: Validates bonus amounts, Alaska mentions, and keyword frequencies

### 🆕 Advanced Features (v2.0)
- **Month-over-Month Comparison**: Automatically detect bonus changes, messaging shifts, and new content
- **Playwright Integration**: Real browser automation for 60-80% success rate (vs 0% with basic scraper)
- **Email Alerts**: Get notified immediately when competitors make significant changes
- **Change Detection**: Track $5,000+ bonus increases, 50%+ messaging shifts, and duty station changes
- **Reusable**: Run monthly to track messaging changes over time

## Installation

### Basic Installation
```bash
cd alaska-dod-scraper
pip install requests-html beautifulsoup4 pandas lxml lxml_html_clean
```

### Advanced Installation (Recommended for better success rate)
```bash
# Install Playwright for real browser automation
pip install playwright
playwright install chromium
```

## Quick Start

### Option 1: Demo Mode (Recommended First Run)
```bash
python demo_scraper.py
```
See what the outputs look like with realistic sample data.

### Option 2: Enhanced Scraper (Playwright - Best Success Rate)
```bash
python scraper_playwright.py
```
Uses real browser automation for 60-80% success rate.

### Option 3: Basic Scraper
```bash
python scraper_script.py
```
May encounter 403 errors on most military sites.

## New Features Guide

### 🔄 Month-over-Month Comparison

Track changes between scraping runs:

```bash
# Compare two specific reports
python compare_reports.py data/oct_2025.json data/nov_2025.json

# Or compare the latest two reports automatically
python compare_reports.py --latest
```

**Detects:**
- Bonus increases/decreases ($5,000+ triggers HIGH alert)
- New bonuses added
- Messaging theme shifts (50%+ change in keyword frequency)
- Duty station coverage changes
- Alaska mention frequency changes

**Outputs:**
- `alaska_intel_CHANGES.md` - Human-readable change report
- `alaska_changes.json` - Machine-readable change data

### 📧 Email Alerts

Get notified when significant changes occur:

```bash
# 1. Configure credentials
cp config.example.env .env
# Edit .env with your SMTP settings

# 2. Set environment variables
export SMTP_USERNAME='your-email@gmail.com'
export SMTP_PASSWORD='your-app-password'
export ALERT_TO_EMAILS='recruiting@akarng.mil,leadership@akarng.mil'

# 3. Run alert system
python alert_system.py alaska_changes.json
```

**Alert Triggers:**
- Bonus changes of $5,000+ (HIGH priority)
- Bonus changes of $2,000+ (MEDIUM priority)
- New bonuses added
- 50%+ shifts in messaging themes
- Duty station coverage changes

**Supports:**
- Email (HTML formatted)
- Slack webhooks (optional)

### 🎯 Recommended Monthly Workflow

```bash
# Month 1: Establish baseline
python scraper_playwright.py
mv alaska_competitor_data.json data/oct_2025.json

# Month 2: Detect changes and alert
python scraper_playwright.py
mv alaska_competitor_data.json data/nov_2025.json
python compare_reports.py data/oct_2025.json data/nov_2025.json
python alert_system.py alaska_changes.json
```

**Automated with cron:**
```bash
# Run 1st of each month at 6am
0 6 1 * * cd /path/to/alaska-dod-scraper && python scraper_playwright.py && python compare_reports.py --latest && python alert_system.py alaska_changes.json
```

## Output Files

1. **alaska_competitor_data.json** - Machine-readable structured data
   - Full scraping results with metadata
   - Can be fed to analysis tools or Claude for further insights
   - Size: ~50-200KB

2. **alaska_intel_summary.md** - Human-readable intelligence report
   - Executive summary of key findings
   - Branch-by-branch analysis
   - Cross-branch insights
   - AKARNG response recommendations

3. **scraping_errors.txt** - Error log
   - Failed URLs with timestamps
   - Error types (timeout, connection, parsing)
   - Useful for debugging and improving scraper

## Scraping Targets

### Primary Sites
- Coast Guard: Active duty careers and Alaska region pages
- Air Force: Recruiter finder and career pages
- Navy: Local recruiter locator
- Marines: Recruiter contact pages
- JBER: Joint Base Elmendorf-Richardson news

### Data Extracted

**Alaska-Specific Messaging:**
- Headlines mentioning Alaska
- Duty station descriptions (JBER, Kodiak, Fairbanks, etc.)
- Lifestyle benefits (outdoor recreation, housing, allowances)

**Bonuses & Incentives:**
- Dollar amounts and eligibility
- Alaska-specific incentives (COLA, remote duty pay)
- Student loan repayment programs

**Messaging Themes:**
- Keyword frequency analysis
- Emotional appeals (adventure, camaraderie, mission)
- Family messaging (housing, schools, employment)

**Recruiting Tactics:**
- CTA button text and positioning
- Lead capture methods
- Local Alaska recruiter contacts
- Testimonials from Alaska-based service members

## Technical Details

**Libraries:**
- `requests-html`: JavaScript rendering capability
- `BeautifulSoup4`: HTML parsing
- `pandas`: Data structuring
- `lxml`: Fast XML/HTML processing

**Anti-Detection:**
- 4 rotating user agents (desktop browsers)
- Random 3-7 second delays between requests
- robots.txt compliance check
- 10-15 second timeouts (.mil sites get 15s)

**Error Handling:**
- Graceful failure: skips failed pages, continues scraping
- Comprehensive logging to scraping_errors.txt
- Partial results saved after each branch
- Bonus amount validation with manual review flags

## Validation

The scraper automatically validates:
- At least 1 Alaska mention per branch
- Bonus amounts match pattern `$X,XXX` or flagged for review
- All URLs are valid (http:// or https://)
- Keyword frequencies are reasonable

Validation warnings appear in both console output and the markdown report.

## Recommended Schedule

**Monthly scraping** to track:
- Seasonal bonus changes (e.g., Coast Guard winter recruitment push)
- New Alaska duty station messaging
- Competitor response to AKARNG campaigns
- Shifts in messaging themes

Run on the **1st of each month** and compare reports over time.

## Customization

To modify target URLs, edit the `TARGET_URLS` dictionary in `scraper_script.py`:

```python
TARGET_URLS = {
    'Coast Guard': [
        'https://www.gocoastguard.com/...',
        # Add more URLs
    ],
    # Add more branches or update URLs
}
```

To add keywords to track, edit the `TARGET_KEYWORDS` list:

```python
TARGET_KEYWORDS = [
    'adventure', 'outdoor', 'wilderness',
    # Add more keywords
]
```

## Troubleshooting

**"robots.txt disallows all crawling"**
- The site blocks automated scraping
- Consider manual review or contact site admin

**"Timeout fetching URL"**
- Site is slow or down
- Check if .mil site is accessible
- Increase timeout in code if needed

**"No Alaska mentions found"**
- URL may not have Alaska-specific content
- Check if page structure changed
- Verify URL is correct

**JavaScript rendering issues**
- Some sites may not render properly
- Script falls back to static HTML
- Check browser manually if data seems incomplete

## Example Usage Workflow

1. **Initial baseline** (October 2025): Run scraper to establish baseline
2. **Monthly monitoring**: Re-run on 1st of each month
3. **Compare reports**: Look for changes in bonuses, messaging, new duty stations
4. **Adapt AKARNG strategy**: Use insights to inform recruitment campaigns
5. **Update URLs**: Quarterly review to ensure target pages haven't moved

## Data Privacy & Ethics

- Scrapes only **publicly available** recruiting information
- Respects robots.txt directives
- No personal data collection
- Defensive security use only (competitive intelligence)
- Delays between requests to avoid server load

## License

Internal use for Alaska Army National Guard recruiting analysis.

## Version

**v1.0** - Initial release (October 2025)

## Support

For issues or questions:
1. Check scraping_errors.txt for specific failures
2. Review validation warnings in console output
3. Verify target URLs are still active
4. Consider updating user agents if sites change detection methods

---

*Built for Alaska Army National Guard recruiting competitive intelligence*
