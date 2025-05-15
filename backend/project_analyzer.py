from model_service import ModelService
import json
import os
from pathlib import Path
import nbformat
from typing import List, Dict, Tuple, Union
VALID_EXTENSIONS = {'.py', '.ipynb', '.md', '.txt', '.sql'}

def analyze_project(project_folder: Union[str, Path], requirements: str,
                    description: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    Analyzes the uploaded project directory by summarizing files, structuring requirements,
    and generating quality feedback using an LLM-based service.

    Args:
        project_folder (Union[str, Path]): Path to the extracted project folder.
        requirements (str): Raw textual requirements provided by the user.
        description (str): High-level project description.

    Returns:
        Tuple[str, List[Dict[str, str]]]: Final feedback string and list of file data dicts
        with keys: 'path', 'code', and 'summary'.
    """
    print("Analyzing files in ", project_folder)
    file_data = get_all_project_files(project_folder, description)
    file_summary = [{"summary": file["summary"], "path": file["path"]} for file in file_data]
    print("Summary of files")
    print(file_summary)

    model_service = ModelService()
    structured_requirements = model_service.restructure_requirements(requirements)
    try:
        structured_requirements = json.loads(structured_requirements)
        assert isinstance(structured_requirements, list)
    except (json.JSONDecodeError, AssertionError):
        structured_requirements = []
    print("Structured Requirements:")
    print(structured_requirements)


    file_feedbacks = {}
    for file in file_data:
        path = file["path"]
        content = file["code"]
        summary = file["summary"]
        file_feedback = model_service.analyze_file_quality(path, summary, content, structured_requirements)
        print(f"Feedback for {path}:")
        print(file_feedback)
        file_feedbacks[path] = file_feedback

    final_feedback = model_service.generate_final_feedback(file_feedbacks, structured_requirements, description)
    return final_feedback, file_data

def get_all_project_files(folder_path: Union[str, Path], project_description: str) -> List[Dict[str, str]]:
    """
    Recursively traverses a project directory and summarizes each file using an LLM.

    Args:
        folder_path (Union[str, Path]): Path to the root folder of the project.
        project_description (str): Description of the project for contextual summarization.

    Returns:
        List[Dict[str, str]]: List of file info dictionaries with keys:
                              'path' (str), 'code' (str), and 'summary' (str).
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

def process_follow_up_message(chat_history: List[Dict[str, str]],
                              user_query: str, file_data: List[Dict[str, str]]) -> str:
    """
    Processes a follow-up question by finding relevant files and generating a response.

    Args:
        chat_history (List[Dict[str, str]]): Conversation history between user and system.
        user_query (str): User's current message or question.
        file_data (List[Dict[str, str]]): List of files with their code and paths.

    Returns:
        str: Model-generated response based on relevant files and chat history.
    """
    model_service = ModelService()
    relevant_files = model_service.get_relevant_files(file_data, user_query)
    print(f"Relevant files: {relevant_files}")
    relevant_file_data = [{file["path"]: file["code"]} for file in file_data if file["path"] in relevant_files]
    model_response = model_service.generate_response(relevant_file_data, chat_history)
    return model_response