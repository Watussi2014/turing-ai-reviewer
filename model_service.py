from langchain.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage
import constants
from typing import List
from langchain_core.prompts import PromptTemplate


class ModelService:
    """
    A service for interacting with a language model, generating responses, and naming conversations.
    """

    def __init__(self):
        """
        Initializes the ModelService with the default language model.
        """
        self.llm = self._init_model()

    def _init_model(self, model: str = constants.DEFAULT_MODEL) -> ChatOpenAI:
        """
        Initializes and returns a language model instance.

        Args:
            - model: The model name to use.

        Returns: An instance of ChatOpenAI.
        """
        return ChatOpenAI(model=model)

    def summarize_file(self, filepath, project_description):
        """
        Summarizes the content of a file. Consider modifying it to analyze only code.
        """
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        template = """
        You are a project reviewer analyzing a student's project. You have access to the project description.

        Your task is to analyze the following part of the project and provide a concise summary that includes:
        - The **main purpose** of this file or component.
        - The **approach** used (if relevant).
        - A list of **key functionalities** or features implemented.
        
        Project Description:
        {project_description}

        Be specific and avoid vague statements.

        Content:
        {content}
        """

        summary_prompt = PromptTemplate(
            input_variables=["project_description", "content"],
            template=template)

        chain = summary_prompt | self.llm
        file_summary = chain.invoke({"content": content,
                                     "project_description": project_description}).content
        return {"file": filepath, "summary": file_summary, "content": content}

    def check_requirements(self, requirements, vectorstore):
        results = []
        for req in requirements:
            rel_docs = vectorstore.similarity_search(req, k=3)
            combined_code = "\n\n".join([doc.metadata["code"] for doc in rel_docs])
            eval_prompt = PromptTemplate(
                input_variables=["requirement", "code"],
                template="""
                Requirement: {requirement}
            
                Relevant Code:
                {code}
            
                Does the code satisfy the requirement? Explain clearly. If improvements are needed, describe them.
                """)

            chain = eval_prompt | self.llm
            review = chain.invoke({"requirement": req, "code": combined_code})
            results.append({"requirement": req, "code": combined_code, "review": review})
        return results

    def analyze_code_quality(self, file_summaries):
        quality_prompt = PromptTemplate(
            input_variables=["code"],
            template="""
                    Analyze the following code for structure, clarity, naming, 
                    modularity, and error handling. Suggest improvements:
                
                    {code}
                    """
                        )

        reviews = []
        for f in file_summaries:
            chain = quality_prompt | self.llm
            review = chain.invoke({"code": f["content"]})
            reviews.append({"file": f["file"], "quality_review": review})
        return reviews

