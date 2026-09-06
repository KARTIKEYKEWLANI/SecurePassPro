from cryptography.fernet import Fernet

# Generate a new symmetric key
def generate_key():
    return Fernet.generate_key()

# Save the key to a file (binary mode)
def save_key(key, filename="secret.key"):
    with open(filename, "wb") as key_file:
        key_file.write(key)

# Load the key from a file
def load_key(filename="secret.key"):
    with open(filename, "rb") as key_file:
        return key_file.read()

# Encrypt a plain text message and return bytes
def encrypt_text(message, key):
    fernet = Fernet(key)
    encrypted_message = fernet.encrypt(message.encode())  # Convert string to bytes
    return encrypted_message

# Decrypt from bytes back to plain text
def decrypt_text(encrypted_message, key):
    fernet = Fernet(key)
    decrypted_message = fernet.decrypt(encrypted_message).decode()  # Convert bytes to string
    return decrypted_message

def encrypt_text_to_file(message, key, filename="encrypted_text.bin"):
    encrypted_message = encrypt_text(message, key)
    with open(filename, "wb") as f:
        f.write(encrypted_message)

def decrypt_text_from_file(key, filename="encrypted_text.bin"):
    with open(filename, "rb") as f:
        encrypted_message = f.read()
    return decrypt_text(encrypted_message, key)
