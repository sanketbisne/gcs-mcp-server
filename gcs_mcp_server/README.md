# MyEnhancedGCSMCPServer

A `fastmcp` server that exposes a comprehensive set of tools for managing Google Cloud Storage (GCS). This server allows you to interact with GCS buckets and objects through a simple HTTP API.

## Features

This server provides a wide range of tools to manage GCS resources:

- **Bucket Management**: Create, delete, list, and get metadata for GCS buckets.
- **Object Management**: Upload, download, delete, list, rename, and copy objects (blobs).
- **Metadata**: Retrieve detailed metadata for both buckets and objects.
- **Security**: Generate temporary, secure signed URLs for object access.

## Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) installed (`pip install uv`).
- A Google Cloud Platform (GCP) project with the **Cloud Storage API** enabled.
- The Google Cloud SDK installed and configured on your local machine.

## Setup and Installation

1.  **Clone the Repository**
    ```bash
    git clone <your-repository-url>
    cd gcs-mcp-server
    ```

2.  **Create Virtual Environment and Install Dependencies**
    `uv` can handle both steps in one go. It will create a virtual environment in the `.venv` directory and install all packages from `requirements.txt`.
    ```bash
    uv venv
    uv pip install -r requirements.txt
    ```

## Authentication

To allow the server to access your Google Cloud resources, you need to provide application default credentials. The easiest way to do this for local development is with the `gcloud` CLI:

```bash
gcloud auth application-default login
```

This command will open a browser window for you to log in and grant the necessary permissions.

## Running the Server

The best way to run the server during development is with the `fastmcp run` command. It starts your server and launches the **MCP Inspector**, a web UI for interactively testing your tools.

```bash
fastmcp run main.py --transport="http" --port="8080" --ui-port="9080"
```

You should see output confirming that the server is running and listing the available tools:

```
================================================================================
MyEnhancedGCSMCPServer is running on http://127.0.0.1:8080/mcp
The following tools are available:
- greet(name: str) -> str
- list_gcs_buckets() -> list[str]
- ... (and all other tools)
================================================================================
```

All tool endpoints are available under the `/mcp/` path. You can interact with them using any HTTP client, such as `curl`.
You can interact with the server's tools using the `mcp-inspector` command-line utility, which comes bundled with `fastmcp`. It provides a more convenient way to call tools than using `curl`.

The `uv run` command ensures that `mcp-inspector` is executed within your project's virtual environment.


## API Reference: Available Tools

Below is a complete list of the available tools and their parameters.

| Tool | Description | Parameters |
| :--- | :--- | :--- |
| `greet` | Returns a friendly greeting. | `name: str` |
| `list_gcs_buckets` | Lists all GCS buckets. | (None) |
| `create_bucket` | Creates a new GCS bucket. | `bucket_name: str`, `location: str = "US"` |
| `delete_bucket` | Deletes a GCS bucket. | `bucket_name: str` |
| `list_objects` | Lists all objects in a bucket. | `bucket_name: str` |
| `upload_blob` | Uploads a file to a bucket. | `bucket_name: str`, `source_file_name: str`, `destination_blob_name: str` |
| `download_blob` | Downloads a blob from a bucket. | `bucket_name: str`, `blob_name: str`, `destination_file_name: str` |
| `delete_blob` | Deletes a blob from a bucket. | `bucket_name: str`, `blob_name: str` |
| `get_bucket_metadata` | Retrieves metadata for a bucket. | `bucket_name: str` |
| `get_blob_metadata` | Retrieves metadata for an object. | `bucket_name: str`, `blob_name: str` |
| `generate_signed_url` | Generates a temporary signed URL. | `bucket_name: str`, `blob_name: str`, `expiration_minutes: int = 15` |
| `rename_blob` | Renames/moves an object. | `bucket_name: str`, `blob_name: str`, `new_name: str` |
| `copy_blob` | Copies an object to another bucket. | `source_bucket_name: str`, `blob_name: str`, `destination_bucket_name: str`, `destination_blob_name: str` |
| `set_bucket_cors` | Sets the CORS configuration for a bucket. | `bucket_name: str`, `cors_rules: list[dict]` |


**Example:**

```python
from google.api_core import exceptions

@mcp.tool
def delete_bucket(bucket_name: str) -> str:
    """Deletes a GCS bucket"""
    try:
        bucket = storage_client.bucket(bucket_name)
        bucket.delete(force=True)
        return f"Bucket '{bucket_name}' deleted successfully."
    except exceptions.NotFound:
        return f"Error: Bucket '{bucket_name}' not found."
    except exceptions.Forbidden as e:
        return f"Error: Permission denied for bucket '{bucket_name}'. Details: {e}"
```

### Configuration

Hardcoding values like the default location (`"US"`) is inflexible. These could be moved to environment variables or a configuration file for better management.

## Contributing

Contributions are welcome! Please feel free to submit a pull request for bug fixes, new features, or improvements to the documentation.
