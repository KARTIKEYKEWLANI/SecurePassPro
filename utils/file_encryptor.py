from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key()

def encrypt_file_data(data, key):
    fernet = Fernet(key)
    return fernet.encrypt(data)

def decrypt_file_data(encrypted_data, key):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data)

def save_key(key, filename="file.key"):
    with open(filename, "wb") as key_file:
        key_file.write(key)

def load_key(filename="file.key"):
    with open(filename, "rb") as key_file:
        return key_file.read()

def encrypt_file(input_path, key):
    with open(input_path, "rb") as file:
        file_data = file.read()
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(file_data)

    encrypted_path = input_path + ".enc"
    with open(encrypted_path, "wb") as f:
        f.write(encrypted_data)
    return encrypted_path

def decrypt_file(input_path, key, output_path):
    with open(input_path, "rb") as file:
        encrypted_data = file.read()
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data)

    with open(output_path, "wb") as f:
        f.write(decrypted_data)
    return output_path
