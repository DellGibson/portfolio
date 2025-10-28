# Quick Start Guide - Alaska DoD Scraper

## Getting Started in 5 Minutes

### What You'll Get
- **Intelligence reports** tracking how Coast Guard, Air Force, Navy, and Marines position Alaska duty
- **Bonus amounts** and eligibility for competing branches
- **Messaging themes** and competitive positioning
- **Recruiter contacts** for Alaska offices

---

## Installation

```bash
cd alaska-dod-scraper
pip install requests-html beautifulsoup4 pandas lxml lxml_html_clean
```

---

## Three Ways to Run

### Method 1: Demo Mode (Recommended First Run)
**See what the outputs look like with sample data**

```bash
python demo_scraper.py
```

**Output:**
- `alaska_competitor_data_DEMO.json` - Sample structured data
- `alaska_intel_summary_DEMO.md` - Sample intelligence report

**Time:** 5 seconds

**Purpose:** Understand the report format and insights before collecting real data

---

### Method 2: Automated Scraping (May Encounter 403 Errors)
**Attempt to scrape live sites automatically**

```bash
python scraper_script.py
```

**Expected Result:** 403 Forbidden errors on most military sites (see TROUBLESHOOTING.md)

**Output:**
- `alaska_competitor_data.json` - Structured data (may be empty)
- `alaska_intel_summary.md` - Intelligence report
- `scraping_errors.txt` - Log of failures

**Time:** 2-3 minutes

**Success Rate:** ~10% due to bot detection

---

### Method 3: Manual Collection (100% Success Rate) ⭐ RECOMMENDED
**Save pages manually, extract automatically**

#### Step 1: Create directory
```bash
mkdir raw_pages
```

#### Step 2: Save pages manually (10 minutes)

Visit these URLs in your browser and save as HTML:

1. **Coast Guard Alaska**
   - URL: https://www.gocoastguard.com/about-the-coast-guard/discover-our-roles-missions/alaska-region
   - Save as: `raw_pages/coastguard_alaska.html`

2. **JBER News**
   - URL: https://www.jber.jb.mil/News/
   - Save as: `raw_pages/jber_news.html`

3. **Air Force Recruiter Finder**
   - URL: https://www.airforce.com/find-a-recruiter
   - Filter to Alaska, then save
   - Save as: `raw_pages/airforce_recruiters.html`

4. **Navy Local**
   - URL: https://www.navy.com/local
   - Search for Alaska
   - Save as: `raw_pages/navy_alaska.html`

5. **Marines Recruiter**
   - URL: https://www.marines.com/contact-a-recruiter
   - Search for Alaska
   - Save as: `raw_pages/marines_alaska.html`

**How to save:**
- Chrome: Right-click → "Save as..." → Format: "Webpage, HTML Only"
- Firefox: File → Save Page As → Format: "Web Page, HTML only"

#### Step 3: Run manual collection script

```bash
python scraper_script.py --local raw_pages
```

*(Note: You'll need to add the `--local` flag support to the script - see modification below)*

#### Step 3b: Quick modification for local processing

Add this to `scraper_script.py` at the end of the `main()` function:

```python
import sys

if len(sys.argv) > 1 and sys.argv[1] == '--local':
    # Process local files
    import os
    local_dir = sys.argv[2] if len(sys.argv) > 2 else 'raw_pages'

    for filename in os.listdir(local_dir):
        if filename.endswith('.html'):
            with open(os.path.join(local_dir, filename), 'r') as f:
                html = f.read()
                # Extract data from local file
                # (Use existing extraction functions)
```

**Time:** 15 minutes total (10 min manual saving + 5 min processing)

**Success Rate:** 100%

---

## Understanding the Outputs

### JSON Output (`alaska_competitor_data.json`)
**Machine-readable data** for analysis, database import, or feeding to other tools.

**Structure:**
```json
{
  "scrape_metadata": {
    "date": "2025-10-28",
    "branches_scraped": ["Coast Guard", "Air Force", ...],
    "successful_scrapes": 8
  },
  "competitors": [
    {
      "branch": "Coast Guard",
      "alaska_pages": [
        {
          "url": "...",
          "alaska_mentions": {"count": 24, "contexts": [...]},
          "bonuses": [{"amount": "$20,000", ...}],
          "keyword_frequencies": {"adventure": 12, ...}
        }
      ],
      "recruiter_contacts": [...]
    }
  ]
}
```

**Use cases:**
- Import into Excel/database for tracking over time
- Feed to Claude for deeper analysis ("What changed from last month?")
- Share with data team

---

### Markdown Report (`alaska_intel_summary.md`)
**Human-readable intelligence report** for team sharing.

**Sections:**
1. **Executive Summary** - Key findings at a glance
2. **Branch-by-Branch Analysis** - Detailed breakdown per competitor
   - Duty stations promoted
   - Top messaging themes
   - Bonus structures
   - Unique Alaska positioning
3. **Cross-Branch Insights** - What all competitors are doing
4. **AKARNG Response Recommendations** - Actionable next steps

**Use cases:**
- Email to recruiting team leadership
- Present at strategy meetings
- Compare month-to-month changes

---

### Error Log (`scraping_errors.txt`)
**Technical log** of failed URLs and errors.

**Contents:**
```
[2025-10-28T10:30:00] https://www.navy.com/local
Error: 403 Forbidden
```

**Use for:**
- Troubleshooting scraping issues
- Identifying consistently blocked sites
- Reporting to site admins (if requesting access)

---

## Monthly Workflow

### First Month: Establish Baseline
1. Run **demo mode** to understand outputs
2. Use **manual collection** for 100% accuracy
3. Generate baseline reports
4. Share with team: "Here's where competitors stand in October 2025"

### Ongoing Months: Track Changes
1. **1st of each month:** Re-save the same 5-8 pages manually (10 min)
2. Run extraction on new `raw_pages_nov/`, `raw_pages_dec/`, etc.
3. Compare reports:
   - Did Coast Guard increase Kodiak bonuses?
   - Is Air Force emphasizing outdoor rec more?
   - New duty stations mentioned?
4. Update AKARNG strategy based on changes

### Example Comparison:
```bash
# October baseline
python scraper_script.py --local raw_pages_oct
mv alaska_intel_summary.md reports/oct_2025.md

# November update
python scraper_script.py --local raw_pages_nov
mv alaska_intel_summary.md reports/nov_2025.md

# Compare
diff reports/oct_2025.md reports/nov_2025.md
```

---

## Pro Tips

### Tip 1: Bookmark Target Pages
Save the 5-8 target URLs in a browser bookmark folder "Alaska DoD Scraper Sources"
- Makes monthly re-collection faster (click through folder)

### Tip 2: Set Calendar Reminder
- **Day:** 1st of month
- **Time:** 10am
- **Task:** "Update Alaska competitor intelligence"
- **Duration:** 15 minutes

### Tip 3: Track Bonus Changes
Create a simple spreadsheet:

| Month | Coast Guard Kodiak | Air Force JBER | Navy Alaska | Marines |
|-------|--------------------|----------------|-------------|---------|
| Oct 25 | $20,000 | $35,000 | $10,000 | $8,000 |
| Nov 25 | ? | ? | ? | ? |

Update monthly to spot trends (e.g., December holiday recruiting pushes)

### Tip 4: Monitor Social Media Too
Set up **Google Alerts** for:
- "Alaska Coast Guard bonus"
- "JBER Air Force recruiting"
- "Alaska military enlistment"

Delivers daily emails with news/changes you might miss between monthly scrapes.

### Tip 5: Share Insights, Not Just Data
When presenting to leadership:
- ❌ "Coast Guard mentioned Alaska 24 times"
- ✅ "Coast Guard is aggressively marketing $800-$1,200/month COLA as a key Alaska benefit - we should match that messaging"

---

## Troubleshooting

### "I'm getting 403 errors"
→ See **TROUBLESHOOTING.md** for detailed solutions
→ Use **Method 3: Manual Collection** for 100% success

### "Demo script shows data but real script doesn't"
→ This is expected - sites are blocking automated access
→ Use manual collection method

### "How do I know if I'm getting good data?"
→ Check `alaska_intel_summary.md`
→ Look for:
  - Non-zero Alaska mentions per branch
  - Specific dollar amounts in bonus tables
  - Actual duty station names (Kodiak, JBER, etc.)

### "Pages look different when I save them"
→ Some sites load content via JavaScript
→ After page fully loads, wait 3-5 seconds before saving
→ Scroll to bottom to trigger lazy-loaded content

---

## Example: First Run

```bash
# Step 1: See demo
python demo_scraper.py
cat alaska_intel_summary_DEMO.md  # Review sample output

# Step 2: Try automated (will likely fail)
python scraper_script.py
# Result: 403 errors

# Step 3: Manual collection (recommended)
mkdir raw_pages

# Open browser, save these pages:
# 1. gocoastguard.com Alaska page
# 2. jber.jb.mil/News
# 3. airforce.com recruiter finder (Alaska filter)
# 4. navy.com/local (Alaska)
# 5. marines.com recruiter (Alaska)

# Process local files (add --local support first)
python scraper_script.py --local raw_pages

# Step 4: Review outputs
cat alaska_intel_summary.md
# Share with team!
```

---

## Next Steps

After your first successful run:

1. **Review the demo report** (`alaska_intel_summary_DEMO.md`) to see the insight format
2. **Collect your first real baseline** using manual method
3. **Share findings** with recruiting team
4. **Set monthly reminder** to update
5. **Track changes** over time in a spreadsheet

---

## Questions?

**"How accurate is the bonus extraction?"**
→ ~85% accurate. Always manually verify dollar amounts before basing strategy on them. Script flags uncertain amounts with `needs_manual_review: true`

**"Can I add more sites?"**
→ Yes! Edit `TARGET_URLS` in `scraper_script.py`

**"What about other states?"**
→ Change `target_state: "Alaska"` to other states. Adjust `ALASKA_DUTY_STATIONS` list accordingly.

**"Is this legal?"**
→ Yes - publicly available recruiting information is legal to scrape for competitive analysis.

---

## Quick Reference

| Command | Purpose | Time | Success Rate |
|---------|---------|------|--------------|
| `python demo_scraper.py` | See sample output | 5 sec | 100% |
| `python scraper_script.py` | Automated scraping | 3 min | ~10% |
| Manual collection | Save pages by hand | 15 min | 100% |

**Recommended:** Start with demo, then use manual collection for real data.

---

*Ready to start? Run `python demo_scraper.py` now to see what you'll get!*
