from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from download_util import clean_zip_file
from ask_llm import AskLLM

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Simple CORS configuration allowing all origins
CORS(app, supports_credentials=True, origins="*")

# Get GitHub token from environment variables
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
headers = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}

# Store repo data in memory (for simplicity)
repo_cache = {}

llm_cache = None

@app.route('/api/analyze', methods=['POST'])
def analyze_repo():
    """Endpoint to analyze a GitHub repository."""
    global llm_cache
    data = request.json
    repo_url = data.get('repoUrl')
    print(repo_url)
    ask_llm = AskLLM(repo_url)
    ask_llm.extract_files()
    
    
    if not repo_url:
        return jsonify({'error': 'Repository URL and message are required'}), 400
    
    message = ask_llm.analyze_project()
    llm_cache = ask_llm
    
    return jsonify({'response': message}), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint to handle chat messages about a repository."""
    global llm_cache
    if llm_cache is None:
        return jsonify({'error': 'Repository must be analyzed first'}), 400
    data = request.json
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    # Assuming AskLLM has a method to respond to messages
    reply = llm_cache.ask_followup(user_message)
    print(f"Reply type: {type(reply)}")

    return jsonify({'response': reply}), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"Server running at http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)