from langchain.chat_models import ChatOpenAI
import constants
from langchain_core.prompts import PromptTemplate
import streamlit as st
import json

class ModelService:
    def __init__(self):
        self.llm = self._init_model()

    def _init_model(self, model: str = constants.DEFAULT_MODEL) -> ChatOpenAI:
        return ChatOpenAI(model=model, temperature=0)

    def restructure_requirements(self, requirements):
        template = """
            You are a helpful assistant that analyzes project requirements and breaks them into 
            clear implementation steps for a student developer.

            A student wrote the following requirements:
            {requirements}
            
            Break it down into a list of technical tasks that a developer would implement 
            to fulfill the requirement. Output your response strictly as a **JSON array of strings** 
            (with no explanations or extra text outside the list). Don't use any markdown in your output.

            Example Requirement:
            "The app should allow users to register and log in."

            Example Output:
            [
              "Create a registration form with email and password input fields",
              "Add a /register backend route to handle sign-ups",
              "Implement a User model to store credentials",
              "Hash the user's password before saving it",
              "Create a login form and /login route",
              "Validate login credentials and authenticate users",
              "Implement session or token-based login persistence"
            ]
            """
        restructuring_prompt = PromptTemplate(
            input_variables=["requirements"],
            template=template)

        chain = restructuring_prompt | self.llm
        restructured = chain.invoke({"requirements": requirements})
        return restructured

    def summarize_file(self, file_path, file_content, project_description):
        template = """
        You are reviewing a file from a student software project. 
        Your task is to summarize what this file contains and explain its role in the project.

        You are given:
        - A brief description of the overall project
        - The content of one project file (which may be code, a README, documentation, or configuration)

        Based on the content and filename, write a clear and concise (2–4 sentence) 
        summary describing what the file does or contains, and how it might contribute to the project.

        Project Description:
        {project_description}

        Filename: {file_path}

        File Content:
        {file_content}

        Your output should be a plain, helpful summary suitable for another developer trying to understand the project structure.
        """
        summary_prompt = PromptTemplate(
            input_variables=["project_description", "file_path", "file_content"],
            template=template)

        chain = summary_prompt | self.llm
        file_summary = chain.invoke({"file_content": file_content,
                                     "project_description": project_description,
                                     "file_path": file_path}).content
        return file_summary

    def analyze_file_quality(self, file_path, file_summary, file_content):
        prompt = f"""
        You are reviewing a file from a student project. You are given:
        - A short summary describing the purpose of the file
        - The full file content
        - The file's path (to infer its role based on its name)

        Your task is to critically analyze the file based on what it is supposed to do and how well it does it.

        Consider the following when reviewing:

        ### If it's a documentation file (like README.md or requirements.txt):
        - Does it include all the essential sections? (e.g., project description, usage, install instructions)
        - Is it clearly written and informative?
        - Is anything important missing?

        ### If it's a utility/helper code file:
        - Are the functions clearly named and scoped?
        - Is the logic correct and well-documented?
        - Could the implementation be improved? (e.g., made cleaner, more efficient, or more Pythonic?)
        - Is the file doing too much or violating separation of concerns?

        ### General (applies to all code files):
        - Code cleanliness and structure
        - Comments and docstrings
        - Naming conventions
        - Maintainability and extensibility
        - Readability and formatting

        ---

        Now analyze the following file.

        **Filename**: {file_path}
        
        **File Summary**:
        {file_summary}

        **File Content**:
        {file_content}

        ---

        Provide your analysis in the following JSON format:

        {{
          "overall_assessment": "Short summary of how well the file fulfills its purpose",
          "strengths": ["List of specific things done well"],
          "issues": ["List of concrete issues or missed expectations"],
          "suggestions": ["List of ways to improve this file (e.g., structure, content, efficiency)"]
        }}
        """


        message = PromptTemplate(template=prompt,
                                 input_variables=["file_summary", "file_code"])
        chain = message | self.llm
        file_feedback = chain.invoke({"file_summary": file_summary,
                                     "file_code": file_code}).content
        return file_feedback


    def split_review(self, description, requirements, file_data):
        planning_prompt = """
            You are a lead project reviewer. Your task is to analyze a student's project and create a review plan.
    
            You are given:
            - A **project description**
            - A list of **requirements** the project must fulfill
            - A list of **files**, each with a path and a short summary of its content
    
            Your goal is to determine the best order in which to review the files. 
            The plan should reflect a logical step-by-step approach based on how the files contribute to 
            fulfilling the requirements.    
            First, think about which files are most relevant to the requirements and the project description and 
            try to come up with the explanations to what goes first, second, etc. 
            Then, provide a list of file paths in the order they should be analyzed.
            
            Return only a space-separated list of file paths, in the order they should be analyzed.
                        Do not include any extra text or formatting.
            Example:
            '
            project/main.py project/utils.py project/tests/test_main.py
            '
    
            Project Description:
            {description}
    
            Requirements:
            {requirements}
    
            Files:
            {file_path_summary} 
            """
        message = PromptTemplate(template=planning_prompt,
                                 input_variables=["description", "requirements", "file_path_summary"])
        chain = message | self.llm
        serialized_reqs = json.dumps(requirements, indent=2)
        serialized_files = json.dumps(
            [{"path": f["path"], "summary": f["summary"]} for f in file_data],
            indent=2
        )
        full_prompt = message.format(
            description=description,
            requirements=serialized_reqs,
            file_path_summary=serialized_files
        )
        st.write("Split Review Prompt Length: ")
        st.write(len(full_prompt))
        file_paths = chain.invoke({"description": description,
                                   "requirements": serialized_reqs,
                                   "file_path_summary": serialized_files}).content
        file_paths = file_paths.strip().split()
        return file_paths

    def generate_final_feedback(self, file_feedbacks, requirements, description):
        prompt = f"""
        You are a project reviewer. Your task is to analyze a student's project and provide final feedback.

        You have the following information:
        - A list of **file feedbacks** from different files
        - A list of **requirements** the project must fulfill
        - A **project description**

        Your job is to provide a final review of the project, focusing on the overall quality, 
        completeness, and adherence to the requirements.

        Project Description:
        {description}

        Requirements:
        {requirements}

        File Feedbacks:
        {file_feedbacks}

        Provide a structured feedback report.
        """

        message = PromptTemplate(template=prompt,
                                 input_variables=["file_feedbacks", "requirements", "description"])

        chain = message | self.llm
        final_feedback = chain.invoke({"file_feedbacks": file_feedbacks,
                                       "requirements": requirements,
                                       "description": description}).content
        return final_feedback

    def choose_files_to_analyze(self, file_summary, requirement):
        template = f"""
            You are a project reviewer. Your task is to select the most relevant file from the list below 
            that best matches the given requirement. Choose 1 file only
    
            Here is the dictionary of file paths and their summaries:
            {file_summary}
    
            Requirement:
            {requirement}
    
            Select the most relevant file path based on their summaries and the requirement.
            YOUR OUTPUT SHOULD BE A LIST OF ONE FILE PATH. EXAMPLE: ["project/main.py"]
            """
        selection_prompt = PromptTemplate(
            input_variables=["file_summary", "requirement"],
            template=template)

        chain = selection_prompt | self.llm
        selected_files = chain.invoke({"file_summary": file_summary, "requirements": requirement})
        return selected_files

#
# Return only a space-separated list of file paths, in the order they should be analyzed.
#             Do not include any extra text or formatting.
# Example:
# '
# project / main.py
# project / utils.py
# project / tests / test_main.py
# '