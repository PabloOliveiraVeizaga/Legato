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

# --- CAPTURA DE QUERY PARAMS ---
query_params = st.query_params
code = query_params.get("code", [None])[0]

# --- AUTENTICAÇÃO ---
sp = spotipy.Spotify(
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        show_dialog=True,               # Garante que usuário sempre veja a tela de login
        open_browser=False              # Evita erro de browser em ambiente web
    )
)
auth_manager = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    show_dialog=True,               # Garante que usuário sempre veja a tela de login
    open_browser=False              # Evita erro de browser em ambiente web
)

# --- FLUXO: JÁ TEMOS TOKEN EM SESSÃO? ---
if "token_info" not in st.session_state:
    if code:
        # Trocar o code por um token
        token_info = auth_manager.get_access_token(code, as_dict=True)
        st.session_state.token_info = token_info
    else:
        # Gera o link de autenticação
        auth_url = auth_manager.get_authorize_url()
        st.markdown(f"[👉 Clique aqui para autenticar com o Spotify]({auth_url})")
        st.stop()

# --- INSTANCIA O CLIENTE SPOTIPY ---
access_token = st.session_state.token_info["access_token"]
sp = spotipy.Spotify(auth=access_token)

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
