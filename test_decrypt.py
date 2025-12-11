import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# Load private key
with open("student_private.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

# Load encrypted seed
with open("encrypted_seed.txt", "r") as f:
    encrypted_b64 = f.read().strip()

# Decrypt
encrypted = base64.b64decode(encrypted_b64)
decrypted = private_key.decrypt(
    encrypted,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
hex_seed = decrypted.decode('utf-8')

# Validate: 64-char hex
if len(hex_seed) == 64 and all(c in '0123456789abcdefABCDEF' for c in hex_seed):
    print("Decrypted seed:", hex_seed)
else:
    print("Invalid seed format")