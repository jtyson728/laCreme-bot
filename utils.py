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
    if msg.startswith('https://open.spotify.com'):
      link = msg.split()[0]
      description = msg.split(None, 1)[1]
    else:
      link_index = msg.index('https')
      description = msg[:link_index]
      link = msg[link_index:]
    print(f'This is the link: {link}')
    print(f'This is the description: {description}')
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

