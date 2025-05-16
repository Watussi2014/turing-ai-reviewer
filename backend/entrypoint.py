from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from project_reviewer import ProjectReviewer
from uuid import uuid4
from datetime import datetime, timedelta
import dotenv
import logging
from requests.exceptions import HTTPError

dotenv.load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static")
CORS(app, supports_credentials=True, origins="*")

llm_sessions = {}


@app.route("/api/analyze", methods=["POST"])
def analyze_repo():
    """Endpoint to analyze a GitHub repository."""

    global llm_cache
    data = request.json

    try:
        repo_url = data.get("repoUrl")
    except HTTPError as e:
        log.error("Exception in /api/analyze: %s", str(e))
        return jsonify(
            {
                "message": "Error processing the repository. Please make sure the repo is publicly available."
            }
        ), 500

    session_id = request.json.get("sessionId", str(uuid4()))
    ask_llm = ProjectReviewer(repo_url)
    ask_llm.extract_files()

    if not repo_url:
        return jsonify({"error": "Repository URL and message are required"}), 400

    try:
        log.info(
            "Launching analysis of repo:\n  Repo URL: %s\n  Session ID: %s",
            repo_url,
            session_id,
        )
        message = ask_llm.analyze_project()
        llm_sessions[session_id] = {"llm": ask_llm, "last_accessed": datetime.now()}
        return jsonify({"response": message, "sessionId": session_id}), 200

    except Exception as e:
        log.error("Exception in /api/analyze: %s", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    """Endpoint to handle chat messages about a repository."""
    data = request.json
    session_id = data.get("sessionId")
    user_message = data.get("message")
    ask_llm = llm_sessions[session_id]["llm"]
    llm_sessions[session_id]["last_accessed"] = datetime.now()

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        reply = ask_llm.ask_followup(user_message)
        return jsonify({"response": reply}), 200

    except Exception as e:
        log.error("Exception in /api/chat: %s", str(e))
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
    if request.path.startswith("/api"):
        log.info(
            "[Before request] API call to %s — Current sessions: %s",
            request.path,
            list(llm_sessions.keys()),
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    log.info("Starting flask server...")
    app.run(host="0.0.0.0", port=port, debug=True)
    log.info(f"Server running at http://localhost:{port}")
