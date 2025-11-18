"""
America's Top 100 Innovators - Work Policy Research Platform

Author: Maximilian Daub
Course: Critical Analytical Thinking (Stanford LEAD)
Professor: Haim Mendelson

An academic research project examining return-to-office policies
across America's most innovative companies.
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import anthropic
from utils.chatbot import CompanySearchEngine, format_company_context, create_system_prompt, generate_response_prompt

# Page config
st.set_page_config(
    page_title="America's Top 100 Innovators",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for academic, neutral design
st.markdown("""
<style>
    /* Main theme colors - neutral academic palette */
    :root {
        --primary: #475569;
        --accent: #6366F1;
        --bg-light: #F8FAFC;
        --bg-medium: #F1F5F9;
        --text-primary: #1E293B;
        --text-secondary: #64748B;
    }

    /* Header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }

    .sub-header {
        font-size: 1.1rem;
        color: var(--text-secondary);
        margin-bottom: 2rem;
    }

    /* Company card styling */
    .company-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border: 1px solid #E2E8F0;
    }

    /* Quote styling */
    .quote-box {
        background: var(--bg-light);
        border-left: 4px solid var(--accent);
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        font-style: italic;
        color: var(--text-secondary);
        border-radius: 0 8px 8px 0;
    }

    /* Policy badge styling - neutral colors */
    .policy-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
    }

    .badge-remote { background: #DBEAFE; color: #1E40AF; }
    .badge-hybrid { background: #EDE9FE; color: #5B21B6; }
    .badge-office { background: #FEF3C7; color: #92400E; }

    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #E2E8F0;
    }

    /* Academic footer */
    .academic-footer {
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid #E2E8F0;
        font-size: 0.875rem;
        color: var(--text-secondary);
    }

    /* Logo image styling */
    .company-logo {
        border-radius: 8px;
        background: white;
        padding: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    """Load the enriched Forbes Top 100 Innovators data"""
    data_path = Path(__file__).parent / "data" / "forbes500_rto_data_top100_enriched.json"

    with open(data_path, 'r', encoding='utf-8') as f:
        companies = json.load(f)

    # Convert to DataFrame
    rows = []
    for company in companies:
        wp = company.get('work_policy', {})
        innovation = company.get('innovation', {})

        # Safely convert days_required to int
        days_required = wp.get('days_required', 0)
        try:
            days_required = int(days_required) if days_required is not None else 0
        except (ValueError, TypeError):
            days_required = 0

        # Safely convert employee_count
        employee_count = company.get('employee_count', 0)
        try:
            employee_count = int(employee_count) if employee_count else 0
        except (ValueError, TypeError):
            employee_count = 0

        row = {
            'company': company.get('company', 'Unknown'),
            'rank': company.get('rank', 999),
            'sector': company.get('sector', 'Unknown'),
            'fortune_500_rank': company.get('fortune_500_rank', 'N/A'),
            'policy_type': wp.get('type', 'Unknown'),
            'category': wp.get('category', 'Unknown'),
            'days_required': days_required,
            'specific_days': wp.get('specific_days', 'N/A'),
            'details': wp.get('details', ''),
            'effective_date': wp.get('effective_date', 'N/A'),
            'trend_direction': wp.get('trend_direction', 'Unknown'),
            'previous_policy': wp.get('previous_policy', 'N/A'),
            'verification_status': company.get('verification_status', 'Unknown'),
            'key_quote': company.get('key_quote', ''),
            'research_date': company.get('research_date', 'N/A'),
            'sources': company.get('sources', []),
            'notes': company.get('notes', ''),
            # Enriched data
            'logo_url': company.get('logo_url', ''),
            'headquarters': company.get('headquarters', 'Unknown'),
            'industry_sector': company.get('industry_sector', 'Unknown'),
            'employee_count': employee_count,
            'innovation_overall': innovation.get('overall_rank', 0),
            'innovation_culture': innovation.get('culture_rank', 0),
            'innovation_process': innovation.get('process_rank', 0),
            'innovation_product': innovation.get('product_rank', 0),
            # Geolocation
            'latitude': company.get('latitude', 0),
            'longitude': company.get('longitude', 0),
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    df = df[df['company'] != 'Unknown']
    df['days_required'] = df['days_required'].astype(int)

    return df, companies

# Load data
df, raw_data = load_data()

# Header
st.markdown('<p class="main-header">America\'s Top 100 Innovators</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Work Policy Research Platform | Stanford LEAD - Critical Analytical Thinking</p>', unsafe_allow_html=True)

# Sidebar filters
st.sidebar.header("Research Filters")

# Search
search_query = st.sidebar.text_input("Search Company", "", placeholder="Type company name...")

# Sector filter
all_sectors = sorted(df['sector'].unique())
selected_sectors = st.sidebar.multiselect("Sectors", options=all_sectors, default=[])

# Policy category filter
all_categories = sorted(df['category'].unique())
selected_categories = st.sidebar.multiselect("Policy Category", options=all_categories, default=[])

# Days required
days_range = st.sidebar.slider("Days in Office Required", min_value=0, max_value=5, value=(0, 5))

# Trend direction
all_trends = sorted([t for t in df['trend_direction'].unique() if t and t != 'Unknown'])
selected_trends = st.sidebar.multiselect("Policy Trend", options=all_trends, default=[])

# Apply filters
filtered_df = df.copy()

if search_query:
    filtered_df = filtered_df[filtered_df['company'].str.contains(search_query, case=False, na=False)]

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

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ Map",
    "🏢 Company Profiles",
    "🤖 Assistant",
    "📈 Analytics",
    "📚 About"
])

# Tab 1: Map
with tab1:
    st.subheader("Company Headquarters Map")

    # Filter for companies with valid coordinates
    map_df = filtered_df[
        (filtered_df['latitude'] != 0) &
        (filtered_df['longitude'] != 0)
    ].copy()

    if len(map_df) > 0:
        # Add color based on policy category (neutral palette)
        def get_color(category):
            colors = {
                'Hybrid': [196, 181, 253, 200],      # Soft purple
                'Full Office': [252, 211, 77, 200],  # Soft amber
                'Fully Remote': [147, 197, 253, 200], # Soft blue
            }
            return colors.get(category, [226, 232, 240, 200])

        map_df['color'] = map_df['category'].apply(get_color)

        # Create tooltip
        map_df['tooltip'] = map_df.apply(
            lambda row: f"{row['company']}\n{row['policy_type']}\n{row['days_required']} days/week",
            axis=1
        )

        # PyDeck layer
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position=["longitude", "latitude"],
            get_color="color",
            get_radius=50000,  # Radius in meters
            pickable=True,
            opacity=0.8,
            stroked=True,
            filled=True,
            radius_min_pixels=8,
            radius_max_pixels=25,
            line_width_min_pixels=1,
        )

        # Initial view centered on US
        view_state = pdk.ViewState(
            latitude=39.8283,
            longitude=-98.5795,
            zoom=3.5,
            pitch=0,
        )

        # Render map
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "text": "{tooltip}",
                "style": {
                    "backgroundColor": "#1E293B",
                    "color": "white",
                    "fontSize": "12px",
                    "padding": "8px"
                }
            },
            map_style="light"
        )

        st.pydeck_chart(deck)

        # Legend
        st.markdown("**Legend**")
        col_leg1, col_leg2, col_leg3 = st.columns(3)
        with col_leg1:
            st.markdown("🟣 Hybrid")
        with col_leg2:
            st.markdown("🟡 Full Office")
        with col_leg3:
            st.markdown("🔵 Fully Remote")

        st.caption(f"Showing {len(map_df)} companies with headquarters locations")
    else:
        st.info("No companies with location data match your current filters.")

# Tab 2: Company Profiles
with tab2:
    st.subheader("Company Profiles")

    # Sort options
    sort_col1, sort_col2 = st.columns([1, 3])
    with sort_col1:
        sort_by = st.selectbox(
            "Sort by",
            options=['Innovation Rank', 'Company Name', 'Days Required', 'Employee Count'],
            index=0
        )

    # Map sort options to columns
    sort_map = {
        'Innovation Rank': 'innovation_overall',
        'Company Name': 'company',
        'Days Required': 'days_required',
        'Employee Count': 'employee_count'
    }

    ascending = sort_by in ['Innovation Rank', 'Company Name']
    sorted_df = filtered_df.sort_values(by=sort_map[sort_by], ascending=ascending)

    # Display companies in a grid
    for idx, row in sorted_df.iterrows():
        with st.container():
            col_logo, col_info, col_policy = st.columns([1, 2, 2])

            with col_logo:
                if row['logo_url']:
                    st.image(row['logo_url'], width=80)
                else:
                    st.write("🏢")
                st.caption(f"Rank #{row['innovation_overall']}")

            with col_info:
                st.markdown(f"**{row['company']}**")
                st.caption(f"{row['industry_sector']}")
                st.caption(f"📍 {row['headquarters']}")
                if row['employee_count'] > 0:
                    st.caption(f"👥 {row['employee_count']:,} employees")

            with col_policy:
                # Policy badge
                badge_class = 'badge-hybrid'
                if 'Remote' in row['category']:
                    badge_class = 'badge-remote'
                elif 'Office' in row['category']:
                    badge_class = 'badge-office'

                st.markdown(f"**{row['policy_type']}**")
                st.caption(f"{row['days_required']} days/week • {row['trend_direction']}")

                # Expander for details
                with st.expander("View Details"):
                    st.write(f"**Policy Details:** {row['details']}")

                    if row['key_quote']:
                        st.markdown(f"""
                        <div class="quote-box">
                            "{row['key_quote']}"
                        </div>
                        """, unsafe_allow_html=True)

                    st.write(f"**Effective Date:** {row['effective_date']}")
                    if row['previous_policy'] != 'N/A':
                        st.write(f"**Previous Policy:** {row['previous_policy']}")

                    # Innovation breakdown
                    st.write("**Innovation Rankings:**")
                    inno_col1, inno_col2, inno_col3 = st.columns(3)
                    with inno_col1:
                        st.metric("Culture", f"#{row['innovation_culture']}")
                    with inno_col2:
                        st.metric("Process", f"#{row['innovation_process']}")
                    with inno_col3:
                        st.metric("Product", f"#{row['innovation_product']}")

                    # Sources
                    if row['sources']:
                        st.write("**Sources:**")
                        for source in row['sources']:
                            url = source.get('url', '#')
                            source_type = source.get('type', 'Source')
                            reliability = source.get('reliability', '')
                            st.markdown(f"- [{source_type}]({url}) ({reliability})")

            st.divider()

# Tab 3: AI Assistant
with tab3:
    # Initialize search engine
    @st.cache_resource
    def get_search_engine():
        return CompanySearchEngine(raw_data)

    search_engine = get_search_engine()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Two different layouts based on state
    if not st.session_state.messages:
        # EMPTY STATE: Centered layout with input in middle
        st.markdown("")
        st.markdown("")
        st.subheader("Research Assistant")
        st.markdown("Ask questions about work policies across America's top innovators.")

        # Input in the middle
        prompt = st.chat_input("Ask about work policies...")

        # Example queries below input
        st.markdown("")
        st.caption("**Try these queries:**")
        col1, col2 = st.columns(2)
        with col1:
            st.caption("• Which tech companies are fully remote?")
            st.caption("• Compare Google and Microsoft policies")
        with col2:
            st.caption("• Which companies are tightening RTO?")
            st.caption("• Find 3-day hybrid companies")
    else:
        # CHAT STATE: Messages above, input at bottom
        # Header with clear button
        col_header, col_clear = st.columns([4, 1])
        with col_header:
            st.subheader("Research Assistant")
        with col_clear:
            if st.button("Clear", type="secondary"):
                st.session_state.messages = []
                st.rerun()

        # Chat messages container with fixed height
        chat_container = st.container(height=450)

        with chat_container:
            # Display chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Input at bottom
        prompt = st.chat_input("Ask about work policies...")

    # Handle the prompt (works for both states)
    if prompt:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Search for relevant companies
        search_results = search_engine.search(prompt, top_k=5)

        if search_results:
            # Format context
            context = format_company_context(search_results)

            # Generate response
            with st.chat_message("assistant"):
                try:
                    # Check for API key
                    api_key = st.secrets.get("ANTHROPIC_API_KEY", None)

                    if api_key:
                        client = anthropic.Anthropic(api_key=api_key)

                        # Streaming response
                        with client.messages.stream(
                            model="claude-sonnet-4-20250514",
                            max_tokens=1024,
                            system=create_system_prompt(),
                            messages=[
                                {"role": "user", "content": generate_response_prompt(prompt, context)}
                            ]
                        ) as stream:
                            response_placeholder = st.empty()
                            assistant_message = ""
                            for text in stream.text_stream:
                                assistant_message += text
                                response_placeholder.markdown(assistant_message + "▌")
                            response_placeholder.markdown(assistant_message)
                    else:
                        # Fallback: Show search results without LLM
                        companies_found = [r['company'].get('company', 'Unknown') for r in search_results]
                        assistant_message = f"""I found {len(search_results)} relevant companies based on your query:

**Companies found:** {', '.join(companies_found)}

To get AI-generated insights, please add your Anthropic API key to the app secrets.

Here's a summary of what I found:

"""
                        for result in search_results[:3]:
                            company = result['company']
                            wp = company.get('work_policy', {})
                            assistant_message += f"""
**{company.get('company', 'Unknown')}**
- Policy: {wp.get('type', 'Unknown')}
- Days in office: {wp.get('days_required', 'N/A')}
- Trend: {wp.get('trend_direction', 'Unknown')}
"""
                        st.markdown(assistant_message)

                    st.session_state.messages.append({"role": "assistant", "content": assistant_message})

                except Exception as e:
                    error_msg = f"Error generating response: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
        else:
            no_results_msg = "I couldn't find any companies matching your query. Try rephrasing or asking about specific companies, sectors, or policy types."
            with st.chat_message("assistant"):
                st.markdown(no_results_msg)
            st.session_state.messages.append({"role": "assistant", "content": no_results_msg})

# Tab 4: Analytics
with tab4:
    st.subheader("Research Analytics")

    # Key metrics at top
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Companies", len(filtered_df))

    with col2:
        avg_days = filtered_df['days_required'].mean()
        st.metric("Avg. Days in Office", f"{avg_days:.1f}")

    with col3:
        total_employees = filtered_df['employee_count'].sum()
        st.metric("Total Employees", f"{total_employees:,.0f}")

    with col4:
        tightening = len(filtered_df[filtered_df['trend_direction'] == 'Tightening'])
        pct = (tightening / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
        st.metric("Policies Tightening", f"{tightening} ({pct:.0f}%)")

    st.divider()

    # Policy Distribution and Days Required
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.write("**Policy Distribution**")

        # Neutral color scheme for categories
        color_map = {
            'Hybrid': '#C4B5FD',      # Soft purple
            'Full Office': '#FCD34D', # Soft amber
            'Fully Remote': '#93C5FD', # Soft blue
            'Unknown': '#E2E8F0'      # Gray
        }

        category_counts = filtered_df['category'].value_counts()
        fig_pie = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            hole=0.4,
            color=category_counts.index,
            color_discrete_map=color_map
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(
            showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        st.write("**Days Required Distribution**")

        days_counts = filtered_df['days_required'].value_counts().sort_index()
        fig_bar = px.bar(
            x=days_counts.index,
            y=days_counts.values,
            labels={'x': 'Days per Week', 'y': 'Number of Companies'},
            color_discrete_sequence=['#6366F1']
        )
        fig_bar.update_layout(
            xaxis_title="Days Required in Office",
            yaxis_title="Companies",
            margin=dict(t=20, b=40, l=40, r=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Sector breakdown heatmap
    st.write("**Policy Patterns by Sector**")

    sector_category = pd.crosstab(filtered_df['sector'], filtered_df['category'])
    fig_heatmap = px.imshow(
        sector_category,
        labels=dict(x="Policy Category", y="Sector", color="Count"),
        aspect="auto",
        color_continuous_scale=["#F1F5F9", "#6366F1"]
    )
    fig_heatmap.update_layout(margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.divider()

    col_ana1, col_ana2 = st.columns(2)

    with col_ana1:
        # Innovation vs Days Required
        st.write("**Innovation Rank vs. Days Required**")
        fig_scatter = px.scatter(
            filtered_df,
            x='days_required',
            y='innovation_overall',
            size='employee_count',
            hover_name='company',
            color='sector',
            labels={
                'days_required': 'Days in Office',
                'innovation_overall': 'Innovation Rank',
                'employee_count': 'Employees'
            },
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_scatter.update_yaxes(autorange="reversed")  # Lower rank = better
        fig_scatter.update_layout(margin=dict(t=20, b=40, l=40, r=20))
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_ana2:
        # Trend direction
        st.write("**Policy Trend Direction**")
        trend_counts = filtered_df['trend_direction'].value_counts()

        # Neutral colors for trends
        trend_colors = {
            'Tightening': '#F59E0B',
            'Stable': '#6366F1',
            'Maintaining': '#6366F1',
            'Relaxing': '#10B981',
            'Unknown': '#94A3B8'
        }

        fig_trend = px.bar(
            x=trend_counts.index,
            y=trend_counts.values,
            color=trend_counts.index,
            color_discrete_map=trend_colors,
            labels={'x': 'Trend', 'y': 'Companies'}
        )
        fig_trend.update_layout(
            showlegend=False,
            margin=dict(t=20, b=40, l=40, r=20)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    # Sector analysis
    st.write("**Average Days in Office by Sector**")
    sector_avg = filtered_df.groupby('sector')['days_required'].mean().sort_values(ascending=True)
    fig_sector = px.bar(
        x=sector_avg.values,
        y=sector_avg.index,
        orientation='h',
        labels={'x': 'Average Days Required', 'y': 'Sector'},
        color_discrete_sequence=['#6366F1']
    )
    fig_sector.update_layout(margin=dict(t=20, b=40, l=100, r=20))
    st.plotly_chart(fig_sector, use_container_width=True)

# Tab 5: About
with tab5:
    st.subheader("About This Research")

    st.markdown("""
    ### Research Context

    This platform presents research on work policies across America's most innovative companies,
    conducted as part of the **Critical Analytical Thinking** course at Stanford LEAD,
    taught by Professor **Haim Mendelson**.

    ---

    ### Company Selection: Why the Top 100?

    Companies in this study were selected from [Fortune's America's Most Innovative Companies 2025](https://fortune.com/ranking/americas-most-innovative-companies/),
    a ranking developed by **Statista** in partnership with Fortune magazine.

    **Why focus on the Top 100?**

    1. **Research Scope**: The top 100 represents the highest-scoring third of the 300 ranked companies,
       providing a focused yet comprehensive sample of innovation leaders
    2. **Data Quality**: Higher-ranked companies typically have more publicly available information
       about their workplace policies
    3. **Relevance**: These companies set industry standards and their policies influence broader
       workforce trends
    4. **Diversity**: The top 100 spans 18 industries and 37 states, ensuring representative coverage

    ---

    ### Innovation Ranking Methodology (Statista/Fortune)

    The Fortune ranking evaluates companies across **three dimensions of innovation**:

    #### 1. Product Innovation (1/3 weight)
    - Regular introduction of new products or services
    - Improvement of existing products and services
    - Patent portfolio strength (via LexisNexis® Patent Asset Index)

    #### 2. Process Innovation (1/3 weight)
    - Development and use of new technologies
    - Innovative production processes
    - Digital transformation initiatives

    #### 3. Innovation Culture (1/3 weight)
    - Spirit of entrepreneurship and creativity
    - Employee empowerment to take initiative
    - Environment for developing new ideas

    **Data Sources:**
    - **Employee Survey**: 40,000+ US employees (internal view)
    - **Expert Survey**: 2,500+ innovation experts (external view)
    - **Patent Analysis**: LexisNexis® Intellectual Property Solutions
    - **Expert Advisory Board**: 10 academics and innovation consultants

    ---

    ### Work Policy Research Methodology

    Work policy data was collected through multi-source verification:

    **Primary Sources:**
    - **Official Sources**: Company career pages, press releases, SEC filings, executive statements
    - **Media Reports**: Verified news articles from major publications (Reuters, Bloomberg, WSJ, etc.)
    - **Employee Sources**: Glassdoor reviews, Blind posts, verified employee accounts

    **Data Points Collected:**
    - Policy type and category
    - Days required in office
    - Specific day requirements
    - Effective dates and policy timeline
    - Trend direction (Tightening, Stable, Relaxing)
    - Executive quotes explaining policy rationale

    **Verification Process:**
    - Each policy verified against multiple sources
    - Source reliability rated (High, Medium, Low)
    - Research date recorded for each entry

    ---

    ### Data Quality & Limitations

    **Quality Indicators:**
    - **Verification Status**: Verified, Partially Verified, or Unverified
    - **Source Reliability**: Based on source type and recency
    - **Research Date**: All data collected November 2025

    **Limitations:**
    - Policies change frequently; information represents a point-in-time snapshot
    - Remote work eligibility varies by role, team, and location within companies
    - Official policy may differ from actual enforcement
    - Some companies have limited public information available
    - Employee reviews represent individual experiences, not comprehensive surveys

    ---

    ### Author

    **Maximilian Daub**
    Stanford LEAD Program
    [LinkedIn](https://www.linkedin.com/in/maximilian-daub/)

    ### Acknowledgments

    - Professor **Haim Mendelson** for guidance on this research project
    - [Monika Stezewska-Kruk](https://www.linkedin.com/in/monikastezewskakruk/) as course facilitator
    - **Fortune** and **Statista** for the Most Innovative Companies ranking and methodology
    - **LexisNexis®** for patent analysis data

    #### Team Limitation Busters (Stanford LEAD)

    - [Iryna Salamykina](https://www.linkedin.com/in/iryna-salamykina/) (Ireland)
    - [Stefanie Danner](https://www.linkedin.com/in/stefanie-danner-70837038/) (Switzerland)
    - Seun Ogunkunle (Ireland)
    - [Karan Dehghani](https://www.linkedin.com/in/karandehghani/) (Germany)
    - [Ruediger Schils](https://www.linkedin.com/in/ruediger-schils-6b611169/) (Germany)

    ---

    ### References

    - Fortune. (2025). *America's Most Innovative Companies 2025*. [https://fortune.com/ranking/americas-most-innovative-companies/](https://fortune.com/ranking/americas-most-innovative-companies/)
    - Statista. (2025). *America's Most Innovative Companies 2025: Methodology*. March 2025.

    ---

    *This research is presented for educational purposes as part of Stanford LEAD coursework.
    It does not constitute endorsement or criticism of any company's work policies.
    The quality of companies not included in this study is not disputed.*
    """)

# Footer
st.markdown("""
<div class="academic-footer">
    <strong>America's Top 100 Innovators - Work Policy Research Platform</strong><br>
    Stanford LEAD | Critical Analytical Thinking | November 2025<br>
    Research by Maximilian Daub
</div>
""", unsafe_allow_html=True)
