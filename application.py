import streamlit as st
import requests
import pickle
import pandas as pd
import base64
from PIL import Image, ImageDraw, ImageFilter
import io
import gdown  # Added to download similarity.pkl from Google Drive

# TMDb API Configuration
API_KEY = 'c9cb5ec336fa36659fbba0ba516298dc'
BASE_URL = 'https://api.themoviedb.org/3'

# -------------------- Download similarity.pkl from Google Drive --------------------
# File ID from your shared Google Drive link
file_id = '1yz5J_bO6YhwsNnDakBR7WFQPWwhjUX_j'
url = f'https://drive.google.com/uc?id={file_id}'
output_path = 'similarity.pkl'
gdown.download(url, output_path, quiet=False)

# -------------------- Data Loading --------------------
movies = pd.DataFrame(pickle.load(open('movie_dict1.pkl', 'rb')))
with open('similarity.pkl', 'rb') as f:
    similarity = pickle.load(f)

# -------------------- Helper Functions --------------------
def fetch_poster(movie_id):
    try:
        response = requests.get(f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}")
        data = response.json()
        return f"https://image.tmdb.org/t/p/w500/{data['poster_path']}" if data.get('poster_path') else None
    except:
        return None

def fetch_movie_details(movie_id):
    try:
        details = requests.get(f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}").json()
        credits = requests.get(f"{BASE_URL}/movie/{movie_id}/credits?api_key={API_KEY}").json()
        reviews = requests.get(f"{BASE_URL}/movie/{movie_id}/reviews?api_key={API_KEY}").json()
        
        return {
            'title': details.get('title'),
            'poster': fetch_poster(movie_id),
            'overview': details.get('overview'),
            'rating': details.get('vote_average'),
            'runtime': details.get('runtime'),
            'genres': [g['name'] for g in details.get('genres', [])],
            'director': next((c['name'] for c in credits.get('crew', []) if c['job'] == 'Director'), None),
            'cast': [c['name'] for c in credits.get('cast', [])[:5]],
            'reviews': [r['content'] for r in reviews.get('results', [])[:3]],
            'trailer': get_trailer_key(movie_id)
        }
    except:
        return None

def get_trailer_key(movie_id):
    try:
        videos = requests.get(f"{BASE_URL}/movie/{movie_id}/videos?api_key={API_KEY}").json()
        return next((v['key'] for v in videos['results'] if v['type'] == 'Trailer' and v['site'] == 'YouTube'), None)
    except:
        return None

def fetch_popular_movies():
    response = requests.get(f"{BASE_URL}/movie/popular?api_key={API_KEY}")
    return [{'id': m['id'], 'title': m['title']} for m in response.json()['results'][:10]]

def fetch_trending_movies():
    response = requests.get(f"{BASE_URL}/trending/movie/week?api_key={API_KEY}")
    return [{'id': m['id'], 'title': m['title']} for m in response.json()['results'][:10]]

def fetch_upcoming_movies():
    response = requests.get(f"{BASE_URL}/movie/upcoming?api_key={API_KEY}")
    return [{'id': m['id'], 'title': m['title']} for m in response.json()['results'][:10]]

def recommend(movie_title):
    try:
        idx = movies[movies['title'] == movie_title].index[0]
        sim_scores = list(enumerate(similarity[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:6]
        return [movies.iloc[i[0]].movie_id for i in sim_scores]
    except:
        return []

# -------------------- Custom Styling --------------------
def inject_custom_style():
    st.markdown("""
    <style>
    :root {
        --primary: #00ff9d;
        --secondary: #0066ff;
        --bg: #0a0a0f;
        --surface: #161622;
        --text: #e0e0e0;
        --border: rgba(255,255,255,0.1);
    }

    * {
        font-family: 'Inter', sans-serif;
    }

    body {
        background: var(--bg);
        color: var(--text);
    }

    .stApp {
        background: linear-gradient(180deg, var(--bg) 0%, #000000 100%);
    }

    .movie-card {
        background: var(--surface);
        border-radius: 16px;
        border: 1px solid var(--border);
        padding: 1.5rem;
        margin: 1rem 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(0, 255, 157, 0.1);
    }

    .stAlertContainer {
        display: none;
    }

    .stSelectbox div[data-baseweb="select"] {
        background: var(--surface);
        border-color: var(--border) !important;
        color: var(--text) !important;
    }

    .stButton button {
        background: linear-gradient(45deg, var(--primary), var(--secondary)) !important;
        border: none !important;
        color: black !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }

    .stButton button:hover {
        opacity: 0.9 !important;
        transform: scale(1.02) !important;
    }

    .stTabs [aria-selected="true"] {
        color: var(--primary) !important;
        border-bottom: 2px solid var(--primary) !important;
    }

    .genre-tag {
        display: inline-block;
        padding: 4px 12px;
        background: rgba(0, 255, 157, 0.1);
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 4px 2px;
        border: 1px solid var(--primary);
    }

    .review-card {
        background: rgba(255,255,255,0.05);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid var(--primary);
    }

    .trailer-container {
        border-radius: 12px;
        overflow: hidden;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------- App Setup --------------------
st.set_page_config(page_title="CineVerse", page_icon="🎬", layout="wide")
inject_custom_style()

# -------------------- Header --------------------
st.markdown("""
<div style="text-align:center; padding:4rem 0 3rem;">
    <h1 style="font-size:3.5rem; margin:0; 
    background:linear-gradient(45deg, #00ff9d, #0066ff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
        CineVerse
    </h1>
    <p style="opacity:0.8; font-size:1.1rem;">
        Discover Your Next Favorite Movie • Powered by TMDb
    </p>
</div>
""", unsafe_allow_html=True)

# -------------------- Main Content --------------------
tabs = st.tabs(["🎬 Recommendations", "🔥 Trending Now", "📅 Coming Soon", "⭐ Popular Picks"])

with tabs[0]:
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_movie = st.selectbox("Select a movie you enjoy:", movies['title'].values)
    with col2:
        st.write("\n")
        generate_btn = st.button("Generate Recommendations")

    if generate_btn:
        with st.spinner("Analyzing cinematic patterns..."):
            movie_ids = recommend(selected_movie)

        st.subheader(f"Because you liked {selected_movie}", divider="rainbow")

        cols = st.columns(5)
        for idx, movie_id in enumerate(movie_ids):
            details = fetch_movie_details(movie_id)
            if details:
                with cols[idx % 5]:
                    with st.container():
                        st.markdown("<div class='movie-card'>", unsafe_allow_html=True)

                        if details['poster']:
                            st.image(details['poster'], use_column_width=True)

                        st.markdown(f"{details['title']}")
                        st.caption(f"⭐ {details['rating']} • {details['runtime']} mins")

                        if details['genres']:
                            st.markdown("".join([f"<span class='genre-tag'>{g}</span>" for g in details['genres'][:3]]),
                                        unsafe_allow_html=True)

                        with st.expander("More Details"):
                            if details['director']:
                                st.markdown("🎬 **Director**")
                                st.markdown(f"<div style='margin-bottom:1.5rem;'>{details['director']}</div>", unsafe_allow_html=True)

                            st.markdown("🌟 **Top Cast**")
                            st.markdown("<div style='margin-bottom:1.5rem;'>" + "<br>".join(details['cast']) + "</div>", unsafe_allow_html=True)

                            if details['reviews']:
                                st.write("*Top Reviews:*")
                                for review in details['reviews']:
                                    st.markdown(f"<div class='review-card'>{review[:200]}...</div>", unsafe_allow_html=True)

                            if details['trailer']:
                                st.markdown(f"""
                                <div class='trailer-container'>
                                    <iframe width="100%" height="200" 
                                    src="https://www.youtube.com/embed/{details['trailer']}" 
                                    frameborder="0" 
                                    allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" 
                                    allowfullscreen>
                                    </iframe>
                                </div>
                                """, unsafe_allow_html=True)

                        st.markdown("</div>", unsafe_allow_html=True)

# Trending Now Tab
with tabs[1]:
    with st.spinner("Loading trending movies..."):
        trending_movies = fetch_trending_movies()

    st.subheader("🔥 Trending This Week", divider="rainbow")
    cols = st.columns(5)
    for idx, movie in enumerate(trending_movies[:10]):
        details = fetch_movie_details(movie['id'])
        if details:
            with cols[idx % 5]:
                with st.container():
                    st.markdown("<div class='movie-card'>", unsafe_allow_html=True)
                    if details['poster']:
                        st.image(details['poster'], use_column_width=True)
                    st.markdown(f"{details['title']}")
                    st.caption(f"⭐ {details['rating']} • {details['runtime']} mins")
                    st.markdown("</div>", unsafe_allow_html=True)

# Coming Soon Tab
with tabs[2]:
    with st.spinner("Loading upcoming releases..."):
        upcoming_movies = fetch_upcoming_movies()

    st.subheader("📅 Coming Soon to Theaters", divider="rainbow")
    cols = st.columns(5)
    for idx, movie in enumerate(upcoming_movies[:10]):
        details = fetch_movie_details(movie['id'])
        if details:
            with cols[idx % 5]:
                with st.container():
                    st.markdown("<div class='movie-card'>", unsafe_allow_html=True)
                    if details['poster']:
                        st.image(details['poster'], use_column_width=True)
                    st.markdown(f"{details['title']}")
                    st.caption(f"⭐ {details['rating']} • {details['runtime']} mins")
                    st.markdown("</div>", unsafe_allow_html=True)

# Popular Picks Tab
with tabs[3]:
    with st.spinner("Loading popular movies..."):
        popular_movies = fetch_popular_movies()

    st.subheader("⭐ Currently Popular", divider="rainbow")
    cols = st.columns(5)
    for idx, movie in enumerate(popular_movies[:10]):
        details = fetch_movie_details(movie['id'])
        if details:
            with cols[idx % 5]:
                with st.container():
                    st.markdown("<div class='movie-card'>", unsafe_allow_html=True)
                    if details['poster']:
                        st.image(details['poster'], use_column_width=True)
                    st.markdown(f"{details['title']}")
                    st.caption(f"⭐ {details['rating']} • {details['runtime']} mins")
                    st.markdown("</div>", unsafe_allow_html=True)

# -------------------- Footer --------------------
st.markdown("""
<div style="text-align:center; padding:3rem 0 2rem; opacity:0.8;">
    <hr style="border-color:var(--border);">
    <p style="font-size:0.9rem;">
        Powered by TMDb API • Data refreshes every 24 hours
    </p>
</div>
""", unsafe_allow_html=True)
