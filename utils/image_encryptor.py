from cryptography.fernet import Fernet
from PIL import Image
import io

def generate_key():
    return Fernet.generate_key()

def save_key(key, filename="image.key"):
    with open(filename, "wb") as key_file:
        key_file.write(key)

def load_key(filename="image.key"):
    with open(filename, "rb") as key_file:
        return key_file.read()

def encrypt_image(image_path, key):
    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(image_bytes)
    return encrypted_data

def decrypt_image(encrypted_data, key, output_path):
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data)
    with open(output_path, "wb") as out_file:
        out_file.write(decrypted_data)
