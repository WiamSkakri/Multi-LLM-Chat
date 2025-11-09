'use client'

import { useState, useRef, useEffect, KeyboardEvent } from 'react'

interface MessageInputProps {
  onSend: (content: string) => void
  providerStatus: Record<string, string>
}

const MENTIONS = ['gpt', 'claude', 'gemini', 'local']

export default function MessageInput({ onSend, providerStatus }: MessageInputProps) {
  const [input, setInput] = useState('')
  const [showMentions, setShowMentions] = useState(false)
  const [mentionIndex, setMentionIndex] = useState(-1)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value
    setInput(value)

    // Check for @ mention
    const cursorPos = e.target.selectionStart
    const textBeforeCursor = value.substring(0, cursorPos)
    const lastAtIndex = textBeforeCursor.lastIndexOf('@')

    if (lastAtIndex !== -1) {
      const textAfterAt = textBeforeCursor.substring(lastAtIndex + 1)
      if (!textAfterAt.includes(' ') && !textAfterAt.includes('\n')) {
        setShowMentions(true)
        return
      }
    }
    setShowMentions(false)
  }

  const insertMention = (mention: string) => {
    const cursorPos = inputRef.current?.selectionStart || 0
    const textBeforeCursor = input.substring(0, cursorPos)
    const textAfterCursor = input.substring(cursorPos)
    const lastAtIndex = textBeforeCursor.lastIndexOf('@')
    
    if (lastAtIndex !== -1) {
      const newInput = 
        input.substring(0, lastAtIndex) + 
        `@${mention} ` + 
        textAfterCursor
      setInput(newInput)
      setShowMentions(false)
      setTimeout(() => {
        inputRef.current?.focus()
        const newPos = lastAtIndex + mention.length + 2
        inputRef.current?.setSelectionRange(newPos, newPos)
      }, 0)
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (showMentions) {
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setMentionIndex(prev => (prev + 1) % MENTIONS.length)
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setMentionIndex(prev => (prev - 1 + MENTIONS.length) % MENTIONS.length)
      } else if (e.key === 'Enter' && mentionIndex >= 0) {
        e.preventDefault()
        insertMention(MENTIONS[mentionIndex])
      } else if (e.key === 'Escape') {
        setShowMentions(false)
      }
      return
    }

    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault()
      handleSend()
    }
  }

  const handleSend = () => {
    if (input.trim()) {
      onSend(input.trim())
      setInput('')
      setShowMentions(false)
    }
  }

  return (
    <div className="relative w-full">
      <div className="relative">
        <textarea
          ref={inputRef}
          value={input}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Type @ to mention a model (e.g., @gpt What is LoRA?)"
          className="w-full px-4 py-3 pr-12 border border-black dark:border-white bg-white dark:bg-black text-black dark:text-white rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white placeholder-gray-500 dark:placeholder-gray-400"
          rows={1}
          style={{ minHeight: '52px', maxHeight: '200px' }}
          onInput={(e) => {
            const target = e.target as HTMLTextAreaElement
            target.style.height = 'auto'
            target.style.height = `${Math.min(target.scrollHeight, 200)}px`
          }}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim()}
          className="absolute right-3 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center bg-black dark:bg-white text-white dark:text-black rounded-full hover:bg-gray-800 dark:hover:bg-gray-200 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          aria-label="Send message"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            className="w-4 h-4"
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M12 19V5M5 12l7-7 7 7" />
          </svg>
        </button>
        {showMentions && (
          <div className="absolute bottom-full mb-2 left-0 bg-white dark:bg-black border border-black dark:border-white rounded-lg shadow-lg z-10 min-w-[200px]">
            {MENTIONS.map((mention, idx) => {
              const status = providerStatus[mention] || 'unknown'
              const isAvailable = status === 'available'
              return (
                <button
                  key={mention}
                  onClick={() => insertMention(mention)}
                  className={`w-full text-left px-4 py-2 text-black dark:text-white hover:bg-gray-200 dark:hover:bg-gray-800 flex items-center gap-2 ${
                    idx === mentionIndex ? 'bg-gray-200 dark:bg-gray-800' : ''
                  } ${!isAvailable ? 'opacity-50' : ''}`}
                >
                  <span className={`w-2 h-2 rounded-full ${isAvailable ? 'bg-green-500' : 'bg-red-500'}`} />
                  <span>@{mention}</span>
                  {!isAvailable && <span className="text-xs text-gray-500 dark:text-gray-400">(unavailable)</span>}
                </button>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

