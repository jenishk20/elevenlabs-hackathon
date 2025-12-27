import { useState } from 'react'
import { ConversationView } from './components/ConversationView'
import { WelcomeScreen } from './components/WelcomeScreen'

function App() {
  const [started, setStarted] = useState(false)
  const [userName, setUserName] = useState('')

  const handleStart = (name: string) => {
    setUserName(name)
    setStarted(true)
  }

  return (
    <div className="app">
      {!started ? (
        <WelcomeScreen onStart={handleStart} />
      ) : (
        <ConversationView userName={userName} onEnd={() => setStarted(false)} />
      )}
    </div>
  )
}

export default App

