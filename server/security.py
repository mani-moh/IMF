from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

def generate_key(password: str, salt: bytes = None) -> bytes:
    """Generate encryption key from password"""
    if salt is None:
        salt = os.urandom(16)  # Generate a random salt

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt


def encrypt_file(file_path: str, key: bytes, output_path: str = None) -> bytes:
    """Encrypt a file and return the encrypted data"""
    with open(file_path, 'rb') as f:
        file_data = f.read()

    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(file_data)

    if output_path:
        with open(output_path, 'wb') as f:
            f.write(encrypted_data)

    return encrypted_data


def decrypt_file(encrypted_data: bytes, key: bytes, output_path: str = None) -> bytes:
    """Decrypt file data and optionally save to file"""
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data)

    if output_path:
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)

    return decrypted_data



def generate_master_key():
    """
    Generates a master encryption key and saves it to a file.
    This should only be run ONCE.
    """
    key_file = "server_master.key"
    if os.path.exists(key_file):
        return

    key = Fernet.generate_key()
    with open(key_file, "wb") as f:
        f.write(key)
    print(f"Successfully generated and saved master key to '{key_file}'.")
    print("Store this file securely and do not share it.")
    return key



if __name__ == "__main__":
    try:
        with open("server_master.key", "rb") as f:
            master_key = f.read()
        master_fernet = Fernet(master_key)
        print("Server master key loaded successfully.")
    except FileNotFoundError:
        print("server_master.key not found.")
    #encrypt_file("database/files/nuclear_files/nuc.txt", master_key, "database/files/nuclear_files/nuc.txt")
