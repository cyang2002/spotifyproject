import os
import time
from dotenv import load_dotenv
from pprint import pprint as pp
from flask import Flask, session, redirect, url_for, request
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

load_dotenv()

app = Flask(__name__)

app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'
app.secret_key = '*********'

TOKEN_INFO = 'token_info'

@app.route('/')
def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('get_playlists', external = True))

@app.route('/get_playlists')
def get_playlists():
    token_info = get_token()
    print(token_info)
    if not token_info:
        print("User not logged in")
        return redirect('/')
    
    sp = Spotify(auth=token_info['access_token'])
    playlists = sp.current_user_playlists()
    playlists_info = [(pl['name'], pl['external_urls']['spotify']) for pl in playlists['items']]
    playlists_html = '<br>'.join([f'{name}: {url}' for name, url in playlists_info])

    return playlists_html


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = os.getenv("CLIENT_ID"),
        client_secret = os.getenv("CLIENT_SECRET"),
        redirect_uri = url_for('redirect_page', _external = True),
        scope='user-library-read playlist-read-private'
    )

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        return None  
    
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60

    if is_expired:
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
        session[TOKEN_INFO] = token_info 

    return token_info

app.run(debug = True)