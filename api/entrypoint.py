from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
import os
from uuid import uuid4
from datetime import datetime, timedelta
from ask_llm import AskLLM
import dotenv

dotenv.load_dotenv()

app = Flask(__name__, static_folder="static")
# Simple CORS configuration allowing all origins
CORS(app, supports_credentials=True, origins="*")

llm_sessions = {}


@app.route("/api/analyze", methods=["POST"])
def analyze_repo():
    """Endpoint to analyze a GitHub repository."""
    data = request.json
    repo_url = data.get("repoUrl")
    session_id = request.json.get("sessionId") or str(uuid4())
    ask_llm = AskLLM(repo_url)
    ask_llm.extract_files()

    if not repo_url:
        return jsonify({"error": "Repository URL and message are required"}), 400

    try:
        print("Launching repo analyzis : ", repo_url)
        message = ask_llm.analyze_project()
        llm_sessions[session_id] = {"llm": ask_llm, "last_accessed": datetime.now()}
        return jsonify({"response": message, "sessionId": session_id}), 200

    except Exception as e:
        print("Exception in /api/analyze:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    """Endpoint to handle chat messages about a repository."""
    session_id = request.json.get("sessionId")
    if not session_id or session_id not in llm_sessions:
        return jsonify({"error": "Repository must be analyzed first"}), 400

    data = request.json
    user_message = data.get("message")
    ask_llm = llm_sessions[session_id]["llm"]
    llm_sessions[session_id]["last_accessed"] = datetime.now()

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        reply = ask_llm.ask_followup(user_message)
        print(f"Reply type: {type(reply)}")
        return jsonify({"response": reply}), 200

    except Exception as e:
        print("Exception in /api/chat:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path and os.path.exists(app.static_folder + "/" + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


def cleanup_sessions(timeout_minutes=30):
    now = datetime.now()
    expired = [
        sid
        for sid, data in llm_sessions.items()
        if now - data["last_accessed"] > timedelta(minutes=timeout_minutes)
    ]
    for sid in expired:
        print(f"Cleaning up session {sid}")
        del llm_sessions[sid]


@app.before_request
def before_request():
    cleanup_sessions()

@app.before_request
def log_sessions():
    if request.path.startswith('/api'):
        print(f"[Before request] API call to {request.path} — Current sessions: {list(llm_sessions.keys())}")



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    print("Starting flask server...")
    app.run(host="0.0.0.0", port=port, debug=True)
    print(f"Server running at http://localhost:{port}")
