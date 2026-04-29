# n8n Credential Import Automation

This simple Python tool allows you to import exported n8n credentials into your n8n instance via API.

## ⚠ IMPORTANT NOTE

- This script assumes you already have an exported credentials JSON file from n8n.
- The exported file includes encrypted credential `data` fields that cannot be automatically decrypted via API.
- You will need to manually reconstruct (or decrypt) the credential `data` fields before importing, or modify the script to handle only credentials that do not store sensitive data.

---

## Prerequisites

- Python 3.x installed
- Access to your exported credential file (e.g. `credentials_export.json`)
- Your n8n instance URL
- Your n8n API Key (must be enabled and authorized to create credentials)

---

## Configuration

Edit the following variables at the top of the script:

```python
N8N_API_URL = 'https://n8nwhiteshark.damiam.com:5678/api/v1/credentials'
N8N_API_KEY = '<your-n8n-api-key>'
EXPORT_FILE = 'credentials_export.json'

```

N8N_API_URL: The full URL to your n8n instance’s credential API.

N8N_API_KEY: Your n8n personal API key.

EXPORT_FILE: Path to your exported credentials file.

## Usage

1. Place your exported credential JSON file in the same folder as the script, e.g. `credentials_export.json`.

2. Manually update each credential object inside the file to reconstruct the decrypted data fields.

For example:

```json
{
  "name": "My API Key Credential",
  "type": "httpBasicAuth",
  "nodesAccess": [],
  "data": {
    "user": "myusername",
    "password": "mypassword"
  }
}
⚠ The data field must contain raw decrypted values for each credential type.

3. Run the script:

```bash
python3 n8n_credential_importer.py
```
4. The script will:

Load all credentials from your file.

Clean up any unsupported fields.

Submit each credential to your n8n instance.

Print status for each imported credential.

## Output Example

```text
Preparing to import credential: Ollama account (ollamaApi)
Successfully imported: Ollama account
Preparing to import credential: Mattermost account (mattermostApi)
Successfully imported: Mattermost account
```

## Limitations
Only supports credential import (not workflows, triggers, etc).

Cannot decrypt encrypted data fields automatically.

Imports one credential at a time using the n8n API.

## Full Automation
If you need a fully automated decrypt + import tool, you'll need to provide:

The encryption key file from your .n8n directory (encryptionKey).

Full credential export file.

