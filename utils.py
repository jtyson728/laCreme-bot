import apscheduler
import discord
from discord.ext import commands, tasks
import requests
import json

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

def last_month_user_metrics(user):
  return user

