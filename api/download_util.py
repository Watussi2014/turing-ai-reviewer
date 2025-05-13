import requests
import io
import zipfile
import json
import os
import re
from typing import Optional, Tuple
from model_service import ModelService
import tempfile

def download_repo(repo_url: str):
    """
    Download a Github repo into a zip file.

    Returns it in memory.
    """
    # Construct the correct URL for the ZIP file
    url = f"{repo_url}/archive/refs/heads/main.zip"
    
    # Send a GET request to download the ZIP file with authentication
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Load the ZIP file into memory using BytesIO
        zip_file = io.BytesIO(response.content)
        return zip_file     
    else:
        print(f"Failed to download repository. Status code: {response.status_code}")
        return None

def extract_zip(zip_file):
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    temp_dir = os.path.join(temp_dir, os.listdir(temp_dir)[0])
    return temp_dir

def extract_task_description_file_content(zip_file: io.BytesIO) -> Optional[Tuple[str, str]]:
    """
    Extracts the content and file extension of the first file in a ZIP archive
    whose name (excluding extension) consists only of digits and has either a
    .ipynb or .md extension.
    This file should be the task description in Turing project

    Args:
        zip_file (str): The path to the ZIP archive.

    Returns:
        Optional[Tuple[str, str]]: A tuple containing the file content as a string
        and its extension (either '.ipynb' or '.md'), or None if no matching file is found.
    """
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        # Iterate through all the files in the ZIP archive
        for file_info in zip_ref.infolist():
            print(file_info.filename)
            full_filename = os.path.basename(file_info.filename)
            filename = os.path.splitext(full_filename)[0]
            file_extension = os.path.splitext(full_filename)[1]
            print(filename)
            print(file_extension)
            if (file_extension == '.ipynb' or file_extension == '.md') and filename.isdigit():  # Only extract .ipynb files
                with zip_ref.open(file_info) as f:
                    return f.read().decode('utf-8'), file_extension
    print("No valid task description file found in the ZIP archive.")
    return None

def extract_task_description(zip_file: io.BytesIO) -> str:
    """
    Extracts and returns task description of the Turing project. Some of the projects have
    .md or .ipynb files. That is why we have to check for both of them.

    Args:
        zip_file (str): The path to the ZIP archive.

    Returns:
        str: The combined markdown content. Returns an empty string if the file is invalid or cannot be processed.
    """
    content, extension = extract_task_description_file_content(zip_file)
    if extension == '.ipynb':
        combined_source_code = ""
        try:
            notebook = json.loads(content)
        except json.JSONDecodeError:
            print("Error decoding JSON in the notebook content")
            return ""

        for cell in notebook.get("cells", []):
            if cell.get("cell_type") == "markdown":  # Only extract code cells
                combined_source_code += "".join(cell.get("source", []))  # Combine the source code

        if not combined_source_code:
            print("No source code found in the notebook.")
        return combined_source_code
    elif extension == '.md':
        return content
    return ""

def extract_requirements(source_code):
    """
    Extract the content between '## Requirements' and the next '##' in the source code.

    Args:
        source_code (str): The source code string extracted from the notebook's code cells.

    Returns:
        str: The content between '## Requirements' and the next '##', or an empty string if not found.
    """
    pattern = r'(## Requirements\s*(?:.*?))(?=\n##|\Z)'

    match = re.search(pattern, source_code, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        print("No '## Requirements' section found.")
        return ""

def extract_project_description(task_description, model_service):
    """
    Extract the content that appears before the '## Requirements' heading.

    Args:
        task_description (str): The source code string extracted from the notebook's code cells.

    Returns:
        str: All text before the '## Requirements' heading, or an empty string if not found.
    """
    # Match everything from the beginning up to the line containing '## Requirements'
    print("Content before requirements:")
    project_description = model_service.extract_project_description(task_description)
    print("Project description:")
    print(project_description)
    return project_description

def clean_zip_file(repo: str) -> dict:
    """
    Cleans a GitHub repository ZIP file by extracting and processing relevant information.

    Args:
        repo (str): The URL of the GitHub repository.

    Returns:
        dict: A dictionary containing:
            - "requirements": The extracted requirements section from the notebook's source code.
            - "description": The content before the requirements section in the notebook's source code.
            - "zip": A BytesIO object of a new ZIP file containing all files except .ipynb files.
    """

    project_data = {}
    model_service = ModelService()
    zip_file = download_repo(repo)
    project_folder = extract_zip(zip_file)
    task_description = extract_task_description(zip_file)
    requirements = extract_requirements(task_description)
    description = extract_project_description(task_description, model_service)

    project_data["requirements"] = requirements
    project_data["description"] = description
    project_data["project_directory"] = project_folder
    return project_data