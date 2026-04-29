import os
import json
import argparse
import uuid
import shutil
import subprocess
from dotenv import load_dotenv

# Define paths relative to this script (project root)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(PROJECT_ROOT, '.env')

# Load environment variables from .env file
if os.path.exists(DOTENV_PATH):
    load_dotenv(dotenv_path=DOTENV_PATH)
    print(f"Loaded environment variables from: {DOTENV_PATH}")
else:
    print(f"Warning: .env file not found at {DOTENV_PATH}. Environment variables might not be loaded.")

N8N_TARGET_ENCRYPTION_KEY = os.getenv('N8N_TARGET_ENCRYPTION_KEY')
N8N_TARGET_USER_FOLDER = os.getenv('N8N_TARGET_USER_FOLDER')
FLASK_APP_DIR = os.path.join(PROJECT_ROOT, 'flask_app')
WORKFLOWS_FILE = os.path.join(FLASK_APP_DIR, 'workflows.json')
CREDENTIALS_FILE = os.path.join(FLASK_APP_DIR, 'credentials.json')
TEMP_IMPORT_DIR_HOST = os.path.join(PROJECT_ROOT, 'tmp_cli_imports')

def run_local_n8n_command(command_parts, input_file_path, environment_vars=None):
    """Executes a local n8n command using subprocess."""
    try:
        cmd = ['n8n'] + command_parts + [f'--input={input_file_path}']
        
        # Prepare environment for subprocess
        process_env = os.environ.copy()
        if environment_vars:
            process_env.update(environment_vars)

        print(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, env=process_env, check=False)
        
        if result.returncode == 0:
            print(f"Success: {result.stdout.strip()}")
            return True, result.stdout.strip()
        else:
            error_message = f"Error (Code {result.returncode}): {result.stderr.strip()} {result.stdout.strip()}".strip()
            print(error_message)
            return False, error_message
    except FileNotFoundError:
        msg = "Error: 'n8n' command not found. Make sure n8n is installed and in your system's PATH."
        print(msg)
        return False, msg
    except Exception as e:
        msg = f"An unexpected error occurred: {e}"
        print(msg)
        return False, msg

def import_workflows():
    """Imports workflows from workflows.json."""
    if not os.path.exists(WORKFLOWS_FILE):
        print(f"Error: Workflows file not found at {WORKFLOWS_FILE}")
        return

    with open(WORKFLOWS_FILE, 'r', encoding='utf-8') as f:
        workflows_data = json.load(f)

    if not workflows_data:
        print("No workflows found in workflows.json to import.")
        return

    print(f"Found {len(workflows_data)} workflows to import.")
    overall_success = True

    for wf_data in workflows_data:
        wf_name = wf_data.get('name', 'Unnamed Workflow')
        temp_filename = f"temp_workflow_{uuid.uuid4()}.json"
        temp_filepath_host = os.path.join(TEMP_IMPORT_DIR_HOST, temp_filename)

        try:
            with open(temp_filepath_host, 'w', encoding='utf-8') as f:
                json.dump(wf_data, f, indent=2)
            
            command_parts = ['import:workflow']
            env_vars = {
                'DB_TYPE': 'postgresdb',
                'DB_POSTGRESDB_HOST': 'localhost', # Assuming PG is on localhost from host's perspective
                'DB_POSTGRESDB_PORT': '5432',      # Default PG port
                'DB_POSTGRESDB_USER': 'postgres',
                'DB_POSTGRESDB_DATABASE': 'postgres'
            }
            if os.getenv('POSTGRES_PASSWORD'):
                env_vars['DB_POSTGRESDB_PASSWORD'] = os.getenv('POSTGRES_PASSWORD')
            else:
                print("Warning: POSTGRES_PASSWORD not found in .env. Database connection might fail.")

            if N8N_TARGET_ENCRYPTION_KEY:
                env_vars['N8N_ENCRYPTION_KEY'] = N8N_TARGET_ENCRYPTION_KEY
            if N8N_TARGET_USER_FOLDER:
                env_vars['N8N_USER_FOLDER'] = N8N_TARGET_USER_FOLDER
            success, message = run_local_n8n_command(command_parts, temp_filepath_host, environment_vars=env_vars)
            print(f"Importing workflow '{wf_name}': {'Success' if success else 'Failed'}") # Message already printed by run_local_n8n_command
            if not success:
                overall_success = False
        except Exception as e:
            print(f"Error processing workflow {wf_name} for import: {e}")
            overall_success = False
    
    print("Workflow import process completed." if overall_success else "Workflow import process completed with errors.")

def import_credentials():
    """Imports credentials from credentials.json."""
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Error: Credentials file not found at {CREDENTIALS_FILE}")
        return

    with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
        credentials_data = json.load(f)

    if not credentials_data:
        print("No credentials found in credentials.json to import.")
        return

    print(f"Found {len(credentials_data)} credentials to import.")
    temp_filename = f"temp_credentials_{uuid.uuid4()}.json"
    temp_filepath_host = os.path.join(TEMP_IMPORT_DIR_HOST, temp_filename)

    try:
        with open(temp_filepath_host, 'w', encoding='utf-8') as f:
            json.dump(credentials_data, f, indent=2) # n8n expects an array of credentials

        command_parts = ['import:credentials']
        env_vars = {
            'DB_TYPE': 'postgresdb',
            'DB_POSTGRESDB_HOST': 'localhost', # Assuming PG is on localhost from host's perspective
            'DB_POSTGRESDB_PORT': '5432',      # Default PG port
            'DB_POSTGRESDB_USER': 'postgres',
            'DB_POSTGRESDB_DATABASE': 'postgres'
        }
        if os.getenv('POSTGRES_PASSWORD'):
            env_vars['DB_POSTGRESDB_PASSWORD'] = os.getenv('POSTGRES_PASSWORD')
        else:
            print("Warning: POSTGRES_PASSWORD not found in .env. Database connection might fail.")
            
        if N8N_TARGET_ENCRYPTION_KEY:
            env_vars['N8N_ENCRYPTION_KEY'] = N8N_TARGET_ENCRYPTION_KEY
        if N8N_TARGET_USER_FOLDER:
            env_vars['N8N_USER_FOLDER'] = N8N_TARGET_USER_FOLDER
        success, message = run_local_n8n_command(command_parts, temp_filepath_host, environment_vars=env_vars)
        print(f"Importing credentials: {'Success' if success else 'Failed'}") # Message already printed
    except Exception as e:
        print(f"Error processing credentials for import: {e}")
    
    print("Credentials import process completed.")

def main():
    parser = argparse.ArgumentParser(description='n8n CLI Importer Tool (Local n8n).')
    parser.add_argument('--workflows', action='store_true', help='Import all workflows from flask_app/workflows.json')
    parser.add_argument('--credentials', action='store_true', help='Import all credentials from flask_app/credentials.json')
    parser.add_argument('--all', action='store_true', help='Import both workflows and credentials')

    args = parser.parse_args()

    if not N8N_TARGET_ENCRYPTION_KEY:
        print("Warning: N8N_TARGET_ENCRYPTION_KEY is not set in .env file. Imports may fail for encrypted items.")
    if not N8N_TARGET_USER_FOLDER:
        print("Warning: N8N_TARGET_USER_FOLDER is not set in .env file. The script might target the default n8n data directory.")

    # Create temporary directory for staging import files
    if os.path.exists(TEMP_IMPORT_DIR_HOST):
        shutil.rmtree(TEMP_IMPORT_DIR_HOST) # Clean up if exists
    os.makedirs(TEMP_IMPORT_DIR_HOST)
    print(f"Created temporary import directory: {TEMP_IMPORT_DIR_HOST}")

    try:
        if args.all or args.workflows:
            print("\n--- Starting Workflow Import ---")
            import_workflows()
        
        if args.all or args.credentials:
            print("\n--- Starting Credential Import ---")
            import_credentials()

        if not (args.workflows or args.credentials or args.all):
            parser.print_help()
            print("\nPlease specify --workflows, --credentials, or --all.")

    finally:
        # Clean up temporary directory
        if os.path.exists(TEMP_IMPORT_DIR_HOST):
            shutil.rmtree(TEMP_IMPORT_DIR_HOST)
            print(f"Cleaned up temporary import directory: {TEMP_IMPORT_DIR_HOST}")

if __name__ == '__main__':
    main()
