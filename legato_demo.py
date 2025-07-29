import streamlit as st
import requests
import base64
import urllib.parse
import pandas as pd

# ======================
# CONFIGURAÇÕES SPOTIFY
# ======================
CLIENT_ID = "418bc0b18e11485589d6898e5530c0df"
CLIENT_SECRET = "500b4a2a865e4b748c65bf48c1cf4b3f"
REDIRECT_URI = "https://legato-top10tracks.streamlit.app"
SCOPE = "user-top-read user-library-read user-read-recently-played user-read-playback-state user-modify-playback-state"

# ================
# FUNÇÕES AUXILIARES
# ================

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
        st.error(f"Erro ao trocar código por token: {response.text}")
        return None

def get_user_top_tracks(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = "https://api.spotify.com/v1/me/top/tracks?limit=10&time_range=short_term"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        st.error("❌ Erro ao buscar top tracks.")
        return None

def render_top_tracks(tracks):
    data = []
    for i, track in enumerate(tracks['items'], 1):
        name = track['name']
        artists = ', '.join([artist['name'] for artist in track['artists']])
        popularity = track['popularity']
        data.append({'#': i, 'Track': name, 'Artists': artists, 'Popularity': popularity})

    df = pd.DataFrame(data)

    st.write("### 🎧 Suas Top 10 Músicas")
    st.dataframe(df, use_container_width=True)

    st.write("### 🔥 Popularidade das Músicas")
    st.bar_chart(df.set_index('Track')['Popularity'])

# ============
# APP STREAMLIT
# ============

def main():
    st.set_page_config(page_title="Legato - Spotify Insights", layout="centered")
    st.title("🎶 Legato - Análise das suas músicas no Spotify")

    query_params = st.query_params

    if "code" not in query_params:
        auth_url = get_auth_url()
        st.markdown(f"🔐 Para continuar, [clique aqui para autorizar o Spotify]({auth_url})")
    else:
        code = query_params["code"]
        token_info = exchange_code_for_token(code)

        if token_info and "access_token" in token_info:
            access_token = token_info["access_token"]

            # Buscar músicas
            top_tracks = get_user_top_tracks(access_token)

            if top_tracks:
                render_top_tracks(top_tracks)

if __name__ == "__main__":
    main()
