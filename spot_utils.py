#want to add all spotify actions in this file
import os
import spotipy
import apscheduler
from spotipy.oauth2 import SpotifyOAuth
import requests
import json

spotify_username = os.environ['SPOT_USERNAME']

# returns a dictionary object containing the name, and spotify ids of the songs on the playlist
def get_playlist_songs(sp, link):
  track_ids_list = []
  playlist_id = link
  offset = 0
  response = sp.playlist_items(playlist_id,
                              offset=offset,
                              fields='items.track.id,total,items.track.name,items.track.artists',
                              additional_types=['track'])
  if len(response['items']) == 0:
      return track_ids_list
  for item in response['items']:
    track_ids_list.append(item['track']['id'])
  return track_ids_list

# creates new playlist, add functionality to check if playlist name already exists
def create_playlist(sp, username, playlist_name):
  sp.user_playlist_create(user=username,public=True,name=playlist_name,description='testing',collaborative=False)

# currently, this looks for playlists with the channel name and 'monthly' at the end
def get_existing_playlist_id(sp, channel_name):
  existing_playlists = sp.user_playlists(spotify_username)
  for playlist in existing_playlists['items']:
    if playlist['name'] == channel_name:
      return playlist['id']
  return None

def check_duplicates(sp, songs):
  playlists = []
  duplicates = set()
  existing_playlists = sp.user_playlists(spotify_username)
  for playlist in existing_playlists['items']:
    if 'archive' in playlist['name'] or 'weekly' in playlist['name']:
      tracklist = get_playlist_songs(sp, playlist['id'])
      if(len(tracklist) > 0):
        duplicates = duplicates | set(songs).intersection(tracklist) 
  return duplicates

def get_all_playlists_with_name(sp, name):
  playlist_ids = []
  playlist_names = []
  existing_playlists = sp.user_playlists(spotify_username)
  for playlist in existing_playlists['items']:
    if name in playlist['name']:
      playlist_ids.append(playlist['id'])
      playlist_ids.append(playlist['name'])
  return playlist_ids, playlist_names

def add_songs_to_playlist(sp, tracks_to_add, channel_name):
  add_id = get_existing_playlist_id(sp, channel_name) # check to see if channel playlist already exists in Jeremy's account
  if add_id:                                          # if it exists, add items
    present_songs = get_playlist_songs(sp, add_id)
    if(len(present_songs) > 0):
      tracks_to_add = [track for track in tracks_to_add if track not in present_songs]
    sp.playlist_add_items(add_id, tracks_to_add)
  else:                                               # if it doesn't exist, create playlist, then get its id, then add songs to that playlist
    create_playlist(sp, spotify_username, channel_name)
    add_id = get_existing_playlist_id(sp, channel_name)
    sp.playlist_add_items(add_id, tracks_to_add)

def clear_and_archive_playlist(sp, channel_name, archive):
  print(channel_name)
  playlist_id = get_existing_playlist_id(sp, channel_name)
  track_ids = get_playlist_songs(sp, playlist_id)
  if(track_ids):
    results = sp.playlist_remove_all_occurrences_of_items(playlist_id, track_ids)
    if archive:
      add_songs_to_playlist(sp, track_ids, f'{channel_name.split()[0]} archive')
  else:
    print('Playlist already empty!!!!')