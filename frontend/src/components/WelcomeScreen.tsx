import { useState } from 'react'

interface WelcomeScreenProps {
  onStart: (name: string) => void
}

export function WelcomeScreen({ onStart }: WelcomeScreenProps) {
  const [name, setName] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (name.trim()) {
      onStart(name.trim())
    }
  }

  return (
    <div className="welcome-screen">
      {/* Floating decorative elements */}
      <div className="floating-elements">
        <div className="floating-circle circle-1"></div>
        <div className="floating-circle circle-2"></div>
        <div className="floating-circle circle-3"></div>
      </div>

      <div className="welcome-content">
        {/* Warm lamp illustration */}
        <div className="lamp-container">
          <div className="lamp-glow"></div>
          <div className="lamp-icon">🪔</div>
        </div>

        <h1 className="welcome-title">
          <span className="title-hello">Hello,</span>
          <span className="title-friend">friend</span>
        </h1>
        
        <p className="welcome-subtitle">
          I'm GrandPal, your companion for<br />
          <em>meaningful conversations</em>
        </p>

        <form onSubmit={handleSubmit} className="name-form">
          <div className="input-wrapper">
            <label htmlFor="name" className="name-label">
              What's your name?
            </label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Type your name..."
              className="name-input"
              autoFocus
              autoComplete="off"
            />
          </div>
          
          <button 
            type="submit" 
            className="start-button"
            disabled={!name.trim()}
          >
            <span>Let's Talk</span>
            <svg className="button-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </button>
        </form>

        <div className="trust-badges">
          <div className="badge">
            <span className="badge-icon">🔒</span>
            <span>Private & Secure</span>
          </div>
          <div className="badge">
            <span className="badge-icon">💚</span>
            <span>Always Here</span>
          </div>
          <div className="badge">
            <span className="badge-icon">🧠</span>
            <span>Remembers You</span>
          </div>
        </div>
      </div>

      <footer className="welcome-footer">
        <p>Powered by ElevenLabs & Google Gemini</p>
      </footer>
    </div>
  )
}
