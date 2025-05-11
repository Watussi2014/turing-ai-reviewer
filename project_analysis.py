from extract_zip import extract_zip_to_temp
from model_service import ModelService
import json
import streamlit as st
import os
VALID_EXTENSIONS = {'.py', '.ipynb', '.md', '.txt'}
import nbformat

def clean_notebook_outputs(path):
    with open(path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    for cell in nb.cells:
        if cell.cell_type == 'code':
            cell.outputs = []
            cell.execution_count = None

    return nbformat.writes(nb)

def is_valid_file(file_path):
    filename = os.path.basename(file_path)
    return not (
        '__MACOSX' in file_path or
        filename.startswith('._') or
        filename == '.DS_Store'
    )

def get_all_project_files(folder_path, project_description):
    """
    Recursively collects all file paths from a given folder and summarizes them with an LLM.
    Returns a list of dicts with 'path', 'code', and 'summary'.
    """
    file_data = []
    model_service = ModelService()
    st.write("Collecting files from the project directory...")
    for root, _, files in os.walk(folder_path):
        st.write(f"Processing directory: {root}")
        if not is_valid_file(root):
            st.write(f"Skipped {root} due to macOS metadata or unsupported format.")
            continue
        for name in files:
            st.write(os.path.join(root, name))
            ext = os.path.splitext(name)[1].lower()
            if ext not in VALID_EXTENSIONS:
                st.write(f"Skipped {name} due to unsupported file extension.")
                continue
            file_path = os.path.join(root, name)
            try:
                if ext == '.ipynb':
                    content = clean_notebook_outputs(file_path)
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

def analyze_project(uploaded_zip, requirements, description):
    """
    Analyzes the project by extracting files from the zip and checking requirements.

    Args:
        uploaded_zip: The uploaded zip file containing the project.
        requirements: The project requirements provided by the user.
        file_names: List of specific files to analyze.

    Returns:
        None
    """
    temp_dir = extract_zip_to_temp(uploaded_zip)
    st.write(temp_dir)
    file_data = get_all_project_files(temp_dir, description)
    file_summary = [{"summary": file["summary"], "path": file["path"]} for file in file_data]
    st.write("Summary of files")
    st.write(file_summary)
    model_service = ModelService()

    structured_requirements = model_service.restructure_requirements(requirements).content
    try:
        structured_requirements = json.loads(structured_requirements)
        assert isinstance(structured_requirements, list)
    except (json.JSONDecodeError, AssertionError):
        st.error("⚠️ The model returned invalid JSON. Please check the prompt or response.")
        structured_requirements = []
    st.write("Structured Requirements:")
    st.write(structured_requirements)

    file_paths = model_service.split_review(description, structured_requirements, file_data)
    st.write("File Paths:")
    st.write(file_paths)

    file_feedbacks = {}
    for path in file_paths:
        summary = [f["summary"] for f in file_data if f["path"] == path]
        content = [code["code"] for code in file_data if code["path"] == path]
        file_feedback = model_service.analyze_file_quality(path, summary, content)
        st.write(f"Feedback for {path}:")
        st.write(file_feedback)
        file_feedbacks[path] = file_feedback
    st.write("File Feedbacks:")

    final_feedback = model_service.generate_final_feedback(file_feedbacks, structured_requirements, description)
    st.write("Final Feedback:")
    st.write(final_feedback)
    return final_feedback, file_data