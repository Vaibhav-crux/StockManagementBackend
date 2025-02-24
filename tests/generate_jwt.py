import os
secret_key = os.urandom(24)  # Generates a 24-byte random key
print(secret_key.hex())  # This will display the secret key in hexadecimal format
