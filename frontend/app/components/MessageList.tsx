'use client'

import { useEffect, useRef } from 'react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  model?: string
  isStreaming?: boolean
  tokens?: number
  latency_ms?: number
  cost_usd?: number
}

interface MessageListProps {
  messages: Message[]
  providerStatus: Record<string, string>
}

const MODEL_COLORS: Record<string, string> = {
  gpt: 'border-l-4 border-black dark:border-white',
  claude: 'border-l-4 border-black dark:border-white',
  gemini: 'border-l-4 border-black dark:border-white',
  local: 'border-l-4 border-black dark:border-white',
}

const MODEL_NAMES: Record<string, string> = {
  gpt: 'GPT',
  claude: 'Claude',
  gemini: 'Gemini',
  local: 'Local',
}

export default function MessageList({ messages, providerStatus }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="space-y-4">
      {messages.map((message) => {
        if (message.role === 'user') {
          return (
            <div key={message.id} className="flex justify-start">
              <div className="border border-black dark:border-white rounded-lg px-4 py-2 max-w-2xl">
                <p className="text-black dark:text-white whitespace-pre-wrap">{message.content}</p>
              </div>
            </div>
          )
        }

        const model = message.model || 'unknown'
        const colorClass = MODEL_COLORS[model] || 'border-l-4 border-black dark:border-white'
        const modelName = MODEL_NAMES[model] || model

        return (
          <div key={message.id} className="flex justify-end">
            <div className={`border border-black dark:border-white rounded-lg px-4 py-2 max-w-2xl ${colorClass}`}>
              <div className="flex items-center gap-2 mb-1">
                <span className="font-semibold text-sm text-black dark:text-white">{modelName}</span>
                {message.isStreaming && (
                  <span className="text-xs text-black dark:text-white">...</span>
                )}
              </div>
              <p className="text-black dark:text-white whitespace-pre-wrap mb-2">
                {message.content}
              </p>
              {!message.isStreaming && (message.tokens || message.latency_ms || message.cost_usd) && (
                <div className="text-xs text-black dark:text-white mt-2 pt-2 border-t border-black dark:border-white">
                  {message.tokens && `${(message.tokens / 1000).toFixed(1)}k tokens`}
                  {message.latency_ms && ` • ${(message.latency_ms / 1000).toFixed(1)}s`}
                  {message.cost_usd && ` • $${message.cost_usd.toFixed(4)}`}
                </div>
              )}
            </div>
          </div>
        )
      })}
      <div ref={messagesEndRef} />
    </div>
  )
}
