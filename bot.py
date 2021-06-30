import os
import discord
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import json
from utils import *
from spot_utils import *

#spotify credentials (ask Jeremy for environment keys)
spotify_client_id = os.environ['SPOTIPY_CLIENT_ID']
spotify_client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
scope = "playlist-modify-public user-library-read user-modify-playback-state"
spotify_username = '12141073399'
redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']

#discord bot credentials (ask Jeremy for environment keys)
bot_token = os.environ['TOKEN']

# this creates a discord client connection
client = discord.Client()

# puts credentials for Jeremys account into SpotifyOAuth.
spot_token=SpotifyOAuth(username=spotify_username,client_id=spotify_client_id,client_secret=spotify_client_secret,redirect_uri=redirect_uri,scope=scope)


# initiates spotify connection instance
sp = spotipy.Spotify(auth_manager=spot_token)

#notification that bot is logged in when bot is first started
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

#this is event for when a message is posted to the server that the bot is in
@client.event
async def on_message(message):
  # if the message came from the bot itself, then ignore it
  if message.author == client.user:
    return
  msg = message.content

  # playlist posted in general
  if (message.channel.name == 'general'): 
    # this denotes that the message is somebody posting a laCreme playlist
    if msg.startswith('https://open.spotify.com'):
        await message.channel.send(f'{msg.author.user.id} just uploaded some new creme')
        link, description = split_music_message(msg)
        playlist_songs = get_playlist_songs(sp, link)
        print(f'Playlist Songs: {playlist_songs}')
  else:
    print('other channel')

# This runs the bot, with secret bot token, very important! This will need to be kept alive and running on server
client.run(bot_token)
