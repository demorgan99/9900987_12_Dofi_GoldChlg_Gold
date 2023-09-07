import os
import sqlite3
from flask import Flask, request, jsonify
from flasgger import Swagger, LazyJSONEncoder, swag_from

app = Flask(__name__)
app.json_encoder = LazyJSONEncoder

# Inisialisasi Swagger
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Text Cleansing API",
        "description": "API untuk melakukan text cleansing dan menyimpan data dalam SQLite",
        "version": "1.0.0",
    },
}

swagger = Swagger(app, template=swagger_template)

# Membuat atau menghubungkan ke database SQLite
db_path = "text_data.db"

# Cek apakah file database sudah ada, jika belum, maka akan dibuat
if not os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE text_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT
        )
        """
    )
    conn.commit()
    conn.close()

@app.route("/", methods=["GET"])
def root():
    return "API untuk Text Cleansing dan Data Storage ☕"

@app.route("/cleanse", methods=["POST"])
@swag_from("docs/cleanse.yml", methods=["POST"])
def cleanse_text():
    try:
        data = request.get_json()
        if "text" not in data:
            return jsonify({"error": "Field 'text' diperlukan dalam input JSON"}), 400

        text = data["text"]

        # Lakukan proses cleansing teks di sini (misalnya, menghapus karakter khusus)
        # Anda dapat menambahkan logika pemrosesan teks sesuai kebutuhan
        cleaned_text = text.strip()  # Contoh: Menghapus spasi ekstra di awal dan akhir

        # Simpan data teks yang telah dicleansing ke dalam database SQLite
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("INSERT INTO text_data (text) VALUES (?)", (cleaned_text,))
        conn.commit()
        conn.close()

        result = {"message": "Text berhasil dicleansing dan disimpan", "cleaned_text": cleaned_text}
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/upload", methods=["POST"])
@swag_from("docs/upload.yml", methods=["POST"])
def upload_text_file():
    try:
        # Memastikan Anda memiliki logika untuk mengelola unggahan file
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        uploaded_file = request.files["file"]

        # Jika pengguna tidak memilih file
        if uploaded_file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        # Mendapatkan teks dari file yang diunggah
        file_contents = uploaded_file.read()
        text = file_contents.decode("utf-8")

        # Lakukan proses cleansing teks di sini (misalnya, menghapus karakter khusus)
        # Anda dapat menambahkan logika pemrosesan teks sesuai kebutuhan
        cleaned_text = text.strip()  # Contoh: Menghapus spasi ekstra di awal dan akhir

        # Simpan data teks yang telah dicleansing ke dalam database SQLite
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("INSERT INTO text_data (text) VALUES (?)", (cleaned_text,))
        conn.commit()
        conn.close()

        result = {"message": "File berhasil diunggah, teks berhasil dicleansing dan disimpan", "cleaned_text": cleaned_text}
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
