from zipfile import ZipFile

from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
import datetime
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'

@app.route('/', methods=['GET',"POST"])
@app.route('/home', methods=['GET',"POST"])
def home():
    start = datetime.datetime.now()
    if request.method == 'POST':
        file = request.files['fileToUpload']
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))) # Then save the file
        end = datetime.datetime.now()

        folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'])
        files = []
        for file in os.listdir(folder):
            files.append(file)


        return render_template('files.html',files=files,duration=str(end-start))
    return render_template('index.html')


@app.route('/zip', methods=['GET'])
def ziplocal():
    return render_template('indexzip.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['zipFile']
    temp_zip_filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                           secure_filename(file.filename))
    file.save(temp_zip_filename)  # Then save the file

    return {'data':'upload successful'}

if __name__ == '__main__':
    app.run(debug=True)