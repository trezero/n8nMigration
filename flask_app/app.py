import os
import docker
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file if present

app = Flask(__name__)
CORS(app) # Initialize CORS for all routes

BACKUPS_DIR = '/app/n8n_backups' # This path is inside the migration_ui container
N8N_IMPORTER_CONTAINER_NAME = os.getenv('N8N_IMPORTER_CONTAINER_NAME', 'n8n_migration_target')
N8N_TARGET_ENCRYPTION_KEY = os.getenv('N8N_TARGET_ENCRYPTION_KEY')

client = docker.from_env()

import json # Add json import

def get_backup_files():
    """Scans the backup directory for .json files and extracts their 'name' field."""
    backup_items = []
    if not os.path.exists(BACKUPS_DIR):
        return backup_items
    
    for filename in os.listdir(BACKUPS_DIR):
        if filename.endswith('.json'):
            file_path = os.path.join(BACKUPS_DIR, filename)
            display_name = filename # Default to filename
            file_type = 'unknown' # Default file type
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        if 'name' in data:
                            display_name = data['name']
                        # Determine file type
                        if 'nodes' in data: # Workflows have a 'nodes' array
                            file_type = 'workflow'
                        elif 'data' in data and 'type' in data: # Credentials have 'data' and 'type'
                            file_type = 'credential'
                        else:
                            # Could be some other JSON structure, or a credential without a 'name'
                            # For now, if it has a 'name' but no 'nodes', assume credential for selection purposes
                            if 'name' in data:
                                file_type = 'credential' # Fallback for named JSONs not identified as workflows
                            else:
                                app.logger.warning(f"Could not determine type for {filename}, missing 'name', 'nodes', or 'data'/'type' keys.")
                    else:
                        app.logger.warning(f"Could not parse {filename} as a dictionary.")

            except Exception as e:
                app.logger.error(f"Error reading or parsing {filename}: {e}")
            backup_items.append({'filename': filename, 'displayName': display_name, 'file_type': file_type})
    return backup_items

def run_n8n_import_command(container_name, command_parts):
    """Executes a command inside the specified n8n container."""
    try:
        container = client.containers.get(container_name)
        full_command = ['n8n'] + command_parts
        app.logger.info(f"Executing command in {container_name}: {' '.join(full_command)}")
        
        # Prepare environment variables for the exec command
        exec_environment = {}
        if N8N_TARGET_ENCRYPTION_KEY:
            exec_environment['N8N_ENCRYPTION_KEY'] = N8N_TARGET_ENCRYPTION_KEY

        exit_code, output = container.exec_run(full_command, environment=exec_environment, demux=True)
        stdout, stderr = output
        
        stdout_str = stdout.decode('utf-8') if stdout else ''
        stderr_str = stderr.decode('utf-8') if stderr else ''
        app.logger.info(f"Exit code: {exit_code}")
        app.logger.info(f"STDOUT: {stdout_str}")
        app.logger.error(f"STDERR: {stderr_str}")

        if exit_code == 0:
            return True, stdout_str or "Command executed successfully."
        else:
            return False, f"Error (Code {exit_code}): {stderr_str or stdout_str or 'Unknown error'}"
    except docker.errors.NotFound:
        app.logger.error(f"Container {container_name} not found.")
        return False, f"Error: Container {container_name} not found."
    except Exception as e:
        app.logger.error(f"Exception during docker exec: {str(e)}")
        return False, f"Error: {str(e)}"

@app.route('/')
def index():
    backup_items = get_backup_files()
    return render_template('index.html', backup_items=backup_items, n8n_key_set=bool(N8N_TARGET_ENCRYPTION_KEY))

@app.route('/api/files', methods=['GET'])
def api_get_backup_files():
    backup_items = get_backup_files()
    return jsonify(backup_items)

@app.route('/import-workflows', methods=['POST'])
def import_workflows():
    if not N8N_TARGET_ENCRYPTION_KEY:
        return jsonify({'success': False, 'message': 'N8N_TARGET_ENCRYPTION_KEY is not set. Cannot import.'}), 400

    data = request.get_json()
    if not data or 'workflow_files' not in data:
        return jsonify({'success': False, 'message': 'Invalid JSON payload or missing workflow_files key.'}), 400
    selected_files = data['workflow_files']
    if not selected_files:
        return jsonify({'success': False, 'message': 'No workflow files selected.'}), 400

    results = []
    overall_success = True
    for file_name in selected_files:
        backup_file_path_in_container = f"/backups/{file_name}" # Path inside n8n_importer container
        command = ['import:workflow', f'--input={backup_file_path_in_container}']
        
        success, message = run_n8n_import_command(N8N_IMPORTER_CONTAINER_NAME, command)
        results.append({'file': file_name, 'success': success, 'message': message})
        if not success:
            overall_success = False
            
    return jsonify({'success': overall_success, 'results': results})

@app.route('/import-credentials', methods=['POST'])
def import_credentials():
    if not N8N_TARGET_ENCRYPTION_KEY:
        return jsonify({'success': False, 'message': 'N8N_TARGET_ENCRYPTION_KEY is not set. Cannot import credentials.'}), 400

    credential_file = request.form.get('credential_file')
    if not credential_file:
        return jsonify({'success': False, 'message': 'No credential file selected/specified.'}), 400

    backup_file_path_in_container = f"/backups/{credential_file}" # Path inside n8n_importer container
    command = ['import:credentials', f'--input={backup_file_path_in_container}']

    success, message = run_n8n_import_command(N8N_IMPORTER_CONTAINER_NAME, command)
    return jsonify({'success': success, 'message': message})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
