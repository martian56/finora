import { useState, useEffect, useCallback, useRef } from "react"
import { CandlestickData, Time } from "lightweight-charts"
import { useKlineWebSocket } from "./use-websocket"

interface UseCandlestickDataOptions {
  symbol: string | null
  interval?: string // '1m', '5m', '15m', '1h', '4h', '1d'
  limit?: number
}

export function useCandlestickData({
  symbol,
  interval = "15m",
  limit = 100,
}: UseCandlestickDataOptions) {
  const [data, setData] = useState<CandlestickData[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const initializedRef = useRef(false)

  // Connect to WebSocket for real-time updates
  const { klineData, isConnected } = useKlineWebSocket(symbol, interval)

  // Initialize with mock data (reset when symbol changes)
  useEffect(() => {
    if (!symbol) return

    console.log(`Initializing candlestick data for ${symbol}`)
    const mockData = generateMockCandlestickData(limit, symbol)
    setData(mockData)
    setIsLoading(false)
    initializedRef.current = true
  }, [symbol, limit]) // Will re-run when symbol changes

  // Update when WebSocket data arrives
  useEffect(() => {
    if (!klineData || klineData.length === 0) return

    try {
      console.log(`Received kline data:`, klineData.length, 'candles')
      
      // Transform WebSocket data to candlestick format
      const candlestickData: CandlestickData[] = klineData.map((item: any) => ({
        time: (typeof item.time === 'number' ? item.time : new Date(item.time || item.timestamp).getTime() / 1000) as Time,
        open: parseFloat(item.open),
        high: parseFloat(item.high),
        low: parseFloat(item.low),
        close: parseFloat(item.close),
      }))

      setData(candlestickData)
      setError(null)
    } catch (err) {
      console.error("Error processing kline data:", err)
      setError("Failed to process chart data")
    }
  }, [klineData])

  // Simulate real-time price updates on the mock data
  useEffect(() => {
    if (!symbol || klineData.length > 0 || data.length === 0) return

    const updateInterval = setInterval(() => {
      setData(prevData => {
        if (prevData.length === 0) return prevData

        const lastCandle = prevData[prevData.length - 1]

        // Update last candle with slight price movement
        const priceChange = (Math.random() - 0.5) * 20 // ±10
        const newClose = lastCandle.close + priceChange
        const newHigh = Math.max(lastCandle.high, newClose, lastCandle.open)
        const newLow = Math.min(lastCandle.low, newClose, lastCandle.open)

        const updatedCandle: CandlestickData = {
          time: lastCandle.time,
          open: lastCandle.open,
          high: newHigh,
          low: newLow,
          close: newClose,
        }

        // Return a new array with updated last candle
        // This creates a shallow copy which React detects as a change
        const newData = [...prevData]
        newData[newData.length - 1] = updatedCandle
        return newData
      })
    }, 2000) // Update every 2 seconds

    return () => clearInterval(updateInterval)
  }, [symbol, klineData.length, data.length])

  return {
    data,
    isLoading,
    error,
    isConnected,
    refetch: () => {
      initializedRef.current = false
      const mockData = generateMockCandlestickData(limit, symbol || 'BTC/USDT')
      setData(mockData)
    },
  }
}

// Helper function to determine refresh interval
function getRefreshInterval(interval: string): number {
  const intervalMap: Record<string, number> = {
    "1m": 60 * 1000, // 1 minute
    "5m": 5 * 60 * 1000, // 5 minutes
    "15m": 15 * 60 * 1000, // 15 minutes
    "1h": 60 * 60 * 1000, // 1 hour
    "4h": 4 * 60 * 60 * 1000, // 4 hours
    "1d": 24 * 60 * 60 * 1000, // 1 day
  }
  return intervalMap[interval] || 60 * 1000 // Default to 1 minute
}

// Generate mock candlestick data for development/testing
function generateMockCandlestickData(count: number, symbol: string): CandlestickData[] {
  const data: CandlestickData[] = []
  const now = Math.floor(Date.now() / 1000)
  const intervalSeconds = 15 * 60 // 15 minutes

  // Set realistic base prices based on symbol
  let currentPrice = 50000
  if (symbol.includes('BTC')) {
    currentPrice = 50000 + Math.random() * 1000
  } else if (symbol.includes('ETH')) {
    currentPrice = 3000 + Math.random() * 100
  } else if (symbol.includes('SOL')) {
    currentPrice = 100 + Math.random() * 10
  } else {
    currentPrice = 1 + Math.random() * 0.1
  }

  for (let i = count - 1; i >= 0; i--) {
    const time = (now - i * intervalSeconds) as Time

    // Generate realistic OHLC data
    const open = currentPrice
    const volatility = currentPrice * 0.002 // 0.2% volatility
    const change = (Math.random() - 0.5) * volatility * 2
    const close = open + change
    const high = Math.max(open, close) + Math.random() * volatility
    const low = Math.min(open, close) - Math.random() * volatility

    data.push({
      time,
      open: parseFloat(open.toFixed(2)),
      high: parseFloat(high.toFixed(2)),
      low: parseFloat(low.toFixed(2)),
      close: parseFloat(close.toFixed(2)),
    })

    currentPrice = close // Next candle starts at previous close
  }

  return data
}

