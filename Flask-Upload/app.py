from zipfile import ZipFile
from multiprocessing import Process
from time import sleep
from flask import Flask, render_template, request,Response
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

def upload_to_artifactory(number,id):
    for sheep in range(number):
        sleep(1)
        print(f'I have slept for {sheep} second for id : '+id)

@app.route('/test/<id>', methods=['GET'])
def testProcess(id):
    p = Process(target=upload_to_artifactory, args=(100,id,))
    p.daemon = True
    p.start()
    print("Let's just forget about it and quit here and now.")
    return {'data':'success'}


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['zipFile']
    temp_zip_filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                           secure_filename(file.filename))
    file.save(temp_zip_filename)  # Then save the file
    filesize = request.headers.get('filesize')
    response = Response({'data':'upload successful'})
    response.headers['filesize'] = filesize
    return response

@app.route('/merge/<id>', methods=['GET'])
def merge(id):
    temp_zip_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'])
    prefixed = [filename for filename in os.listdir(temp_zip_path) if filename.startswith(id)]
    with ZipFile(os.path.join(temp_zip_path,id+'.zip'), 'a') as finalZip:
        for fname in prefixed:
            zf = ZipFile(os.path.join(temp_zip_path,fname), 'r')
            for n in zf.namelist():
                finalZip.writestr(n, zf.open(n).read())
            zf.close()
    for file in prefixed:
        os.remove(os.path.join(temp_zip_path,file))
    return {'id':id,'count':len(prefixed)}

if __name__ == '__main__':
    app.run(debug=True)