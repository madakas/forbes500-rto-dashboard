#!/usr/bin/env python3
"""
Merge enrichment results (HQ, industry, employees) into the top 100 enriched dataset.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

def load_enrichment_results(results_dir: str) -> Dict[str, Dict[str, Any]]:
    """Load all enrichment batch results."""
    results_path = Path(results_dir)

    if not results_path.exists():
        print(f"Error: {results_dir} does not exist")
        return {}

    all_enrichments = {}
    batch_files = sorted(results_path.glob("batch_*_results.json"))

    print(f"Loading {len(batch_files)} batch result files...")

    for batch_file in batch_files:
        with open(batch_file, 'r', encoding='utf-8') as f:
            batch_data = json.load(f)

        for company_data in batch_data:
            company_name = company_data['company']
            all_enrichments[company_name] = company_data

    print(f"✓ Loaded enrichment data for {len(all_enrichments)} companies\n")
    return all_enrichments

def merge_enrichment_data(dataset_file: str, enrichments: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge enrichment data into the main dataset."""

    with open(dataset_file, 'r', encoding='utf-8') as f:
        companies = json.load(f)

    print("=" * 70)
    print("MERGING ENRICHMENT DATA")
    print("=" * 70)
    print(f"\nDataset companies: {len(companies)}")
    print(f"Enrichment records: {len(enrichments)}")

    stats = {
        'matched': 0,
        'not_found': 0,
        'enriched': []
    }

    for company in companies:
        company_name = company['company']

        if company_name in enrichments:
            enrichment = enrichments[company_name]

            # Add enrichment fields
            company['headquarters'] = enrichment['headquarters']
            company['industry_sector'] = enrichment['industry_sector']
            company['employee_count'] = enrichment['employee_count']
            company['enrichment_source'] = enrichment['data_source']
            company['enrichment_date'] = enrichment['last_updated']

            stats['matched'] += 1
            stats['enriched'].append(company_name)
        else:
            stats['not_found'] += 1
            print(f"  ⚠️  No enrichment data for: {company_name}")

    print(f"\n{'=' * 70}")
    print("MERGE STATISTICS")
    print(f"{'=' * 70}")
    print(f"Successfully enriched: {stats['matched']}")
    print(f"Not found: {stats['not_found']}")
    print(f"Enrichment rate: {(stats['matched'] / len(companies)) * 100:.1f}%")
    print(f"{'=' * 70}\n")

    return companies

def validate_enrichment(companies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate enrichment data quality."""

    print("=" * 70)
    print("ENRICHMENT VALIDATION")
    print("=" * 70)

    required_fields = ['headquarters', 'industry_sector', 'employee_count']

    issues = []
    for company in companies:
        company_name = company['company']

        # Check for required fields
        for field in required_fields:
            if field not in company:
                issues.append(f"{company_name}: Missing {field}")
            elif not company[field]:
                issues.append(f"{company_name}: Empty {field}")

        # Validate employee_count is numeric
        if 'employee_count' in company:
            try:
                count = int(company['employee_count'])
                if count <= 0:
                    issues.append(f"{company_name}: Invalid employee_count {count}")
            except (ValueError, TypeError):
                issues.append(f"{company_name}: employee_count not numeric")

    if issues:
        print(f"⚠️  Found {len(issues)} validation issues:\n")
        for issue in issues[:10]:
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")
    else:
        print("✅ All enrichment data validated successfully!")

    print(f"{'=' * 70}\n")

    return {'total_issues': len(issues), 'issues': issues}

def print_sample_enriched_data(companies: List[Dict[str, Any]]):
    """Print sample of enriched company data."""

    print("=" * 70)
    print("SAMPLE ENRICHED DATA")
    print("=" * 70)

    for company in companies[:3]:
        print(f"\nCompany: {company['company']}")
        print(f"  Innovation Rank: {company.get('innovation', {}).get('overall_rank', 'N/A')}")
        print(f"  Headquarters: {company.get('headquarters', 'N/A')}")
        print(f"  Industry: {company.get('industry_sector', 'N/A')}")
        print(f"  Employees: {company.get('employee_count', 'N/A'):,}")
        print(f"  RTO Policy: {company.get('work_policy', {}).get('category', 'N/A')} ({company.get('work_policy', {}).get('days_required', 0)} days)")

    print(f"{'=' * 70}\n")

if __name__ == "__main__":
    # Paths
    results_dir = Path(__file__).parent.parent / "enrichment_results"
    dataset_file = Path(__file__).parent.parent / "data" / "forbes500_rto_data_top100_enriched.json"
    output_file = Path(__file__).parent.parent / "data" / "forbes500_rto_data_top100_enriched.json"

    # Load enrichment results
    enrichments = load_enrichment_results(str(results_dir))

    if not enrichments:
        print("No enrichment data found. Exiting.")
        exit(1)

    # Merge data
    enriched_companies = merge_enrichment_data(str(dataset_file), enrichments)

    # Validate
    validation_results = validate_enrichment(enriched_companies)

    # Print sample
    print_sample_enriched_data(enriched_companies)

    # Save enriched dataset
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enriched_companies, f, indent=2, ensure_ascii=False)

    file_size = output_file.stat().st_size / 1024

    print(f"✓ Saved enriched dataset to: {output_file}")
    print(f"  File size: {file_size:.1f} KB")
    print(f"  Companies: {len(enriched_companies)}")
    print(f"\n✅ Enrichment merge complete!")
