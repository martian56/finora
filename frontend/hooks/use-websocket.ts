import { useEffect, useRef, useState, useCallback } from 'react'

const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'

interface OrderBookLevel {
  price: number
  quantity: number
  total: number
  count?: number
}

interface OrderBookData {
  bids: OrderBookLevel[]
  asks: OrderBookLevel[]
  timestamp?: string
}

interface PriceData {
  price: number
  change_24h: number
  change_percent_24h: number
  volume_24h: number
  high_24h: number
  low_24h: number
  timestamp: string
}

export function useOrderBookWebSocket(tradingPair: string | null) {
  const [orderBook, setOrderBook] = useState<OrderBookData>({ bids: [], asks: [] })
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const currentPairRef = useRef<string | null>(null)
  const maxReconnectAttempts = 5

  useEffect(() => {
    // Clear old data when switching pairs
    if (currentPairRef.current !== tradingPair) {
      setOrderBook({ bids: [], asks: [] })
      setIsConnected(false)
      setError(null)
    }
    
    if (!tradingPair) {
      // Clean up if no trading pair
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
      currentPairRef.current = null
      return
    }

    // Store current pair
    currentPairRef.current = tradingPair
    
    // Clean up existing connection
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    
    // Reset reconnect attempts
    reconnectAttemptsRef.current = 0

    const connect = () => {
      // Don't connect if pair has changed
      if (currentPairRef.current !== tradingPair) return

      try {
        const url = `${WS_BASE_URL}/ws/orderbook/${tradingPair}/`
        console.log(`Connecting to order book WebSocket: ${url}`)
        
        const ws = new WebSocket(url)
        wsRef.current = ws

        ws.onopen = () => {
          // Only update state if we're still on the same pair
          if (currentPairRef.current === tradingPair) {
            console.log(`Order book WebSocket connected for ${tradingPair}`)
            setIsConnected(true)
            setError(null)
            reconnectAttemptsRef.current = 0
          } else {
            // Close if pair has changed
            ws.close()
          }
        }

        ws.onmessage = (event) => {
          // Only process messages if we're still on the same pair
          if (currentPairRef.current !== tradingPair) return

          try {
            const message = JSON.parse(event.data)
            
            if (message.type === 'orderbook_data' || message.type === 'orderbook_update') {
              setOrderBook(message.data)
            }
          } catch (err) {
            console.error('Error parsing WebSocket message:', err)
          }
        }

        ws.onerror = (event) => {
          if (currentPairRef.current === tradingPair) {
            console.error('Order book WebSocket error:', event)
            setError('WebSocket connection error')
          }
        }

        ws.onclose = (event) => {
          // Only handle close if we're still on the same pair
          if (currentPairRef.current !== tradingPair) return

          console.log(`Order book WebSocket closed for ${tradingPair}`, event.code, event.reason)
          setIsConnected(false)
          wsRef.current = null

          // Attempt to reconnect
          if (reconnectAttemptsRef.current < maxReconnectAttempts) {
            reconnectAttemptsRef.current += 1
            const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000)
            console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`)
            
            reconnectTimeoutRef.current = setTimeout(() => {
              connect()
            }, delay)
          } else {
            setError('Failed to connect after multiple attempts')
          }
        }
      } catch (err) {
        console.error('Error creating WebSocket:', err)
        setError('Failed to create WebSocket connection')
      }
    }

    connect()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [tradingPair])

  return { orderBook, isConnected, error }
}

export function usePriceWebSocket(tradingPair: string | null) {
  const [priceData, setPriceData] = useState<PriceData | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const currentPairRef = useRef<string | null>(null)
  const maxReconnectAttempts = 5

  useEffect(() => {
    // Clear old data when switching pairs
    if (currentPairRef.current !== tradingPair) {
      setPriceData(null)
      setIsConnected(false)
      setError(null)
    }
    
    if (!tradingPair) {
      // Clean up if no trading pair
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
      currentPairRef.current = null
      return
    }

    // Store current pair
    currentPairRef.current = tradingPair
    
    // Clean up existing connection
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    
    // Reset reconnect attempts
    reconnectAttemptsRef.current = 0

    const connect = () => {
      // Don't connect if pair has changed
      if (currentPairRef.current !== tradingPair) return

      try {
        const url = `${WS_BASE_URL}/ws/price/${tradingPair}/`
        console.log(`Connecting to price WebSocket: ${url}`)
        
        const ws = new WebSocket(url)
        wsRef.current = ws

        ws.onopen = () => {
          // Only update state if we're still on the same pair
          if (currentPairRef.current === tradingPair) {
            console.log(`Price WebSocket connected for ${tradingPair}`)
            setIsConnected(true)
            setError(null)
            reconnectAttemptsRef.current = 0
          } else {
            // Close if pair has changed
            ws.close()
          }
        }

        ws.onmessage = (event) => {
          // Only process messages if we're still on the same pair
          if (currentPairRef.current !== tradingPair) return

          try {
            const message = JSON.parse(event.data)
            
            if (message.type === 'price_data' || message.type === 'price_update') {
              setPriceData(message.data)
            }
          } catch (err) {
            console.error('Error parsing WebSocket message:', err)
          }
        }

        ws.onerror = (event) => {
          if (currentPairRef.current === tradingPair) {
            console.error('Price WebSocket error:', event)
            setError('WebSocket connection error')
          }
        }

        ws.onclose = (event) => {
          // Only handle close if we're still on the same pair
          if (currentPairRef.current !== tradingPair) return

          console.log(`Price WebSocket closed for ${tradingPair}`, event.code, event.reason)
          setIsConnected(false)
          wsRef.current = null

          // Attempt to reconnect
          if (reconnectAttemptsRef.current < maxReconnectAttempts) {
            reconnectAttemptsRef.current += 1
            const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000)
            console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`)
            
            reconnectTimeoutRef.current = setTimeout(() => {
              connect()
            }, delay)
          } else {
            setError('Failed to connect after multiple attempts')
          }
        }
      } catch (err) {
        console.error('Error creating WebSocket:', err)
        setError('Failed to create WebSocket connection')
      }
    }

    connect()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [tradingPair])

  return { priceData, isConnected, error }
}

export function useKlineWebSocket(tradingPair: string | null, interval: string = '15m') {
  const [klineData, setKlineData] = useState<any[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const currentPairRef = useRef<string | null>(null)
  const currentIntervalRef = useRef<string | null>(null)
  const maxReconnectAttempts = 5

  useEffect(() => {
    const pairIntervalKey = tradingPair ? `${tradingPair}:${interval}` : null
    const currentKey = currentPairRef.current && currentIntervalRef.current 
      ? `${currentPairRef.current}:${currentIntervalRef.current}` 
      : null

    // Clear old data when switching pairs or intervals
    if (currentKey !== pairIntervalKey) {
      setKlineData([])
      setIsConnected(false)
      setError(null)
    }
    
    if (!tradingPair) {
      // Clean up if no trading pair
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
      currentPairRef.current = null
      currentIntervalRef.current = null
      return
    }

    // Store current pair and interval
    currentPairRef.current = tradingPair
    currentIntervalRef.current = interval
    
    // Clean up existing connection
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    
    // Reset reconnect attempts
    reconnectAttemptsRef.current = 0

    const connect = () => {
      // Don't connect if pair or interval has changed
      if (currentPairRef.current !== tradingPair || currentIntervalRef.current !== interval) return

      try {
        const url = `${WS_BASE_URL}/ws/klines/${tradingPair}/${interval}/`
        console.log(`Connecting to klines WebSocket: ${url}`)
        
        const ws = new WebSocket(url)
        wsRef.current = ws

        ws.onopen = () => {
          // Only update state if we're still on the same pair and interval
          if (currentPairRef.current === tradingPair && currentIntervalRef.current === interval) {
            console.log(`Klines WebSocket connected for ${tradingPair} (${interval})`)
            setIsConnected(true)
            setError(null)
            reconnectAttemptsRef.current = 0
          } else {
            // Close if pair or interval has changed
            ws.close()
          }
        }

        ws.onmessage = (event) => {
          // Only process messages if we're still on the same pair and interval
          if (currentPairRef.current !== tradingPair || currentIntervalRef.current !== interval) return

          try {
            const message = JSON.parse(event.data)
            
            if (message.type === 'kline_data' || message.type === 'kline_update') {
              setKlineData(message.data)
            }
          } catch (err) {
            console.error('Error parsing WebSocket message:', err)
          }
        }

        ws.onerror = (event) => {
          if (currentPairRef.current === tradingPair && currentIntervalRef.current === interval) {
            console.error('Klines WebSocket error:', event)
            setError('WebSocket connection error')
          }
        }

        ws.onclose = (event) => {
          // Only handle close if we're still on the same pair and interval
          if (currentPairRef.current !== tradingPair || currentIntervalRef.current !== interval) return

          console.log(`Klines WebSocket closed for ${tradingPair}`, event.code, event.reason)
          setIsConnected(false)
          wsRef.current = null

          // Attempt to reconnect
          if (reconnectAttemptsRef.current < maxReconnectAttempts) {
            reconnectAttemptsRef.current += 1
            const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000)
            console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`)
            
            reconnectTimeoutRef.current = setTimeout(() => {
              connect()
            }, delay)
          } else {
            setError('Failed to connect after multiple attempts')
          }
        }
      } catch (err) {
        console.error('Error creating WebSocket:', err)
        setError('Failed to create WebSocket connection')
      }
    }

    connect()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [tradingPair, interval])

  return { klineData, isConnected, error }
}


