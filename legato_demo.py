import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st
import requests
import os
import urllib.parse
import base64

# --- CONFIGURAÇÕES ---
CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET", "")
REDIRECT_URI = 'https://legato-top10tracks.streamlit.app'
SCOPE = 'user-top-read user-library-read user-read-recently-played'

# --- LINK DE AUTENTICAÇÃO ---
auth_manager = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
)
auth_url = auth_manager.get_authorize_url()

# --- LAYOUT ---
st.set_page_config(page_title="Legato - Spotify", layout="wide")
st.title("🎵 Legato - Suas 10 músicas mais tocadas")
query_params = st.query_params

# --- FLUXO: se ainda não há code, mostrar link para autenticar ---
if "code" not in query_params:
    st.markdown(f"[👉 Clique aqui para autenticar com o Spotify]({auth_url})")
    st.stop()

# --- OBTÉM CODE DA URL ---
code = query_params["code"]

# --- TROCA DE CODE POR ACCESS TOKEN via requests ---
auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
b64_auth_str = base64.b64encode(auth_str.encode()).decode()

headers = {
    "Authorization": f"Basic {b64_auth_str}",
    "Content-Type": "application/x-www-form-urlencoded"
}
data = {
    "grant_type": "authorization_code",
    "code": code,
    "redirect_uri": REDIRECT_URI
}

response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)

if response.status_code != 200:
    st.error("❌ Erro ao obter o token de acesso do Spotify.")
    st.write("Status:", response.status_code)
    st.write("Resposta:", response.json())
    st.stop()

# --- PEGA ACCESS TOKEN E CRIA INSTÂNCIA DO SPOTIFY COM ELE ---
access_token = response.json().get("access_token")
sp = spotipy.Spotify(auth=access_token)

# --- OBTÉM TOP TRACKS ---
top_tracks = sp.current_user_top_tracks(limit=10, time_range="short_term")

# --- EXIBIÇÃO DAS MÚSICAS ---
st.subheader("🎧 Suas Top 10 Músicas das ultimas quatro semanas!")

for i, item in enumerate(top_tracks['items'], 1):
    track_name = item['name']
    album_name = item['album']['name']
    artists = ', '.join([artist['name'] for artist in item['artists']])
    release_date = item['album']['release_date']
    duration_ms = item['duration_ms']
    popularity = item['popularity']
    image_url = item['album']['images'][0]['url']
    spotify_url = item['external_urls']['spotify']

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

top_tracks = sp.current_user_top_tracks(limit=10, time_range="medium_term")

# --- EXIBIÇÃO DAS MÚSICAS ---
st.subheader("🎧 Suas Top 10 Músicas dos ultimos seis meses!")

for i, item in enumerate(top_tracks['items'], 1):
    track_name = item['name']
    album_name = item['album']['name']
    artists = ', '.join([artist['name'] for artist in item['artists']])
    release_date = item['album']['release_date']
    duration_ms = item['duration_ms']
    popularity = item['popularity']
    image_url = item['album']['images'][0]['url']
    spotify_url = item['external_urls']['spotify']

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
