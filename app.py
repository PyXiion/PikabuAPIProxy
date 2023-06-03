import requests
import re
import argparse
import json

from flask import Flask, request, Response
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_SUPPORTS_CREDENTIALS'] = True

controller_regex = re.compile(r'[.a-z]+')

api_endpoint = 'https://api.pikabu.ru/v1/'


def create_request(controller, data, **kwargs):
  headers = {
    "deviceuid": "0", # ?
    "user-agent": "ru.pikabu.android/1.21.15 (SM-N975F; Android 7.1.2)",
    "accept-encoding": "gzip",
    "content-type": "application/json"
  }
  r = requests.post(api_endpoint + controller, data=data, headers=headers, **kwargs)
  return r

@app.route('/<controller>', methods=['POST'])
@cross_origin()
def proxy(controller):
  global log
  if not controller_regex.fullmatch(controller):
    return 'Bad request', 400

  data = request.get_data()

  resp = create_request(
    controller, 
    data,
    cookies=request.cookies
  )

  allowed_headers = []
  headers = [
    (k, v.replace('.pikabu.ru', request.host)) for k,v in resp.headers.items()
    if k.lower() in allowed_headers
  ]

  response = Response(resp.content, resp.status_code, headers)

  for k, v in resp.cookies.iteritems():
    response.set_cookie(k, v, 60*60*24*365*2)

  return response
  

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Pikabu API cors proxy")

  parser.add_argument('host', default='127.0.0.1')
  parser.add_argument('-p', '--port', default=45450)
  parser.add_argument('-d', '--debug', default=False)

  app.run(host='127.0.0.1', port=45450, debug=True)