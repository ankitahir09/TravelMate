# main.py

import os
import json
import operator
from typing import TypedDict, Annotated, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langchain_core.output_parsers import StrOutputParser

# --- 1. SETUP AND CONFIGURATION ---

# Load environment variables from a .env file
load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY is missing from your .env file.")

# Initialize the Language Model
llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash-latest", temperature=0.2)


# --- 2. LANGGRAPH STATE DEFINITION ---


class TripPlanState(TypedDict):
    """Defines the structure of the agent's memory (state)."""

    destination: Optional[str]
    time_duration: Optional[str]
    interests: Optional[str]
    chat_history: Annotated[List[BaseMessage], operator.add]
    itinerary: Optional[str]
    missing_info: Optional[str]
    next_action: Optional[str]


# --- 3. NODE FUNCTIONS ---
# Each function represents a step or "node" in our agent's thought process.


def parse_query_node(state: TripPlanState) -> dict:
    """
    The entry point. It parses the entire conversation to extract key details.
    This is more robust as it considers the whole context.
    """
    print("--- NODE: parse_query_node ---")
    prompt = f"""
    You are a strict information extraction engine. Analyze the ENTIRE conversation history below to extract the user's trip details.
    
    **CRITICAL RULES:**
    1. You MUST NOT infer, guess, or add any information that is not EXPLICITLY MENTIONed.
    2. For any field not found in the conversation (destination, time_duration, interests), you MUST use an empty string "".

    CONVERSATION HISTORY:
    {state['chat_history']}

    Your response must be a single, valid JSON object.
    """
    json_llm = llm.bind(generation_config={"response_mime_type": "application/json"})
    chain = json_llm | StrOutputParser()
    response_str = chain.invoke(prompt)
    parsed_response = json.loads(response_str)

    # Always update the state with the latest extracted info
    return {
        "destination": parsed_response.get("destination", state.get("destination")),
        "time_duration": parsed_response.get(
            "time_duration", state.get("time_duration")
        ),
        "interests": parsed_response.get("interests", state.get("interests")),
    }


def check_details_node(state: TripPlanState) -> dict:
    """Checks the state to see if all required information has been collected."""
    print("--- NODE: check_details_node ---")
    prompt = f"""
    Check if all info is provided based on the state below.
    - Destination: {state.get('destination') or 'Not provided'}
    - Time/Duration: {state.get('time_duration') or 'Not provided'}
    - Interests: {state.get('interests') or 'Not provided'}
    Reply with a comma-separated list of missing fields, or "OK" if nothing is missing.
    """
    response = llm.invoke(prompt)
    return {"missing_info": response.content.strip()}


def router_node(state: TripPlanState) -> str:
    """Routes the conversation to the correct node based on the state."""
    print("--- NODE: router_node ---")
    missing_info = state.get("missing_info", "").lower()

    # Check the actual data fields first for robustness
    if not state.get("destination"):
        return "get_destination"
    if not state.get("time_duration"):
        return "get_time"
    if not state.get("interests"):
        return "get_interest"

    # If all fields are present, check the LLM's confirmation
    if "ok" in missing_info:
        return "get_itinerary"

    return "end"


def get_destination_node(state: TripPlanState) -> dict:
    """Asks the user for the destination."""
    print("--- NODE: get_destination_node ---")
    ai_message = AIMessage(content="Where are you planning to go?")
    return {"chat_history": [ai_message], "next_action": "user_provides_destination"}


def get_time_node(state: TripPlanState) -> dict:
    """Asks the user for the trip duration."""
    print("--- NODE: get_time_node ---")
    ai_message = AIMessage(
        content="How long will your trip be? (e.g., 2 days, a weekend)"
    )
    return {"chat_history": [ai_message], "next_action": "user_provides_time"}


def get_interest_node(state: TripPlanState) -> dict:
    """Asks the user for their interests."""
    print("--- NODE: get_interest_node ---")
    ai_message = AIMessage(content="What kind of activities do you enjoy on trips?")
    return {"chat_history": [ai_message], "next_action": "user_provides_interest"}


def get_itinerary_node(state: TripPlanState) -> dict:
    """Generates the final trip itinerary."""
    print("--- NODE: get_itinerary_node ---")
    prompt = f"""
    Create a detailed trip itinerary based on the following plan:
    - Destination: {state['destination']}
    - Duration: {state['time_duration']}
    - Interests: {state['interests']}
    Include local food suggestions, practical travel tips, and a day-by-day schedule.
    """
    response = llm.invoke(prompt)
    itinerary = response.content.strip()
    ai_message = AIMessage(content=itinerary)
    return {
        "itinerary": itinerary,
        "chat_history": [ai_message],
        "next_action": "finished",
    }


# --- 4. GRAPH DEFINITION AND COMPILATION ---

builder = StateGraph(TripPlanState)

# Add nodes to the graph
builder.add_node("parse_query", parse_query_node)
builder.add_node("check_details", check_details_node)
builder.add_node("get_destination", get_destination_node)
builder.add_node("get_time", get_time_node)
builder.add_node("get_interest", get_interest_node)
builder.add_node("get_itinerary", get_itinerary_node)

# Define the graph's workflow and edges
builder.set_entry_point("parse_query")
builder.add_edge("parse_query", "check_details")

builder.add_conditional_edges(
    "check_details",
    router_node,
    {
        "get_destination": "get_destination",
        "get_time": "get_time",
        "get_interest": "get_interest",
        "get_itinerary": "get_itinerary",
        "end": END,
    },
)

# After asking a question, the graph's work for this turn is done.
builder.add_edge("get_destination", END)
builder.add_edge("get_time", END)
builder.add_edge("get_interest", END)
builder.add_edge("get_itinerary", END)

# Compile the graph
graph = builder.compile()


# --- 5. FASTAPI APPLICATION ---

app = FastAPI(title="Stateless Trip Planner API")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # WARNING: For development only. Restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define the structure of the request from the frontend
class ChatRequest(BaseModel):
    chat_history: List[dict]  # Expects a list of {"role": "user/ai", "content": "..."}


# Define the structure of the response to the frontend
class ChatResponse(BaseModel):
    ai_message: str
    next_action: str
    is_finished: bool


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main API endpoint for the chat agent."""

    # Convert the list of dictionaries from the request into LangChain message objects
    chat_history = []
    for msg in request.chat_history:
        if msg.get("role") == "user":
            chat_history.append(HumanMessage(content=msg.get("content", "")))
        elif msg.get("role") == "ai":
            chat_history.append(AIMessage(content=msg.get("content", "")))

    # Invoke the graph with the current conversation history
    # The graph will run from the beginning with the full context on every call
    final_state = graph.invoke({"chat_history": chat_history})

    # Extract the necessary info from the final state to send to the frontend
    ai_response_message = final_state.get("chat_history", [])[-1].content
    next_action = final_state.get("next_action", "")
    is_finished = next_action == "finished"

    return ChatResponse(
        ai_message=ai_response_message,
        next_action=next_action,
        is_finished=is_finished,
    )


@app.get("/")
def root():
    return {"status": "online", "message": "Welcome to the Trip Planner API"}
