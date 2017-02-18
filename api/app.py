from flask import Flask
from apiclient.discovery import build

# app = Flask(__name__)

# @app.route('/')
# def index_hanlder():
service = build('customsearch', 'v1', developerKey='AIzaSyBl3oaBTl3QC0hhkJrjKEV9KuGXne0t1Q4')
request = service.cse().list(q='camel',
                             searchType='image',
                             imgDominantColor='pink',
                             imgSize='medium',
                             cx='010344681634201659024:28tylyxabkm')
response = request.execute()
print len(response['items'])
