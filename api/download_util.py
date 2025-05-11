import requests
import io
import zipfile
import json
import re

def download_repo_to_memory(repo_url: str):
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


def extract_ipynb(zip_file):
    
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        # Iterate through all the files in the ZIP archive
        for file in zip_ref.infolist():
            if file.filename.endswith('.ipynb'):  # Only extract .ipynb files
                with zip_ref.open(file) as f:
                    return f.read().decode('utf-8')

def extract_sources_from_ipynb(zip_file):
    """
    Extracts and combines the source code from all code cells in an .ipynb file.

    Args:
        ipynb_content (str): The content of the .ipynb file as a string.
    
    Returns:
        str: A single string containing all the source code from code cells in the .ipynb file.
    """
    combined_source_code = ""
    ipynb_content = extract_ipynb(zip_file)
    # Parse the JSON content of the notebook
    try:
        notebook = json.loads(ipynb_content)
    except json.JSONDecodeError:
        print("Error decoding JSON in the notebook content")
        return ""

    # Extract the source code from code cells
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") == "markdown":  # Only extract code cells
            combined_source_code += "".join(cell.get("source", []))  # Combine the source code
    
    if not combined_source_code:
        print("No source code found in the notebook.")
    
    return combined_source_code

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

def extract_description(source_code):
    """
    Extract the content that appears before the '## Requirements' heading.

    Args:
        source_code (str): The source code string extracted from the notebook's code cells.

    Returns:
        str: All text before the '## Requirements' heading, or an empty string if not found.
    """
    # Match everything from the beginning up to the line containing '## Requirements'
    pattern = r'^(.*?)(?=^## Requirements\b)'  # Stop before the line that starts with ## Requirements

    match = re.search(pattern, source_code, re.DOTALL | re.MULTILINE)
    if match:
        return match.group(1).strip()
    else:
        print("No content found above '## Requirements'.")
        return ""

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

    output = {}
    new_zip_buffer = io.BytesIO()
    zip_file = download_repo_to_memory(repo)
    source = extract_sources_from_ipynb(zip_file)
    requirements = extract_requirements(source)
    description = extract_description(source)
    output["requirements"] = requirements
    output["description"] = description

    with zipfile.ZipFile(zip_file, 'r') as original_zip, \
         zipfile.ZipFile(new_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as new_zip:
        
        for file_info in original_zip.infolist():
            if not file_info.filename.endswith('.ipynb'):
                # Read file from the original zip
                with original_zip.open(file_info) as source_file:
                    content = source_file.read()
                # Write it to the new zip
                new_zip.writestr(file_info.filename, content)

    new_zip_buffer.seek(0)
    output["zip"] = new_zip_buffer  # Reset buffer position to the beginning
    return output