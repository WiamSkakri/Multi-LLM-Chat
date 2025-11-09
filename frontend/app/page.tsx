'use client'

import ChatInterface from './components/ChatInterface'
import ThemeToggle from './components/ThemeToggle'

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-white dark:bg-black">
      <ThemeToggle />
      <div className="w-full max-w-4xl mx-auto px-6 flex flex-col items-center">
        <header className="mb-8 text-center">
          <h1 className="text-xl text-black dark:text-white mb-12">
            Ask multiple LLMs your question and compare
          </h1>
        </header>
        <ChatInterface />
      </div>
    </main>
  )
}

