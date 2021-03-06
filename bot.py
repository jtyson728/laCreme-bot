import os
import signal
import sys
import discord
import logging
from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound
import spotipy
import spotify_token as st
from spotipy.cache_handler import MemoryCacheHandler
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import requests
import json
from requests.exceptions import ReadTimeout
from datetime import datetime, timedelta
from time import sleep
from utils import *
from spot_utils import *

#spotify credentials (ask Jeremy for environment keys)
spotify_client_id = os.environ['SPOTIPY_CLIENT_ID']
spotify_client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
scope = "playlist-modify-public user-library-read user-modify-playback-state"
redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']
spotify_username = os.environ['SPOT_USERNAME']
spot_token_info = os.environ['TOKEN_INFO']
admins = os.environ['ADMINS']
token_info = {'access_token': 'BQAkQWdDUE0Wj4wxInt7enGd_gSfMqfjA29e5nlUnlk7Dfyu-IZVP53UpxaMkSo7boq06kwsLgpQCVCjYgT6rdg8ZAxOrDINSYB1FVvlVj0Lzs7HsDUXFLZRx9Ugo-TP7RpZ586G2zKydVnMr3R0UkEQJ46UYCG9pGbRR-LVkMAio4upZwyG75RuuDqZ3DNlQHP52t78v3hXYg', 'token_type': 'Bearer', 'expires_in': 3600, 'scope': 'playlist-modify-public user-library-read user-modify-playback-state', 'expires_at': 1641953724, 'refresh_token': 'AQCTyzTDGp1FULZYoFE8G8et6FljHCUawW6VJLZuZJp1fWVblGPtrGKeHpZRnpxMgg1pAEAgczWOHVs-u74SDUHp_1JuRbVi68k7RX7VLrFQRBhrTb0tZtUQQA7sN5E1tA8'}
#access_token = os.environ['LOCAL_TOKEN']
laCreme_bot_test_id = 859275367712555029
print(redirect_uri)

#discord bot credentials (ask Jeremy for environment keys) and create a discord client connection
intents = discord.Intents.default()
intents.members = True
bot_token = os.environ['TOKEN']
client = commands.Bot(command_prefix='$', intents=intents)

# this chunk intializes a logger to print to log file
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='laCreme.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
cache_handler = spotipy.cache_handler.MemoryCacheHandler(token_info=token_info)
spot_token=SpotifyOAuth(username=spotify_username,client_id=spotify_client_id,
                        client_secret=spotify_client_secret,
                        redirect_uri=redirect_uri,
                        scope=scope,
                        show_dialog=False,
                        cache_handler=cache_handler)

# spot_token=SpotifyOAuth(username=spotify_username,client_id=spotify_client_id,client_secret=spotify_client_secret,redirect_uri=redirect_uri,scope=scope, show_dialog=False)
# print(f'{spot_token.get_access_token(as_dict=True)}')
# if not spot_token.validate_token(cache_handler.get_cached_token()):
#   # Step 2. Display sign in link when no token
#   auth_url = spot_token.get_authorize_url()
# print(auth_url)

#readyToGo = input('Please wait while we authorize you on a browser')

# sp = spotipy.Spotify(auth=access_token, requests_timeout=15, retries=10)
sp = spotipy.Spotify(auth_manager=spot_token, requests_timeout=15, retries=10)

# print(f'Dictionary: {cache_handler.token_info}')

# load cog (activate it on bot)
@client.command()
async def load(ctx, extension):
  if(is_admin(ctx)):
    client.load_extension(f'cogs.{extension}')
    print('Loaded {extension}')

# unload cog (deactivate it from bot)
@client.command()
async def unload(ctx, extension):
  if(is_admin(ctx)):
    client.unload_extension(f'cogs.{extension}')
    print('Unloaded {extension}')

# unloads then loads cog
@client.command()
async def reload(ctx, extension):
  if(is_admin(ctx)):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    print('Reloaded {extension}')

# runs once when bot is first ran. goes thru cogs folder and loads them all up
for filename in os.listdir('./cogs'):
  if filename.endswith('.py'):
    client.load_extension(f'cogs.{filename[:-3]}')

# (sanity check) notification that bot is logged in when bot is first started
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  #clear_weekly.start()
  #idle_alerts.start(laCreme_bot_test_id)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
      em = discord.Embed(title=f"Error!!!", description=f"Command not found.", color=ctx.author.color) 
      await ctx.send(embed=em)
      return
    raise error

# @tasks.loop(hours=24)
async def idle_alerts(guild_id):
  print("sending idle alerts...")
  guild = client.get_guild(guild_id)
  refresh_time_first = timedelta(days=13) # time to first reminder message
  refresh_time_second = timedelta(days=17) # time to second reminder message
  first_message = f"Hola non-gendered papacan. We (tommy) has been crying every night missing out on your unique taste in tunes. It's been {refresh_time_first.days} days since you last posted, oh my gad, oh my gad. Just a genteel reminder to drop some heat in #lacreme. Much love. Thank you kindly."
  second_message = "Hey, sugar. We talked a few days ago about puttiing a lil something something in #lacreme , and I wanted to choose love before I choose violence. I know you're busy, but it would mean a lot to us. ciao bello."
  members = guild.members # members in guild
  channels = guild.text_channels # text channenls in guild


  for member in members:
    timeStamps = [] # initialize time stamps for each user message
    for channel in channels:
      msg = await channel.history().get(author__id=member.id) # get last user message in each text channel
      if msg: # filter out None
        if msg.created_at > (datetime.utcnow()-refresh_time_first): # if user posted within first refresh time, break loop, get rid of timestamps
          timeStamps=[]
          break
        timeStamps.append(msg.created_at)
    if timeStamps: # remove users who never posted or who have posted within first refresh time
      timeStamps.sort() # most recent post at end of array
      if (datetime.utcnow()-refresh_time_first - timedelta(days=1)) < timeStamps[-1] < (datetime.utcnow()-refresh_time_first):
        if member.bot == False:
          await member.send(first_message) # DM first message
      elif (datetime.utcnow()-refresh_time_second - timedelta(days=1)) < timeStamps[-1] < (datetime.utcnow()-refresh_time_second):
        if member.bot == False:
          await member.send(second_message) # DM second message


#@tasks.loop(seconds=120)
@tasks.loop(hours=504)
async def clear_weekly():
  print(f"Clearing weekly playlists {datetime.utcnow()}")
  weekly_ids, weekly_names = get_all_playlists_with_name(sp, 'weekly')
  for weekly_id, weekly_name in zip(weekly_ids,weekly_names):
    clear_and_archive_playlist(sp, weekly_id, weekly_name, True)
  print("Done clearing weeklys")

client.run(bot_token)
