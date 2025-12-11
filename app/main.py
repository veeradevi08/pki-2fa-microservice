from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import base64
import pyotp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from pathlib import Path
import datetime

app = FastAPI(title="PKI-Based 2FA Microservice")

DATA_DIR = Path("/data")
SEED_FILE = DATA_DIR / "seed.txt"
PRIVATE_KEY_PATH = Path("/app/student_private.pem")

# Load private key at startup
def load_private_key():
    try:
        with open(PRIVATE_KEY_PATH, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)
    except Exception as e:
        print(f"[ERROR] Failed to load private key: {e}")
        return None

private_key = load_private_key()

class DecryptPayload(BaseModel):
    encrypted_seed: str

class VerifyPayload(BaseModel):
    code: str

@app.post("/decrypt-seed")
async def decrypt_seed(payload: DecryptPayload):
    if not private_key:
        raise HTTPException(500, {"error": "Private key not available"})
    
    try:
        encrypted = base64.b64decode(payload.encrypted_seed)
        decrypted = private_key.decrypt(
            encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        hex_seed = decrypted.decode("utf-8").strip().lower()
        
        if len(hex_seed) != 64 or not all(c in "0123456789abcdef" for c in hex_seed):
            raise ValueError("Invalid seed")
        
        DATA_DIR.mkdir(exist_ok=True)
        SEED_FILE.write_text(hex_seed)
        return {"status": "ok"}
    except Exception as e:
        print(f"[ERROR] Decryption failed: {e}")
        raise HTTPException(500, {"error": "Decryption failed"})

def get_totp():
    if not SEED_FILE.exists():
        return None
    hex_seed = SEED_FILE.read_text().strip()
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode()
    return pyotp.TOTP(base32_seed, digits=6, interval=30)

@app.get("/generate-2fa")
async def generate_2fa():
    totp = get_totp()
    if not totp:
        raise HTTPException(500, {"error": "Seed not decrypted yet"})
    code = totp.now()
    valid_for = 30 - (int(datetime.datetime.utcnow().timestamp()) % 30)
    return {"code": code, "valid_for": valid_for}

@app.post("/verify-2fa")
async def verify_2fa(payload: VerifyPayload):
    if not payload.code:
        raise HTTPException(400, {"error": "Missing code"})
    
    totp = get_totp()
    if not totp:
        raise HTTPException(500, {"error": "Seed not decrypted yet"})
    
    return {"valid": totp.verify(payload.code, valid_window=1)}