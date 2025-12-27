from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid

from .config import ELEVENLABS_AGENT_ID
from .gemini_service import get_or_create_session, end_session, active_sessions
from .elevenlabs_service import get_signed_url, get_agent_info, list_available_voices

# Create FastAPI app
app = FastAPI(
    title="GrandPal API",
    description="Backend API for GrandPal - AI Companion for the Elderly",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class StartConversationRequest(BaseModel):
    userName: str


class StartConversationResponse(BaseModel):
    sessionId: str
    signedUrl: str | None
    agentId: str
    greeting: str


class MessageRequest(BaseModel):
    sessionId: str
    message: str


class MessageResponse(BaseModel):
    response: str
    emotion: dict | None = None


class EndConversationRequest(BaseModel):
    sessionId: str


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "grandpal-api"}


# Start conversation endpoint
@app.post("/api/conversation/start", response_model=StartConversationResponse)
async def start_conversation(request: StartConversationRequest):
    """
    Start a new conversation session.
    Returns a signed URL for connecting to ElevenLabs agent.
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create Gemini brain session with memory
        brain = get_or_create_session(session_id, request.userName)
        
        # Get personalized greeting from the brain
        greeting = brain.get_greeting()
        
        # Try to get signed URL for ElevenLabs
        signed_url = None
        agent_id = ELEVENLABS_AGENT_ID
        
        if agent_id:
            try:
                signed_url = get_signed_url(agent_id)
            except Exception as e:
                print(f"Could not get signed URL: {e}")
        
        return StartConversationResponse(
            sessionId=session_id,
            signedUrl=signed_url,
            agentId=agent_id,
            greeting=greeting
        )
        
    except Exception as e:
        print(f"Error starting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Chat message endpoint (for webhook/tool calls from ElevenLabs)
@app.post("/api/conversation/message", response_model=MessageResponse)
async def send_message(request: MessageRequest):
    """
    Process a message and get a response from GrandPal.
    This is called by ElevenLabs agent as a tool/webhook.
    """
    try:
        if request.sessionId not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        brain = active_sessions[request.sessionId]
        
        # Get response
        response = brain.get_response(request.message)
        
        # Analyze emotion
        emotion = brain.analyze_emotion(request.message)
        
        return MessageResponse(
            response=response,
            emotion=emotion
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# End conversation endpoint
@app.post("/api/conversation/end")
async def end_conversation_endpoint(request: EndConversationRequest):
    """End a conversation session and save memories."""
    try:
        await end_session(request.sessionId)
        return {"status": "ended", "sessionId": request.sessionId, "memories_saved": True}
    except Exception as e:
        print(f"Error ending conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get agent info
@app.get("/api/agent/info")
async def agent_info():
    """Get information about the configured ElevenLabs agent."""
    info = get_agent_info()
    if not info:
        return {
            "configured": False,
            "message": "No agent configured. Create one in ElevenLabs dashboard and add ELEVENLABS_AGENT_ID to .env"
        }
    return {"configured": True, **info}


# List voices
@app.get("/api/voices")
async def voices():
    """List available ElevenLabs voices."""
    return {"voices": list_available_voices()}


# Get user memories (for debugging/demo)
@app.get("/api/memories/{user_name}")
async def get_memories(user_name: str):
    """Get stored memories for a user (for demo purposes)."""
    from .memory_service import MEMORY_DIR
    import json
    
    user_id = user_name.lower().replace(" ", "_")
    memory_file = MEMORY_DIR / f"{user_id}.json"
    
    if memory_file.exists():
        with open(memory_file, "r") as f:
            return json.load(f)
    
    return {"message": "No memories found for this user"}


if __name__ == "__main__":
    import uvicorn
    from .config import API_HOST, API_PORT
    
    uvicorn.run(app, host=API_HOST, port=API_PORT)
