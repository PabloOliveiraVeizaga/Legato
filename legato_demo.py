import streamlit as st
import requests
import urllib.parse
import base64

# ======================
# CONFIGURAÇÕES SPOTIFY
# ======================
CLIENT_ID = "418bc0b18e11485589d6898e5530c0df"
CLIENT_SECRET = "500b4a2a865e4b748c65bf48c1cf4b3f"
REDIRECT_URI = 'https://legato-top10tracks.streamlit.app/callback'
SCOPE = "user-top-read user-library-read user-read-recently-played user-read-playback-state user-modify-playback-state"

# ======================
# INICIALIZA INTERFACE
# ======================
st.set_page_config(
    page_title="Legato - Spotify Top Tracks Analysis",
    page_icon="🎵",
    layout="wide"
)

st.title("🎶 Analise suas 10 músicas favoritas no Spotify")

query_params = st.query_params

# ======================
# AUTENTICAÇÃO
# ======================
if "code" not in query_params:
    # Se não tiver código, mostrar botão de login
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE
    }
    auth_url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
    st.markdown("Para continuar, é necessário autorizar o acesso à sua conta Spotify:")
    st.markdown(f"👉 [Clique aqui para autenticar com o Spotify]({auth_url})")
    st.stop()

# ======================
# TROCAR CÓDIGO POR TOKEN
# ======================
code = query_params["code"]
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
    st.error("❌ Erro ao trocar código por token.")
    st.stop()

token_info = response.json()
access_token = token_info["access_token"]

# ======================
# OBTER TOP TRACKS
# ======================
headers = {"Authorization": f"Bearer {access_token}"}
tracks_url = "https://api.spotify.com/v1/me/top/tracks?limit=10&time_range=short_term"

tracks_response = requests.get(tracks_url, headers=headers)

if tracks_response.status_code != 200:
    st.error("❌ Erro ao buscar suas músicas.")
    st.stop()

top_tracks = tracks_response.json()

# ======================
# EXIBIR MÚSICAS
# ======================
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
