import os
import csv
from dotenv import load_dotenv
from spotipy import Spotify, SpotifyOAuth
from spotipy.cache_handler import CacheFileHandler

load_dotenv()

class SpotifyProject:
    def __init__(self):
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.redirect_uri = 'http://127.0.0.1:5000/redirect'
        self.scope = 'user-top-read'
        
        self.sp_oauth = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            cache_handler=CacheFileHandler(cache_path=".spotifycache")
        )

    def get_token(self):
        token_info = self.sp_oauth.get_cached_token()
        if not token_info:
            auth_url = self.sp_oauth.get_authorize_url()
            print(f'Please navigate to this URL to authorize access: {auth_url}')
            response = input('Paste the URL you were redirected to here: ')
            code = self.sp_oauth.parse_response_code(response)
            token_info = self.sp_oauth.get_access_token(code)

        return token_info['access_token']

    def get_user_top_tracks(self, token, time_range='medium_term', limit=50):
        spotify = Spotify(auth=token)
        results = spotify.current_user_top_tracks(time_range=time_range, limit=limit)
        return results['items']

    def flatten_track_data(self, track):
        flattened_data = {
            "album_name": track['album']['name'],
            "album_release_date": track['album']['release_date'],
            "album_total_tracks": track['album']['total_tracks'],
            "track_name": track['name'],
            "track_id": track['id'],
            "track_popularity": track['popularity'],
            "track_duration_ms": track['duration_ms'],
            "track_number": track['track_number'],
            "is_explicit": track['explicit'],
            "is_playable": track.get('is_playable', 'N/A'),  # Use 'get' to avoid KeyError
            "track_preview_url": track['preview_url'],
            "track_uri": track['uri'],
            "artists": ', '.join([artist['name'] for artist in track['artists']])
        }
        return flattened_data


    def create_csv(self, tracks, filename='user_top_tracks.csv'):
        with open(filename, "w", newline="") as csv_file:
            fieldnames = [
                "album_name", "album_release_date", "album_total_tracks",
                "track_name", "track_id", "track_popularity", "track_duration_ms",
                "track_number", "is_explicit", "is_playable", "track_preview_url",
                "track_uri", "artists"
            ]
            csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            csv_writer.writeheader()

            for track in tracks:
                flattened_data = self.flatten_track_data(track)
                csv_writer.writerow(flattened_data)

            print(f"Data saved to '{filename}' successfully.")

if __name__ == "__main__":
    spotify = SpotifyProject()
    
    token = spotify.get_token()
    
    top_tracks = spotify.get_user_top_tracks(token, time_range='medium_term', limit=50)
    
    if top_tracks:
        spotify.create_csv(top_tracks, filename='user_top_tracks.csv')
    else:
        print("No tracks found or an error occurred.")
