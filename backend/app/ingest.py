from pathlib import Path
from fastapi import UploadFile
from .config import client, VECTOR_STORE_ID


# Define the folder where uploaded PDFs will be stored.
UPLOAD_DIR = Path("app/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
# Why?
# - Path(...) is a nicer, object-oriented way to handle filesystem paths.
# - mkdir(..., exist_ok=True) creates the folder if it doesn't exist
#   and does nothing if it already exists. So it's safe to call every time.

async def save_uploaded_pdf(file: UploadFile) -> Path:
    """
    Save an uploaded PDF to disk and return the file path.
    """
    # Build the full path where we want to store the file:
    # e.g. app/uploads/TheLossSurfacesOfMultilayerNetworks.pdf
    file_path = UPLOAD_DIR / file.filename

    # Read the file contents from the upload (async).
    contents = await file.read()

    # Write the bytes to disk.
    with file_path.open("wb") as f:
        f.write(contents)

    return file_path

def _clear_vector_store_files():
    """
    Remove all files currently attached to the vector store.

    This does NOT delete the underlying OpenAI files from your account,
    it just detaches them from this vector store so they are no longer
    used for retrieval.
    """
    file_list = client.vector_stores.files.list(
        vector_store_id=VECTOR_STORE_ID
    )

    # The SDK returns an object with a .data list
    for f in getattr(file_list, "data", []):
        client.vector_stores.files.delete(
            vector_store_id=VECTOR_STORE_ID,
            file_id=f.id,
        )



def index_pdf_in_openai(file_path: Path, replace_existing: bool = False) -> dict:
    """
    Upload the saved PDF to OpenAI and attach it to our vector store.

    If replace_existing is True:
        - First detach all existing files from the vector store
        - Then attach ONLY this new file

    Returns:
        {
            "file_id": <OpenAI file id>,
            "vector_store_id": <OpenAI vector store id>
        }
    """

    if replace_existing:
        _clear_vector_store_files()

    # 1) Upload file bytes to OpenAI as a "knowledge" file.
    with file_path.open("rb") as f:
        file_obj = client.files.create(
            file=f,
            purpose="assistants",
        )

    # 2) Attach this file to your existing vector store so it becomes searchable.
    client.vector_stores.files.create(
        vector_store_id=VECTOR_STORE_ID,
        file_id=file_obj.id,
    )

    return {
        "file_id": file_obj.id,
        "vector_store_id": VECTOR_STORE_ID,
    }
