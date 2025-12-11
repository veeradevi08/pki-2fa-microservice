#!/usr/bin/env python3
import pyotp
import base64
import datetime
import os
import sys

SEED_FILE = "/data/seed.txt"
LOG_FILE = "/cron/last_code.txt"

# If seed file doesn't exist → just exit silently with error
if not os.path.exists(SEED_FILE):
    print("ERROR: Seed file not found at /data/seed.txt", file=sys.stderr)
    sys.exit(1)

try:
    # Read the 64-char hex seed
    hex_seed = open(SEED_FILE, "r").read().strip()
    
    # Convert hex → bytes → base32 (exactly as required)
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
    
    # Generate TOTP code
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30)
    code = totp.now()
    
    # UTC timestamp in the exact format required
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    # Final line
    line = f"{timestamp} - 2FA Code: {code}\n"
    
    # Append to log file
    with open(LOG_FILE, "a") as f:
        f.write(line)
    
    # Also print to stdout so you can see it in Docker logs
    print(line.strip())

except Exception as e:
    print(f"CRON ERROR: {e}", file=sys.stderr)
    sys.exit(1)