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

# ✅ 2. Sports Industry Donut Chart (grouped small values into "Others")
st.subheader("Sports Industry Employment")

# Count categories
industry_counts = {}
for val in df["In Sports Industry"].dropna():
    for category in map(str.strip, val.split(",")):
        industry_counts[category] = industry_counts.get(category, 0) + 1
industry_df = pd.DataFrame(industry_counts.items(), columns=["Category", "Count"]).sort_values(by="Count", ascending=False)

# Group small values
def group_small_categories(df, category_col, count_col="Count", threshold=1):
    large_df = df[df[count_col] > threshold]
    small_df = df[df[count_col] <= threshold]

    if not small_df.empty:
        others_sum = small_df[count_col].sum()
        others_row = pd.DataFrame([{category_col: "Others", count_col: others_sum}])
        grouped_df = pd.concat([large_df, others_row], ignore_index=True)
    else:
        grouped_df = df.copy()

    return grouped_df, small_df

industry_df_grouped, industry_others = group_small_categories(industry_df, "Category", "Count", threshold=1)

# Donut chart
fig_industry = px.pie(industry_df_grouped, names="Category", values="Count", hole=0.5)
fig_industry.update_traces(textposition='inside', textinfo='percent')
st.plotly_chart(fig_industry, use_container_width=True)

# Others list
if not industry_others.empty:
    with st.expander("View items grouped into 'Others' (Count ≤ 1)"):
        st.write(industry_others.sort_values("Category").reset_index(drop=True))

# 3. Job Titles by Reclassified Sector
st.subheader("Job Titles by Reclassified Sector")

job_df = df[['Job Title', 'Organization']].dropna(subset=['Job Title', 'Organization'])

def classify_sector(job_title, organization):
    text = f"{job_title} {organization}".lower()
    if any(x in text for x in ["university", "research", "professor", "lecturer"]):
        return "Academia"
    elif any(x in text for x in ["ministry", "authority", "department", "municipality", "public"]):
        return "Government"
    elif any(x in text for x in ["federation", "association", "olympic", "committee", "noc"]):
        if "international" in organization.lower():
            return "International Federation"
        return "National Federation"
    elif any(x in text for x in ["ngo", "foundation", "non-profit", "charity", "relief"]):
        return "NGO"
    elif any(x in text for x in ["company", "consulting", "consultant", "agency", "firm", "marketing", "ltd", "inc", "club"]):
        return "Private Sector"
    else:
        return "Other"

job_df["Reclassified Sector"] = job_df.apply(lambda row: classify_sector(row["Job Title"], row["Organization"]), axis=1)
sector_counts = job_df["Reclassified Sector"].value_counts().reset_index()
sector_counts.columns = ["Sector", "Count"]
fig_job = px.bar(sector_counts.sort_values("Count"), x="Count", y="Sector", orientation="h", text="Count")
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
