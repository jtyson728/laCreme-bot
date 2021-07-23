import sys, os.path
import os
import discord
from discord.ext import commands, tasks
import spotipy
import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
from spotipy.oauth2 import SpotifyOAuth
from utils import *
import requests
import json
from utils import *
from spot_utils import *
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
    loosie_category = discord.utils.get(message.guild.channels, name='loosies').id
    msg = message.content
    def check(msg):
      return msg.author == message.author and msg.channel == message.channel
    if msg.startswith('https://open.spotify.com'):
      link, description = split_music_message(msg)
      playlist_songs = get_playlist_songs(sp, link)
      if (message.channel.name == 'lacreme' and len(playlist_songs) > 5):        # if lacreme playlist, make sure user only posted max 5 songs to add
        em = discord.Embed(title=f"ALERT", description=f"Please repost a playlist with 5 or less songs.", color=message.author.color) 
        await message.channel.send(embed=em, delete_after=60)
        if description != '':
          await message.channel.send(f'Here is your description to copy, this message will delete after 60 seconds: \n{description}', delete_after=60.0)
        await message.delete()
      elif(message.channel.category_id == loosie_category and len(playlist_songs) > 1):
        em = discord.Embed(title=f"ALERT", description=f"Hey baby. I\'m sorry to tell you, but up here in #loosies, we only want single songs. 5-song boi\'s go in #lacreme.", color=message.author.color) 
        await message.channel.send(embed=em, delete_after=60)
        if description != '':
          await message.channel.send(f'Here is your description to copy, this message will delete after 60 seconds: \n{description}', delete_after=60.0)
        await message.delete()
      else:
        print(f'Playlist Songs: {playlist_songs}')
        duplicates = check_duplicates(sp, playlist_songs)
        if(len(duplicates) > 0):
          await message.channel.send(f"You posted duplicate songs. {len(duplicates)} Post anyways? (y/n)", delete_after=10)
        add_songs_to_playlist(sp, playlist_songs, f'{message.channel.name} weekly')
        add_songs_to_playlist(sp, playlist_songs, f'{message.author.name}')
    else:
      if any(mention.name == 'SonOfGloin' for mention in message.mentions):
        await message.channel.send('**ALERT** Tommy is a very stinky boy', delete_after=5.0)

def setup(client):
  client.add_cog(Musik(client))