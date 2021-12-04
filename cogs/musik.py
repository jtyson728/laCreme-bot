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
    creme_category = discord.utils.get(message.guild.channels, name='5 Packs.').id
    loosie_category = discord.utils.get(message.guild.channels, name='Loosies.').id
    msg = message.content
    def check(msg):
      return msg.author == message.author and msg.channel == message.channel
    if ('https://open.spotify.com') in msg:
      link, description = split_music_message(msg)
      playlist_songs= get_playlist_songs(sp, link)
      # if lacreme playlist, make sure user only posted max 5 songs to add
      if (message.channel.category_id == creme_category and len(playlist_songs) > 5):       
        em = discord.Embed(title=f"ALERT - Your posting was deleted", description=f"Creme playlists are meant to be short and consumable. Please repost a playlist with 5 or less songs.", color=message.author.color)
        if description != '':
          em.add_field(name='Creme Description', value=description, inline=False)
          em.set_footer(text="Please copy your description above so you can repost dat knowledge <3")
        await message.author.send(embed=em)
        await message.delete()
        await message.channel.send(f'Sit tight! {message.author.nick} is fixing some technical difficulties, and will repost their creme shortly :)', delete_after=1800.0)
      # if loosie post, make sure user only posted a single song
      elif(message.channel.category_id == loosie_category and len(playlist_songs) > 1):
        em = discord.Embed(title=f"ALERT - Your posting was deleted", description=f"Hey baby. I\'m sorry to tell you, but up here in #loosies, we only want single songs. 5-song boi\'s go in #lacreme.", color=message.author.color) 
        if description != '':
          em.add_field(name='Loosie Description', value=description, inline=False)
          em.set_footer(text="Please copy your description above so you can repost dat knowledge <3")
        await message.author.send(embed=em)
        await message.delete()
        await message.channel.send(f'Sit tight! {message.author.nick} is fixing some technical difficulties, and will repost their creme shortly :)', delete_after=1800.0)
      elif(message.channel.category_id != loosie_category and message.channel.category_id != creme_category):
        pass

      else:
        print(f'Playlist Songs: {playlist_songs}')
        duplicates, dupe_users = check_duplicates(sp, playlist_songs)
        if(len(duplicates) > 0):
          duplicates = ','.join(duplicates)
          print(dupe_users)
          duplicates_message = "Amore mio— No biggie, just wanted to inform you that one or more of your songs are flames, and were posted already by other members of our lucious community as shown below: \n"
          for key in dupe_users:
            duplicates_message = duplicates_message + f'{key} posted by: {",".join(dupe_users[key])}\n'        
          duplicates_message = duplicates_message + f'This just means that you are indeed posting some heat. Do you baby, and carry on <3'

          await message.author.send(duplicates_message)
        # members = get_all_members(message)
        # matches = artist_chat_up(sp, playlist_artists, members)
        add_songs_to_playlist(sp, playlist_songs, f'{message.channel.name} weekly')
        add_songs_to_playlist(sp, playlist_songs, f'{message.author.name}')
        await update_profile(sp, message.author.name, message)
    else:
      if any(mention.name == 'SonOfGloin' for mention in message.mentions):
        await message.channel.send('**ALERT** Tommy is a very, very stinky boy', delete_after=5.0)

def setup(client):
  client.add_cog(Musik(client))