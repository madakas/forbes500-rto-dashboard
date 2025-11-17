#!/usr/bin/env python3
"""
Fix missing ranks by matching companies back to original Forbes CSV
"""

import json
import csv
from pathlib import Path

def load_forbes_ranks():
    """Load company names and ranks from original CSV"""
    forbes_path = Path("/Users/maximiliandaub/Code/forbes500/americas_most_innovative_companies_2025_full.csv")

    ranks = {}
    sectors = {}

    with open(forbes_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            company = row['Company'].strip()
            ranks[company] = int(row['Rank'])
            sectors[company] = row['Sector'].strip()

    return ranks, sectors

def fix_data():
    """Fix ranks and sectors in the dataset"""
    data_path = Path(__file__).parent.parent / "data" / "forbes500_rto_data.json"

    # Load Forbes ranks
    forbes_ranks, forbes_sectors = load_forbes_ranks()

    # Load current data
    with open(data_path, 'r') as f:
        companies = json.load(f)

    print(f"Loaded {len(companies)} companies from dataset")
    print(f"Loaded {len(forbes_ranks)} companies from Forbes CSV\n")

    fixed_count = 0
    removed_count = 0
    not_found = []

    fixed_companies = []

    for company in companies:
        company_name = company.get('company')
        current_rank = company.get('rank')

        # Try to match with Forbes list
        if company_name in forbes_ranks:
            # Fix rank and sector
            company['rank'] = forbes_ranks[company_name]
            company['sector'] = forbes_sectors[company_name]
            fixed_companies.append(company)

            if current_rank == 999:
                fixed_count += 1
                print(f"✓ Fixed: {company_name} → Rank {forbes_ranks[company_name]}, Sector {forbes_sectors[company_name]}")
        else:
            # Not on Forbes list - should be removed
            not_found.append(company_name)
            removed_count += 1
            print(f"✗ Removing: {company_name} (not on Forbes list)")

    print(f"\n{'='*60}")
    print(f"Fixed {fixed_count} companies with missing ranks")
    print(f"Removed {removed_count} companies not on Forbes list")
    print(f"Final dataset: {len(fixed_companies)} companies")
    print(f"{'='*60}\n")

    if not_found:
        print("Companies NOT on Forbes list (removed):")
        for name in sorted(not_found):
            print(f"  - {name}")
        print()

    # Save fixed data
    with open(data_path, 'w') as f:
        json.dump(fixed_companies, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved fixed data to {data_path}")

    # Verify
    sectors_unknown = [c for c in fixed_companies if c.get('sector') == 'Unknown']
    rank_999 = [c for c in fixed_companies if c.get('rank') == 999]

    print(f"\nVerification:")
    print(f"  Companies with 'Unknown' sector: {len(sectors_unknown)}")
    print(f"  Companies with rank 999: {len(rank_999)}")

    if sectors_unknown:
        print(f"\n  Still have Unknown sectors:")
        for c in sectors_unknown[:5]:
            print(f"    - {c.get('company')}")

if __name__ == "__main__":
    fix_data()
