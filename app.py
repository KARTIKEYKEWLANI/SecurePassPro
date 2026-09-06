from flask import Flask, render_template, request, redirect, url_for, flash, Response
from werkzeug.utils import secure_filename
import os
import uuid
import boto3

# ================== IMPORT YOUR MODULES ==================
from utils.password_checker import analyze_password
from utils.text_encryptor import generate_key, load_key, save_key, encrypt_text, decrypt_text
from utils.image_encryptor import generate_key as img_generate_key, save_key as img_save_key, load_key as img_load_key, encrypt_image, decrypt_image
from utils.file_encryptor import (
    generate_key as file_generate_key,
    save_key as file_save_key,
    load_key as file_load_key,
    encrypt_file,
    decrypt_file,
    encrypt_file_data,
    decrypt_file_data
)

# ================== APP INIT ==================
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# ================== AWS CONFIG ==================
s3 = boto3.client('s3')
BUCKET_NAME = "23bcs12398amzbucket"

# ================== KEY SETUP ==================
FILE_KEY_PATH = "file.key"
if not os.path.exists(FILE_KEY_PATH):
    file_save_key(file_generate_key(), FILE_KEY_PATH)
file_key = file_load_key(FILE_KEY_PATH)

# ================== ROUTES ==================

# 🔥 Home
@app.route('/')
def index():
    return render_template('index.html')

# ================== PASSWORD ==================
@app.route('/password', methods=['GET', 'POST'])
def password():
    strength, suggestions = None, []
    if request.method == 'POST':
        pwd = request.form['password']
        strength, suggestions = analyze_password(pwd)
    return render_template('password.html', strength=strength, suggestions=suggestions)

# ================== TEXT ENCRYPT ==================
@app.route('/text-encrypt', methods=['GET', 'POST'])
def text_encrypt():
    key_path = "secret.key"

    if not os.path.exists(key_path):
        save_key(generate_key(), key_path)

    key = load_key(key_path)

    result = None
    action = None
    input_text = ""

    if request.method == 'POST':
        action = request.form.get('action')
        input_text = request.form.get('text', "").strip()
        

        try:
            if action == 'encrypt':
                result = encrypt_text(input_text, key).decode()

            elif action == 'decrypt':
                result = decrypt_text(input_text.encode(), key)

        except Exception as e:
            result = f"Error: {e}"

    return render_template(
        'text_encrypt.html',
        result=result,
        action=action,
        input_text=input_text
    )
# ================== IMAGE ENCRYPT ==================
@app.route('/image-encrypt', methods=['GET', 'POST'])
def image_encrypt():
    result_path = None
    key_path = "image.key"

    if not os.path.exists(key_path):
        img_save_key(img_generate_key(), key_path)
    key = img_load_key(key_path)

    if request.method == 'POST':
        action = request.form.get('action')
        file = request.files['image']

        filename = secure_filename(file.filename).replace(" ", "_").strip()
        upload_path = os.path.join("static", filename)
        file.save(upload_path)

        try:
            if action == 'encrypt':
                encrypted_data = encrypt_image(upload_path, key)
                encrypted_path = upload_path + ".enc"
                with open(encrypted_path, "wb") as f:
                    f.write(encrypted_data)
                os.remove(upload_path)
                result_path = encrypted_path

            elif action == 'decrypt':
                with open(upload_path, "rb") as f:
                    encrypted_data = f.read()
                output_path = os.path.join("static", "decrypted_" + filename)
                decrypt_image(encrypted_data, key, output_path)
                result_path = output_path

        except Exception as e:
            print(e)

    return render_template('image_encrypt.html', result_path=result_path)

# ================== LOCAL FILE ENCRYPT ==================
@app.route('/file-encrypt', methods=['GET', 'POST'])
def file_encrypt():
    result_path = None
    key = file_key

    if request.method == 'POST':
        action = request.form.get('action')
        file = request.files['file']

        filename = secure_filename(file.filename).replace(" ", "_").strip()
        upload_path = os.path.join("static", filename)
        file.save(upload_path)

        try:
            if action == 'encrypt':
                result_path = encrypt_file(upload_path, key)
                os.remove(upload_path)

            elif action == 'decrypt':
                output_path = os.path.join("static", "decrypted_" + filename)
                result_path = decrypt_file(upload_path, key, output_path)

        except Exception as e:
            print(e)

    return render_template('file_encrypt.html', result_path=result_path)

# ================== S3 UPLOAD ==================
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']

    if file.filename == "":
        return "No file selected"

    filename = secure_filename(file.filename).replace(" ", "_").strip()
    unique_name = str(uuid.uuid4()) + "_" + filename

    try:
        data = file.read()
        encrypted_data = encrypt_file_data(data, file_key)

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=unique_name + ".enc",
            Body=encrypted_data
        )

        return "Uploaded to S3 successfully"

    except Exception as e:
        return str(e)

# ================== S3 FILE LIST ==================
@app.route('/files')
def list_files():
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)

    files = []
    if 'Contents' in response:
        for obj in response['Contents']:
            files.append({
    "original": obj['Key'],
    "display": obj['Key'].replace(".enc", "").split("_", 1)[-1]
})

    return render_template('files.html', files=files)

# ================== S3 DOWNLOAD ==================
@app.route('/download/<filename>')
def download(filename):
    response = s3.get_object(Bucket=BUCKET_NAME, Key=filename)
    encrypted_data = response['Body'].read()

    decrypted_data = decrypt_file_data(encrypted_data, file_key)

    return Response(
        decrypted_data,
        mimetype='application/octet-stream',
        headers={
            "Content-Disposition": f"attachment; filename={filename.replace('.enc','')}"
        }
    )

# ================== KEYLOGGER ==================
@app.route('/web-keylogger')
def web_keylogger():
    return render_template('web_keylogger.html')

@app.route('/keylogger')
def keylogger_info():
    return render_template('keylogger.html')


# ================== RUN ==================
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )