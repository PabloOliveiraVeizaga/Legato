# 🎵 Legato - Suas 10 Músicas Mais Tocadas no Spotify

<img width="100" height="100" alt="image" src="https://github.com/user-attachments/assets/8cfd1426-fc2b-48cc-ac49-cdfed113cf37" align="right"/>
Legato é uma aplicação web interativa desenvolvida com [Streamlit](https://streamlit.io) que se conecta à sua conta Spotify e exibe suas 10 músicas mais ouvidas recentemente.

## 🚀 Funcionalidades

- 🔒 Autenticação segura com sua conta Spotify
- 🎧 Exibição das 10 faixas mais tocadas no curto prazo (`short_term`)
- 🖼️ Capas dos álbuns e links diretos para as músicas no Spotify
- 📊 Informações detalhadas: nome da música, álbum, artistas, data de lançamento, duração e popularidade

---

## 🛠️ Tecnologias Utilizadas

- [Python](https://www.python.org/)
- [Spotipy](https://spotipy.readthedocs.io/en/2.22.1/)
- [Streamlit](https://docs.streamlit.io/)
- [Spotify Web API](https://developer.spotify.com/documentation/web-api/)

---

## 💻 Como Usar

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/legato-spotify-app.git
cd legato-spotify-app
```
### 2. Instale as dependências

```bash
pip install -r requirements.txt
```
### 3. Configure variáveis do ambiente
Crie um arquivo .env (ou defina variáveis no sistema) com:

```bash
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
```
⚠️ Você pode obter essas credenciais criando um app no Spotify Developer Dashboard.

### 4. Rode o app
```bash
streamlit run app.py
```
