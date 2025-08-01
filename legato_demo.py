import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st
import os

# --- CONFIGURAÇÕES ---
CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET", "")
REDIRECT_URI = "https://legato-top10tracks.streamlit.app"
SCOPE = "user-top-read user-library-read user-read-recently-played"

# --- SETUP DO APP ---
st.set_page_config(page_title="Legato - Spotify", layout="wide")
st.title("🎵 Legato - Suas 10 músicas mais tocadas")

# --- AUTENTICAÇÃO ---
auth_manager = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    show_dialog=True,               # Garante que usuário sempre veja a tela de login
    open_browser=False              # Evita erro de browser em ambiente web
)

# Gerencia o token automaticamente
if not auth_manager.get_cached_token():
    auth_url = auth_manager.get_authorize_url()
    st.markdown(f"[👉 Clique aqui para autenticar com o Spotify]({auth_url})")
    st.stop()

# Tenta obter o token (Spotipy gerencia a troca do code por token)
token_info = auth_manager.get_access_token(as_dict=False)
sp = spotipy.Spotify(auth=token_info)

# --- OBTÉM TOP TRACKS ---
top_tracks = sp.current_user_top_tracks(limit=10, time_range="short_term")

st.subheader("🎧 Suas Top 10 Músicas")

for i, item in enumerate(top_tracks["items"], 1):
    track_name = item["name"]
    album_name = item["album"]["name"]
    artists = ", ".join([artist["name"] for artist in item["artists"]])
    release_date = item["album"]["release_date"]
    duration_ms = item["duration_ms"]
    popularity = item["popularity"]
    image_url = item["album"]["images"][0]["url"]
    spotify_url = item["external_urls"]["spotify"]

    st.markdown(f"### {i}º Lugar")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(image_url, width=250)
    with col2:
        st.markdown(f"**Música:** [{track_name}]({spotify_url})")
        st.markdown(f"**Álbum:** {album_name}")
        st.markdown(f"**Artistas:** {artists}")
        st.markdown(f"**Lançamento:** {release_date}")
        st.markdown(f"**Duração (ms):** {duration_ms}")
        st.markdown(f"**Popularidade:** {popularity}")
    st.markdown("---")
