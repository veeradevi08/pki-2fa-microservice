from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Generate exactly 4096-bit key with exponent 65537
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096
)

# Private key PEM
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
).decode('utf-8')

# Public key PEM
public_pem = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode('utf-8')

# Save both files
with open("student_private.pem", "w", newline='\n') as f:
    f.write(private_pem)
with open("student_public.pem", "w", newline='\n') as f:
    f.write(public_pem)

print("Keys generated successfully!")
print("student_private.pem and student_public.pem created in your project folder.")