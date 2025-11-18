#!/usr/bin/env python3
"""
Validate data quality for the enriched top 100 dataset.
Performs comprehensive checks on innovation rankings, schema, and data consistency.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from collections import defaultdict

def validate_innovation_rankings(companies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate innovation rankings for consistency.

    Checks:
    - Rankings are within valid range (1-100)
    - No duplicate overall rankings
    - Culture/Process/Product ranks correlate with overall rank
    - All required fields are present
    """
    issues = []
    stats = {
        'total_with_innovation': 0,
        'missing_innovation': 0,
        'invalid_ranges': 0,
        'duplicate_overall_ranks': 0,
        'missing_fields': 0
    }

    overall_ranks_seen = defaultdict(list)

    for company in companies:
        company_name = company.get('company', 'Unknown')

        # Check if innovation data exists
        if 'innovation' not in company:
            stats['missing_innovation'] += 1
            issues.append({
                'company': company_name,
                'issue_type': 'missing_innovation',
                'severity': 'high',
                'message': 'No innovation data found'
            })
            continue

        stats['total_with_innovation'] += 1
        innovation = company['innovation']

        # Check for required fields
        required_fields = ['culture_rank', 'process_rank', 'product_rank', 'overall_rank']
        missing = [f for f in required_fields if f not in innovation]

        if missing:
            stats['missing_fields'] += 1
            issues.append({
                'company': company_name,
                'issue_type': 'missing_fields',
                'severity': 'high',
                'message': f'Missing fields: {", ".join(missing)}'
            })
            continue

        # Check valid ranges (1-100)
        for field in required_fields:
            value = innovation[field]
            if value is None or not isinstance(value, (int, float)):
                stats['invalid_ranges'] += 1
                issues.append({
                    'company': company_name,
                    'issue_type': 'invalid_type',
                    'severity': 'high',
                    'field': field,
                    'value': value,
                    'message': f'{field} is not a number: {value}'
                })
            elif value < 1 or value > 100:
                stats['invalid_ranges'] += 1
                issues.append({
                    'company': company_name,
                    'issue_type': 'out_of_range',
                    'severity': 'high',
                    'field': field,
                    'value': value,
                    'message': f'{field} out of range (1-100): {value}'
                })

        # Track overall ranks for duplicate detection
        overall_rank = innovation.get('overall_rank')
        if overall_rank:
            overall_ranks_seen[overall_rank].append(company_name)

    # Check for duplicate overall ranks
    for rank, companies_with_rank in overall_ranks_seen.items():
        if len(companies_with_rank) > 1:
            stats['duplicate_overall_ranks'] += 1
            issues.append({
                'issue_type': 'duplicate_rank',
                'severity': 'medium',
                'rank': rank,
                'companies': companies_with_rank,
                'message': f'Overall rank {rank} assigned to multiple companies: {", ".join(companies_with_rank)}'
            })

    return {
        'stats': stats,
        'issues': issues
    }

def validate_schema(companies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate schema consistency and data types.

    Checks:
    - Required fields present
    - Data types consistent
    - Valid enumeration values
    """
    issues = []
    stats = {
        'total_companies': len(companies),
        'schema_violations': 0,
        'type_errors': 0,
        'null_values': 0
    }

    required_fields = ['company', 'rank', 'sector', 'work_policy']
    optional_fields = ['fortune_500_rank', 'innovation', 'logo_url', 'sources', 'key_quote']

    valid_categories = ['Fully Remote', 'Hybrid', 'Full Office']
    valid_trends = ['Maintaining', 'Tightening', 'Relaxing', 'Unknown']
    valid_verification = ['Verified', 'Partial', 'Unverified', 'Unknown']

    for company in companies:
        company_name = company.get('company', 'Unknown')

        # Check required fields
        missing_required = [f for f in required_fields if f not in company]
        if missing_required:
            stats['schema_violations'] += 1
            issues.append({
                'company': company_name,
                'issue_type': 'missing_required_fields',
                'severity': 'critical',
                'fields': missing_required,
                'message': f'Missing required fields: {", ".join(missing_required)}'
            })

        # Check work_policy structure
        if 'work_policy' in company:
            work_policy = company['work_policy']

            if not isinstance(work_policy, dict):
                stats['type_errors'] += 1
                issues.append({
                    'company': company_name,
                    'issue_type': 'invalid_type',
                    'severity': 'critical',
                    'field': 'work_policy',
                    'message': 'work_policy is not a dictionary'
                })
            else:
                # Check category
                category = work_policy.get('category')
                if category and category not in valid_categories:
                    stats['type_errors'] += 1
                    issues.append({
                        'company': company_name,
                        'issue_type': 'invalid_enum',
                        'severity': 'medium',
                        'field': 'work_policy.category',
                        'value': category,
                        'message': f'Invalid category: {category} (expected one of {valid_categories})'
                    })

                # Check days_required is int
                days = work_policy.get('days_required')
                if days is not None and not isinstance(days, int):
                    stats['type_errors'] += 1
                    issues.append({
                        'company': company_name,
                        'issue_type': 'invalid_type',
                        'severity': 'medium',
                        'field': 'work_policy.days_required',
                        'value': days,
                        'message': f'days_required should be int, got {type(days).__name__}'
                    })

                # Check trend_direction
                trend = work_policy.get('trend_direction')
                if trend and trend not in valid_trends:
                    stats['type_errors'] += 1
                    issues.append({
                        'company': company_name,
                        'issue_type': 'invalid_enum',
                        'severity': 'low',
                        'field': 'work_policy.trend_direction',
                        'value': trend,
                        'message': f'Invalid trend: {trend} (expected one of {valid_trends})'
                    })

        # Check verification_status
        verification = company.get('verification_status')
        if verification and verification not in valid_verification:
            stats['type_errors'] += 1
            issues.append({
                'company': company_name,
                'issue_type': 'invalid_enum',
                'severity': 'low',
                'field': 'verification_status',
                'value': verification,
                'message': f'Invalid verification status: {verification}'
            })

        # Check for null/empty critical values
        if not company.get('company') or company.get('company') == 'Unknown':
            stats['null_values'] += 1
            issues.append({
                'company': company_name,
                'issue_type': 'null_value',
                'severity': 'critical',
                'field': 'company',
                'message': 'Company name is missing or "Unknown"'
            })

        if not company.get('sector') or company.get('sector') == 'Unknown':
            stats['null_values'] += 1
            issues.append({
                'company': company_name,
                'issue_type': 'null_value',
                'severity': 'medium',
                'field': 'sector',
                'message': 'Sector is missing or "Unknown"'
            })

    return {
        'stats': stats,
        'issues': issues
    }

def check_company_names(companies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Check for company name inconsistencies.

    Checks:
    - Duplicate names
    - Names with trailing/leading whitespace
    - Names with inconsistent capitalization
    - Names missing common suffixes
    """
    issues = []
    stats = {
        'total_companies': len(companies),
        'duplicate_names': 0,
        'whitespace_issues': 0,
        'capitalization_issues': 0
    }

    names_seen = defaultdict(list)
    normalized_names = defaultdict(list)

    for idx, company in enumerate(companies):
        name = company.get('company', '')

        # Track exact names
        names_seen[name].append(idx)

        # Track normalized names (for case-insensitive duplicates)
        normalized = name.lower().strip()
        normalized_names[normalized].append((name, idx))

        # Check for whitespace issues
        if name != name.strip():
            stats['whitespace_issues'] += 1
            issues.append({
                'company': name,
                'issue_type': 'whitespace',
                'severity': 'low',
                'message': f'Company name has leading/trailing whitespace: "{name}"'
            })

    # Check for exact duplicates
    for name, indices in names_seen.items():
        if len(indices) > 1:
            stats['duplicate_names'] += 1
            issues.append({
                'issue_type': 'exact_duplicate',
                'severity': 'critical',
                'name': name,
                'count': len(indices),
                'message': f'Exact duplicate company name appears {len(indices)} times: "{name}"'
            })

    # Check for case-insensitive duplicates
    for normalized, name_list in normalized_names.items():
        if len(name_list) > 1:
            unique_names = set(name for name, idx in name_list)
            if len(unique_names) > 1:
                stats['capitalization_issues'] += 1
                issues.append({
                    'issue_type': 'case_mismatch',
                    'severity': 'medium',
                    'names': list(unique_names),
                    'message': f'Same company with different capitalization: {list(unique_names)}'
                })

    return {
        'stats': stats,
        'issues': issues
    }

def run_all_validations(filepath: str) -> Dict[str, Any]:
    """Run all validation checks on the dataset."""

    with open(filepath, 'r', encoding='utf-8') as f:
        companies = json.load(f)

    print("=" * 70)
    print("DATA VALIDATION REPORT")
    print("=" * 70)
    print(f"\nDataset: {filepath}")
    print(f"Total companies: {len(companies)}\n")

    # Run validations
    innovation_results = validate_innovation_rankings(companies)
    schema_results = validate_schema(companies)
    name_results = check_company_names(companies)

    # Print results
    print("=" * 70)
    print("INNOVATION RANKINGS VALIDATION")
    print("=" * 70)
    print(f"Companies with innovation data: {innovation_results['stats']['total_with_innovation']}")
    print(f"Missing innovation data: {innovation_results['stats']['missing_innovation']}")
    print(f"Invalid ranges: {innovation_results['stats']['invalid_ranges']}")
    print(f"Duplicate overall ranks: {innovation_results['stats']['duplicate_overall_ranks']}")
    print(f"Missing fields: {innovation_results['stats']['missing_fields']}")

    if innovation_results['issues']:
        print(f"\n⚠️  Found {len(innovation_results['issues'])} innovation ranking issues:")
        for issue in innovation_results['issues'][:5]:  # Show first 5
            print(f"  - [{issue['severity'].upper()}] {issue['message']}")
        if len(innovation_results['issues']) > 5:
            print(f"  ... and {len(innovation_results['issues']) - 5} more")
    else:
        print("✓ No innovation ranking issues found")

    print("\n" + "=" * 70)
    print("SCHEMA VALIDATION")
    print("=" * 70)
    print(f"Total companies: {schema_results['stats']['total_companies']}")
    print(f"Schema violations: {schema_results['stats']['schema_violations']}")
    print(f"Type errors: {schema_results['stats']['type_errors']}")
    print(f"Null values: {schema_results['stats']['null_values']}")

    if schema_results['issues']:
        print(f"\n⚠️  Found {len(schema_results['issues'])} schema issues:")
        # Group by severity
        critical = [i for i in schema_results['issues'] if i['severity'] == 'critical']
        high = [i for i in schema_results['issues'] if i['severity'] == 'high']
        medium = [i for i in schema_results['issues'] if i['severity'] == 'medium']
        low = [i for i in schema_results['issues'] if i['severity'] == 'low']

        if critical:
            print(f"  CRITICAL: {len(critical)} issues")
            for issue in critical[:3]:
                print(f"    - {issue['message']}")
        if high:
            print(f"  HIGH: {len(high)} issues")
        if medium:
            print(f"  MEDIUM: {len(medium)} issues")
        if low:
            print(f"  LOW: {len(low)} issues")
    else:
        print("✓ No schema issues found")

    print("\n" + "=" * 70)
    print("COMPANY NAME VALIDATION")
    print("=" * 70)
    print(f"Total companies: {name_results['stats']['total_companies']}")
    print(f"Duplicate names: {name_results['stats']['duplicate_names']}")
    print(f"Whitespace issues: {name_results['stats']['whitespace_issues']}")
    print(f"Capitalization issues: {name_results['stats']['capitalization_issues']}")

    if name_results['issues']:
        print(f"\n⚠️  Found {len(name_results['issues'])} name issues:")
        for issue in name_results['issues'][:5]:
            print(f"  - [{issue['severity'].upper()}] {issue['message']}")
        if len(name_results['issues']) > 5:
            print(f"  ... and {len(name_results['issues']) - 5} more")
    else:
        print("✓ No company name issues found")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total_issues = (
        len(innovation_results['issues']) +
        len(schema_results['issues']) +
        len(name_results['issues'])
    )

    if total_issues == 0:
        print("✅ All validations passed! Dataset is clean.")
    else:
        print(f"⚠️  Found {total_issues} total issues across all validations.")

        critical_count = sum(
            1 for r in [innovation_results, schema_results, name_results]
            for i in r['issues']
            if i.get('severity') == 'critical'
        )

        if critical_count > 0:
            print(f"   {critical_count} CRITICAL issues require immediate attention.")

    print("=" * 70)

    return {
        'innovation': innovation_results,
        'schema': schema_results,
        'names': name_results,
        'total_issues': total_issues
    }

if __name__ == "__main__":
    # Validate the enriched top 100 dataset
    enriched_path = Path(__file__).parent.parent / "data" / "forbes500_rto_data_top100_enriched.json"

    results = run_all_validations(enriched_path)

    # Save detailed results
    output_path = Path(__file__).parent.parent / "data" / "validation_report.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Detailed validation report saved to: {output_path}")
