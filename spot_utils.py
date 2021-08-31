#want to add all spotify actions in this file
import os
import spotipy
import apscheduler
from datetime import datetime
from spotipy.oauth2 import SpotifyOAuth
import requests
import json

spotify_username = os.environ['SPOT_USERNAME']

# takes spotify playlist link or id and returns 
# list of track_ids, artists, and release years
def get_playlist_info(sp, link):
  track_ids_list = []
  artists = []
  release_years = []
  playlist_id = link
  offset = 0
  response = sp.playlist_items(playlist_id,
                              offset=offset,
                              fields='items.track.id,total,items.track.name,items.track.artists.name, items.track.album.release_date',
                              additional_types=['track'])
  if len(response['items']) == 0:
    return track_ids_list
  #print(json.dumps(results, indent=4))
  for item in response['items']:
    track_ids_list.append(item['track']['id'])
    artists.append(item['track']['artists'][0]['name'])
    release_years.append(int(datetime.strptime(item['track']['album']['release_date'], '%Y-%m-%d').year))  
  # features = sp.audio_features(track_ids_list[0])
  # print(json.dumps(features, indent=4))
  return track_ids_list, artists, release_years


def get_playlist_songs(sp, link):
  track_ids_list = []
  playlist_id = link
  offset = 0
  response = sp.playlist_items(playlist_id,
                              offset=offset,
                              fields='items.track.id,total',
                              additional_types=['track'])
  if len(response['items']) == 0:
      return track_ids_list
  for item in response['items']:
    track_ids_list.append(item['track']['id'])
  return track_ids_list

def add_songs_to_playlist(sp, tracks_to_add, channel_name):
  # check to see if channel playlist already exists in dummy account
  add_id = get_existing_playlist_id(sp, channel_name)
  # if it exists, add items
  if add_id:
    present_songs = get_playlist_songs(sp, add_id)
    if(len(present_songs) > 0):
      tracks_to_add = [track for track in tracks_to_add if track not in present_songs]
    if(not len(tracks_to_add) == 0):
      sp.playlist_add_items(add_id, tracks_to_add)
  # if it doesn't exist, create playlist, then get its id, then add songs to that playlist
  else:
    sp.user_playlist_create(user=spotify_username,public=True,name=channel_name,collaborative=False)
    add_id = get_existing_playlist_id(sp, channel_name)
    sp.playlist_add_items(add_id, tracks_to_add)

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

#input: artist of song(s) that were just posted
#output: list of people who have also posted this artist for chat up suggestion
def artist_chat_up(sp, artists, members):
  for member in members:
    print(member)


