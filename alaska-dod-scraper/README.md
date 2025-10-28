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

- **Anti-detection measures**: User agent rotation, random delays, robots.txt respect
- **Comprehensive data extraction**: Bonuses, keywords, testimonials, CTAs, recruiter contacts
- **Dual output formats**: Machine-readable JSON and human-readable markdown report
- **Error handling**: Continues scraping even if individual pages fail, logs all errors
- **Data validation**: Validates bonus amounts, Alaska mentions, and keyword frequencies
- **Reusable**: Run monthly to track messaging changes over time

## Installation

```bash
cd alaska-dod-scraper
pip install requests-html beautifulsoup4 pandas lxml
```

## Usage

```bash
python scraper_script.py
```

The script will:
1. Scrape target URLs from Coast Guard, Air Force, Navy, and Marines
2. Extract Alaska-specific content, bonuses, and messaging
3. Generate three output files

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
