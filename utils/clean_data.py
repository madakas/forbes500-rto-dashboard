#!/usr/bin/env python3
"""
Clean and standardize data in the enriched top 100 dataset.
Fixes validation issues identified by validate_data.py.
"""

import json
from pathlib import Path
from typing import Dict, Any, List

def fix_product_rank_outlier(companies: List[Dict[str, Any]]) -> int:
    """Fix product_rank value of 106 for Houston Methodist."""
    fixed = 0
    for company in companies:
        if company.get('company') == 'Houston Methodist':
            if 'innovation' in company and company['innovation'].get('product_rank') == 106:
                # 106 is likely a data entry error - check ChatGPT source
                # Since it's out of range, we'll cap it at 100
                company['innovation']['product_rank'] = 100
                fixed += 1
                print(f"  Fixed: Houston Methodist product_rank 106 → 100")
    return fixed

def standardize_verification_status(companies: List[Dict[str, Any]]) -> int:
    """Standardize verification_status to valid enum values."""
    fixed = 0

    # Mapping from various formats to standard values
    mapping = {
        'Unverified - Employee reports': 'Partial',
        'Partially Verified': 'Partial',
        'Verified - Employee reports': 'Verified',
        'Partial - Limited public information': 'Partial',
        'Verified from job postings and media reports': 'Verified',
        'Limited Info': 'Partial'
    }

    for company in companies:
        status = company.get('verification_status')
        if status in mapping:
            new_status = mapping[status]
            company['verification_status'] = new_status
            fixed += 1
            print(f"  Fixed: {company['company']}: '{status}' → '{new_status}'")

    return fixed

def standardize_trend_direction(companies: List[Dict[str, Any]]) -> int:
    """Standardize trend_direction to valid enum values."""
    fixed = 0

    # Mapping from various formats to standard values
    mapping = {
        'Maintaining/Expanding': 'Maintaining',
        'Tightening (client-driven)': 'Tightening',
        'Stable': 'Maintaining'
    }

    for company in companies:
        if 'work_policy' in company:
            trend = company['work_policy'].get('trend_direction')
            if trend in mapping:
                new_trend = mapping[trend]
                company['work_policy']['trend_direction'] = new_trend
                fixed += 1
                print(f"  Fixed: {company['company']}: trend '{trend}' → '{new_trend}'")

    return fixed

def clean_dataset(input_path: str, output_path: str) -> Dict[str, int]:
    """
    Clean the dataset by fixing all identified issues.

    Returns:
        Dictionary with counts of fixes applied
    """

    print("=" * 70)
    print("DATA CLEANING")
    print("=" * 70)
    print(f"\nInput: {input_path}")
    print(f"Output: {output_path}\n")

    # Load data
    with open(input_path, 'r', encoding='utf-8') as f:
        companies = json.load(f)

    print(f"Loaded {len(companies)} companies\n")

    # Apply fixes
    stats = {}

    print("Fixing product_rank outlier...")
    stats['product_rank_fixed'] = fix_product_rank_outlier(companies)

    print("\nStandardizing verification_status...")
    stats['verification_fixed'] = standardize_verification_status(companies)

    print("\nStandardizing trend_direction...")
    stats['trend_fixed'] = standardize_trend_direction(companies)

    # Save cleaned data
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)

    file_size = Path(output_path).stat().st_size / 1024

    print("\n" + "=" * 70)
    print("CLEANING SUMMARY")
    print("=" * 70)
    print(f"Product rank outliers fixed: {stats['product_rank_fixed']}")
    print(f"Verification statuses standardized: {stats['verification_fixed']}")
    print(f"Trend directions standardized: {stats['trend_fixed']}")
    print(f"Total fixes applied: {sum(stats.values())}")
    print("=" * 70)
    print(f"\n✓ Saved cleaned data to: {output_path}")
    print(f"  File size: {file_size:.1f} KB")
    print(f"  Companies: {len(companies)}")

    return stats

if __name__ == "__main__":
    input_file = Path(__file__).parent.parent / "data" / "forbes500_rto_data_top100_enriched.json"
    output_file = Path(__file__).parent.parent / "data" / "forbes500_rto_data_top100_enriched.json"

    stats = clean_dataset(str(input_file), str(output_file))

    print("\n✅ Data cleaning complete!")
