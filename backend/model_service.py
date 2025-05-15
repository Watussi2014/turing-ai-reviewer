from langchain.chat_models import ChatOpenAI
import constants
from langchain_core.prompts import PromptTemplate
import json
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import tiktoken

def count_tokens(text: str, model: str = "gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

class ModelService:
    def __init__(self):
        self.llm = self._init_model()

    def _init_model(self, model: str = constants.DEFAULT_MODEL) -> ChatOpenAI:
        return ChatOpenAI(model=model, temperature=0)

    def _invoke_llm(self, prompt: PromptTemplate, inputs: dict) -> str:
        formatted_prompt = prompt.format(**inputs)
        print("Prompt Length:", count_tokens(formatted_prompt))
        return (prompt | self.llm).invoke(inputs).content

    def extract_project_description(self, task_description: str) -> str:
        template = """
            You are a helpful assistant that analyzes task descriptions and extracts the project description from them.
            The task description may contain details about the student, the course, or additional context. 
            Your primary responsibility is to extract ONLY the project description. 
            This description should be a concise paragraph that focuses on explaining the idea of the project.
            Focus on summarizing the project idea clearly and briefly.
    
            The task description is as follows:
            {task_description}
        """
        prompt = PromptTemplate(
            input_variables=["task_description"],
            template=template,
        )
        return self._invoke_llm(prompt, {"task_description": task_description})

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
        prompt = PromptTemplate(
            input_variables=["requirements"],
            template=template.strip()
        )
        return self._invoke_llm(prompt, {"requirements": requirements})

    def summarize_file(self, file_path: str, file_content: str, project_description: str) -> str:
        template = """
                    You are reviewing a file from a student project. 
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
        prompt = PromptTemplate(
            input_variables=["project_description", "file_path", "file_content"],
            template=template.strip()
        )
        return self._invoke_llm(prompt, {
            "project_description": project_description,
            "file_path": file_path,
            "file_content": file_content
        })

    def analyze_file_quality(self, file_path: str, file_summary: str,
                             file_content: str, structured_requirements: str) -> str:
        prompt = """
                You are reviewing a file from a student project. You are given:
                - A short summary describing the purpose of the file
                - The full file content
                - The file's path (to infer its role based on its name)
                - A list of project requirements

               Your tasks are as follows:
                1. **Assess File Purpose**: 
                   - Clearly state the file's role based on its name and summary.
                   - Judge if it fulfills this purpose effectively (✅ True / ❌ False).
                2. **Requirement Fulfillment**:
                   - **Only list requirements that are fully (✅) or partially (⚠️) satisfied** by this file.
                   - Ignore requirements that are irrelevant or not addressed.
                3. **Strengths**:
                   - Highlight well-implemented aspects.
                   - For each, specify the **code location** (e.g., `function_x()`, `Section Y`).
                4. **Improvements Needed**:
                   - Prioritize critical issues.
                   - Include **why** it matters and **how to fix**.
                   - For minor issues (e.g., typos, formatting), group them concisely.

                Be context-aware: treat README, requirements.txt, or config files differently from code modules.

                ---
                
                **Project Requirements**:
                {structured_requirements}

                Now analyze the following file.

                **Filename**: {file_path}

                **File Summary**:
                {file_summary}

                **File Content**:
                {file_content}
                """
        prompt = PromptTemplate(
            input_variables=["structured_requirements", "file_path", "file_summary", "file_content"],
            template=prompt
        )
        return self._invoke_llm(prompt, {
            "structured_requirements": structured_requirements,
            "file_path": file_path,
            "file_summary": file_summary,
            "file_content": file_content
        })

    def generate_final_feedback(self, file_feedbacks: str, requirements: str, project_description: str) -> str:
        template = """
        You are a lead project reviewer. You have just analyzed each file of the project and provided feedback on them.

        Your task now is to produce a comprehensive project review for a student's project submission.

        You are given:
        - A short description of the overall project
        - A list of project requirements
        - Structured feedback for each file in the project the you generated

        ---

        **Project Description**:
        {project_description}

        **Project Requirements**:
        {requirements}

        **Feedback on Each File**:
        {file_feedbacks}

        ---

        Write a structured, professional project review in Markdown format.

        Base all evaluations on the provided file feedback. Reference specific filenames or sections where appropriate.

        Your output should include:

        1. **Overall Summary**  
           - Briefly assess the project's overall quality, clarity, and correctness.

        2. **Requirement Fulfillment**  
           - For each requirement, explain whether and how it's fulfilled.
           - Identify which file(s) contribute to fulfilling each.
           - Present this as a Markdown table with columns like: `Requirement`, `Status`, `Notes`, `Files Involved`.

        3. **General Strengths**  
           - List notable strengths of the project.
           - For each, explain why it stands out and where it appears (filename or section).

        4. **Areas for Improvement**  
           - Start with the most critical issues, then cover lesser concerns.
           - Explain why each issue matters and where it occurs (filename, function, or snippet).

        5. **Suggested Next Steps**  
           - Provide actionable advice on how the student can improve the project.

        6. **Estimated Likelihood of Passing**  
           - Estimate how likely the project is to pass a review by a Senior Developer, assuming 70/100 is the passing threshold.
           - Express this as an approximate chance (e.g., “likely”, “borderline”, “unlikely”).
           - Justify your estimate by summarizing the main strengths and weaknesses.

        Use bullet points and subheadings to keep the review scannable. Present requirement fulfillment in a Markdown table.
        """
        prompt = PromptTemplate(
            input_variables=["file_feedbacks", "requirements", "project_description"],
            template=template
        )
        return self._invoke_llm(prompt, {
            "file_feedbacks": file_feedbacks,
            "requirements": requirements,
            "project_description": project_description
        })

    def get_relevant_files(self, file_data: list[dict], query: str) -> list[str]:
        """
        Identifies the most relevant files for answering a student's technical question.
        Returns up to 2 file paths.
        """
        file_summary = json.dumps([
            {"path": file["path"], "summary": file["summary"]}
            for file in file_data
        ], indent=2)

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
            template=template.strip()
        )
        output = self._invoke_llm(prompt, {
            "file_summary": file_summary,
            "query": query
        }).strip()

        return output.split() if output else []

    def generate_response(self, relevant_files: list[dict],
                          previous_conversation: list[HumanMessage | AIMessage]) -> str:
        """
        Generates a follow-up response using context from selected files and prior conversation.
        """
        relevant_file_data = "\n\n".join(
            f"{path}:\n{content}"
            for file in relevant_files
            for path, content in file.items()
        )

        system_message = SystemMessage(content=f"""
                    You are a lead project reviewer. You provided a comprehensive review of the learner's project. 
                    After that, the user asks you follow-up questions about the project. To answer the user's question,
                    you may be provided with some of the project files' contents. Use them to answer the user's question.
                    If the question is not related to the project, say "I can't help with that."
                    You can also refer to the previous conversation for context.

                    Here are the relevant project files:
                    {relevant_file_data}
                    """)

        print("System Message Tokens:", count_tokens(system_message.content))
        print("Conversation Tokens:", sum(count_tokens(msg.content) for msg in previous_conversation))

        messages = [system_message] + previous_conversation
        return self.llm(messages).content

