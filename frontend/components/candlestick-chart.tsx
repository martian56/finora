"use client"

import { useEffect, useRef, useState } from "react"
import {
  createChart,
  IChartApi,
  ISeriesApi,
  CandlestickData,
  CandlestickSeries,
  ColorType,
  CrosshairMode,
} from "lightweight-charts"

interface CandlestickChartProps {
  symbol: string
  data?: CandlestickData[]
  height?: number
  theme?: "light" | "dark"
}

export function CandlestickChart({
  symbol,
  data = [],
  height = 400,
  theme = "dark",
}: CandlestickChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const candlestickSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null)
  // volumeSeriesRef removed - not using volume histogram currently
  const [isLoading, setIsLoading] = useState(true)
  const previousDataLengthRef = useRef(0)
  const previousSymbolRef = useRef(symbol)

  // Reset data length tracker when symbol changes
  useEffect(() => {
    if (previousSymbolRef.current !== symbol) {
      console.log(`Symbol changed from ${previousSymbolRef.current} to ${symbol}, resetting chart`)
      previousDataLengthRef.current = 0
      previousSymbolRef.current = symbol
    }
  }, [symbol])

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: height,
      layout: {
        background: { type: ColorType.Solid, color: theme === "dark" ? "#0a0a0a" : "#ffffff" },
        textColor: theme === "dark" ? "#9ca3af" : "#1f2937",
      },
      grid: {
        vertLines: {
          color: theme === "dark" ? "#1f2937" : "#e5e7eb",
          style: 1,
          visible: true,
        },
        horzLines: {
          color: theme === "dark" ? "#1f2937" : "#e5e7eb",
          style: 1,
          visible: true,
        },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: {
          width: 1,
          color: theme === "dark" ? "#4b5563" : "#9ca3af",
          style: 3,
          labelBackgroundColor: theme === "dark" ? "#374151" : "#6b7280",
        },
        horzLine: {
          width: 1,
          color: theme === "dark" ? "#4b5563" : "#9ca3af",
          style: 3,
          labelBackgroundColor: theme === "dark" ? "#374151" : "#6b7280",
        },
      },
      rightPriceScale: {
        borderColor: theme === "dark" ? "#1f2937" : "#d1d5db",
        visible: true,
      },
      timeScale: {
        borderColor: theme === "dark" ? "#1f2937" : "#d1d5db",
        timeVisible: true,
        secondsVisible: false,
      },
    })

    chartRef.current = chart

    // Add candlestick series (v5.0 API)
    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#22c55e",
      downColor: "#ef4444",
      borderVisible: false,
      wickUpColor: "#22c55e",
      wickDownColor: "#ef4444",
      priceFormat: {
        type: "price",
        precision: 2,
        minMove: 0.01,
      },
    })

    candlestickSeriesRef.current = candlestickSeries

    // Volume series removed - we don't have real volume data yet
    // Uncomment below when you have real volume data
    // const volumeSeries = chart.addSeries(HistogramSeries, {
    //   color: theme === "dark" ? "#374151" : "#d1d5db",
    //   priceFormat: {
    //     type: "volume",
    //   },
    //   priceScaleId: "",
    //   scaleMargins: {
    //     top: 0.9,  // Reduced to 10% of chart height
    //     bottom: 0,
    //   },
    // })
    // volumeSeriesRef.current = volumeSeries

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        })
      }
    }

    window.addEventListener("resize", handleResize)

    setIsLoading(false)

    // Cleanup
    return () => {
      window.removeEventListener("resize", handleResize)
      if (chartRef.current) {
        chartRef.current.remove()
        chartRef.current = null
      }
    }
  }, [height, theme])

  // Update data
  useEffect(() => {
    if (!candlestickSeriesRef.current || data.length === 0) return

    try {
      const isInitialLoad = previousDataLengthRef.current === 0
      const isIncrementalUpdate = data.length === previousDataLengthRef.current

      if (isInitialLoad) {
        // Initial load: set all data and fit content
        candlestickSeriesRef.current.setData(data)

        // Fit content only on initial load
        if (chartRef.current) {
          chartRef.current.timeScale().fitContent()
        }

        previousDataLengthRef.current = data.length
      } else if (isIncrementalUpdate && data.length > 0) {
        // Incremental update: update only the last candle (preserves zoom)
        const lastCandle = data[data.length - 1]
        candlestickSeriesRef.current.update(lastCandle)
      } else {
        // Data length changed (new candles added): set all data but don't reset zoom
        candlestickSeriesRef.current.setData(data)
        previousDataLengthRef.current = data.length
      }
    } catch (error) {
      console.error("Error updating chart data:", error)
    }
  }, [data])

  return (
    <div className="relative w-full">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-background/50 backdrop-blur-sm">
          <div className="flex items-center gap-2">
            <div className="h-6 w-6 animate-spin rounded-full border-4 border-primary border-t-transparent" />
            <span className="text-sm text-muted-foreground">Loading chart...</span>
          </div>
        </div>
      )}
      <div className="mb-2 flex items-center justify-between px-2">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-medium text-foreground">{symbol}</h3>
          <span className="text-xs text-muted-foreground">Candlestick Chart</span>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1">
            <div className="h-2 w-2 rounded-sm bg-[#22c55e]" />
            <span className="text-muted-foreground">Up</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="h-2 w-2 rounded-sm bg-[#ef4444]" />
            <span className="text-muted-foreground">Down</span>
          </div>
        </div>
      </div>
      <div ref={chartContainerRef} className="w-full" />
      {data.length === 0 && !isLoading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <p className="text-sm text-muted-foreground">No chart data available</p>
        </div>
      )}
    </div>
  )
}

