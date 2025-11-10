'use client'

import { useState } from 'react'

interface PasswordPromptProps {
  onAuthenticated: (password: string) => void
}

export default function PasswordPrompt({ onAuthenticated }: PasswordPromptProps) {
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (password.length < 3) {
      setError('Password is required')
      return
    }
    setError('')
    onAuthenticated(password)
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-white dark:bg-black">
      <div className="w-full max-w-md p-8 bg-gray-50 dark:bg-gray-900 rounded-lg shadow-lg border border-gray-200 dark:border-gray-800">
        <h1 className="text-3xl font-bold mb-2 text-center text-black dark:text-white">
          Multi-LLM Chat
        </h1>
        <p className="text-sm text-gray-600 dark:text-gray-400 text-center mb-6">
          Enter password to access
        </p>
        <form onSubmit={handleSubmit}>
          <label className="block mb-4">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Password
            </span>
            <input
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value)
                setError('')
              }}
              className="mt-1 block w-full px-4 py-3 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800 text-black dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter password"
              autoFocus
            />
          </label>
          {error && (
            <p className="text-red-500 text-sm mb-4">{error}</p>
          )}
          <button
            type="submit"
            className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md transition-colors duration-200"
          >
            Access Chat
          </button>
        </form>
      </div>
    </div>
  )
}
