#!/usr/bin/env python3
"""
Quick validation of merged Forbes 500 RTO data
"""

import json
from pathlib import Path
from collections import Counter

def validate_data():
    # Load data
    data_path = Path(__file__).parent / "data" / "forbes500_rto_data.json"

    with open(data_path, 'r', encoding='utf-8') as f:
        companies = json.load(f)

    print("="*60)
    print("FORBES 500 RTO DATA VALIDATION")
    print("="*60)
    print()

    # Basic counts
    print(f"✓ Total companies: {len(companies)}")
    print()

    # Schema validation
    required_fields = ['company', 'rank', 'sector', 'work_policy']
    valid_count = 0

    for company in companies:
        if all(field in company for field in required_fields):
            valid_count += 1

    print(f"✓ Companies with valid schema: {valid_count}/{len(companies)} ({valid_count/len(companies)*100:.1f}%)")
    print()

    # Category distribution
    categories = Counter()
    days_dist = Counter()
    trends = Counter()
    verification = Counter()

    for company in companies:
        wp = company.get('work_policy', {})
        categories[wp.get('category', 'Unknown')] += 1

        # Handle days_required
        days = wp.get('days_required', 0)
        try:
            days = int(days) if days is not None else 0
        except (ValueError, TypeError):
            days = 0
        days_dist[days] += 1

        trends[wp.get('trend_direction', 'Unknown')] += 1
        verification[company.get('verification_status', 'Unknown')] += 1

    # Print distributions
    print("POLICY CATEGORIES:")
    for cat, count in categories.most_common():
        pct = (count / len(companies)) * 100
        print(f"  {cat:25s}: {count:3d} ({pct:5.1f}%)")

    print()
    print("DAYS IN OFFICE:")
    for days in sorted(days_dist.keys()):
        count = days_dist[days]
        pct = (count / len(companies)) * 100
        print(f"  {days} days: {count:3d} ({pct:5.1f}%)")

    print()
    print("TREND DIRECTIONS:")
    for trend, count in trends.most_common():
        pct = (count / len(companies)) * 100
        print(f"  {trend:20s}: {count:3d} ({pct:5.1f}%)")

    print()
    print("VERIFICATION STATUS:")
    for status, count in verification.most_common():
        pct = (count / len(companies)) * 100
        print(f"  {status:20s}: {count:3d} ({pct:5.1f}%)")

    print()
    print("="*60)
    print("KEY INSIGHTS:")
    print("="*60)

    # Calculate key metrics
    total_days = sum(days * count for days, count in days_dist.items())
    avg_days = total_days / len(companies)

    office_first = categories.get('Office-First', 0)
    hybrid_majority = categories.get('Hybrid-Majority', 0)
    hybrid_flexible = categories.get('Hybrid-Flexible', 0)
    remote_first = categories.get('Remote-First', 0)

    tightening = trends.get('Tightening', 0)
    maintaining = trends.get('Maintaining', 0)

    verified = verification.get('Verified', 0)

    print(f"Average days in office: {avg_days:.1f} days/week")
    print(f"Office-First companies: {office_first} ({office_first/len(companies)*100:.1f}%)")
    print(f"Hybrid companies: {hybrid_majority + hybrid_flexible} ({(hybrid_majority + hybrid_flexible)/len(companies)*100:.1f}%)")
    print(f"Remote-First companies: {remote_first} ({remote_first/len(companies)*100:.1f}%)")
    print()
    print(f"Tightening policies: {tightening} ({tightening/len(companies)*100:.1f}%)")
    print(f"Maintaining policies: {maintaining} ({maintaining/len(companies)*100:.1f}%)")
    print()
    print(f"Verified data: {verified} ({verified/len(companies)*100:.1f}%)")
    print()
    print("="*60)
    print("✅ DATA VALIDATION COMPLETE")
    print("="*60)

if __name__ == "__main__":
    validate_data()
