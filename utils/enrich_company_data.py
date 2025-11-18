#!/usr/bin/env python3
"""
Enrich company data with HQ address, industry sector, and employee count.
Creates batches for research agents to process.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

def create_enrichment_batches(input_file: str, batch_size: int = 5) -> List[Dict[str, Any]]:
    """
    Create batches of companies that need enrichment.

    Args:
        input_file: Path to enriched dataset
        batch_size: Number of companies per batch

    Returns:
        List of batch dictionaries
    """

    with open(input_file, 'r', encoding='utf-8') as f:
        companies = json.load(f)

    print("=" * 70)
    print("CREATING COMPANY ENRICHMENT BATCHES")
    print("=" * 70)
    print(f"\nTotal companies to enrich: {len(companies)}")
    print(f"Batch size: {batch_size}")
    print(f"Total batches: {(len(companies) + batch_size - 1) // batch_size}\n")

    batches = []
    for i in range(0, len(companies), batch_size):
        batch_companies = companies[i:i + batch_size]

        batch = {
            "batch_number": (i // batch_size) + 1,
            "companies": [
                {
                    "company": c['company'],
                    "sector": c.get('sector', 'Unknown'),
                    "innovation_rank": c.get('innovation', {}).get('overall_rank', 'N/A'),
                    "data_needed": {
                        "headquarters": "City, State/Country format",
                        "industry_sector": "Specific industry classification",
                        "employee_count": "Approximate number of employees (latest available)"
                    }
                }
                for c in batch_companies
            ]
        }

        batches.append(batch)

    return batches

def save_enrichment_batches(batches: List[Dict[str, Any]], output_dir: str):
    """Save enrichment batches to JSON files."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print("Saving batches...")
    for batch in batches:
        batch_num = batch['batch_number']
        filename = output_path / f"enrichment_batch_{batch_num}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(batch, f, indent=2, ensure_ascii=False)

        print(f"  ✓ Saved batch {batch_num}: {len(batch['companies'])} companies → {filename.name}")

    print(f"\n✅ Created {len(batches)} enrichment batches in {output_dir}")

if __name__ == "__main__":
    enriched_file = Path(__file__).parent.parent / "data" / "forbes500_rto_data_top100_enriched.json"
    output_directory = Path(__file__).parent.parent / "enrichment_batches"

    # Create batches
    batches = create_enrichment_batches(str(enriched_file), batch_size=5)

    # Save batches
    save_enrichment_batches(batches, str(output_directory))

    print("\nNext steps:")
    print("1. Launch Task agents to research each batch")
    print("2. Agents will find HQ address, industry sector, and employee count")
    print("3. Merge results back into enriched dataset")
