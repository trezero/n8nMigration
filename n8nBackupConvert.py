import os
import json

# Define the source directory for backups and output directory for consolidated files
BACKUP_DIR = "n8n_backups"
OUTPUT_DIR = "flask_app" # Save into flask_app directory
CREDENTIALS_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "credentials.json")
WORKFLOWS_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "workflows.json")

def is_workflow(data):
    """Checks if the provided data object is an n8n workflow."""
    return isinstance(data, dict) and "nodes" in data and isinstance(data["nodes"], list)

def main():
    all_credentials = []
    all_workflows = []

    if not os.path.isdir(OUTPUT_DIR):
        try:
            os.makedirs(OUTPUT_DIR)
            print(f"Created output directory '{OUTPUT_DIR}'.")
        except OSError as e:
            print(f"Error: Could not create output directory '{OUTPUT_DIR}': {e}")
            return

    if not os.path.isdir(BACKUP_DIR):
        print(f"Error: Backup directory '{BACKUP_DIR}' not found.")
        return

    print(f"Processing files in '{BACKUP_DIR}'...")

    for filename in os.listdir(BACKUP_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(BACKUP_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if is_workflow(data):
                    all_workflows.append(data)
                    print(f"  Added '{filename}' to workflows.")
                else:
                    all_credentials.append(data)
                    print(f"  Added '{filename}' to credentials.")

            except json.JSONDecodeError:
                print(f"  Warning: Could not decode JSON from '{filename}'. Skipping.")
            except Exception as e:
                print(f"  Warning: Error processing file '{filename}': {e}. Skipping.")

    # Write the consolidated credentials file
    try:
        with open(CREDENTIALS_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_credentials, f, indent=2)
        print(f"\nSuccessfully created '{CREDENTIALS_OUTPUT_FILE}' with {len(all_credentials)} credentials.")
    except Exception as e:
        print(f"Error writing credentials file: {e}")

    # Write the consolidated workflows file
    try:
        with open(WORKFLOWS_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_workflows, f, indent=2)
        print(f"Successfully created '{WORKFLOWS_OUTPUT_FILE}' with {len(all_workflows)} workflows.")
    except Exception as e:
        print(f"Error writing workflows file: {e}")

if __name__ == "__main__":
    main()
