#!/usr/bin/env python3
"""
Merge ChatGPT innovation ranking data with our RTO dataset.
Adds culture/process/product rankings and logo URLs.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from difflib import SequenceMatcher

def fuzzy_match(name1: str, name2: str) -> float:
    """Calculate similarity ratio between two company names."""
    return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()

def normalize_company_name(name: str) -> str:
    """Normalize company name for matching."""
    # Remove common suffixes
    suffixes = [' Inc.', ' Inc', ' Corporation', ' Corp.', ' Corp', ' Company',
                ' Co.', ' Co', ' LLC', ' L.L.C.', ' Holdings', ' Group', ' Ltd.',
                ' Limited', ' Holding', ' Incorporated']

    normalized = name
    for suffix in suffixes:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)]

    return normalized.strip()

def find_best_match(chatgpt_name: str, our_companies: Dict[str, Any], threshold: float = 0.8) -> Optional[str]:
    """Find best matching company name from our dataset."""
    best_match = None
    best_score = 0.0

    chatgpt_normalized = normalize_company_name(chatgpt_name)

    for our_name in our_companies.keys():
        our_normalized = normalize_company_name(our_name)

        # Try exact match first
        if chatgpt_normalized.lower() == our_normalized.lower():
            return our_name

        # Try fuzzy match
        score = fuzzy_match(chatgpt_normalized, our_normalized)
        if score > best_score:
            best_score = score
            best_match = our_name

    return best_match if best_score >= threshold else None

def merge_datasets():
    """Merge ChatGPT innovation data with our RTO dataset."""

    # Load both datasets
    chatgpt_path = Path(__file__).parent.parent / "data" / "chatgpt_top100_raw.json"
    our_path = Path(__file__).parent.parent / "data" / "forbes500_rto_data_top100.json"

    with open(chatgpt_path, 'r') as f:
        chatgpt_data = json.load(f)

    with open(our_path, 'r') as f:
        our_data = json.load(f)

    # Create lookup dictionary for our data
    our_companies = {c['company']: c for c in our_data}

    print("="*70)
    print("MERGING CHATGPT INNOVATION DATA WITH RTO DATASET")
    print("="*70)
    print(f"\nChatGPT dataset: {len(chatgpt_data)} companies")
    print(f"Our dataset: {len(our_data)} companies")

    # Statistics
    stats = {
        'exact_matches': 0,
        'fuzzy_matches': 0,
        'no_match': 0,
        'enriched': 0
    }

    unmatched = []

    # Merge data
    for chatgpt_company in chatgpt_data:
        chatgpt_name = chatgpt_company['Name']

        # Try to find matching company in our dataset
        matched_name = None

        # First try exact match
        if chatgpt_name in our_companies:
            matched_name = chatgpt_name
            stats['exact_matches'] += 1
        else:
            # Try fuzzy matching
            matched_name = find_best_match(chatgpt_name, our_companies)
            if matched_name:
                stats['fuzzy_matches'] += 1
                print(f"  Fuzzy match: '{chatgpt_name}' → '{matched_name}'")

        if matched_name:
            # Enrich our data with ChatGPT fields
            our_company = our_companies[matched_name]

            # Add innovation rankings
            our_company['innovation'] = {
                'culture_rank': chatgpt_company['Culture rank'],
                'process_rank': chatgpt_company['Process rank'],
                'product_rank': chatgpt_company['Product rank'],
                'overall_rank': chatgpt_company['Rank']
            }

            # Add logo URL
            our_company['logo_url'] = chatgpt_company['logo_url']

            # Update Fortune 500 rank if we don't have it
            if chatgpt_company['Fortune 500 rank'] is not None:
                if not our_company.get('fortune_500_rank') or our_company.get('fortune_500_rank') == 'N/A':
                    our_company['fortune_500_rank'] = chatgpt_company['Fortune 500 rank']

            stats['enriched'] += 1
        else:
            stats['no_match'] += 1
            unmatched.append({
                'rank': chatgpt_company['Rank'],
                'name': chatgpt_name,
                'culture_rank': chatgpt_company['Culture rank'],
                'process_rank': chatgpt_company['Process rank'],
                'product_rank': chatgpt_company['Product rank']
            })

    print(f"\n{'='*70}")
    print("MERGE STATISTICS:")
    print(f"{'='*70}")
    print(f"  Exact matches: {stats['exact_matches']}")
    print(f"  Fuzzy matches: {stats['fuzzy_matches']}")
    print(f"  Total enriched: {stats['enriched']}")
    print(f"  No match found: {stats['no_match']}")
    print(f"{'='*70}")

    # Save enriched dataset
    output_path = Path(__file__).parent.parent / "data" / "forbes500_rto_data_top100_enriched.json"

    # Sort by innovation overall rank
    enriched_companies = []
    for company in our_data:
        if 'innovation' in company:
            enriched_companies.append(company)

    # Add companies that were enriched
    enriched_companies.sort(key=lambda x: x['innovation']['overall_rank'])

    with open(output_path, 'w') as f:
        json.dump(enriched_companies, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved enriched dataset to: {output_path}")
    print(f"  Companies: {len(enriched_companies)}")
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")

    # Save unmatched companies for research
    if unmatched:
        unmatched_path = Path(__file__).parent.parent / "data" / "companies_to_research.json"
        unmatched.sort(key=lambda x: x['rank'])

        with open(unmatched_path, 'w') as f:
            json.dump(unmatched, f, indent=2, ensure_ascii=False)

        print(f"\n⚠️  Saved {len(unmatched)} unmatched companies to: {unmatched_path}")
        print(f"\nTop 10 missing companies:")
        for company in unmatched[:10]:
            print(f"  Rank {company['rank']:3d}: {company['name']}")

    # Print sample enriched data
    if enriched_companies:
        print(f"\n{'='*70}")
        print("SAMPLE ENRICHED DATA:")
        print(f"{'='*70}")
        sample = enriched_companies[0]
        print(f"\nCompany: {sample['company']}")
        print(f"Innovation Overall Rank: {sample['innovation']['overall_rank']}")
        print(f"  Culture Rank: {sample['innovation']['culture_rank']}")
        print(f"  Process Rank: {sample['innovation']['process_rank']}")
        print(f"  Product Rank: {sample['innovation']['product_rank']}")
        print(f"Logo URL: {sample['logo_url']}")
        print(f"RTO Policy: {sample['work_policy']['category']} ({sample['work_policy']['days_required']} days)")
        print(f"{'='*70}")

    return enriched_companies, unmatched

if __name__ == "__main__":
    enriched, unmatched = merge_datasets()
    print(f"\n✅ Merge complete! {len(enriched)} companies enriched with innovation data.")
