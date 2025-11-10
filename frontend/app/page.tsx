'use client'

import { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import PasswordPrompt from './components/PasswordPrompt'
import ThemeToggle from './components/ThemeToggle'

export default function Home() {
  const [password, setPassword] = useState<string | null>(null)

  if (!password) {
    return (
      <main className="h-screen flex flex-col bg-white dark:bg-black">
        <ThemeToggle />
        <PasswordPrompt onAuthenticated={setPassword} />
      </main>
    )
  }

  return (
    <main className="h-screen flex flex-col bg-white dark:bg-black">
      <ThemeToggle />
      <div className="flex-1 overflow-y-auto">
        <ChatInterface password={password} />
      </div>
    </main>
  )
}

