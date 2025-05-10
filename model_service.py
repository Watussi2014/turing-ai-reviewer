from langchain.chat_models import ChatOpenAI
import constants
from langchain_core.prompts import PromptTemplate
import streamlit as st
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

class ModelService:
    def __init__(self):
        self.llm = self._init_model()

    def _init_model(self, model: str = constants.DEFAULT_MODEL) -> ChatOpenAI:
        return ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.0)

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
        prompt = """
        You are reviewing a file from a student project. You are given:
        - A short summary describing the purpose of the file
        - The full file content
        - The file's path (to infer its role based on its name)

       Your goal is to:
        1. Judge how well the file fulfills its intended role in the project
        2. Highlight strengths and issues
        3. Suggest specific improvements, especially in terms of clarity, correctness, maintainability, and usefulness
        
        Be context-aware: treat README, requirements.txt, or config files differently from code modules.

        ---

        Now analyze the following file.

        **Filename**: {file_path}
        
        **File Summary**:
        {file_summary}

        **File Content**:
        {file_content}
        
        ---

        Return your analysis in this exact JSON format:
        
        {{
          "file_purpose": "What is this file for? Based on filename + summary.",
          "fulfills_purpose": true/false,
          "strengths": ["Short bullet list of what's good"],
          "issues": ["Short bullet list of what's missing, incorrect, or weak"],
          "suggestions": ["Specific, actionable ways to improve the file"]
        }}
        """

        message = PromptTemplate(template=prompt,
                                 input_variables=["file_path", "file_summary", "file_code"])
        chain = message | self.llm
        file_feedback = chain.invoke({"file_path": file_path,
                                      "file_summary": file_summary,
                                     "file_content": file_content}).content
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

    def generate_final_feedback(self, file_feedbacks, requirements, project_description):
        prompt = """
        Your task is to produce a comprehensive project review for a student's software submission.
        You are given:
        - A short description of the overall project
        - A list of project requirements
        - Structured feedback for each file in the project
        ---
        **Project Description**:
        {project_description}

        **Project Requirements**:
        {requirements}

        **Feedback on Each File**:
        {file_feedbacks}

        ---

        Based on this, write a structured project review in Markdown format.

        Your output should include:
        1. **Overall Summary**: Brief overview of project quality, clarity, and correctness.
        2. **Requirement Fulfillment**: For each requirement, explain if and how it's fulfilled, and which files contribute to it.
        3. **File Quality Highlights**: Mention files that are especially strong or weak and why.
        4. **General Strengths**: E.g., clear structure, readable code, useful documentation.
        5. **Areas for Improvement**: E.g., missing functionality, unclear code, poor comments, inefficiencies.
        6. **Suggested Next Steps**: Actionable advice for improving the project.

        Use bullet points and subheadings to keep the review scannable.
        """

        message = PromptTemplate(template=prompt,
                                 input_variables=["file_feedbacks", "requirements", "project_description"])

        chain = message | self.llm
        final_feedback = chain.invoke({"file_feedbacks": file_feedbacks,
                                       "requirements": requirements,
                                       "project_description": project_description}).content
        full_prompt = message.format(
            file_feedbacks=file_feedbacks,
            requirements=requirements,
            project_description=project_description
        )
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