'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import { useWebSocket } from '../hooks/useWebSocket'

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

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [threadId, setThreadId] = useState<string | null>(null)
  const [providerStatus, setProviderStatus] = useState<Record<string, string>>({})
  const { ws, connected, sendMessage, reconnect } = useWebSocket()

  // Fetch provider status on mount
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_HTTP_API_URL || 'http://localhost:8000'
        const response = await fetch(`${apiUrl}/api/providers/status`)
        const status = await response.json()
        setProviderStatus(status)
      } catch (error) {
        console.error('Failed to fetch provider status:', error)
      }
    }
    fetchStatus()
    const interval = setInterval(fetchStatus, 30000) // Poll every 30s
    return () => clearInterval(interval)
  }, [])

  // Handle WebSocket messages
  useEffect(() => {
    if (!ws) return

    const handleMessage = (event: MessageEvent) => {
      const data = JSON.parse(event.data)

      switch (data.type) {
        case 'authenticated':
          setThreadId(data.thread_id)
          break

        case 'response_start':
          setMessages(prev => [...prev, {
            id: data.message_id,
            role: 'assistant',
            content: '',
            model: data.model,
            isStreaming: true
          }])
          break

        case 'chunk':
          setMessages(prev => prev.map(msg =>
            msg.id === data.message_id
              ? { ...msg, content: msg.content + data.content }
              : msg
          ))
          break

        case 'response_complete':
          setMessages(prev => prev.map(msg =>
            msg.id === data.message_id
              ? {
                  ...msg,
                  isStreaming: false,
                  tokens: data.tokens,
                  latency_ms: data.latency_ms,
                  cost_usd: data.cost_usd
                }
              : msg
          ))
          break

        case 'error':
          alert(data.message)
          break
      }
    }

    ws.addEventListener('message', handleMessage)
    return () => ws.removeEventListener('message', handleMessage)
  }, [ws])

  const handleSend = useCallback((content: string) => {
    if (!ws || !connected) {
      alert('Not connected. Please reconnect.')
      return
    }

    // Add user message to UI immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content
    }
    setMessages(prev => [...prev, userMessage])

    // Send to server
    sendMessage({
      type: 'message',
      content,
      thread_id: threadId
    })
  }, [ws, connected, threadId, sendMessage])

  return (
    <div className="w-full flex flex-col">
      {messages.length > 0 && (
        <div className="mb-8 max-h-96 overflow-y-auto">
          <MessageList messages={messages} providerStatus={providerStatus} />
        </div>
      )}
      <MessageInput onSend={handleSend} providerStatus={providerStatus} />
      {!connected && (
        <div className="flex items-center justify-center gap-2 mt-3 text-xs">
          <div className="w-2 h-2 rounded-full bg-red-500" />
          <span className="text-black dark:text-white">Disconnected</span>
          <button
            onClick={reconnect}
            className="text-black dark:text-white underline hover:no-underline"
          >
            Reconnect
          </button>
        </div>
      )}
    </div>
  )
}

