import apscheduler
import discord
import os
import re
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
    link = re.search("(?P<url>https?://open.spotify[^\s]+)", msg).group("url")
    description = re.sub("(?P<url>https?://open.spotify[^\s]+)", '', msg)
  else:
    link = msg
    description = ''
  return link, description

# checks if input username exists in the server
async def is_valid_username(ctx, username):
  async for member in ctx.guild.fetch_members(limit=None):
    if username == member.name:
      return True
  return False

# returns list of all members in server
async def get_all_members(message):
  members = []
  async for member in message.guild.fetch_members(limit=None):
    members.append(member)
  return members

# takes in string username and returns member object
async def get_member(ctx, username):
  async for member in ctx.guild.fetch_members(limit=None):
    print(member.name)
    if username == member.name:
      return member
  return ''

# check to see if calling author of command message is an admin
def is_admin(ctx):
  return ctx.author.name in admins

