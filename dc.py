from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import binascii

def encrypt_data(data):
    # Convert key and data to bytes
    key = "qwertyuioplkjhgf"
    key_bytes = key.encode('utf-8')
    data_bytes = data.encode('utf-8')

    # Pad the data using PKCS#7
    padded_data = pad(data_bytes, AES.block_size)

    # Initialize AES cipher in ECB mode
    cipher = AES.new(key_bytes, AES.MODE_ECB)

    # Encrypt the data
    encrypted_data = cipher.encrypt(padded_data)

    # Convert encrypted bytes to hexadecimal string
    encrypted_hex = binascii.hexlify(encrypted_data).decode('utf-8')

    return encrypted_hex

# Example usage

