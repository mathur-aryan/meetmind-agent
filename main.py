import os
from dotenv import load_dotenv
from agents.summarizer_agent import run_summarizer
from agents.task_agent import run_task_agent
from agents.followup_agent import run_followup_agent
from agents.memory_agent import save_meeting, search_memory
from utils.helpers import pretty_print_json, validate_transcript, format_task_list

def run_pipeline() -> None:
    # Runs the full multi-agent pipeline sequentially, printing output for each stage.
    
    # Step 1: Read sample_transcripts/sample1.txt
    print("\n--- Step 1: Reading Transcript ---")
    transcript_path = os.path.join("sample_transcripts", "sample1.txt")
    try:
        with open(transcript_path, "r") as f:
            transcript = f.read()
        print(f"Loaded transcript from {transcript_path}")
    except Exception as e:
        print(f"Error reading transcript file: {e}")
        return
        
    print("\n" + "=" * 60)
    
    # Step 2: Validate transcript using validate_transcript()
    print("--- Step 2: Validating Transcript ---")
    if not validate_transcript(transcript):
        print("Aborting: Transcript validation failed.")
        return
    print("Transcript validation successful.")
    
    print("\n" + "=" * 60)
    
    # Step 3: Run run_summarizer() and pretty_print_json output
    print("--- Step 3: Running Summarizer Agent ---")
    summary = run_summarizer(transcript)
    pretty_print_json(summary, "Summarizer Agent Output")
    
    print("\n" + "=" * 60)
    
    # Step 4: Run run_task_agent() and pretty_print_json output
    print("--- Step 4: Running Task Agent ---")
    tasks = run_task_agent(summary)
    pretty_print_json(tasks, "Task Agent Output")
    
    print("\n" + "=" * 60)
    
    # Step 5: Run run_followup_agent() and pretty_print_json output
    print("--- Step 5: Running Followup Agent ---")
    attendees = summary.get("attendees", [])
    followup = run_followup_agent(tasks, attendees)
    pretty_print_json(followup, "Followup Agent Output")
    
    print("\n" + "=" * 60)
    
    # Step 6: Run save_meeting() to store in memory
    print("--- Step 6: Saving Meeting to Memory ---")
    meeting_id = "meeting_sample_1"
    saved = save_meeting(meeting_id, summary, tasks)
    if saved:
        print(f"Successfully saved meeting {meeting_id} to memory.")
    else:
        print(f"Failed to save meeting {meeting_id} to memory.")
        
    print("\n" + "=" * 60)
    
    # Step 7: Run search_memory() with keyword "app" and print results
    print("--- Step 7: Searching Memory for 'app' ---")
    matches = search_memory("app")
    print(f"Found {len(matches)} matching meeting(s):")
    for i, match in enumerate(matches, start=1):
        pretty_print_json(match, f"Match {i}")
        
    print("\n" + "=" * 60)
    
    # Step 8: Print format_task_list() output
    print("--- Step 8: Formatting Task List ---")
    formatted_tasks = format_task_list(tasks)
    print(formatted_tasks)
    
    print("\n" + "=" * 60)
    
    # Step 9: Print "MeetMind Complete!" at the end
    print("--- Step 9: Pipeline Completion ---")
    print("MeetMind Complete!")
    print("MeetMind Phase 1 Complete!")

if __name__ == "__main__":
    # Main entry point of the pipeline script. Loads environmental variables and initiates pipeline execution.
    load_dotenv()
    run_pipeline()
