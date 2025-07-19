import os
import time
import shutil
import threading
import subprocess

from dotenv import load_dotenv
from flask import abort
from flask import Flask
from flask import request
from flask import send_from_directory
from flask_cors import CORS
from flask_restful import Api
from flask_restful import Resource
from werkzeug.utils import secure_filename


load_dotenv()

application = Flask(__name__)
application.config['CORS_HEADERS'] = 'Content-Type'
application.config['CORS_RESOURCES'] = {r'/api/*': {'origins': '*'}}
application.config['PROPAGATE_EXCEPTIONS'] = True

cors = CORS(application)
api = Api(application)

GPT_TEXT_MODEL = os.getenv('GPT_TEXT_MODEL')
GPT_IMAGE_MODEL = os.getenv('GPT_IMAGE_MODEL')
GPT_KEY = os.getenv('GPT_KEY')

DATA_DIR = os.getenv('DATA_DIR')

STATUS_READY = 0
STATUS_ANALYZING = 1
STATUS_GENERATING = 2
STATUS_MERGING = 3
STATUS_MAP = {
    STATUS_READY: 'Ready',
    STATUS_ANALYZING: 'Analyzing Video...',
    STATUS_GENERATING: 'Generating Narration...',
    STATUS_MERGING: 'Merging Video and Audio...',
}

current_status = STATUS_READY
status_lock = threading.Lock()


class Index(Resource):
    def get(self):
        return send_from_directory('templates', 'index.html')


class Data(Resource):
    def get(self, path):
        full_path = os.path.join(os.getcwd(), DATA_DIR, path)
        if not os.path.isfile(full_path):
            return abort(404, description='File not found')
        directory = os.path.dirname(full_path)
        filename = os.path.basename(full_path)
        return send_from_directory(directory, filename)


class Status(Resource):
    def get(self):
        with status_lock:
            code = current_status
        return {'code': code, 'status': STATUS_MAP[code]}, 200


class Upload(Resource):
    def post(self):
        global current_status
        if current_status != STATUS_READY:
            abort(409, description='Server is busy, try later')
        if 'file' not in request.files:
            abort(400, description='No file part in the request')
        file = request.files['file']
        if file.filename == '':
            abort(400, description='No selected file')
        filename = secure_filename(file.filename)
        if not filename.lower().endswith('.mp4'):
            abort(400, description='Only .mp4 files are allowed')
        save_dir = os.path.join(os.getcwd(), DATA_DIR)
        if os.path.exists(save_dir):
            shutil.rmtree(save_dir)
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, filename)
        file.save(save_path)
        threading.Thread(target=pipeline_runner, args=(save_path,), daemon=True).start()
        return {
            'message': 'Upload successful',
            'filename': filename,
            'size_bytes': os.path.getsize(save_path)
        }, 201


def pipeline_runner(mp4_path):
    global current_status
    stages = [
        (STATUS_ANALYZING,  ['python', 'test1.py', mp4_path]),
        (STATUS_GENERATING, ['python', 'test2.py', mp4_path]),
        (STATUS_MERGING,    ['python', 'test3.py', mp4_path]),
    ]
    for status_code, cmd in stages:
        with status_lock:
            current_status = status_code
        print('Current Status:', current_status)
        try:
            subprocess.run(cmd, check=True)
        except Exception as e:
            print(f'Stage failed: {cmd}\n{e}')
            break
    with status_lock:
        current_status = STATUS_READY


api.add_resource(Index, '/', endpoint='index')
api.add_resource(Data, '/data/<path:path>')
api.add_resource(Upload, '/api/upload', endpoint='upload')
api.add_resource(Status,  '/api/status', endpoint='status')


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5050)
