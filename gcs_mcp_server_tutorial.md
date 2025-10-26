
# From Zero to Hero: Building and Deploying a GCS Super-Server with Gemini CLI

Ever wanted to manage your Google Cloud Storage from a command line, but with the power of AI? Imagine a world where you can simply type what you want to do, and an intelligent agent takes care of the rest. Well, that world is here, and in this tutorial, you'll learn how to build your own GCS (Google Cloud Storage) super-server and command it using the Gemini CLI.

We'll be building a GCS MCP (Multi-Capability Peripheral) server, which is a fancy way of saying a server that exposes a set of tools that an AI can use. We'll then deploy this server to Google Cloud Run, a serverless platform that makes it incredibly easy to run your code in the cloud. Finally, we'll use the Gemini CLI to interact with our server and perform GCS operations with natural language commands.

By the end of this tutorial, you'll have a fully functional GCS management tool powered by AI, and you'll have the knowledge to extend it with any capabilities you can imagine.

## Prerequisites

Before we begin, make sure you have the following tools installed and configured:

*   **Python 3.10+**: You can download it from [python.org](https://python.org).
*   **Google Cloud SDK**: Install it from the [Google Cloud documentation](https://cloud.google.com/sdk/docs/install). Make sure you are authenticated by running `gcloud auth login` and `gcloud auth application-default login`.
*   **A Google Cloud Project**: You'll need a project with billing enabled to use Google Cloud Storage and Cloud Run.
*   **Gemini CLI**: The installation instructions can be found on the [Gemini CLI website](https://gemini.google.com/cli).
*   **Docker**: You'll need Docker to containerize our application. You can get it from the [Docker website](https://www.docker.com/).

## Part 1: Building the GCS MCP Server

First, let's build our GCS MCP server. The server will be a simple Python application that uses the `fastmcp` library to define and expose our GCS tools.

### Project Structure

Our project will have the following structure:

```
.
├── Dockerfile
├── main.py
├── pyproject.toml
├── README.md
└── requirements.txt
```

### The Core: `main.py`

The `main.py` file is the heart of our server. It's where we'll define the tools that our AI will use to interact with GCS. We'll use the `fastmcp` library to create our MCP server and the `@mcp.tool` decorator to define our tools.

Here are a few examples of the tools we can create:

```python
import asyncio
import logging
import os
from datetime import timedelta
from typing import List, Dict, Any

from fastmcp import FastMCP
from google.cloud import storage
from google.api_core import exceptions

# ---------------------------------------------------------
# 🌐 Initialize MCP
# ---------------------------------------------------------
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP(name="MyEnhancedGCSMCPServer")

# ---------------------------------------------------------
# 1️⃣ Simple Greeting
# ---------------------------------------------------------
@mcp.tool
def greet(name: str) -> str:
    '''Returns a friendly greeting'''
    return f"Hello {name}! It's a pleasure to connect from your enhanced MCP Server."

# ---------------------------------------------------------
# 2️⃣ List all GCS buckets
# ---------------------------------------------------------
@mcp.tool
def list_gcs_buckets() -> List[str]:
    '''Lists all GCS buckets in the project.'''
    try:
        storage_client = storage.Client()
        buckets = storage_client.list_buckets()
        return [bucket.name for bucket in buckets]
    except exceptions.Forbidden as e:
        return [f"Error: Permission denied to list buckets. Details: {e}"]
    except Exception as e:
        return [f"An unexpected error occurred: {e}"]

# ---------------------------------------------------------
# 6️⃣ Upload file to a bucket
# ---------------------------------------------------------
@mcp.tool
def upload_blob(bucket_name: str, source_file_name: str, destination_blob_name: str) -> str:
    '''Uploads a local file to a GCS bucket.'''
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        return f"📤 File '{source_file_name}' uploaded to '{destination_blob_name}' in bucket '{bucket_name}'."
    except FileNotFoundError:
        return f"⚠️ Local file '{source_file_name}' not found."
    except exceptions.NotFound:
        return f"⚠️ Bucket '{bucket_name}' not found."
    except exceptions.Forbidden as e:
        return f"❌ Permission denied. Details: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {e}"

# ... (and many more tools) ...

# ---------------------------------------------------------
# 🚀 Entry Point
# ---------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logger.info(f"🚀 Starting Enhanced GCS MCP Server on port {port}")
    asyncio.run(
        mcp.run_async(
            transport="http",
            host="0.0.0.0",
            port=port,
        )
    )
```

As you can see, defining a tool is as simple as writing a Python function and decorating it with `@mcp.tool`. The `fastmcp` library takes care of exposing this function to the AI.

### Dependencies: `pyproject.toml` and `requirements.txt`

Our project has a few dependencies, which are listed in `pyproject.toml` and `requirements.txt`.

**`pyproject.toml`**:
```toml
[project]
name = "gcs-mcp-server"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "fastmcp==2.12.4",
    "google-cloud-storage",
    "google-api-core",
    "pydantic",
    "uvicorn"
]
```

**`requirements.txt`**:
```
fastmcp==2.12.4
google-cloud-storage
google-api-core
pydantic
uvicorn
```

These files ensure that all the necessary libraries are installed when we build our Docker container.

### Containerizing with Docker: `Dockerfile`

To deploy our server to Cloud Run, we need to containerize it using Docker. Here's the `Dockerfile` we'll use:

```dockerfile
# Use the official Python image.
# https://hub.docker.com/_/python
FROM python:3.13-slim

# Allow statements and log messages to be sent straight to the logs.
ENV PYTHONUNBUFFERED TRUE

# Set the working directory in the container.
WORKDIR /app

# Copy the requirements file.
COPY requirements.txt .

# Install the dependencies.
RUN pip install -r requirements.txt

# Copy the rest of the application code.
COPY . .

# Set the entrypoint for the container.
ENTRYPOINT ["python", "main.py"]
```

This `Dockerfile` creates a container with our Python application and all its dependencies.

## Part 2: Deploying to Cloud Run with Gemini CLI

Now that we have our GCS MCP server containerized, it's time to deploy it to Cloud Run. Thanks to the Gemini CLI and its `cloud-run` extension, this is incredibly simple.

All you need to do is run the following command in your terminal:

```bash
gemini deploy
```

The Gemini CLI will automatically detect your project, build the Docker container, push it to the Google Container Registry, and deploy it to Cloud Run. It's like magic!

## Part 3: Interacting with Your GCS Super-Server

Once your server is deployed, you can start interacting with it using the Gemini CLI. The `cloud-run` extension automatically makes the tools defined in your MCP server available in the Gemini CLI.

You can use natural language to ask the Gemini CLI to perform GCS operations. For example:

**List all your GCS buckets:**
```
/list_all
```

**Upload a file:**
```
/upload_file
```
The Gemini CLI will then guide you through the process, asking for the necessary information like the bucket name and the file path.

You can even create your own custom prompts for more complex workflows. We have already created a few prompts in the `.gemini/commands/` directory.

## Conclusion

Congratulations! You have successfully built and deployed a GCS MCP server and learned how to interact with it using the Gemini CLI. You now have a powerful, AI-powered tool for managing your Google Cloud Storage.

This is just the beginning. You can extend your server with more tools to manage other Google Cloud services, or even integrate it with other APIs. The possibilities are endless.

So go ahead, experiment, and build your own army of AI-powered minions to automate your cloud workflows!
