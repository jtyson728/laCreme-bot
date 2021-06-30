import os
import discord
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import json
from utils import *
from spot_utils import *
#from replit import db
#from utils import *
# from keep_alive import keep_alive

#spotify credentials
spotify_client_id = os.environ['SPOTIPY_CLIENT_ID']
spotify_client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
scope = "playlist-modify-public user-library-read user-modify-playback-state"
spotify_username = '12141073399'
redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']

#discord bot credentials
bot_token = os.environ['TOKEN']

#api initializations
client = discord.Client()

spot_token=SpotifyOAuth(username=spotify_username,client_id=spotify_client_id,client_secret=spotify_client_secret,redirect_uri=redirect_uri,scope=scope)
#spot_token=SpotifyOAuth(username=spotify_username,scope=scope)

sp = spotipy.Spotify(auth_manager=spot_token)

#notification that bot is logged in
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  msg = message.content
  #print(message.channel.id, message.channel.name)

  # playlist posted in general
  if (message.channel.name == 'general'): 
    if msg.startswith('https://open.spotify.com'):
        print('Someone posted spotify music')
        await message.channel.send('Somebody posted spotify music')
        link, description = split_music_message(msg)
        print(f'Link: {link} and Description: {description}')
        playlist_songs = get_playlist_songs(sp, link)
        print(f'Playlist Songs: {playlist_songs}')
  else:
    print('other channel')

#create_playlist(sp, spotify_username, 'test')
client.run(bot_token)
#get_saved_tracks()