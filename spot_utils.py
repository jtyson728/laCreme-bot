#want to add all spotify actions in this file
import spotipy
import apscheduler
from spotipy.oauth2 import SpotifyOAuth
import requests
import json

spotify_username = '12141073399'

# returns a dictionary object containing the name, and spotify ids of the songs on the playlist
def get_playlist_songs(sp, link):
  track_ids_list = []
  playlist_id = link
  offset = 0
  while True:
    response = sp.playlist_items(playlist_id,
                                offset=offset,
                                fields='items.track.id,total,items.track.name,items.track.artists',
                                additional_types=['track'])
    if len(response['items']) == 0:
        break
    for item in response['items']:
      track_ids_list.append(item['track']['id'])
    return track_ids_list

# creates new playlist, add functionality to check if playlist name already exists
def create_playlist(sp, username, playlist_name):
  sp.user_playlist_create(user=username,public=True,name=playlist_name,description='testing',collaborative=False)

def get_existing_playlist_id(sp, channel_name):
  existing_playlists = sp.user_playlists(spotify_username)
  for playlist in existing_playlists['items']:
    if playlist['name'] == f'{channel_name} monthly':
      return playlist['id']
  return None

def add_songs_to_playlist(sp, tracks_to_add, channel_name):
  # check to see if channel playlist already exists in Jeremy's account
  add_id = get_existing_playlist_id(sp, channel_name)
  if add_id:
    sp.playlist_add_items(add_id, tracks_to_add)
  else:
    create_playlist(sp, spotify_username, f'{channel_name} monthly')
    add_id = get_existing_playlist_id(sp, channel_name)
    sp.playlist_add_items(add_id, tracks_to_add)