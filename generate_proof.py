import subprocess
import hashlib
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# Get latest commit hash
commit_hash = subprocess.check_output(["git", "log", "-1", "--format=%H"]).decode().strip()
print("Commit Hash :", commit_hash)

# Load your private key
with open("student_private.pem", "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

# Sign the commit hash (RSA-PSS-SHA256 (sign the ASCII string)
signature = private_key.sign(
    commit_hash.encode("utf-8"),
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

# Load instructor public key
with open("instructor_public.pem", "rb") as f:
    instructor_pub = serialization.load_pem_public_key(f.read())

# Encrypt signature with instructor's public key (RSA-OAEP-SHA256)
encrypted_sig = instructor_pub.encrypt(
    signature,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Base64 encode
import base64
final_proof = base64.b64encode(encrypted_sig).decode()

print("\nENCRYPTED SIGNATURE (copy this exactly):")
print(final_proof)
print("\nSubmit this in the form!")