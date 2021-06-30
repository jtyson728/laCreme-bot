def split_music_message(msg):
  link = msg.split()[0]
  description = msg.split(None, 1)[1]
  return link, description