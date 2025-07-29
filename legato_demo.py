import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import pandas as pd
import streamlit as st
import os

SPOTIPY_CLIENT_ID = "418bc0b18e11485589d6898e5530c0df"
SPOTIPY_CLIENT_SECRET = "500b4a2a865e4b748c65bf48c1cf4b3f"
REDIRECT_URI = 'https://legato-top10tracks.streamlit.app/callback'

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope='user-top-read user-library-read user-read-recently-played user-read-playback-state user-modify-playback-state'
    )
)

st.set_page_config(
    page_title="Legato - Spotify Top Tracks Analysis",
    page_icon=":musical_note:",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("Analise seu Top 10 Músicas Favoritas no Spotify")
st.write("Esta aplicação permite que você visualize e analise suas 10 músicas mais tocadas no Spotify, incluindo informações como nome da música, álbum, artistas, data de lançamento, duração, popularidade.")
url = "https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri=https%3A%2F%2Flegato-top10tracks.streamlit.app&scope=user-top-read+user-library-read+user-read-recently-played+user-read-playback-state+user-modify-playback-state"
st.markdown("Clique nesse link para fazer a autorização [link](%s)" % url)

top_tracks = sp.current_user_top_tracks(limit=10, time_range='short_term')
track_ids = [track['id'] for track in top_tracks['items']]
i = 1
st.write("### Suas Top 10 Músicas mais tocadas")

for item in top_tracks['items']:
    st.subheader(f"{i}º Lugar")
    i += 1
    track_name = item['name']
    album_name = item['album']['name']
    artist_names = ', '.join(artist['name'] for artist in item['artists'])
    release_date = item['album']['release_date']
    track_image = item['album']['images'][0]['url'] if item['album']['images'] else 'No image available'
    track_url = item['external_urls']['spotify']
    preview_url = item.get('preview_url', 'No preview available')
    duration_ms = item['duration_ms']
    popularity = item['popularity']

    col1, col2 = st.columns([1, 3])

    with col1:
        st.image(track_image, width=300)

    with col2:
        st.markdown(f"**Música:** [{track_name}]({track_url})")
        st.markdown(f"**Álbum:** {album_name}")
        st.markdown(f"**Artista:** {artist_names}")
        st.markdown(f"**Data de Lançamento:** {release_date}")
        st.markdown(f"**Duração (ms):** {duration_ms}")
        st.markdown(f"**Popularidade:** {popularity}")

    st.markdown("---")
