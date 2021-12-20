#want to add all spotify actions in this file
import os
import spotipy
import discord
from datetime import datetime
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOAuth
import requests
import json
from statistics import median
from collections import defaultdict

spotify_username = os.environ['SPOT_USERNAME']

# takes spotify playlist link or id and returns 
# list of track_ids, artists, and release years
def get_playlist_info(sp, link):
  track_ids_list = []
  artists = []
  release_years = []
  playlist_id = link
  offset = 0
  response = sp.playlist_items(playlist_id,
                              offset=offset,
                              fields='items.track.id,total,items.track.name,items.track.artists.name,items.track.artists.external_urls,items.track.album.release_date',
                              additional_types=['track'])
  if len(response['items']) == 0:
    return track_ids_list
  genre_count = dict()
  for item in response['items']:
    artist = sp.artist(item['track']["artists"][0]["external_urls"]["spotify"])
    for i in artist['genres']:
      genre_count[i] = genre_count.get(i, 0) + 1
    track_ids_list.append(item['track']['id'])
    artists.append(item['track']['artists'][0]['name'])
    try:
      release_years.append(int(datetime.strptime(item['track']['album']['release_date'], '%Y-%m-%d').year))
    except ValueError as ve:
      try:
        release_years.append(int(datetime.strptime(item['track']['album']['release_date'], '%Y').year))
      except ValueError as ee:
        continue
  # features = sp.audio_features(track_ids_list[0])
  # print(json.dumps(features, indent=4))
  return track_ids_list, artists, release_years, genre_count


def get_playlist_songs(sp, link):
  track_ids_list = []
  playlist_id = link
  offset = 0
  try:
    response = sp.playlist_items(playlist_id,
                                offset=offset,
                                fields='items.track.id,total',
                                additional_types=['track'])

    if len(response['items']) == 0:
      return track_ids_list
    for item in response['items']:
      track_ids_list.append(item['track']['id'])
  except SpotifyException as e:
    try:
      response = sp.track(playlist_id)
      track_ids_list.append(response['id'])
    except Exception as e:
      print(f'Failed because of {e}, not adding anywhere')
  
  return track_ids_list

def add_songs_to_playlist(sp, tracks_to_add, channel_name):
  # check to see if channel playlist already exists in dummy account
  add_id = get_existing_playlist_id(sp, channel_name)
  # if it exists, add items
  if len(tracks_to_add) > 0:
    if add_id:
      present_songs = get_playlist_songs(sp, add_id)
      if(len(present_songs) > 0):
        tracks_to_add = [track for track in tracks_to_add if track not in present_songs]
      if(not len(tracks_to_add) == 0):
        sp.playlist_add_items(add_id, tracks_to_add)
    # if it doesn't exist, create playlist, then get its id, then add songs to that playlist
    else:
      sp.user_playlist_create(user=spotify_username,public=True,name=channel_name,collaborative=False)
      add_id = get_existing_playlist_id(sp, channel_name)
      sp.playlist_add_items(add_id, tracks_to_add)

def get_existing_playlist_id(sp, channel_name):
  existing_playlists = sp.user_playlists(spotify_username)
  for playlist in existing_playlists['items']:
    if playlist['name'] == channel_name:
      return playlist['id']
  return None

def get_existing_playlist_object(sp, channel_name):
  existing_playlists = sp.user_playlists(spotify_username)
  for playlist in existing_playlists['items']:
    if playlist['name'] == channel_name:
      return playlist
  return None

def check_duplicates(sp, songs):
  playlists = []
  duplicates = set()
  users_who_already_posted = defaultdict(list)
  existing_playlists = sp.user_playlists(spotify_username)
  for playlist in existing_playlists['items']:
    if 'archive' not in playlist['name'] and 'weekly' not in playlist['name']:
      tracklist = get_playlist_songs(sp, playlist['id'])
      if(len(tracklist) > 0):
        intersections = set(songs).intersection(tracklist)
        if(len(intersections) > 0):
          for i in intersections:
            users_who_already_posted[sp.track(i)['name']].append(playlist['name'])
        duplicates = duplicates | intersections
  return [sp.track(dupe)['name'] for dupe in duplicates], users_who_already_posted

def get_all_playlists_with_name(sp, name):
  playlist_ids = []
  playlist_names = []
  existing_playlists = sp.user_playlists(spotify_username)
  for playlist in existing_playlists['items']:
    print(playlist['name'])
    if name in playlist['name']:
      playlist_ids.append(playlist['id'])
      playlist_names.append(playlist['name'])
  return playlist_ids, playlist_names

def clear_and_archive_playlist(sp, weekly_id, weekly_name, archive):
  print(weekly_name)
  track_ids = get_playlist_songs(sp, weekly_id)
  if(track_ids):
    results = sp.playlist_remove_all_occurrences_of_items(weekly_id, track_ids)
    if archive:
      add_songs_to_playlist(sp, track_ids, f'{weekly_name.split()[0]} archive')
  else:
    print('Playlist already empty!!!!')

#input: artist of song(s) that were just posted
#output: list of people who have also posted this artist for chat up suggestion
def artist_chat_up(sp, artists, members):
  for member in members:
    print(member)

async def update_profile(sp, username, message):  
  #user = discord.utils.get(message.guild.get_all_members(), name=username)
  user = message.author
  profiles_channel = discord.utils.get(message.guild.channels, name='profiles')
  all_profiles = await profiles_channel.history(limit=None).flatten()
  message_to_update = None

  for message in all_profiles:
    if len(message.embeds) > 0 and message.embeds[0].title == username:
      message_to_update = message
      break

  years = []
  playlist = get_existing_playlist_object(sp, username)
  if(playlist):
    tracklist, artists, years, genre_count = get_playlist_info(sp, playlist['id'])
    top_3_genres = ','.join(sorted(genre_count, key=genre_count.get, reverse=True)[:3])
    playlist_link = playlist['external_urls']['spotify']
    try:
      time_period = round(median(years))
    except Exception as e:
      print('Cant calculate time period')
    if time_period == None or time_period == 0 or not time_period:
      time_period = 'N/A'
    try:
      if user.nick == None:
        displayname = username
      else:
        displayname = user.nick
    except:
      displayname = username
    embed = discord.Embed(
      title = username,
      description = f'Link to {displayname}\'s Tunes: \n {playlist_link}',
      colour = discord.Colour.random()
    )
    embed.set_thumbnail(url = user.avatar_url)
    embed.add_field(name='Goes by', value=displayname, inline=True)
    embed.add_field(name='Median time period', value=time_period, inline=True)
    embed.add_field(name='Top 3 Genres', value=top_3_genres, inline=False)
    
    if not message_to_update:
      await profiles_channel.send(embed=embed)
    else:
      await message_to_update.edit(embed=embed)


