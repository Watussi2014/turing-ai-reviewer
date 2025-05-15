import requests
import io
import zipfile
import json
import os
import re
from typing import Optional, Tuple
from model_service import ModelService
import tempfile
import shutil
import dotenv
from urllib.parse import urlparse

dotenv.load_dotenv()

def clean_zip_file(repo: str) -> dict:
    """
    Processes a GitHub repository by downloading, extracting, and analyzing its contents to extract:
    - Task requirements (from a structured `.ipynb` or `.md` file. Turing College task descriptions
    are located in either .ipynb or .md file with the name consisting only of numbers).
    - Project description (generated using Large Language Model).
    - The path to the extracted project directory.

    Args:
        repo (str): The URL of the GitHub repository (e.g., "https://github.com/user/repo").

    Returns:
        dict: A dictionary containing the following keys:
            - s"requirements" (str): Extracted task requirements (cleaned text).
            - "description" (str): Generated project description (from a model service).
            - "project_directory" (str): Path to the extracted project folder.
    """
    project_data = {}
    model_service = ModelService()
    zip_file = download_repo(repo)
    project_folder = extract_zip(zip_file)
    task_description = extract_task_description(project_folder)
    requirements = extract_requirements(task_description)
    description = extract_project_description(task_description, model_service)

    project_data["requirements"] = requirements
    project_data["description"] = description
    project_data["project_directory"] = project_folder
    return project_data

def download_repo(repo_url: str, branch: str = "main") -> Optional[io.BytesIO]:
    """
    Download a GitHub repository as a ZIP file into memory.

    Args:
        repo_url (str): The URL of the GitHub repository (e.g., "https://github.com/user/repo").
        branch (str, optional): The branch to download. Defaults to "main".

    Returns:
        Optional[io.BytesIO]: A BytesIO object containing the ZIP file if successful, None otherwise.

    Raises:
        requests.exceptions.RequestException: If the request fails (e.g., connection error).
    """
    token = os.getenv("GITHUB_TOKEN", None)
    owner, repo_name = parse_github_url(repo_url)

    headers = {"Accept": "application/vnd.github+json", 
               "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        # Construct the correct URL for the ZIP file
        url = f"https://api.github.com/repos/{owner}/{repo_name}/zipball/{branch}"

        # Send a GET request to download the ZIP file
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return io.BytesIO(response.content)
    except requests.exceptions.RequestException as e:
        raise e

def parse_github_url(repo_url: str) -> Tuple[str, str]:
    """
    Parse a GitHub repository URL to extract owner and repository name.
    
    Args:
        repo_url (str): GitHub repository URL (e.g., "https://github.com/owner/repo")
        
    Returns:
        Tuple[str, str]: A tuple containing (owner, repo_name)
        
    Raises:
        ValueError: If the URL is not a valid GitHub repository URL
    """
    # Handle URLs with or without https://
    if not repo_url.startswith(('http://', 'https://')):
        repo_url = 'https://' + repo_url
    
    # Parse the URL
    parsed_url = urlparse(repo_url)
    
    # Ensure it's a GitHub URL
    if 'github.com' not in parsed_url.netloc:
        raise ValueError(f"Not a GitHub URL: {repo_url}")
    
    # Extract path parts
    path_parts = [p for p in parsed_url.path.split('/') if p]
    
    # Path should have at least owner/repo
    if len(path_parts) < 2:
        raise ValueError(f"Invalid GitHub repository URL: {repo_url}")
    
    owner = path_parts[0]
    repo_name = path_parts[1]
    
    # Remove .git suffix if present
    if repo_name.endswith('.git'):
        repo_name = repo_name[:-4]
    
    return owner, repo_name
def extract_zip(zip_file: io.BytesIO) -> Optional[str]:
    """
    Extracts a ZIP file into a temporary directory and returns the path to the extracted contents.

    Args:
        zip_file (io.BytesIO): A BytesIO object containing the ZIP file data.

    Returns:
        Optional[str]: The path to the extracted directory if successful, None otherwise.

    Raises:
        zipfile.BadZipFile: If the file is not a valid ZIP file.
        RuntimeError: If the extracted directory structure is unexpected.
    """
    temp_dir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        extracted_items = os.listdir(temp_dir)
        if len(extracted_items) != 1 or not os.path.isdir(os.path.join(temp_dir, extracted_items[0])):
            raise RuntimeError("Unexpected ZIP file structure (expected a single top-level directory).")

        return os.path.join(temp_dir, os.listdir(temp_dir)[0])

    except (zipfile.BadZipFile, RuntimeError) as e:
        print(f"Failed to extract ZIP file: {e}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return None

def extract_task_description(directory: str) -> str:
    """
    Extracts and returns the task description from an extracted project directory.
    Supports both `.ipynb` (Jupyter Notebook) and `.md` (Markdown) files.

    Args:
        directory (str): Path to the extracted project directory.

    Returns:
        str: The combined markdown content. Returns an empty string if no valid file is found
             or if processing fails.
    """
    # Find the task description file (either .ipynb or .md)
    result = find_task_description_file_content(directory)
    if not result:
        return ""

    content, extension = result

    if extension == '.ipynb':
        try:
            notebook = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in the notebook: {e}")
            return ""

        combined_markdown = ""
        for cell in notebook.get("cells", []):
            if cell.get("cell_type") == "markdown":
                combined_markdown += "".join(cell.get("source", []))

        return combined_markdown if combined_markdown else ""

    elif extension == '.md':
        return content

    return ""

def find_task_description_file_content(directory: str) -> Optional[Tuple[str, str]]:
    """
    Searches an extracted directory for the first file whose name (excluding extension)
    consists only of digits and has either a `.ipynb` or `.md` extension.
    This file should be the task description in a Turing project.

    Args:
        directory (str): Path to the extracted directory.

    Returns:
        Optional[Tuple[str, str]]: A tuple containing the file content as a string
        and its extension (either '.ipynb' or '.md'), or None if no matching file is found.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            full_filename = os.path.basename(file)
            filename, file_extension = os.path.splitext(full_filename)

            if (file_extension in ('.ipynb', '.md')) and filename.isdigit():
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    extension = file_extension
                os.remove(file_path)
                print(f"Deleted {file_path} after reading")
                return content, extension

    print("No valid task description file found in the directory.")
    return None

def extract_requirements(source_code: str) -> str:
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

def extract_project_description(task_description: str, model_service: ModelService) -> Optional[str]:
    """
    Use LLM to extract the project description from the task description.

    Args:
        task_description (str): The source code string extracted from the notebook's code cells.

    Returns:
        str: Project description extracted from the task description.
    """
    project_description = model_service.extract_project_description(task_description)
    print("Project description:")
    print(project_description)
    return project_description