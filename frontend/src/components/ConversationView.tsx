import { useCallback, useState, useEffect, useRef } from 'react'
import { useConversation } from '@elevenlabs/react'
import { getApiUrl } from '../config'

interface ConversationViewProps {
  userName: string
  onEnd: () => void
}

export function ConversationView({ userName, onEnd }: ConversationViewProps) {
  const [statusMessage, setStatusMessage] = useState('Ready when you are')
  const [transcript, setTranscript] = useState<Array<{ role: string; text: string }>>([])
  const transcriptRef = useRef<HTMLDivElement>(null)

  const conversation = useConversation({
    onConnect: () => {
      console.log('Connected to ElevenLabs')
      setStatusMessage('I\'m listening...')
    },
    onDisconnect: () => {
      console.log('Disconnected from ElevenLabs')
      setStatusMessage('Until next time!')
    },
    onMessage: (message) => {
      console.log('Message received:', message)
      if (message.message) {
        const role = message.source === 'ai' ? 'grandpal' : 'user'
        setTranscript(prev => [...prev, { role, text: message.message }])
      }
    },
    onModeChange: (mode) => {
      console.log('Mode changed:', mode)
      if (mode.mode === 'speaking') {
        setStatusMessage('Speaking...')
      } else {
        setStatusMessage('I\'m listening...')
      }
    },
    onError: (error) => {
      console.error('Conversation error:', error)
      setStatusMessage('Let me try that again...')
    },
  })

  // Auto-scroll transcript
  useEffect(() => {
    if (transcriptRef.current) {
      transcriptRef.current.scrollTop = transcriptRef.current.scrollHeight
    }
  }, [transcript])

  const handleStartConversation = useCallback(async () => {
    try {
      setStatusMessage('Connecting...')
      
      await navigator.mediaDevices.getUserMedia({ audio: true })
      
      // Use the API URL helper for production compatibility
      const response = await fetch(getApiUrl('/api/conversation/start'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userName }),
      })
      
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to start conversation')
      }
      
      const { signedUrl, agentId } = await response.json()
      
      if (signedUrl) {
        await conversation.startSession({ signedUrl })
      } else if (agentId) {
        await conversation.startSession({ agentId })
      } else {
        throw new Error('No agent configured')
      }
      
    } catch (error) {
      console.error('Failed to start:', error)
      if (error instanceof Error) {
        setStatusMessage(error.message)
      } else {
        setStatusMessage('Please check your microphone')
      }
    }
  }, [conversation, userName])

  const handleEndConversation = useCallback(async () => {
    await conversation.endSession()
    setStatusMessage('Take care! Come back anytime.')
  }, [conversation])

  const isConnected = conversation.status === 'connected'
  const isSpeaking = conversation.isSpeaking

  return (
    <div className="conversation-view">
      {/* Ambient background */}
      <div className="ambient-bg">
        <div className="ambient-circle ambient-1"></div>
        <div className="ambient-circle ambient-2"></div>
      </div>

      {/* Minimal header */}
      <header className="conversation-header">
        <button className="back-button" onClick={onEnd} aria-label="Go back">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
        </button>
        <div className="header-center">
          <span className="header-name">GrandPal</span>
          <span className={`header-status ${isConnected ? 'online' : ''}`}>
            {isConnected ? '● Connected' : '○ Offline'}
          </span>
        </div>
        <div className="header-spacer"></div>
      </header>

      <main className="conversation-main">
        {/* Central avatar area */}
        <div className="avatar-section">
          <div className={`avatar-ring ${isConnected ? 'active' : ''} ${isSpeaking ? 'speaking' : ''}`}>
            <div className="avatar-inner">
              <div className="avatar-face">
                {isSpeaking ? '😊' : isConnected ? '🙂' : '😌'}
              </div>
            </div>
            {/* Sound waves when speaking */}
            {isSpeaking && (
              <div className="sound-waves">
                <span></span>
                <span></span>
                <span></span>
                <span></span>
              </div>
            )}
          </div>
          
          <h2 className="greeting">
            {!isConnected ? `Hi, ${userName}` : statusMessage}
          </h2>
          
          {!isConnected && (
            <p className="greeting-sub">Ready to chat whenever you are</p>
          )}
        </div>

        {/* Conversation transcript */}
        {transcript.length > 0 && (
          <div className="transcript-container" ref={transcriptRef}>
            {transcript.map((msg, idx) => (
              <div 
                key={idx} 
                className={`message ${msg.role}`}
              >
                <div className="message-bubble">
                  {msg.text}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Action footer */}
      <footer className="conversation-footer">
        {!isConnected ? (
          <button 
            className="action-button primary"
            onClick={handleStartConversation}
          >
            <div className="button-icon-wrapper">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
              </svg>
            </div>
            <span>Start Talking</span>
          </button>
        ) : (
          <div className="connected-actions">
            <div className="listening-badge">
              <div className="pulse-dot"></div>
              <span>{isSpeaking ? 'GrandPal is speaking' : 'Listening to you'}</span>
            </div>
            <button 
              className="action-button secondary"
              onClick={handleEndConversation}
            >
              End Chat
            </button>
          </div>
        )}
      </footer>
    </div>
  )
}
