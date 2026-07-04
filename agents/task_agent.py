import os
import json
import asyncio
from pydantic import BaseModel, Field
from google.genai import types
from google.adk import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

class TaskItem(BaseModel):
    id: str
    title: str
    description: str
    owner: str
    deadline: str
    priority: str
    status: str

class TaskOutput(BaseModel):
    tasks: list[TaskItem]
    total_tasks: int
    high_priority_count: int

async def _run_task_agent_async(summary_str: str) -> str:
    # Sets up and runs the Google ADK TaskAgent to extract action items from a summary.
    agent = Agent(
        name="task_agent",
        model="gemini-3.5-flash",
        instruction=(
            "Extract action items from the meeting summary JSON. "
            "Only create tasks that have a clear action verb. "
            "Make sure every task has an owner (default to 'Unassigned' if not mentioned), "
            "a deadline, a priority (High, Medium, Low), and status set to 'Pending'. "
            "Ensure the output conforms exactly to the TaskOutput schema."
        ),
        output_schema=TaskOutput
    )
    
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, session_service=session_service, app_name="meetmind")
    
    session = await runner.session_service.create_session(
        app_name="meetmind",
        user_id="user_task",
        session_id="session_task"
    )
    
    new_msg = types.Content(
        role="user",
        parts=[types.Part.from_text(text=summary_str)]
    )
    
    response_text = ""
    async for event in runner.run_async(
        user_id="user_task",
        session_id=session.id,
        new_message=new_msg
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text
                    
    return response_text

def run_task_agent(summary_json: dict) -> dict:
    # Takes the SummarizerAgent JSON output dict as input, runs the TaskAgent, and returns structured tasks JSON.
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY is not set in environment.")
        
    summary_str = json.dumps(summary_json)
    
    try:
        raw_output = asyncio.run(_run_task_agent_async(summary_str))
    except Exception as e:
        print(f"Error during TaskAgent execution: {e}")
        raw_output = "{}"
        
    try:
        cleaned = raw_output.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
            
        data = json.loads(cleaned)
        
        # Post-process for safety
        if "tasks" not in data:
            data["tasks"] = []
        
        # Ensure owner is present and defaults to 'Unassigned'
        for t in data["tasks"]:
            if not t.get("owner") or str(t.get("owner")).strip() == "":
                t["owner"] = "Unassigned"
            if not t.get("status"):
                t["status"] = "Pending"
                
        data["total_tasks"] = len(data["tasks"])
        data["high_priority_count"] = sum(1 for t in data["tasks"] if str(t.get("priority")).lower() == "high")
        
        print(f"Extraction complete! Found {data['total_tasks']} tasks.")
        return data
    except Exception as e:
        print(f"Error parsing TaskAgent response JSON: {e}")
        return {
            "tasks": [],
            "total_tasks": 0,
            "high_priority_count": 0
        }
