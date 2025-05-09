import streamlit as st

st.set_page_config(page_title="AI Project Reviewer", layout="wide")

st.title("🤖 AI Project Reviewer")
st.markdown("Upload your project files and enter your requirements to get an AI-based review. Ask follow-up questions anytime!")
st.sidebar.header("Upload Project Files")
uploaded_zip = st.sidebar.file_uploader("Upload your project folder (.zip)", type="zip")
requirements = st.text_area("📌 Project Requirements", placeholder="Describe the expected behavior, features, or goals...")

if "file_inputs" not in st.session_state:
    st.session_state.file_inputs = [{"name": "", "desc": ""}]

if st.button("➕ Add File Entry"):
    st.session_state.file_inputs.append({"name": "", "desc": ""})

for i, entry in enumerate(st.session_state.file_inputs):
    st.text_input(f"File Name #{i+1}", key=f"filename_{i}", value=entry["name"])
    st.text_area(f"Description #{i+1}", key=f"description_{i}", value=entry["desc"])

if st.button("🧠 Review Project"):
    if not uploaded_zip or not requirements.strip():
        st.warning("Please upload at least one file and provide the requirements.")
    else:
        st.success("✅ Project reviewed successfully!")
        analysis_result = "Here is a sample analysis of your project based on the uploaded files and given requirements."
        st.session_state.chat_history.append(("AI", analysis_result))

if st.session_state.chat_history:
    st.subheader("💬 Review & Chat")
    for role, message in st.session_state.chat_history:
        if role == "User":
            st.markdown(f"**You:** {message}")
        else:
            st.markdown(f"**AI:** {message}")

    user_question = st.text_input("Ask a follow-up question")
    if st.button("Send Question"):
        if user_question.strip():
            st.session_state.chat_history.append(("User", user_question))
            # Placeholder AI response
            ai_response = f"This is a response to your question: '{user_question}'."
            st.session_state.chat_history.append(("AI", ai_response))
        else:
            st.warning("Please enter a question before sending.")

