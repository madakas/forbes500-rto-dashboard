# Forbes 500 Return-to-Office Dashboard

Interactive dashboard tracking Return-to-Office (RTO) policies across America's most innovative companies.

## Features

- **🔍 Search & Filter**: Find companies by name, sector, policy type, and more
- **📊 Interactive Visualizations**: Charts and graphs showing policy distributions
- **🏢 Company Explorer**: Detailed view of each company's RTO policy
- **📈 Trend Analysis**: Track how policies are changing over time
- **✅ Data Quality**: Verification status and source tracking

## Data Overview

Currently tracking **116 companies** with verified RTO policies including:
- Policy type and category
- Days required in office
- Trend direction (Tightening, Maintaining, Relaxing)
- Official sources and key quotes
- Implementation dates

## Running Locally

1. Clone the repository:
```bash
git clone https://github.com/madakas/forbes500-rto-dashboard.git
cd forbes500-rto-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Deployment

This app is designed to deploy seamlessly to [Streamlit Community Cloud](https://streamlit.io/cloud):

1. Push this repo to GitHub
2. Sign in to Streamlit Community Cloud
3. Deploy from your GitHub repository
4. App goes live at `https://[your-app-name].streamlit.app`

## Project Structure

```
forbes500-rto-dashboard/
├── app.py                      # Main Streamlit application
├── data/
│   └── forbes500_rto_data.json # Consolidated research data
├── utils/
│   └── merge_data.py           # Script to merge research batches
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Data Schema

Each company record includes:
- Company name and rank
- Sector and Fortune 500 ranking
- Work policy details (type, category, days required)
- Trend direction and effective dates
- Verification status and sources
- Key quotes and notes

## Research Methodology

Data collected through multi-source verification:
- **Official sources**: Company announcements, career pages, policy documents
- **Media sources**: News articles, industry reports
- **Employee sources**: Reviews, forums, verified accounts

Each entry includes source reliability ratings and verification status.

## Contributing

This is a research project tracking publicly available information about corporate RTO policies. Data is regularly updated as policies change.

## License

Data for research and informational purposes.

---

**Last Updated**: November 2025
**Companies Tracked**: 116
**Data Source**: Multi-source verification
