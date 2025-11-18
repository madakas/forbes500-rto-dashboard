#!/usr/bin/env python3
"""
Generate research batches for companies with data quality issues
"""

import json
from pathlib import Path

def generate_cleanup_batches():
    """Generate batches of companies needing research"""
    data_path = Path(__file__).parent.parent / "data" / "forbes500_rto_data.json"

    with open(data_path, 'r') as f:
        data = json.load(f)

    # Find companies with issues
    priority_research = []

    for company in data:
        wp = company.get('work_policy', {})
        policy_type = wp.get('type', '').lower()
        verification = company.get('verification_status', '')
        trend = wp.get('trend_direction', '')

        name = company.get('company')
        rank = company.get('rank')
        sector = company.get('sector')

        issue_count = 0
        issues = []

        if 'unknown' in policy_type or not policy_type:
            issue_count += 1
            issues.append('NoPolicy')

        if verification in ['Unknown', 'Unverified']:
            issue_count += 1
            issues.append('NotVerified')

        if trend in ['Unknown', '']:
            issue_count += 1
            issues.append('NoTrend')

        # Priority: companies with 2+ issues
        if issue_count >= 2:
            priority_research.append({
                'rank': rank,
                'company': name,
                'sector': sector,
                'issues': issues,
                'issue_count': issue_count
            })

    # Sort by rank
    priority_research.sort(key=lambda x: x['rank'])

    # Create batches of 5
    batches = []
    batch_size = 5

    for i in range(0, len(priority_research), batch_size):
        batch = priority_research[i:i+batch_size]
        batches.append({
            'batch_number': len(batches) + 1,
            'companies': batch
        })

    print(f"Generated {len(batches)} research batches for {len(priority_research)} companies\n")

    # Save batches
    output_dir = Path(__file__).parent.parent / "cleanup_batches"
    output_dir.mkdir(exist_ok=True)

    for batch_info in batches:
        batch_num = batch_info['batch_number']
        batch_file = output_dir / f"cleanup_batch_{batch_num:02d}.json"

        with open(batch_file, 'w') as f:
            json.dump(batch_info, f, indent=2)

        print(f"Batch {batch_num:2d}: {', '.join([c['company'] for c in batch_info['companies']])}")

    print(f"\n✓ Saved {len(batches)} batch files to {output_dir}")
    return len(batches)

if __name__ == "__main__":
    num_batches = generate_cleanup_batches()
    print(f"\nReady to launch {num_batches} research agents")
