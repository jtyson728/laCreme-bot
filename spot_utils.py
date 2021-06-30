#want to add all spotify actions in this file
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import json

def get_playlist_songs(sp, link):
  playlist_id = link
  offset = 0
  while True:
    response = sp.playlist_items(playlist_id,
                                offset=offset,
                                fields='items.track.id,total,items.track.name',
                                additional_types=['track'])
  
    if len(response['items']) == 0:
        break
    print(response['items'])
    offset = offset + len(response['items'])
    print(offset, "/", response['total'])
    return response['items']

def create_playlist(sp, username, link):
  sp.user_playlist_create(user=username,public=True,name='poop',description='testing',collaborative=False)