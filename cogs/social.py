import sys, os.path
import os
import discord
from datetime import datetime 
import spotipy
import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
from spotipy.oauth2 import SpotifyOAuth
from discord.ext import commands, tasks
from utils import *
from spot_utils import *
sys.path.append(os.path.abspath('../'))
from bot import sp, scheduler, spotify_username, admins


class Social(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command()
  async def shoutout(self, ctx, shoutee, *, song_info=None):
    def check(msg):
      return msg.author == ctx.author and msg.channel == ctx.channel
    shoutout_channel = discord.utils.get(ctx.guild.channels, name='shoutouts').id
    if(ctx.message.channel != shoutout_channel):
      await ctx.send(f'All shoutouts should go in the shoutout channel',delete_after=3.5)

    msg = await self.client.wait_for("Add a note to this shoutout, or type s to skip", check=check)

  @commands.command()
  async def taste(self, ctx, username):
    #user = get_member(ctx, username)
    #user = ctx.author
    profiles_channel = discord.utils.get(ctx.guild.channels, name='profiles').id
    user = discord.utils.get(self.client.get_all_members(), name=username)
    years = []
    existing_playlists = sp.user_playlists(spotify_username)
    for playlist in existing_playlists['items']:
      if playlist['name'] == username:
        print(playlist['external_urls'])
        tracklist, artists, years = get_playlist_info(sp, playlist['id'])
        playlist_link = playlist['external_urls']['spotify']
        time_period = median(years)
        print(time_period)
        embed = discord.Embed(
          title = username,
          description = playlist_link,
          colour = discord.Colour.blue()
        )
        embed.set_thumbnail(url = user.avatar_url)
        embed.add_field(name='Median time period', value=time_period, inline=True)
        embed.add_field(name='Goes by', value=user.nick, inline=True)
        await ctx.send(embed=embed)
  @taste.error
  async def info_error(self, ctx, error):
      if isinstance(error, commands.MissingRequiredArgument):
          await ctx.send('Don\'t forget to add a user ')
def setup(client):
  client.add_cog(Social(client))