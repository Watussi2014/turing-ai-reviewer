import zipfile
import os
import tempfile
from typing import Optional, List
'''
Functions that extract zip files and collect code files from a given directory.
'''

def extract_zip_to_temp(zip_file):
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    return temp_dir