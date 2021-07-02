import os
import discord
import spotipy
import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
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

  if msg.startswith('https://open.spotify.com'):
    #await message.channel.send(f'{message.author.name} just uploaded some new creme')
    link, description = split_music_message(msg)
    playlist_songs = get_playlist_songs(sp, link)
    if (message.channel.name == 'lacreme' and len(playlist_songs) > 5):
      await message.channel.send('**ALERT** Please repost a playlist with 5 or less songs', delete_after=60.0)
      if description != '':
        await message.channel.send(f'Here is your description to copy, this message will delete after 60 seconds: \n{description}', delete_after=60.0)
      await message.delete()

    else:
      print(f'Playlist Songs: {playlist_songs}')
      add_songs_to_playlist(sp, playlist_songs, message.channel.name)
  else:
    if msg.startswith('$clear'):
      clear_playlist(sp, message.channel.name)
    if any(mention.name == 'jtyson728' for mention in message.mentions):
      await message.channel.send('**ALERT** Tommy is a very stinky boy', delete_after=10.0)

# This runs the bot, with secret bot token, very important! This will need to be kept alive and running on server
client.run(bot_token)
