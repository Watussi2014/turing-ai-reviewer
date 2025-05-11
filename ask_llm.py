from project_analysis import analyze_project
from processing_chat import process_follow_up_message
from download_util import clean_zip_file
from langchain_core.messages import HumanMessage, AIMessage

class AskLLM:
    def __init__(self,repo):
        self.project_repo = repo
        self.chat_history = []
        self.project_description = None
        self.project_requirements = None
        self.zip_file = None
        self.file_data = None

    def extract_files(self):
        file_data = clean_zip_file(self.project_repo)
        self.project_requirements = file_data["requirements"]
        self.project_description = file_data["description"]
        self.zip_file = file_data["zip"]

    def analyze_project(self):
        feedback, self.file_data = analyze_project(self.zip_file, self.project_requirements, self.project_description)
        ai_message = AIMessage(content=feedback)
        self.chat_history.append(ai_message)
        return ai_message.content

    def ask_followup(self, user_input):
        human_reply = HumanMessage(content=user_input)
        self.chat_history.append(human_reply)
        response = process_follow_up_message(self.chat_history, user_input, self.file_data)
        ai_reply = AIMessage(content=response)
        self.chat_history.append(ai_reply)
        return ai_reply

