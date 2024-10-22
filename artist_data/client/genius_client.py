import os
import lyricsgenius
from dotenv import load_dotenv

load_dotenv('../../.env')

# Utility function
from artist_data.utils import suppress_stdout

# Define custom exceptions for Genius Client
class GeniusClientError(Exception):
    """Exception raised for errors in the Genius client setup."""
    pass

class InvalidTokenError(GeniusClientError):
    """Exception raised for invalid Genius API token."""
    pass

class GeniusConnectionError(GeniusClientError):
    """Exception raised for connection issues to the Genius API."""
    pass

def create_genius_client() -> lyricsgenius.genius.Genius:
    """
    Create and return an instance of the Genius API client using the token provided.

    Returns:
        lyricsgenius.genius.Genius: Genius API client instance.

    Raises:
        InvalidTokenError: If the API token is invalid or missing.
        GeniusConnectionError: If there's an issue connecting to the Genius API.
    """
    try:
        # Fetch Genius API token from environment variables
        api_token = os.getenv('GENIUS_API_TOKEN')

        if not api_token:
            raise InvalidTokenError("Genius API token is missing or invalid. Please set the GENIUS_API_TOKEN environment variable.")

        genius = lyricsgenius.Genius(api_token,
                                     timeout=10,
                                     sleep_time=0.5,
                                     retries=5)

        # Perform a test call to ensure the token is valid
        try:
            with suppress_stdout():
                genius.search_artist("ABCDEFGHIJKLMNOPKRSTUVWXYZ",
                                     max_songs = 1,
                                     include_features=True)

            print('INFO: Connection Successful!')

        except Exception as e:
            raise GeniusConnectionError(f"Failed to connect to Genius API: {str(e)}")

        return genius

    except InvalidTokenError as e:
        raise e
    
    except GeniusConnectionError as e:
        raise e
    
    except Exception as e:
        raise GeniusClientError(f"An unexpected error occurred in the Genius client setup: {str(e)}")