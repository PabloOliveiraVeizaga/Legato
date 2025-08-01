import spotipy
import streamlit as st
import requests
import os
import urllib.parse
import base64

# --- CONFIGURAÇÕES ---
CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET", "")
REDIRECT_URI = "https://legato-top10tracks.streamlit.app"

sp = spotipy.Spotify(
    auth=SpotifyOAuth(
        client_id= CLIENT_ID,
        client_secret= CLIENT_SECRET,
        redirect_uri= REDIRECT_URI,
        scope= 'user-top-read user-library-read user-read-recently-played'
    )
)

# --- LINK DE AUTENTICAÇÃO ---
params = {
    "client_id": CLIENT_ID,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": "user-top-read user-library-read user-read-recently-played"
}
auth_url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"

# --- LAYOUT ---
st.set_page_config(page_title="Legato - Spotify", layout="wide")
st.title("🎵 Legato - Suas 10 músicas mais tocadas")
query_params = st.query_params

# --- FLUXO ---
if "code" not in query_params:
    st.markdown(f"[👉 Clique aqui para autenticar com o Spotify]({auth_url})")
    st.stop()

# --- TROCA DE CODE POR TOKEN ---
code = query_params["code"][0]

# Preparar cabeçalho de autenticação
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

# Requisição de token
token_response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)

st.write(os.environ)

if token_response.status_code != 200:
    st.error("❌ Erro ao obter o token de acesso do Spotify.")
    st.write("Status:", token_response.status_code)
    st.write("Resposta:", token_response.json())
    st.stop()

# 🔄 Limpar a URL após sucesso
st.query_params

# Usar o token
access_token = token_response.json()["access_token"]

# --- OBTÉM TOP TRACKS ---
top_tracks = sp.current_user_top_tracks(limit=10, time_range="short_term")

st.subheader("🎧 Suas Top 10 Músicas")

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
