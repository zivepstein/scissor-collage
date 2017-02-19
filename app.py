import os, json, colorsys, random, string
import networkx as nx
from flask import Flask, request, redirect, url_for, jsonify, send_from_directory, render_template
from scipy.spatial import distance
from scipy import misc
from werkzeug.utils import secure_filename
from image_processing.color_cluster import cluster_color
import refine, time

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/get/<name>')
def get(name):
    return send_from_directory('json-out', '{}-out.json'.format(name), as_attachment=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload/', methods=['POST'])
def upload():
    if request.method == 'POST':
        kw = request.form['kw']
        file = request.files['file']
        if file and allowed_file(file.filename):
            name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], "{}.jpg".format(name)))
            refine.go(name, kw)
            return name







