import streamlit as st
import requests
import pickle
import pandas as pd
import gdown
import os

# TMDb API Configuration
API_KEY = 'c9cb5ec336fa36659fbba0ba516298dc'
BASE_URL = 'https://api.themoviedb.org/3'

# -------------------- Download similarity.pkl from Google Drive --------------------
def download_similarity_file():
    file_id = '1yz5J_bO6YhwsNnDakBR7WFQPWwhjUX_j'
    output_path = 'similarity.pkl'
    if not os.path.exists(output_path):
        try:
            gdown.download_file_from_google_drive(file_id=file_id, dest_path=output_path, quiet=False)
            st.success("similarity.pkl downloaded successfully.")
        except Exception as e:
            st.error("❌ Failed to download similarity.pkl. Make sure the file is shared publicly (anyone with the link can view).")
            st.stop()

download_similarity_file()

# -------------------- Data Loading --------------------
try:
    movies = pd.DataFrame(pickle.load(open('movie_dict1.pkl', 'rb')))
    with open('similarity.pkl', 'rb') as f:
        similarity = pickle.load(f)
except Exception as e:
    st.error("❌ Failed to load required files. Please ensure `movie_dict1.pkl` and `similarity.pkl` are available.")
    st.stop()

# -------------------- Helper Functions --------------------
def fetch_poster(movie_id):
    try:
        response = requests.get(f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}")
        data = response.json()
        return f"https://image.tmdb.org/t/p/w500/{data['poster_path']}" if data.get('poster_path') else None
    except:
        return None

def get_trailer_key(movie_id):
    try:
        videos = requests.get(f"{BASE_URL}/movie/{movie_id}/videos?api_key={API_KEY}").json()
        return next((v['key'] for v in videos['results'] if v['type'] == 'Trailer' and v['site'] == 'YouTube'), None)
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

# -------------------- App Setup --------------------
st.set_page_config(page_title="CineVerse", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #0a0a0f;
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    .movie-card {
        background: #161622;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.1);
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .genre-tag {
        background: rgba(0, 255, 157, 0.1);
        padding: 4px 12px;
        border-radius: 20px;
        border: 1px solid #00ff9d;
        font-size: 0.8rem;
        display: inline-block;
        margin: 4px 2px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding:4rem 0 2rem;">
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

tabs = st.tabs(["🎬 Recommendations", "🔥 Trending", "📅 Upcoming", "⭐ Popular"])

with tabs[0]:
    selected_movie = st.selectbox("🎞️ Select a movie you liked:", movies['title'].values)
    if st.button("🎯 Recommend"):
        with st.spinner("Finding your next favorites..."):
            recommended_ids = recommend(selected_movie)

        if not recommended_ids:
            st.warning("Couldn't find recommendations for this movie.")
        else:
            st.subheader(f"Because you liked *{selected_movie}*:")
            cols = st.columns(5)
            for i, movie_id in enumerate(recommended_ids):
                details = fetch_movie_details(movie_id)
                if details:
                    with cols[i % 5]:
                        st.markdown(f"<div class='movie-card'>", unsafe_allow_html=True)
                        if details['poster']:
                            st.image(details['poster'], use_column_width=True)
                        st.markdown(f"**{details['title']}**")
                        st.caption(f"⭐ {details['rating']} • {details['runtime']} mins")
                        st.markdown("".join([f"<span class='genre-tag'>{g}</span>" for g in details['genres'][:3]]),
                                    unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)

# Other Tabs (Trending, Upcoming, Popular)
tabs_data = [
    ("🔥 Trending This Week", fetch_trending_movies),
    ("📅 Coming Soon", fetch_upcoming_movies),
    ("⭐ Popular Picks", fetch_popular_movies)
]

for i in range(1, 4):
    with tabs[i]:
        with st.spinner("Fetching movies..."):
            movies_list = tabs_data[i - 1][1]()
        st.subheader(tabs_data[i - 1][0])
        cols = st.columns(5)
        for idx, movie in enumerate(movies_list):
            details = fetch_movie_details(movie['id'])
            if details:
                with cols[idx % 5]:
                    st.markdown("<div class='movie-card'>", unsafe_allow_html=True)
                    if details['poster']:
                        st.image(details['poster'], use_column_width=True)
                    st.markdown(f"**{details['title']}**")
                    st.caption(f"⭐ {details['rating']} • {details['runtime']} mins")
                    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center; padding:3rem 0 2rem; opacity:0.8;">
    <hr style="border-color:rgba(255,255,255,0.1);">
    <p style="font-size:0.9rem;">
        🚀 Built with TMDb API • Updated daily
    </p>
</div>
""", unsafe_allow_html=True)
