import os
import docker
from flask import Flask, request, jsonify, render_template # Added render_template
from flask_cors import CORS # Import CORS
from dotenv import load_dotenv
import json
import uuid # For temporary file names

load_dotenv() 

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Define base directory for the app, expecting workflows.json and credentials.json here
# This path is inside the migration_ui container.
APP_DATA_DIR = app.root_path # This will be /app in the container
TEMP_IMPORT_SUBDIR = "tmp_imports"
TEMP_IMPORT_FULL_PATH = os.path.join(APP_DATA_DIR, TEMP_IMPORT_SUBDIR)

# Ensure the temporary import subdirectory exists
if not os.path.exists(TEMP_IMPORT_FULL_PATH):
    try:
        os.makedirs(TEMP_IMPORT_FULL_PATH)
        app.logger.info(f"Created temporary import directory: {TEMP_IMPORT_FULL_PATH}")
    except OSError as e:
        app.logger.error(f"Could not create temporary import directory {TEMP_IMPORT_FULL_PATH}: {e}")

WORKFLOWS_FILE = os.path.join(APP_DATA_DIR, 'workflows.json')
CREDENTIALS_FILE = os.path.join(APP_DATA_DIR, 'credentials.json')

N8N_IMPORTER_CONTAINER_NAME = os.getenv('N8N_IMPORTER_CONTAINER_NAME', 'n8n_migration_target')
N8N_TARGET_ENCRYPTION_KEY = os.getenv('N8N_TARGET_ENCRYPTION_KEY')

# Docker client will be initialized lazily within run_n8n_command

def run_n8n_command(container_name, command_parts, environment_vars=None):
    """Executes a command inside the specified n8n container."""
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        
        base_environment = {
            'N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS': 'true', # n8n often suggests this
            'N8N_RUNNERS_ENABLED': 'true' # May or may not be needed for import
        }
        if N8N_TARGET_ENCRYPTION_KEY:
            base_environment['N8N_ENCRYPTION_KEY'] = N8N_TARGET_ENCRYPTION_KEY
        
        if environment_vars:
            base_environment.update(environment_vars)

        full_command = ['n8n'] + command_parts
        app.logger.info(f"Executing command in {container_name}: {' '.join(full_command)}")
        app.logger.debug(f"Environment for exec: {base_environment}")
        
        exit_code, output = container.exec_run(full_command, environment=base_environment, demux=True)
        stdout, stderr = output
        
        stdout_str = stdout.decode('utf-8') if stdout else ''
        stderr_str = stderr.decode('utf-8') if stderr else ''
        
        app.logger.info(f"Exit code: {exit_code}")
        if stdout_str:
            app.logger.info(f"STDOUT: {stdout_str}")
        if stderr_str:
            app.logger.error(f"STDERR: {stderr_str}")
        
        if exit_code == 0:
            return True, stdout_str or "Command executed successfully."
        else:
            # Prepend "Error (Code X): " to the message if not already present
            error_prefix = f"Error (Code {exit_code}): "
            message = stderr_str or stdout_str or 'Unknown error during n8n command execution.'
            if not message.strip().startswith("Error (Code"):
                 message = error_prefix + message
            return False, message
            
    except docker.errors.NotFound:
        app.logger.error(f"Container {container_name} not found.")
        return False, f"Error: Container {container_name} not found."
    except docker.errors.APIError as e:
        app.logger.error(f"Docker API error: {str(e)}")
        return False, f"Error: Docker API error - {str(e)}"
    except Exception as e:
        app.logger.error(f"Exception during docker exec: {str(e)}")
        return False, f"Error: An unexpected error occurred - {str(e)}"

@app.route('/api/files', methods=['GET'])
def api_get_files():
    workflows = []
    credentials = []

    try:
        if os.path.exists(WORKFLOWS_FILE):
            with open(WORKFLOWS_FILE, 'r', encoding='utf-8') as f:
                wf_data = json.load(f)
                for index, wf in enumerate(wf_data):
                    workflows.append({
                        'name': wf.get('name', f'Workflow {index + 1}'),
                        'key': f'wf_{index}', 
                        'data': wf 
                    })
        else:
            app.logger.warning(f"{WORKFLOWS_FILE} not found.")
    except Exception as e:
        app.logger.error(f"Error reading or parsing {WORKFLOWS_FILE}: {e}")

    try:
        if os.path.exists(CREDENTIALS_FILE):
            with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
                cred_data = json.load(f)
                for cred in cred_data:
                    credentials.append({
                        'id': cred.get('id'),
                        'name': cred.get('name', 'Unnamed Credential'),
                        'type': cred.get('type'),
                        'data': cred 
                    })
        else:
            app.logger.warning(f"{CREDENTIALS_FILE} not found.")
    except Exception as e:
        app.logger.error(f"Error reading or parsing {CREDENTIALS_FILE}: {e}")
        
    return jsonify({'workflows': workflows, 'credentials': credentials})

@app.route('/api/import-workflows', methods=['POST'])
def api_import_workflows():
    if not N8N_TARGET_ENCRYPTION_KEY:
        return jsonify({'success': False, 'message': 'N8N_TARGET_ENCRYPTION_KEY is not set. Cannot import workflows.'}), 400

    data = request.get_json()
    if not data or 'workflows_to_import' not in data:
        return jsonify({'success': False, 'message': 'Missing "workflows_to_import" in request body.'}), 400

    selected_workflows = data['workflows_to_import']
    if not isinstance(selected_workflows, list) or not selected_workflows:
        return jsonify({'success': False, 'message': '"workflows_to_import" must be a non-empty list.'}), 400

    results = []
    overall_success = True

    for wf_data in selected_workflows:
        if not isinstance(wf_data, dict):
            results.append({'name': 'Unknown Workflow', 'success': False, 'message': 'Invalid workflow data format.'})
            overall_success = False
            continue

        wf_name = wf_data.get('name', 'Unnamed Workflow')
        temp_filename = f"temp_workflow_{uuid.uuid4()}.json"
        temp_filepath_host = os.path.join(TEMP_IMPORT_FULL_PATH, temp_filename) 
        temp_filepath_container = f"/app/{TEMP_IMPORT_SUBDIR}/{temp_filename}" 

        try:
            with open(temp_filepath_host, 'w', encoding='utf-8') as f:
                json.dump(wf_data, f, indent=2) 

            command = ['import:workflow', f'--input={temp_filepath_container}']
            success, message = run_n8n_command(N8N_IMPORTER_CONTAINER_NAME, command)
            results.append({'name': wf_name, 'success': success, 'message': message})
            if not success:
                overall_success = False
        except Exception as e:
            app.logger.error(f"Error processing workflow {wf_name}: {e}")
            results.append({'name': wf_name, 'success': False, 'message': f"Internal server error: {e}"})
            overall_success = False
        finally:
            if os.path.exists(temp_filepath_host):
                try:
                    os.remove(temp_filepath_host)
                except Exception as e:
                    app.logger.error(f"Error deleting temporary file {temp_filepath_host}: {e}")
            
    return jsonify({'success': overall_success, 'results': results})

@app.route('/api/import-credentials', methods=['POST'])
def api_import_credentials():
    if not N8N_TARGET_ENCRYPTION_KEY:
        return jsonify({'success': False, 'message': 'N8N_TARGET_ENCRYPTION_KEY is not set. Cannot import credentials.'}), 400

    data = request.get_json()
    if not data or 'credentials_to_import' not in data:
        return jsonify({'success': False, 'message': 'Missing "credentials_to_import" in request body.'}), 400
        
    selected_credentials = data['credentials_to_import']
    if not isinstance(selected_credentials, list) or not selected_credentials:
         return jsonify({'success': False, 'message': '"credentials_to_import" must be a non-empty list of credential objects.'}), 400

    temp_filename = f"temp_credentials_{uuid.uuid4()}.json"
    temp_filepath_host = os.path.join(TEMP_IMPORT_FULL_PATH, temp_filename) 
    temp_filepath_container = f"/app/{TEMP_IMPORT_SUBDIR}/{temp_filename}" 
    
    success = False
    message = "No credentials processed."

    try:
        with open(temp_filepath_host, 'w', encoding='utf-8') as f:
            json.dump(selected_credentials, f, indent=2)

        command = ['import:credentials', f'--input={temp_filepath_container}']
        success, message = run_n8n_command(N8N_IMPORTER_CONTAINER_NAME, command)
        
    except Exception as e:
        app.logger.error(f"Error processing credentials for import: {e}")
        success = False
        message = f"Internal server error: {e}"
    finally:
        if os.path.exists(temp_filepath_host):
            try:
                os.remove(temp_filepath_host)
            except Exception as e:
                app.logger.error(f"Error deleting temporary file {temp_filepath_host}: {e}")

    return jsonify({'success': success, 'message': message})

@app.route('/')
def index():
    return render_template('index.html', n8n_key_set=bool(N8N_TARGET_ENCRYPTION_KEY))

@app.route('/import-workflows', methods=['POST'])
def old_import_workflows():
    if request.content_type == 'application/json':
        return api_import_workflows()

    if not N8N_TARGET_ENCRYPTION_KEY:
        return jsonify({'success': False, 'message': 'N8N_TARGET_ENCRYPTION_KEY is not set. Cannot import.'}), 400
    # Minimal old logic placeholder
    selected_files = request.form.getlist('workflow_files') # Example of old form access
    if not selected_files:
        return jsonify({'success': False, 'message': 'Old endpoint: No workflow files selected via form.'}), 400
    # Actual import logic for old form-based submission would go here
    # For now, just indicating it's the old path
    return jsonify({'success': False, 'message': f'Old endpoint received form data for {selected_files}. Transition to /api/import-workflows.'}), 400


@app.route('/import-credentials', methods=['POST'])
def old_import_credentials():
    if request.content_type == 'application/json':
        return api_import_credentials()

    if not N8N_TARGET_ENCRYPTION_KEY:
        return jsonify({'success': False, 'message': 'N8N_TARGET_ENCRYPTION_KEY is not set. Cannot import credentials.'}), 400
    # Minimal old logic placeholder
    credential_file = request.form.get('credential_file') # Example of old form access
    if not credential_file:
        return jsonify({'success': False, 'message': 'Old endpoint: No credential file selected/specified via form.'}), 400
    # Actual import logic for old form-based submission would go here
    return jsonify({'success': False, 'message': f'Old endpoint received form data for {credential_file}. Transition to /api/import-credentials.'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
