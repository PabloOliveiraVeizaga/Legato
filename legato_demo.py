import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
import streamlit as st
import requests
import os
import urllib.parse
import base64

# --- CONFIGURAÇÕES ---
CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET", "")
REDIRECT_URI = 'https://legato-top10tracks.streamlit.app'
SCOPE = 'user-top-read user-library-read user-read-recently-played user-read-email user-read-private'

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
# --- OBTÉM INFORMAÇÕES DO USUÁRIO ---
user_info = sp.current_user()

# --- EXTRAI DADOS DO USUÁRIO ---
user_name = user_info.get("display_name", "Usuário")
user_image = user_info.get("images", [{}])[0].get("url", "")
followers = user_info.get("followers", {}).get("total", 0)
country = user_info.get("country", "N/A")
subscription = user_info.get("product", "N/A").capitalize()  # 'free' ou 'premium'

# --- MOSTRA NO CANTO SUPERIOR DIREITO ---
with st.sidebar:
    if user_image:
        st.image(user_image, width=150)
    st.markdown(f"## 👤 {user_name}")
    st.markdown(f"**Seguidores:** {followers}")
    st.markdown(f"**País:** {country}")
    st.markdown(f"**Plano:** {subscription}")
    st.markdown("---")

# --- FUNÇÃO PARA EXIBIR TRACKS ---
def mostrar_top_tracks(time_range, titulo, container):
    top_tracks = sp.current_user_top_tracks(limit=10, time_range=time_range)
    container.subheader(titulo)
    for i, item in enumerate(top_tracks['items'], 1):
        track_name = item['name']
        album_name = item['album']['name']
        artists = ', '.join([artist['name'] for artist in item['artists']])
        release_date = item['album']['release_date']
        try:
            data_formatada = datetime.strptime(release_date, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            try:
                data_formatada = datetime.strptime(release_date, "%Y-%m").strftime("%m/%Y")
            except ValueError:
                data_formatada = release_date  # Apenas o ano, sem formatação extra
        duration_ms = item['duration_ms']
        minutos = duration_ms // 60000
        segundos = (duration_ms % 60000) // 1000
        popularity = item['popularity']
        image_url = item['album']['images'][0]['url']
        spotify_url = item['external_urls']['spotify']

        container.markdown(f"### {i}º Lugar")
        col1, col2 = container.columns([1, 3])
        with col1:
            container.image(image_url, width=200)
        with col2:
            container.markdown(f"**Música:** [{track_name}]({spotify_url})")
            container.markdown(f"**Álbum:** {album_name}")
            container.markdown(f"**Artistas:** {artists}")
            container.markdown(f"**Lançamento:** {data_formatada}")
            container.markdown(f"**Duração:** {minutos}min {segundos:02d}s")
            container.markdown(f"**Popularidade:** {popularity} (i)")
        container.markdown("---")


# --- TRÊS COLUNAS: curto, médio e longo prazo ---
col1, col2, col3 = st.columns(3)

mostrar_top_tracks("short_term", "🎧 Últimas 4 semanas", col1)
mostrar_top_tracks("medium_term", "🕒 Últimos 6 meses", col2)
mostrar_top_tracks("long_term", "📅 Último ano", col3)
st.caption("(i) Popularidade da faixa: O valor estará entre 0 e 100, sendo 100 o mais popular. É calculada por algoritmo e se baseia, em grande parte, no número total de reproduções da faixa e em quão recentes essas reproduções foram. De modo geral, músicas que estão sendo muito tocadas agora terão uma popularidade maior do que músicas que foram muito tocadas no passado. Faixas duplicadas (por exemplo, a mesma faixa de um single e de um álbum) são classificadas de forma independente. A popularidade do artista e do álbum é derivada matematicamente da popularidade da faixa. Observação: o valor da popularidade pode ter um atraso de alguns dias em relação à popularidade real: o valor não é atualizado em tempo real.")
