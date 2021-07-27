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
import datetime
from time import sleep
from utils import *
from spot_utils import *

#spotify credentials (ask Jeremy for environment keys)
spotify_client_id = os.environ['SPOTIPY_CLIENT_ID']
spotify_client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
scope = "playlist-modify-public user-library-read user-modify-playback-state"
redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']
spotify_username = os.environ['SPOT_USERNAME']
admins = os.environ['ADMINS']
laCreme_bot_test_id = 859275367712555029

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
  if(is_admin(ctx)):
    client.load_extension(f'cogs.{extension}')
    print('Loaded {extension}')

@client.command()
async def unload(ctx, extension):
  if(is_admin(ctx)):
    client.unload_extension(f'cogs.{extension}')
    print('Unloaded {extension}')

@client.command()
async def reload(ctx, extension):
  if(is_admin(ctx)):
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    print('Reloaded {extension}')

for filename in os.listdir('./cogs'):
  if filename.endswith('.py'):
    client.load_extension(f'cogs.{filename[:-3]}')

#notification that bot is logged in when bot is first started
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  clear_weekly.start()
  idle_alerts.start(laCreme_bot_test_id)

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

# @client.command()
@tasks.loop(hours=24)
async def idle_alerts(guild_id):
  print("sending idle alerts...")
  guild = client.get_guild(guild_id)
  refresh_time_first = datetime.timedelta(days=13) # time to first reminder message
  refresh_time_second = datetime.timedelta(days=17) # time to second reminder message
  first_message = f"Hola non-gendered papacan. We (tommy) has been crying every night missing out on your unique taste in tunes. It's been {refresh_time_first.days} days since you last posted, oh my gad, oh my gad. Just a genteel reminder to drop some heat in #lacreme. Much love. Thank you kindly."
  second_message = "Hey, sugar. We talked a few days ago about puttiing a lil something something in #lacreme , and I wanted choose love before I choose violence. I know you're busy, but it would mean a lot to us. ciao bello."
  members = guild.members # members in guild
  channels = guild.text_channels # text channenls in guild


  for member in members:
    timeStamps = [] # initialize time stamps for each user message
    for channel in channels:
      msg = await channel.history().get(author__id=member.id) # get last user message in each text channel
      if msg: # filter out None
        if msg.created_at > (datetime.datetime.utcnow()-refresh_time_first): # if user posted within first refresh time, break loop, get rid of timestamps
          timeStamps=[]
          break
        timeStamps.append(msg.created_at)
    if timeStamps: # remove users who never posted or who have posted within first refresh time
      timeStamps.sort() # most recent post at end of array
      if (datetime.datetime.utcnow()-refresh_time_first - datetime.timedelta(days=1)) < timeStamps[-1] < (datetime.datetime.utcnow()-refresh_time_first):
        if member.bot == False:
          await member.send(first_message) # DM first message
      elif (datetime.datetime.utcnow()-refresh_time_second - datetime.timedelta(days=1)) < timeStamps[-1] < (datetime.datetime.utcnow()-refresh_time_second):
        if member.bot == False:
          await member.send(second_message) # DM second message





@tasks.loop(seconds=120)
async def clear_weekly():
  weekly_ids, weekly_names = get_all_playlists_with_name(sp, 'weekly')
  for weekly in weekly_names:
    clear_and_archive_playlist(sp, weekly, True)

client.run(bot_token)
