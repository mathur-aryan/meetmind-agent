import json
import sys

def pretty_print_json(data: dict, title: str) -> None:
    # Prints the title as a colored header with === borders and data formatted as indented JSON.
    print(f"\033[92m=== {title} ===\033[0m")
    try:
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error printing JSON: {e}")
    print("\033[92m" + "=" * (len(title) + 8) + "\033[0m")

def validate_transcript(text: str) -> bool:
    # Checks if the text has at least 50 words. Returns False and prints warning if not, True otherwise.
    words = text.strip().split()
    if len(words) < 50:
        print(f"\033[91mWarning: Transcript is under 50 words (found {len(words)} words).\033[0m")
        return False
    return True

def format_task_list(tasks_json: dict) -> str:
    # Returns a clean, readable string of tasks formatted as a numbered list with owner and priority.
    try:
        tasks = tasks_json.get("tasks", [])
        if not tasks:
            return "No tasks identified."
        lines = []
        for i, task in enumerate(tasks, start=1):
            title = task.get("title", "No Title")
            owner = task.get("owner", "Unassigned")
            priority = task.get("priority", "Medium")
            lines.append(f"{i}. {title} - Owner: {owner} (Priority: {priority})")
        return "\n".join(lines)
    except Exception as e:
        return f"Error formatting task list: {str(e)}"
