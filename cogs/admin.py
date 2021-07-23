import sys, os.path
import os
import discord
import spotipy
import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
from spotipy.oauth2 import SpotifyOAuth
from discord.ext import commands, tasks
from utils import *
from spot_utils import *
sys.path.append(os.path.abspath('../'))
from bot import sp, scheduler, spotify_username, admins

class Admin(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command()
  async def clear(self, ctx, *, playlist_name):
    if(ctx.author.name in admins):
      if(not 'archive' in playlist_name):
        clear_and_archive_playlist(sp, playlist_name, False)
      else:
        await ctx.send('You cannot clear an archive')
    else:
      await ctx.send(f'You do not have admin permissions to run this command')

  @commands.command()
  async def scan(self, ctx):
    if(ctx.author.name in admins):
      this_guild=ctx.message.guild
      for channel in this_guild.text_channels:
        print(f'Channel name: {channel.name} Channel ID: {channel.id}')
        all_messages = await channel.history().flatten()
        for post in all_messages:
          if post.content.startswith('https://open.spotify.com'):
            link,description = split_music_message(post.content)
            playlist_songs = get_playlist_songs(sp, link)
            add_songs_to_playlist(sp, playlist_songs, f'{post.channel.name} archive')
            add_songs_to_playlist(sp, playlist_songs, f'{post.author.name}')
    else:
      await ctx.send(f'You do not have admin permissions to run this command')

  
  @commands.command(aliases=['metrics'])
  async def stats(self, ctx, *, username=None):
    admin_channel = discord.utils.get(ctx.guild.channels, name='admin').id
    loosie_category = discord.utils.get(ctx.guild.channels, name='loosies').id
    creme_count = 0
    loosie_count = 0
    gen_count = 0
    creme_posts = []
    loosie_posts = []
    if(is_admin):
      if username:
        if(await is_valid_username(ctx, username)):
          await ctx.send(f'Stats of: {username}')
          this_guild=ctx.message.guild
          for channel in this_guild.text_channels:
            print(f'Channel name: {channel.name} Channel ID: {channel.id}')
            if channel.category_id == loosie_category:
              print(channel.name)
              loosies = await channel.history(limit=1000).flatten()
              for post in loosies:
                if post.author.name == username:
                  gen_count +=1
                  if post.content.startswith('https://open.spotify.com'):
                    loosie_count +=1
                    loosie_posts.append(post)  
                    gen_count -=1
              #items = await channel.history(limit=1000).filter(lambda x: x.author.name == username and x.content.startswith('https://open.spotify.com')).flatten()   
            elif channel.name == 'lacreme':
              cremes = await channel.history(limit=1000).flatten()
              for post in cremes:
                if post.author.name == username:
                  gen_count +=1
                  if post.content.startswith('https://open.spotify.com'):
                    creme_count+=1
                    creme_posts.append(post)
                    gen_count -=1
              #creme_posts = await channel.history(limit=1000).filter(lambda x: x.author.name == username and x.content.startswith('https://open.spotify.com')).flatten()
            else:
              others = await channel.history(limit=1000).flatten()
              for post in others:
                if post.author.name == username:
                  gen_count +=1
          creme_count = len(creme_posts)
          print(f'Creme Count: {creme_count}')
          #loosie_count = len(loosie_posts)
          print(f'Loosie Count: {loosie_count}')
          await admin_channel.send(f'Creme Count: {creme_count} \n Loosie Count: {loosie_count}\n General Messages: {gen_count}')
      else:
        print('general stats go here')
    else:
      await ctx.send(f'You do not have admin permissions to run this command') 

def setup(client):
  client.add_cog(Admin(client))