import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- 0. Configuration and Data Loading ---

# I'm setting up my page configuration for a wide layout and a nice title.
# This makes my dashboard look professional and utilize the screen space better.
st.set_page_config(
    page_title="Freelance Marketplace Dynamics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# I'm loading the clean, pre-processed data that I created in Step 3.
# I'm using st.cache_data to make sure my dashboard loads quickly!
@st.cache_data
def load_data():
    try:
        # I must ensure this .xlsx file exists in the same folder!
        # I am changing this to read the Excel file now.
        data = pd.read_excel('freelance_dashboard_data.xlsx')
        return data
    except FileNotFoundError:
        st.error("🚨 Error: I couldn't find 'freelance_dashboard_data.xlsx'. I need to stop the app, check my D:\oogunjobi folder, and make sure the file name and extension are correct.")
        return pd.DataFrame() 

df = load_data()

# I will stop the application if the data didn't load successfully.
if df.empty:
    st.stop()


# --- 1. Dashboard Title and Overview Metrics ---

st.title("🎯 Freelance Marketplace Dynamics Dashboard")
st.subheader("My Analysis of Demand, Supply, and Search Friction (Search-Model View)")

# I'm calculating the key metrics for the top bar (The Overview Panel)
total_jobs = int(df.shape[0])
avg_price = df['Price_USD'].mean()
unique_countries = df['client_country'].nunique()

# I'm using columns to present these metrics clearly and neatly.
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total Job Postings (Demand)", value=f"{total_jobs:,}")
with col2:
    st.metric(label="Average Project Price (USD)", value=f"${avg_price:,.0f}")
with col3:
    st.metric(label="Unique Client Countries", value=f"{unique_countries}")

st.markdown("---") # A separator to keep things tidy

# --- 2. Demand/Supply Balance Analysis (The Core Story) ---

st.header("📈 Market Tightness: Competition & Pay")

# I'm creating a sidebar filter so users can interact with the data.
st.sidebar.header("🔍 Filter Options")
selected_country = st.sidebar.selectbox(
    '1. Filter by Client Country',
    ['All Countries'] + sorted(df['client_country'].unique().tolist())
)

# Apply filter
if selected_country != 'All Countries':
    df_filtered = df[df['client_country'] == selected_country]
    st.markdown(f"**I am now viewing data for:** {selected_country}")
else:
    df_filtered = df

# --- Re-calculating the data for the Scatter Plot based on the filter ---
avg_price_by_skill = df_filtered.groupby('Skill_Category')['Price_USD'].mean().reset_index()
avg_friction_by_skill = df_filtered.groupby('Skill_Category')['Freelancer_Friction_Index'].mean().reset_index()
market_analysis = pd.merge(avg_price_by_skill, avg_friction_by_skill, on='Skill_Category')


# --- Chart 1: Market Tightness Scatter Plot ---
fig1 = px.scatter(
    market_analysis,
    x='Freelancer_Friction_Index',
    y='Price_USD',
    color='Skill_Category',
    size='Price_USD',
    hover_name='Skill_Category',
    title='Competition vs. Pay by Skill Category',
    labels={
        'Freelancer_Friction_Index': 'Freelancer Friction Index (Proxy for Competition)',
        'Price_USD': 'Average Project Price (USD)'
    }
)
fig1.update_layout(template="plotly_white", title_x=0.5, legend_title="Skill Category")

# I'm setting up two columns: one for the chart, one for the interpretation.
col_chart1, col_insight1 = st.columns([3, 2])

with col_chart1:
    st.plotly_chart(fig1, use_container_width=True)

with col_insight1:
    st.markdown("### 💡 My Search-Model Interpretation")
    st.info(
        "**This chart is the core of my Search-Model analysis.** It shows the **bargaining power** and **friction** in the market. \n\n"
        "**Niche/High-Value (Low Friction, High Pay):** Categories like Web & Software Dev show high average pay but low competition. This is where **my supply (freelancers) has high bargaining power** and clients face less friction in finding quality services.\n\n"
        "**Oversupplied/Low-Value (High Friction, Low Pay):** Categories like Writing & Translation have intense competition (high Friction Index) and lower pay. This indicates an **oversaturated market** and high friction for **my side** (freelancers) trying to secure a job."
    )

st.markdown("---")


# --- 3. Regional Demand & Project Structure Analysis ---

st.header("🌍 Demand Agents and Trade Surplus Structure")

# I'm using two columns for the remaining two charts.
col_chart2, col_chart3 = st.columns(2)

# --- Chart 2: Top 10 Client Countries Bar Chart ---
with col_chart2:
    st.subheader("Top Client Countries (Demand Dominance)")
    
    # Recalculate based on current filtered data
    country_counts = df_filtered['client_country'].value_counts().nlargest(10).reset_index()
    country_counts.columns = ['Country', 'Job_Count']

    fig2 = px.bar(
        country_counts,
        x='Job_Count',
        y='Country',
        orientation='h',
        color='Job_Count',
        color_continuous_scale=px.colors.sequential.Teal,
        labels={'Job_Count': 'Total Jobs Posted', 'Country': 'Client Country'}
    )
    fig2.update_layout(yaxis={'categoryorder':'total ascending'}, template="plotly_white", showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### My Interpretation (Demand Side)")
    st.caption(
        "The **Demand Agents** (clients) are heavily concentrated in a few regions (India and the US dominate). "
        "This concentration means **regional demand patterns** strongly influence the platform's overall market equilibrium and pricing."
    )

# --- Chart 3: Job Type Distribution Pie Chart ---
with col_chart3:
    st.subheader("Project Type Preference (Trade Surplus)")

    # Recalculate based on current filtered data
    job_type_counts = df_filtered['Job_Type'].value_counts().reset_index()
    job_type_counts.columns = ['Job_Type', 'Count']

    # I'm using 'Teal' here for consistency and safety.
    fig3 = px.pie(
        job_type_counts,
        values='Count',
        names='Job_Type',
        color_discrete_sequence=px.colors.sequential.Teal
    )
    fig3.update_traces(textinfo='percent+label', pull=[0.05, 0])
    fig3.update_layout(height=400, showlegend=True, margin=dict(t=30, b=30, l=0, r=0))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("#### My Interpretation (Trade Surplus)")
    st.caption(
        "The market overwhelmingly prefers **Fixed Price** jobs (~80%). "
        "This structure minimizes client risk (Demand Side), but the smaller **Hourly Rate** segment "
        "suggests opportunities for long-term engagements where the **search friction** of defining scope is too high for a fixed bid."
    )

st.markdown("---")

st.markdown("---")
st.markdown("Created as a portfolio project using Streamlit and Search-Model theory.")
