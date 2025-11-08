#!/usr/bin/env python3
"""
Month-over-Month Comparison Tool for Alaska DoD Intelligence

Compares two scraping results to identify:
- Bonus amount changes
- Messaging theme shifts
- New content additions
- Duty station changes
- Keyword frequency trends

Usage:
    python compare_reports.py data/oct_2025.json data/nov_2025.json
    python compare_reports.py --latest  # Compare last two runs
"""

import json
import sys
from datetime import datetime
from typing import Dict, List, Tuple
from pathlib import Path


class ChangeDetector:
    """Detects and analyzes changes between two scraping runs."""

    def __init__(self, old_data: Dict, new_data: Dict):
        self.old_data = old_data
        self.new_data = new_data
        self.changes = {
            'metadata': {
                'old_date': old_data['scrape_metadata']['date'],
                'new_date': new_data['scrape_metadata']['date'],
                'comparison_date': datetime.now().isoformat()
            },
            'bonus_changes': [],
            'messaging_shifts': [],
            'new_content': [],
            'duty_station_changes': [],
            'alert_level': 'NONE',
            'summary': ''
        }

    def find_branch(self, data: Dict, branch_name: str) -> Dict:
        """Find branch data by name."""
        for competitor in data['competitors']:
            if competitor['branch'] == branch_name:
                return competitor
        return None

    def compare_bonuses(self):
        """Compare bonus structures between old and new data."""
        for new_competitor in self.new_data['competitors']:
            branch = new_competitor['branch']
            old_competitor = self.find_branch(self.old_data, branch)

            if not old_competitor:
                self.changes['new_content'].append({
                    'type': 'NEW_BRANCH',
                    'branch': branch,
                    'description': f'Started tracking {branch} data'
                })
                continue

            # Compare bonuses
            new_bonuses = []
            for page in new_competitor['alaska_pages']:
                new_bonuses.extend(page.get('bonuses', []))

            old_bonuses = []
            for page in old_competitor['alaska_pages']:
                old_bonuses.extend(page.get('bonuses', []))

            # Detect bonus changes
            for new_bonus in new_bonuses:
                if not new_bonus.get('alaska_specific'):
                    continue

                new_amount = self._parse_bonus_amount(new_bonus['amount'])

                # Try to find matching bonus in old data
                matched = False
                for old_bonus in old_bonuses:
                    old_amount = self._parse_bonus_amount(old_bonus['amount'])

                    # Check if same bonus type (by context similarity)
                    if self._similar_context(old_bonus.get('context', ''), new_bonus.get('context', '')):
                        matched = True

                        if new_amount != old_amount and new_amount > 0 and old_amount > 0:
                            delta = new_amount - old_amount
                            alert_level = 'HIGH' if abs(delta) >= 5000 else 'MEDIUM' if abs(delta) >= 2000 else 'LOW'

                            self.changes['bonus_changes'].append({
                                'branch': branch,
                                'old_amount': old_amount,
                                'new_amount': new_amount,
                                'delta': delta,
                                'delta_percent': round((delta / old_amount) * 100, 1) if old_amount > 0 else 0,
                                'context': new_bonus.get('context', '')[:100],
                                'alert_level': alert_level,
                                'direction': 'INCREASE' if delta > 0 else 'DECREASE'
                            })

                            # Update overall alert level
                            if alert_level == 'HIGH' and self.changes['alert_level'] != 'CRITICAL':
                                self.changes['alert_level'] = 'HIGH'
                        break

                # New bonus detected
                if not matched and new_amount > 0:
                    self.changes['bonus_changes'].append({
                        'branch': branch,
                        'old_amount': 0,
                        'new_amount': new_amount,
                        'delta': new_amount,
                        'delta_percent': 100,
                        'context': new_bonus.get('context', '')[:100],
                        'alert_level': 'HIGH' if new_amount >= 10000 else 'MEDIUM',
                        'direction': 'NEW'
                    })

                    if new_amount >= 15000:
                        self.changes['alert_level'] = 'HIGH'

    def _parse_bonus_amount(self, amount) -> int:
        """Extract numeric value from bonus amount."""
        if isinstance(amount, int):
            return amount
        if isinstance(amount, str):
            if amount.lower() == 'varies':
                return 0
            # Extract numbers from string like "$20,000"
            import re
            numbers = re.sub(r'[^\d]', '', amount)
            return int(numbers) if numbers else 0
        return 0

    def _similar_context(self, context1: str, context2: str) -> bool:
        """Check if two contexts are similar (same bonus type)."""
        if not context1 or not context2:
            return False

        # Simple similarity: check for common important words
        words1 = set(context1.lower().split())
        words2 = set(context2.lower().split())

        important_words = words1.intersection(words2)

        # If they share key terms, likely same bonus
        key_terms = ['cyber', 'aviation', 'maintenance', 'infantry', 'maritime', 'enforcement', 'nuclear']
        for term in key_terms:
            if term in important_words:
                return True

        return len(important_words) > 5

    def compare_messaging(self):
        """Compare messaging themes and keyword frequencies."""
        for new_competitor in self.new_data['competitors']:
            branch = new_competitor['branch']
            old_competitor = self.find_branch(self.old_data, branch)

            if not old_competitor or not new_competitor['alaska_pages']:
                continue

            # Aggregate keyword frequencies
            new_keywords = {}
            for page in new_competitor['alaska_pages']:
                for keyword, count in page.get('keyword_frequencies', {}).items():
                    new_keywords[keyword] = new_keywords.get(keyword, 0) + count

            old_keywords = {}
            for page in old_competitor['alaska_pages']:
                for keyword, count in page.get('keyword_frequencies', {}).items():
                    old_keywords[keyword] = old_keywords.get(keyword, 0) + count

            # Detect significant shifts
            for keyword, new_count in new_keywords.items():
                old_count = old_keywords.get(keyword, 0)

                if old_count == 0 and new_count > 5:
                    # New messaging theme
                    self.changes['messaging_shifts'].append({
                        'branch': branch,
                        'keyword': keyword,
                        'old_count': 0,
                        'new_count': new_count,
                        'change_type': 'NEW_THEME',
                        'significance': 'MEDIUM'
                    })
                elif old_count > 0:
                    percent_change = ((new_count - old_count) / old_count) * 100

                    if abs(percent_change) >= 50:  # 50%+ change is significant
                        self.changes['messaging_shifts'].append({
                            'branch': branch,
                            'keyword': keyword,
                            'old_count': old_count,
                            'new_count': new_count,
                            'percent_change': round(percent_change, 1),
                            'change_type': 'SHIFT',
                            'significance': 'HIGH' if abs(percent_change) >= 100 else 'MEDIUM'
                        })

    def compare_duty_stations(self):
        """Compare duty station coverage."""
        for new_competitor in self.new_data['competitors']:
            branch = new_competitor['branch']
            old_competitor = self.find_branch(self.old_data, branch)

            if not old_competitor:
                continue

            # Aggregate duty stations
            new_stations = set()
            for page in new_competitor['alaska_pages']:
                new_stations.update(page.get('duty_stations_listed', []))

            old_stations = set()
            for page in old_competitor['alaska_pages']:
                old_stations.update(page.get('duty_stations_listed', []))

            # Find new stations
            added_stations = new_stations - old_stations
            removed_stations = old_stations - new_stations

            if added_stations:
                self.changes['duty_station_changes'].append({
                    'branch': branch,
                    'change_type': 'ADDED',
                    'stations': list(added_stations),
                    'alert_level': 'MEDIUM'
                })

            if removed_stations:
                self.changes['duty_station_changes'].append({
                    'branch': branch,
                    'change_type': 'REMOVED',
                    'stations': list(removed_stations),
                    'alert_level': 'LOW'
                })

    def compare_alaska_mentions(self):
        """Compare Alaska mention frequency."""
        for new_competitor in self.new_data['competitors']:
            branch = new_competitor['branch']
            old_competitor = self.find_branch(self.old_data, branch)

            if not old_competitor:
                continue

            new_mentions = sum(page['alaska_mentions']['count'] for page in new_competitor['alaska_pages'])
            old_mentions = sum(page['alaska_mentions']['count'] for page in old_competitor['alaska_pages'])

            if old_mentions > 0:
                percent_change = ((new_mentions - old_mentions) / old_mentions) * 100

                if abs(percent_change) >= 30:  # 30%+ change
                    self.changes['messaging_shifts'].append({
                        'branch': branch,
                        'keyword': 'alaska',
                        'old_count': old_mentions,
                        'new_count': new_mentions,
                        'percent_change': round(percent_change, 1),
                        'change_type': 'ALASKA_FOCUS_SHIFT',
                        'significance': 'HIGH' if abs(percent_change) >= 50 else 'MEDIUM'
                    })

    def generate_summary(self):
        """Generate executive summary of changes."""
        summary_parts = []

        # Critical changes
        critical_bonuses = [b for b in self.changes['bonus_changes'] if b['alert_level'] == 'HIGH']
        if critical_bonuses:
            summary_parts.append(f"🚨 {len(critical_bonuses)} HIGH PRIORITY bonus change(s) detected")

        # All bonus changes
        if self.changes['bonus_changes']:
            total_bonus_changes = len(self.changes['bonus_changes'])
            increases = len([b for b in self.changes['bonus_changes'] if b['direction'] in ['INCREASE', 'NEW']])
            summary_parts.append(f"{total_bonus_changes} bonus change(s) ({increases} increases)")

        # Messaging shifts
        if self.changes['messaging_shifts']:
            significant = len([m for m in self.changes['messaging_shifts'] if m.get('significance') == 'HIGH'])
            summary_parts.append(f"{len(self.changes['messaging_shifts'])} messaging shift(s) ({significant} significant)")

        # Duty stations
        if self.changes['duty_station_changes']:
            summary_parts.append(f"{len(self.changes['duty_station_changes'])} duty station change(s)")

        if not summary_parts:
            self.changes['summary'] = "No significant changes detected between reports"
        else:
            self.changes['summary'] = " | ".join(summary_parts)

    def analyze(self) -> Dict:
        """Run all comparisons and return results."""
        self.compare_bonuses()
        self.compare_messaging()
        self.compare_duty_stations()
        self.compare_alaska_mentions()
        self.generate_summary()

        return self.changes


def generate_comparison_report(changes: Dict) -> str:
    """Generate markdown report from changes."""
    md = []

    md.append("# Alaska DoD Competitor Intelligence - Change Report\n")
    md.append(f"**Previous Report:** {changes['metadata']['old_date'][:10]}")
    md.append(f"**Current Report:** {changes['metadata']['new_date'][:10]}")
    md.append(f"**Analysis Date:** {changes['metadata']['comparison_date'][:10]}\n")

    # Alert banner
    if changes['alert_level'] in ['HIGH', 'CRITICAL']:
        md.append(f"## 🚨 {changes['alert_level']} PRIORITY ALERT\n")
        md.append(f"**Summary:** {changes['summary']}\n")
        md.append("**Immediate action recommended**\n")
    else:
        md.append(f"## Summary\n")
        md.append(f"{changes['summary']}\n")

    # Bonus changes
    if changes['bonus_changes']:
        md.append("## 💰 Bonus Changes\n")

        # High priority first
        high_priority = [b for b in changes['bonus_changes'] if b['alert_level'] == 'HIGH']
        if high_priority:
            md.append("### 🚨 High Priority\n")
            md.append("| Branch | Old | New | Change | % | Type |")
            md.append("|--------|-----|-----|--------|---|------|")

            for change in high_priority:
                old_fmt = f"${change['old_amount']:,}" if change['old_amount'] > 0 else "N/A"
                new_fmt = f"${change['new_amount']:,}"
                delta_fmt = f"+${change['delta']:,}" if change['delta'] > 0 else f"-${abs(change['delta']):,}"

                md.append(f"| {change['branch']} | {old_fmt} | {new_fmt} | {delta_fmt} | {change['delta_percent']:+.1f}% | {change['direction']} |")

            md.append("")

        # Medium/Low priority
        other_changes = [b for b in changes['bonus_changes'] if b['alert_level'] != 'HIGH']
        if other_changes:
            md.append("### Other Changes\n")
            md.append("| Branch | Old | New | Change | % | Type |")
            md.append("|--------|-----|-----|--------|---|------|")

            for change in other_changes:
                old_fmt = f"${change['old_amount']:,}" if change['old_amount'] > 0 else "N/A"
                new_fmt = f"${change['new_amount']:,}"
                delta_fmt = f"+${change['delta']:,}" if change['delta'] > 0 else f"-${abs(change['delta']):,}"

                md.append(f"| {change['branch']} | {old_fmt} | {new_fmt} | {delta_fmt} | {change['delta_percent']:+.1f}% | {change['direction']} |")

            md.append("")

    # Messaging shifts
    if changes['messaging_shifts']:
        md.append("## 📊 Messaging Shifts\n")

        significant = [m for m in changes['messaging_shifts'] if m.get('significance') == 'HIGH']
        if significant:
            md.append("### Significant Changes (50%+ shift)\n")
            md.append("| Branch | Theme | Old Count | New Count | Change |")
            md.append("|--------|-------|-----------|-----------|--------|")

            for shift in significant:
                if shift.get('change_type') == 'ALASKA_FOCUS_SHIFT':
                    md.append(f"| {shift['branch']} | Alaska mentions | {shift['old_count']} | {shift['new_count']} | {shift['percent_change']:+.1f}% |")
                else:
                    md.append(f"| {shift['branch']} | {shift['keyword']} | {shift['old_count']} | {shift['new_count']} | {shift.get('percent_change', 'NEW'):+.1f}% |")

            md.append("")

        # New themes
        new_themes = [m for m in changes['messaging_shifts'] if m.get('change_type') == 'NEW_THEME']
        if new_themes:
            md.append("### New Messaging Themes\n")
            for theme in new_themes:
                md.append(f"- **{theme['branch']}**: Started emphasizing '{theme['keyword']}' ({theme['new_count']} mentions)")
            md.append("")

    # Duty station changes
    if changes['duty_station_changes']:
        md.append("## 🗺️ Duty Station Changes\n")

        for change in changes['duty_station_changes']:
            if change['change_type'] == 'ADDED':
                md.append(f"- **{change['branch']}** added: {', '.join(change['stations'])}")
            else:
                md.append(f"- **{change['branch']}** removed: {', '.join(change['stations'])}")

        md.append("")

    # Recommendations
    md.append("## 🎯 AKARNG Response Recommendations\n")

    if changes['bonus_changes']:
        max_increase = max([b['delta'] for b in changes['bonus_changes'] if b['direction'] in ['INCREASE', 'NEW']], default=0)
        if max_increase >= 5000:
            md.append(f"1. **URGENT - Bonus Review**: Competitor increased bonuses by up to ${max_increase:,}. Review AKARNG bonus structure within 72 hours.")

    significant_messaging = [m for m in changes['messaging_shifts'] if m.get('significance') == 'HIGH']
    if significant_messaging:
        top_shift = significant_messaging[0]
        md.append(f"2. **Messaging Adaptation**: {top_shift['branch']} significantly increased '{top_shift['keyword']}' messaging. Consider incorporating similar themes.")

    if changes['duty_station_changes']:
        md.append(f"3. **Market Positioning**: Competitors adjusted duty station marketing. Review AKARNG armory/location messaging.")

    if not changes['bonus_changes'] and not significant_messaging:
        md.append("1. **Maintain Course**: No significant competitor changes detected. Continue current strategy.")

    md.append("")

    # Footer
    md.append("---")
    md.append(f"*Report generated by Alaska DoD Scraper - Change Detection v1.0*")
    md.append(f"*Comparison run on {changes['metadata']['comparison_date'][:10]}*")

    return '\n'.join(md)


def find_latest_reports(directory: str = '.') -> Tuple[str, str]:
    """Find the two most recent JSON reports."""
    json_files = sorted(
        [f for f in Path(directory).glob('alaska_competitor_data*.json')
         if 'DEMO' not in f.name and 'partial' not in f.name],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )

    if len(json_files) < 2:
        raise ValueError("Need at least 2 report files to compare. Found: " + str(len(json_files)))

    return str(json_files[1]), str(json_files[0])  # older, newer


def main():
    """Main execution."""
    if len(sys.argv) > 1 and sys.argv[1] == '--latest':
        try:
            old_file, new_file = find_latest_reports()
            print(f"Comparing latest reports:")
            print(f"  Old: {old_file}")
            print(f"  New: {new_file}")
        except ValueError as e:
            print(f"Error: {e}")
            print("\nManual usage: python compare_reports.py <old_report.json> <new_report.json>")
            sys.exit(1)
    elif len(sys.argv) >= 3:
        old_file = sys.argv[1]
        new_file = sys.argv[2]
    else:
        print("Usage:")
        print("  python compare_reports.py <old_report.json> <new_report.json>")
        print("  python compare_reports.py --latest")
        sys.exit(1)

    # Load data
    print(f"\nLoading reports...")
    with open(old_file, 'r') as f:
        old_data = json.load(f)
    with open(new_file, 'r') as f:
        new_data = json.load(f)

    # Analyze changes
    print("Analyzing changes...")
    detector = ChangeDetector(old_data, new_data)
    changes = detector.analyze()

    # Generate report
    print("Generating comparison report...")
    report = generate_comparison_report(changes)

    # Save outputs
    output_md = 'alaska_intel_CHANGES.md'
    with open(output_md, 'w') as f:
        f.write(report)

    output_json = 'alaska_changes.json'
    with open(output_json, 'w') as f:
        json.dump(changes, f, indent=2)

    print(f"\n✓ Comparison complete!")
    print(f"✓ Markdown report: {output_md}")
    print(f"✓ JSON data: {output_json}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"SUMMARY: {changes['summary']}")
    print(f"ALERT LEVEL: {changes['alert_level']}")
    print(f"{'='*60}")

    if changes['bonus_changes']:
        print(f"\nBonus changes: {len(changes['bonus_changes'])}")
        for change in changes['bonus_changes'][:3]:  # Show top 3
            print(f"  - {change['branch']}: ${change['old_amount']:,} → ${change['new_amount']:,} ({change['direction']})")

    if changes['messaging_shifts']:
        print(f"\nMessaging shifts: {len(changes['messaging_shifts'])}")
        for shift in changes['messaging_shifts'][:3]:  # Show top 3
            print(f"  - {shift['branch']}: '{shift['keyword']}' changed {shift.get('percent_change', 'NEW')}%")


if __name__ == '__main__':
    main()
