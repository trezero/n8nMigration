# n8n Migration Tool

This tool provides a simple web interface to help migrate n8n workflows and credentials from backup files to a new n8n instance, all running within Docker containers.

## Prerequisites

*   Docker: [Install Docker](https://docs.docker.com/get-docker/)
*   Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)

## Directory Structure

```
n8n_migrate/
├── .env                       # Your local environment configuration (create from .env.example)
├── .env.example               # Example environment variables
├── docker-compose.yml         # Docker Compose configuration
├── flask_app/                 # Flask application for the UI
│   ├── Dockerfile             # Dockerfile for the Flask app
│   ├── app.py                 # Main Flask application logic
│   ├── requirements.txt       # Python dependencies
│   └── templates/
│       └── index.html         # HTML template for the UI
├── n8n_backups/               # << PLACE YOUR EXPORTED .json FILES HERE
│   ├── your_workflow_export1.json
│   ├── your_workflow_export2.json
│   └── your_credentials_export.json
└── README.md                  # This file
```

## Setup Instructions

1.  **Prepare the Directory:**
    Ensure you have the `n8n_migrate` directory with all the files provided (or clone this repository if it's version controlled).

2.  **Configure Environment Variables:**
    *   Copy `.env.example` to a new file named `.env` in the `n8n_migrate` directory:
        ```bash
        cp .env.example .env
        ```
    *   Edit the `.env` file and set the `N8N_TARGET_ENCRYPTION_KEY`:
        ```env
        N8N_TARGET_ENCRYPTION_KEY=your_actual_n8n_encryption_key
        ```
        **IMPORTANT:** 
        *   This key is crucial for the target n8n instance (`n8n_importer` service) to correctly decrypt and use your credentials and any encrypted data within workflows.
        *   If your source n8n instance used an encryption key, you **must** use the same key here for successful import of encrypted data.
        *   If you are setting up a new n8n instance and want to use a new key, set it here. Workflows and credentials will be imported and then re-encrypted with this new key by the target n8n instance.
        *   If your source n8n did not use an encryption key, you can leave this blank or set a new one if you want the target instance to use encryption.

3.  **Add Backup Files:**
    *   Create the `n8n_backups` directory if it doesn't exist: `mkdir -p n8n_backups`
    *   Place your exported n8n workflow (`.json` files) and credentials (`.json` file) into the `n8n_migrate/n8n_backups/` directory.

## Running the Migration Tool

1.  **Start Services:**
    Navigate to the `n8n_migrate` directory in your terminal and run:
    ```bash
    docker-compose up --build -d
    ```
    *   `--build` ensures the Flask app image is built (or rebuilt if changes were made).
    *   `-d` runs the containers in detached mode (in the background).

2.  **Access the UI:**
    Open your web browser and go to: [http://localhost:5000](http://localhost:5000)

3.  **Access the Target n8n Instance (Optional):**
    You can access the new n8n instance directly at: [http://localhost:5679](http://localhost:5679)
    This is useful for verifying that workflows and credentials have been imported correctly.

## Using the Web Interface

The web interface at [http://localhost:5000](http://localhost:5000) will allow you to:

*   **View Backup Files:** It lists all `.json` files found in your `n8n_backups` directory.
*   **Import Workflows:**
    *   Check the boxes next to the workflow files you want to import.
    *   Click the "Import Selected Workflows" button.
    *   Results for each file will be displayed.
*   **Import Credentials:**
    *   Select your credentials backup file from the dropdown menu.
    *   Click the "Import Credentials" button.
    *   The result of the import will be displayed.

    **Note on Credentials Import:** n8n typically uses a single file for all credentials. The import process will replace any existing credentials in the target n8n instance with those from the selected file.

## Important Notes

*   **Encryption Key:** The `N8N_TARGET_ENCRYPTION_KEY` is critical. If it's missing or incorrect, credential import will fail, and workflows with encrypted data may not function correctly.
*   **Docker Socket:** The Flask UI container mounts the Docker socket (`/var/run/docker.sock`). This allows it to execute `docker exec` commands against the `n8n_importer` container to run the n8n CLI import commands.
*   **File Paths:** The Flask app reads backup files from `/app/n8n_backups` (its internal path), which is mapped from `./n8n_backups` on your host. The n8n CLI commands executed inside the `n8n_importer` container will refer to these files via `/backups` (its internal path), also mapped from `./n8n_backups` on your host.

## Stopping the Services

To stop the Docker containers, navigate to the `n8n_migrate` directory and run:

```bash
docker-compose down
```

This will stop and remove the containers. Your n8n data (in `n8n_importer_data` volume) and backup files will persist.
To remove the data volume as well (e.g., for a fresh start), run:

```bash
docker-compose down -v
```

## Troubleshooting

*   **Check Container Logs:** If something goes wrong, check the logs for each service:
    ```bash
    docker-compose logs n8n_importer
    docker-compose logs migration_ui
    ```
*   **Permissions:** Ensure Docker has the necessary permissions to mount directories and the Docker socket.
*   **Encryption Key Mismatch:** If imports fail, especially credentials, double-check the `N8N_TARGET_ENCRYPTION_KEY`.
*   **File Not Found in UI:** Ensure your `.json` backup files are directly inside the `n8n_backups` folder (not in subdirectories) and that the `migration_ui` service has restarted if you added them after `docker-compose up`.
