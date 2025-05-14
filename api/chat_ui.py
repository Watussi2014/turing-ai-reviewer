import streamlit as st
from download_util import clean_zip_file
from project_analysis import analyze_project
from langchain_core.messages import HumanMessage, AIMessage
from processing_chat import process_follow_up_message

st.set_page_config(page_title="AI Project Reviewer", layout="wide")

st.title("🤖 AI Project Reviewer")
st.markdown("Upload your project files and enter your requirements to get an AI-based review. Ask follow-up questions anytime!")
github_link = st.text_area("📌 GitHub link to the project", placeholder="")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "initial_feedback" not in st.session_state:
    st.session_state.initial_feedback = None

if "project_uploaded" not in st.session_state:
    st.session_state.project_uploaded = False

if st.button("🧠 Review Project"):
    if github_link:
        project_data = clean_zip_file(github_link)
        requirements = project_data["requirements"]
        description = project_data["description"]
        project_directory = project_data["project_directory"]
        st.write("Project directory:")
        st.write(project_directory)
        st.write("Project Description: ")
        st.write(description)
        st.write("Project Requirements: ")
        st.write(requirements)
        st.session_state.chat_history = []
        st.session_state.requirements = requirements
        st.session_state.description = description
        st.success("Project review in progress...")
        feedback, project_data = analyze_project(project_directory, requirements, description)
        st.session_state.initial_feedback = feedback
        st.session_state.project_data = project_data
        st.session_state.project_uploaded = True

        ai_message = AIMessage(content=feedback)
        st.session_state.chat_history.append(ai_message)
    else:
        st.warning("Please upload a project zip file and enter your requirements.")

for msg in st.session_state.chat_history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.write(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.write(msg.content)

if st.session_state.project_uploaded and st.session_state.initial_feedback:
    if user_input := st.chat_input("💬 Ask a follow-up question..."):
        human_reply = HumanMessage(content=user_input)
        st.session_state.chat_history.append(human_reply)
        with st.spinner("Thinking..."):
            response = process_follow_up_message(
                st.session_state.chat_history,
                user_input,
                st.session_state.project_data
            )
        ai_reply = AIMessage(content=response)
        st.session_state.chat_history.append(ai_reply)
        st.rerun()
