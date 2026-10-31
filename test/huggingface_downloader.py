import os
from pathlib import Path


from huggingface_hub import snapshot_download


base_dir: str = "/app/test/huggingface"
model_name: str = "multilingual-e5-small"
model_dir = os.path.join(base_dir, model_name)

def create_directory_structure(base_dir: str, model_name: str) -> None:
    """
    Create the directory structure for storing the downloaded model.

    Args:
        base_dir (str): The base directory where the model will be stored.
        model_name (str): The name of the model to be downloaded.
    """
    # Create the base directory if it doesn't exist
    Path(base_dir).mkdir(parents=True, exist_ok=True)

    # Create a subdirectory for the specific model
    model_dir = Path(base_dir) / model_name
    model_dir.mkdir(parents=True, exist_ok=True)


create_directory_structure(base_dir, model_name)

# Download everything into a local directory
snapshot_download(
    repo_id="intfloat/multilingual-e5-small", 
    local_dir="model_dir"
)

