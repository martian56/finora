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
import { Slider } from "@/components/ui/slider"
import { TrendingUp, TrendingDown, AlertTriangle } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { useTradingPairs, useWallets } from "@/hooks/use-trading"
import { apiClient } from "@/lib/api-client"

interface Position {
  symbol: string
  side: "long" | "short"
  size: number
  entryPrice: number
  markPrice: number
  leverage: number
  margin: number
  pnl: number
  pnlPercent: number
  liquidationPrice: number
}

export default function FuturesTradingPage() {
  const router = useRouter()
  const { user, isLoading } = useAuth()
  const { toast } = useToast()
  const { pairs, isLoading: pairsLoading } = useTradingPairs()
  const { wallets } = useWallets()
  
  const [selectedPair, setSelectedPair] = useState<any>(null)
  const [marketData, setMarketData] = useState<any>(null)
  const [leverage, setLeverage] = useState([10])
  const [orderType, setOrderType] = useState<"limit" | "market">("limit")
  const [longAmount, setLongAmount] = useState("")
  const [longPrice, setLongPrice] = useState("")
  const [shortAmount, setShortAmount] = useState("")
  const [shortPrice, setShortPrice] = useState("")
  const [positions, setPositions] = useState<Position[]>([])

  // Set default pair when pairs are loaded
  useEffect(() => {
    if (pairs.length > 0 && !selectedPair) {
      setSelectedPair(pairs[0])
    }
  }, [pairs, selectedPair])

  // Fetch market data for selected pair
  useEffect(() => {
    if (selectedPair?.symbol) {
      const fetchMarketData = async () => {
        try {
          const data = await apiClient.getMarketData(selectedPair.symbol)
          setMarketData(data)
          setSelectedPair((prev: any) => ({
            ...prev,
            price: data.price,
            change: data.change_24h,
          }))
        } catch (error) {
          console.error("Failed to fetch market data:", error)
          // Set empty market data - will show zeros until trading starts
          setMarketData(null)
          setSelectedPair((prev: any) => ({
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

  // Real-time price updates (only if market data exists)
  useEffect(() => {
    if (!marketData || !marketData.price) return
    
    const interval = setInterval(() => {
      // Update positions PnL based on current market price
      setPositions((prev) =>
        prev.map((pos) => {
          const newMarkPrice = pos.markPrice + (Math.random() - 0.5) * 10
          const pnl =
            pos.side === "long"
              ? (newMarkPrice - pos.entryPrice) * pos.size
              : (pos.entryPrice - newMarkPrice) * pos.size
          const pnlPercent = (pnl / pos.margin) * 100
          return { ...pos, markPrice: newMarkPrice, pnl, pnlPercent }
        }),
      )
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

  const calculateLiquidationPrice = (entryPrice: number, leverage: number, side: "long" | "short") => {
    if (side === "long") {
      return entryPrice * (1 - 0.9 / leverage)
    } else {
      return entryPrice * (1 + 0.9 / leverage)
    }
  }

  // Calculate total balance from wallets
  const totalBalance = Array.isArray(wallets) 
    ? wallets.reduce((sum, wallet) => sum + (Number(wallet.balance) || 0), 0) 
    : 0

  const handleOpenLong = () => {
    if (!longAmount || (orderType === "limit" && !longPrice)) {
      toast({
        title: "Invalid Order",
        description: "Please fill in all required fields",
        variant: "destructive",
      })
      return
    }

    const amount = Number.parseFloat(longAmount)
    const price = orderType === "limit" ? Number.parseFloat(longPrice) : (selectedPair.price || marketData?.price || 0)
    const margin = (price * amount) / leverage[0]

    if (margin > totalBalance) {
      toast({
        title: "Insufficient Balance",
        description: "You don't have enough balance for this position",
        variant: "destructive",
      })
      return
    }

    const newPosition: Position = {
      symbol: selectedPair.symbol,
      side: "long",
      size: amount,
      entryPrice: price,
      markPrice: price,
      leverage: leverage[0],
      margin,
      pnl: 0,
      pnlPercent: 0,
      liquidationPrice: calculateLiquidationPrice(price, leverage[0], "long"),
    }

    setPositions([...positions, newPosition])
    toast({
      title: "Position Opened",
      description: `Long position opened for ${amount} ${selectedPair.symbol} at ${leverage[0]}x leverage`,
    })
    setLongAmount("")
    setLongPrice("")
  }

  const handleOpenShort = () => {
    if (!shortAmount || (orderType === "limit" && !shortPrice)) {
      toast({
        title: "Invalid Order",
        description: "Please fill in all required fields",
        variant: "destructive",
      })
      return
    }

    const amount = Number.parseFloat(shortAmount)
    const price = orderType === "limit" ? Number.parseFloat(shortPrice) : (selectedPair.price || marketData?.price || 0)
    const margin = (price * amount) / leverage[0]

    if (margin > totalBalance) {
      toast({
        title: "Insufficient Balance",
        description: "You don't have enough balance for this position",
        variant: "destructive",
      })
      return
    }

    const newPosition: Position = {
      symbol: selectedPair.symbol,
      side: "short",
      size: amount,
      entryPrice: price,
      markPrice: price,
      leverage: leverage[0],
      margin,
      pnl: 0,
      pnlPercent: 0,
      liquidationPrice: calculateLiquidationPrice(price, leverage[0], "short"),
    }

    setPositions([...positions, newPosition])
    toast({
      title: "Position Opened",
      description: `Short position opened for ${amount} ${selectedPair.symbol} at ${leverage[0]}x leverage`,
    })
    setShortAmount("")
    setShortPrice("")
  }

  const handleClosePosition = (index: number) => {
    const position = positions[index]
    toast({
      title: "Position Closed",
      description: `${position.side.toUpperCase()} position closed with ${position.pnl >= 0 ? "profit" : "loss"} of ${Math.abs(position.pnl).toFixed(2)} USDT`,
    })
    setPositions(positions.filter((_, i) => i !== index))
  }

  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="mb-6">
          <h2 className="text-3xl font-bold">Futures Trading</h2>
          <p className="text-muted-foreground">Trade perpetual futures with up to 125x leverage</p>
        </div>

        <div className="grid gap-6 lg:grid-cols-12">
          {/* Left sidebar - Trading pairs */}
          <div className="lg:col-span-3">
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle className="text-base">Perpetual Futures</CardTitle>
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
                        className={`flex w-full flex-col gap-1 px-4 py-3 text-left transition-colors hover:bg-muted ${
                          selectedPair?.id === pair.id ? "bg-muted" : ""
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <p className="font-medium">
                            {pair.base_currency.symbol}/{pair.quote_currency.symbol}
                          </p>
                          <div
                            className={`text-sm font-medium ${
                              marketData?.change_24h >= 0 ? "text-primary" : "text-destructive"
                            }`}
                          >
                            {marketData?.change_24h >= 0 ? "+" : ""}
                            {marketData?.change_24h?.toFixed(2) || "0.00"}%
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <p className="text-sm text-muted-foreground">
                            ${marketData?.price?.toFixed(2) || "Loading..."}
                          </p>
                          <p className="text-xs text-muted-foreground">FR: 0.01%</p>
                        </div>
                      </button>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Center - Chart and Positions */}
          <div className="space-y-6 lg:col-span-6">
            {/* Price header */}
            <Card className="border-border/50">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">
                      {selectedPair ? `${selectedPair.base_currency.symbol}/${selectedPair.quote_currency.symbol} Perpetual` : "Select a Pair"}
                    </p>
                    <div className="flex items-center gap-2">
                      <p className="text-3xl font-bold">
                        ${marketData?.price?.toFixed(2) || "Loading..."}
                      </p>
                      <div
                        className={`flex items-center gap-1 text-sm font-medium ${
                          marketData?.change_24h >= 0 ? "text-primary" : "text-destructive"
                        }`}
                      >
                        {marketData?.change_24h >= 0 ? (
                          <TrendingUp className="h-4 w-4" />
                        ) : (
                          <TrendingDown className="h-4 w-4" />
                        )}
                        {marketData?.change_24h >= 0 ? "+" : ""}
                        {marketData?.change_24h?.toFixed(2) || "0.00"}%
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">Funding Rate</p>
                    <p className="text-lg font-semibold">0.01%</p>
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

            {/* Open Positions */}
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle className="text-base">Open Positions</CardTitle>
              </CardHeader>
              <CardContent>
                {positions.length === 0 ? (
                  <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
                    No open positions
                  </div>
                ) : (
                  <div className="space-y-3">
                    {positions.map((position, index) => (
                      <div key={index} className="rounded-lg border border-border/50 p-4">
                        <div className="mb-3 flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <span className="font-medium">{position.symbol}</span>
                            <span
                              className={`rounded px-2 py-0.5 text-xs font-medium ${
                                position.side === "long"
                                  ? "bg-primary/20 text-primary"
                                  : "bg-destructive/20 text-destructive"
                              }`}
                            >
                              {position.side.toUpperCase()} {position.leverage}x
                            </span>
                          </div>
                          <Button size="sm" variant="outline" onClick={() => handleClosePosition(index)}>
                            Close
                          </Button>
                        </div>
                        <div className="grid grid-cols-2 gap-3 text-sm">
                          <div>
                            <p className="text-muted-foreground">Size</p>
                            <p className="font-medium">{position.size.toFixed(4)}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Entry Price</p>
                            <p className="font-medium">{position.entryPrice.toFixed(2)}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Mark Price</p>
                            <p className="font-medium">{position.markPrice.toFixed(2)}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Margin</p>
                            <p className="font-medium">{position.margin.toFixed(2)} USDT</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">PnL</p>
                            <p className={`font-medium ${position.pnl >= 0 ? "text-primary" : "text-destructive"}`}>
                              {position.pnl >= 0 ? "+" : ""}
                              {position.pnl.toFixed(2)} USDT ({position.pnlPercent.toFixed(2)}%)
                            </p>
                          </div>
                          <div>
                            <p className="flex items-center gap-1 text-muted-foreground">
                              <AlertTriangle className="h-3 w-3" />
                              Liq. Price
                            </p>
                            <p className="font-medium text-destructive">{position.liquidationPrice.toFixed(2)}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right sidebar - Trading panel */}
          <div className="lg:col-span-3">
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle className="text-base">Open Position</CardTitle>
              </CardHeader>
              <CardContent>
                {/* Leverage Slider */}
                <div className="mb-6">
                  <div className="mb-2 flex items-center justify-between">
                    <Label className="text-xs text-muted-foreground">Leverage</Label>
                    <span className="text-sm font-bold">{leverage[0]}x</span>
                  </div>
                  <Slider value={leverage} onValueChange={setLeverage} min={1} max={125} step={1} className="mb-2" />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>1x</span>
                    <span>125x</span>
                  </div>
                </div>

                <Tabs defaultValue="long" className="w-full">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="long">Long</TabsTrigger>
                    <TabsTrigger value="short">Short</TabsTrigger>
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

                  <TabsContent value="long" className="space-y-4">
                    {orderType === "limit" && (
                      <div>
                        <Label className="text-xs text-muted-foreground">Price (USDT)</Label>
                        <Input
                          type="number"
                          placeholder="0.00"
                          value={longPrice}
                          onChange={(e) => setLongPrice(e.target.value)}
                          className="mt-1"
                        />
                      </div>
                    )}
                    <div>
                      <Label className="text-xs text-muted-foreground">Size</Label>
                      <Input
                        type="number"
                        placeholder="0.00"
                        value={longAmount}
                        onChange={(e) => setLongAmount(e.target.value)}
                        className="mt-1"
                      />
                    </div>
                    <div className="rounded-lg bg-muted/50 p-3 text-sm">
                      <div className="mb-1 flex justify-between">
                        <span className="text-muted-foreground">Available</span>
                        <span className="font-medium">{totalBalance.toFixed(2)} USDT</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Required Margin</span>
                        <span className="font-medium">
                          {longAmount && (orderType === "market" || longPrice)
                            ? (
                                ((orderType === "limit" ? Number.parseFloat(longPrice) : selectedPair.price) *
                                  Number.parseFloat(longAmount)) /
                                leverage[0]
                              ).toFixed(2)
                            : "0.00"}{" "}
                          USDT
                        </span>
                      </div>
                    </div>
                    <Button onClick={handleOpenLong} className="w-full bg-primary hover:bg-primary/90">
                      Open Long
                    </Button>
                  </TabsContent>

                  <TabsContent value="short" className="space-y-4">
                    {orderType === "limit" && (
                      <div>
                        <Label className="text-xs text-muted-foreground">Price (USDT)</Label>
                        <Input
                          type="number"
                          placeholder="0.00"
                          value={shortPrice}
                          onChange={(e) => setShortPrice(e.target.value)}
                          className="mt-1"
                        />
                      </div>
                    )}
                    <div>
                      <Label className="text-xs text-muted-foreground">Size</Label>
                      <Input
                        type="number"
                        placeholder="0.00"
                        value={shortAmount}
                        onChange={(e) => setShortAmount(e.target.value)}
                        className="mt-1"
                      />
                    </div>
                    <div className="rounded-lg bg-muted/50 p-3 text-sm">
                      <div className="mb-1 flex justify-between">
                        <span className="text-muted-foreground">Available</span>
                        <span className="font-medium">{totalBalance.toFixed(2)} USDT</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Required Margin</span>
                        <span className="font-medium">
                          {shortAmount && (orderType === "market" || shortPrice)
                            ? (
                                ((orderType === "limit" ? Number.parseFloat(shortPrice) : selectedPair.price) *
                                  Number.parseFloat(shortAmount)) /
                                leverage[0]
                              ).toFixed(2)
                            : "0.00"}{" "}
                          USDT
                        </span>
                      </div>
                    </div>
                    <Button onClick={handleOpenShort} variant="destructive" className="w-full">
                      Open Short
                    </Button>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
