#!/usr/bin/env python3
"""
Merge all research batch JSON files into a single consolidated dataset.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any

def load_json_file(filepath: Path) -> List[Dict[str, Any]]:
    """Load a JSON file and return its contents."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Ensure data is a list
            if isinstance(data, list):
                return data
            else:
                print(f"Warning: {filepath} does not contain a list, wrapping in list")
                return [data]
    except json.JSONDecodeError as e:
        print(f"Error decoding {filepath}: {e}")
        return []
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return []

def merge_research_data(source_dir: str) -> List[Dict[str, Any]]:
    """
    Merge all research batch files from the source directory.

    Args:
        source_dir: Path to the forbes500 research directory

    Returns:
        List of all company records
    """
    source_path = Path(source_dir)
    all_companies = []
    company_names_seen = set()

    # Pattern for pilot batch files
    pilot_batches = sorted(source_path.glob("pilot_results_batch*.json"))

    # Pattern for research_results batch files
    research_batches = sorted((source_path / "research_results").glob("batch_*.json"))

    all_batch_files = pilot_batches + research_batches

    print(f"Found {len(all_batch_files)} batch files to merge\n")

    for batch_file in all_batch_files:
        print(f"Processing: {batch_file.name}")
        companies = load_json_file(batch_file)

        # Add to consolidated list, checking for duplicates
        for company in companies:
            company_name = company.get('company', 'Unknown')

            if company_name in company_names_seen:
                print(f"  ⚠️  Duplicate found: {company_name} (skipping)")
                continue

            company_names_seen.add(company_name)
            all_companies.append(company)

        print(f"  ✓ Added {len(companies)} companies")

    print(f"\n{'='*60}")
    print(f"Total unique companies: {len(all_companies)}")
    print(f"{'='*60}\n")

    # Sort by rank if available (handle both string and int types)
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

    print(f"✓ Saved merged data to: {output_file}")
    print(f"  File size: {output_file.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    # Path to the original research directory
    source_directory = "/Users/maximiliandaub/Code/forbes500"

    # Output path in the new dashboard repo
    output_path = Path(__file__).parent.parent / "data" / "forbes500_rto_data.json"

    print("Forbes 500 RTO Data Merger")
    print("="*60)

    # Merge all data
    merged_companies = merge_research_data(source_directory)

    # Save to output file
    save_merged_data(merged_companies, output_path)

    # Print some statistics
    print("\nData Statistics:")
    print("-"*60)

    # Count by policy category
    categories = {}
    for company in merged_companies:
        category = company.get('work_policy', {}).get('category', 'Unknown')
        categories[category] = categories.get(category, 0) + 1

    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count}")

    print("-"*60)
