from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from ask_llm import AskLLM
import dotenv


dotenv.load_dotenv()

app = Flask(__name__, static_folder='static')
# Simple CORS configuration allowing all origins
CORS(app, supports_credentials=True, origins="*")

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

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

def main():
    port = int(os.environ.get('PORT', 3000))
    print("Starting flask server...")
    app.run(host='0.0.0.0', port=port, debug=True)
    print(f"Server running at http://localhost:{port}")

if __name__ == '__main__':
    main()