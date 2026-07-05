# ============================================
# Agent Skill: Meeting Memory
# This module implements a reusable agent skill
# for persistent meeting memory storage and retrieval
# Key Concept: Agent Skills (Agents CLI)
# Demonstrated for Kaggle x Google 5-Day AI 
# Agents Capstone 2026
# ============================================

# In-memory store – survives across requests within
# the same serverless invocation / process lifetime.
MEMORY_STORE = {}


def save_meeting(meeting_id: str, summary: dict, tasks: dict) -> bool:
    # Saves a meeting's summary and tasks to the in-memory store under a meeting ID.
    try:
        MEMORY_STORE[meeting_id] = {
            "meeting_id": meeting_id,
            "summary": summary,
            "tasks": tasks,
        }
        return True
    except Exception as e:
        print(f"Error saving meeting to memory: {e}")
        return False


def search_memory(keyword: str) -> list:
    # Searches MEMORY_STORE for meetings where keyword appears in
    # summary text or key_topics. Case-insensitive.
    # Returns list of matching meeting summary dicts.
    try:
        if not MEMORY_STORE:
            return []

        matches = []
        kw = keyword.lower()

        for meeting in MEMORY_STORE.values():
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
    # Returns all stored meetings from MEMORY_STORE.
    try:
        return list(MEMORY_STORE.values())
    except Exception as e:
        print(f"Error getting all meetings: {e}")
        return []
