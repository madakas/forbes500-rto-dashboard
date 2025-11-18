#!/usr/bin/env python3
"""
Add missing high-priority companies to the enriched dataset.
Combines RTO policy data, innovation rankings, and company enrichment data.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

# 10 high-priority missing companies with complete data
MISSING_COMPANIES = [
    {
        "company": "Apple",
        "rank": 3,
        "sector": "Technology",
        "fortune_500_rank": "3",
        "work_policy": {
            "type": "3-day hybrid",
            "category": "Hybrid",
            "days_required": 3,
            "specific_days": "Monday, Tuesday, Thursday",
            "details": "Employees required to work in office 3 days per week. Tim Cook: 'combine the best of what we have learned about working remotely with the irreplaceable benefits of in-person collaboration'",
            "effective_date": "2022-09-05",
            "trend_direction": "Maintaining",
            "previous_policy": "Remote during COVID",
            "previous_date": "2020-2022"
        },
        "sources": [
            {"url": "https://buildremote.co/return-to-office/apple/", "type": "Tracker", "reliability": "High"}
        ],
        "key_quote": "Combine the best of what we have learned about working remotely with the irreplaceable benefits of in-person collaboration",
        "verification_status": "Verified",
        "research_date": "2025-11-18",
        "notes": "",
        "innovation": {"culture_rank": 25, "process_rank": 9, "product_rank": 2, "overall_rank": 3},
        "logo_url": "https://logo.clearbit.com/apple.com",
        "headquarters": "Cupertino, California, USA",
        "industry_sector": "Technology - Consumer Electronics",
        "employee_count": 164000,
        "enrichment_source": "BuildRemote.co, Wikipedia",
        "enrichment_date": "2025"
    },
    {
        "company": "IBM",
        "rank": 4,
        "sector": "Technology",
        "fortune_500_rank": "63",
        "work_policy": {
            "type": "3-day hybrid",
            "category": "Hybrid",
            "days_required": 3,
            "specific_days": "N/A",
            "details": "U.S. sales staff and cloud employees required minimum 3 days/week. Internally branded as 'return to client' for sales roles. Employees >50 miles from office may be offered relocation.",
            "effective_date": "2025-04-18",
            "trend_direction": "Tightening",
            "previous_policy": "Flexible remote",
            "previous_date": "2020-2024"
        },
        "sources": [
            {"url": "https://buildremote.co/return-to-office/ibm/", "type": "Tracker", "reliability": "High"}
        ],
        "key_quote": "Third attempt at RTO enforcement with stronger mandates",
        "verification_status": "Verified",
        "research_date": "2025-11-18",
        "notes": "3rd attempt at enforcement",
        "innovation": {"culture_rank": 14, "process_rank": 15, "product_rank": 4, "overall_rank": 4},
        "logo_url": "https://logo.clearbit.com/ibm.com",
        "headquarters": "Armonk, New York, USA",
        "industry_sector": "IT Services and Consulting",
        "employee_count": 282000,
        "enrichment_source": "BuildRemote.co, Wikipedia",
        "enrichment_date": "2025"
    },
    {
        "company": "Salesforce",
        "rank": 5,
        "sector": "Technology",
        "fortune_500_rank": "136",
        "work_policy": {
            "type": "Tiered hybrid (3-5 days)",
            "category": "Hybrid",
            "days_required": 4,
            "specific_days": "Varies by role",
            "details": "Sales: 4-5 days/week, Other: 3 days/week, Engineers: 10 days/quarter minimum. Categories: Office-Based, Office-Flex, Remote. Badge scan tracking enforced.",
            "effective_date": "2024-10-01",
            "trend_direction": "Tightening",
            "previous_policy": "Flexible remote-first",
            "previous_date": "2020-2024"
        },
        "sources": [
            {"url": "https://buildremote.co/return-to-office/salesforce/", "type": "Tracker", "reliability": "High"}
        ],
        "key_quote": "CEO Marc Benioff reversed position after saying in 2022 'Office mandates are never going to work'",
        "verification_status": "Verified",
        "research_date": "2025-11-18",
        "notes": "CEO reversed anti-mandate position",
        "innovation": {"culture_rank": 8, "process_rank": 7, "product_rank": 22, "overall_rank": 5},
        "logo_url": "https://logo.clearbit.com/salesforce.com",
        "headquarters": "San Francisco, California, USA",
        "industry_sector": "Cloud Computing and Enterprise Software",
        "employee_count": 79000,
        "enrichment_source": "BuildRemote.co, Wikipedia",
        "enrichment_date": "2025"
    },
    {
        "company": "Oracle",
        "rank": 6,
        "sector": "Technology",
        "fortune_500_rank": "80",
        "work_policy": {
            "type": "Team-dependent hybrid",
            "category": "Hybrid",
            "days_required": 3,
            "specific_days": "N/A - Team dependent",
            "details": "Policy varies significantly by team - some full remote, some hybrid. Requires negotiation during hiring. Generally 0-5 days depending on organization.",
            "effective_date": "N/A",
            "trend_direction": "Unknown",
            "previous_policy": "",
            "previous_date": ""
        },
        "sources": [
            {"url": "https://www.glassdoor.com/oracle", "type": "Employee Reports", "reliability": "Medium"}
        ],
        "key_quote": "Policy varies by team and requires negotiation during hiring",
        "verification_status": "Partial",
        "research_date": "2025-11-18",
        "notes": "Organization-specific policies",
        "innovation": {"culture_rank": 48, "process_rank": 12, "product_rank": 7, "overall_rank": 6},
        "logo_url": "https://logo.clearbit.com/oracle.com",
        "headquarters": "Austin, Texas, USA",
        "industry_sector": "IT Services and Consulting",
        "employee_count": 202000,
        "enrichment_source": "Employee Reports, Wikipedia",
        "enrichment_date": "2025"
    },
    {
        "company": "Adobe",
        "rank": 9,
        "sector": "Technology",
        "fortune_500_rank": "234",
        "work_policy": {
            "type": "3-day hybrid",
            "category": "Hybrid",
            "days_required": 3,
            "specific_days": "Org-specific (employee polling)",
            "details": "Employees work 3 days in office with day selection determined by organization through employee polling.",
            "effective_date": "2022-06",
            "trend_direction": "Maintaining",
            "previous_policy": "Remote during COVID",
            "previous_date": "2020-2022"
        },
        "sources": [
            {"url": "https://buildremote.co/return-to-office/adobe/", "type": "Tracker", "reliability": "High"}
        ],
        "key_quote": "Day selection determined by organization through employee polling",
        "verification_status": "Verified",
        "research_date": "2025-11-18",
        "notes": "",
        "innovation": {"culture_rank": 17, "process_rank": 16, "product_rank": 27, "overall_rank": 9},
        "logo_url": "https://logo.clearbit.com/adobe.com",
        "headquarters": "San Jose, California, USA",
        "industry_sector": "Software Development",
        "employee_count": 40000,
        "enrichment_source": "BuildRemote.co, Wikipedia",
        "enrichment_date": "2025"
    },
    {
        "company": "Cisco Systems",
        "rank": 10,
        "sector": "Technology",
        "fortune_500_rank": "74",
        "work_policy": {
            "type": "Hybrid (transitioning)",
            "category": "Hybrid",
            "days_required": 3,
            "specific_days": "N/A",
            "details": "RTO mandate effective February 24, 2025. Cisco publishes extensive hybrid work research showing 63% of employees would take pay cuts for flexibility.",
            "effective_date": "2025-02-24",
            "trend_direction": "Tightening",
            "previous_policy": "Flexible hybrid",
            "previous_date": "2020-2024"
        },
        "sources": [
            {"url": "https://buildremote.co/return-to-office/cisco/", "type": "Tracker", "reliability": "High"}
        ],
        "key_quote": "63% of employees would take pay cuts for flexibility",
        "verification_status": "Verified",
        "research_date": "2025-11-18",
        "notes": "Company publishes hybrid work research",
        "innovation": {"culture_rank": 19, "process_rank": 21, "product_rank": 20, "overall_rank": 10},
        "logo_url": "https://logo.clearbit.com/cisco.com",
        "headquarters": "San Jose, California, USA",
        "industry_sector": "Technology - Networking and Communications",
        "employee_count": 86200,
        "enrichment_source": "BuildRemote.co, Wikipedia",
        "enrichment_date": "2025"
    },
    {
        "company": "Intel",
        "rank": 12,
        "sector": "Technology",
        "fortune_500_rank": "56",
        "work_policy": {
            "type": "4-day hybrid",
            "category": "Hybrid",
            "days_required": 4,
            "specific_days": "N/A",
            "details": "Increased from 3 to 4 days per week. CEO Lip-Bu Tan: 'When we spend time together in person, it fosters more engaging and productive discussion and debate.'",
            "effective_date": "2025-09-01",
            "trend_direction": "Tightening",
            "previous_policy": "3-day hybrid",
            "previous_date": "2023-2024"
        },
        "sources": [
            {"url": "https://buildremote.co/return-to-office/intel/", "type": "Tracker", "reliability": "High"}
        ],
        "key_quote": "When we spend time together in person, it fosters more engaging and productive discussion and debate",
        "verification_status": "Verified",
        "research_date": "2025-11-18",
        "notes": "Increased from 3 to 4 days",
        "innovation": {"culture_rank": 7, "process_rank": 2, "product_rank": 47, "overall_rank": 12},
        "logo_url": "https://logo.clearbit.com/intel.com",
        "headquarters": "Santa Clara, California, USA",
        "industry_sector": "Semiconductors",
        "employee_count": 131000,
        "enrichment_source": "BuildRemote.co, Wikipedia",
        "enrichment_date": "2025"
    },
    {
        "company": "Johnson & Johnson",
        "rank": 13,
        "sector": "Health Care",
        "fortune_500_rank": "36",
        "work_policy": {
            "type": "Hybrid (~3 days)",
            "category": "Hybrid",
            "days_required": 3,
            "specific_days": "N/A",
            "details": "Approximately 3 days per week based on employee reports. Limited public policy announcements available.",
            "effective_date": "N/A",
            "trend_direction": "Unknown",
            "previous_policy": "",
            "previous_date": ""
        },
        "sources": [
            {"url": "https://www.glassdoor.com/jnj", "type": "Employee Reports", "reliability": "Medium"}
        ],
        "key_quote": "Limited public policy announcements",
        "verification_status": "Partial",
        "research_date": "2025-11-18",
        "notes": "Requires additional research - limited public data",
        "innovation": {"culture_rank": 12, "process_rank": 8, "product_rank": 72, "overall_rank": 13},
        "logo_url": "https://logo.clearbit.com/jnj.com",
        "headquarters": "New Brunswick, New Jersey, USA",
        "industry_sector": "Pharmaceuticals and Medical Technology",
        "employee_count": 138000,
        "enrichment_source": "Employee Reports, Wikipedia",
        "enrichment_date": "2025"
    },
    {
        "company": "Dell Technologies",
        "rank": 14,
        "sector": "Technology",
        "fortune_500_rank": "31",
        "work_policy": {
            "type": "5-day full office",
            "category": "Full Office",
            "days_required": 5,
            "specific_days": "Monday-Friday",
            "details": "All hybrid/remote employees within 1 hour of office required 5 days/week. CEO Michael Dell: 'nothing is faster than the speed of human interaction'. 6th RTO mandate.",
            "effective_date": "2025-03-03",
            "trend_direction": "Tightening",
            "previous_policy": "3-day hybrid",
            "previous_date": "2023-05"
        },
        "sources": [
            {"url": "https://buildremote.co/return-to-office/dell/", "type": "Tracker", "reliability": "High"}
        ],
        "key_quote": "Nothing is faster than the speed of human interaction",
        "verification_status": "Verified",
        "research_date": "2025-11-18",
        "notes": "6th RTO mandate - most aggressive in tech",
        "innovation": {"culture_rank": 9, "process_rank": 13, "product_rank": 58, "overall_rank": 14},
        "logo_url": "https://logo.clearbit.com/dell.com",
        "headquarters": "Round Rock, Texas, USA",
        "industry_sector": "Computer Hardware",
        "employee_count": 108000,
        "enrichment_source": "BuildRemote.co, Wikipedia",
        "enrichment_date": "2025"
    },
    {
        "company": "3M",
        "rank": 15,
        "sector": "Industrials",
        "fortune_500_rank": "102",
        "work_policy": {
            "type": "4-day office-majority hybrid",
            "category": "Hybrid",
            "days_required": 4,
            "specific_days": "N/A",
            "details": "All non-production U.S. employees required 4 days/week. Previous 'Work Your Way' flexible policy (since 2021) ended. 'Our ability to engage, collaborate and innovate is stronger in person.'",
            "effective_date": "2025-09-01",
            "trend_direction": "Tightening",
            "previous_policy": "Work Your Way (flexible)",
            "previous_date": "2021-2024"
        },
        "sources": [
            {"url": "https://buildremote.co/return-to-office/3m/", "type": "Tracker", "reliability": "High"}
        ],
        "key_quote": "Our ability to engage, collaborate and innovate is stronger in person",
        "verification_status": "Verified",
        "research_date": "2025-11-18",
        "notes": "Ended popular 'Work Your Way' program",
        "innovation": {"culture_rank": 18, "process_rank": 5, "product_rank": 69, "overall_rank": 15},
        "logo_url": "https://logo.clearbit.com/3m.com",
        "headquarters": "Maplewood, Minnesota, USA",
        "industry_sector": "Industrial Goods and Machinery",
        "employee_count": 93000,
        "enrichment_source": "BuildRemote.co, Wikipedia",
        "enrichment_date": "2025"
    }
]

def add_missing_companies(dataset_file: str, output_file: str) -> int:
    """Add missing companies to the enriched dataset."""

    # Load existing dataset
    with open(dataset_file, 'r', encoding='utf-8') as f:
        companies = json.load(f)

    print("=" * 70)
    print("ADDING MISSING HIGH-PRIORITY COMPANIES")
    print("=" * 70)
    print(f"\nExisting companies: {len(companies)}")
    print(f"Companies to add: {len(MISSING_COMPANIES)}")

    # Get existing company names for deduplication
    existing_names = {c['company'] for c in companies}

    added = 0
    for new_company in MISSING_COMPANIES:
        if new_company['company'] not in existing_names:
            companies.append(new_company)
            added += 1
            print(f"  ✓ Added: {new_company['company']} (rank {new_company['rank']})")
        else:
            print(f"  - Skipped (exists): {new_company['company']}")

    # Sort by innovation overall rank
    companies.sort(key=lambda x: x.get('innovation', {}).get('overall_rank', 999))

    # Save updated dataset
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)

    file_size = Path(output_file).stat().st_size / 1024

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    print(f"Companies added: {added}")
    print(f"Total companies: {len(companies)}")
    print(f"File size: {file_size:.1f} KB")
    print(f"{'=' * 70}")

    return added

if __name__ == "__main__":
    dataset_file = Path(__file__).parent.parent / "data" / "forbes500_rto_data_top100_enriched.json"
    output_file = dataset_file  # Overwrite

    added = add_missing_companies(str(dataset_file), str(output_file))

    print(f"\n✅ Successfully added {added} high-priority companies!")
