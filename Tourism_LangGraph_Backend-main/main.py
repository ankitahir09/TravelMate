# main.py
from datetime import datetime
import os
import json
import operator
from typing import TypedDict, Annotated, List, Optional

from pydantic import BeforeValidator
from typing_extensions import Annotated

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from database import (
    add_vendors,
    find_vendor_by_id,
    find_vendor_by_type,
    ObjectId,
    find_all_vendors,
    find_vendors_by_city_and_type,
)

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
llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", temperature=0.2)


# --- 2. LANGGRAPH STATE DEFINITION ---


class TripPlanState(BaseModel):
    """Defines the structure of the agent's memory (state)."""

    destination: str = ""
    time_duration: str = ""
    interests: str = ""
    chat_history: List[BaseMessage] = Field(default_factory=list)
    itinerary: str = ""
    missing_info: str = ""
    next_action: str = ""
    itinerary_confirmed: bool = False

    fix_request: str = ""
    driver_details: str = ""
    hotel_details: str = ""


# --- 3. NODE FUNCTIONS ---
# Each function represents a step or "node" in our agent's thought process.
def route_from_start(state: TripPlanState) -> str:
    print("Node: route_from_start")
    if state.itinerary and state.itinerary_confirmed:
        print("Decision: Plan is fixed, routing to arrangement")
        return "ask_what_to_fix"
    elif state.itinerary and not state.itinerary_confirmed:
        print("Decision: Plan proposed but yet to be confirmed")
        return "handle_confirmation"
    else:
        print("Decision: No plan exists, routing to planning")
        return "planning_branch"


def parse_query_node(state: TripPlanState) -> dict:
    """
    The entry point. It parses the entire conversation to extract key details.
    This is more robust as it considers the whole context.
    """
    print("--- NODE: parse_query_node ---")
    prompt = f"""
    You are a strict information extraction engine. Analyze the ENTIRE conversation history below to extract the user's trip details.
    
    *CRITICAL RULES:*
    1. You MUST NOT infer, guess, or add any information that is not EXPLICITLY MENTIONed.
    2. For any field not found in the conversation (destination, time_duration, interests), you MUST use an empty string "".

    CONVERSATION HISTORY:
    {state.chat_history}

    Your response must be a single, valid JSON object.
    """

    json_llm = llm.bind(generation_config={"response_mime_type": "application/json"})
    chain = json_llm | StrOutputParser()
    response_str = chain.invoke(prompt)
    parsed_response = json.loads(response_str)
    print(f"Parsed Repsonse {parsed_response}")
    # Always update the state with the latest extracted info
    return {
        "destination": parsed_response.get("destination", state.destination),
        "time_duration": parsed_response.get("time_duration", state.time_duration),
        "interests": parsed_response.get("interests", state.interests),
    }


def check_details_node(state: TripPlanState) -> dict:
    """Checks the state to see if all required information has been collected."""
    print("--- NODE: check_details_node ---")
    prompt = f"""
    Check if all info is provided based on the state below.
    - Destination: {state.destination or 'Not provided'}
    - Time/Duration: {state.time_duration or 'Not provided'}
    - Interests: {state.interests or 'Not provided'}
    Reply with a comma-separated list of missing fields, or "OK" if nothing is missing.
    """
    response = llm.invoke(prompt)
    return {"missing_info": response.content.strip()}


def router_node(state: TripPlanState) -> str:
    """Routes the conversation to the correct node based on the state."""
    print("--- NODE: router_node ---")
    missing_info = (state.missing_info or "").lower()

    # Check the actual data fields first for robustness
    if not state.destination:
        return "get_destination"
    if not state.time_duration:
        return "get_time"
    if not state.interests:
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
    - Destination: {state.destination}
    - Duration: {state.time_duration}
    - Interests: {state.interests}
    Include local food suggestions, practical travel tips, and a day-by-day schedule.
    """
    response = llm.invoke(prompt)
    itinerary = response.content.strip()
    ai_message = AIMessage(
        content=f"Here is a proposed itinerary for your trip:\n\n{itinerary}\n\n Would you like to confrim it or not?"
    )
    return {
        "itinerary": itinerary,
        "chat_history": [ai_message],
        "next_action": "itinerary_generated",
    }


# In main.py, replace your handle_confirmation_node with this:


def start_node(state: TripPlanState) -> dict:
    """A simple node that just passes the state along. This is our entry point."""
    print("--- 1. Entering Graph ---")
    return {}


# --- 4. GRAPH DEFINITION AND COMPILATION ---

builder = StateGraph(TripPlanState)

# Add ALL nodes to the graph, including the new simple entry point
builder.add_node("start_node", start_node)
builder.add_node("parse_query", parse_query_node)
builder.add_node("check_details", check_details_node)
builder.add_node("get_destination", get_destination_node)
builder.add_node("get_time", get_time_node)
builder.add_node("get_interest", get_interest_node)
builder.add_node("get_itinerary", get_itinerary_node)


# 1. Set the simple, non-conditional entry point
builder.set_entry_point("start_node")

# 2. From the start_node, immediately branch based on the master router's decision
builder.add_edge("start_node", "parse_query")

# 3. Define all other edges for the branches
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
builder.add_edge("get_destination", END)
builder.add_edge("get_time", END)
builder.add_edge("get_interest", END)
builder.add_edge("get_itinerary", END)

# Compile the final graph
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


PyObjectId = Annotated[str, BeforeValidator(str)]


# --- Request Models ---
class ChatRequest(BaseModel):
    chat_history: List[dict]


class VendorRegistrationRequest(BaseModel):
    vendor_type: str = Field(..., example="Driver")
    business_name: str = Field(..., example="Gujarat Cabs")
    contact_name: str = Field(..., example="Suresh Patel")
    mobile_number: str = Field(..., example="9876543210")
    city: str = Field(..., example="Ahmedabad")
    summary: str = Field(..., example="AC Sedan for local tours.")
    portfolio_url: Optional[str] = Field(
        None, example="http://instagram.com/gujaratroads"
    )
    languages: Optional[List[str]] = Field(None, example=["Gujarati", "Hindi"])
    pan_number: Optional[str] = Field(None, example="ABCDE1234F")
    gstin: Optional[str] = Field(None, example="22AAAAA0000A1Z5")


# --- Response Models ---
class ChatResponse(BaseModel):
    ai_message: str
    next_action: str
    is_finished: bool


class VendorResponse(BaseModel):
    # This model is now complete and correctly handles ObjectId
    id: PyObjectId = Field(alias="_id", default=None)
    vendor_type: str
    business_name: str
    contact_name: str
    mobile_number: str
    city: str
    summary: str
    registration_date: datetime

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


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


@app.post("/vendors", response_model=VendorResponse)
async def register_vendor(vendor_data: VendorRegistrationRequest):
    vendor_dict = vendor_data.model_dump()
    try:
        new_vendor_id = add_vendors(vendor_dict)
        created_vendor = find_vendor_by_id(new_vendor_id)
        if not created_vendor:
            raise HTTPException(
                status_code=404, detail="Vendor not fount after creation"
            )
        created_vendor["id"] = str(created_vendor["_id"])
        return created_vendor
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


""


@app.get("/vendors", response_model=List[VendorResponse])
async def get_vendors(vendor_type: Optional[str] = None):
    if vendor_type:
        vendors = find_vendor_by_type(vendor_type)
    else:
        vendors = find_all_vendors()
    return vendors