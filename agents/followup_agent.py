import os
import json
import asyncio
from pydantic import BaseModel, Field
from google.genai import types
from google.adk import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

class EmailItem(BaseModel):
    to: str
    subject: str
    body: str

class FollowupOutput(BaseModel):
    emails: list[EmailItem]
    total_emails: int

async def _run_followup_agent_async(prompt_str: str) -> str:
    # Sets up and runs the Google ADK FollowupAgent to generate emails for attendees.
    agent = Agent(
        name="followup_agent",
        model="gemini-3.5-flash",
        instruction=(
            "Generate professional follow-up emails for the meeting attendees. "
            "Generate one email per unique task owner found in the tasks list. "
            "Do not generate emails for 'Unassigned'. "
            "Ensure each email body is professional and under 150 words. "
            "Conform exactly to the FollowupOutput schema."
        ),
        output_schema=FollowupOutput
    )
    
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, session_service=session_service, app_name="meetmind")
    
    session = await runner.session_service.create_session(
        app_name="meetmind",
        user_id="user_followup",
        session_id="session_followup"
    )
    
    new_msg = types.Content(
        role="user",
        parts=[types.Part.from_text(text=prompt_str)]
    )
    
    response_text = ""
    async for event in runner.run_async(
        user_id="user_followup",
        session_id=session.id,
        new_message=new_msg
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text
                    
    return response_text

def run_followup_agent(tasks_json: dict, attendees: list) -> dict:
    # Takes task list dict and attendees list as input, runs the FollowupAgent, and returns email structured JSON.
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY is not set in environment.")
        
    prompt_payload = {
        "tasks": tasks_json.get("tasks", []),
        "attendees": attendees
    }
    prompt_str = json.dumps(prompt_payload)
    
    try:
        raw_output = asyncio.run(_run_followup_agent_async(prompt_str))
    except Exception as e:
        print(f"Error during FollowupAgent execution: {e}")
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
        
        if "emails" not in data:
            data["emails"] = []
            
        data["total_emails"] = len(data["emails"])
        return data
    except Exception as e:
        print(f"Error parsing FollowupAgent response JSON: {e}")
        return {
            "emails": [],
            "total_emails": 0
        }
