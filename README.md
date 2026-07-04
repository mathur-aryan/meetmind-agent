# MeetMind Agent

[![Kaggle x Google 5-Day AI Agents 2026](https://img.shields.io/badge/Kaggle%20x%20Google-5--Day%20AI%20Agents%202026-blue?style=for-the-badge&logo=kaggle&logoColor=white)](https://www.kaggle.com)

An automated 4-agent AI intelligence pipeline that transforms unstructured meeting transcripts into structured summaries, actionable task items, draft follow-up emails, and persistent long-term memory using Google ADK and Gemini 3.5 Flash.

---

## 1. Architecture Diagram

Below is the sequential multi-agent orchestration pipeline showing how the transcript data flows from input to final storage and output:

```text
  ┌──────────────┐
  │  Transcript  │
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │  Summarizer  │  ──> Extract Title, Attendees, Key Topics, & Decisions
  │    Agent     │
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │  Task Agent  │  ──> Parse Tasks, Owners, Deadlines, & Priority
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │  Followup    │  ──> Generate custom emails for each assignee
  │    Agent     │
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ Memory Agent │  ──> Persistent JSON memory store (memory_store.json)
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │    Output    │  ──> Structured CLI logs & HTTP JSON API responses
  └──────────────┘
```

---

## 2. Key Concepts Used

This application demonstrates four central design patterns for building modern LLM-based agent applications:

1. **Multi-Agent Orchestration / Pipeline**
   Agents are organized in a sequential pipeline where the outputs of preceding agents act as the input prompt context for the next. This divides a complex task (transcript processing) into focused, single-purpose roles.
2. **Structured Output Enforcement**
   Using the Google ADK's `output_schema` parameter backed by Pydantic models (such as `SummarizerOutput`, `TaskOutput`, and `FollowupOutput`), ensuring that the LLM response always conforms to a predefined JSON format for safe API/code ingestion.
3. **Persistent Local Memory (Agent Skill)**
   Implements a local JSON-based memory skill (`memory_store.json`) capable of saving session histories, listing stored meetings, and executing keyword search queries over past meeting content.
4. **Input Sanitization & Security**
   Protects downstream agents from prompt-injection vulnerabilities by executing an input sanitization step that strips malicious command patterns (e.g. `"ignore previous instructions"`) from transcripts before LLM processing.

---

## 3. Tech Stack

- **Framework / SDK**: [Google Agent Development Kit (ADK)](https://github.com/google/adk) & Google GenAI SDK
- **Language / Runtime**: Python 3.10+ & Asyncio
- **Foundation Models**: Google Gemini 3.5 Flash (`gemini-3.5-flash`)
- **API Server**: Flask & Flask-CORS
- **Libraries**: Pydantic v2 (Validation & Schemas), Python-dotenv

---

## 4. Setup Instructions

Follow these step-by-step instructions to get the project set up locally:

### Step 1: Clone & Navigate
Navigate into the project folder:
```bash
cd "meetmind"
```

### Step 2: Create a Virtual Environment
Create and activate a virtual environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
Install all package requirements:
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create a file named `.env` in the root directory (`meetmind/`) and add your Gemini API Key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 5. How to Run Locally

You can run MeetMind in two different modes:

### Option A: Command Line Interface (CLI) Pipeline
Run the fully sequential test pipeline on the sample transcript file:
```bash
python main.py
```
This reads the transcript from `sample_transcripts/sample1.txt`, validates it, runs the multi-agent pipeline, saves it to memory, and searches for matching records.

### Option B: Local API Server
Start the Flask web server to expose HTTP endpoints:
```bash
python app.py
```
By default, the server runs locally on **http://localhost:8080**.

---

## 6. API Endpoints

When running `app.py`, the following HTTP API routes are exposed:

### 1. Run Pipeline
* **Endpoint**: `POST /analyze`
* **Content-Type**: `application/json`
* **Request Body**:
  ```json
  {
    "transcript": "Meeting transcript text goes here..."
  }
  ```
* **Response**: `200 OK`
  ```json
  {
    "meeting_id": "meet_a1b2c3d4",
    "summary": {
      "meeting_title": "...",
      "attendees": ["...", "..."],
      "key_topics": ["..."],
      "key_decisions": ["..."],
      "summary": "..."
    },
    "tasks": {
      "tasks": [
        {
          "id": "1",
          "title": "...",
          "description": "...",
          "owner": "...",
          "deadline": "...",
          "priority": "...",
          "status": "Pending"
        }
      ],
      "total_tasks": 1,
      "high_priority_count": 0
    },
    "emails": {
      "emails": [
        {
          "to": "...",
          "subject": "...",
          "body": "..."
        }
      ],
      "total_emails": 1
    },
    "saved_to_memory": true
  }
  ```

### 2. Get All Meetings
* **Endpoint**: `GET /memory`
* **Response**: `200 OK`
  Returns an array of all meetings saved in the memory JSON store.

### 3. Search Memory
* **Endpoint**: `GET /search?q=<keyword>`
* **Response**: `200 OK`
  Returns an array of matching meeting summaries where the query keyword `<keyword>` matches the meeting title, summary content, or key topics.

---

## 7. Project Structure

Here is the directory layout of the `meetmind` project:

```text
meetmind/
├── agents/                      # Multi-agent implementations
│   ├── __init__.py
│   ├── followup_agent.py        # Email drafting agent
│   ├── memory_agent.py          # Memory storage and query utility
│   ├── summarizer_agent.py      # Meeting summarization agent
│   └── task_agent.py            # Task extraction agent
├── sample_transcripts/          # Testing sample materials
│   └── sample1.txt              # Standard sample meeting transcript
├── utils/                       # Shared utility functions
│   ├── __init__.py
│   └── helpers.py               # Formatting, logging, validation helpers
├── .env.example                 # Example configuration file
├── .gitignore                   # Specifies files to ignore from Git
├── app.py                       # Flask server entrypoint (HTTP APIs)
├── main.py                      # CLI testing entrypoint (Full pipeline run)
├── requirements.txt             # Python project dependencies
└── README.md                    # Project documentation (This file)
```

---

## 8. Capstone Validation

This agent project is submitted as a Capstone project for the **Kaggle x Google 5-Day AI Agents 2026** course, showcasing production-ready AI agent architectures using the official Google ADK.
