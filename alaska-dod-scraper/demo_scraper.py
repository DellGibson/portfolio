#!/usr/bin/env python3
"""
Alaska DoD Scraper - DEMO MODE

Generates sample data to demonstrate what the scraper outputs would look like
with real data. Use this to understand the data structure and reporting format.

Usage:
    python demo_scraper.py
"""

import json
from datetime import datetime

# Sample data simulating successful scraping
demo_data = {
    "scrape_metadata": {
        "date": datetime.now().isoformat(),
        "target_state": "Alaska",
        "branches_scraped": ["Coast Guard", "Air Force", "Navy", "Marines"],
        "total_pages": 8,
        "successful_scrapes": 8,
        "failed_scrapes": 0,
        "mode": "DEMO - Sample Data"
    },
    "competitors": [
        {
            "branch": "Coast Guard",
            "alaska_pages": [
                {
                    "url": "https://www.gocoastguard.com/about-the-coast-guard/discover-our-roles-missions/alaska-region",
                    "page_title": "Coast Guard Alaska - America's Arctic Guardians",
                    "last_updated": "2025-10-15",
                    "alaska_mentions": {
                        "count": 24,
                        "contexts": [
                            "Coast Guard Alaska operates 17 cutters and 300 aircraft supporting maritime safety across the Bering Sea and Arctic Ocean.",
                            "Stationed in Kodiak, Alaska, the nation's largest Coast Guard base, you'll protect critical fishing waters and conduct search and rescue.",
                            "Alaska offers unique duty stations including Kodiak, Sitka, Ketchikan, and Juneau with unparalleled outdoor recreation.",
                            "Cost of Living Allowance (COLA) in Alaska can add $800-$1,200 per month to your base pay.",
                            "The tight-knit community at Coast Guard Alaska creates lifelong bonds among service members and families."
                        ]
                    },
                    "bonuses": [
                        {
                            "amount": "$20,000",
                            "context": "Maritime Enforcement Specialists stationed in Alaska eligible for up to $20,000 enlistment bonus",
                            "alaska_specific": True,
                            "needs_manual_review": False
                        },
                        {
                            "amount": "$15,000",
                            "context": "Aviation Maintenance Technicians receive $15,000 bonus for Kodiak assignments",
                            "alaska_specific": True,
                            "needs_manual_review": False
                        }
                    ],
                    "duty_stations_listed": ["Kodiak", "Sitka", "Ketchikan", "Juneau"],
                    "lifestyle_messaging": {
                        "outdoor_emphasis": True,
                        "remote_pay_mentioned": True,
                        "community_tight_knit": True,
                        "family_support": True
                    },
                    "headlines": [
                        "Serve Where America's Day Begins",
                        "Alaska: The Coast Guard's Premier Operational Theater",
                        "Protect the Arctic Frontier",
                        "World-Class Fishing, Hunting, and Adventure at Your Doorstep"
                    ],
                    "ctas": [
                        {"text": "Apply for Alaska Duty", "url": "https://www.gocoastguard.com/apply", "position": "above_fold"},
                        {"text": "Talk to Alaska Recruiter", "url": "https://www.gocoastguard.com/recruiters/alaska", "position": "above_fold"},
                        {"text": "Explore Kodiak Base", "url": "https://www.gocoastguard.com/bases/kodiak", "position": "below_fold"}
                    ],
                    "testimonials": [
                        {
                            "text": "Stationed in Kodiak for 4 years - best assignment of my career. The mission is real, the scenery is unbeatable, and the camaraderie is like family.",
                            "rank_name": "Petty Officer",
                            "location": "Kodiak, Alaska",
                            "alaska_related": True
                        },
                        {
                            "text": "Alaska COLA and remote duty pay made a huge difference for my family. We saved more money here than any other duty station.",
                            "rank_name": "Chief",
                            "location": "Juneau, Alaska",
                            "alaska_related": True
                        }
                    ],
                    "keyword_frequencies": {
                        "adventure": 12,
                        "outdoor": 18,
                        "wilderness": 7,
                        "unique": 15,
                        "remote": 9,
                        "tight-knit": 4,
                        "community": 11,
                        "alaska": 24,
                        "frontier": 6,
                        "mission": 14,
                        "camaraderie": 5,
                        "stability": 3,
                        "flexibility": 2
                    }
                }
            ],
            "recruiter_contacts": [
                {
                    "office_location": "Anchorage Coast Guard Recruiting Office",
                    "phone": "907-271-6736",
                    "email": "alaskarecruiting@uscg.mil",
                    "address": "510 L St, Suite 200, Anchorage, AK 99501"
                },
                {
                    "office_location": "Kodiak Recruiting Office",
                    "phone": "907-487-5232",
                    "email": "kodiakrecruiting@uscg.mil",
                    "address": "Coast Guard Base Kodiak, AK 99619"
                }
            ]
        },
        {
            "branch": "Air Force",
            "alaska_pages": [
                {
                    "url": "https://www.jber.jb.mil/News/",
                    "page_title": "Joint Base Elmendorf-Richardson - News & Stories",
                    "last_updated": "2025-10-27",
                    "alaska_mentions": {
                        "count": 31,
                        "contexts": [
                            "JBER is the Air Force's strategic gateway to the Arctic, hosting F-22 Raptors and C-17 Globemasters.",
                            "Elmendorf-Richardson offers Alaska's best housing with mountain views and proximity to Anchorage amenities.",
                            "Air Force members at JBER receive full COLA benefits, often exceeding $1,000 monthly for families.",
                            "The Midnight Sun and Northern Lights make Alaska assignments unforgettable experiences.",
                            "JBER's outdoor recreation program offers free gear rentals for skiing, fishing, and camping across Alaska."
                        ]
                    },
                    "bonuses": [
                        {
                            "amount": "$35,000",
                            "context": "Cyber Systems Operations specialists can earn up to $35,000 enlistment bonus with JBER assignment preference",
                            "alaska_specific": True,
                            "needs_manual_review": False
                        },
                        {
                            "amount": "$25,000",
                            "context": "Aircraft Maintenance personnel receive $25,000 for 6-year enlistment at Eielson AFB near Fairbanks",
                            "alaska_specific": True,
                            "needs_manual_review": False
                        }
                    ],
                    "duty_stations_listed": ["JBER", "Joint Base Elmendorf-Richardson", "Elmendorf", "Eielson", "Clear Space Force Station"],
                    "lifestyle_messaging": {
                        "outdoor_emphasis": True,
                        "remote_pay_mentioned": True,
                        "community_tight_knit": True,
                        "family_support": True
                    },
                    "headlines": [
                        "Defend America's Arctic Domain",
                        "F-22 Raptors. Alaskan Wilderness. Your Career.",
                        "JBER: Where Mission Meets Adventure",
                        "Award-Winning Schools and Family Programs"
                    ],
                    "ctas": [
                        {"text": "Request Alaska Assignment", "url": "https://www.airforce.com/apply", "position": "above_fold"},
                        {"text": "Tour JBER Virtually", "url": "https://www.jber.jb.mil/tour", "position": "above_fold"},
                        {"text": "Connect with Alaska Recruiter", "url": "https://www.airforce.com/find-a-recruiter", "position": "below_fold"}
                    ],
                    "testimonials": [
                        {
                            "text": "Three years at JBER and I've summited Denali, caught 50-pound king salmon, and worked on the most advanced fighters in the world. Can't beat it.",
                            "rank_name": "Staff Sergeant",
                            "location": "JBER, Alaska",
                            "alaska_related": True
                        }
                    ],
                    "keyword_frequencies": {
                        "adventure": 16,
                        "outdoor": 22,
                        "wilderness": 11,
                        "unique": 18,
                        "remote": 7,
                        "tight-knit": 5,
                        "community": 13,
                        "alaska": 31,
                        "frontier": 4,
                        "mission": 19,
                        "camaraderie": 6,
                        "stability": 8,
                        "flexibility": 5
                    }
                }
            ],
            "recruiter_contacts": [
                {
                    "office_location": "Anchorage Air Force Recruiting Office",
                    "phone": "907-552-3896",
                    "email": "anchorage.recruiting@us.af.mil",
                    "address": "8510 Lake Otis Pkwy, Anchorage, AK 99507"
                },
                {
                    "office_location": "Fairbanks Air Force Recruiting",
                    "phone": "907-356-4422",
                    "email": "fairbanks.recruiting@us.af.mil",
                    "address": "567 Gaffney Rd, Fort Wainwright, AK 99703"
                }
            ]
        },
        {
            "branch": "Navy",
            "alaska_pages": [
                {
                    "url": "https://www.navy.com/local/alaska",
                    "page_title": "U.S. Navy Recruiting - Alaska",
                    "last_updated": "2025-10-20",
                    "alaska_mentions": {
                        "count": 8,
                        "contexts": [
                            "Navy personnel in Alaska support Arctic operations and strategic deterrence missions.",
                            "Alaska duty offers Navy members unique cold-weather training opportunities.",
                            "Submarine forces operating from Alaska receive specialized Arctic pay.",
                        ]
                    },
                    "bonuses": [
                        {
                            "amount": "$10,000",
                            "context": "Nuclear-trained personnel can receive up to $10,000 additional bonus for Alaska assignments",
                            "alaska_specific": True,
                            "needs_manual_review": False
                        }
                    ],
                    "duty_stations_listed": [],
                    "lifestyle_messaging": {
                        "outdoor_emphasis": False,
                        "remote_pay_mentioned": True,
                        "community_tight_knit": False,
                        "family_support": True
                    },
                    "headlines": [
                        "Navy Alaska - Arctic Excellence",
                        "Serve in America's Last Frontier"
                    ],
                    "ctas": [
                        {"text": "Talk to a Navy Recruiter", "url": "https://www.navy.com/contact", "position": "above_fold"},
                        {"text": "Explore Navy Jobs", "url": "https://www.navy.com/careers", "position": "below_fold"}
                    ],
                    "testimonials": [],
                    "keyword_frequencies": {
                        "adventure": 3,
                        "outdoor": 2,
                        "wilderness": 1,
                        "unique": 4,
                        "remote": 3,
                        "tight-knit": 0,
                        "community": 2,
                        "alaska": 8,
                        "frontier": 1,
                        "mission": 6,
                        "camaraderie": 1,
                        "stability": 2,
                        "flexibility": 1
                    }
                }
            ],
            "recruiter_contacts": [
                {
                    "office_location": "Anchorage Navy Recruiting Station",
                    "phone": "907-279-2704",
                    "email": "anchorage.recruiting@navy.mil",
                    "address": "3601 C St #960, Anchorage, AK 99503"
                }
            ]
        },
        {
            "branch": "Marines",
            "alaska_pages": [
                {
                    "url": "https://www.marines.com/contact-a-recruiter/alaska",
                    "page_title": "Marine Corps Recruiting - Alaska",
                    "last_updated": "2025-10-18",
                    "alaska_mentions": {
                        "count": 5,
                        "contexts": [
                            "Marines stationed in Alaska train in extreme cold-weather environments.",
                            "Alaska prepares Marines for Arctic warfare and expeditionary operations.",
                        ]
                    },
                    "bonuses": [
                        {
                            "amount": "$8,000",
                            "context": "Infantry Marines can receive $8,000 enlistment bonus",
                            "alaska_specific": False,
                            "needs_manual_review": False
                        }
                    ],
                    "duty_stations_listed": [],
                    "lifestyle_messaging": {
                        "outdoor_emphasis": True,
                        "remote_pay_mentioned": False,
                        "community_tight_knit": True,
                        "family_support": False
                    },
                    "headlines": [
                        "The Few. The Proud. The Arctic Warriors.",
                        "Forge Your Future in Alaska"
                    ],
                    "ctas": [
                        {"text": "Become a Marine", "url": "https://www.marines.com/become-a-marine", "position": "above_fold"},
                        {"text": "Find Alaska Recruiter", "url": "https://www.marines.com/find-recruiter", "position": "above_fold"}
                    ],
                    "testimonials": [],
                    "keyword_frequencies": {
                        "adventure": 2,
                        "outdoor": 4,
                        "wilderness": 2,
                        "unique": 3,
                        "remote": 1,
                        "tight-knit": 1,
                        "community": 3,
                        "alaska": 5,
                        "frontier": 2,
                        "mission": 7,
                        "camaraderie": 4,
                        "stability": 1,
                        "flexibility": 0
                    }
                }
            ],
            "recruiter_contacts": [
                {
                    "office_location": "Anchorage Marine Corps Recruiting",
                    "phone": "907-276-4062",
                    "email": "recruiting.anchorage@usmc.mil",
                    "address": "550 W 7th Ave #1770, Anchorage, AK 99501"
                }
            ]
        }
    ]
}


def generate_demo_summary():
    """Generate markdown summary from demo data."""
    md = []

    md.append("# Alaska DoD Competitor Intelligence Report (DEMO)")
    md.append(f"**Scraped:** {datetime.now().strftime('%Y-%m-%d')}")
    md.append("**Branches Analyzed:** Coast Guard, Air Force, Navy, Marines")
    md.append("**NOTE:** This is DEMO DATA showing expected output format\n")

    md.append("## Executive Summary\n")
    md.append("- **4** of 4 branches have Alaska-specific recruiting content")
    md.append("- **Coast Guard** and **Air Force** lead in Alaska-specific messaging (24 and 31 mentions)")
    md.append("- **Air Force** offers highest bonuses: up to $35,000 for cyber roles at JBER")
    md.append("- **Coast Guard** has most comprehensive Alaska duty station coverage")
    md.append("- Common themes: outdoor recreation, remote duty pay, tight-knit communities\n")

    md.append("## Branch-by-Branch Alaska Positioning\n")

    # Coast Guard
    md.append("### Coast Guard\n")
    md.append("**Alaska Duty Stations Promoted:** Kodiak, Sitka, Ketchikan, Juneau\n")
    md.append("**Top Messaging Themes:** outdoor (18), alaska (24), unique (15), mission (14), adventure (12)\n")
    md.append("**Bonuses for Alaska Duty:**\n")
    md.append("| Amount | Rating | Notes |")
    md.append("|--------|--------|-------|")
    md.append("| $20,000 | Maritime Enforcement Specialist | Alaska-specific |")
    md.append("| $15,000 | Aviation Maintenance Technician | Kodiak assignment |")
    md.append("\n**Unique Alaska Angle:** Positions Alaska as 'America's Arctic Guardians' with emphasis on COLA ($800-$1,200/month) and world-class outdoor recreation. Strong testimonial strategy highlighting family savings and quality of life.\n")
    md.append("---\n")

    # Air Force
    md.append("### Air Force\n")
    md.append("**Alaska Duty Stations Promoted:** JBER, Elmendorf-Richardson, Eielson, Clear Space Force Station\n")
    md.append("**Top Messaging Themes:** alaska (31), outdoor (22), mission (19), unique (18), adventure (16)\n")
    md.append("**Bonuses for Alaska Duty:**\n")
    md.append("| Amount | AFSC | Notes |")
    md.append("|--------|------|-------|")
    md.append("| $35,000 | Cyber Systems Operations | JBER assignment preference |")
    md.append("| $25,000 | Aircraft Maintenance | Eielson AFB, 6-year enlistment |")
    md.append("\n**Unique Alaska Angle:** Leverages JBER prestige and F-22 mission cachet. Emphasizes 'strategic gateway to Arctic' positioning. Strong family messaging with award-winning schools and free outdoor rec gear.\n")
    md.append("---\n")

    # Navy
    md.append("### Navy\n")
    md.append("**Alaska Duty Stations Promoted:** None explicitly mentioned\n")
    md.append("**Top Messaging Themes:** alaska (8), mission (6), unique (4), adventure (3)\n")
    md.append("**Bonuses for Alaska Duty:**\n")
    md.append("| Amount | Rating | Notes |")
    md.append("|--------|--------|-------|")
    md.append("| $10,000 | Nuclear-trained personnel | Additional bonus for Alaska |")
    md.append("\n**Unique Alaska Angle:** Limited Alaska-specific content. Focuses on Arctic operations and specialized pay. Less emphasis on lifestyle/quality of life compared to Coast Guard and Air Force.\n")
    md.append("---\n")

    # Marines
    md.append("### Marines\n")
    md.append("**Alaska Duty Stations Promoted:** None explicitly mentioned\n")
    md.append("**Top Messaging Themes:** mission (7), outdoor (4), camaraderie (4), unique (3)\n")
    md.append("**Bonuses for Alaska Duty:**\n")
    md.append("| Amount | MOS | Notes |")
    md.append("|--------|-----|-------|")
    md.append("| $8,000 | Infantry | Not Alaska-specific |")
    md.append("\n**Unique Alaska Angle:** Positions Alaska as cold-weather/Arctic warfare training ground. Emphasizes toughness over lifestyle benefits. 'Arctic Warriors' branding.\n")
    md.append("---\n")

    # Cross-branch insights
    md.append("## Cross-Branch Insights\n")
    md.append("**Most Common Alaska Appeal:** Outdoor recreation - mentioned by 4/4 branches\n")
    md.append("**Highest Alaska Bonus:** Air Force Cyber Systems Operations - $35,000\n")
    md.append("**Most Alaska Mentions:** Air Force JBER (31 mentions), Coast Guard (24 mentions)\n")
    md.append("**Weakest Alaska Positioning:** Navy and Marines - limited duty station details and lifestyle messaging\n\n")

    md.append("**Key Competitive Themes:**\n")
    md.append("1. **Full-time employment** - All branches emphasize active duty stability vs. Guard part-time")
    md.append("2. **Geographic certainty** - 'Pick Alaska and stay Alaska' vs. unknown Guard drill locations")
    md.append("3. **Bonus size** - Air Force $35K and Coast Guard $20K exceed typical Guard bonuses")
    md.append("4. **Mission prestige** - F-22s at JBER, Coast Guard Arctic ops > Guard state mission perception")
    md.append("5. **Remote duty pay** - COLA explicitly marketed as $800-$1,200/month additional income\n")

    md.append("## AKARNG Response Recommendations\n")
    md.append("1. **Counter the full-time myth:** Create content showcasing AGR positions (Active Guard Reserve) and full-time technician jobs within AKARNG - match Air Force's $35K with competitive tech role bonuses")
    md.append("2. **Flip geographic stability:** Position AKARNG as 'Serve your Alaska community for life' vs. active duty PCS rotations every 3-4 years. Testimonials from 10+ year AKARNG members who've never left Alaska")
    md.append("3. **Match or exceed bonuses:** Review current AKARNG incentive structure. If Coast Guard offers $20K for ME, AKARNG should offer $22K+ for comparable MOSs")
    md.append("4. **Own the state mission:** Emphasize wildfire response, disaster relief, COVID response - missions active duty didn't/can't do. 'We protect Alaskans, not just America'")
    md.append("5. **Target families explicitly:** Coast Guard and Air Force lead here. AKARNG needs content on: spousal employment flexibility (don't PCS), no uprooting kids from schools, building generational Alaskan roots")
    md.append("6. **Leverage outdoor rec authenticity:** Active duty members leave Alaska after 3-4 years. AKARNG members ARE Alaskans - they know the best fishing holes, hunting spots, trails. Position as 'real Alaskans' vs. 'tourists in uniform'")
    md.append("7. **Create Alaska duty station comparison page:** Side-by-side AKARNG armories/facilities vs. JBER/Kodiak. Show AKARNG locations in Fairbanks, Anchorage, Juneau, Bethel, Nome - 'serve in YOUR Alaska community'")
    md.append("8. **Counter 'mission prestige' gap:** F-22s are sexy, but AKARNG has unique Arctic training, partnership with active duty (JBER support missions), and state-side hero opportunities (saving lives in disasters)\n")

    md.append("## Guard-Specific Vulnerabilities Identified\n")
    md.append("Based on competitor messaging, these are the objections AKARNG must address:\n")
    md.append("- **'Part-time pay'** - Competitors imply Guard income is unreliable. Counter: Highlight AGR, technician, and deployment pay potential")
    md.append("- **'Limited benefits'** - Coast Guard emphasizes full healthcare/housing. Counter: Guard benefits are comparable, plus state education benefits active duty doesn't get")
    md.append("- **'No guaranteed Alaska assignment'** - Active duty markets 'pick your duty station'. Counter: Guard IS the Alaska assignment - you never leave")
    md.append("- **'Lower mission impact'** - F-22s vs. 'weekend warrior' perception. Counter: Guard does real-world state emergencies, not just training")
    md.append("- **'Smaller bonuses'** - Air Force $35K creates anchor. Counter: Match it or position Guard bonuses + state benefits + stay-in-Alaska value as higher lifetime value\n")

    md.append("---")
    md.append("*DEMO Report generated by Alaska DoD Scraper v1.0*")
    md.append(f"*This is sample data showing expected output format - {datetime.now().strftime('%Y-%m-%d')}*")

    return '\n'.join(md)


def main():
    """Generate demo outputs."""
    print("="*60)
    print("Alaska DoD Scraper - DEMO MODE")
    print("Generating sample data outputs...")
    print("="*60)
    print()

    # Save demo JSON
    with open('alaska_competitor_data_DEMO.json', 'w', encoding='utf-8') as f:
        json.dump(demo_data, f, indent=2, ensure_ascii=False)
    print("✓ Generated alaska_competitor_data_DEMO.json")

    # Save demo markdown
    md_content = generate_demo_summary()
    with open('alaska_intel_summary_DEMO.md', 'w', encoding='utf-8') as f:
        f.write(md_content)
    print("✓ Generated alaska_intel_summary_DEMO.md")

    print("\n" + "="*60)
    print("Demo outputs created successfully!")
    print("="*60)
    print("\nThese files show what the scraper would produce with real data.")
    print("Review these to understand the intelligence format and insights.")
    print("\nTo run actual scraping (may encounter 403 errors):")
    print("  python scraper_script.py")


if __name__ == '__main__':
    main()
