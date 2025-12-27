# 🧓 GrandPal - AI Companion for the Elderly

> *No one should feel alone. GrandPal is always there to listen.*

GrandPal is an AI-powered voice companion designed to combat loneliness among elderly individuals living alone. Through natural, empathetic conversation, GrandPal provides daily check-ins, remembers personal stories, and offers genuine emotional support.

## 🌟 Features

- **Natural Voice Conversations** - Powered by ElevenLabs for warm, human-like interactions
- **Conversational Memory** - Remembers names, stories, and preferences across sessions
- **Emotion-Aware Responses** - Detects mood and adjusts tone accordingly
- **Daily Check-Ins** - Proactively engages users, doesn't wait to be asked
- **Senior-Friendly Design** - Large buttons, simple interface, voice-first interaction

## 🛠️ Tech Stack

- **Frontend**: React + TypeScript + Vite
- **Voice AI**: ElevenLabs Conversational AI
- **AI Brain**: Google Gemini (via Vertex AI)
- **Backend**: Python FastAPI
- **Hosting**: Google Cloud Run
- **Database**: Firestore

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- ElevenLabs API Key
- Google Cloud Project with Gemini API enabled

### Setup

1. **Clone and install dependencies**

```bash
# Frontend
cd frontend
npm install

# Backend
cd ../backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment variables**

```bash
# In project root, create .env
ELEVENLABS_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

3. **Run the application**

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

4. **Open http://localhost:5173**

## 📁 Project Structure

```
grandpal/
├── frontend/           # React application
│   ├── src/
│   │   ├── components/ # UI components
│   │   ├── hooks/      # Custom React hooks
│   │   └── App.tsx     # Main application
│   └── package.json
├── backend/            # Python FastAPI server
│   ├── src/
│   │   ├── main.py     # API endpoints
│   │   ├── gemini.py   # Gemini integration
│   │   └── prompts/    # AI personality prompts
│   └── requirements.txt
└── README.md
```

## 🎯 For Hackathon Judges

This project was built for the **AI Partner Catalyst Hackathon** (ElevenLabs Challenge).

- **ElevenLabs Integration**: Conversational AI Agent with custom companion voice
- **Google Cloud Integration**: Gemini API for intelligent responses, Cloud Run for hosting
- **Impact**: Addressing the loneliness epidemic affecting 12M+ elderly Americans

## 📄 License

MIT License - See [LICENSE](LICENSE) file

## 👥 Team

Built with ❤️ for the AI Partner Catalyst Hackathon 2025

