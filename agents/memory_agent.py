# ============================================
# Agent Skill: Meeting Memory
# This module implements a reusable agent skill
# for persistent meeting memory storage and retrieval
# Key Concept: Agent Skills (Agents CLI)
# Demonstrated for Kaggle x Google 5-Day AI 
# Agents Capstone 2026
# ============================================

import json
import os

MEMORY_FILE = "memory_store.json"

def save_meeting(meeting_id: str, summary: dict, tasks: dict) -> bool:
    # Saves a meeting's summary and tasks to the local memory_store.json file under a meeting ID.
    try:
        data = {}
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                    
        data[meeting_id] = {
            "meeting_id": meeting_id,
            "summary": summary,
            "tasks": tasks
        }
        
        with open(MEMORY_FILE, "w") as f:
            json.dump(data, f, indent=2)
            
        return True
    except Exception as e:
        print(f"Error saving meeting to memory: {e}")
        return False

def search_memory(keyword: str) -> list:
    # Searches memory_store.json for meetings where keyword appears in summary or topics.
    # Returns list of matching meeting summaries.
    try:
        if not os.path.exists(MEMORY_FILE):
            return []
            
        with open(MEMORY_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            data = json.loads(content)
            
        matches = []
        kw = keyword.lower()
        for meeting in data.values():
            summary_dict = meeting.get("summary", {})
            summary_text = summary_dict.get("summary", "").lower()
            topics = [t.lower() for t in summary_dict.get("key_topics", [])]
            title = summary_dict.get("meeting_title", "").lower()
            
            if kw in summary_text or any(kw in topic for topic in topics) or kw in title:
                matches.append(summary_dict)
                
        return matches
    except Exception as e:
        print(f"Error searching memory: {e}")
        return []

def get_all_meetings() -> list:
    # Returns all stored meetings from the memory_store.json file.
    try:
        if not os.path.exists(MEMORY_FILE):
            return []
            
        with open(MEMORY_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            data = json.loads(content)
            
        return list(data.values())
    except Exception as e:
        print(f"Error getting all meetings: {e}")
        return []
