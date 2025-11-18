# America's Top 100 Innovators - Work Policy Research Platform

An academic research project examining return-to-office policies across America's most innovative companies.

**Author**: Maximilian Daub
**Course**: Critical Analytical Thinking (Stanford LEAD)
**Professor**: Haim Mendelson

## Overview

This platform provides research-based insights into work policies at America's top 100 most innovative companies, as ranked by Fortune. The data includes:

- **Policy Type**: Remote, Hybrid, or Full Office requirements
- **Days Required**: Number of days per week in office
- **Trend Direction**: Whether policies are tightening, stable, or relaxing
- **Innovation Rankings**: Culture, Process, and Product innovation scores
- **Company Metadata**: Headquarters, employee count, industry sector

## Features

- **Interactive Filters**: Search by company, sector, policy type, or trend
- **Company Profiles**: Detailed view with logos, key quotes, and source citations
- **Analytics Dashboard**: Visualizations showing policy patterns across sectors
- **Academic Attribution**: Full methodology and limitations disclosure

## Data

Currently tracking **62 companies** with verified work policies and enriched metadata including:
- Company logos (via Clearbit)
- Headquarters locations
- Employee counts
- Innovation rankings (Culture, Process, Product)
- Executive quotes on work policy rationale
- Source citations with reliability ratings

## Running Locally

```bash
# Clone the repository
git clone https://github.com/madakas/forbes500-rto-dashboard.git
cd forbes500-rto-dashboard

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Deployment

Deployed on [Streamlit Community Cloud](https://streamlit.io/cloud).

## Methodology

Companies were selected based on the 2024 Fortune Most Innovative Companies list. Work policy data was collected through:

1. **Official Sources**: Company career pages, press releases, SEC filings
2. **Media Reports**: Verified news articles from major publications
3. **Employee Sources**: Glassdoor, Blind, and verified employee reviews

Each entry includes source attribution and reliability ratings (High, Medium, Low).

## Limitations

- Policies change frequently; some information may be outdated
- Remote work eligibility varies by role within companies
- Employee sentiment and actual enforcement may differ from official policy
- Data represents a snapshot as of November 2025

## Project Structure

```
forbes500-rto-dashboard/
├── app.py                                    # Main Streamlit application
├── data/
│   └── forbes500_rto_data_top100_enriched.json  # Research data
├── requirements.txt                          # Python dependencies
└── README.md
```

## License

This research is presented for educational purposes as part of Stanford LEAD coursework. It does not constitute endorsement or criticism of any company's work policies.

## Contact

**Maximilian Daub**
Stanford LEAD Program
[LinkedIn](https://www.linkedin.com/in/maximilian-daub/)

---

*Stanford LEAD | Critical Analytical Thinking | November 2025*
