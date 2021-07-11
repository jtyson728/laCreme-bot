import os
import signal
import sys
import discord
from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound
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
intents = discord.Intents.default()
intents.members = True
bot_token = os.environ['TOKEN']
client = commands.Bot(command_prefix='$', intents=intents)

# puts credentials for Jeremys account into SpotifyOAuth and initiate spotify connection instance
spot_token=SpotifyOAuth(username=spotify_username,client_id=spotify_client_id,client_secret=spotify_client_secret,redirect_uri=redirect_uri,scope=scope)
sp = spotipy.Spotify(auth_manager=spot_token)

@client.command()
async def load(ctx, extension):
  client.load_extension(f'cogs.{extension}')

@client.command()
async def unload(ctx, extension):
  client.unload_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
  if filename.endswith('.py'):
    client.load_extension(f'cogs.{filename[:-3]}')

#notification that bot is logged in when bot is first started
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
      em = discord.Embed(title=f"Error!!!", description=f"Command not found.", color=ctx.author.color) 
      await ctx.send(embed=em)
      return
    raise error

@client.command()
async def posts_by(ctx, *, username):
  if(await is_valid_username(ctx, username)):
    messages = await ctx.channel.history(oldest_first=False, limit=500).flatten()
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
#scheduler.add_job(clear_and_archive_playlist, args=[sp, 'lacreme monthly', True], trigger='interval', seconds=30)    # clear lacreme playlist every 30 seconds (testing purposes)
client.run(bot_token)
