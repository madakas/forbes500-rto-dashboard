#!/usr/bin/env python3
"""
Merge all research batch JSON files into a single consolidated dataset.
Handles both old and new JSON formats.
"""

import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

def extract_days_from_text(text: str) -> int:
    """Extract number of days from text like '3 days in office' or '4-day hybrid'."""
    if not text:
        return 0

    # Try to find patterns like "3 days", "4-day", "5 day"
    patterns = [
        r'(\d+)\s*days?',
        r'(\d+)-day',
        r'(\d+)\s*day',
    ]

    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return int(match.group(1))

    # Check for specific keywords
    if 'fully remote' in text.lower() or 'remote-first' in text.lower():
        return 0
    if 'full-time' in text.lower() and 'office' in text.lower():
        return 5

    return 0

def map_to_category(policy_type: str, days_required: int, details: str) -> str:
    """
    Categorize work policy into simplified categories.

    Categories:
    - Fully Remote: 0 days required, remote-first policies
    - Hybrid: 1-4 days in office, flexible arrangements
    - Full Office: 5 days required in office
    """
    policy_lower = policy_type.lower() if policy_type else ""
    details_lower = details.lower() if details else ""

    # Full Office (5 days)
    if days_required >= 5:
        return "Full Office"

    if any(keyword in policy_lower for keyword in ['5-day office', 'full-time office', 'five days']):
        return "Full Office"

    # Fully Remote (0 days or remote-first)
    if any(keyword in policy_lower for keyword in ['remote-first', 'fully remote', 'permanent remote', 'remote only']):
        return "Fully Remote"

    if days_required == 0 and any(keyword in policy_lower for keyword in ['remote', 'work from anywhere', 'distributed']):
        return "Fully Remote"

    # Hybrid (1-4 days or any hybrid/flexible arrangement)
    if days_required in [1, 2, 3, 4]:
        return "Hybrid"

    if any(keyword in policy_lower for keyword in ['hybrid', 'flexible', 'days in office', 'days per week']):
        return "Hybrid"

    # Role-dependent - categorize as Hybrid since it varies
    if any(keyword in policy_lower + details_lower for keyword in ['role-dependent', 'varies by role', 'position-dependent']):
        return "Hybrid"

    # Healthcare-specific - categorize as Hybrid
    if 'clinical' in details_lower and 'administrative' in details_lower:
        return "Hybrid"

    # Default based on days if we have that info
    if days_required == 0:
        return "Fully Remote"
    elif days_required > 0:
        return "Hybrid"

    # Unknown/unverified - default to Hybrid as most common middle ground
    return "Hybrid"

def normalize_old_format(company: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize old format (batches 1-25) to unified schema."""
    work_policy = company.get('work_policy', {})

    # Extract days and policy type for re-categorization
    policy_type = work_policy.get('type', 'Unknown')
    days_required = work_policy.get('days_required', 0)
    details = work_policy.get('details', '')

    # Ensure days_required is int
    try:
        days_required = int(days_required) if days_required is not None else 0
    except (ValueError, TypeError):
        days_required = extract_days_from_text(str(days_required))

    # Re-categorize using simplified categories
    category = map_to_category(policy_type, days_required, details)

    return {
        'company': company.get('company', 'Unknown'),
        'rank': company.get('rank', 999),
        'sector': company.get('sector', 'Unknown'),
        'fortune_500_rank': company.get('fortune_500_rank', 'N/A'),
        'work_policy': {
            'type': policy_type,
            'category': category,
            'days_required': days_required,
            'specific_days': work_policy.get('specific_days', 'N/A'),
            'details': details,
            'effective_date': work_policy.get('effective_date', 'N/A'),
            'trend_direction': work_policy.get('trend_direction', 'Unknown'),
            'previous_policy': work_policy.get('previous_policy', ''),
            'previous_date': work_policy.get('previous_date', '')
        },
        'sources': company.get('sources', []),
        'key_quote': company.get('key_quote', ''),
        'verification_status': company.get('verification_status', 'Unknown'),
        'research_date': company.get('research_date', 'N/A'),
        'notes': company.get('notes', '')
    }

def normalize_new_format(company: Dict[str, Any], batch_date: str = "2025-11-17") -> Dict[str, Any]:
    """Normalize new format (batches 26-56) to unified schema."""

    # Extract basic info
    company_name = company.get('company_name', company.get('company', 'Unknown'))

    # Get policy details
    policy_details = company.get('policy_details', {})
    current_policy = company.get('current_policy', '')

    # Extract policy type
    policy_type = (
        policy_details.get('model_type') or
        policy_details.get('policy_type') or
        current_policy or
        'Unknown'
    )

    # Extract days required
    days_required = (
        policy_details.get('in_office_days') or
        policy_details.get('office_requirements') or
        extract_days_from_text(policy_type) or
        extract_days_from_text(current_policy) or
        0
    )

    # Ensure days_required is int
    try:
        days_required = int(days_required)
    except (ValueError, TypeError):
        days_required = extract_days_from_text(str(days_required))

    # Get details
    office_req = policy_details.get('office_requirements', '')
    flexibility = policy_details.get('flexibility', '')
    details = f"{office_req} {flexibility}".strip() or current_policy

    # Map confidence to verification status
    confidence = company.get('confidence_level', 'Medium')
    if confidence in ['Very High', 'High']:
        verification_status = 'Verified'
    elif confidence == 'Medium':
        verification_status = 'Partial'
    else:
        verification_status = 'Unverified'

    # Get trend direction
    trend = company.get('trend_direction', 'Unknown')
    if trend in ['Stable', 'stable', 'Maintaining']:
        trend_direction = 'Maintaining'
    elif trend in ['Tightening', 'More restrictive', 'Increasing']:
        trend_direction = 'Tightening'
    elif trend in ['Relaxing', 'More flexible']:
        trend_direction = 'Relaxing'
    else:
        trend_direction = 'Unknown'

    # Auto-categorize
    category = map_to_category(policy_type, days_required, details)

    # Build unified structure
    return {
        'company': company_name,
        'rank': company.get('rank', 999),
        'sector': company.get('sector', 'Unknown'),
        'fortune_500_rank': company.get('fortune_500_rank', 'N/A'),
        'work_policy': {
            'type': policy_type,
            'category': category,
            'days_required': days_required,
            'specific_days': policy_details.get('typical_schedule', 'N/A'),
            'details': details,
            'effective_date': policy_details.get('enforcement_date', 'N/A'),
            'trend_direction': trend_direction,
            'previous_policy': '',
            'previous_date': ''
        },
        'sources': company.get('sources', []),
        'key_quote': company.get('key_findings', company.get('key_quote', '')),
        'verification_status': verification_status,
        'research_date': batch_date,
        'notes': company.get('notes', company.get('additional_notes', ''))
    }

def load_json_file(filepath: Path):
    """
    Load a JSON file and return its contents with batch date.
    Returns: (list of companies, batch_date)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle new format (object with batch_number and companies array)
        if isinstance(data, dict) and 'companies' in data:
            companies = data['companies']
            batch_date = data.get('research_date', '2025-11-17')
            return companies, batch_date

        # Handle old format (direct array)
        elif isinstance(data, list):
            return data, '2025-11-17'

        # Handle unexpected single object
        else:
            print(f"Warning: {filepath.name} has unexpected format, wrapping in list")
            return [data], '2025-11-17'

    except json.JSONDecodeError as e:
        print(f"Error decoding {filepath}: {e}")
        return [], '2025-11-17'
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return [], '2025-11-17'

def is_old_format(company: Dict[str, Any]) -> bool:
    """Detect if company data is in old format."""
    # Old format has 'company' field and 'work_policy' dict
    if 'company' in company and isinstance(company.get('work_policy'), dict):
        return True
    # New format has 'company_name' or 'policy_details'
    if 'company_name' in company or 'policy_details' in company:
        return False
    # Default to old format if unclear
    return True

def merge_research_data(source_dir: str) -> List[Dict[str, Any]]:
    """
    Merge all research batch files from the source directory.
    Handles both old and new JSON formats.

    Args:
        source_dir: Path to the forbes500 research directory

    Returns:
        List of all company records in unified format
    """
    source_path = Path(source_dir)
    all_companies = []
    company_names_seen = set()

    # Pattern for pilot batch files (old format)
    pilot_batches = sorted(source_path.glob("pilot_results_batch*.json"))

    # Pattern for research_results batch files (mixed formats)
    research_batches = sorted((source_path / "research_results").glob("batch_*_results.json"))

    # Exclude batch_plan.json
    research_batches = [f for f in research_batches if 'plan' not in f.name]

    all_batch_files = pilot_batches + research_batches

    print(f"Found {len(all_batch_files)} batch files to merge")
    print(f"  Pilot batches: {len(pilot_batches)}")
    print(f"  Research batches: {len(research_batches)}\n")

    stats = {
        'old_format': 0,
        'new_format': 0,
        'duplicates': 0,
        'unknown_skipped': 0
    }

    for batch_file in all_batch_files:
        print(f"Processing: {batch_file.name}")
        companies, batch_date = load_json_file(batch_file)

        batch_count = 0
        for company in companies:
            # Skip Unknown companies
            company_name = company.get('company', company.get('company_name', 'Unknown'))

            if company_name == 'Unknown' or not company_name:
                stats['unknown_skipped'] += 1
                continue

            # Check for duplicates
            if company_name in company_names_seen:
                print(f"  ⚠️  Duplicate: {company_name} (skipping)")
                stats['duplicates'] += 1
                continue

            # Normalize based on format
            if is_old_format(company):
                normalized = normalize_old_format(company)
                stats['old_format'] += 1
            else:
                normalized = normalize_new_format(company, batch_date)
                stats['new_format'] += 1

            company_names_seen.add(company_name)
            all_companies.append(normalized)
            batch_count += 1

        print(f"  ✓ Added {batch_count} companies")

    print(f"\n{'='*60}")
    print(f"Merge Statistics:")
    print(f"  Total unique companies: {len(all_companies)}")
    print(f"  Old format processed: {stats['old_format']}")
    print(f"  New format processed: {stats['new_format']}")
    print(f"  Duplicates skipped: {stats['duplicates']}")
    print(f"  Unknown/empty skipped: {stats['unknown_skipped']}")
    print(f"{'='*60}\n")

    # Sort by rank
    def get_sort_key(company):
        rank = company.get('rank', 999)
        try:
            return int(rank)
        except (ValueError, TypeError):
            return 999

    all_companies.sort(key=get_sort_key)

    return all_companies

def save_merged_data(companies: List[Dict[str, Any]], output_path: str):
    """Save the merged data to a JSON file."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)

    file_size = output_file.stat().st_size / 1024
    print(f"✓ Saved merged data to: {output_file}")
    print(f"  File size: {file_size:.1f} KB")
    print(f"  Companies: {len(companies)}")

def print_statistics(companies: List[Dict[str, Any]]):
    """Print detailed statistics about the merged data."""
    print("\nData Statistics:")
    print("-"*60)

    # Count by policy category
    categories = {}
    for company in companies:
        category = company.get('work_policy', {}).get('category', 'Unknown')
        categories[category] = categories.get(category, 0) + 1

    print("\nPolicy Categories:")
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(companies)) * 100
        print(f"  {category:20s}: {count:3d} ({pct:5.1f}%)")

    # Count by days required
    days_dist = {}
    for company in companies:
        days = company.get('work_policy', {}).get('days_required', 0)
        # Ensure days is int
        try:
            days = int(days) if days is not None else 0
        except (ValueError, TypeError):
            days = 0
        days_dist[days] = days_dist.get(days, 0) + 1

    print("\nDays in Office Distribution:")
    for days in sorted(days_dist.keys()):
        count = days_dist[days]
        pct = (count / len(companies)) * 100
        print(f"  {days} days: {count:3d} ({pct:5.1f}%)")

    # Count by trend direction
    trends = {}
    for company in companies:
        trend = company.get('work_policy', {}).get('trend_direction', 'Unknown')
        trends[trend] = trends.get(trend, 0) + 1

    print("\nTrend Directions:")
    for trend, count in sorted(trends.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(companies)) * 100
        print(f"  {trend:20s}: {count:3d} ({pct:5.1f}%)")

    # Count by verification status
    verification = {}
    for company in companies:
        status = company.get('verification_status', 'Unknown')
        verification[status] = verification.get(status, 0) + 1

    print("\nVerification Status:")
    for status, count in sorted(verification.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(companies)) * 100
        print(f"  {status:20s}: {count:3d} ({pct:5.1f}%)")

    print("-"*60)

if __name__ == "__main__":
    # Path to the original research directory
    source_directory = "/Users/maximiliandaub/Code/forbes500"

    # Output path in the dashboard repo
    output_path = Path(__file__).parent.parent / "data" / "forbes500_rto_data.json"

    print("Forbes 500 RTO Data Merger")
    print("="*60)
    print("Handles both old and new JSON formats")
    print("="*60)
    print()

    # Merge all data
    merged_companies = merge_research_data(source_directory)

    # Save to output file
    save_merged_data(merged_companies, output_path)

    # Print detailed statistics
    print_statistics(merged_companies)
