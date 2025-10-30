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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Wallet, TrendingUp, TrendingDown, ArrowUpRight, ArrowDownRight, Plus, Minus, PieChart } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { useWallets } from "@/hooks/use-trading"
import { apiClient } from "@/lib/api-client"

interface Asset {
  symbol: string
  name: string
  balance: number
  availableBalance: number
  lockedBalance: number
  usdValue: number
  price: number
  change24h: number
  avgBuyPrice?: number
  pnl?: number
  pnlPercentage?: number
}

interface Transaction {
  id: string
  type: "deposit" | "withdraw" | "trade" | "buy" | "sell"
  asset: string
  amount: number
  price?: number
  timestamp: Date
  status: "completed" | "pending" | "failed"
}

export default function PortfolioPage() {
  const router = useRouter()
  const { user, isLoading } = useAuth()
  const { toast } = useToast()
  const { wallets, isLoading: walletsLoading } = useWallets()

  // Convert wallets to assets format for compatibility
  const assets = Array.isArray(wallets) ? wallets.map(wallet => ({
    symbol: wallet.currency.symbol,
    name: wallet.currency.name,
    balance: Number(wallet.balance) || 0,
    availableBalance: Number(wallet.available_balance) || 0,
    lockedBalance: Number(wallet.frozen_balance) || 0,
    usdValue: Number(wallet.balance) || 0, // Assuming 1:1 for USDT, would need price data for others
    price: 1.0, // Would need to fetch real prices
    change24h: 0, // Would need to fetch real price changes
    avgBuyPrice: 1.0,
    pnl: 0,
    pnlPercentage: 0,
  })) : []

  const [transactions, setTransactions] = useState<Transaction[]>([
    {
      id: "1",
      type: "deposit",
      asset: "USDT",
      amount: 1000,
      timestamp: new Date(Date.now() - 86400000 * 5),
      status: "completed",
    },
    {
      id: "2",
      type: "buy",
      asset: "BTC",
      amount: 0.05234,
      price: 98500,
      timestamp: new Date(Date.now() - 86400000 * 4),
      status: "completed",
    },
    {
      id: "3",
      type: "buy",
      asset: "ETH",
      amount: 1.2456,
      price: 3450,
      timestamp: new Date(Date.now() - 86400000 * 3),
      status: "completed",
    },
    {
      id: "4",
      type: "buy",
      asset: "BNB",
      amount: 5.678,
      price: 580,
      timestamp: new Date(Date.now() - 86400000 * 2),
      status: "completed",
    },
    {
      id: "5",
      type: "buy",
      asset: "SOL",
      amount: 12.345,
      price: 195,
      timestamp: new Date(Date.now() - 86400000),
      status: "completed",
    },
  ])

  const [isDepositOpen, setIsDepositOpen] = useState(false)
  const [isWithdrawOpen, setIsWithdrawOpen] = useState(false)
  const [depositAmount, setDepositAmount] = useState("")
  const [withdrawAmount, setWithdrawAmount] = useState("")

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login")
    }
  }, [user, isLoading, router])

  if (isLoading || walletsLoading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <span className="text-lg text-muted-foreground">Loading...</span>
        </div>
      </div>
    )
  }

  const totalBalance = assets.reduce((sum, asset) => sum + asset.usdValue, 0)
  const totalAvailable = assets.reduce((sum, asset) => sum + asset.availableBalance * asset.price, 0)
  const totalLocked = assets.reduce((sum, asset) => sum + asset.lockedBalance * asset.price, 0)

  const totalPnL = assets.reduce((sum, asset) => sum + (asset.pnl || 0), 0)
  const totalPnLPercentage = totalBalance > 0 ? (totalPnL / (totalBalance - totalPnL)) * 100 : 0

  const handleDeposit = () => {
    const amount = Number.parseFloat(depositAmount)
    if (!amount || amount <= 0) {
      toast({
        title: "Invalid Amount",
        description: "Please enter a valid deposit amount",
        variant: "destructive",
      })
      return
    }

    setAssets((prev) =>
      prev.map((asset) =>
        asset.symbol === "USDT"
          ? {
              ...asset,
              balance: asset.balance + amount,
              availableBalance: asset.availableBalance + amount,
              usdValue: asset.usdValue + amount,
            }
          : asset,
      ),
    )

    const newTransaction: Transaction = {
      id: Math.random().toString(36).substr(2, 9),
      type: "deposit",
      asset: "USDT",
      amount,
      timestamp: new Date(),
      status: "completed",
    }
    setTransactions([newTransaction, ...transactions])

    toast({
      title: "Deposit Successful",
      description: `${amount} USDT has been added to your account`,
    })

    setDepositAmount("")
    setIsDepositOpen(false)
  }

  const handleWithdraw = () => {
    const amount = Number.parseFloat(withdrawAmount)
    if (!amount || amount <= 0) {
      toast({
        title: "Invalid Amount",
        description: "Please enter a valid withdrawal amount",
        variant: "destructive",
      })
      return
    }

    const usdtAsset = assets.find((a) => a.symbol === "USDT")
    if (!usdtAsset || amount > usdtAsset.availableBalance) {
      toast({
        title: "Insufficient Balance",
        description: "You don't have enough available balance for this withdrawal",
        variant: "destructive",
      })
      return
    }

    setAssets((prev) =>
      prev.map((asset) =>
        asset.symbol === "USDT"
          ? {
              ...asset,
              balance: asset.balance - amount,
              availableBalance: asset.availableBalance - amount,
              usdValue: asset.usdValue - amount,
            }
          : asset,
      ),
    )

    const newTransaction: Transaction = {
      id: Math.random().toString(36).substr(2, 9),
      type: "withdraw",
      asset: "USDT",
      amount,
      timestamp: new Date(),
      status: "completed",
    }
    setTransactions([newTransaction, ...transactions])

    toast({
      title: "Withdrawal Successful",
      description: `${amount} USDT has been withdrawn from your account`,
    })

    setWithdrawAmount("")
    setIsWithdrawOpen(false)
  }

  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold">Portfolio</h2>
            <p className="text-muted-foreground">Manage your assets and view transaction history</p>
          </div>
          <div className="flex gap-2">
            <Dialog open={isDepositOpen} onOpenChange={setIsDepositOpen}>
              <DialogTrigger asChild>
                <Button variant="outline">
                  <Plus className="mr-2 h-4 w-4" />
                  Deposit
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Deposit Funds</DialogTitle>
                  <DialogDescription>Add funds to your trading account (mock deposit)</DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div>
                    <Label htmlFor="depositAmount">Amount (USDT)</Label>
                    <Input
                      id="depositAmount"
                      type="number"
                      placeholder="0.00"
                      value={depositAmount}
                      onChange={(e) => setDepositAmount(e.target.value)}
                      className="mt-1"
                    />
                  </div>
                </div>
                <Button onClick={handleDeposit} className="w-full">
                  Confirm Deposit
                </Button>
              </DialogContent>
            </Dialog>

            <Dialog open={isWithdrawOpen} onOpenChange={setIsWithdrawOpen}>
              <DialogTrigger asChild>
                <Button variant="outline">
                  <Minus className="mr-2 h-4 w-4" />
                  Withdraw
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Withdraw Funds</DialogTitle>
                  <DialogDescription>Withdraw funds from your trading account (mock withdrawal)</DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div>
                    <Label htmlFor="withdrawAmount">Amount (USDT)</Label>
                    <Input
                      id="withdrawAmount"
                      type="number"
                      placeholder="0.00"
                      value={withdrawAmount}
                      onChange={(e) => setWithdrawAmount(e.target.value)}
                      className="mt-1"
                    />
                    <p className="mt-1 text-xs text-muted-foreground">
                      Available: {assets.find((a) => a.symbol === "USDT")?.availableBalance.toFixed(2)} USDT
                    </p>
                  </div>
                </div>
                <Button onClick={handleWithdraw} className="w-full">
                  Confirm Withdrawal
                </Button>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        <div className="mb-6 grid gap-4 md:grid-cols-4">
          <Card className="border-border/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Balance</CardTitle>
              <Wallet className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${totalBalance.toFixed(2)}</div>
              <p className="mt-1 text-xs text-muted-foreground">Portfolio value</p>
            </CardContent>
          </Card>

          <Card className="border-border/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total PnL</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${totalPnL >= 0 ? "text-primary" : "text-destructive"}`}>
                {totalPnL >= 0 ? "+" : ""}
                {totalPnL.toFixed(2)} USDT
              </div>
              <p className={`mt-1 text-xs ${totalPnLPercentage >= 0 ? "text-primary" : "text-destructive"}`}>
                {totalPnLPercentage >= 0 ? "+" : ""}
                {totalPnLPercentage.toFixed(2)}%
              </p>
            </CardContent>
          </Card>

          <Card className="border-border/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Available Balance</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${totalAvailable.toFixed(2)}</div>
              <p className="mt-1 text-xs text-muted-foreground">Ready for trading</p>
            </CardContent>
          </Card>

          <Card className="border-border/50">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">In Orders</CardTitle>
              <TrendingDown className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${totalLocked.toFixed(2)}</div>
              <p className="mt-1 text-xs text-muted-foreground">Locked in positions</p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="assets" className="space-y-6">
          <TabsList>
            <TabsTrigger value="assets">Assets</TabsTrigger>
            <TabsTrigger value="allocation">Allocation</TabsTrigger>
            <TabsTrigger value="transactions">Transaction History</TabsTrigger>
          </TabsList>

          <TabsContent value="assets" className="space-y-4">
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle>Asset Balances</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {assets.map((asset) => (
                    <div
                      key={asset.symbol}
                      className="flex items-center justify-between rounded-lg border border-border/50 p-4 transition-colors hover:bg-muted/50"
                    >
                      <div className="flex items-center gap-4">
                        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/20">
                          <span className="text-lg font-bold text-primary">{asset.symbol[0]}</span>
                        </div>
                        <div>
                          <p className="font-semibold">{asset.symbol}</p>
                          <p className="text-sm text-muted-foreground">{asset.name}</p>
                        </div>
                      </div>

                      <div className="text-right">
                        <p className="text-sm text-muted-foreground">Balance</p>
                        <p className="font-medium">{asset.balance.toFixed(6)}</p>
                      </div>

                      <div className="text-right">
                        <p className="text-sm text-muted-foreground">Value</p>
                        <p className="font-medium">${asset.usdValue.toFixed(2)}</p>
                      </div>

                      <div className="text-right">
                        <p className="text-sm text-muted-foreground">Available</p>
                        <p className="font-medium">{asset.availableBalance.toFixed(6)}</p>
                      </div>

                      {asset.lockedBalance > 0 && (
                        <div className="text-right">
                          <p className="text-sm text-muted-foreground">Locked</p>
                          <p className="font-medium text-amber-500">{asset.lockedBalance.toFixed(6)}</p>
                        </div>
                      )}

                      {asset.pnl !== undefined && (
                        <div className="text-right">
                          <p className="text-sm text-muted-foreground">PnL</p>
                          <p className={`font-medium ${asset.pnl >= 0 ? "text-primary" : "text-destructive"}`}>
                            {asset.pnl >= 0 ? "+" : ""}
                            {asset.pnl.toFixed(2)} USDT
                          </p>
                          <p className={`text-xs ${asset.pnlPercentage! >= 0 ? "text-primary" : "text-destructive"}`}>
                            {asset.pnlPercentage! >= 0 ? "+" : ""}
                            {asset.pnlPercentage!.toFixed(2)}%
                          </p>
                        </div>
                      )}

                      <div className="text-right">
                        <p className="text-sm text-muted-foreground">24h Change</p>
                        <p className={`font-medium ${asset.change24h >= 0 ? "text-primary" : "text-destructive"}`}>
                          {asset.change24h >= 0 ? "+" : ""}
                          {asset.change24h.toFixed(2)}%
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="allocation" className="space-y-4">
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChart className="h-5 w-5" />
                  Portfolio Allocation
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {assets.map((asset) => {
                    const percentage = (asset.usdValue / totalBalance) * 100
                    return (
                      <div key={asset.symbol} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/20">
                              <span className="font-bold text-primary">{asset.symbol[0]}</span>
                            </div>
                            <div>
                              <p className="font-medium">{asset.symbol}</p>
                              <p className="text-sm text-muted-foreground">${asset.usdValue.toFixed(2)}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="font-semibold">{percentage.toFixed(2)}%</p>
                            <p className="text-sm text-muted-foreground">{asset.balance.toFixed(6)}</p>
                          </div>
                        </div>
                        <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                          <div className="h-full bg-primary transition-all" style={{ width: `${percentage}%` }} />
                        </div>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="transactions" className="space-y-4">
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle>Recent Transactions</CardTitle>
              </CardHeader>
              <CardContent>
                {transactions.length === 0 ? (
                  <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
                    No transactions yet
                  </div>
                ) : (
                  <div className="space-y-3">
                    {transactions.map((transaction) => (
                      <div
                        key={transaction.id}
                        className="flex items-center justify-between rounded-lg border border-border/50 p-4 transition-colors hover:bg-muted/50"
                      >
                        <div className="flex items-center gap-4">
                          <div
                            className={`flex h-10 w-10 items-center justify-center rounded-full ${
                              transaction.type === "deposit" || transaction.type === "buy"
                                ? "bg-primary/20"
                                : transaction.type === "withdraw" || transaction.type === "sell"
                                  ? "bg-destructive/20"
                                  : "bg-muted"
                            }`}
                          >
                            {transaction.type === "deposit" || transaction.type === "buy" ? (
                              <ArrowDownRight className="h-5 w-5 text-primary" />
                            ) : transaction.type === "withdraw" || transaction.type === "sell" ? (
                              <ArrowUpRight className="h-5 w-5 text-destructive" />
                            ) : (
                              <TrendingUp className="h-5 w-5 text-muted-foreground" />
                            )}
                          </div>
                          <div>
                            <p className="font-medium capitalize">
                              {transaction.type} {transaction.asset}
                            </p>
                            <p className="text-sm text-muted-foreground">
                              {transaction.timestamp.toLocaleDateString()} at{" "}
                              {transaction.timestamp.toLocaleTimeString()}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p
                            className={`font-medium ${
                              transaction.type === "deposit" || transaction.type === "buy"
                                ? "text-primary"
                                : transaction.type === "withdraw" || transaction.type === "sell"
                                  ? "text-destructive"
                                  : ""
                            }`}
                          >
                            {transaction.type === "deposit" || transaction.type === "buy" ? "+" : "-"}
                            {transaction.amount.toFixed(6)} {transaction.asset}
                          </p>
                          {transaction.price && (
                            <p className="text-sm text-muted-foreground">@ ${transaction.price.toLocaleString()}</p>
                          )}
                          <p className="text-xs text-muted-foreground capitalize">{transaction.status}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}
