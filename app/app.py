import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

#---------------Page Config (MUST BE FIRST)------------------
st.set_page_config(
    page_title="Netflix Analytics Dashboard",
    page_icon="🎬",
    layout="wide"
)

#---------------Title-------------------
st.title("🎬 Netflix Analytics Dashboard")

st.markdown(
"""
Explore Netflix Movies and TV Shows using interactive filters.
"""
)

#--------------Background (CSS)---------------------
st.markdown("""
<style>

/* Google Font */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

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

/* Sidebar */
[data-testid="stSidebar"]{
    background: linear-gradient(180deg,#141E30,#243B55);
    border-right:1px solid rgba(255,255,255,0.15);
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

/* Slider */
.stSlider{
    padding-top:10px;
}

/* Select Boxes */
.stMultiSelect, .stSelectbox{
    background:rgba(255,255,255,0.04);
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

/* Hide Streamlit Menu */
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

#--------------Image--------------------------
# Double check your "images" folder is uploaded to GitHub as well!
st.image("images/N.webp", width=200)

#-------------Description-------------------
st.markdown(
"""
This dashboard provides insights into Netflix's global catalog,
including trends by country, genre, rating, and release year.
"""
)

#-------------------Dataset--------------------
@st.cache_data
def load_data():
    # Bulletproof relative path finding logic
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Looks for data folder relative to app.py
    file_path = os.path.join(current_dir, "..", "data", "netflix_titles_updated.csv")
    
    # Fallback to absolute repository path structure if Streamlit mounts from root
    if not os.path.exists(file_path):
        file_path = os.path.join(current_dir, "data", "netflix_titles_updated.csv")
        
    return pd.read_csv(file_path)

netflix = load_data()

#------------------Sidebars--------------------
st.sidebar.header("Filters")
content_type = st.sidebar.multiselect(
    "Select Content Type",
    options=sorted(netflix["type"].dropna().unique()),
    default=sorted(netflix["type"].dropna().unique())
)
country = st.sidebar.multiselect(
    "Select Country",
    options=sorted(netflix["country"].dropna().unique()),
    default=sorted(netflix["country"].dropna().unique())
)
rating = st.sidebar.multiselect(
    "Select Rating",
    options=sorted(netflix["rating"].dropna().unique()),
    default=sorted(netflix["rating"].dropna().unique())
)
years = sorted(netflix["release_year"].unique())

year_range = st.sidebar.slider(
    "Release Year",
    min_value=min(years),
    max_value=max(years),
    value=(min(years), max(years))
)

#-------------------Filters-------------------
filtered = netflix[
    (netflix["type"].isin(content_type)) &
    (netflix["country"].isin(country)) &
    (netflix["rating"].isin(rating)) &
    (netflix["release_year"].between(year_range[0], year_range[1]))
]

#-------------------KPI-----------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Titles",
    len(filtered)
)

col2.metric(
    "Movies",
    (filtered["type"]=="Movie").sum()
)

col3.metric(
    "TV Shows",
    (filtered["type"]=="TV Show").sum()
)

col4.metric(
    "Countries",
    filtered["country"].nunique()
)

#----------------Movies vs Tv shows------------------
st.subheader("Movies vs TV Shows")
type_counts = filtered["type"].value_counts()
fig, ax = plt.subplots(figsize=(5,5))
ax.pie(
    type_counts,
    labels=type_counts.index,
    autopct="%1.1f%%",
    startangle=90
)
st.pyplot(fig)

#--------------------Top Genres--------------------------
genre = filtered.copy()
genre["listed_in"] = genre["listed_in"].str.split(",")
genre = genre.explode("listed_in")
genre["listed_in"] = genre["listed_in"].str.strip()
top_genres = genre["listed_in"].value_counts().head(10)
st.subheader("Top Genres")
fig, ax = plt.subplots(figsize=(8,5))
ax.barh(
    top_genres.index,
    top_genres.values
)
st.pyplot(fig)

#---------------Content Added Over Time------------------
st.subheader("Content Added Over Time")
trend = filtered["year_added"].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(10,5))
ax.plot(
    trend.index,
    trend.values,
    marker="o"
)
ax.set_xlabel("Year")
ax.set_ylabel("Titles")
st.pyplot(fig)

#-----------------Top Ratings-------------------------------
st.subheader("Ratings")
rating_count = filtered["rating"].value_counts()
fig, ax = plt.subplots(figsize=(8,5))
ax.bar(
    rating_count.index,
    rating_count.values
)
plt.xticks(rotation=45)
st.pyplot(fig)

#------------------Show Data-------------------------------
st.subheader("Dataset")
st.dataframe(filtered)

with st.expander("View Raw Data"):
    st.dataframe(filtered)

#-------------Download Button---------------------
csv = filtered.to_csv(index=False)

st.download_button(
    "Download Filtered Data",
    csv,
    "filtered_netflix.csv",
    "text/csv"
)

#----------------Footer--------------------------
st.markdown("---")
st.markdown(
"Created by **Roshan** using Python, Jupyter, Pandas, Matplotlib, and Streamlit."
)
