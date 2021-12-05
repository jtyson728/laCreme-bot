import sys, os.path
import os
import discord
from datetime import datetime, timedelta
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
    split_message_worked = True
    if(ctx.author.name in admins):
      compilations = discord.utils.get(ctx.guild.channels, name='compilations')
      this_guild=ctx.message.guild
      creme_category = discord.utils.get(this_guild.channels, name='5 Packs.').id
      loosie_category = discord.utils.get(this_guild.channels, name='Loosies.').id
      for channel in this_guild.text_channels:
        if(channel.category_id == creme_category or channel.category_id == loosie_category):
          print(f'===============Channel name: {channel.name} Channel ID: {channel.id}==============')
          all_messages = await channel.history(limit=None).flatten()
          for post in all_messages:
            if ('https://open.spotify.com') in post.content:
              link,description = split_music_message(post.content)
              playlist_songs = get_playlist_songs(sp, link)
              add_songs_to_playlist(sp, playlist_songs, f'{post.channel.name} archive')
              add_songs_to_playlist(sp, playlist_songs, f'{post.author.name}')
              await update_profile(sp, post.author.name, post)

      sp.user_playlist_create(user=spotify_username,public=True,name='lacreme weekly',collaborative=False)
      sp.user_playlist_create(user=spotify_username,public=True,name='hangingout weekly',collaborative=False)
      sp.user_playlist_create(user=spotify_username,public=True,name='partytunes weekly',collaborative=False)
      creme_embed = discord.Embed(
        title = "La Creme Links",
        description = "Weekly compilation (resets every 3 weeks), as well as an archive of all Creme posted",
        colour = discord.Colour.random()
      )
      # creme_embed.set_thumbnail(url = user.avatar_url)
      playlist = get_existing_playlist_object(sp, 'lacreme weekly')
      creme_weekly = playlist['external_urls']['spotify']
      creme_embed.add_field(name='LaCreme Weekly', value=creme_weekly, inline=False)
      playlist = get_existing_playlist_object(sp, 'lacreme archive')
      creme_archive = playlist['external_urls']['spotify']
      creme_embed.add_field(name='LaCreme Archive', value=creme_archive, inline=False)
      
      await compilations.send(embed=creme_embed)

      hangin_embed = discord.Embed(
        title = "Hanging Out Loosie Links",
        description = "Weekly compilation of chill loosies (resets every 3 weeks), as well as an archive of all chill loosies",
        colour = discord.Colour.random()
      )
      # creme_embed.set_thumbnail(url = user.avatar_url)
      playlist = get_existing_playlist_object(sp, 'hangingout weekly')
      hangin_weekly = playlist['external_urls']['spotify']
      hangin_embed.add_field(name='Hanging Out Weekly', value=hangin_weekly, inline=False)
      playlist = get_existing_playlist_object(sp, 'hangingout archive')
      hangin_archive = playlist['external_urls']['spotify']
      hangin_embed.add_field(name='Hanging Out Archive', value=hangin_archive, inline=False)
      await compilations.send(embed=hangin_embed)

      party_embed = discord.Embed(
        title = "Party Tunes Loosie Links",
        description = "Weekly compilation of party loosies (resets every 3 weeks), as well as an archive of all party loosies",
        colour = discord.Colour.random()
      )
      # creme_embed.set_thumbnail(url = user.avatar_url)
      playlist = get_existing_playlist_object(sp, 'partytunes weekly')
      party_weekly = playlist['external_urls']['spotify']
      party_embed.add_field(name='Party Tunes Weekly', value=party_weekly, inline=False)
      playlist = get_existing_playlist_object(sp, 'partytunes archive')
      party_archive = playlist['external_urls']['spotify']
      party_embed.add_field(name='Party Tunes Archive', value=party_archive, inline=False)
      await compilations.send(embed=party_embed)
    else:
      await ctx.send(f'You do not have admin permissions to run this command')

  #return user message stats for last month
  @commands.command(aliases=['metrics'])
  async def stats(self, ctx, *, username=None):
    this_guild=ctx.message.guild
    last_month = datetime.now() - timedelta(days=30)
    admin_channel_id = discord.utils.get(ctx.guild.channels, name='admin').id
    admin_channel = self.client.get_channel(admin_channel_id)
    creme_category = discord.utils.get(this_guild.channels, name='5 Packs.').id
    loosie_category = discord.utils.get(this_guild.channels, name='Loosies.').id
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
            if channel.category_id == loosie_category:
              loosies = await channel.history(limit=None, after=last_month).flatten()
              for post in loosies:
                if post.author.name == username:
                  gen_count +=1
                  if post.content.startswith('https://open.spotify.com'):
                    loosie_count +=1
                    loosie_posts.append(post)  
                    gen_count -=1
              #items = await channel.history(limit=1000).filter(lambda x: x.author.name == username and x.content.startswith('https://open.spotify.com')).flatten()   
            elif channel.category_id == creme_category:
              cremes = await channel.history(limit=None, after=last_month).flatten()
              for post in cremes:
                if post.author.name == username:
                  gen_count +=1
                  if post.content.startswith('https://open.spotify.com'):
                    creme_count+=1
                    creme_posts.append(post)
                    gen_count -=1
              #creme_posts = await channel.history(limit=1000).filter(lambda x: x.author.name == username and x.content.startswith('https://open.spotify.com')).flatten()
            else:
              others = await channel.history(limit=None, after=last_month).flatten()
              for post in others:
                if post.author.name == username:
                  gen_count +=1
          creme_count = len(creme_posts)
          await admin_channel.send(f'Creme Count: {creme_count} \n Loosie Count: {loosie_count}\n General Messages: {gen_count}')
      else:
        print('general stats go here')
    else:
      await ctx.send(f'You do not have admin permissions to run this command') 

def setup(client):
  client.add_cog(Admin(client))