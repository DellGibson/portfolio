#!/usr/bin/env python3
"""
Email Alert System for Alaska DoD Competitor Intelligence

Sends email notifications when significant competitive changes are detected:
- Large bonus increases ($5,000+)
- New bonuses added
- Major messaging shifts (50%+ change)
- New duty stations

Configuration: Edit config/alerts.yaml

Usage:
    python alert_system.py alaska_changes.json
    python alert_system.py --check-and-alert  # Run comparison then alert
"""

import json
import sys
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from typing import Dict, List


# Default configuration
DEFAULT_CONFIG = {
    'email': {
        'enabled': True,
        'smtp_server': 'smtp.gmail.com',  # Change to your SMTP server
        'smtp_port': 587,
        'use_tls': True,
        'from_address': os.getenv('ALERT_FROM_EMAIL', 'alaska-intel@example.com'),
        'from_name': 'Alaska DoD Intelligence',
        'to_addresses': os.getenv('ALERT_TO_EMAILS', 'recruiting@example.com').split(','),
        'username': os.getenv('SMTP_USERNAME', ''),
        'password': os.getenv('SMTP_PASSWORD', ''),
    },
    'thresholds': {
        'bonus_change_high': 5000,  # $5,000+ triggers HIGH alert
        'bonus_change_medium': 2000,  # $2,000+ triggers MEDIUM alert
        'messaging_shift_significant': 50,  # 50%+ change in keyword frequency
        'alert_on_new_bonuses': True,
        'alert_on_duty_station_changes': True,
    },
    'slack': {
        'enabled': False,
        'webhook_url': os.getenv('SLACK_WEBHOOK_URL', ''),
    }
}


class AlertSystem:
    """Manages alerts for competitive intelligence changes."""

    def __init__(self, config: Dict = None):
        self.config = config or DEFAULT_CONFIG

    def should_alert(self, changes: Dict) -> bool:
        """Determine if changes warrant an alert."""
        # Check for high-priority bonus changes
        high_priority_bonuses = [
            b for b in changes.get('bonus_changes', [])
            if b.get('alert_level') == 'HIGH'
        ]

        if high_priority_bonuses:
            return True

        # Check for significant messaging shifts
        significant_messaging = [
            m for m in changes.get('messaging_shifts', [])
            if m.get('significance') == 'HIGH'
        ]

        if significant_messaging:
            return True

        # Check for new duty stations
        if changes.get('duty_station_changes') and self.config['thresholds']['alert_on_duty_station_changes']:
            return True

        # Check overall alert level
        if changes.get('alert_level') in ['HIGH', 'CRITICAL']:
            return True

        return False

    def generate_email_subject(self, changes: Dict) -> str:
        """Generate email subject line based on changes."""
        alert_level = changes.get('alert_level', 'NONE')

        if alert_level == 'HIGH':
            return "🚨 URGENT: Alaska Competitor Bonus Increase Detected"
        elif alert_level == 'MEDIUM':
            return "⚠️ Alaska Competitor Intelligence Update - Action Recommended"
        else:
            return "📊 Alaska Competitor Intelligence - Monthly Update"

    def generate_email_body(self, changes: Dict) -> str:
        """Generate HTML email body."""
        html = []

        html.append("""
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .header { background-color: #d32f2f; color: white; padding: 20px; }
                .warning { background-color: #d32f2f; color: white; padding: 20px; }
                .info { background-color: #1976d2; color: white; padding: 20px; }
                .content { padding: 20px; }
                table { border-collapse: collapse; width: 100%; margin: 20px 0; }
                th { background-color: #f5f5f5; padding: 10px; text-align: left; border-bottom: 2px solid #ddd; }
                td { padding: 10px; border-bottom: 1px solid #ddd; }
                .increase { color: #d32f2f; font-weight: bold; }
                .new { color: #1976d2; font-weight: bold; }
                .recommendation { background-color: #fff3cd; padding: 15px; margin: 15px 0; border-left: 4px solid: #ffc107; }
                .footer { background-color: #f5f5f5; padding: 15px; margin-top: 20px; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
        """)

        # Header
        if changes.get('alert_level') == 'HIGH':
            html.append("""
            <div class="warning">
                <h1>🚨 HIGH PRIORITY ALERT</h1>
                <p><strong>Competitor made significant changes to Alaska recruiting strategy</strong></p>
            </div>
            """)
        else:
            html.append("""
            <div class="info">
                <h1>Alaska DoD Competitor Intelligence Update</h1>
            </div>
            """)

        html.append('<div class="content">')

        # Summary
        html.append(f"<h2>Summary</h2>")
        html.append(f"<p>{changes.get('summary', 'No significant changes')}</p>")
        html.append(f"<p><strong>Report Period:</strong> {changes['metadata']['old_date'][:10]} to {changes['metadata']['new_date'][:10]}</p>")

        # Bonus changes
        if changes.get('bonus_changes'):
            html.append("<h2>💰 Bonus Changes</h2>")

            # High priority
            high_priority = [b for b in changes['bonus_changes'] if b['alert_level'] == 'HIGH']
            if high_priority:
                html.append("<h3>🚨 High Priority</h3>")
                html.append("<table>")
                html.append("<tr><th>Branch</th><th>Old Amount</th><th>New Amount</th><th>Change</th><th>Type</th></tr>")

                for change in high_priority:
                    old_fmt = f"${change['old_amount']:,}" if change['old_amount'] > 0 else "N/A"
                    new_fmt = f"${change['new_amount']:,}"
                    delta_fmt = f"+${change['delta']:,}" if change['delta'] > 0 else f"-${abs(change['delta']):,}"
                    delta_class = 'increase' if change['delta'] > 0 else ''

                    html.append(f"""
                    <tr>
                        <td><strong>{change['branch']}</strong></td>
                        <td>{old_fmt}</td>
                        <td>{new_fmt}</td>
                        <td class="{delta_class}">{delta_fmt} ({change['delta_percent']:+.1f}%)</td>
                        <td class="{change['direction'].lower()}">{change['direction']}</td>
                    </tr>
                    """)

                html.append("</table>")

            # Other changes
            other_changes = [b for b in changes['bonus_changes'] if b['alert_level'] != 'HIGH']
            if other_changes:
                html.append("<h3>Other Changes</h3>")
                html.append("<table>")
                html.append("<tr><th>Branch</th><th>Old Amount</th><th>New Amount</th><th>Change</th></tr>")

                for change in other_changes:
                    old_fmt = f"${change['old_amount']:,}" if change['old_amount'] > 0 else "N/A"
                    new_fmt = f"${change['new_amount']:,}"
                    delta_fmt = f"+${change['delta']:,}" if change['delta'] > 0 else f"-${abs(change['delta']):,}"

                    html.append(f"""
                    <tr>
                        <td>{change['branch']}</td>
                        <td>{old_fmt}</td>
                        <td>{new_fmt}</td>
                        <td>{delta_fmt} ({change['delta_percent']:+.1f}%)</td>
                    </tr>
                    """)

                html.append("</table>")

        # Messaging shifts
        if changes.get('messaging_shifts'):
            significant = [m for m in changes['messaging_shifts'] if m.get('significance') == 'HIGH']
            if significant:
                html.append("<h2>📊 Significant Messaging Shifts</h2>")
                html.append("<ul>")

                for shift in significant[:5]:  # Top 5
                    if shift.get('change_type') == 'ALASKA_FOCUS_SHIFT':
                        html.append(f"<li><strong>{shift['branch']}</strong>: Alaska mentions changed from {shift['old_count']} to {shift['new_count']} ({shift['percent_change']:+.1f}%)</li>")
                    else:
                        html.append(f"<li><strong>{shift['branch']}</strong>: '{shift['keyword']}' keyword usage changed {shift.get('percent_change', 'NEW')}%</li>")

                html.append("</ul>")

        # Duty station changes
        if changes.get('duty_station_changes'):
            html.append("<h2>🗺️ Duty Station Changes</h2>")
            html.append("<ul>")

            for change in changes['duty_station_changes']:
                if change['change_type'] == 'ADDED':
                    html.append(f"<li><strong>{change['branch']}</strong> added: {', '.join(change['stations'])}</li>")
                else:
                    html.append(f"<li><strong>{change['branch']}</strong> removed: {', '.join(change['stations'])}</li>")

            html.append("</ul>")

        # Recommendations
        html.append("<h2>🎯 Recommended Actions</h2>")
        html.append('<div class="recommendation">')

        if changes.get('bonus_changes'):
            max_increase = max([b['delta'] for b in changes['bonus_changes'] if b['direction'] in ['INCREASE', 'NEW']], default=0)
            if max_increase >= 5000:
                html.append(f"""
                <p><strong>URGENT - Bonus Structure Review:</strong> Competitor increased bonuses by up to ${max_increase:,}.</p>
                <ul>
                    <li>Convene recruiting leadership within 72 hours</li>
                    <li>Review current AKARNG bonus structure</li>
                    <li>Consider matching or exceeding to maintain competitiveness</li>
                    <li>Analyze recruitment impact if no action taken</li>
                </ul>
                """)
            elif max_increase >= 2000:
                html.append(f"""
                <p><strong>Bonus Review Recommended:</strong> Competitor increased bonuses by ${max_increase:,}.</p>
                <ul>
                    <li>Monitor recruitment metrics for next 30 days</li>
                    <li>Review bonus effectiveness at next planning meeting</li>
                </ul>
                """)

        significant_messaging = [m for m in changes.get('messaging_shifts', []) if m.get('significance') == 'HIGH']
        if significant_messaging:
            top_shift = significant_messaging[0]
            html.append(f"""
            <p><strong>Messaging Adaptation:</strong> {top_shift['branch']} significantly increased '{top_shift['keyword']}' messaging.</p>
            <ul>
                <li>Review AKARNG content strategy</li>
                <li>Consider incorporating similar themes in recruitment materials</li>
            </ul>
            """)

        if not changes.get('bonus_changes') and not significant_messaging:
            html.append("<p>No immediate action required. Continue monitoring monthly.</p>")

        html.append('</div>')

        html.append('</div>')  # Close content

        # Footer
        html.append(f"""
        <div class="footer">
            <p>This is an automated alert from the Alaska DoD Competitor Intelligence System.</p>
            <p>Full report available in: <strong>alaska_intel_CHANGES.md</strong></p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>For questions or to unsubscribe, contact your system administrator.</p>
        </div>
        """)

        html.append("</body></html>")

        return '\n'.join(html)

    def send_email_alert(self, changes: Dict) -> bool:
        """Send email alert."""
        if not self.config['email']['enabled']:
            print("Email alerts disabled in configuration")
            return False

        if not self.config['email']['username'] or not self.config['email']['password']:
            print("⚠️  Email credentials not configured. Set SMTP_USERNAME and SMTP_PASSWORD environment variables.")
            print("\nExample:")
            print("  export SMTP_USERNAME='your-email@gmail.com'")
            print("  export SMTP_PASSWORD='your-app-password'")
            print("  export ALERT_TO_EMAILS='recruiting@akarng.mil,leadership@akarng.mil'")
            print("\nFor Gmail, use App Passwords: https://support.google.com/accounts/answer/185833")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = self.generate_email_subject(changes)
            msg['From'] = f"{self.config['email']['from_name']} <{self.config['email']['from_address']}>"
            msg['To'] = ', '.join(self.config['email']['to_addresses'])

            # Generate body
            html_body = self.generate_email_body(changes)
            msg.attach(MIMEText(html_body, 'html'))

            # Send email
            print(f"\nSending alert email to: {', '.join(self.config['email']['to_addresses'])}")

            with smtplib.SMTP(self.config['email']['smtp_server'], self.config['email']['smtp_port']) as server:
                if self.config['email']['use_tls']:
                    server.starttls()

                server.login(self.config['email']['username'], self.config['email']['password'])
                server.send_message(msg)

            print("✓ Email alert sent successfully!")
            return True

        except Exception as e:
            print(f"✗ Failed to send email: {str(e)}")
            return False

    def send_slack_alert(self, changes: Dict) -> bool:
        """Send Slack notification."""
        if not self.config['slack']['enabled']:
            return False

        if not self.config['slack']['webhook_url']:
            print("⚠️  Slack webhook not configured")
            return False

        try:
            import requests

            # Build Slack message
            blocks = []

            # Header
            if changes.get('alert_level') == 'HIGH':
                blocks.append({
                    "type": "header",
                    "text": {"type": "plain_text", "text": "🚨 HIGH PRIORITY: Alaska Competitor Alert"}
                })
            else:
                blocks.append({
                    "type": "header",
                    "text": {"type": "plain_text", "text": "Alaska DoD Competitor Update"}
                })

            # Summary
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Summary:* {changes.get('summary', 'No changes')}"}
            })

            # Bonus changes
            if changes.get('bonus_changes'):
                bonus_text = ""
                for change in changes['bonus_changes'][:3]:  # Top 3
                    delta_fmt = f"+${change['delta']:,}" if change['delta'] > 0 else f"${change['delta']:,}"
                    bonus_text += f"• *{change['branch']}*: ${change['old_amount']:,} → ${change['new_amount']:,} ({delta_fmt})\n"

                blocks.append({
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*Bonus Changes:*\n{bonus_text}"}
                })

            # Send to Slack
            response = requests.post(
                self.config['slack']['webhook_url'],
                json={'blocks': blocks}
            )

            if response.status_code == 200:
                print("✓ Slack alert sent successfully!")
                return True
            else:
                print(f"✗ Slack alert failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"✗ Failed to send Slack alert: {str(e)}")
            return False

    def process_changes(self, changes: Dict):
        """Process changes and send alerts if warranted."""
        print("="*60)
        print("Alaska DoD Intelligence - Alert System")
        print("="*60)
        print()

        print(f"Summary: {changes.get('summary', 'No changes')}")
        print(f"Alert Level: {changes.get('alert_level', 'NONE')}")
        print()

        if self.should_alert(changes):
            print("✓ Changes warrant an alert\n")

            # Send email
            if self.config['email']['enabled']:
                self.send_email_alert(changes)

            # Send Slack
            if self.config['slack']['enabled']:
                self.send_slack_alert(changes)

        else:
            print("ℹ️  No significant changes detected - no alert sent")
            print("   (Changes don't meet threshold criteria)")


def load_changes(filename: str) -> Dict:
    """Load changes from JSON file."""
    with open(filename, 'r') as f:
        return json.load(f)


def main():
    """Main execution."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python alert_system.py <changes.json>")
        print("  python alert_system.py alaska_changes.json")
        print()
        print("Configuration:")
        print("  Set environment variables:")
        print("    SMTP_USERNAME - Your SMTP username")
        print("    SMTP_PASSWORD - Your SMTP password")
        print("    ALERT_TO_EMAILS - Comma-separated recipient emails")
        print("    SLACK_WEBHOOK_URL - Slack webhook URL (optional)")
        sys.exit(1)

    changes_file = sys.argv[1]

    if not Path(changes_file).exists():
        print(f"Error: File not found: {changes_file}")
        sys.exit(1)

    # Load changes
    changes = load_changes(changes_file)

    # Process and send alerts
    alert_system = AlertSystem()
    alert_system.process_changes(changes)


if __name__ == '__main__':
    main()
