from langchain.chat_models import ChatOpenAI
import constants
from langchain_core.prompts import PromptTemplate
import streamlit as st
import json
from langchain.schema import SystemMessage, HumanMessage
import tiktoken

def count_tokens(text: str, model: str = "gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

class ModelService:
    def __init__(self):
        self.llm = self._init_model()

    def _init_model(self, model: str = constants.DEFAULT_MODEL) -> ChatOpenAI:
        return ChatOpenAI(model=model, temperature=0)

    def extract_project_description(self, task_description) -> str:
        template = """
        You are a helpful assistant that analyzes task descriptions and extracts the project description from them.
        The task description may contain details about the student, the course, or additional context. 
        Your primary responsibility is to extract ONLY the project description. 
        This description should be a concise paragraph that focuses on explaining the idea of the project.
        Focus on summarizing the project idea clearly and briefly.

        The task description is as follows:
        {task_description}
        """
        prompt_tepmlate = PromptTemplate(
            input_variables=["text_before_requirements"],
            template=template,
        )
        chain = prompt_tepmlate | self.llm
        project_description = chain.invoke({"task_description": task_description}).content
        return project_description

    def restructure_requirements(self, requirements: str) -> str:
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
        restructured = chain.invoke({"requirements": requirements}).content
        return restructured

    def summarize_file(self, file_path: str, file_content: str, project_description: str) -> str:
        """
        Generates a concise summary of a file's purpose and role within a project using an LLM.

        Args:
            file_path (str): Path/filename of the file being summarized (used for context).
            file_content (str): Content of the file to analyze.
            project_description (str): Brief description of the overall project for context.

        Returns:
            Optional[str]: 2-4 sentence plain text summary of the file's role.
        """
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
    
            Your output should be a plain, helpful summary suitable for another developer trying to 
            understand the project structure.
        """
        summary_prompt = PromptTemplate(
            input_variables=["project_description", "file_path", "file_content"],
            template=template)

        chain = summary_prompt | self.llm
        file_summary = chain.invoke({"file_content": file_content,
                                     "project_description": project_description,
                                     "file_path": file_path}).content
        # Count tokens in the prompt
        prompt_length = count_tokens(summary_prompt.format(
            project_description=project_description,
            file_path=file_path,
            file_content=file_content
        ))
        st.write("File Summary Prompt Length: ")
        st.write(summary_prompt.format(
            project_description=project_description,
            file_path=file_path,
            file_content=file_content
        ))
        st.write(prompt_length)
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
        
        Be context-aware: treat README, requirements.txt, or config files differently from code modules.

        ---

        Now analyze the following file.

        **Filename**: {file_path}
        
        **File Summary**:
        {file_summary}

        **File Content**:
        {file_content}
        
        
        Your output should include:
        1. **File purpose**: "What is this file for? Based on filename + summary."
        2. **Fulfills the purpose**: true/false
        3. **General Strengths**: 
            - List the file’s notable strengths.
            - For each, include an explanation and specify where (which file or part of the project) it is implemented.
        5. **Areas for Improvement**: 
            - Focus first on the most critical issues, followed by less significant ones.
            - For each issue, explain why it matters and point to the specific implementation location (e.g. 
            function or code snippet).
        """

        message = PromptTemplate(template=prompt,
                                 input_variables=["file_path", "file_summary", "file_content"])
        # Count tokens in the prompt
        prompt_length = count_tokens(message.format(
            file_path=file_path,
            file_summary=file_summary,
            file_content=file_content
        ))
        st.write("File Analysis Prompt Length: ")
        st.write(prompt_length)
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
        Your task is to produce a comprehensive project review for a student's project submission.
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
        2. **Requirement Fulfillment**: For each requirement, explain if and how it's fulfilled, 
        and which files contribute to it.
        3. **General Strengths**: 
            - List the project’s notable strengths.
            - For each, include an explanation and specify where (which file or part of the project) it is implemented.
        5. **Areas for Improvement**: 
            - Focus first on the most critical issues, followed by less significant ones.
            - For each issue, explain why it matters and point to the specific implementation location (e.g., filename, 
            function or code snippet).
        6. **Suggested Next Steps**: Actionable advice for improving the project.
        7. **Estimated Likelihood of Passing**: Based on the overall quality, requirement fulfillment, 
        and file feedback, estimate the project's likelihood of passing a review by a Senior Developer. 
        Assume that a score of 70/100 is the passing threshold. Provide a brief justification for the estimate,
         highlighting strengths and weaknesses that influence the evaluation. Clearly state the estimated likelihood as
          an approximate chance of passing (not a numeric score), and briefly justify the estimate by summarizing key 
          strengths and weaknesses.

        Use bullet points and subheadings to keep the review scannable. Use markdown table for requirement fulfillment.
        """

        message = PromptTemplate(template=prompt,
                                 input_variables=["file_feedbacks", "requirements", "project_description"])

        # Count tokens in the prompt
        prompt_length = count_tokens(message.format(
            file_feedbacks=file_feedbacks,
            requirements=requirements,
            project_description=project_description
        ))
        st.write("Final Feedback Prompt Length: ")
        st.write(prompt_length)

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

    def get_relevant_files(self, file_data, query):
        """
        Uses LangChain to query the LLM for the best matching filenames based on a description.
        """
        file_summary = [{"summary": file["summary"], "path": file["path"]} for file in file_data]

        template = """
            You are an expert project reviewer analyzing questions about a codebase. 
            Your task is to identify if specific files are needed to answer a student's technical question.
    
            ### Instructions:
            1. **Analyze the question** and the available file summaries below
            2. **Decision**:
               - If the question can be answered using just the general project knowledge: return "" (empty string)
               - If specific files are needed to answer properly: return 1-2 most relevant file paths
            3. **Output Format**:
               - Only return space-separated file paths (e.g., "src/utils.py tests/test_main.py")
               - Never include explanations, justifications, or punctuation
               - Maximum 2 files (choose the most critical ones)
    
            ### Evaluation Criteria for File Relevance:
            - The file must contain SPECIFIC implementation details needed to answer
            - Prefer:
              - Core implementation files over tests
              - Main files over utility files
              - Files explicitly mentioned in the question
    
            ### Available Files:
            {file_summary}
    
            ### Student Question:
            {query}
    
            Your response (only space-separated paths or empty string):"""

        prompt = PromptTemplate(
            input_variables=["file_summary", "query"],
            template=template
        )
        chain = prompt | self.llm
        selected_files = chain.invoke({"file_summary": file_summary, "query": query}).content
        print("Selected files:")
        print(selected_files)
        return selected_files.split(" ")

    def generate_response(self, relevant_files, previous_conversation):
        # Join file contents for context
        relevant_file_data = "\n\n".join(
            f"{path}:\n{content}"
            for file in relevant_files
            for path, content in file.items()
        )

        # Compose a system message that provides context only
        system_message = SystemMessage(content=f"""
            You are a lead project reviewer. You provided a comprehensive review of the learner's project. After that,
            the user asks you follow-up questions about the project. To answer the user's question, you may be 
            provided with some of the project files' contents. Use them to answer the user's question.
            If the question is not related to the project, say "I can't help with that."
            You can also refer to the previous conversation for context.
        
            Here are the relevant project files:
            {relevant_file_data}
            """)
        system_message_token_length = count_tokens(system_message.content)
        previous_conversation_token_length = sum(
            count_tokens(msg.content) for msg in previous_conversation
        )
        print("System Message Length: ")
        print(system_message_token_length)
        print("Previous Conversation Length: ")
        print(previous_conversation_token_length)

        messages = [system_message] + previous_conversation
        response = self.llm(messages)

        return response.content

