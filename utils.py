import apscheduler
import discord
import os
from discord.ext import commands, tasks
import requests
import json

admins = os.environ['ADMINS']

class Post:
  def __init__(self, name, time_posted, author):
    self.name = name
    self.time_posted = time_posted
    self.author = author

# splits message into 2 parts: playlist link, and their description for the playlist
def split_music_message(msg):
  if len(msg.split()) > 1:
    link = msg.split()[0]
    description = msg.split(None, 1)[1]
  else:
    link = msg
    description = ''
  return link, description

async def is_valid_username(ctx, username):
  async for member in ctx.guild.fetch_members(limit=None):
    print(member.name)
    if username == member.name:
      return True
  return False

def last_month_user_metrics(user):
  return user

def is_admin(ctx):
  return ctx.author.name in admins

