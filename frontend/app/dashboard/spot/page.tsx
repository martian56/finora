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
  const [orderBook, setOrderBook] = useState({ asks: [], bids: [] })
  const [orderType, setOrderType] = useState<"limit" | "market">("limit")
  const [buyAmount, setBuyAmount] = useState("")
  const [buyPrice, setBuyPrice] = useState("")
  const [sellAmount, setSellAmount] = useState("")
  const [sellPrice, setSellPrice] = useState("")

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

  // Fetch market data for selected pair
  useEffect(() => {
    if (selectedPair?.symbol) {
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
  }, [selectedPair?.symbol])


  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login")
    }
  }, [user, isLoading, router])

  // Real-time order book updates (only if market data exists)
  useEffect(() => {
    if (!marketData || !selectedPair || !marketData.price) return
    
    const generateOrderBook = () => {
      const asks = Array.from({ length: 10 }, (_, i) => ({
        price: marketData.price + i * 10,
        amount: Math.random() * 2,
        total: 0,
      }))
      const bids = Array.from({ length: 10 }, (_, i) => ({
        price: marketData.price - i * 10,
        amount: Math.random() * 2,
        total: 0,
      }))
      return { asks: asks.reverse(), bids }
    }
    
    // Initial order book
    setOrderBook(generateOrderBook())
    
    const interval = setInterval(() => {
      setOrderBook(generateOrderBook())
    }, 3000)
    
    return () => clearInterval(interval)
  }, [marketData])

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
      <div className="p-6">
        <div className="mb-6">
          <h2 className="text-3xl font-bold">Spot Trading</h2>
          <p className="text-muted-foreground">Trade cryptocurrencies with instant settlement</p>
        </div>

        <div className="grid gap-6 lg:grid-cols-12">
          {/* Left sidebar - Trading pairs */}
          <div className="lg:col-span-3">
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle className="text-base">Markets</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <div className="space-y-1">
                  {pairsLoading ? (
                    <div className="flex h-32 items-center justify-center">
                      <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                    </div>
                  ) : pairs.length === 0 ? (
                    <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
                      No trading pairs available
                    </div>
                  ) : (
                    pairs.map((pair) => (
                      <button
                        key={pair.id}
                        onClick={() => setSelectedPair(pair)}
                        className={`flex w-full items-center justify-between px-4 py-3 text-left transition-colors hover:bg-muted ${
                          selectedPair?.id === pair.id ? "bg-muted" : ""
                        }`}
                      >
                        <div>
                          <p className="font-medium">
                            {pair.base_currency.symbol}/{pair.quote_currency.symbol}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {marketData?.price?.toFixed(2) || "Loading..."}
                          </p>
                        </div>
                        <div className={`text-sm font-medium ${
                          marketData?.change_24h >= 0 ? "text-primary" : "text-destructive"
                        }`}>
                          {marketData?.change_24h >= 0 ? "+" : ""}
                          {marketData?.change_24h?.toFixed(2) || "0.00"}%
                        </div>
                      </button>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Center - Chart and Order Book */}
          <div className="space-y-6 lg:col-span-6">
            {/* Price header */}
            <Card className="border-border/50">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{selectedPair?.symbol || 'N/A'}</p>
                    <div className="flex items-center gap-2">
                      <p className="text-3xl font-bold">{selectedPair?.price?.toFixed(2) || '0.00'}</p>
                      <div
                        className={`flex items-center gap-1 text-sm font-medium ${
                          (selectedPair?.change || 0) >= 0 ? "text-primary" : "text-destructive"
                        }`}
                      >
                        {(selectedPair?.change || 0) >= 0 ? (
                          <TrendingUp className="h-4 w-4" />
                        ) : (
                          <TrendingDown className="h-4 w-4" />
                        )}
                        {(selectedPair?.change || 0) >= 0 ? "+" : ""}
                        {(selectedPair?.change || 0).toFixed(2)}%
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">24h Volume</p>
                    <p className="text-lg font-semibold">1,234.56 BTC</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Chart placeholder */}
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle className="text-base">Price Chart</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex h-64 items-center justify-center rounded-lg bg-muted/30">
                  <p className="text-muted-foreground">Chart visualization coming soon</p>
                </div>
              </CardContent>
            </Card>

            {/* Order Book */}
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle className="text-base">Order Book</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-2 text-xs font-medium text-muted-foreground">
                    <div>Price (USDT)</div>
                    <div className="text-right">Amount (BTC)</div>
                    <div className="text-right">Total</div>
                  </div>
                  {/* Asks (Sell orders) */}
                  <div className="space-y-1">
                    {orderBook.asks.slice(0, 5).map((ask, i) => (
                      <div key={i} className="grid grid-cols-3 gap-2 text-sm">
                        <div className="font-medium text-destructive">{ask.price.toFixed(2)}</div>
                        <div className="text-right">{ask.amount.toFixed(4)}</div>
                        <div className="text-right text-muted-foreground">{(ask.price * ask.amount).toFixed(2)}</div>
                      </div>
                    ))}
                  </div>
                  {/* Current price */}
                  <div className="border-y border-border/50 py-2 text-center font-bold">
                    {selectedPair?.price?.toFixed(2) || '0.00'}
                  </div>
                  {/* Bids (Buy orders) */}
                  <div className="space-y-1">
                    {orderBook.bids.slice(0, 5).map((bid, i) => (
                      <div key={i} className="grid grid-cols-3 gap-2 text-sm">
                        <div className="font-medium text-primary">{bid.price.toFixed(2)}</div>
                        <div className="text-right">{bid.amount.toFixed(4)}</div>
                        <div className="text-right text-muted-foreground">{(bid.price * bid.amount).toFixed(2)}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right sidebar - Trading panel */}
          <div className="lg:col-span-3">
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle className="text-base">Place Order</CardTitle>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="buy" className="w-full">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="buy">Buy</TabsTrigger>
                    <TabsTrigger value="sell">Sell</TabsTrigger>
                  </TabsList>

                  <div className="mb-4 mt-4">
                    <Label className="text-xs text-muted-foreground">Order Type</Label>
                    <Select value={orderType} onValueChange={(v) => setOrderType(v as "limit" | "market")}>
                      <SelectTrigger className="mt-1">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="limit">Limit</SelectItem>
                        <SelectItem value="market">Market</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <TabsContent value="buy" className="space-y-4">
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
