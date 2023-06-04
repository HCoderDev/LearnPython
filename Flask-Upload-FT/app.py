import zipfile

from flask import Flask, render_template, request, Response, make_response
from werkzeug.utils import secure_filename
import os
import shutil
app = Flask(__name__)


@app.route('/', methods=['GET', "POST"])
def home():
    return render_template('index.html')

@app.route('/upload1', methods=['GET', "POST"])
def upload1():
    print(request.headers)
    return "Success",200

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    file_name = secure_filename(file.filename)
    save_path = os.path.join('static','files', secure_filename(file.filename))
    zip_folder_path = None
    '''if str(file_name).endswith('.zip'):
        save_path = os.path.join('static','files', secure_filename(file.filename))
    else:
        formZip = request.form.get('forceZip')
        dirpath = request.form.get('Path')
        file_id = request.form.get('fileId')
        if formZip is not None and formZip=='yes' and dirpath is not None:
            zip_folder_path = os.path.join('static', 'files', file_id)
            save_path = os.path.join('static','files',file_id)+f'/{dirpath}'
        else:
            save_path = os.path.join('static', 'files', secure_filename(file.filename))'''

    current_chunk = int(request.form['dzchunkindex'])

    # If the file already exists it's ok if we are appending to it,
    # but not if it's new file that would overwrite the existing one
    if os.path.exists(save_path) and current_chunk == 0:
        # 400 and 500s will tell dropzone that an error occurred and show an error
        return make_response(('File already exists', 400))
    #os.makedirs(os.path.dirname(save_path),exist_ok=True)
    try:
        with open(save_path, 'ab') as f:
            f.seek(int(request.form['dzchunkbyteoffset']))
            f.write(file.read())
            f.close()
    except OSError as e:
        # log.exception will include the traceback so we can see what's wrong 
        print(e)
        return make_response(("Not sure why,"
                              " but we couldn't write the file to disk", 500))

    total_chunks = int(request.form['dztotalchunkcount'])

    if current_chunk + 1 == total_chunks:
        # This was the last chunk, the file should be complete and the size we expect
        if os.path.getsize(save_path) != int(request.form['dztotalfilesize']):
            print('Size Mismatch');
            return make_response(('Size mismatch', 500))
        else:
            print(f'File {file.filename} has been uploaded successfully')
            '''if not file_name.endswith('.zip'):
                file_id = request.form.get('fileId')
                dirpath = os.path.dirname(save_path)
                #create_zip(zip_folder_path,os.path.join('static','files',file_id+f'_{os.path.basename(dirpath)}.zip'))
                #shutil.rmtree(zip_folder_path)'''
    else:
        print(f'Chunk {current_chunk + 1} of {total_chunks} '
                  f'for file {file.filename} complete')

    return make_response(("Chunk upload successful", 200))

def create_zip(directory_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_BZIP2) as zipf:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, arcname=os.path.relpath(file_path, directory_path))

if __name__ == '__main__':
    app.run(debug=True)