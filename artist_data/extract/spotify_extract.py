import pandas as pd
from tqdm import tqdm
import spotipy
from typing import Dict, Any, List

# Utility function
from artist_data.setup import UNKNOWN_VALUE
from artist_data.utils import safe_get, safe_extract, flat_nested_dictionary

def spotify_artist_search(spotify_client: spotipy.Spotify, artist_name: str) -> Dict[str, Any]:
    """
    Search for an artist on Spotify by their name.
    
    :param spotify_client: Spotify API client
    :param artist_name: Name of the artist to search for
    :return: The first matching artist's Spotify data
    :raises: ValueError if no artist is found
    """
    spotify_artist_search_result = safe_extract(
        spotify_client.search(artist_name, type='artist'), 
        ['artists', 'items'], 
        None
    )
    
    if spotify_artist_search_result:
        return spotify_artist_search_result[0]
    
    raise ValueError(f"No artist found with the name '{artist_name}'")

def build_spotify_artist_data(spotify_client: spotipy.Spotify, spotify_artist_search_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Builds a dictionary containing basic artist data from a Spotify search result.
    
    :param spotify_client: Spotify API client
    :param spotify_artist_search_result: The artist data returned by a Spotify search
    :return: A dictionary with artist details such as ID, name, genres, and popularity
    """
    return {
        'spotify_artist_id': safe_get(spotify_artist_search_result, 'id'),
        'spotify_artist_name': safe_get(spotify_artist_search_result, 'name'),
        'spotify_artist_uri_path': safe_get(spotify_artist_search_result, 'uri'),
        'spotify_artist_url': safe_get(spotify_artist_search_result, 'href'),
        'spotify_artist_image_url': safe_get(safe_get(spotify_artist_search_result, 'images')[0], 'url'),
        'spotify_artist_n_followers': safe_extract(spotify_artist_search_result, ['followers', 'total']),
        'spotify_popularity': safe_get(spotify_artist_search_result, 'popularity'),
        'spotify_artist_genres': safe_get(spotify_artist_search_result, 'genres'),
        'spotify_related_artists': [safe_get(artist_related, 'name') for artist_related in 
                                    safe_get(spotify_client.artist_related_artists(safe_get(spotify_artist_search_result, 'id')), 'artists')]
    }

def get_artist_albums(spotify_client: spotipy.Spotify, artist_id: str, album_types: List[str] = ['album', 'single']) -> List:
    """
    Retrieves all albums (including singles) from a Spotify artist.
    
    :param spotify_client: Spotify API client
    :param artist_id: Spotify artist ID
    :param album_types: Types of albums to retrieve ('album', 'single', etc.)
    :return: A list of albums (with no duplicates)
    """
    albums = []
    results = spotify_client.artist_albums(artist_id, album_type=','.join(album_types), limit=50)
    
    while results:
        albums.extend(results['items'])
        if results['next']:
            results = spotify_client.next(results)
        else:
            break
    
    # Remove duplicates by album ID
    unique_albums = {album['id']: album for album in albums}.values()
    return list(unique_albums)

def get_album_tracks(spotify_client: spotipy.Spotify, album_id: str) -> List[Dict[str, Any]]:
    """
    Retrieves all tracks from a specific Spotify album.
    
    :param spotify_client: Spotify API client
    :param album_id: Spotify album ID
    :return: A list of tracks in the album
    """
    tracks = []
    results = spotify_client.album_tracks(album_id)
    
    while results:
        tracks.extend(results['items'])
        if results['next']:
            results = spotify_client.next(results)
        else:
            break
    
    return tracks

def get_all_tracks_of_artist(spotify_client: spotipy.Spotify, artist_id: str) -> List[Dict[str, Any]]:
    """
    Retrieves all tracks from a Spotify artist, including singles and album tracks.
    
    :param spotify_client: Spotify API client
    :param artist_id: Spotify artist ID
    :return: A list of all tracks by the artist
    """
    all_tracks = []
    albums = get_artist_albums(spotify_client, artist_id)
    
    for album in tqdm(albums, desc="Fetching album tracks"):
        album_id = safe_get(album, 'id')
        print(album_id)
        tracks = get_album_tracks(spotify_client, album_id)
        tracks = [{**track, 'spotify_album_id': album_id} for track in tracks]
        all_tracks.extend(tracks)
    
    return all_tracks

def build_spotify_artist_tracks(spotify_client: spotipy.Spotify, spotify_artist_id: str) -> List[Dict[str, Any]]:
    """
    Builds a list of all tracks by the artist, including their audio features.
    
    :param spotify_client: Spotify API client
    :param spotify_artist_id: Spotify artist ID
    :return: A list of dictionaries with track details and audio features
    """
    tracks = get_all_tracks_of_artist(spotify_client, spotify_artist_id)
    spotify_artist_tracks = []

    for track in tqdm(tracks, desc="Processing tracks"):
        spotify_artist_tracks.append({
            "spotify_artist_id": spotify_artist_id,
            "spotify_track_id": safe_get(track, 'id'),
            "spotify_track_name": safe_get(track, 'name'),
            "spotify_track_uri": safe_get(track, 'uri'),
            "spotify_track_url": safe_get(track, 'href'),
            "track_number": safe_get(track, 'track_number'),
            "spotify_album_id": safe_get(track, 'spotify_album_id'),
            "track_audio_features_spotify": spotify_client.audio_features(safe_get(track, 'id'))[0] if safe_get(track, 'id') != UNKNOWN_VALUE else {}
        })
    
    # Flatten the nested 'track_audio_features_spotify' into the main dictionary
    spotify_artist_tracks = [flat_nested_dictionary(track, 'track_audio_features_spotify') for track in spotify_artist_tracks]

    return spotify_artist_tracks

def fetch_spotify_artist_data(spotify_client: spotipy.Spotify, artist_name: str) -> Dict[str, Any]:
    """
    Fetches both the metadata and tracks of an artist from Spotify.
    
    This function integrates the steps of searching for the artist, retrieving artist details, 
    and fetching all tracks (along with their audio features).
    
    :param spotify_client: Spotify API client
    :param artist_name: Name of the artist to search for
    :return: A dictionary containing artist metadata and their tracks
    """
    # Step 1: Search for the artist by name
    spotify_artist_search_result = spotify_artist_search(spotify_client, artist_name)
    
    # Step 2: Build the artist's metadata
    spotify_artist_data = build_spotify_artist_data(spotify_client, spotify_artist_search_result)
    
    # Step 3: Build and retrieve the artist's tracks
    spotify_artist_tracks = build_spotify_artist_tracks(spotify_client, spotify_artist_data['spotify_artist_id'])
    
    # Return both artist data and tracks
    return {
        'artist_data': spotify_artist_data,
        'artist_tracks': spotify_artist_tracks
    }