import os, json, colorsys
import networkx as nx
from flask import Flask, request, redirect, url_for, jsonify, send_from_directory, render_template
from scipy.spatial import distance
from scipy import misc
from werkzeug.utils import secure_filename
from apiclient.discovery import build
from image_processing.color_cluster import cluster_color

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload/', methods=['GET', 'POST'])
def upload():
    return send_from_directory('json-out', 'test.json', as_attachment=False)
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            os.system('node triangulate.js {}'.format(os.path.join(app.config['UPLOAD_FOLDER'], filename)))
            with open('json-out/data.json') as data_file:
                data = json.load(data_file)
                for d in data:
                    d['fill'] = rgb_tup_to_str(closest_color(rgb_str_to_tup(d['fill'])))
                sort(data, key=lambda d: colorsys.rgb_to_hsv(*rgb_str_to_tup(d['fill']))[0])

            return send_from_directory('json-out', 'data.json', as_attachment=False)

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''







# service = build('customsearch', 'v1', developerKey='AIzaSyBl3oaBTl3QC0hhkJrjKEV9KuGXne0t1Q4')
# request = service.cse().list(q='camel',
#                              searchType='image',
#                              imgDominantColor='pink',
#                              imgSize='medium',
#                              cx='010344681634201659024:28tylyxabkm')
# response = request.execute()
# print len(response['items'])
