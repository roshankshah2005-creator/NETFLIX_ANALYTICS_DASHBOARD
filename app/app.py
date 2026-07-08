import os
import streamlit as st
import pandas as pd
import altair as alt

# ---------------Page Config (MUST BE FIRST)------------------
st.set_page_config(
    page_title="Netflix Analytics Dashboard",
    page_icon="🎬",
    layout="wide"
)

# --------------Background (CSS Layout Engine)---------------------
st.markdown("""
<style>

/* Google Font */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght=300;400;500;600;700&display=swap');

/* Main Background */
.stApp{
    background: linear-gradient(135deg,#0f172a,#1e293b,#111827);
    background-attachment: fixed;
    font-family: 'Poppins', sans-serif;
    color: white;
}

/* Main Container */
.block-container{
    padding-top:2rem;
    padding-bottom:2rem;
}

/* Metric Cards */
[data-testid="metric-container"]{
    background: rgba(255,255,255,0.08);
    border:1px solid rgba(255,255,255,0.12);
    border-radius:18px;
    padding:20px;
    box-shadow:0 10px 25px rgba(0,0,0,0.35);
    transition:0.3s;
}

[data-testid="metric-container"]:hover{
    transform:translateY(-6px);
    border:1px solid #E50914;
    box-shadow:0 15px 30px rgba(229,9,20,.35);
}

/* Buttons */
.stButton>button,
.stDownloadButton>button{
    width:100%;
    background:#E50914;
    color:white;
    border:none;
    border-radius:10px;
    padding:10px;
    font-weight:600;
}

.stButton>button:hover,
.stDownloadButton>button:hover{
    background:#ff2d3b;
}

/* Dataframe */
[data-testid="stDataFrame"]{
    border-radius:15px;
    overflow:hidden;
    border:1px solid rgba(255,255,255,.15);
}

/* Expander */
.streamlit-expanderHeader{
    background:rgba(255,255,255,0.06);
    border-radius:10px;
}

/* Headings */
h1{
    color:#E50914;
    font-weight:700;
}

h2,h3{
    color:white;
}

/* Horizontal Line */
hr{
    border:1px solid rgba(255,255,255,.1);
}

/* Scrollbar */
::-webkit-scrollbar{
    width:8px;
}

::-webkit-scrollbar-thumb{
    background:#E50914;
    border-radius:20px;
}

::-webkit-scrollbar-track{
    background:#1a1a1a;
}

/* Hide Streamlit Default UI branding elements */
#MainMenu{
    visibility:hidden;
}

footer{
    visibility:hidden;
}

header{
    visibility:hidden;
}

</style>
""", unsafe_allow_html=True)

#-------------------Dataset Loader (Fixed Relative Paths)--------------------
@st.cache_data
def load_data():
    # Pinpoints file path dynamically by checking the script's real execution path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.abspath(os.path.join(current_dir, "..", "data", "netflix_titles_updated.csv"))
    
    # Cloud Failback route verification check
    if not os.path.exists(file_path):
        file_path = os.path.abspath(os.path.join(current_dir, "..", "data", "netflix_cleaned.csv"))
        
    df = pd.read_csv(file_path)
    df["country"] = df["country"].fillna("Unknown")
    df["rating"] = df["rating"].fillna("UR")
    return df

raw_data = load_data()
filtered = raw_data.copy()

#--------------Sidebar Management & Search Engine Filters------------
try:
    st.sidebar.image("images/netflix_logo.png", width=180)
except Exception:
    try:
        st.sidebar.image("images/N.webp", width=100)
    except Exception:
        st.sidebar.title("🍿 Netflix")

st.sidebar.title("Netflix Dashboard")
st.sidebar.markdown("Use the filters below to explore the Netflix catalog.")

# Text Title Filter Input
search = st.sidebar.text_input("Search Title", placeholder="e.g. Stranger Things")
if search:
    filtered = filtered[filtered["title"].str.contains(search, case=False, na=False)]

# Content Categorization Selection Dropdown
content_choices = st.sidebar.multiselect("Select Content Type", options=raw_data["type"].unique(), default=raw_data["type"].unique())
filtered = filtered[filtered["type"].isin(content_choices)]

#------------------Tab Layout Grid Navigation System-------------------
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📋 Dataset Explorer", "ℹ️ About"])

with tab1:
    st.title("🎬 Netflix Analytics Dashboard")
    st.markdown("This dashboard provides global insights into the complete Netflix catalog, exploring core trends by country, genre, rating, and release timeline.")
    st.markdown("---")

    #-------------------Expanded 6 Metric Card KPI Matrix-----------------------
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    
    kpi1.metric("Total Titles", f"{len(filtered):,}")
    kpi2.metric("Movies", f"{(filtered['type'] == 'Movie').sum():,}")
    kpi3.metric("TV Shows", f"{(filtered['type'] == 'TV Show').sum():,}")
    kpi4.metric("Countries", f"{filtered['country'].nunique():,}")
    
    oldest_release = int(filtered["release_year"].min()) if not filtered.empty else "N/A"
    latest_release = int(filtered["release_year"].max()) if not filtered.empty else "N/A"
    
    kpi5.metric("Oldest Release", oldest_release)
    kpi6.metric("Latest Release", latest_release)
    st.markdown("---")

    #----------------Two-Column Layout: Donut vs Horizontal Bars------------------
    left, right = st.columns(2)
    
    with left:
        st.subheader("Movies vs TV Shows")
        if not filtered.empty:
            type_counts = filtered["type"].value_counts().reset_index()
            type_counts.columns = ["Type", "Count"]
            
            chart1 = alt.Chart(type_counts).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Type", type="nominal", scale=alt.Scale(domain=['Movie', 'TV Show'], range=['#E50914', '#262730'])),
                tooltip=["Type", "Count"]
            ).properties(height=300)
            st.altair_chart(chart1, use_container_width=True)
        else:
            st.warning("No records match your query layout filters.")

    with right:
        st.subheader("Top 10 Genres")
        if not filtered.empty:
            genre_df = filtered.copy()
            genre_df["listed_in"] = genre_df["listed_in"].str.split(",")
            genre_df = genre_df.explode("listed_in")
            genre_df["listed_in"] = genre_df["listed_in"].str.strip()
            top_genres = genre_df["listed_in"].value_counts().head(10).reset_index()
            top_genres.columns = ["Genre", "Count"]
            
            chart2 = alt.Chart(top_genres).mark_bar(color="#E50914").encode(
                x=alt.X("Count:Q", title="Total Titles"),
                y=alt.Y("Genre:N", sort="-x", title="Genre"),
                tooltip=["Genre", "Count"]
            ).properties(height=300)
            st.altair_chart(chart2, use_container_width=True)
        else:
            st.warning("No records match your query layout filters.")

    st.markdown("---")
    
    #----------------Two-Column Layout: Line vs Vertical Bars------------------
    left_trend, right_rating = st.columns(2)
    
    with left_trend:
        st.subheader("Content Added Over Time")
        if not filtered.empty and "year_added" in filtered.columns:
            trend = filtered["year_added"].dropna().value_counts().sort_index().reset_index()
            trend.columns = ["Year", "Titles"]
            
            chart3 = alt.Chart(trend).mark_line(color="#E50914", point=True).encode(
                x=alt.X("Year:O", title="Year"),
                y=alt.Y("Titles:Q", title="Titles Added"),
                tooltip=["Year", "Titles"]
            ).properties(height=300)
            st.altair_chart(chart3, use_container_width=True)
        else:
            st.warning("Timeline metadata metric filters are unavailable.")

    with right_rating:
        st.subheader("Content Distribution by Rating")
        if not filtered.empty:
            rating_count = filtered["rating"].value_counts().head(10).reset_index()
            rating_count.columns = ["Rating", "Count"]
            
            chart4 = alt.Chart(rating_count).mark_bar(color="#262730").encode(
                x=alt.X("Rating:N", sort="-y", title="Age Rating"),
                y=alt.Y("Count:Q", title="Titles Count"),
                tooltip=["Rating", "Count"]
            ).properties(height=300)
            st.altair_chart(chart4, use_container_width=True)
        else:
            st.warning("No structural rating counts match selections.")

    st.markdown("---")

    #-----------------Top Countries Distribution Layer---------------------
    st.subheader("🗺️ Content Distribution Across Top Production Countries")
    if not filtered.empty:
        country = filtered.copy()
        country["country"] = country["country"].str.split(",")
        country = country.explode("country")
        country["country"] = country["country"].str.strip()
        
        country_count = country["country"].value_counts().reset_index()
        country_count.columns = ["Country", "Titles"]
        country_count = country_count[country_count["Country"] != "Unknown"].head(15)

        chart_countries = alt.Chart(country_count).mark_bar(color="#E50914").encode(
            x=alt.X("Country:N", sort="-y", title="Country"),
            y=alt.Y("Titles:Q", title="Total Catalog Size"),
            tooltip=["Country", "Titles"]
        ).properties(height=350)
        st.altair_chart(chart_countries, use_container_width=True)
    else:
        st.warning("No geographic dataset properties found.")

with tab2:
    st.title("📋 Interactive Dataset Explorer")
    st.markdown("Search, slice, and verify dataset parameters on-demand below.")
    st.dataframe(filtered, use_container_width=True)
    
    # -------------Download Section Included inside Data View---------------------
    st.markdown("### Export Segment Records")
    csv = filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Active Dataset Selection",
        data=csv,
        file_name="netflix_catalog_filtered.csv",
        mime="text/csv"
    )

with tab3:
    st.title("ℹ️ About This Analytics Architecture")
    st.write("""
    ### Netflix Portfolio Engine
    Designed as an enterprise-grade workspace view capturing programmatic metrics evaluating international content distribution, ratings, and media tracking timelines.
    
    Built using:
    * **Python**
    * **Pandas Dataframes**
    * **Altair Native Rendering Engine**
    * **Streamlit Web Framework**
    """)

#----------------Project Footer Layout--------------------------
st.markdown("---")
st.caption("Created by **Roshan** | Data Science Portfolio Project 🚀")
