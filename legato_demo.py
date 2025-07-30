import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import streamlit as st
import requests
import os
import urllib.parse
import base64

# Recomendado: use variáveis de ambiente para segurança (especialmente em produção)
CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID", "")  # ou coloque diretamente: "sua_client_id"
CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET", "")  # ou diretamente: "seu_client_secret"
REDIRECT_URI = 'https://legato-top10tracks.streamlit.app/callback'

# Geração do link de autenticação
params = {
    "client_id": CLIENT_ID,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": 'user-top-read user-library-read user-read-recently-played user-read-playback-state user-modify-playback-state'
}
auth_url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"

# Configuração da interface
st.set_page_config(
    page_title="Legato - Spotify Top Tracks Analysis",
    page_icon=":musical_note:",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Analise seu Top 10 Músicas Favoritas no Spotify")
st.write("Esta aplicação permite que você visualize e analise suas 10 músicas mais tocadas no Spotify, incluindo nome da música, álbum, artistas, data de lançamento, duração e popularidade.")

# Pegando parâmetros da URL
query_params = st.query_params()

# Se não tiver código, mostra botão de login
if "code" not in query_params:
    st.markdown(f"[Clique aqui para autenticar com o Spotify]({auth_url})")
    st.stop()

# Troca do código por token de acesso
code = query_params["code"][0]
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

# Faz a requisição para obter token
token_response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)

# Se falhar, interrompe e exibe erro
if token_response.status_code != 200:
    st.error("Erro ao obter o token de acesso do Spotify.")
    st.stop()

# Recupera o token
access_token = token_response.json().get("access_token")

# Inicializa cliente Spotify com o token manualmente
sp = spotipy.Spotify(auth=access_token)

# Coleta das Top Tracks
top_tracks = sp.current_user_top_tracks(limit=10, time_range='short_term')
track_ids = [track['id'] for track in top_tracks['items']]

st.write("### Suas Top 10 Músicas mais tocadas")
for i, item in enumerate(top_tracks['items'], 1):
    st.subheader(f"{i}º Lugar")

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
