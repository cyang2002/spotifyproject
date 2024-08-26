import os
import base64
import csv
import json
import requests
from dotenv import load_dotenv
from requests import post, get

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    
    return json_result["access_token"]

def get_auth_header(token):
    if not isinstance(token, str):
        raise TypeError(f"Got a {type(token).__name__} instead of expected String Type")
    
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers = headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("There is no artist with this name")
        return None
    
    return json_result[0]

def get_artist_songs(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers = headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

def get_artist_albums(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?market=US"
    headers = get_auth_header(token)
    result = get(url, headers = headers)
    json_result = json.loads(result.content)["items"]
    return json_result

def flatten_track_data(track):
    """Flattens the track data into a single dictionary suitable for CSV."""
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
        "is_playable": track['is_playable'],
        "track_preview_url": track['preview_url'],
        "track_uri": track['uri'],
    }

    artist_names = [artist['name'] for artist in track['artists']]
    flattened_data['artists'] = ', '.join(artist_names)
    
    return flattened_data

def createCSV():
    token = get_token()
    url = f"https://api.spotify.com/v1/artists/6nxWCVXbOlEVRexSbLsTer/top-tracks?country=US"
    headers = get_auth_header(token)

    csv_filename = f"flume.csv"
    with open(csv_filename, "w", newline="") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=[
            "album_name", "album_release_date", "album_total_tracks",
            "track_name", "track_id", "track_popularity", "track_duration_ms",
            "track_number", "is_explicit", "is_playable", "track_preview_url",
            "track_uri", "artists"
        ])
        csv_writer.writeheader()

        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            json_result = response.json()["tracks"]
            
            for count, track in enumerate(json_result):
                flattened_data = flatten_track_data(track)
                csv_writer.writerow(flattened_data)

            print(f"Data saved to '{csv_filename}' successfully.")
        else:
            print('Error:', response.status_code)


createCSV()

token = get_token()

result = search_for_artist(token, "Flume")
artist_id = result["id"]

songs = get_artist_songs(token,artist_id)

albums = get_artist_albums(token,artist_id)

for i, song in enumerate(songs):
    print(f"{i + 1}. {song['name']}")

# for i, album in enumerate(albums):
#     print(f"{i + 1}. {album['name']}")

print(artist_id)


