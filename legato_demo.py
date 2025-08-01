import streamlit as st
import requests
import spotipy
import os
import base64
import urllib.parse

# --- CONFIGURAÇÕES ---
CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET", "")
REDIRECT_URI = "https://legato-top10tracks.streamlit.app"
SCOPE = "user-top-read user-library-read user-read-recently-played"
CODE = "AQBSm53MBlONcSXEnxV8u55f88hCNEdottZxEAtdoCjONe57O5d4DQsTURb8Loocxgt9O-3jWupha3sbrRkePwVVfmHGhyI1Im2RS-iuTEWlHs0fZP8Pea3IsB0qxney3WWcy9CHrISStEgEs3dwbNO0jOc5Rg_xeJMQh2_BehWuurKdgbYnzTHBlfHMXqLhrMmx2VKWTF1xC90DlYUT5K7iGXzAmsIkPqSJLyP4pMB139GAnapTILQDaC7UIsCl-8NdJXadgJQI"

# Montar cabeçalho de autorização
auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
b64_auth_str = base64.b64encode(auth_str.encode()).decode()

headers = {
    "Authorization": f"Basic {b64_auth_str}",
    "Content-Type": "application/x-www-form-urlencoded"
}

data = {
    "grant_type": "authorization_code",
    "code": CODE,
    "redirect_uri": REDIRECT_URI
}

response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)

print("Status:", response.status_code)
print("Resposta:", response.json())

# --- LAYOUT ---
st.set_page_config(page_title="Legato - Spotify", layout="wide")
st.title("🎵 Legato - Suas 10 músicas mais tocadas")

# --- GERAR URL DE AUTENTICAÇÃO ---
params = {
    "client_id": CLIENT_ID,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE
}
auth_url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"

# --- OBTÉM CODE DA URL ---
query_params = st.query_params
code = query_params.get("code", [None])[0]

# --- FLUXO PRINCIPAL ---
if "access_token" not in st.session_state:
    if code:
        # Preparar requisição para trocar o code por token
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
            token_data = response.json()
            st.session_state.access_token = token_data["access_token"]
        else:
            st.error("❌ Erro ao obter o token de acesso do Spotify.")
            st.write("Status:", response.status_code)
            st.write("Resposta:", response.json())
            st.stop()
    else:
        # Se ainda não autenticado, mostra link
        st.markdown(f"[👉 Clique aqui para autenticar com o Spotify]({auth_url})")
        st.stop()

# --- CLIENTE SPOTIPY COM TOKEN AUTORIZADO ---
sp = spotipy.Spotify(auth=st.session_state.access_token)

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
