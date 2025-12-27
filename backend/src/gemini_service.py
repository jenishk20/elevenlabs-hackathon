import google.generativeai as genai
from pathlib import Path
from .config import GEMINI_API_KEY
from .memory_service import get_or_create_user_memory, UserMemory

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Load the companion persona prompt
PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_companion_prompt(user_name: str, memory_context: str = "") -> str:
    """Load and personalize the companion persona prompt with memory context."""
    prompt_path = PROMPTS_DIR / "companion_persona.txt"
    with open(prompt_path, "r") as f:
        prompt = f.read()
    
    # Add memory context
    full_prompt = prompt.replace("{user_name}", user_name)
    
    if memory_context:
        full_prompt += f"\n\n## What You Remember About {user_name}\n{memory_context}"
    
    return full_prompt


class GrandPalBrain:
    """The AI brain of GrandPal using Google Gemini with memory."""
    
    def __init__(self, user_id: str, user_name: str):
        self.user_id = user_id
        self.user_name = user_name
        self.conversation_history: list[dict] = []
        
        # Get or create user memory
        self.memory = get_or_create_user_memory(user_id, user_name)
        self.memory.increment_conversation()
        
        # Get memory context
        memory_context = self.memory.get_context_for_conversation()
        
        # Build system prompt with memory
        self.system_prompt = load_companion_prompt(user_name, memory_context)
        
        # Initialize Gemini model
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=self.system_prompt
        )
        self.chat = self.model.start_chat(history=[])
    
    def get_response(self, user_message: str) -> str:
        """Generate a response to the user's message."""
        try:
            # Add to history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Get response from Gemini
            response = self.chat.send_message(user_message)
            assistant_message = response.text
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant", 
                "content": assistant_message
            })
            
            return assistant_message
            
        except Exception as e:
            print(f"Error getting Gemini response: {e}")
            return f"I'm sorry, {self.user_name}, I had a little trouble there. Could you say that again?"
    
    def get_greeting(self) -> str:
        """Generate a personalized greeting based on memory."""
        memory_context = self.memory.get_context_for_conversation()
        conv_count = self.memory.memories.get("conversation_count", 1)
        
        if conv_count == 1:
            # First time meeting
            greeting_prompt = f"Generate a warm, friendly first greeting for {self.user_name} who you're meeting for the first time. Keep it to 1-2 sentences. Be warm and welcoming."
        else:
            # Returning user
            recent_topics = self.memory.memories.get("recent_topics", [])
            family = self.memory.memories.get("profile", {}).get("family_members", [])
            
            context = ""
            if recent_topics:
                context += f"Last time you talked about: {', '.join(recent_topics[-2:])}. "
            if family:
                context += f"You know about their family: {', '.join([m['name'] for m in family[:3]])}. "
            
            greeting_prompt = f"""Generate a warm greeting for {self.user_name} who you've talked to {conv_count} times before.
            
{context}

Reference something from previous conversations if relevant, or just give a warm "welcome back" greeting.
Keep it to 1-2 sentences. Be genuine and warm, like greeting an old friend."""
        
        return self.get_response(greeting_prompt)
    
    def analyze_emotion(self, text: str) -> dict:
        """Analyze the emotional content of text."""
        try:
            analysis_model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"""Analyze the emotional tone of this message and respond with ONLY a JSON object:
            
Message: "{text}"

Respond with exactly this format, no other text:
{{"emotion": "happy|sad|anxious|lonely|neutral|excited", "confidence": 0.0-1.0, "needs_support": true|false}}"""
            
            response = analysis_model.generate_content(prompt)
            import json
            return json.loads(response.text.strip())
        except Exception as e:
            print(f"Emotion analysis error: {e}")
            return {"emotion": "neutral", "confidence": 0.5, "needs_support": False}
    
    def get_conversation_transcript(self) -> str:
        """Get the full conversation transcript."""
        transcript = ""
        for msg in self.conversation_history:
            role = "GrandPal" if msg["role"] == "assistant" else self.user_name
            transcript += f"{role}: {msg['content']}\n\n"
        return transcript
    
    async def save_memories(self):
        """Extract and save memories from this conversation."""
        from .memory_service import extract_memories_from_conversation
        
        transcript = self.get_conversation_transcript()
        if transcript:
            await extract_memories_from_conversation(self.memory, transcript)


# Store active sessions
active_sessions: dict[str, GrandPalBrain] = {}


def get_or_create_session(session_id: str, user_name: str) -> GrandPalBrain:
    """Get an existing session or create a new one."""
    if session_id not in active_sessions:
        # Use a simplified user_id based on name for demo
        # In production, you'd use proper authentication
        user_id = user_name.lower().replace(" ", "_")
        active_sessions[session_id] = GrandPalBrain(user_id, user_name)
    return active_sessions[session_id]


async def end_session(session_id: str) -> None:
    """Clean up a session and save memories."""
    if session_id in active_sessions:
        brain = active_sessions[session_id]
        # Save memories before ending
        await brain.save_memories()
        del active_sessions[session_id]
