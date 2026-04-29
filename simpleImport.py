import json
import requests

# === CONFIGURATION ===
N8N_API_URL = 'https://n8nwhiteshark.damiam.com:5678/api/v1/credentials'
N8N_API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzNWNmMjNiOS1iNzYxLTRmZjUtOTQxOC1lMjIzY2M0Y2ViMGEiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzQ5OTY2NTIyfQ.sgxvxjrD3Ifrm-2NwhWTlhJysGqmYmY5dFKGQxsxOOI'

EXPORT_FILE = 'credentials.json'

# === LOAD YOUR EXPORT FILE ===
with open(EXPORT_FILE, 'r') as f:
    exported_credentials = json.load(f)

for credential in exported_credentials:
    # Strip out fields not accepted by the API
    payload = {
        "name": credential["name"],
        "type": credential["type"],
        "nodesAccess": [],  # Assuming default open access
        "data": {}  # Placeholder for decrypted data
    }

    # === ⚠ MANUAL STEP ===
    # You'll need to reconstruct this with decrypted data.
    # For now we leave it empty
    print(f"Preparing to import credential: {credential['name']} ({credential['type']})")

    response = requests.post(
        N8N_API_URL,
        headers={
            "Authorization": f"Bearer {N8N_API_KEY}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    if response.ok:
        print(f"Successfully imported: {credential['name']}")
    else:
        print(f"Failed to import: {credential['name']} -> {response.text}")
