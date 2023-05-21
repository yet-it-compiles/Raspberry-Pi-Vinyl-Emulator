"""
@File: Vinyl_Emulator.py

@Created on: May 15th, 2023
@Last Updated: May 19th, 2023

@Version: 1.0.0 - [Ready for Testing #1]

@Description:
This module contains the logic for a Spotify-NFC-Sonos Controller.
"""

import nfc
import time
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from requests.exceptions import RequestException

# Sonos initialization
SONOS_IP_ADDRESS = ""
SONOS_ROOM_NAME = "Everywhere"
SONOS_HTTP_API_URL = f"http://{SONOS_IP_ADDRESS}:5005/{SONOS_ROOM_NAME}/spotify/now/"

# Spotify initialization
SPOTIFY_CLIENT_ID = ""
SPOTIFY_API_KEY = ""
SPOTIFY_REDIRECT_URI = ""

# Declare Spotify authentication
PREMISSIONS_TO_SPOTIFY_API = "user-read-playback-state,user-modify-playback-state"

Spotify_Client = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_API_KEY,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=PREMISSIONS_TO_SPOTIFY_API,
    )
)

# !TESTING VALUE and PRINT
track_info = Spotify_Client.track("spotify:track:6rqhFgbbKwnb9MLmUQDhG6")
print(track_info)

# Possible NFC reader ports
NFC_PORTS = ["tty:AMA0"]


def on_startup(targets):
    """ "
    This function is responsible for configuring the NFC reader and is called
    every time the script is run.

    Parameters:
        targets: The targets for NFC communication.
    """
    print("🚀 NFC Reader has been initialized")


if __name__ == "__main__":
    """
    Responsible for running the main program
    """
    main()
