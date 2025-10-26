from fastmcp import FastMCP
from google.cloud import storage
from google.api_core import exceptions
from datetime import timedelta
import os

mcp = FastMCP(name="MyEnhancedGCSMCPServer")
storage_client = storage.Client()

# ---------------------------------------------------------
# 1️⃣ Simple Greeting
# ---------------------------------------------------------
@mcp.tool
def greet(name: str) -> str:
    """Returns a friendly greeting"""
    return f"Hello {name}! It's a pleasure to connect from your enhanced MCP Server."

# ---------------------------------------------------------
# 2️⃣ List all GCS buckets
# ---------------------------------------------------------
@mcp.tool
def list_gcs_buckets() -> list[str]:
    """Lists all GCS buckets in the project."""
    try:
        buckets = storage_client.list_buckets()
        return [bucket.name for bucket in buckets]
    except exceptions.Forbidden as e:
        return [f"Error: Permission denied to list buckets. Details: {e}"]
    except Exception as e:
        return [f"An unexpected error occurred: {e}"]

# ---------------------------------------------------------
# 3️⃣ Create a new bucket
# ---------------------------------------------------------
@mcp.tool
def create_bucket(bucket_name: str, location: str = "US") -> str:
    """Creates a new GCS bucket. Bucket names must be globally unique."""
    try:
        bucket = storage_client.bucket(bucket_name)
        bucket.location = location
        storage_client.create_bucket(bucket)
        return f"Bucket '{bucket_name}' created successfully in location '{location}'."
    except exceptions.Conflict:
        return f"Error: Bucket '{bucket_name}' already exists."
    except exceptions.Forbidden as e:
        return f"Error: Permission denied to create bucket. Details: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# ---------------------------------------------------------
# 4️⃣ Delete a bucket
# ---------------------------------------------------------
@mcp.tool
def delete_bucket(bucket_name: str) -> str:
    """Deletes a GCS bucket. The bucket must be empty unless force is used."""
    try:
        bucket = storage_client.bucket(bucket_name)
        # force=True deletes the bucket even if it contains objects. Use with caution.
        bucket.delete(force=True)
        return f"Bucket '{bucket_name}' deleted successfully."
    except exceptions.NotFound:
        return f"Error: Bucket '{bucket_name}' not found."
    except exceptions.Forbidden as e:
        return f"Error: Permission denied to delete bucket '{bucket_name}'. Details: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# ---------------------------------------------------------
# 5️⃣ List objects in a bucket
# ---------------------------------------------------------
@mcp.tool
def list_objects(bucket_name: str) -> list[str]:
    """Lists all objects in a specified GCS bucket."""
    try:
        blobs = storage_client.list_blobs(bucket_name)
        return [blob.name for blob in blobs]
    except exceptions.NotFound:
        return [f"Error: Bucket '{bucket_name}' not found."]
    except Exception as e:
        return [f"An unexpected error occurred: {e}"]

# ---------------------------------------------------------
# 6️⃣ Upload file to a bucket
# ---------------------------------------------------------
@mcp.tool
def upload_blob(bucket_name: str, source_file_name: str, destination_blob_name: str) -> str:
    """Uploads a local file to a GCS bucket."""
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_name)
        return f"File '{source_file_name}' uploaded to '{destination_blob_name}' in bucket '{bucket_name}'."
    except FileNotFoundError:
        return f"Error: Local file '{source_file_name}' not found."
    except exceptions.NotFound:
        return f"Error: Bucket '{bucket_name}' not found."
    except exceptions.Forbidden as e:
        return f"Error: Permission denied. Details: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# ---------------------------------------------------------
# 7️⃣ Download file from a bucket
# ---------------------------------------------------------
@mcp.tool
def download_blob(bucket_name: str, blob_name: str, destination_file_name: str) -> str:
    """Downloads a blob from a GCS bucket to a local file."""
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.download_to_filename(destination_file_name)
        return f"Blob '{blob_name}' downloaded to '{destination_file_name}'."
    except exceptions.NotFound:
        return f"Error: Bucket '{bucket_name}' or blob '{blob_name}' not found."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# ---------------------------------------------------------
# 8️⃣ Delete file from a bucket
# ---------------------------------------------------------
@mcp.tool
def delete_blob(bucket_name: str, blob_name: str) -> str:
    """Deletes a blob from a GCS bucket."""
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.delete()
        return f"Blob '{blob_name}' deleted from bucket '{bucket_name}'."
    except exceptions.NotFound:
        return f"Error: Bucket '{bucket_name}' or blob '{blob_name}' not found."
    except exceptions.Forbidden as e:
        return f"Error: Permission denied. Details: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# ---------------------------------------------------------
# 9️⃣ Get bucket metadata
# ---------------------------------------------------------
@mcp.tool
def get_bucket_metadata(bucket_name: str) -> dict:
    """Retrieves metadata for a GCS bucket."""
    try:
        bucket = storage_client.get_bucket(bucket_name)
        return {
            "id": bucket.id,
            "name": bucket.name,
            "location": bucket.location,
            "storage_class": bucket.storage_class,
            "created": bucket.time_created.isoformat() if bucket.time_created else None,
            "updated": bucket.updated.isoformat() if bucket.updated else None,
            "versioning_enabled": bucket.versioning_enabled,
        }
    except exceptions.NotFound:
        return {"error": f"Bucket '{bucket_name}' not found."}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

# ---------------------------------------------------------
# 🔟 Get object metadata
# ---------------------------------------------------------
@mcp.tool
def get_blob_metadata(bucket_name: str, blob_name: str) -> dict:
    """Retrieves metadata for a specific object in a bucket."""
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.get_blob(blob_name)
        if not blob:
            return {"error": f"Blob '{blob_name}' not found in bucket '{bucket_name}'."}
        return {
            "name": blob.name,
            "bucket": blob.bucket.name,
            "size": blob.size,
            "content_type": blob.content_type,
            "updated": blob.updated.isoformat() if blob.updated else None,
            "storage_class": blob.storage_class,
            "crc32c": blob.crc32c,
            "md5_hash": blob.md5_hash,
        }
    except exceptions.NotFound:
        return {"error": f"Bucket '{bucket_name}' not found."}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

# ---------------------------------------------------------
# 11️⃣ Generate signed URL
# ---------------------------------------------------------
@mcp.tool
def generate_signed_url(bucket_name: str, blob_name: str, expiration_minutes: int = 15) -> str:
    """Generates a signed URL for temporary access to a blob"""
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        if not blob.exists():
             return f"Error: Blob '{blob_name}' not found in bucket '{bucket_name}'."

        url = blob.generate_signed_url(expiration=timedelta(minutes=expiration_minutes))
        return url
    except exceptions.NotFound:
        return f"Error: Bucket '{bucket_name}' not found."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# ---------------------------------------------------------
# 12️⃣ Rename or move an object
# ---------------------------------------------------------
@mcp.tool
def rename_blob(bucket_name: str, blob_name: str, new_name: str) -> str:
    """Renames a blob (object) within a GCS bucket."""
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        if not blob.exists():
            return f"Error: Source blob '{blob_name}' not found."
        new_blob = bucket.rename_blob(blob, new_name)
        return f"Blob '{blob_name}' renamed to '{new_blob.name}' in bucket '{bucket_name}'."
    except exceptions.NotFound:
        return f"Error: Bucket '{bucket_name}' or blob '{blob_name}' not found."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# ---------------------------------------------------------
# 13️⃣ Copy object to another bucket
# ---------------------------------------------------------
@mcp.tool
def copy_blob(source_bucket_name: str, blob_name: str, destination_bucket_name: str, destination_blob_name: str) -> str:
    """Copies an object from one GCS bucket to another."""
    try:
        source_bucket = storage_client.bucket(source_bucket_name)
        destination_bucket = storage_client.bucket(destination_bucket_name)
        blob = source_bucket.blob(blob_name)
        if not blob.exists():
            return f"Error: Source blob '{blob_name}' not found in bucket '{source_bucket_name}'."
        source_bucket.copy_blob(blob, destination_bucket, destination_blob_name)
        return f"Blob '{blob_name}' copied to '{destination_blob_name}' in bucket '{destination_bucket_name}'."
    except exceptions.NotFound:
        return f"Error: Source or destination bucket not found."
    except Exception as e:
        return f"An unexpected error occurred: {e}"
