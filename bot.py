import os
import signal
import sys
import discord
import logging
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

# create apscheduler object
job_defaults = {'max_instances':3}
scheduler = BackgroundScheduler(daemon=True, job_defaults=job_defaults)

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

# puts credentials for Jeremys account into SpotifyOAuth and initiate spotify connection instance
spot_token=SpotifyOAuth(username=spotify_username,client_id=spotify_client_id,client_secret=spotify_client_secret,redirect_uri=redirect_uri,scope=scope)
sp = spotipy.Spotify(auth_manager=spot_token)

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
  clear_weekly.start()

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

@client.command()
async def idle_alerts(ctx):
  refresh_time_first = datetime.timedelta(days=13) # time to first reminder message
  refresh_time_second = datetime.timedelta(days=17) # time to second reminder message
  first_message = [] # list will contain user ids to send first message
  second_message = [] # list will contain user ids to send second message
  history_limit = 200 # number of messages grabbed in reverse chron order
  laCreme = discord.utils.get(ctx.guild.channels, name='lacreme') # discord channel object
  member_ids=[] # will contain all member ids in channel
  members=ctx.guild.members # grab channel members
  messages = await laCreme.history(limit=history_limit).flatten() # grab message history

  # add member ids to member_ids
  for member in members: 
    member_ids.append(member.id)
  # if more than history_limit number of messages have transpired between refresh_time_second, grab more messages.
  # history_limit should change accordingly so this rarely happens
  if messages:
    i=2
    while messages[-1].created_at>(datetime.datetime.utcnow()-refresh_time_second):
      messages = await laCreme.history(limit=history_limit*i).flatten()
      i+=1

  j=0
  while member_ids and j<len(messages):
    # if user posted in time between check and refresh_time_first days ago, remove them from list
    if messages[j].created_at > (datetime.datetime.utcnow()-refresh_time_first):
      if messages[j].author.id in member_ids:
        member_ids.remove(messages[j].author.id)

    # if user posted refresh_time_first days ago, add them to list to receive first message
    if (datetime.datetime.utcnow()-refresh_time_first - datetime.timedelta(days=1)) < messages[j].created_at < (datetime.datetime.utcnow()-refresh_time_first):
      if messages[j].author.id in member_ids:
        member_ids.remove(messages[j].author.id)
        first_message.append(messages[j].author.id)

    # if user posted refresh_time_second days ago, add them to list to receive second message
    if (datetime.datetime.utcnow()-refresh_time_second - datetime.timedelta(days=1)) < messages[j].created_at < (datetime.datetime.utcnow()-refresh_time_second):
      if messages[j].author.id in member_ids:
        member_ids.remove(messages[j].author.id)
        second_message.append(messages[j].author.id)
    j+=1

  # send first message to users in first_message list
  for id in first_message:
    curr_user = client.get_user(id)
    if curr_user.bot == False:
      await curr_user.send(f"Hola non-gendered papacan. We (tommy) has been crying every night missing out on your unique taste in tunes. It's been {refresh_time_first.days} days since you last posted, oh my gad, oh my gad. Just a genteel reminder to drop some heat in #lacreme. Much love. Thank you kindly.")

  # send second message to users in second_message list
  for id in second_message:
    curr_user = client.get_user(id)
    if curr_user.bot == False:
      await curr_user.send(f"Hey, sugar. We talked a few days ago about puttiing a lil something something in #lacreme , and I wanted choose love before I choose violence. I know you're busy, but it would mean a lot to us. ciao bello.")

@tasks.loop(seconds=120)
async def clear_weekly():
  weekly_ids, weekly_names = get_all_playlists_with_name(sp, 'weekly')
  for weekly in weekly_names:
    clear_and_archive_playlist(sp, weekly, True)

client.run(bot_token)
