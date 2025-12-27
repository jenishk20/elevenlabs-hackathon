"""
Conversation Memory Service for GrandPal

This service manages persistent memory across conversations,
allowing GrandPal to remember:
- User's name and preferences
- Family member names (spouse, children, grandchildren)
- Important life events and stories shared
- Health mentions
- Interests and hobbies
- Recent conversation topics

For the hackathon, we use a simple JSON file storage.
In production, this would use Firestore or another database.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional
import google.generativeai as genai
from .config import GEMINI_API_KEY

# Configure Gemini for memory extraction
genai.configure(api_key=GEMINI_API_KEY)

# Memory storage path
MEMORY_DIR = Path(__file__).parent.parent / "data" / "memories"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)


class UserMemory:
    """Manages memory for a single user."""
    
    def __init__(self, user_id: str, user_name: str):
        self.user_id = user_id
        self.user_name = user_name
        self.memory_file = MEMORY_DIR / f"{user_id}.json"
        self.memories = self._load_memories()
    
    def _load_memories(self) -> dict:
        """Load existing memories from file."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        
        # Initialize new memory structure
        return {
            "user_name": self.user_name,
            "created_at": datetime.now().isoformat(),
            "last_conversation": None,
            "profile": {
                "family_members": [],  # {"name": "Emma", "relation": "granddaughter", "details": "plays soccer"}
                "health_notes": [],    # ["mentioned knee pain", "taking medication for blood pressure"]
                "interests": [],       # ["gardening", "watching old movies", "crossword puzzles"]
                "important_dates": [], # {"date": "1955-06-15", "event": "wedding anniversary"}
                "location": None,      # "Boston, Massachusetts"
                "occupation": None,    # "retired teacher"
            },
            "stories": [],  # Significant stories or memories they've shared
            "recent_topics": [],  # Last few conversation topics for continuity
            "conversation_count": 0,
        }
    
    def save(self):
        """Persist memories to file."""
        self.memories["last_conversation"] = datetime.now().isoformat()
        with open(self.memory_file, "w") as f:
            json.dump(self.memories, f, indent=2)
    
    def get_context_for_conversation(self) -> str:
        """Generate context string to include in AI prompts."""
        profile = self.memories.get("profile", {})
        
        context_parts = [f"User's name: {self.user_name}"]
        
        # Family members
        family = profile.get("family_members", [])
        if family:
            family_str = ", ".join([
                f"{m['name']} ({m['relation']})" + (f" - {m['details']}" if m.get('details') else "")
                for m in family[:5]  # Limit to 5 most relevant
            ])
            context_parts.append(f"Family: {family_str}")
        
        # Health notes
        health = profile.get("health_notes", [])
        if health:
            context_parts.append(f"Health notes: {'; '.join(health[-3:])}")
        
        # Interests
        interests = profile.get("interests", [])
        if interests:
            context_parts.append(f"Interests: {', '.join(interests[:5])}")
        
        # Recent topics
        recent = self.memories.get("recent_topics", [])
        if recent:
            context_parts.append(f"Recent conversation topics: {', '.join(recent[-3:])}")
        
        # Conversation count for relationship depth
        count = self.memories.get("conversation_count", 0)
        if count > 0:
            context_parts.append(f"You've had {count} conversations with {self.user_name}")
        
        return "\n".join(context_parts)
    
    def increment_conversation(self):
        """Track that a new conversation started."""
        self.memories["conversation_count"] = self.memories.get("conversation_count", 0) + 1
        self.save()
    
    def add_family_member(self, name: str, relation: str, details: str = ""):
        """Add or update a family member."""
        family = self.memories["profile"]["family_members"]
        
        # Check if already exists
        for member in family:
            if member["name"].lower() == name.lower():
                member["relation"] = relation
                if details:
                    member["details"] = details
                self.save()
                return
        
        # Add new
        family.append({"name": name, "relation": relation, "details": details})
        self.save()
    
    def add_interest(self, interest: str):
        """Add an interest if not already present."""
        interests = self.memories["profile"]["interests"]
        if interest.lower() not in [i.lower() for i in interests]:
            interests.append(interest)
            self.save()
    
    def add_health_note(self, note: str):
        """Add a health-related note."""
        self.memories["profile"]["health_notes"].append(note)
        # Keep only last 10 health notes
        self.memories["profile"]["health_notes"] = self.memories["profile"]["health_notes"][-10:]
        self.save()
    
    def add_recent_topic(self, topic: str):
        """Track recent conversation topic."""
        self.memories["recent_topics"].append(topic)
        # Keep only last 5 topics
        self.memories["recent_topics"] = self.memories["recent_topics"][-5:]
        self.save()
    
    def add_story(self, summary: str):
        """Store a significant story or memory shared."""
        self.memories["stories"].append({
            "summary": summary,
            "date": datetime.now().isoformat()
        })
        # Keep only last 20 stories
        self.memories["stories"] = self.memories["stories"][-20:]
        self.save()


async def extract_memories_from_conversation(
    user_memory: UserMemory,
    conversation_transcript: str
) -> dict:
    """
    Use Gemini to extract memorable information from the conversation.
    This runs after a conversation ends to update the user's memory.
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""Analyze this conversation and extract any important information to remember about the user.

Conversation:
{conversation_transcript}

Extract and return a JSON object with these fields (use null if not mentioned):
{{
    "family_members": [
        {{"name": "string", "relation": "string", "details": "string or null"}}
    ],
    "health_mentions": ["string"],
    "interests": ["string"],
    "important_stories": ["brief summary of any significant story or memory shared"],
    "topics_discussed": ["string"],
    "emotional_state": "happy/sad/lonely/anxious/neutral",
    "needs_followup": "anything that should be followed up on next conversation"
}}

Only include information that was explicitly mentioned. Return valid JSON only."""

        response = model.generate_content(prompt)
        
        # Parse the response
        import re
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            extracted = json.loads(json_match.group())
            
            # Update memory with extracted information
            for member in extracted.get("family_members", []):
                if member.get("name"):
                    user_memory.add_family_member(
                        member["name"],
                        member.get("relation", "family"),
                        member.get("details", "")
                    )
            
            for interest in extracted.get("interests", []):
                user_memory.add_interest(interest)
            
            for health in extracted.get("health_mentions", []):
                user_memory.add_health_note(health)
            
            for story in extracted.get("important_stories", []):
                user_memory.add_story(story)
            
            for topic in extracted.get("topics_discussed", []):
                user_memory.add_recent_topic(topic)
            
            return extracted
            
    except Exception as e:
        print(f"Error extracting memories: {e}")
    
    return {}


# Store active user memories
user_memories: dict[str, UserMemory] = {}


def get_or_create_user_memory(user_id: str, user_name: str) -> UserMemory:
    """Get or create a user's memory store."""
    if user_id not in user_memories:
        user_memories[user_id] = UserMemory(user_id, user_name)
    return user_memories[user_id]

