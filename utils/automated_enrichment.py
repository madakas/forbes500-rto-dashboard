#!/usr/bin/env python3
"""
Automated company data enrichment using parallel Task agents.
Enriches companies with HQ address, industry sector, and employee count.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

# Template for Task agent research prompt
RESEARCH_PROMPT_TEMPLATE = """Research the following information for {company_name}:

1. **Headquarters address**: Full city, state/country location (e.g., "Mountain View, California, USA")
2. **Industry sector**: Specific industry classification (e.g., "Technology - Internet Services", "Healthcare - Pharmaceutical", "Financial Services - Banking")
3. **Employee count**: Latest available total employee count (approximate is fine, include year if available)

Use web search to find this information from reliable sources like:
- Company's official website
- Wikipedia
- Fortune 500 / Forbes listings
- Recent news articles
- LinkedIn company pages

IMPORTANT: Return ONLY the JSON data in this exact format, with no additional text:

```json
{{
  "company": "{company_name}",
  "headquarters": "City, State/Country",
  "industry_sector": "Primary Industry - Specific Sector",
  "employee_count": 000000,
  "data_source": "Source name",
  "last_updated": "2025"
}}
```

Just return the JSON, nothing else."""

def load_companies(filepath: str) -> List[Dict[str, Any]]:
    """Load companies from enriched dataset."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_batch_plan(companies: List[Dict[str, Any]], batch_size: int = 5) -> List[List[str]]:
    """Create batches of company names for parallel processing."""
    company_names = [c['company'] for c in companies]

    batches = []
    for i in range(0, len(company_names), batch_size):
        batches.append(company_names[i:i + batch_size])

    return batches

def generate_research_prompts(batch: List[str]) -> List[str]:
    """Generate research prompts for a batch of companies."""
    return [RESEARCH_PROMPT_TEMPLATE.format(company_name=name) for name in batch]

def save_batch_instructions(batches: List[List[str]], output_dir: str):
    """Save batch instructions for manual agent launching."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    plan = {
        "total_companies": sum(len(batch) for batch in batches),
        "total_batches": len(batches),
        "batch_size": len(batches[0]) if batches else 0,
        "batches": []
    }

    for batch_num, batch in enumerate(batches, 1):
        batch_info = {
            "batch_number": batch_num,
            "companies": batch,
            "company_count": len(batch)
        }
        plan["batches"].append(batch_info)

    plan_file = output_path / "enrichment_plan.json"
    with open(plan_file, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved enrichment plan to: {plan_file}")
    return plan

def print_enrichment_summary(plan: Dict[str, Any]):
    """Print summary of enrichment plan."""
    print("\n" + "=" * 70)
    print("COMPANY DATA ENRICHMENT PLAN")
    print("=" * 70)
    print(f"\nTotal companies to enrich: {plan['total_companies']}")
    print(f"Batch size: {plan['batch_size']}")
    print(f"Total batches: {plan['total_batches']}")
    print("\nBatch breakdown:")
    for batch in plan['batches'][:5]:
        print(f"  Batch {batch['batch_number']}: {batch['company_count']} companies - {', '.join(batch['companies'][:3])}...")
    if len(plan['batches']) > 5:
        print(f"  ... and {len(plan['batches']) - 5} more batches")
    print("=" * 70)

if __name__ == "__main__":
    # Paths
    enriched_file = Path(__file__).parent.parent / "data" / "forbes500_rto_data_top100_enriched.json"
    output_dir = Path(__file__).parent.parent / "enrichment_plan"

    # Load companies
    companies = load_companies(str(enriched_file))

    # Create batch plan
    batches = create_batch_plan(companies, batch_size=5)

    # Save plan
    plan = save_batch_instructions(batches, str(output_dir))

    # Print summary
    print_enrichment_summary(plan)

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("Launch Task agents in parallel to research companies.")
    print("Each agent will return JSON data for its batch.")
    print("Results will be saved to enrichment_results/ directory.")
    print("=" * 70)
