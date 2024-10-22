import os
from dotenv import load_dotenv

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv('../../.env')

# Define custom exceptions for Spotify Client
class SpotifyClientError(Exception):
    """Exception raised for errors in the Spotify client setup."""
    pass

class InvalidCredentialsError(SpotifyClientError):
    """Exception raised for invalid Spotify API credentials."""
    pass

class SpotifyConnectionError(SpotifyClientError):
    """Exception raised for connection issues to the Spotify API."""
    pass

def create_spotify_client() -> spotipy.Spotify:
    """
    Create and return an instance of the Spotify API client using the credentials provided.

    Returns:
        spotipy.Spotify: Spotify API client instance.

    Raises:
        InvalidCredentialsError: If the client credentials are invalid or missing.
        SpotifyConnectionError: If there's an issue connecting to the Spotify API.
    """
    try:
        # Fetch Spotify credentials from environment variables
        client_id = os.getenv('CLIENT_ID_SPOTIFY')
        client_secret = os.getenv('CLIENT_SECRET_SPOTIFY')

        if not client_id or not client_secret:
            raise InvalidCredentialsError("Spotify client credentials are missing or invalid. "
                                          "Please set the CLIENT_ID_SPOTIFY and CLIENT_SECRET_SPOTIFY environment variables.")

        # Initialize Spotify client
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id,
                                                              client_secret=client_secret)
        
        spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        # Perform a test call to ensure the credentials are valid
        try:
            spotify.search("ABCDEFGHIJKLMNOPKRSTUVWXYZ",
                           type='artist',
                           limit=1)
            
            print('INFO: Spotify Connection Successful!')

        except Exception as e:
            raise SpotifyConnectionError(f"Failed to connect to Spotify API: {str(e)}")

        return spotify

    except InvalidCredentialsError as e:
        raise e
    
    except SpotifyConnectionError as e:
        raise e
    
    except Exception as e:
        raise SpotifyClientError(f"An unexpected error occurred in the Spotify client setup: {str(e)}")