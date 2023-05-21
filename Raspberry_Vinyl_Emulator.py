"""
@File: Vinyl_Emulator.py

@Created on: May 15th, 2023
@Last Updated: May 19th, 2023

@Version: 1.0.0 - [Ready for Testing #1]

@Description:
This module contains the logic for a Spotify-NFC-Sonos Controller.

This controller is designed to read NFC tags, extract Spotify URIs from them, 
and control a Sonos sound system accordingly. 

@Features:
- Initialization and configuration of an NFC reader
- Initialization of a Sonos sound system and Spotify 
- Detecting NFC tags and reading their NDEF [NFC Data Exchange Format] records
- Extracting Spotify URIs from the NDEF [NFC Data Exchange Format] records
- Checking Sonos API connectivity
- Clearing the current Sonos queue
- Sending commands to Sonos system to play music linked by the Spotify URIs
- ⚠️ Retrieving album cover URLs via Spotify API [!not yet fully implemented!]

@Notes:
- Requires Spotify client id, client secret, and redirect URI to be assigned
- The Sonos IP address and room name are also necessary to be assigned
- It's assumed that the NFC reader is connected to one of the following ports:
    o tty:AMA0 | tty:S0 | tty:USB0
- Exception handling mechanisms are in place for errors related to the Sonos API
 and the NFC reader
"""

import nfc
import time
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from requests.exceptions import RequestException

# Sonos initialization
SONOS_IP_ADDRESS = ""
SONOS_ROOM_NAME = ""
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
NFC_PORTS = ["tty:AMA0", "tty:S0", "tty:USB0"]


def on_startup(targets):
    """ "
    This function is responsible for configuring the NFC reader and is called
    every time the script is run.

    Parameters:
        targets: The targets for NFC communication.
    """
    print("🚀 NFC Reader has been initialized")


def on_connect(tag):
    """
    This function is responsible for reading the NFC tag data and extracting
    the Spotify URI. It does this by checking if the NFC tag has a
    NDEF [NFC Data Exchange Format] record.

    Parameters:
        tag: The NFC tag object.
    """
    print("🪝An NFC tag has been detected!")
    try:
        if tag.ndef:
            spotify_uri = tag.ndef.records[0].text
            print("Captured Spotify URI:", spotify_uri)
            play_on_sonos(spotify_uri)
        else:
            print("No NDEF records found on tag.")
    except Exception as error:
        print("There was an error reading tag or playing song: ", str(error))


def check_sonos_api():
    """Checks the status of the Sonos API

    Returns:
        boolean: if the status was successful or unsuccessful
    """
    try:
        response = requests.get(f"http://{SONOS_IP_ADDRESS}:5005")
        if response.status_code == 200:
            print("✅ SONOS API is up and running!")
            return True
        else:
            print(f"🛑 SONOS API responded with status code {response.status_code}")
            return False
    except RequestException as error:
        print(
            f"There was an error attempting to communicate with the Sonos API: {str(error)}"
        )
        return False


def clear_sonos_queue():
    """
    Clears the current Sonos queue
    """
    try:
        requests.get(f"http://{SONOS_IP_ADDRESS}:5005/{SONOS_ROOM_NAME}/clearqueue")
        print("Cleared Sonos queue!")
    except RequestException as error:
        print(f"There was an error attempting to clear Sonos queue: {str(error)}")


def play_on_sonos(spotify_uri):
    """
    Attempts to send an HTTP request to the Sonos HTTP API to play the
    corresponding song on the Sonos system. Error handling has been implemented
    to attempt this process 3 times before stopping.

    Parameters:
        spotify_uri: The Spotify URI of the song to be played.
    """
    try:
        # Clearlys the sonos queue
        clear_sonos_queue()
        for _ in range(3):
            try:
                requests.get(SONOS_HTTP_API_URL + spotify_uri)
                print(f"Playing {spotify_uri} on Sonos")
                break
            except RequestException as error:
                print(
                    f"There was an error attempting to communicate with Sonos retrying: {str(error)}"
                )
                time.sleep(1)
        else:
            print("Failed to control Sonos after 3 attempts")
    except Exception as error:
        print("An unexpected error occurred while controlling Sonos: ", str(error))


def get_album_cover(tag_data):
    """
    Retrieves the album cover URL using the Spotify API.

    ! Placeholder for now for easier testing

    Parameters:
        tag_data: The Spotify track data.

    Returns:
        The URL of the album cover.
    """
    try:
        retrieved_album_id = Spotify_Client.track(tag_data)["album"]["id"]
        album_meta_data = Spotify_Client.album(retrieved_album_id)
        album_cover_url = album_meta_data["images"][0]["url"]

        return album_cover_url
    except Exception as event:
        print("There was an error getting the album cover: ", str(event))
        return None


def main():
    """
    The main function of the script. Initializes the NFC reader and starts the
    main loop.
    """
    try:
        print("Starting main...")

        clf = nfc.ContactlessFrontend()
        for each_port in NFC_PORTS:
            try:
                if clf.open(each_port):
                    print(
                        f"✅ Successfully connected to NFC reader on port {each_port}!"
                    )
                    break
            except IOError as error:
                print(
                    f"🛑 There was an error opening the NFC reader on port {each_port}: {str(error)}"
                )
        else:
            print(
                "There was an error attempting to open NFC reader on any known port. Exiting..."
            )
            return

        clf.connect(
            rdwr={
                "on-startup": on_startup,
                "on-connect": on_connect,
            }
        )

        while True:
            print("Waiting for NFC Tag...")
            time.sleep(1)
    except Exception as errorMessage:
        print("An unexpected error occurred: ", str(errorMessage))
    finally:
        clf.close()


if __name__ == "__main__":
    """
    Responsible for running the main program
    """
    main()
