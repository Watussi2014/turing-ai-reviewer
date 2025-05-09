import zipfile
import os
import tempfile
import streamlit as st
from typing import Optional, List
'''
Functions that extract zip files and collect code files from a given directory.
'''

def extract_zip_to_temp(zip_file):
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    return temp_dir

def collect_code_files(project_path: str, files_to_collect: Optional[List[str]] = None):
    code_files = []
    for root, _, files in os.walk(project_path):
        for file in files:
            full_path = os.path.join(root, file)
            if files_to_collect is None:
                code_files.append(full_path)
            else:
                if file in files_to_collect:
                    code_files.append(full_path)
    return code_files
