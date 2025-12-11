import requests
import json

# CHANGE ONLY THIS LINE — PUT YOUR REAL STUDENT ID HERE
STUDENT_ID = "22P31A4462"          # ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
# Example: STUDENT_ID = "GPP-2025-00876"

# Your GitHub repo URL — already correct
GITHUB_REPO_URL = "https://github.com/veeradevi08/pki-2fa-microservice"

# Instructor API endpoint
API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

# Step 1: Read your public key exactly as required (with \n line breaks preserved)
try:
    with open("student_public.pem", "r", encoding="utf-8") as f:
        public_key_pem = f.read().strip()   # removes any extra blank lines at end
except FileNotFoundError:
    print("ERROR: student_public.pem not found in the folder!")
    print("Make sure the file exists and you are running the script from the correct folder.")
    exit()

# Step 2: Prepare the exact JSON payload the instructor expects
payload = {
    "student_id": STUDENT_ID,
    "github_repo_url": GITHUB_REPO_URL,
    "public_key": public_key_pem
}

print("Sending request to instructor API...")
print(f"Student ID : {STUDENT_ID}")
print(f"Repo URL   : {GITHUB_REPO_URL}")
print("-" * 60)

# Step 3: Send the POST request
try:
    response = requests.post(API_URL, json=payload, timeout=15)
except requests.exceptions.RequestException as e:
    print("Network error:", e)
    exit()

# Step 4: Check response
if response.status_code == 200:
    data = response.json()
    if data.get("status") == "success" and "encrypted_seed" in data:
        encrypted_seed = data["encrypted_seed"]
        
        # Step 5: Save to file (never commit this file!)
        with open("encrypted_seed.txt", "w") as f:
            f.write(encrypted_seed)
        
        print("SUCCESS! Your encrypted seed has been saved to:")
        print("     encrypted_seed.txt")
        print("\nFirst 100 characters of the seed:")
        print(encrypted_seed[:100] + "...")
        print("\nYou can now continue building the microservice!")
    else:
        print("API returned error:", data)
else:
    print(f"HTTP {response.status_code} - Something went wrong")
    print(response.text)