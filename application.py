# import numpy as np
# import pandas as pd
# import streamlit as st
# import requests
# import pickle
# import base64

# # TMDb API key
# API_KEY = 'c9cb5ec336fa36659fbba0ba516298dc'

# # Function to fetch the poster from TMDb API
# def fetch_poster(movie_id):

#     url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
#     response = requests.get(url)
#     data = response.json()
#     full_path = "https://image.tmdb.org/t/p/w500/" + data['poster_path']
#     return full_path

# # Function to fetch popular movies from TMDb API
# def fetch_popular_movies():
#     url = f'https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=en-US'
#     response = requests.get(url)
#     data = response.json()

#     popular_movies = []
#     for movie in data['results'][:10]:  # Limit to 10 movies
#         popular_movies.append({
#             'title': movie['title'],
#             'poster_path': movie['poster_path'],
#             'overview': movie['overview']
#         })
    
#     return popular_movies


# # Function to fetch the YouTube trailer from TMDb API
# def fetch_trailer(movie_id):
#     url = f'https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}&language=en-US'
#     response = requests.get(url)
#     data = response.json()
    
#     trailers = [video for video in data['results'] if video['site'] == 'YouTube' and video['type'] == 'Trailer']
    
#     if trailers:
#         return trailers[0]['key']  # Return the YouTube key for embedding
#     return None

# def fetch_upcoming_movies():
#     url = f'https://api.themoviedb.org/3/movie/upcoming?api_key={API_KEY}&language=en-US'
#     response = requests.get(url)
#     data = response.json()

#     upcoming_movies = []
#     for movie in data['results'][:10]:  # Limit to 10 movies
#         upcoming_movies.append({
#             'title': movie['title'],
#             'poster_path': movie['poster_path'],
#             'overview': movie['overview']
#         })
    
#     return upcoming_movies

# # Function to fetch trending movies from TMDb API
# def fetch_trending_movies():
#     url = f'https://api.themoviedb.org/3/trending/movie/week?api_key={API_KEY}&language=en-US'
#     response = requests.get(url)
#     data = response.json()

#     trending_movies = []
#     for movie in data['results'][:10]:  # Limit to 10 movies
#         trending_movies.append({
#             'title': movie['title'],
#             'poster_path': movie['poster_path'],
#             'overview': movie['overview']
#         })
    
#     return trending_movies


# # Function to fetch movie details (director, cast, reviews)
# def fetch_movie_details(movie_id):
#     url_credits = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}&language=en-US'
#     response_credits = requests.get(url_credits)
#     credits_data = response_credits.json()

#     url_reviews = f'https://api.themoviedb.org/3/movie/{movie_id}/reviews?api_key={API_KEY}&language=en-US'
#     response_reviews = requests.get(url_reviews)
#     reviews_data = response_reviews.json()

#     director = next((crew_member['name'] for crew_member in credits_data['crew'] if crew_member['job'] == 'Director'), None)
#     cast_list = [cast_member['name'] for cast_member in credits_data['cast'][:5]]
#     reviews = [review['content'] for review in reviews_data['results'][:3]]

#     return director, cast_list, reviews

# def set_background(image_file):
#     with open(image_file, "rb") as image:
#         encoded_string = base64.b64encode(image.read()).decode()

#     bg_img = f"""
#     <style>
#     .stApp {{
#         background-image: url("data:image/png;base64,{encoded_string}");
#         background-size: cover;
#         background-position: center;
#         background-attachment: fixed;
#     }}
#     </style>
#     """
#     st.markdown(bg_img, unsafe_allow_html=True)

# # Call the function to set background image
# set_background("netflix_1.jpg")

# # Function to get movie recommendations and their posters
# def recommend(movie):
#     index = movies[movies['title'] == movie].index[0]
#     distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
#     recommended_movie_names = []
#     recommended_movie_posters = []
#     recommended_movie_ids = []

#     for i in distances[1:6]:
#         movie_id = movies.iloc[i[0]].movie_id    
#         recommended_movie_ids.append(movie_id)
#         recommended_movie_names.append(movies.iloc[i[0]].title)
#         recommended_movie_posters.append(fetch_poster(movie_id))

#     return recommended_movie_names, recommended_movie_posters, recommended_movie_ids

# # Load the saved movie data
# movies_dict = pickle.load(open('movie_dict1.pkl', 'rb')) 
# movies = pd.DataFrame(movies_dict)

# # Load the similarity model
# similarity = pickle.load(open('similarity.pkl', 'rb'))

# # Function to get background image
# def get_img_as_base64(file):
#     with open(file, "rb") as f:
#         data = f.read()
#     return base64.b64encode(data).decode()


# # Main app title
# st.markdown('<h1 style="color:#FFFFFF;text-align:center;">Movie Recommendation System</h1>', unsafe_allow_html=True)

# # Tabs for interactive sections
# tab1, tab2, tab3, tab4 = st.tabs(["Recommendations", "Popular", "Trending", "Upcoming"])

# # Recommendations Tab
# with tab1:
#     selected_movie_name = st.selectbox("Choose a Movie You Like:", movies['title'].values)

#     if st.button("Get Recommendations"):
#         recommended_names, recommended_posters, recommended_movie_ids = recommend(selected_movie_name)
        
#         st.markdown('<h2 style="color:#FFFFFF;">Recommended Movies</h2>', unsafe_allow_html=True)
        
#         for i in range(len(recommended_names)):
#             with st.container():
#                 col1, col2 = st.columns([1, 2])
#                 with col1:
#                     st.image(recommended_posters[i], width=150)
#                 with col2:
#                     st.markdown(f"<h3 style='color: #FFFFFF;'>{recommended_names[i]}</h3>", unsafe_allow_html=True)
                
#                     youtube_key = fetch_trailer(recommended_movie_ids[i])
#                     if youtube_key:
#                         st.markdown(
#                             f'<iframe width="80%" height="180" src="https://www.youtube.com/embed/{youtube_key}" frameborder="0" allowfullscreen></iframe>',
#                             unsafe_allow_html=True)
                    
#                     director, cast, reviews = fetch_movie_details(recommended_movie_ids[i])
#                     st.markdown(f"<div><strong>Director:</strong> {director}</div>", unsafe_allow_html=True)
#                     st.markdown(f"<div><strong>Cast:</strong> {', '.join(cast)}</div>", unsafe_allow_html=True)
                    
#                     if reviews:
#                         st.markdown("<strong>User Reviews:</strong>", unsafe_allow_html=True)
#                         for review in reviews:
#                             st.markdown(f"<div style='background-color: rgba(0, 0, 0, 0.45);'>{review}</div>", unsafe_allow_html=True)

# # Popular Movies Tab
# with tab2:
#     if st.button("Show Popular Movies"):
#         popular_movies = fetch_popular_movies()
#         for movie in popular_movies[:10]:
#             with st.expander(movie['title']):
#                 st.image(f"https://image.tmdb.org/t/p/w500/{movie['poster_path']}", width=150)
#                 st.write(movie['overview'])

# # Trending Movies Tab
# with tab3:
#     if st.button("Show Trending Movies"):
#         trending_movies = fetch_trending_movies()
#         for movie in trending_movies[:10]:
#             with st.expander(movie['title']):
#                 st.image(f"https://image.tmdb.org/t/p/w500/{movie['poster_path']}", width=150)
#                 st.write(movie['overview'])

# # Upcoming Movies Tab
# with tab4:
#     if st.button("Show Upcoming Movies"):
#         upcoming_movies = fetch_upcoming_movies()
#         for movie in upcoming_movies[:10]:
#             with st.expander(movie['title']):
#                 st.image(f"https://image.tmdb.org/t/p/w500/{movie['poster_path']}", width=150)
#                 st.write(movie['overview'])



# ----------------------------------------------------

import numpy as np
import pandas as pd
import streamlit as st
import requests
import pickle
import base64
import time  # For animations

# TMDb API key
API_KEY = 'c9cb5ec336fa36659fbba0ba516298dc'

# Function to fetch movie poster
def fetch_poster(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
    response = requests.get(url).json()
    return f"https://image.tmdb.org/t/p/w500/{response['poster_path']}"

# Function to set the background image
def set_background(image_file):
    with open(image_file, "rb") as image:
        encoded_string = base64.b64encode(image.read()).decode()

    bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded_string}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-blend-mode: darken;
    }}
    </style>
    """
    st.markdown(bg_img, unsafe_allow_html=True)

# Apply background image
set_background("netflix_1.jpg")

# Custom CSS for stylish UI
st.markdown("""
    <style>
        h1 { text-align: center; font-size: 48px; color: #ffcc00; text-shadow: 2px 2px 8px #000; }
        .movie-card { border-radius: 10px; background-color: rgba(255, 255, 255, 0.1); padding: 15px; text-align: center; transition: 0.3s; }
        .movie-card:hover { transform: scale(1.05); box-shadow: 0px 0px 20px rgba(255, 255, 255, 0.5); }
        .movie-title { color: #FFFFFF; font-size: 22px; font-weight: bold; }
        .movie-desc { color: #cccccc; font-size: 14px; }
        .stButton > button { background-color: #ffcc00; color: black; font-size: 18px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# Load movie data and similarity model
movies_dict = pickle.load(open('movie_dict1.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Function to get movie recommendations
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movies = [
        {
            'title': movies.iloc[i[0]].title,
            'poster_path': fetch_poster(movies.iloc[i[0]].movie_id),
            'movie_id': movies.iloc[i[0]].movie_id
        }
        for i in distances[1:6]
    ]
    return recommended_movies

# Main app title
st.markdown('<h1>🎬 Movie Recommendation System 🍿</h1>', unsafe_allow_html=True)

# Tabs for sections
tab1, tab2 = st.tabs(["✨ Recommendations", "🔥 Popular Movies"])

# Recommendations Tab
with tab1:
    selected_movie = st.selectbox("Choose a Movie You Like:", movies['title'].values)

    if st.button("🔍 Get Recommendations"):
        with st.spinner("✨ Finding the best movies for you..."):
            time.sleep(2)  # Simulating a delay
        recommended_movies = recommend(selected_movie)

        st.markdown('<h2 style="color:#FFFFFF;">Recommended Movies for You 🎥</h2>', unsafe_allow_html=True)

        # Display in a grid format
        col1, col2, col3 = st.columns(3)
        columns = [col1, col2, col3]
        
        for idx, movie in enumerate(recommended_movies):
            with columns[idx % 3]:  # Distribute in 3 columns
                st.markdown(f"""
                    <div class="movie-card">
                        <img src="{movie['poster_path']}" width="100%">
                        <p class="movie-title">{movie['title']}</p>
                        <p class="movie-desc">⭐ ⭐ ⭐ ⭐ (4.5/5)</p>
                    </div>
                """, unsafe_allow_html=True)

# Popular Movies Tab
with tab2:
    if st.button("🔥 Show Popular Movies"):
        url = f'https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=en-US'
        response = requests.get(url).json()
        popular_movies = response['results'][:6]  # Get top 6

        col1, col2, col3 = st.columns(3)
        columns = [col1, col2, col3]

        for idx, movie in enumerate(popular_movies):
            with columns[idx % 3]:  # Distribute in 3 columns
                st.markdown(f"""
                    <div class="movie-card">
                        <img src="https://image.tmdb.org/t/p/w500/{movie['poster_path']}" width="100%">
                        <p class="movie-title">{movie['title']}</p>
                        <p class="movie-desc">{movie['overview'][:100]}...</p>
                    </div>
                """, unsafe_allow_html=True)

