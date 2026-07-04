import os
import uuid
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv

from agents.summarizer_agent import run_summarizer
from agents.task_agent import run_task_agent
from agents.followup_agent import run_followup_agent
from agents.memory_agent import save_meeting, search_memory, get_all_meetings

load_dotenv()

app = Flask(__name__)
CORS(app)

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MeetMind Agent - AI Meeting Intelligence</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-color: #0f172a;
            --text-secondary: #475569;
            --text-muted: #64748b;
            --primary: #4f46e5;
            --primary-hover: #4338ca;
            --primary-light: #f5f3ff;
            --border: #e2e8f0;
            --blue: #2563eb;
            --blue-light: #eff6ff;
            --blue-border: #bfdbfe;
            --green: #10b981;
            --green-light: #ecfdf5;
            --green-border: #a7f3d0;
            --purple: #8b5cf6;
            --purple-light: #f5f3ff;
            --purple-border: #ddd6fe;
            --danger: #ef4444;
            --danger-light: #fee2e2;
            --warning: #f59e0b;
            --warning-light: #fef3c7;
            --radius-lg: 16px;
            --radius-md: 12px;
            --radius-sm: 8px;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
            --shadow-lg: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
            --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            padding: 2rem 1.5rem;
        }
        .container {
            max-width: 1280px;
            margin: 0 auto;
        }
        header {
            text-align: center;
            margin-bottom: 2.5rem;
        }
        header h1 {
            font-family: 'Outfit', sans-serif;
            font-size: 2.75rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        header p {
            font-family: 'Outfit', sans-serif;
            font-size: 1.2rem;
            color: var(--text-muted);
            font-weight: 500;
        }
        .layout-grid {
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 2rem;
            margin-bottom: 2.5rem;
        }
        @media (max-width: 960px) {
            .layout-grid {
                grid-template-columns: 1fr;
            }
        }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-sm);
            padding: 1.75rem;
            transition: var(--transition);
        }
        .card:hover {
            box-shadow: var(--shadow-md);
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.25rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.75rem;
        }
        .card-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--text-color);
        }
        .btn-link {
            background: none;
            border: none;
            color: var(--primary);
            font-weight: 600;
            font-size: 0.875rem;
            cursor: pointer;
            text-decoration: underline;
            transition: var(--transition);
        }
        .btn-link:hover {
            color: var(--primary-hover);
        }
        textarea {
            width: 100%;
            padding: 1rem;
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            font-family: inherit;
            font-size: 0.95rem;
            resize: vertical;
            background-color: #fafbfc;
            transition: var(--transition);
            margin-bottom: 1.25rem;
        }
        textarea:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1);
            background-color: #ffffff;
        }
        .btn-primary {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            padding: 0.875rem;
            background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
            color: #ffffff;
            border: none;
            border-radius: var(--radius-md);
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: var(--transition);
            box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2);
        }
        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
        }
        .btn-primary:active {
            transform: translateY(0);
        }
        .btn-primary:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        /* Search and History styling */
        .search-row {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1.25rem;
        }
        .search-input {
            flex: 1;
            padding: 0.75rem 1rem;
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            font-size: 0.95rem;
            transition: var(--transition);
        }
        .search-input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1);
        }
        .btn-search {
            padding: 0 1.25rem;
            background-color: var(--primary);
            color: white;
            border: none;
            border-radius: var(--radius-md);
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
        }
        .btn-search:hover {
            background-color: var(--primary-hover);
        }
        .history-list {
            list-style: none;
            max-height: 280px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            padding-right: 0.25rem;
        }
        .history-item {
            padding: 0.75rem 1rem;
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            cursor: pointer;
            transition: var(--transition);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .history-item:hover {
            border-color: var(--primary);
            background-color: var(--primary-light);
            transform: translateX(4px);
        }
        .history-item-title {
            font-weight: 600;
            font-size: 0.95rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 70%;
        }
        .history-item-id {
            font-size: 0.75rem;
            color: var(--text-muted);
            background: #f1f5f9;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
        }
        .empty-history {
            text-align: center;
            color: var(--text-muted);
            padding: 2.5rem 1rem;
            font-size: 0.9rem;
        }
        
        /* Spinner */
        .spinner-wrapper {
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 3rem 1rem;
            text-align: center;
        }
        .spinner {
            width: 44px;
            height: 44px;
            border: 4px solid var(--border);
            border-top-color: var(--primary);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-bottom: 1rem;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .spinner-text {
            font-weight: 600;
            color: var(--text-secondary);
        }

        /* Results Display */
        .results-section {
            display: none;
            margin-top: 1rem;
            animation: fadeIn 0.4s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .results-header {
            font-family: 'Outfit', sans-serif;
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1.25rem;
            border-bottom: 2px solid var(--border);
            padding-bottom: 0.75rem;
        }
        .meta-bar {
            background: linear-gradient(135deg, var(--blue-light) 0%, var(--purple-light) 100%);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 1rem 1.5rem;
            margin-bottom: 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        .meta-title {
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            font-size: 1.2rem;
            color: var(--text-color);
        }
        .meta-id {
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-muted);
            background: white;
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            border: 1px solid var(--border);
        }

        .results-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 1.5rem;
        }
        @media (max-width: 960px) {
            .results-grid {
                grid-template-columns: 1fr;
            }
        }
        .result-card {
            background: white;
            border-radius: var(--radius-lg);
            border: 1px solid var(--border);
            padding: 1.5rem;
            box-shadow: var(--shadow-sm);
            transition: var(--transition);
        }
        .result-card:hover {
            box-shadow: var(--shadow-md);
        }
        .card-blue {
            border-top: 4px solid var(--blue);
        }
        .card-green {
            border-top: 4px solid var(--green);
        }
        .card-purple {
            border-top: 4px solid var(--purple);
        }
        .result-card h3 {
            font-family: 'Outfit', sans-serif;
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 1.25rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .card-blue h3 { color: var(--blue); }
        .card-green h3 { color: var(--green); }
        .card-purple h3 { color: var(--purple); }

        .section-label {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-top: 1.25rem;
            margin-bottom: 0.5rem;
        }
        .section-label:first-of-type {
            margin-top: 0;
        }
        .summary-paragraph {
            font-size: 0.925rem;
            color: var(--text-secondary);
            line-height: 1.5;
        }
        .pills-box {
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
        }
        .pill-badge {
            background-color: #f1f5f9;
            color: var(--text-secondary);
            font-size: 0.775rem;
            font-weight: 500;
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            border: 1px solid var(--border);
        }
        .custom-list {
            list-style: none;
            padding-left: 0;
        }
        .custom-list li {
            position: relative;
            padding-left: 1.2rem;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
            color: var(--text-secondary);
        }
        .custom-list li::before {
            content: "•";
            color: var(--primary);
            font-weight: 800;
            font-size: 1.1rem;
            position: absolute;
            left: 0;
            top: -0.1rem;
        }

        /* Tasks list */
        .task-box {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }
        .task-card {
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 0.875rem;
            background: #fafafa;
            transition: var(--transition);
        }
        .task-card:hover {
            border-color: var(--green);
            background: white;
        }
        .task-card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 0.35rem;
            gap: 0.5rem;
        }
        .task-card-title {
            font-weight: 600;
            font-size: 0.925rem;
            color: var(--text-color);
        }
        .task-card-desc {
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-bottom: 0.6rem;
            line-height: 1.4;
        }
        .task-card-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.75rem;
        }
        .task-badge-owner {
            background-color: var(--primary-light);
            color: var(--primary);
            font-weight: 600;
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
        }
        .task-badge-deadline {
            color: var(--text-muted);
            font-style: italic;
        }
        /* Priorities badges */
        .priority-badge {
            font-size: 0.65rem;
            font-weight: 700;
            text-transform: uppercase;
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
            letter-spacing: 0.05em;
        }
        .priority-high {
            background-color: var(--danger-light);
            color: var(--danger);
        }
        .priority-medium {
            background-color: var(--warning-light);
            color: var(--warning);
        }
        .priority-low {
            background-color: var(--green-light);
            color: var(--green);
        }

        /* Emails list */
        .emails-box {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        .email-card {
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .email-card-header {
            background: #f8fafc;
            border-bottom: 1px solid var(--border);
            padding: 0.6rem 0.875rem;
            font-size: 0.8rem;
            color: var(--text-secondary);
        }
        .email-card-header span {
            font-weight: 600;
            color: var(--text-color);
        }
        .email-card-body-wrapper {
            padding: 0.875rem;
            position: relative;
            background: white;
        }
        .email-card-body {
            font-size: 0.825rem;
            color: var(--text-color);
            white-space: pre-wrap;
            line-height: 1.45;
            padding-top: 1.5rem;
        }
        .btn-copy {
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            padding: 0.2rem 0.5rem;
            font-size: 0.725rem;
            font-weight: 600;
            background: #f1f5f9;
            color: var(--text-secondary);
            border: 1px solid var(--border);
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-copy:hover {
            background: var(--purple-light);
            color: var(--purple);
            border-color: var(--purple-border);
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>MeetMind Agent</h1>
            <p>AI-Powered Meeting Intelligence</p>
        </header>

        <div class="layout-grid">
            <!-- Form Card -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">New Analysis</div>
                    <button class="btn-link" onclick="loadSample()">Load Sample Transcript</button>
                </div>
                <textarea id="transcriptInput" rows="10" placeholder="Paste your meeting transcript here... (Minimum 50 words)"></textarea>
                <button id="analyzeBtn" class="btn-primary" onclick="analyzeMeeting()">Analyze Meeting</button>
            </div>

            <!-- Memory Card -->
            <div class="card">
                <div class="card-header">
                    <div class="card-title">Meeting Memory</div>
                </div>
                <div class="search-row">
                    <input type="text" id="searchInput" class="search-input" placeholder="Search saved meetings..." onkeyup="handleSearchKey(event)">
                    <button class="btn-search" onclick="searchMeetings()">Search</button>
                </div>
                <ul id="historyList" class="history-list">
                    <!-- Dynamic -->
                </ul>
            </div>
        </div>

        <!-- Spinner -->
        <div id="loadingSpinner" class="spinner-wrapper">
            <div class="spinner"></div>
            <div class="spinner-text">Analyzing transcript via sequential multi-agent pipeline...</div>
        </div>

        <!-- Results Container -->
        <div id="resultsSection" class="results-section">
            <div class="results-header">Analysis Results</div>
            
            <div id="metaBar" class="meta-bar">
                <!-- Dynamic -->
            </div>

            <div class="results-grid">
                <!-- Summary Card -->
                <div class="result-card card-blue">
                    <h3>
                        <svg width="18" height="18" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
                        Meeting Summary
                    </h3>
                    
                    <div class="section-label">Title</div>
                    <p id="resultTitle" style="font-weight: 600; font-size: 1.05rem; margin-bottom: 1rem;"></p>

                    <div class="section-label">Attendees</div>
                    <div id="resultAttendees" class="pills-box" style="margin-bottom: 1rem;"></div>

                    <div class="section-label">Summary</div>
                    <p id="resultSummaryText" class="summary-paragraph" style="margin-bottom: 1rem;"></p>

                    <div class="section-label">Key Topics</div>
                    <ul id="resultTopics" class="custom-list" style="margin-bottom: 1rem;"></ul>

                    <div class="section-label">Key Decisions</div>
                    <ul id="resultDecisions" class="custom-list"></ul>
                </div>

                <!-- Tasks Card -->
                <div class="result-card card-green">
                    <h3>
                        <svg width="18" height="18" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
                        Action Items
                    </h3>
                    <div id="resultTasks" class="task-box"></div>
                </div>

                <!-- Emails Card -->
                <div class="result-card card-purple">
                    <h3>
                        <svg width="18" height="18" fill="currentColor" viewBox="0 0 24 24"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>
                        Draft Emails
                    </h3>
                    <div id="resultEmails" class="emails-box"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const sampleTranscript = `Attendees: Sarah (Product Manager), Alex (Lead Developer), Liam (UX Designer), Maya (QA Engineer)

Sarah: Hi everyone, let's start today's standup. We need to align on our upcoming mobile app launch. Alex, how is the development progress?

Alex: Dev is on track. The core functionalities are completed. I am currently resolving a memory leak on the login screen. I should finish that today. However, we need to decide on the staging environment for our final integrations.

Sarah: Good point. Let's make a decision: we will use the AWS staging environment for final integration testing, as it matches our production setup best. Also, we must finalize the beta list.

Liam: I have finished the high-fidelity UI designs. I need someone to review the flow of the onboarding process to make sure the onboarding is smooth.

Sarah: Maya, could you review Liam's onboarding designs by next Monday?

Maya: Sure, I can do that. I've also completed the initial test plan, but I need access to the latest staging credentials to begin API testing.

Sarah: Okay, let's decide that Liam will share the staging credentials securely via 1Password by tomorrow morning.

Alex: Great. For the mobile app launch itself, we are targeting next Friday.

Sarah: Yes, that is our firm deadline. We must submit the app to the App Store and Google Play by next Friday. Here are the action items:
1. Alex will fix the login screen memory leak by this Friday.
2. Liam will draft the App Store description and promotional assets by next Tuesday.
3. Maya will complete the regression testing on the AWS staging environment by next Wednesday.
4. Sarah will prepare the launch checklist and coordinate with marketing by next Thursday.

Sarah: Let's meet again tomorrow. Thanks everyone!`;

        let windowMeetings = [];

        document.addEventListener('DOMContentLoaded', () => {
            loadHistory();
        });

        function loadSample() {
            document.getElementById('transcriptInput').value = sampleTranscript;
        }

        function handleSearchKey(event) {
            if (event.key === 'Enter') {
                searchMeetings();
            }
        }

        async function loadHistory() {
            const listEl = document.getElementById('historyList');
            listEl.innerHTML = '';
            
            try {
                const res = await fetch('/memory');
                if (!res.ok) throw new Error();
                const data = await res.json();
                windowMeetings = data; // stores array of meetings
                renderHistory(data);
            } catch(e) {
                listEl.innerHTML = '<li class="empty-history" style="color:var(--danger);">Error loading history</li>';
            }
        }

        function renderHistory(meetings) {
            const listEl = document.getElementById('historyList');
            listEl.innerHTML = '';
            
            if (!meetings || meetings.length === 0) {
                listEl.innerHTML = '<li class="empty-history">No saved meetings in memory</li>';
                return;
            }
            
            // Render newer meetings first
            const sorted = [...meetings].reverse();
            sorted.forEach(meet => {
                const li = document.createElement('li');
                li.className = 'history-item';
                const title = meet.summary?.meeting_title || 'Untitled Meeting';
                li.innerHTML = `
                    <span class="history-item-title">${title}</span>
                    <span class="history-item-id">${meet.meeting_id}</span>
                `;
                li.onclick = () => selectMeeting(meet);
                listEl.appendChild(li);
            });
        }

        async function searchMeetings() {
            const query = document.getElementById('searchInput').value.trim();
            if (!query) {
                renderHistory(windowMeetings);
                return;
            }

            const listEl = document.getElementById('historyList');
            listEl.innerHTML = '<li class="empty-history">Searching...</li>';

            try {
                const res = await fetch(`/search?q=${encodeURIComponent(query)}`);
                if (!res.ok) throw new Error();
                const summaries = await res.json();
                
                // search_memory in memory_agent.py returns list of summary dicts.
                // We map these matched summaries to their full meeting objects stored in windowMeetings.
                const matchedMeetings = [];
                summaries.forEach(sum => {
                    const match = windowMeetings.find(m => m.summary && m.summary.meeting_title === sum.meeting_title);
                    if (match) {
                        matchedMeetings.push(match);
                    } else {
                        // Create virtual full meeting object if full object is not present locally
                        matchedMeetings.push({
                            meeting_id: 'Loaded',
                            summary: sum,
                            tasks: { tasks: [] }
                        });
                    }
                });
                renderHistory(matchedMeetings);
            } catch(e) {
                listEl.innerHTML = '<li class="empty-history" style="color:var(--danger)">Search failed</li>';
            }
        }

        function selectMeeting(meet) {
            const resultsSection = document.getElementById('resultsSection');
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth' });

            // Set meta
            const metaBar = document.getElementById('metaBar');
            metaBar.innerHTML = `
                <span class="meta-title">${meet.summary?.meeting_title || 'Untitled Meeting'}</span>
                <span class="meta-id">ID: ${meet.meeting_id}</span>
            `;

            // Summary Card
            document.getElementById('resultTitle').innerText = meet.summary?.meeting_title || 'Untitled Meeting';
            document.getElementById('resultSummaryText').innerText = meet.summary?.summary || 'No summary text available.';
            
            const attendeesBox = document.getElementById('resultAttendees');
            attendeesBox.innerHTML = '';
            (meet.summary?.attendees || []).forEach(att => {
                const badge = document.createElement('span');
                badge.className = 'pill-badge';
                badge.innerText = att;
                attendeesBox.appendChild(badge);
            });

            const topicsBox = document.getElementById('resultTopics');
            topicsBox.innerHTML = '';
            (meet.summary?.key_topics || []).forEach(top => {
                const li = document.createElement('li');
                li.innerText = top;
                topicsBox.appendChild(li);
            });

            const decisionsBox = document.getElementById('resultDecisions');
            decisionsBox.innerHTML = '';
            (meet.summary?.key_decisions || []).forEach(dec => {
                const li = document.createElement('li');
                li.innerText = dec;
                decisionsBox.appendChild(li);
            });

            // Tasks Card
            const tasksBox = document.getElementById('resultTasks');
            tasksBox.innerHTML = '';
            const tasksList = meet.tasks?.tasks || [];
            if (tasksList.length === 0) {
                tasksBox.innerHTML = '<div class="empty-history" style="padding: 1.5rem 0;">No tasks found</div>';
            } else {
                tasksList.forEach((task, idx) => {
                    const taskCard = document.createElement('div');
                    taskCard.className = 'task-card';
                    const priorityClass = getPriorityClass(task.priority);
                    taskCard.innerHTML = `
                        <div class="task-card-header">
                            <span class="task-card-title">${idx + 1}. ${task.title}</span>
                            <span class="priority-badge ${priorityClass}">${task.priority}</span>
                        </div>
                        <div class="task-card-desc">${task.description}</div>
                        <div class="task-card-footer">
                            <span class="task-badge-owner">${task.owner}</span>
                            <span class="task-badge-deadline">Due: ${task.deadline}</span>
                        </div>
                    `;
                    tasksBox.appendChild(taskCard);
                });
            }

            // Emails Card (Emails are only returned on fresh analysis, show notice)
            const emailsBox = document.getElementById('resultEmails');
            emailsBox.innerHTML = '';
            if (meet.emails && meet.emails.emails && meet.emails.emails.length > 0) {
                renderEmails(meet.emails.emails);
            } else {
                emailsBox.innerHTML = '<div class="empty-history" style="padding:1.5rem 0;">Email drafts are only available during fresh analysis.</div>';
            }
        }

        function getPriorityClass(priority) {
            const p = String(priority).toLowerCase();
            if (p === 'high') return 'priority-high';
            if (p === 'medium') return 'priority-medium';
            return 'priority-low';
        }

        function renderEmails(emails) {
            const emailsBox = document.getElementById('resultEmails');
            emailsBox.innerHTML = '';
            emails.forEach(email => {
                const card = document.createElement('div');
                card.className = 'email-card';
                card.innerHTML = `
                    <div class="email-card-header">
                        <div><span>To:</span> ${email.to}</div>
                        <div><span>Subject:</span> ${email.subject}</div>
                    </div>
                    <div class="email-card-body-wrapper">
                        <button class="btn-copy" onclick="copyToClipboard(this, \`\${email.subject}\\n\\n\${email.body}\`)">Copy</button>
                        <div class="email-card-body">${email.body}</div>
                    </div>
                `;
                emailsBox.appendChild(card);
            });
        }

        async function analyzeMeeting() {
            const transcript = document.getElementById('transcriptInput').value.trim();
            if (!transcript) {
                alert('Please enter a transcript.');
                return;
            }

            const btn = document.getElementById('analyzeBtn');
            const spinner = document.getElementById('loadingSpinner');
            const resultsSection = document.getElementById('resultsSection');

            resultsSection.style.display = 'none';
            spinner.style.display = 'flex';
            btn.disabled = true;

            try {
                const res = await fetch('/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ transcript })
                });
                
                const data = await res.json();
                if (!res.ok) throw new Error(data.error || 'Failed to analyze');

                // Display new result
                resultsSection.style.display = 'block';
                
                const metaBar = document.getElementById('metaBar');
                metaBar.innerHTML = `
                    <span class="meta-title">${data.summary.meeting_title}</span>
                    <span class="meta-id">ID: ${data.meeting_id}</span>
                `;

                document.getElementById('resultTitle').innerText = data.summary.meeting_title;
                document.getElementById('resultSummaryText').innerText = data.summary.summary;

                const attBox = document.getElementById('resultAttendees');
                attBox.innerHTML = '';
                data.summary.attendees.forEach(att => {
                    const span = document.createElement('span');
                    span.className = 'pill-badge';
                    span.innerText = att;
                    attBox.appendChild(span);
                });

                const topBox = document.getElementById('resultTopics');
                topBox.innerHTML = '';
                data.summary.key_topics.forEach(top => {
                    const li = document.createElement('li');
                    li.innerText = top;
                    topBox.appendChild(li);
                });

                const decBox = document.getElementById('resultDecisions');
                decBox.innerHTML = '';
                data.summary.key_decisions.forEach(dec => {
                    const li = document.createElement('li');
                    li.innerText = dec;
                    decBox.appendChild(li);
                });

                // Tasks
                const tasksBox = document.getElementById('resultTasks');
                tasksBox.innerHTML = '';
                const tasks = data.tasks.tasks || [];
                if (tasks.length === 0) {
                    tasksBox.innerHTML = '<div class="empty-history" style="padding:1.5rem 0;">No tasks found</div>';
                } else {
                    tasks.forEach((task, idx) => {
                        const taskCard = document.createElement('div');
                        taskCard.className = 'task-card';
                        const priorityClass = getPriorityClass(task.priority);
                        taskCard.innerHTML = `
                            <div class="task-card-header">
                                <span class="task-card-title">${idx + 1}. ${task.title}</span>
                                <span class="priority-badge ${priorityClass}">${task.priority}</span>
                            </div>
                            <div class="task-card-desc">${task.description}</div>
                            <div class="task-card-footer">
                                <span class="task-badge-owner">${task.owner}</span>
                                <span class="task-badge-deadline">Due: ${task.deadline}</span>
                            </div>
                        `;
                        tasksBox.appendChild(taskCard);
                    });
                }

                // Emails
                const emailsBox = document.getElementById('resultEmails');
                emailsBox.innerHTML = '';
                const emails = data.emails.emails || [];
                if (emails.length === 0) {
                    emailsBox.innerHTML = '<div class="empty-history" style="padding:1.5rem 0;">No email drafts generated</div>';
                } else {
                    renderEmails(emails);
                }

                // Refresh history listing and reload page memory
                loadHistory();

                resultsSection.scrollIntoView({ behavior: 'smooth' });
            } catch(e) {
                alert('Analysis failed: ' + e.message);
            } finally {
                spinner.style.display = 'none';
                btn.disabled = false;
            }
        }

        function copyToClipboard(btn, text) {
            navigator.clipboard.writeText(text).then(() => {
                const originalText = btn.innerText;
                btn.innerText = 'Copied!';
                btn.style.background = 'var(--green-light)';
                btn.style.color = 'var(--green)';
                btn.style.borderColor = 'var(--green-border)';
                setTimeout(() => {
                    btn.innerText = originalText;
                    btn.style.background = '#f1f5f9';
                    btn.style.color = 'var(--text-secondary)';
                    btn.style.borderColor = 'var(--border)';
                }, 2000);
            }).catch(() => {
                alert('Copy failed');
            });
        }
    </script>
</body>
</html>"""

@app.route('/', methods=['GET'])
def index() -> str:
    # Root endpoint rendering the MeetMind UI
    return render_template_string(HTML_TEMPLATE)

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
