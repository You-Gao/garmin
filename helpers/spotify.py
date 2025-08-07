import os
import time
import ctypes
from ctypes import wintypes

import requests
from dotenv import load_dotenv
load_dotenv()

# VIRTUAL KEY CODES
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_VOLUME_UP = 0xAF
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_MUTE = 0xAD

KEYEVENTF_KEYUP = 0x0002

def send_key(vk_code):
    try:
        user32 = ctypes.windll.user32
        user32.keybd_event(vk_code, 0, 0, 0)
        time.sleep(0.05)
        user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)
        print(f"Sent virtual key: {hex(vk_code)}")
        return True
    except Exception as e:
        print(f"Error sending key: {e}")
        return False

def play_pause():
    send_key(VK_MEDIA_PLAY_PAUSE)

def next_track():
    send_key(VK_MEDIA_NEXT_TRACK)

def previous_track():
    send_key(VK_MEDIA_PREV_TRACK)

def volume_up():
    send_key(VK_VOLUME_UP)

def volume_down():
    send_key(VK_VOLUME_DOWN)

def mute():
    send_key(VK_VOLUME_MUTE)
    
# SPOTIFY WEB API
CLIENT_ID = os.getenv("SPOTIFY_API_KEY")  
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")  

def get_access_token():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Missing Spotify credentials. Add SPOTIFY_CLIENT_SECRET to .env file.")
        return None
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token")
    else:
        print(f"Failed to get access token: {response.status_code}")
        return None

def get_headers():
    token = get_access_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return None

def find_artist(artist_name):
    headers = get_headers()
    if not headers:
        print("Failed to get Spotify access token")
        return None
        
    url = "https://api.spotify.com/v1/search"
    params = {
        "q": artist_name,
        "type": "artist"
    }
    response = requests.get(url, headers=headers, params=params)
    print(f"Searching for artist: {artist_name}")
    print(f"Response: {response.status_code}")
    print(f"Sent request to Spotify API: {url} with params: {params}")
    if response.status_code == 200:
        data = response.json()
        print(f"Searching for artist: {artist_name}")
        artists = data.get("artists", {}).get("items", [])
        if artists:
            return artists[0]  # Return the first artist found
    return None

def play_artist(artist_name):
    headers = get_headers()
    if not headers:
        print("Failed to get Spotify access token")
        return
        
    artist = find_artist(artist_name)
    if artist:
        url = f"https://api.spotify.com/v1/artists/{artist['id']}/top-tracks?market=US"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            tracks = response.json().get("tracks", [])
            if tracks:
                track_uri = tracks[0]['uri']  # Play the first top track
                play_url = "https://api.spotify.com/v1/me/player/play"
                data = {
                    "uris": [track_uri]
                }
                requests.put(play_url, headers=headers, json=data)
                print(f"Playing top track of {artist_name}")
            else:
                print(f"No top tracks found for {artist_name}")
        else:
            print(f"Error fetching top tracks: {response.status_code}")
    else:
        print(f"Artist '{artist_name}' not found")

if __name__ == "__main__":
    pass