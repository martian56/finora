"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { TrendingUp, TrendingDown } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { useTradingPairs, useOrders, useWallets } from "@/hooks/use-trading"
import { useOrderBookWebSocket, usePriceWebSocket } from "@/hooks/use-websocket"
import { useCandlestickData } from "@/hooks/use-candlestick-data"
import { CandlestickChart } from "@/components/candlestick-chart"
import { apiClient } from "@/lib/api-client"

export default function SpotTradingPage() {
  const router = useRouter()
  const { user, isLoading } = useAuth()
  const { toast } = useToast()
  const { pairs, isLoading: pairsLoading } = useTradingPairs()
  const { orders, placeOrder, cancelOrder } = useOrders()
  const { wallets } = useWallets()
  
  const [selectedPair, setSelectedPair] = useState<any>(null)
  const [marketData, setMarketData] = useState<any>(null)
  const [orderType, setOrderType] = useState<"limit" | "market">("limit")
  const [buyAmount, setBuyAmount] = useState("")
  const [buyPrice, setBuyPrice] = useState("")
  const [sellAmount, setSellAmount] = useState("")
  const [sellPrice, setSellPrice] = useState("")

  // WebSocket connections for real-time data
  // These will automatically disconnect/reconnect when selectedPair.symbol changes
  const { orderBook, isConnected: orderBookConnected } = useOrderBookWebSocket(selectedPair?.symbol || null)
  const { priceData, isConnected: priceConnected } = usePriceWebSocket(selectedPair?.symbol || null)
  
  // Candlestick chart data
  // This will regenerate mock data when symbol changes
  const { data: candlestickData, isLoading: chartLoading } = useCandlestickData({
    symbol: selectedPair?.symbol || null,
    interval: "15m",
    limit: 100,
  })

  // Set default pair when pairs are loaded
  useEffect(() => {
    if (pairs.length > 0 && !selectedPair) {
      const pair = pairs[0]
      // Add price and change fields for display (symbol comes from API)
      setSelectedPair({
        ...pair,
        price: pair.price || 0,
        change: pair.change || 0,
      })
    }
  }, [pairs, selectedPair])

  // Fetch initial market data for selected pair (fallback if WebSocket is not connected)
  useEffect(() => {
    if (selectedPair?.symbol && !priceData) {
      const fetchMarketData = async () => {
        try {
          const data = await apiClient.getMarketData(selectedPair.symbol)
          setMarketData(data)
          // Update the selected pair with market data
          setSelectedPair(prev => ({
            ...prev,
            price: data.price,
            change: data.change_24h,
          }))
        } catch (error) {
          console.error("Failed to fetch market data:", error)
          // Set empty market data - will show zeros until trading starts
          setMarketData(null)
          setSelectedPair(prev => ({
            ...prev,
            price: 0,
            change: 0,
          }))
        }
      }
      fetchMarketData()
    }
  }, [selectedPair?.symbol, priceData])

  // Update market data when WebSocket price updates arrive
  useEffect(() => {
    if (priceData) {
      setMarketData(priceData)
      setSelectedPair(prev => ({
        ...prev,
        price: priceData.price,
        change: priceData.change_24h,
      }))
    }
  }, [priceData])

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login")
    }
  }, [user, isLoading, router])

  if (isLoading || pairsLoading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <span className="text-lg text-muted-foreground">Loading...</span>
        </div>
      </div>
    )
  }

  // Show message if no trading pairs available
  if (!selectedPair || pairs.length === 0) {
    return (
      <DashboardLayout>
        <div className="flex min-h-screen items-center justify-center">
          <div className="text-center">
            <p className="text-lg text-muted-foreground">No trading pairs available</p>
            <p className="text-sm text-muted-foreground mt-2">Please contact support</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  // Calculate total balance from wallets
  const totalBalance = Array.isArray(wallets) 
    ? wallets.reduce((sum, wallet) => sum + (Number(wallet.balance) || 0), 0) 
    : 0

  const handleBuy = async () => {
    if (!selectedPair || !buyAmount || (orderType === "limit" && !buyPrice)) {
      toast({
        title: "Invalid Order",
        description: "Please fill in all required fields",
        variant: "destructive",
      })
      return
    }

    try {
      await placeOrder({
        trading_pair: selectedPair.id,
        order_type: orderType,
        side: "buy",
        quantity: parseFloat(buyAmount),
        price: orderType === "limit" ? parseFloat(buyPrice) : undefined,
      })

      setBuyAmount("")
      setBuyPrice("")
    } catch (error) {
      // Error is already handled in the hook
    }
  }

  const handleSell = async () => {
    if (!selectedPair || !sellAmount || (orderType === "limit" && !sellPrice)) {
      toast({
        title: "Invalid Order",
        description: "Please fill in all required fields",
        variant: "destructive",
      })
      return
    }

    try {
      await placeOrder({
        trading_pair: selectedPair.id,
        order_type: orderType,
        side: "sell",
        quantity: parseFloat(sellAmount),
        price: orderType === "limit" ? parseFloat(sellPrice) : undefined,
      })

      setSellAmount("")
      setSellPrice("")
    } catch (error) {
      // Error is already handled in the hook
    }
  }

  return (
    <DashboardLayout>
      <div className="h-[calc(100vh-4rem)] p-4">
        <div className="grid h-full gap-3 lg:grid-cols-12">
          {/* Left sidebar - Trading pairs */}
          <div className="lg:col-span-2 flex flex-col overflow-hidden">
            <Card className="border-border/50 flex flex-col h-full">
              <CardHeader className="py-3 px-4">
                <CardTitle className="text-sm">Markets</CardTitle>
              </CardHeader>
              <CardContent className="p-0 flex-1 overflow-y-auto">
                <div className="space-y-0.5">
                  {pairsLoading ? (
                    <div className="flex h-32 items-center justify-center">
                      <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                    </div>
                  ) : pairs.length === 0 ? (
                    <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
                      No trading pairs available
                    </div>
                  ) : (
                    pairs.map((pair) => {
                      // Show real-time data only for selected pair
                      const isSelected = selectedPair?.id === pair.id
                      const displayPrice = isSelected && marketData?.price 
                        ? marketData.price.toFixed(2) 
                        : "Select"
                      const displayChange = isSelected && marketData?.change_24h 
                        ? marketData.change_24h.toFixed(2) 
                        : "--"
                      
                      return (
                        <button
                          key={pair.id}
                          onClick={() => setSelectedPair(pair)}
                          className={`flex w-full items-center justify-between px-3 py-2 text-left transition-colors hover:bg-muted ${
                            isSelected ? "bg-muted" : ""
                          }`}
                        >
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">
                              {pair.base_currency.symbol}/{pair.quote_currency.symbol}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {displayPrice}
                            </p>
                          </div>
                          <div className={`text-xs font-medium ${
                            isSelected && marketData?.change_24h >= 0 ? "text-primary" : isSelected ? "text-destructive" : "text-muted-foreground"
                          }`}>
                            {isSelected && marketData?.change_24h >= 0 ? "+" : ""}
                            {displayChange}%
                          </div>
                        </button>
                      )
                    })
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Center - Chart and Order Book */}
          <div className="flex flex-col gap-3 lg:col-span-7">
            {/* Price header - Compact */}
            <Card className="border-border/50">
              <CardContent className="p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="text-2xl font-bold">${marketData?.price?.toFixed(2) || "0.00"}</p>
                        <div
                          className={`flex items-center gap-1 text-sm font-medium ${
                            (marketData?.change_24h || 0) >= 0 ? "text-primary" : "text-destructive"
                          }`}
                        >
                          {(marketData?.change_24h || 0) >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                          {(marketData?.change_24h || 0) >= 0 ? "+" : ""}
                          {(marketData?.change_24h || 0).toFixed(2)}%
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground">{selectedPair?.symbol || 'N/A'} Spot</p>
                    </div>
                    <div className="border-l border-border pl-4">
                      <p className="text-xs text-muted-foreground">24h Volume</p>
                      <p className="text-sm font-semibold">{marketData?.volume_24h?.toFixed(2) || "0.00"}</p>
                    </div>
                    <div className="border-l border-border pl-4">
                      <p className="text-xs text-muted-foreground">24h High</p>
                      <p className="text-sm font-semibold">${marketData?.high_24h?.toFixed(2) || "0.00"}</p>
                    </div>
                    <div className="border-l border-border pl-4">
                      <p className="text-xs text-muted-foreground">24h Low</p>
                      <p className="text-sm font-semibold">${marketData?.low_24h?.toFixed(2) || "0.00"}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Candlestick Chart - Large */}
            <Card className="flex-1 border-border/50 overflow-hidden">
              <CardContent className="p-2 h-full">
                <CandlestickChart
                  symbol={selectedPair?.symbol || ""}
                  data={candlestickData}
                  height={600}
                  theme="dark"
                />
              </CardContent>
            </Card>

            {/* Order Book - Below Chart */}
            <Card className="border-border/50">
              <CardHeader className="py-2 px-4">
                <CardTitle className="text-sm">Order Book</CardTitle>
              </CardHeader>
              <CardContent className="p-4 pt-0">
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-2 text-xs font-medium text-muted-foreground">
                    <div>Price (USDT)</div>
                    <div className="text-right">Amount (BTC)</div>
                    <div className="text-right">Total</div>
                  </div>
                  {/* Asks (Sell orders) */}
                  <div className="space-y-0.5">
                    {orderBook.asks.length > 0 ? (
                      orderBook.asks.slice(0, 8).map((ask, i) => (
                        <div key={i} className="grid grid-cols-3 gap-2 text-sm">
                          <div className="font-medium text-destructive">{Number(ask.price).toFixed(2)}</div>
                          <div className="text-right">{Number(ask.quantity || ask.amount || 0).toFixed(4)}</div>
                          <div className="text-right text-muted-foreground">{Number(ask.total || (ask.price * (ask.quantity || ask.amount || 0))).toFixed(2)}</div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center text-sm text-muted-foreground py-2">
                        {orderBookConnected ? 'Waiting for data...' : 'Connecting...'}
                      </div>
                    )}
                  </div>
                  {/* Current price */}
                  <div className="border-y border-border/50 py-2 text-center font-bold">
                    {selectedPair?.price?.toFixed(2) || '0.00'}
                    {priceConnected && <span className="ml-2 text-xs text-green-500">●</span>}
                  </div>
                  {/* Bids (Buy orders) */}
                  <div className="space-y-0.5">
                    {orderBook.bids.length > 0 ? (
                      orderBook.bids.slice(0, 8).map((bid, i) => (
                        <div key={i} className="grid grid-cols-3 gap-2 text-sm">
                          <div className="font-medium text-primary">{Number(bid.price).toFixed(2)}</div>
                          <div className="text-right">{Number(bid.quantity || bid.amount || 0).toFixed(4)}</div>
                          <div className="text-right text-muted-foreground">{Number(bid.total || (bid.price * (bid.quantity || bid.amount || 0))).toFixed(2)}</div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center text-sm text-muted-foreground py-2">
                        {orderBookConnected ? 'Waiting for data...' : 'Connecting...'}
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right sidebar - Trading panel */}
          <div className="lg:col-span-3 flex flex-col gap-3 overflow-hidden">
            <Card className="border-border/50 flex-1 flex flex-col">
              <CardHeader className="py-3 px-4">
                <CardTitle className="text-sm">Trade</CardTitle>
              </CardHeader>
              <CardContent className="flex-1 overflow-y-auto px-4">
                <Tabs defaultValue="buy" className="w-full">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="buy" className="text-xs">Buy</TabsTrigger>
                    <TabsTrigger value="sell" className="text-xs">Sell</TabsTrigger>
                  </TabsList>

                  <div className="mb-3 mt-3">
                    <Label className="text-xs text-muted-foreground">Order Type</Label>
                    <Select value={orderType} onValueChange={(v) => setOrderType(v as "limit" | "market")}>
                      <SelectTrigger className="mt-1 h-8 text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="limit">Limit</SelectItem>
                        <SelectItem value="market">Market</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <TabsContent value="buy" className="space-y-3 mt-0">
                    {orderType === "limit" && (
                      <div>
                        <Label className="text-xs text-muted-foreground">Price (USDT)</Label>
                        <Input
                          type="number"
                          placeholder="0.00"
                          value={buyPrice}
                          onChange={(e) => setBuyPrice(e.target.value)}
                          className="mt-1"
                        />
                      </div>
                    )}
                    <div>
                      <Label className="text-xs text-muted-foreground">Amount (BTC)</Label>
                      <Input
                        type="number"
                        placeholder="0.00"
                        value={buyAmount}
                        onChange={(e) => setBuyAmount(e.target.value)}
                        className="mt-1"
                      />
                    </div>
                    <div className="rounded-lg bg-muted/50 p-3">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Available</span>
                        <span className="font-medium">{totalBalance.toFixed(2)} USDT</span>
                      </div>
                    </div>
                    <Button onClick={handleBuy} className="w-full bg-primary hover:bg-primary/90">
                      Buy {selectedPair.symbol.split("/")[0]}
                    </Button>
                  </TabsContent>

                  <TabsContent value="sell" className="space-y-4">
                    {orderType === "limit" && (
                      <div>
                        <Label className="text-xs text-muted-foreground">Price (USDT)</Label>
                        <Input
                          type="number"
                          placeholder="0.00"
                          value={sellPrice}
                          onChange={(e) => setSellPrice(e.target.value)}
                          className="mt-1"
                        />
                      </div>
                    )}
                    <div>
                      <Label className="text-xs text-muted-foreground">Amount (BTC)</Label>
                      <Input
                        type="number"
                        placeholder="0.00"
                        value={sellAmount}
                        onChange={(e) => setSellAmount(e.target.value)}
                        className="mt-1"
                      />
                    </div>
                    <div className="rounded-lg bg-muted/50 p-3">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Available</span>
                        <span className="font-medium">0.00 BTC</span>
                      </div>
                    </div>
                    <Button onClick={handleSell} variant="destructive" className="w-full">
                      Sell {selectedPair.symbol.split("/")[0]}
                    </Button>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>

            {/* Open Orders */}
            <Card className="mt-6 border-border/50">
              <CardHeader>
                <CardTitle className="text-base">Open Orders</CardTitle>
              </CardHeader>
              <CardContent>
                {!Array.isArray(orders) || orders.filter(o => o.status === 'pending' || o.status === 'partial_filled').length === 0 ? (
                  <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
                    No open orders
                  </div>
                ) : (
                  <div className="space-y-2">
                    {orders
                      .filter(o => o.status === 'pending' || o.status === 'partial_filled')
                      .map((order) => (
                        <div
                          key={order.id}
                          className="flex items-center justify-between rounded-lg border border-border/50 p-3"
                        >
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span
                                className={`text-sm font-medium ${
                                  order.side === 'buy' ? 'text-primary' : 'text-destructive'
                                }`}
                              >
                                {order.side.toUpperCase()}
                              </span>
                              <span className="text-sm text-muted-foreground">
                                {order.trading_pair.symbol}
                              </span>
                            </div>
                            <div className="mt-1 text-xs text-muted-foreground">
                              {order.order_type === 'limit' ? `@ ${order.price}` : 'Market'} • {order.quantity}{' '}
                              {order.trading_pair.base_currency.symbol}
                            </div>
                          </div>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="text-destructive hover:text-destructive"
                            onClick={() => cancelOrder(order.id)}
                          >
                            Cancel
                          </Button>
                        </div>
                      ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
