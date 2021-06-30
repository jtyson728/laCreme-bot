import os
import discord
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import json
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

#if message is spotify playlist
@client.event
async def on_message(message):
  if message.author == client.user:
    return
  msg = message.content

  if msg.startswith('https://open.spotify.com'):
    print('Someone posted spotify music')
    await message.channel.send('Somebody posted spotify music')
    create_playlist(sp, spotify_username, 'poop')

def create_playlist(sp, username, link):
  sp.user_playlist_create(user=username,public=True,name='poop',description='testing',collaborative=False)

#create_playlist(sp, spotify_username, 'test')
client.run(bot_token)
#get_saved_tracks()