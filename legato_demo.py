import streamlit as st
import requests
import urllib.parse
import pandas as pd
import base64

# ======================
# CONFIGURAÇÕES SPOTIFY
# ======================
CLIENT_ID = "418bc0b18e11485589d6898e5530c0df"
CLIENT_SECRET = "500b4a2a865e4b748c65bf48c1cf4b3f"
REDIRECT_URI = 'https://legato-top10tracks.streamlit.app'

SCOPE = "user-top-read user-library-read user-read-recently-played user-read-playback-state user-modify-playback-state"

# ============
# FUNÇÕES
# ============

def get_auth_url():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE
    }
    return f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"

def exchange_code_for_token(code):
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

    if response.status_code == 200:
        return response.json()
    else:
        st.error("Erro ao trocar código por token.")
        return None

def get_top_tracks(token):
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://api.spotify.com/v1/me/top/tracks?limit=10&time_range=short_term"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        st.error("Erro ao buscar Top Tracks.")
        return None

# ======================
# INTERFACE STREAMLIT
# ======================

st.set_page_config(
    page_title="Legato - Spotify Top Tracks Analysis",
    page_icon="🎵",
    layout="wide"
)

st.title("🎶 Analise suas 10 músicas favoritas no Spotify")

query_params = st.query_params

# 1. Se não tiver ?code na URL, mostrar botão de login
if "code" not in query_params:
    st.markdown("Para continuar, é necessário autorizar o acesso à sua conta Spotify.")
    auth_url = get_auth_url()
    st.markdown(f"👉 [Clique aqui para autenticar com o Spotify]({auth_url})")
    st.stop()

# 2. Se tiver código, troque por token
code = query_params["code"]
token_info = exchange_code_for_token(code)

if token_info and "access_token" in token_info:
    access_token = token_info["access_token"]
    top_tracks = get_top_tracks(access_token)

    if top_tracks:
        st.write("### 🎧 Suas Top 10 Músicas")

        for i, item in enumerate(top_tracks['items'], start=1):
            track_name = item['name']
            album_name = item['album']['name']
            artist_names = ', '.join(artist['name'] for artist in item['artists'])
            release_date = item['album']['release_date']
            track_image = item['album']['images'][0]['url'] if item['album']['images'] else ''
            track_url = item['external_urls']['spotify']
            duration_ms = item['duration_ms']
            popularity = item['popularity']

            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(track_image, width=250)

            with col2:
                st.subheader(f"{i}º Lugar - [{track_name}]({track_url})")
                st.markdown(f"**Álbum:** {album_name}")
                st.markdown(f"**Artistas:** {artist_names}")
                st.markdown(f"**Data de Lançamento:** {release_date}")
                st.markdown(f"**Duração (ms):** {duration_ms}")
                st.markdown(f"**Popularidade:** {popularity}")
            st.markdown("---")
