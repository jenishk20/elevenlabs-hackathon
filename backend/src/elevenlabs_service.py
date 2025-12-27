from elevenlabs.client import ElevenLabs
from .config import ELEVENLABS_API_KEY, ELEVENLABS_AGENT_ID

# Initialize ElevenLabs client
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)


def get_signed_url(agent_id: str | None = None) -> str:
    """
    Get a signed URL for connecting to an ElevenLabs Conversational AI agent.
    This URL is used by the frontend to establish a WebSocket connection.
    """
    try:
        agent_id = agent_id or ELEVENLABS_AGENT_ID
        if not agent_id:
            raise ValueError("No agent ID configured. Create an agent in ElevenLabs dashboard first.")
        
        # Get signed URL for the conversation
        response = client.conversational_ai.get_signed_url(agent_id=agent_id)
        return response.signed_url
    except Exception as e:
        print(f"Error getting signed URL: {e}")
        raise


def list_available_voices() -> list[dict]:
    """List available voices for the agent."""
    try:
        voices = client.voices.get_all()
        return [
            {
                "voice_id": voice.voice_id,
                "name": voice.name,
                "category": voice.category,
            }
            for voice in voices.voices
        ]
    except Exception as e:
        print(f"Error listing voices: {e}")
        return []


def get_agent_info(agent_id: str | None = None) -> dict | None:
    """Get information about the configured agent."""
    try:
        agent_id = agent_id or ELEVENLABS_AGENT_ID
        if not agent_id:
            return None
        
        agent = client.conversational_ai.get_agent(agent_id=agent_id)
        return {
            "agent_id": agent.agent_id,
            "name": agent.name,
        }
    except Exception as e:
        print(f"Error getting agent info: {e}")
        return None

