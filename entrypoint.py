from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from download_util import clean_zip_file

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

@app.route('/api/analyze', methods=['POST'])
def analyze_repo():
    """Endpoint to analyze a GitHub repository."""
    data = request.json
    repo_url = data.get('repoUrl')
    print(repo_url)
    output = clean_zip_file(repo_url)
    
    if not repo_url:
        return jsonify({'error': 'Repository URL and message are required'}), 400
    
    message = output['description']
    
    return jsonify({'response': f'The project has been analyzed. Here is the project description: {message}'}), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint to handle chat messages about a repository."""
    data = request.json
    repo_url = data.get('repoUrl')
    output = clean_zip_file(repo_url)
    
    if not repo_url:
        return jsonify({'error': 'Repository URL and message are required'}), 400
    
    message = output['description']
    
    return jsonify({'response': f'The project has been analyzed. Here is the project description: {message}'}), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f"Server running at http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)