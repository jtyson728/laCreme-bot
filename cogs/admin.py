import discord
from discord.ext import commands
from utils import *
from spot_utils import *

class Admin(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.Cog.listener()
  async def on_ready(self):
    print('Bot is online')
  
  @commands.command(aliases=['admin', 'metrics'])
  async def stats(self, ctx, *, username):
    creme_posts = []
    loosie_posts = []
    await ctx.send(f'Stats of: {username}')
    for channel in ctx.guild.text_channels:
      if channel.name == 'lacreme':
        posts = await ctx.channel.history(limit=1000).flatten()
        creme_posts.append([post for post in posts if post.author.name == username and post.content.startswith('https://open.spotify.com')])
    print("This function ran")
    print(creme_posts)
    creme_count = len(creme_posts)
    print(f'Creme Count: {creme_count}')
    loosie_count = len(loosie_posts)

def setup(client):
  client.add_cog(Admin(client))