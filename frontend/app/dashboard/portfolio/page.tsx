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
  id: number
  wallet: number
  transaction_type: "deposit" | "withdrawal" | "trade" | "transfer"
  amount: number
  balance_after: number
  description: string
  timestamp: string
  created_at?: string
}

export default function PortfolioPage() {
  const router = useRouter()
  const { user, isLoading } = useAuth()
  const { toast } = useToast()
  const { wallets, isLoading: walletsLoading } = useWallets()

  // Convert wallets to assets format for compatibility
  // Filter to show only wallets with balance > 0
  const assets = Array.isArray(wallets) ? wallets
    .filter(wallet => Number(wallet.balance) > 0)
    .map(wallet => ({
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

  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [transactionsLoading, setTransactionsLoading] = useState(true)

  // Fetch transactions from API
  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        setTransactionsLoading(true)
        const data = await apiClient.getTransactions()
        setTransactions(data || [])
      } catch (error) {
        console.error('Failed to fetch transactions:', error)
        toast({
          title: "Error",
          description: "Failed to load transactions",
          variant: "destructive",
        })
      } finally {
        setTransactionsLoading(false)
      }
    }

    if (user) {
      fetchTransactions()
    }
  }, [user, toast])

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

    // TODO: Implement actual deposit API call
    toast({
      title: "Deposit Initiated",
      description: `Deposit of ${amount} USDT initiated. This is a mock deposit - implement real deposit in production.`,
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

    // TODO: Implement actual withdrawal API call
    toast({
      title: "Withdrawal Initiated",
      description: `Withdrawal of ${amount} USDT initiated. This is a mock withdrawal - implement real withdrawal in production.`,
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
                {assets.length === 0 ? (
                  <div className="flex h-48 flex-col items-center justify-center text-center">
                    <Wallet className="mb-4 h-12 w-12 text-muted-foreground" />
                    <p className="text-lg font-medium">No Assets Yet</p>
                    <p className="mt-2 text-sm text-muted-foreground">
                      Start trading or deposit funds to see your portfolio here
                    </p>
                  </div>
                ) : (
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
                )}
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
                {assets.length === 0 ? (
                  <div className="flex h-48 flex-col items-center justify-center text-center">
                    <PieChart className="mb-4 h-12 w-12 text-muted-foreground" />
                    <p className="text-lg font-medium">No Assets to Display</p>
                    <p className="mt-2 text-sm text-muted-foreground">
                      Your portfolio allocation will appear here once you have assets
                    </p>
                  </div>
                ) : (
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
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="transactions" className="space-y-4">
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle>Recent Transactions</CardTitle>
              </CardHeader>
              <CardContent>
                {transactionsLoading ? (
                  <div className="flex h-32 items-center justify-center">
                    <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                  </div>
                ) : transactions.length === 0 ? (
                  <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
                    No transactions yet
                  </div>
                ) : (
                  <div className="space-y-3">
                    {transactions.map((transaction) => {
                      const txDate = new Date(transaction.timestamp || transaction.created_at || '')
                      const isIncoming = transaction.transaction_type === "deposit" || transaction.transaction_type === "trade"
                      const isOutgoing = transaction.transaction_type === "withdrawal" || transaction.transaction_type === "transfer"
                      
                      return (
                        <div
                          key={transaction.id}
                          className="flex items-center justify-between rounded-lg border border-border/50 p-4 transition-colors hover:bg-muted/50"
                        >
                          <div className="flex items-center gap-4">
                            <div
                              className={`flex h-10 w-10 items-center justify-center rounded-full ${
                                isIncoming
                                  ? "bg-primary/20"
                                  : isOutgoing
                                    ? "bg-destructive/20"
                                    : "bg-muted"
                              }`}
                            >
                              {isIncoming ? (
                                <ArrowDownRight className="h-5 w-5 text-primary" />
                              ) : isOutgoing ? (
                                <ArrowUpRight className="h-5 w-5 text-destructive" />
                              ) : (
                                <TrendingUp className="h-5 w-5 text-muted-foreground" />
                              )}
                            </div>
                            <div>
                              <p className="font-medium capitalize">
                                {transaction.transaction_type}
                              </p>
                              <p className="text-sm text-muted-foreground">
                                {isNaN(txDate.getTime()) ? 'Invalid date' : (
                                  <>
                                    {txDate.toLocaleDateString()} at{" "}
                                    {txDate.toLocaleTimeString()}
                                  </>
                                )}
                              </p>
                              {transaction.description && (
                                <p className="text-xs text-muted-foreground">
                                  {transaction.description}
                                </p>
                              )}
                            </div>
                          </div>
                          <div className="text-right">
                            <p
                              className={`font-medium ${
                                isIncoming
                                  ? "text-primary"
                                  : isOutgoing
                                    ? "text-destructive"
                                    : ""
                              }`}
                            >
                              {isIncoming ? "+" : isOutgoing ? "-" : ""}
                              {Number(transaction.amount).toFixed(6)}
                            </p>
                            <p className="text-sm text-muted-foreground">
                              Balance: {Number(transaction.balance_after).toFixed(6)}
                            </p>
                          </div>
                        </div>
                      )
                    })}
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
