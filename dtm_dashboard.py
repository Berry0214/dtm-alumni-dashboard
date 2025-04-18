# dtm_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(page_title="DTM Alumni Dashboard", layout="wide")
st.title("DTM Alumni Dashboard")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("DTM_Alumni_ClaudeFriendly.csv").dropna(how="all")

df = load_data()

# Define sports categories
SPORTS_CATEGORIES = sorted({
    cat.strip() for sublist in df["In Sports Industry"].dropna().str.split(",") for cat in sublist
})

# Sidebar filters
st.sidebar.header("Filters")
selected_categories = st.sidebar.multiselect("Select Sports Categories", SPORTS_CATEGORIES)
search_term = st.sidebar.text_input("Search Organization or Job Title")

# Filter by sports categories
if selected_categories:
    df = df[df["In Sports Industry"].fillna("").apply(lambda x: any(cat in x for cat in selected_categories))]

# Filter by search term
if search_term:
    search_term = search_term.lower()
    df = df[df.apply(lambda row: search_term in str(row["Organization"]).lower() or search_term in str(row["Job Title"]).lower(), axis=1)]

# 1. Continent Pie Chart
if "Continent" in df.columns:
    st.subheader("Alumni Distribution by Continent")
    continent_counts = df["Continent"].value_counts().reset_index()
    continent_counts.columns = ["Continent", "Count"]
    fig_continent = px.pie(continent_counts, names="Continent", values="Count", hole=0.3)
    fig_continent.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_continent, use_container_width=True)

# 2. Sports Industry Donut Chart
st.subheader("Sports Industry Employment")
industry_counts = {}
for val in df["In Sports Industry"].dropna():
    for category in map(str.strip, val.split(",")):
        industry_counts[category] = industry_counts.get(category, 0) + 1
industry_df = pd.DataFrame(industry_counts.items(), columns=["Category", "Count"]).sort_values(by="Count", ascending=False)
fig_industry = px.pie(industry_df, names="Category", values="Count", hole=0.5)
fig_industry.update_traces(textposition='inside', textinfo='percent')
st.plotly_chart(fig_industry, use_container_width=True)

# 3. Job Title Category Bar Chart
st.subheader("Job Titles by Sector")
def categorize_job(title):
    t = str(title).lower()
    if "ministry" in t or "authority" in t or "government" in t: return "Government"
    if "noc" in t or ("national" in t and "federation" in t): return "National Federation"
    if "ioc" in t or "fifa" in t or "international federation" in t: return "International Federation"
    if "university" in t or "professor" in t or "research" in t: return "Academia"
    if "company" in t or "consulting" in t or "club" in t: return "Private Sector"
    if "ngo" in t or "non-profit" in t: return "NGO"
    if "self" in t or "entrepreneur" in t or "founder" in t: return "Self-Employed"
    return "Other"

job_df = df["Job Title"].dropna().apply(categorize_job)
job_cat_counts = job_df.value_counts().reset_index()
job_cat_counts.columns = ["Sector", "Count"]
fig_job = px.bar(job_cat_counts, x="Count", y="Sector", orientation="h", text="Count")
fig_job.update_layout(margin=dict(l=10, r=10, t=30, b=10))
fig_job.update_traces(textposition='outside')
st.plotly_chart(fig_job, use_container_width=True)

# 4. Top 10 Organizations + Others
st.subheader("Top 10 Organizations")
org_counts = df["Organization"].dropna().value_counts()
top10 = org_counts.head(10).reset_index()
top10.columns = ["Organization", "Count"]
others = org_counts[10:].sum()
if others > 0:
    top10 = pd.concat([top10, pd.DataFrame([{"Organization": "Others", "Count": others}])], ignore_index=True)
fig_org = px.bar(top10, x="Count", y="Organization", orientation="h", text="Count")
fig_org.update_layout(margin=dict(l=10, r=10, t=30, b=10))
fig_org.update_traces(textposition='outside')
st.plotly_chart(fig_org, use_container_width=True)

# 5. Application Path
st.subheader("DTM Application Pathway")
path_df = df["DTM Application Path"].dropna().value_counts().reset_index()
path_df.columns = ["Pathway", "Count"]
fig_path = px.bar(path_df, x="Pathway", y="Count", text="Count")
fig_path.update_layout(xaxis_tickangle=-45, margin=dict(l=10, r=10, t=30, b=80))
fig_path.update_traces(textposition='outside')
st.plotly_chart(fig_path, use_container_width=True)

# Footer note
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 0.85rem;'>Designed for responsive view – best viewed on desktop and mobile.</p>", unsafe_allow_html=True)
