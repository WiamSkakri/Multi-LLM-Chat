'use client'

import { useState, useEffect, useRef, useCallback } from 'react'

interface WebSocketMessage {
  type: string
  [key: string]: any
}

export function useWebSocket() {
  const [ws, setWs] = useState<WebSocket | null>(null)
  const [connected, setConnected] = useState(false)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 3
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()

  const connect = useCallback(() => {
    const wsUrl = process.env.NEXT_PUBLIC_API_URL || 'ws://localhost:8000/ws'
    const password = process.env.NEXT_PUBLIC_APP_PASSWORD || ''

    const websocket = new WebSocket(wsUrl)

    websocket.onopen = () => {
      console.log('WebSocket connected')
      setConnected(true)
      reconnectAttempts.current = 0
      
      // Send auth
      websocket.send(JSON.stringify({
        type: 'auth',
        password
      }))
    }

    websocket.onclose = () => {
      console.log('WebSocket disconnected')
      setConnected(false)
      
      // Attempt reconnection with exponential backoff
      if (reconnectAttempts.current < maxReconnectAttempts) {
        reconnectAttempts.current += 1
        const delay = Math.pow(2, reconnectAttempts.current - 1) * 1000 // 1s, 2s, 4s
        
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log(`Reconnecting (attempt ${reconnectAttempts.current})...`)
          connect()
        }, delay)
      } else {
        console.log('Max reconnection attempts reached')
      }
    }

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    setWs(websocket)
  }, [])

  useEffect(() => {
    connect()
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (ws) {
        ws.close()
      }
    }
  }, [])

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message))
    } else {
      console.error('WebSocket not connected')
    }
  }, [ws])

  const reconnect = useCallback(() => {
    reconnectAttempts.current = 0
    if (ws) {
      ws.close()
    }
    connect()
  }, [ws, connect])

  return { ws, connected, sendMessage, reconnect }
}

