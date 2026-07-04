import os
import json
import asyncio
from pydantic import BaseModel, Field
from google.genai import types
from google.adk import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

class SummarizerOutput(BaseModel):
    meeting_title: str
    attendees: list[str]
    key_topics: list[str]
    key_decisions: list[str]
    summary: str

async def _run_summarizer_async(transcript: str) -> str:
    # Set up and execute the Google ADK Summarizer agent using Gemini 3.5 Flash.
    agent = Agent(
        name="summarizer_agent",
        model="gemini-3.5-flash",
        instruction=(
            "Extract meeting summary. You must conform to the output schema. "
            "Ensure that you extract: meeting_title, attendees, key_topics, key_decisions, and summary."
        ),
        output_schema=SummarizerOutput
    )
    
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, session_service=session_service, app_name="meetmind")
    
    session = await runner.session_service.create_session(
        app_name="meetmind",
        user_id="user_summarizer",
        session_id="session_summarizer"
    )
    
    new_msg = types.Content(
        role="user",
        parts=[types.Part.from_text(text=transcript)]
    )
    
    response_text = ""
    async for event in runner.run_async(
        user_id="user_summarizer",
        session_id=session.id,
        new_message=new_msg
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text
                    
    return response_text

def run_summarizer(transcript: str) -> dict:
    # Takes a raw meeting transcript string as input and uses the SummarizerAgent to return a structured dict.
    words = transcript.strip().split()
    if len(words) < 50:
        raise ValueError("Transcript is empty or too short (under 50 words).")
        
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY is not set in environment.")
        
    try:
        raw_output = asyncio.run(_run_summarizer_async(transcript))
    except Exception as e:
        print(f"Error during SummarizerAgent execution: {e}")
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
        
        # Verify schema match
        required_fields = ["meeting_title", "attendees", "key_topics", "key_decisions", "summary"]
        for field in required_fields:
            if field not in data:
                if field in ["attendees", "key_topics", "key_decisions"]:
                    data[field] = []
                else:
                    data[field] = "unknown"
                    
        print("Success: Summarization complete!")
        return data
    except Exception as e:
        print(f"Error parsing Summarizer response JSON: {e}")
        return {
            "meeting_title": "unknown",
            "attendees": [],
            "key_topics": [],
            "key_decisions": [],
            "summary": "unknown"
        }
