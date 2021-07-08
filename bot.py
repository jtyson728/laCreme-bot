import os
import signal
import sys
import discord
from discord.ext import commands, tasks
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
redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']
spotify_username = os.environ['SPOT_USERNAME']
admins = os.environ['ADMINS']

# create apscheduler object
job_defaults = {'max_instances':3}
scheduler = BackgroundScheduler(daemon=True, job_defaults=job_defaults)

#discord bot credentials (ask Jeremy for environment keys) and create a discord client connection
bot_token = os.environ['TOKEN']
client = commands.Bot(command_prefix='$')

# puts credentials for Jeremys account into SpotifyOAuth and initiate spotify connection instance
spot_token=SpotifyOAuth(username=spotify_username,client_id=spotify_client_id,client_secret=spotify_client_secret,redirect_uri=redirect_uri,scope=scope)
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
    if (message.channel.name == 'lacreme' and len(playlist_songs) > 5):        # if lacreme playlist, make sure user only posted max 5 songs to add
      await message.channel.send('**ALERT** Please repost a playlist with 5 or less songs', delete_after=30.0)
      if description != '':
        await message.channel.send(f'Here is your description to copy, this message will delete after 60 seconds: \n{description}', delete_after=60.0)
      await message.delete()

    else:
      print(f'Playlist Songs: {playlist_songs}')
      add_songs_to_playlist(sp, playlist_songs, f'{message.channel.name} monthly')
  else:
    if any(mention.name == 'SonOfGloin' for mention in message.mentions):
      await message.channel.send('**ALERT** Tommy is a very stinky boy', delete_after=10.0)
  await client.process_commands(message)

@client.command(aliases=['admin', 'metrics'])
async def stats(ctx, *, username):
  await ctx.send(f'Stats of: {username}')
  print("This function ran")

@client.command()
async def clear(ctx, *, playlist_name):
  if(ctx.author.name in admins):
    clear_and_archive_playlist(sp, playlist_name, False)
  else:
    await ctx.send(f'You do not have admin permissions to run this command')

@client.command()
async def posts_by(ctx, *, username):
  #channel = client.get_channel(730839966472601622)
  messages = await ctx.channel.history(oldest_first=True, limit=500).flatten()
  posts_list = []
  for msg in messages:
    if msg.author.name == username and msg.content.startswith('https://open.spotify.com'):
      link, description = split_music_message(msg.content)
      posts_list.append(link)
  print(posts_list)


# def signal_handler(sig, frame):
#   scheduler.shutdown(wait=False)

# This runs the bot, with secret bot token, very important! This will need to be kept alive and running on server
#signal.signal(signal.SIGINT, signal_handler)
scheduler.start()
scheduler.add_job(clear_and_archive_playlist, args=[sp, 'lacreme monthly', True], trigger='interval', seconds=30)    # clear lacreme playlist every 30 seconds (testing purposes)
client.run(bot_token)
