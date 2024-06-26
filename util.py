import random
import string
import requests
import base64
import secrets
from pyDes import *
import os
from pytube import YouTube
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import binascii

userAgents = [
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/17.17134",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/18.17763",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/19",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 OPR/45",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 OPR/46",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 OPR/47",
]


def generate_random_filename(length: int, extension: str = ''):
  characters = string.ascii_letters + string.digits
  random_string = ''.join(secrets.choice(characters) for _ in range(length))
  if extension:
    random_string += '.' + extension
  return random_string


def get_random_useragent():
  return userAgents[random.randint(0, len(userAgents) - 1)]


def get_headers(url):
  headers = {
    "Accept": "*/*",
    "Accept-Language": "en-us,en;q=0.5",
    "Sec-Fetch-Mode": "navigate",
    "Referer": "https://instavideosave.net/",
    "Origin": "https://instavideosave.net/",
    "User-Agent": get_random_useragent(),
    "url":url
  }
  return headers


# def get_reel_data(url: str):
#   headers = get_headers()
#   body = {
#     "url": url,
#     "ref": " download-audio-instagram",
#     "via": "form",
#   }
#   res = requests.post(os.environ['REEL_SAVER_URL'], data=body, headers=headers)
#   if res.status_code == 200:
#     response = res.json()
#     if response['success']:
#       return response['data']['medias'][0]["src"]
#   else:
#     return ""



# def get_youtube_song_details(id: str, image: str):
#   yt_link = "https://www.youtube.com/watch?v=" + id
#   yt = YouTube(yt_link)
#   audio_url = yt.streams.get_audio_only()[0].url
#   # for stream in yt.streams.filter(only_audio=True):
#   #   yt_audios.append(stream.url)
#   parsed_url = urlparse(yt_audios[0])
#   query_params = parse_qs(parsed_url.query)
#   expire_value = query_params['expire'][0]
#   yt_dl = {
#     "id": id,
#     "album": "",
#     "album_id": "",
#     "artist": "",
#     "duration": yt.vid_info['videoDetails']['lengthSeconds'],
#     "genre": "YouTube",
#     "has_lyrics": "false",
#     "image": image,
#     "language": "YouTube",
#     "release_date": yt.publish_date.strftime("%m-%d-%Y %H:%M:%S"),
#     "subtitle": yt.vid_info['videoDetails']['author'],
#     "title": yt.title,
#     "url": audio_url,
#     "lowUrl": audio_url,
#     "highUrl": audio_url,
#     "year": yt.publish_date.strftime("%Y"),
#     "320kbps": "false",
#     "quality": "null",
#     "perma_url": yt_link,
#     "expire_at": expire_value,
#     "dateAdded": datetime.now().strftime("%m-%d-%Y %H:%M:%S")
#   }
#   return yt_dl


def convert_json(data):
  sections = {}
  for i in range(len(data['track']['sections'])):
    if data['track']['sections'][i]['type'] == "SONG":
      album = []
      if len(data['track']['sections'][i]['metadata']) != 0:
        for j in range(len(data['track']['sections'][i]['metadata'])):
          album.append(data['track']['sections'][i]['metadata'][j]['text'])
      else:
        album.append(data['track']['sections'][i]['metapages'][0]['caption'])
      sections['album'] = ' '.join(album)
    if data['track']['sections'][i]['type'] == "LYRICS":
      sections['lyrics'] = data['track']['sections'][i]['text']
    if data['track']['sections'][i]['type'] == "VIDEO":
      response = requests.get(data['track']['sections'][i]['youtubeurl'])
      if response.status_code == 200:
        yt_details = response.json()
        youtube = {
          "title": yt_details['caption'],
          "thumbnail": yt_details['image']['url'],
          "video_id": yt_details['actions'][0]['uri'].split("/")[-1][:11]
        }
        sections['youtube'] = youtube
  final_data = {
    "title":
    data['track']['title'],
    "subtitle":
    data['track']['subtitle'],
    "cover_art":
    data['track']['images']['coverart'],
    "meta_data":
    sections,
    'genere':
    data['track']['genres']['primary']
    if 'genres' in data['track'] else "Unknown",
    "message":
    "success"
  }
  return final_data


def decrypt_url(url):
  des_cipher = des(b"38346591",
                   ECB,
                   b"\0\0\0\0\0\0\0\0",
                   pad=None,
                   padmode=PAD_PKCS5)
  enc_url = base64.b64decode(url.strip())
  dec_url = des_cipher.decrypt(enc_url, padmode=PAD_PKCS5).decode('utf-8')
  dec_url = dec_url.replace("_96.mp4", "_320.mp4")
  return dec_url


def encrypt_data(data):
  # Convert key and data to bytes
  key = "qwertyuioplkjhgf"
  key_bytes = key.encode('utf-8')
  data_bytes = data.encode('utf-8')

  # Pad the data using PKCS#7
  padded_data = pad(data_bytes, AES.block_size)

  # Initialize AES cipher in ECB mode
  cipher = AES.new(key_bytes, AES.MODE_ECB)

  # Encrypt the data
  encrypted_data = cipher.encrypt(padded_data)

  # Convert encrypted bytes to hexadecimal string
  encrypted_hex = binascii.hexlify(encrypted_data).decode('utf-8')

  return encrypted_hex


def get_reel_data_2(url: str):
  headers  = get_headers(encrypt_data(url))
  res = requests.get(os.environ['REEL_SAVER_URL'] ,headers=headers)
  if res.status_code == 200:
    response = res.json()
    if response['success']:
      return response['video'][0]["video"]
  else:
    return ""
