import pandas as pd
from tqdm import tqdm
import lyricsgenius
from typing import Dict, Any, List, Tuple

# Utility function
from artist_data.setup import UNKNOWN_VALUE
from artist_data.utils import safe_get, safe_extract

# Custom exceptions
class GeniusAPIError(Exception):
    """Custom exception for errors related to the Genius API."""
    pass

class ArtistNotFoundError(GeniusAPIError):
    """Custom exception for when an artist is not found."""
    pass

class TrackDataError(GeniusAPIError):
    """Custom exception for track data issues."""
    pass

# Genius Functions
def genius_artist_search(genius_client: lyricsgenius.Genius, artist_name: str, n_tracks: int = 10) -> Dict[str, Any]:
    """
    Search for an artist on Genius by their name.

    Args:
        genius_client (lyricsgenius.Genius): Genius API client.
        artist_name (str): Name of the artist to search for.
        n_tracks (int, optional): Number of tracks to retrieve. Defaults to 10.

    Returns:
        Dict[str, Any]: The artist's data as a dictionary.

    Raises:
        ArtistNotFoundError: If the artist is not found.
        GeniusAPIError: If there is an error fetching the artist's data.
    """
    try:
        artist = genius_client.search_artist(artist_name, max_songs=n_tracks, get_full_info=True)
        if not artist or safe_get(artist.to_dict(), 'name') != artist_name:
            raise ArtistNotFoundError(f"Artist '{artist_name}' not found on Genius.")
        return artist.to_dict()
    except Exception as e:
        raise GeniusAPIError(f"Error fetching artist '{artist_name}' from Genius API: {str(e)}")


def build_genius_artist_data(genius_artist_search_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a structured dictionary with artist information and track data.

    Args:
        genius_artist_search_result (Dict[str, Any]): The artist data from the Genius API.

    Returns:
        Dict[str, Any]: A dictionary containing artist details and a list of tracks.

    Raises:
        TrackDataError: If there is an error while processing track data.
    """
    try:
        return {
            'genius_artist_id': safe_get(genius_artist_search_result, 'id'),
            'genius_artist_name': safe_get(genius_artist_search_result, 'name'),
            'genius_alternate_names': safe_get(genius_artist_search_result, 'alternate_names', []),
            'genius_artist_api_path': safe_get(genius_artist_search_result, 'api_path'),
            'genius_artist_url': safe_get(genius_artist_search_result, 'url'),
            'genius_artist_image_url': safe_get(genius_artist_search_result, 'image_url'),
            'genius_artist_description': safe_extract(genius_artist_search_result, ["description", "plain"]),
            'genius_twitter_name': safe_get(genius_artist_search_result, 'twitter_name'),
            'genius_facebook_name': safe_get(genius_artist_search_result, 'facebook_name'),
            'genius_instagram_name': safe_get(genius_artist_search_result, 'instagram_name'),
            'genius_is_verified': safe_get(genius_artist_search_result, 'is_verified'),
            'genius_tracks': [
                build_genius_artist_track(track)
                for track in tqdm(safe_get(genius_artist_search_result, 'songs', {}), desc= "Processing tracks")
            ]
        }
    except Exception as e:
        raise TrackDataError(f"Error occurred while building artist data: {str(e)}")


def build_genius_artist_track(genius_artist_track: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a structured dictionary containing track information from a Genius API track result.

    Args:
        genius_artist_track (Dict[str, Any]): Dictionary representing a track retrieved from Genius.

    Returns:
        Dict[str, Any]: A dictionary containing track details such as title, album, pageviews, and artist information.

    Raises:
        TrackDataError: If there is an error processing track data.
    """
    if genius_artist_track == {}:
        return

    try:
        primary_artist = safe_extract(genius_artist_track, ['primary_artist', 'name'])
        primary_artists = safe_get(genius_artist_track, 'primary_artists', [])

        return {
            'genius_track_id': safe_get(genius_artist_track, 'id'),
            'genius_title': safe_get(genius_artist_track, 'title'),
            'genius_release_date': safe_get(genius_artist_track, 'release_date'),
            'genius_album': safe_get(genius_artist_track, 'album'),
            'genius_track_api_path': safe_get(genius_artist_track, 'api_path'),
            'genius_pageviews': safe_extract(genius_artist_track, ['stats', 'pageviews']),
            'genius_track_url': safe_get(genius_artist_track, 'url'),
            'genius_track_image_url': safe_get(genius_artist_track, 'song_art_image_url'),
            'genius_track_language': safe_get(genius_artist_track, 'language'),
            'genius_track_description': safe_extract(genius_artist_track, ["description", "plain"]),
            'genius_lyrics': safe_get(genius_artist_track, 'lyrics'),
            'genius_lyrics_is_complete': safe_get(genius_artist_track, 'lyrics_state'),
            'primary_artist': primary_artist,
            'primary_artists': [
                safe_get(artist, 'name')
                for artist in primary_artists
                if safe_get(artist, 'name') != primary_artist
            ],
            'genius_featured_artists': safe_get(genius_artist_track, 'featured_artists', [])
        }
    except Exception as e:
        raise TrackDataError(f"Error occurred while building track data: {str(e)}")


def fetch_genius_artist_data(genius_client: lyricsgenius.Genius, artist_name: str, n_tracks: int = 10) -> Dict[str, Any]:
    """
    Fetch artist data from Genius and build a combined dictionary with artist details and tracks.

    Args:
        genius_client (lyricsgenius.Genius): Genius API client.
        artist_name (str): Name of the artist to search for.
        n_tracks (int, optional): Number of tracks to fetch from Genius. Defaults to 10.

    Returns:
        Dict[str, Any]: A combined dictionary with artist details and tracks.

    Raises:
        GeniusAPIError: If there is an error fetching or processing artist data.
        ArtistNotFoundError: If the artist is not found.
        TrackDataError: If there is an error processing track data.
    """
    try:
        genius_artist = genius_artist_search(genius_client, artist_name, n_tracks)
        genius_artist_data = build_genius_artist_data(genius_artist)

        return {
            'artist_data': {key: value for key, value in genius_artist_data.items() if key != 'genius_tracks'},
            'artist_tracks': safe_get(genius_artist_data, 'genius_tracks', {})
        }
    except (GeniusAPIError, ArtistNotFoundError, TrackDataError) as e:
        raise e
    except Exception as e:
        raise GeniusAPIError(f"Unexpected error: {str(e)}")