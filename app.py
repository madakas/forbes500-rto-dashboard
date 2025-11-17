"""
Forbes 500 Return-to-Office Dashboard
Interactive dashboard for tracking RTO policies across Fortune 500 companies
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Forbes 500 RTO Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_data():
    """Load the merged Forbes 500 RTO data"""
    data_path = Path(__file__).parent / "data" / "forbes500_rto_data.json"

    with open(data_path, 'r', encoding='utf-8') as f:
        companies = json.load(f)

    # Convert to DataFrame for easier manipulation
    rows = []
    for company in companies:
        wp = company.get('work_policy', {})
        row = {
            'company': company.get('company', 'Unknown'),
            'rank': company.get('rank', 999),
            'sector': company.get('sector', 'Unknown'),
            'fortune_500_rank': company.get('fortune_500_rank', 'N/A'),
            'policy_type': wp.get('type', 'Unknown'),
            'category': wp.get('category', 'Unknown'),
            'days_required': wp.get('days_required', 0),
            'specific_days': wp.get('specific_days', 'N/A'),
            'details': wp.get('details', ''),
            'effective_date': wp.get('effective_date', 'N/A'),
            'trend_direction': wp.get('trend_direction', 'Unknown'),
            'verification_status': company.get('verification_status', 'Unknown'),
            'key_quote': company.get('key_quote', ''),
            'research_date': company.get('research_date', 'N/A'),
            'sources': company.get('sources', []),
            'notes': company.get('notes', '')
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    # Clean up "Unknown" companies
    df = df[df['company'] != 'Unknown']

    return df, companies

# Load data
df, raw_data = load_data()

# Title
st.title("🏢 Forbes 500 Return-to-Office Dashboard")
st.markdown("Interactive tracker of RTO policies across America's most innovative companies")

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Search by company name
search_query = st.sidebar.text_input("Search Company", "")

# Sector filter
all_sectors = sorted(df['sector'].unique())
selected_sectors = st.sidebar.multiselect(
    "Sectors",
    options=all_sectors,
    default=[]
)

# Category filter
all_categories = sorted([cat for cat in df['category'].unique() if cat != 'Unknown'])
selected_categories = st.sidebar.multiselect(
    "Policy Category",
    options=all_categories,
    default=[]
)

# Days required slider
days_range = st.sidebar.slider(
    "Days in Office Required",
    min_value=0,
    max_value=5,
    value=(0, 5)
)

# Trend direction filter
all_trends = sorted(df['trend_direction'].unique())
selected_trends = st.sidebar.multiselect(
    "Trend Direction",
    options=all_trends,
    default=[]
)

# Verification status filter
verification_filter = st.sidebar.multiselect(
    "Verification Status",
    options=df['verification_status'].unique(),
    default=[]
)

# Apply filters
filtered_df = df.copy()

if search_query:
    filtered_df = filtered_df[
        filtered_df['company'].str.contains(search_query, case=False, na=False)
    ]

if selected_sectors:
    filtered_df = filtered_df[filtered_df['sector'].isin(selected_sectors)]

if selected_categories:
    filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]

filtered_df = filtered_df[
    (filtered_df['days_required'] >= days_range[0]) &
    (filtered_df['days_required'] <= days_range[1])
]

if selected_trends:
    filtered_df = filtered_df[filtered_df['trend_direction'].isin(selected_trends)]

if verification_filter:
    filtered_df = filtered_df[filtered_df['verification_status'].isin(verification_filter)]

# Main content
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Companies", len(filtered_df))

with col2:
    avg_days = filtered_df['days_required'].mean()
    st.metric("Avg Days in Office", f"{avg_days:.1f}")

with col3:
    tightening = len(filtered_df[filtered_df['trend_direction'] == 'Tightening'])
    st.metric("Tightening Policies", tightening)

with col4:
    verified = len(filtered_df[filtered_df['verification_status'] == 'Verified'])
    st.metric("Verified Policies", verified)

st.divider()

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "🏢 Company Explorer",
    "📈 Trends",
    "📋 Data Quality"
])

with tab1:
    st.header("Policy Distribution")

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        # Category distribution pie chart
        category_counts = filtered_df['category'].value_counts()
        fig_pie = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title="Distribution by Policy Category",
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_chart2:
        # Days required distribution
        days_counts = filtered_df['days_required'].value_counts().sort_index()
        fig_bar = px.bar(
            x=days_counts.index,
            y=days_counts.values,
            labels={'x': 'Days Required in Office', 'y': 'Number of Companies'},
            title="Distribution by Days Required in Office"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Sector breakdown
    st.subheader("Policy Categories by Sector")
    sector_category = pd.crosstab(filtered_df['sector'], filtered_df['category'])

    fig_heatmap = px.imshow(
        sector_category,
        labels=dict(x="Policy Category", y="Sector", color="Count"),
        aspect="auto",
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

with tab2:
    st.header("Company Explorer")

    # Display options
    show_details = st.checkbox("Show full details", value=False)

    # Sort options
    sort_by = st.selectbox(
        "Sort by",
        options=['company', 'rank', 'days_required', 'sector'],
        index=0
    )

    sorted_df = filtered_df.sort_values(by=sort_by)

    # Display companies
    for idx, row in sorted_df.iterrows():
        with st.expander(f"**{row['company']}** - {row['category']} ({row['days_required']} days)"):
            col_info1, col_info2, col_info3 = st.columns(3)

            with col_info1:
                st.write(f"**Sector:** {row['sector']}")
                st.write(f"**Rank:** {row['rank']}")
                st.write(f"**Fortune 500:** #{row['fortune_500_rank']}")

            with col_info2:
                st.write(f"**Policy Type:** {row['policy_type']}")
                st.write(f"**Days Required:** {row['days_required']}")
                st.write(f"**Specific Days:** {row['specific_days']}")

            with col_info3:
                st.write(f"**Trend:** {row['trend_direction']}")
                st.write(f"**Effective Date:** {row['effective_date']}")
                st.write(f"**Verified:** {row['verification_status']}")

            if show_details:
                st.divider()
                st.write("**Policy Details:**")
                st.write(row['details'])

                if row['key_quote']:
                    st.info(f"💬 *\"{row['key_quote']}\"*")

                if row['notes']:
                    st.write("**Notes:**")
                    st.write(row['notes'])

                if row['sources']:
                    st.write("**Sources:**")
                    for source in row['sources']:
                        reliability = source.get('reliability', 'Unknown')
                        source_type = source.get('type', 'Unknown')
                        url = source.get('url', '#')
                        st.write(f"- [{source_type} - {reliability}]({url})")

with tab3:
    st.header("Trend Analysis")

    # Trend direction breakdown
    trend_counts = filtered_df['trend_direction'].value_counts()

    col_trend1, col_trend2 = st.columns(2)

    with col_trend1:
        fig_trend = px.bar(
            x=trend_counts.index,
            y=trend_counts.values,
            labels={'x': 'Trend Direction', 'y': 'Number of Companies'},
            title="Policy Trend Direction",
            color=trend_counts.index,
            color_discrete_map={
                'Tightening': '#ff6b6b',
                'Maintaining': '#ffd93d',
                'Relaxing': '#6bcf7f'
            }
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_trend2:
        # Trend by sector
        sector_trend = pd.crosstab(filtered_df['sector'], filtered_df['trend_direction'])
        fig_sector_trend = px.bar(
            sector_trend,
            title="Trends by Sector",
            barmode='stack'
        )
        st.plotly_chart(fig_sector_trend, use_container_width=True)

with tab4:
    st.header("Data Quality Dashboard")

    col_qual1, col_qual2 = st.columns(2)

    with col_qual1:
        # Verification status
        verification_counts = df['verification_status'].value_counts()
        fig_verify = px.pie(
            values=verification_counts.values,
            names=verification_counts.index,
            title="Verification Status Distribution"
        )
        st.plotly_chart(fig_verify, use_container_width=True)

    with col_qual2:
        # Research date distribution
        st.subheader("Research Timeline")
        date_counts = df['research_date'].value_counts().sort_index()
        fig_dates = px.bar(
            x=date_counts.index,
            y=date_counts.values,
            labels={'x': 'Research Date', 'y': 'Companies Researched'},
            title="Companies Researched by Date"
        )
        st.plotly_chart(fig_dates, use_container_width=True)

    # Companies needing verification
    st.subheader("Companies Needing Verification")
    unverified = df[df['verification_status'] != 'Verified']
    st.dataframe(
        unverified[['company', 'sector', 'verification_status', 'research_date']],
        use_container_width=True
    )

# Footer
st.divider()
st.caption(f"📊 Data last updated: {df['research_date'].max()} | Total companies: {len(df)}")
st.caption("🔬 Research methodology: Multi-source verification with official, media, and employee sources")
