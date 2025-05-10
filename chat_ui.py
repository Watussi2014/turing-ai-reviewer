import streamlit as st
from project_analysis import analyze_project
st.set_page_config(page_title="AI Project Reviewer", layout="wide")

st.title("🤖 AI Project Reviewer")
st.markdown("Upload your project files and enter your requirements to get an AI-based review. Ask follow-up questions anytime!")
st.sidebar.header("Upload Project Files")
uploaded_zip = st.sidebar.file_uploader("Upload your project folder (.zip)", type="zip")
description = st.text_area("📌 Project Description", placeholder="")
requirements = st.text_area("📌 Project Requirements", placeholder="Describe the expected behavior, features, or goals...")

# if "file_inputs" not in st.session_state:
#     st.session_state.file_inputs = []
#
# if st.button("➕ Add File Entry"):
#     st.session_state.file_inputs.append("")
#
# file_names = []
# st.subheader("📂 Relevant Files to Analyze")
# for i in range(len(st.session_state.file_inputs)):
#     file_key = f"filename_{i}"
#     file_value = st.text_input(f"File Name #{i+1}", key=file_key, value=st.session_state.file_inputs[i])
#     st.session_state.file_inputs[i] = file_value  # Persist edits
#     file_names.append(file_value)

# if file_names:
#     st.markdown("#### 📝 Files to Analyze")
#     for fname in file_names:
#         st.markdown(f"- `{fname}`")

if st.button("🧠 Review Project"):
    if uploaded_zip and requirements and description:
        st.session_state.chat_history = []
        st.session_state.requirements = requirements
        st.session_state.description = description
        analyze_project(uploaded_zip, requirements, description)
        st.success("Project review in progress...")
    else:
        st.warning("Please upload a project zip file and enter your requirements.")
    user_question = st.text_input("Ask a follow-up question")
    if st.button("Send Question"):
        if user_question.strip():
            st.session_state.chat_history.append(("User", user_question))
            ai_response = f"This is a response to your question: '{user_question}'."
            st.session_state.chat_history.append(("AI", ai_response))
        else:
            st.warning("Please enter a question before sending.")

