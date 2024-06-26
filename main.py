from api import Shazam
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import os
import requests
from util import generate_random_filename, convert_json,get_reel_data_2

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app)
CORS(app)


@app.route('/findSong', methods=['GET', 'POST'])
@limiter.limit("3/minute")
def get_song():
  if request.method == "POST":
    song_file = request.files.get("file")
    temp_file_name = generate_random_filename(8, ".wav")
    song_file.save(temp_file_name)
    start = datetime.now()
    mp3 = open(temp_file_name, 'rb').read()
    if os.path.exists(temp_file_name):
      os.remove(temp_file_name)
    shazam_post = Shazam(mp3, )
    rg = shazam_post.recognizeSong()
    try:
      if rg != None:
        final_data = convert_json(rg)
        final_data['time_taken'] = str(datetime.now() - start) + "sec"
        response = {'data': final_data, "message": "success"}
        return response
      else:
        return jsonify({'message': "Song NotFound", 'data': []})
    except Exception as e:
      return jsonify({'message': 'exception occured', 'data': []})

  if request.method == 'GET':
    url: str = request.args.get("url")
    if "instagram.com" in url:
      insta_audio_url = get_reel_data_2(url)
      if len(insta_audio_url) != 0:
        audio_bytes = requests.get(insta_audio_url).content
        shazam_get = Shazam(audio_bytes, )
        rec_data = shazam_get.recognizeSong()
        try:
          if rec_data != None:
            final_data = convert_json(rec_data)
            # saavan_data = get_song_form_saavan(final_data['title'],final_data['genere'])
            # final_data ["related_songs"] = saavan_data
            response = {'data': final_data, "message": "success"}
            return response
          else:
            return jsonify({'message': "Song NotFound", 'data': []})
        except:
          return jsonify({
            'message': 'exception occured while fetching instagram data',
            'data': []
          })
      else:
        return jsonify({
          'message': 'error while getting audio from instagram link',
          'data': []
        })
    else:
      return jsonify({'message': 'submit an valid instagram link', 'data': []})
  else:
    return jsonify({
      'message': "Only POST and GET requests are accepted",
      'data': []
    })


@app.route('/', methods=['GET'])
def get_status():
  return "success", 200


@app.errorhandler(429)
def ratelimit_handler(e):
  return jsonify(
    {'message': "You have exceeded your rate-limit 6 requests per minute"})


app.run(host='0.0.0.0', port=81)
