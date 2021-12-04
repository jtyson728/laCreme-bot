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

  # @commands.command()
  # async def shoutout(self, ctx, shoutee, *, song_info=None):
  #   def check(msg):
  #     return msg.author == ctx.author and msg.channel == ctx.channel
  #   shoutout_channel = discord.utils.get(ctx.guild.channels, name='shoutouts').id
  #   if(ctx.message.channel != shoutout_channel):
  #     await ctx.send(f'All shoutouts should go in the shoutout channel',delete_after=3.5)

  #   msg = await self.client.wait_for("Add a note to this shoutout, or type s to skip", check=check)

def setup(client):
  client.add_cog(Social(client))