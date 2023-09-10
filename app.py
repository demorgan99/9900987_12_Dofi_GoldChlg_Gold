from flask import Flask, jsonify, request
import re
from flasgger import Swagger, LazyJSONEncoder
from flasgger import swag_from
from werkzeug.utils import secure_filename
import os
import sqlite3

app = Flask(__name__)

app.json_encoder = LazyJSONEncoder

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "API Documentation for Data Processing and Modelling",
        "description": "Dokumentasi API untuk Data Processing and Modelling",
        "version": "1.0.0"
    }
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json'
        }
    ],
    "static_url_path": '/flasgger_static',
    "swagger_ui": True,
    "specs_route": "/docs/"
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Lokasi penyimpanan file yang diunggah
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'csv'}  # Jenis file yang diizinkan

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Inisialisasi database SQLite
conn = sqlite3.connect('data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS text_data (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT)''')
conn.commit()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Fungsi untuk membersihkan teks
def clean_text(text):
    cleaned_text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
    return cleaned_text

@swag_from("./docs/hello_world.yml", methods=['GET'])
@app.route('/', methods=['GET'])
def hello_world():
    json_response = {
        'status_code': 200,
        'description': "Menyapa Hello World",
        'data': "Hello World",
    }
    response_data = jsonify(json_response)
    return response_data

@swag_from("./docs/text_processing.yml", methods=['POST'])
@app.route('/text_processing', methods=['POST'])
def text_processing():
    # Menerima input teks dari permintaan JSON
    text = request.form.get('text')

    # Fungsi pembersihan teks
    cleaned_text = clean_text(text)

    # Menyimpan data teks ke dalam database SQLite
    c.execute("INSERT INTO text_data (text) VALUES (?)", (cleaned_text,))
    conn.commit()

    # Mengirim respons JSON
    json_response = {
        'status_code': 200,
        'description': "Teks yang telah dibersihkan",
        'data': cleaned_text,
    }
    response_data = jsonify(json_response)
    return response_data

@swag_from("./docs/upload_file.yml", methods=['POST'])
@app.route('/upload_file', methods=['POST'])
def upload_file():
    # Memeriksa apakah file ada dalam permintaan
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    # Memeriksa apakah file yang diunggah memiliki ekstensi yang diizinkan
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Menyimpan nama file ke dalam database SQLite
        c.execute("INSERT INTO text_data (text) VALUES (?)", (filename,))
        conn.commit()

        return jsonify({'status_code': 200, 'description': 'File berhasil diunggah', 'data': filename})

    return jsonify({'error': 'File tidak diizinkan atau tidak ada'}), 400

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run()
