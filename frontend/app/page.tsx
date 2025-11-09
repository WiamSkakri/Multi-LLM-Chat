'use client'

import ChatInterface from './components/ChatInterface'
import ThemeToggle from './components/ThemeToggle'

export default function Home() {
  return (
    <main className="h-screen flex flex-col bg-white dark:bg-black">
      <ThemeToggle />
      <div className="flex-1 overflow-y-auto">
        <ChatInterface />
      </div>
    </main>
  )
}

