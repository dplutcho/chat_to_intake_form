"""
ADK Multi-Agent Analytics Intake System
A guided chat-based intake application for standardizing analytics request collection.
"""

import json
import datetime
import asyncio
from typing import Dict, Any, Optional
from google.adk.agents import LlmAgent
from google.adk.tools import ToolContext


# for prompt call
import base64
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables from .env file
load_dotenv()


def prompt_call(prompt_text: str, model: str = "gemini-2.5-pro") -> str:
    """Send a single prompt to Gemini and return the full response text.

    Args:
        prompt_text: The user prompt to send to Gemini.
        model: The Gemini model name (default: "gemini-2.5-pro").

    Returns:
        The model’s text response.
    """
    # Create the SDK client (reads GOOGLE_API_KEY from env if not passed)
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    # Build the request payload
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt_text)],
        ),
    ]

    generate_config = types.GenerateContentConfig(
        temperature=0.25,
        thinking_config=types.ThinkingConfig(thinking_budget=-1),
        response_mime_type="text/plain",
    )

    # **Single, non-streaming call**
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_config,
    )

    return response.text

def summarize_analytics_request(request_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Uses Gemini to generate an insightful summary of the analytics request data.
    
    Args:
        request_data: Dictionary containing the analytics request details
        
    Returns:
        dict: Contains the AI-generated summary and status
    
    Purpose: {request_data.get('Report Purpose', 'Not specified')}
    Requested by: {request_data.get('Requester Name', 'Unknown')}
    Time Period: {request_data.get('Time Period', 'Not specified')}
    Data Source: {request_data.get('Data Source', 'Not specified')}
    Output Format: {request_data.get('Output Format', 'Not specified')}
    Segments/Filters: {request_data.get('Segments/Filters', 'None')}
    """
    try:

        # Create a prompt for Gemini to summarize the request
        prompt = f"""
        Please provide a clear and insightful summary of this analytics request:
        
        Requester information:
        {str(request_data)}
        
        Limit to 1 concise paragraph With three key bullet pointsAnd if possible a level of effort statement.
        """
        summary = prompt_call(prompt)

        return summary
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to generate summary: {str(e)}"
        }


def save_analytics_request(request_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Saves the collected analytics request data to a JSON file.
    
    Args:
        request_data: Dictionary containing all collected request information
        
    Returns:
        dict: Status message with file path and summary
    """
    try:
        print("[TOOL: Using the save and summarization tool]")# Generate timestamp for unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analytics_request_{timestamp}.json"
        
        # summarize the request
        print("summarizing the request")
        summary = summarize_analytics_request(request_data)
        request_data["request_summary"] = summary

        # Add metadata
        request_data["metadata"] = {
            "created_at": datetime.datetime.now().isoformat(),
            "status": "pending_review"
        }
        
        # Save to JSON file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(request_data, f, indent=2, ensure_ascii=False)
            
        return {
            "status": "success",
            "message": f"Analytics request saved successfully to {filename}",
            "file_path": filename,
            "summary": f"Request type: {request_data.get('request_type', 'unknown')}, "
                      f"Requester: {request_data.get('basic_info', {}).get('name', 'unknown')}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save request: {str(e)}"
        }


def validate_basic_info(name: str, role: str, department: str, timeline: str) -> Dict[str, Any]:
    """
    Validates and structures basic user information.
    
    Args:
        name: User's name
        role: User's role/title
        department: User's department
        timeline: When they need the request completed
        
    Returns:
        dict: Validation result with structured data
    """
    print("[TOOL: Using the Validation tool]")
    errors = []
    
    if not name or len(name.strip()) < 2:
        errors.append("Name must be at least 2 characters long")
    
    if not role or len(role.strip()) < 2:
        errors.append("Role must be specified")
        
    if not department or len(department.strip()) < 2:
        errors.append("Department must be specified")
        
    if not timeline or len(timeline.strip()) < 3:
        errors.append("Timeline must be specified")
    
    if errors:
        return {
            "valid": False,
            "errors": errors
        }
    
    return {
        "valid": True,
        "data": {
            "name": name.strip(),
            "role": role.strip(),
            "department": department.strip(),
            "timeline": timeline.strip(),
            "collected_at": datetime.datetime.now().isoformat()
        }
    }


# Summary Agents - One for each specialist
reports_summary_agent = LlmAgent(
    name="reports_summary_agent",
    model="gemini-2.0-flash",
    description="Formats and saves collected one-off report request information",
    instruction="""
    You are the Reports Summary Agent responsible for final processing of one-off report requests.
    
    Your tasks:
    1. Review all collected information from the conversation
    2. Format it into a clear, structured summary
    3. Use the save_analytics_request tool to save the complete request
    4. Provide a final confirmation to the user
    
    Always ensure the request contains:
    - Basic info (name, role, department, timeline)
    - Report purpose and specific requirements
    - All relevant details collected by the reports agent
    
    After saving, provide a friendly confirmation message with next steps.
    """,
    tools=[save_analytics_request]
)

dashboard_summary_agent = LlmAgent(
    name="dashboard_summary_agent",
    model="gemini-2.0-flash",
    description="Formats and saves collected dashboard request information",
    instruction="""
    You are the Dashboard Summary Agent responsible for final processing of dashboard requests.
    
    Your tasks:
    1. Review all collected information from the conversation
    2. Format it into a clear, structured summary
    3. Use the save_analytics_request tool to save the complete request
    4. Provide a final confirmation to the user
    
    Always ensure the request contains:
    - Basic info (name, role, department, timeline)
    - Dashboard purpose and specific requirements
    - All relevant details collected by the dashboard agent
    
    After saving, provide a friendly confirmation message with next steps.
    """,
    tools=[save_analytics_request]
)

updates_summary_agent = LlmAgent(
    name="updates_summary_agent",
    model="gemini-2.0-flash",
    description="Formats and saves collected update request information",
    instruction="""
    You are the Updates Summary Agent responsible for final processing of update requests.
    
    Your tasks:
    1. Review all collected information from the conversation
    2. Format it into a clear, structured summary
    3. Use the save_analytics_request tool to save the complete request
    4. Provide a final confirmation to the user
    
    Always ensure the request contains:
    - Basic info (name, role, department, timeline)
    - Update purpose and specific requirements
    - All relevant details collected by the updates agent
    
    After saving, provide a friendly confirmation message with next steps.
    """,
    tools=[save_analytics_request]
)

# Reports Agent - Handles one-off report requests
reports_agent = LlmAgent(
    name="reports_agent",
    model="gemini-2.0-flash",
    description="Collects detailed requirements for one-off report requests",
    instruction="""
    You are the Reports Agent specializing in one-off analytics reports.
    
    Collect these specific details:
    1. Report purpose/objective
    2. Key metrics needed (sales figures, conversion rates, etc.)
    3. Data sources (CRM, web analytics, sales database, etc.)
    4. Time period for data
    5. Filters/segments (by region, product, team, etc.)
    6. Output format (Excel, PDF, dashboard, email, etc.)
    7. Audience who will receive/use the report
    
    # Ask follow-up questions to clarify vague requirements.
    Once you have comprehensive details, transfer to reports_summary_agent for final processing.
    
    Be thorough but efficient - aim to get complete requirements in 3-5 exchanges.
    """,
    # instruction="Just say skipping these questionsanduse the reports_summary_agent sub agent now!!!",
    sub_agents=[reports_summary_agent]
)
#######################################################


# Dashboard Agent - Handles dashboard creation/updates
dashboard_agent = LlmAgent(
    name="dashboard_agent", 
    model="gemini-2.0-flash",
    description="Collects requirements for dashboard creation or updates",
    instruction="""
    You are the Dashboard Agent specializing in dashboard requests.
    
    Collect these specific details:
    1. Dashboard purpose (existing update vs new dashboard)
    2. If existing: dashboard name/location and specific changes needed
    3. Target audience (executives, sales team, operations, etc.)
    4. Key visualizations needed (charts, tables, KPIs, etc.)
    5. Data refresh frequency (real-time, daily, weekly, monthly)
    6. Key metrics and dimensions to display
    7. Interactivity requirements (filters, drill-downs, etc.)
    8. Integration needs (email alerts, embedding, etc.)
    
    For dashboard updates, be specific about what changes are needed.
    Once you have comprehensive details, transfer to dashboard_summary_agent for final processing.
    
    Be thorough but efficient - aim to get complete requirements in 3-5 exchanges.
    """,
    sub_agents=[dashboard_summary_agent]
)

# Updates Agent - Handles updates to existing reports
updates_agent = LlmAgent(
    name="updates_agent",
    model="gemini-2.0-flash", 
    description="Collects requirements for updating existing reports or analytics",
    instruction="""
    You are the Updates Agent specializing in modifications to existing analytics.
    
    Collect these specific details:
    1. Name/identifier of existing report/analysis
    2. Current location/access method
    3. Specific changes needed (new metrics, different time periods, etc.)
    4. Reason for the update (new business requirements, data issues, etc.)
    5. New data sources if any
    6. Timeline changes if any
    7. Format/distribution changes if any
    8. Who should be notified of the updates
    
    Be specific about what exactly needs to change vs what should stay the same.
    Once you have comprehensive details, transfer to updates_summary_agent for final processing.
    
    Be thorough but efficient - aim to get complete requirements in 3-5 exchanges.
    """,
    sub_agents=[updates_summary_agent]
)

# Intake Agent - Collects basic user information
intake_agent = LlmAgent(
    name="intake_agent",
    model="gemini-2.0-flash",
    description="Collects basic user information and determines request type",
    instruction="""
    You are the Intake Agent responsible for initial data collection.
    
    Your tasks:
    1. Warmly greet the user and explain you'll help gather their analytics request details
    2. Collect basic information:
       - Full name
       - Role/title  
       - Department/team
       - Timeline for when they need this completed
    3. Determine request type by asking what kind of analytics help they need
    4. Use validate_basic_info tool to check collected information
    5. Confirm all details with the user
    6. Transfer to the appropriate specialist agent:
       - reports_agent for one-off reports
       - dashboard_agent for dashboard requests  
       - updates_agent for updating existing analytics
    
    Be friendly and professional. If the user's request doesn't clearly fit one category, 
    ask clarifying questions to determine the best specialist agent.
    
    Only transfer after confirming you have complete basic info and request type.
    """,
    tools=[validate_basic_info],
    sub_agents=[reports_agent, dashboard_agent, updates_agent]
)


# Root Agent - Main coordinator
root_agent = LlmAgent(
    name="analytics_intake_coordinator",
    model="gemini-2.0-flash",
    description="Main coordinator for analytics request intake system",
    instruction="""
    You are the Analytics Intake Coordinator, the main entry point for our analytics request system.
    
    Your role:
    1. Welcome users to the analytics request intake system
    2. Explain that you'll guide them through a structured process to collect their requirements
    3. Immediately transfer to intake_agent to begin data collection
    4. Handle any general questions about the process
    
    Always start by transferring to intake_agent unless the user has specific questions about the system itself.
    
    Be professional, efficient, and helpful. Emphasize that this process will ensure their 
    analytics request is complete and can be processed quickly by the analytics team.
    """,
    sub_agents=[intake_agent]
)