import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from plotly.subplots import make_subplots

# Set page config
st.set_page_config(
    page_title="Weapon Arrests Analysis",
    page_icon="🚔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    """Load all CSV files with robust error handling"""
    try:
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir == "":
            script_dir = "."

        # Print directory information for debugging
        st.sidebar.write("Looking for data files in:", script_dir)
        
        # Attempt to load the files
        monthly_data = pd.read_csv(os.path.join(script_dir, 'weapon_arrests_monthly.csv'))
        summary_data = pd.read_csv(os.path.join(script_dir, 'weapon_arrests_summary.csv'))
        monthly_averages = pd.read_csv(os.path.join(script_dir, 'weapon_arrests_monthly_averages.csv'))
        
        return monthly_data, summary_data, monthly_averages
        
    except FileNotFoundError as e:
        st.error(f"""
        Error: Could not find one or more data files.
        
        Please ensure the following files are in the directory {script_dir}:
        - weapon_arrests_monthly.csv
        - weapon_arrests_summary.csv
        - weapon_arrests_monthly_averages.csv
        
        Error details: {str(e)}
        """)
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.stop()

# Application Header
st.title("🚔 New Mexico Weapon-Related Arrests Analysis")
st.markdown("""
This dashboard analyzes weapon-related arrests in New Mexico from 2018 to 2023. 
Use the controls in the sidebar to explore different aspects of the data.
""")

# Load data
monthly_data, summary_data, monthly_averages = load_data()

# Sidebar Controls
st.sidebar.title("Dashboard Controls")

# Year range selector
years = sorted(monthly_data['Year'].unique())
year_range = st.sidebar.select_slider(
    "Select Year Range",
    options=years,
    value=(min(years), max(years))
)

# Filter data based on year range
filtered_data = monthly_data[
    (monthly_data['Year'] >= year_range[0]) & 
    (monthly_data['Year'] <= year_range[1])
]

# Main KPI Metrics
st.markdown("### Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_arrests = filtered_data['Arrests'].sum()
    st.metric("Total Arrests", f"{total_arrests:,.0f}")

with col2:
    avg_monthly = filtered_data['Arrests'].mean()
    st.metric("Average Monthly Arrests", f"{avg_monthly:.1f}")

with col3:
    yoy_change = filtered_data['YoY_Change'].mean()
    st.metric("Average YoY Change", f"{yoy_change:.1f}%")

with col4:
    trend = "📈" if yoy_change > 0 else "📉"
    st.metric("Overall Trend", trend)

# Create tabs for different visualizations
tab1, tab2, tab3, tab4 = st.tabs([
    "Monthly Trends", 
    "Year Comparison",
    "Seasonal Analysis",
    "Statistics"
])

# Tab 1: Monthly Trends
with tab1:
    st.markdown("### Monthly Arrest Trends")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=filtered_data['Year_Month'],
        y=filtered_data['Arrests'],
        name='Monthly Arrests',
        mode='lines+markers',
        line=dict(color='#1f77b4')
    ))
    
    fig.add_trace(go.Scatter(
        x=filtered_data['Year_Month'],
        y=filtered_data['3_Month_Avg'],
        name='3-Month Average',
        line=dict(color='#ff7f0e', dash='dash')
    ))
    
    fig.add_trace(go.Scatter(
        x=filtered_data['Year_Month'],
        y=filtered_data['12_Month_Avg'],
        name='12-Month Average',
        line=dict(color='#2ca02c', dash='dash')
    ))
    
    fig.update_layout(
        title='Monthly Arrests with Moving Averages',
        xaxis_title='Date',
        yaxis_title='Number of Arrests',
        hovermode='x unified',
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Tab 2: Year Comparison
with tab2:
    st.markdown("### Year-over-Year Comparison")
    
    yearly_comparison = filtered_data.pivot(
        index='Month',
        columns='Year',
        values='Arrests'
    )
    
    fig = px.line(
        yearly_comparison,
        title='Year-over-Year Comparison by Month',
        labels={'value': 'Number of Arrests', 'Month': 'Month'},
        height=500
    )
    
    fig.update_layout(hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)
    
    # Heatmap
    yoy_pivot = filtered_data.pivot(
        index='Year',
        columns='Month',
        values='YoY_Change'
    )
    
    fig_heatmap = px.imshow(
        yoy_pivot,
        title='Year-over-Year Change Heatmap (%)',
        color_continuous_scale='RdYlBu',
        aspect='auto',
        height=400
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)

# Tab 3: Seasonal Analysis
with tab3:
    st.markdown("### Seasonal Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            monthly_averages,
            x='Month',
            y='Average_Arrests',
            error_y='Std_Dev',
            title='Average Monthly Arrests',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.box(
            filtered_data,
            x='Month',
            y='Arrests',
            title='Monthly Distribution',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

# Tab 4: Statistics
with tab4:
    st.markdown("### Detailed Statistics")
    
    # Summary statistics
    st.subheader("Yearly Summary")
    st.dataframe(
        summary_data.style.format({
            'Total_Arrests': '{:,.0f}',
            'Average_Monthly_Arrests': '{:.1f}',
            'Max_Monthly_Arrests': '{:.0f}',
            'Min_Monthly_Arrests': '{:.0f}',
            'Standard_Deviation': '{:.1f}'
        }),
        height=400
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Monthly Statistics")
        st.dataframe(
            monthly_averages.style.format({
                'Average_Arrests': '{:.1f}',
                'Std_Dev': '{:.1f}',
                'Min_Arrests': '{:.0f}',
                'Max_Arrests': '{:.0f}'
            })
        )
    
    with col2:
        st.subheader("Year-over-Year Changes")
        yearly_changes = filtered_data.groupby('Year')['Arrests'].agg([
            ('Total_Arrests', 'sum'),
            ('YoY_Change', lambda x: ((x.sum() / x.shift(12).sum()) - 1) * 100)
        ]).reset_index()
        
        st.dataframe(
            yearly_changes.style.format({
                'Total_Arrests': '{:,.0f}',
                'YoY_Change': '{:.1f}%'
            })
        )

# Footer
st.markdown("---")
st.markdown("""
    📊 Data source: NIBRS (National Incident-Based Reporting System)  
    📅 Last updated: {}
""".format(pd.Timestamp.now().strftime("%Y-%m-%d")))

# Debug information in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### Debug Information")
st.sidebar.write("Current working directory:", os.getcwd())
st.sidebar.write("Files in directory:", os.listdir())
