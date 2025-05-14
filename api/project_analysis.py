from model_service import ModelService
import json
import streamlit as st
import os
from pathlib import Path
from typing import Union
import nbformat
VALID_EXTENSIONS = {'.py', '.ipynb', '.md', '.txt'}

def clean_notebook_outputs(path: Union[str, Path]) -> str:
    """
    Clears all code cell outputs and execution counts from a Jupyter Notebook (.ipynb) file.

    Args:
        path (Union[str, Path]): Path to the input Jupyter Notebook file.

    Returns:
        str: The cleaned notebook content as a JSON string (in nbformat).

    Raises:
        FileNotFoundError: If the input file does not exist.
        nbformat.reader.NotJSONError: If the file is not a valid Jupyter Notebook.
        Exception: For other unexpected errors during processing.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)

        for cell in nb.cells:
            if cell.cell_type == 'code':
                cell.outputs = []
                cell.execution_count = None

        return nbformat.writes(nb)

    except FileNotFoundError as e:
        raise FileNotFoundError(f"Notebook file not found: {path}") from e
    except nbformat.reader.NotJSONError as e:
        raise ValueError(f"Invalid Jupyter Notebook format: {path}") from e
    except Exception as e:
        raise RuntimeError(f"Error processing notebook: {e}") from e

def get_all_project_files(folder_path, project_description):
    """
    Recursively collects all file paths from a given folder and summarizes them with an LLM.
    Returns a list of dicts with 'path', 'code', and 'summary'.
    """
    file_data = []
    model_service = ModelService()
    print("Collecting files from the project directory...")
    for root, _, files in os.walk(folder_path):
        print(f"Processing directory: {root}")
        print("All files:")
        print(files)
        for name in files:
            ext = os.path.splitext(name)[1].lower()
            if ext not in VALID_EXTENSIONS:
                print(f"Skipped {name} due to unsupported file extension.")
                continue
            file_path = os.path.join(root, name)
            try:
                if ext == '.ipynb':
                    content = clean_notebook_outputs(file_path)
                    st.write("Content from the notebook:")
                    st.write(content)
                else:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                relative_path = os.path.relpath(file_path, folder_path)
                summary = model_service.summarize_file(relative_path, content, project_description)
                file_data.append({
                    "path": relative_path,
                    "code": content,
                    "summary": summary
                })
            except Exception as e:
                print(f"Skipped {file_path}: {e}")
                continue
    return file_data

def analyze_project(project_folder, requirements, description):
    """
    Analyzes the project by extracting files from the zip and checking requirements.

    Args:
        uploaded_zip: The uploaded zip file containing the project.
        requirements: The project requirements provided by the user.
        file_names: List of specific files to analyze.

    Returns:
        None
    """
    print("Analyzing files in ", project_folder)
    file_data = get_all_project_files(project_folder, description)
    file_summary = [{"summary": file["summary"], "path": file["path"]} for file in file_data]
    st.write("Summary of files")
    st.write(file_summary)

    model_service = ModelService()
    structured_requirements = model_service.restructure_requirements(requirements)
    try:
        structured_requirements = json.loads(structured_requirements)
        assert isinstance(structured_requirements, list)
    except (json.JSONDecodeError, AssertionError):
        st.error("⚠️ The model returned invalid JSON. Please check the prompt or response.")
        structured_requirements = []
    st.write("Structured Requirements:")
    st.write(structured_requirements)


    file_feedbacks = {}
    for file in file_data:
        path = file["path"]
        content = file["code"]
        summary = file["summary"]
        file_feedback = model_service.analyze_file_quality(path, summary, content)
        st.write(f"Feedback for {path}:")
        st.write(file_feedback)
        file_feedbacks[path] = file_feedback

    final_feedback = model_service.generate_final_feedback(file_feedbacks, structured_requirements, description)
    return final_feedback, file_data