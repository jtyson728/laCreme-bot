import sys, os.path
import os
import discord
from discord.ext import commands
import spotipy
import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
from spotipy.oauth2 import SpotifyOAuth
from utils import *
import requests
import json
from spot_utils import *
sys.path.append(os.path.abspath('../'))
from bot import sp, scheduler, spotify_username, admins

class Musik(commands.Cog):
  def __init__(self, client):
    self.client = client

#this is event for when a message is posted to the server that the bot is in
  @commands.Cog.listener()
  async def on_message(self, message):
    # if the message came from the bot itself, then ignore it
    if message.author == self.client.user:
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
      elif(message.channel.category_id == 863860603704573983 and len(playlist_songs) > 1):
        await message.channel.send('**ALERT** Hey baby. I\'m sorry to tell you, but up here in #loosies, we only want single songs. 5-song boi\'s go in #lacreme. ', delete_after=30.0)
        if description != '':
          await message.channel.send(f'Here is your description to copy, this message will delete after 60 seconds: \n{description}', delete_after=60.0)
        await message.delete()
      else:
        print(f'Playlist Songs: {playlist_songs}')
        add_songs_to_playlist(sp, playlist_songs, f'{message.channel.name} monthly')
    else:
      if any(mention.name == 'SonOfGloin' for mention in message.mentions):
        await message.channel.send('**ALERT** Tommy is a very stinky boy', delete_after=10.0)
    #await self.client.process_commands(message)

def setup(client):
  client.add_cog(Musik(client))