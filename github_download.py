import requests
import io
import zipfile

def download_repo_to_memory(repo_url: str):
    """
    Download a Github repo into a zip file.

    Returns it in memory
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
        
        # Open the ZIP file in memory
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            # List all files in the zip file
            zip_ref.printdir()
            
            # Extract files from the zip into a dictionary with filenames as keys
            repo_files = {}
            for file in zip_ref.infolist():
                with zip_ref.open(file) as f:
                    repo_files[file.filename] = f.read()  # Read the content of each file
            
            return repo_files  # Returning the repo files in memory
            
    else:
        print(f"Failed to download repository. Status code: {response.status_code}")
        return None



