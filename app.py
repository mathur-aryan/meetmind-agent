import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from agents.summarizer_agent import run_summarizer
from agents.task_agent import run_task_agent
from agents.followup_agent import run_followup_agent
from agents.memory_agent import save_meeting, search_memory, get_all_meetings

load_dotenv()

app = Flask(__name__)
CORS(app)

def sanitize_input(text: str) -> str:
    # Security Feature: Input Sanitization
    # Strips prompt injection patterns before 
    # passing to agents
    patterns = [
        "ignore previous instructions",
        "ignore all instructions",
        "system:",
        "you are now",
        "forget everything",
        "new instructions:"
    ]
    cleaned = text
    for pattern in patterns:
        cleaned = cleaned.replace(pattern, "")
        cleaned = cleaned.replace(pattern.upper(), "")
    return cleaned.strip()

@app.route('/analyze', methods=['POST'])
def analyze() -> tuple:
    # Post route accepting meeting transcript JSON, sanitizing it, running the pipeline, and storing the result in memory.
    try:
        req_data = request.get_json()
        if not req_data or "transcript" not in req_data:
            return jsonify({"error": "Missing 'transcript' field in request JSON"}), 400
            
        raw_transcript = req_data["transcript"]
        sanitized_transcript = sanitize_input(raw_transcript)
        
        # 1. Summarizer Agent
        summary = run_summarizer(sanitized_transcript)
        
        # 2. Task Agent
        tasks = run_task_agent(summary)
        
        # 3. Followup Agent
        attendees = summary.get("attendees", [])
        emails = run_followup_agent(tasks, attendees)
        
        # 4. Memory Agent
        meeting_id = f"meet_{uuid.uuid4().hex[:8]}"
        saved = save_meeting(meeting_id, summary, tasks)
        
        combined_response = {
            "meeting_id": meeting_id,
            "summary": summary,
            "tasks": tasks,
            "emails": emails,
            "saved_to_memory": saved
        }
        return jsonify(combined_response), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": f"Internal pipeline execution error: {str(e)}"}), 500

@app.route('/memory', methods=['GET'])
def memory() -> tuple:
    # Get route returning all stored meetings from the memory agent.
    try:
        meetings = get_all_meetings()
        return jsonify(meetings), 200
    except Exception as e:
        return jsonify({"error": f"Error retrieving memory: {str(e)}"}), 500

@app.route('/search', methods=['GET'])
def search() -> tuple:
    # Get route searching memory_store for meetings matching the 'q' keyword query parameter.
    try:
        query = request.args.get("q", "")
        if not query:
            return jsonify({"error": "Missing query parameter 'q'"}), 400
            
        results = search_memory(query)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": f"Error searching memory: {str(e)}"}), 500

if __name__ == "__main__":
    # Starts the server on port 8080.
    app.run(host="0.0.0.0", port=8080)
