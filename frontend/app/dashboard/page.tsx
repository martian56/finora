"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useWallets, useOrders } from "@/hooks/use-trading"
import { TrendingUp, TrendingDown, Activity, Wallet } from "lucide-react"

export default function DashboardPage() {
  const router = useRouter()
  const { user, isLoading } = useAuth()
  const { wallets, isLoading: walletsLoading } = useWallets()
  const { orders, isLoading: ordersLoading } = useOrders()

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login")
    }
  }, [user, isLoading, router])

  if (isLoading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <span className="text-lg text-muted-foreground">Loading...</span>
        </div>
      </div>
    )
  }

  // Calculate portfolio metrics
  const totalBalance = Array.isArray(wallets) 
    ? wallets.reduce((sum, wallet) => sum + (Number(wallet.balance) || 0), 0) 
    : 0
  const totalAvailable = Array.isArray(wallets) 
    ? wallets.reduce((sum, wallet) => sum + (Number(wallet.available_balance) || 0), 0) 
    : 0
  const totalLocked = Array.isArray(wallets) 
    ? wallets.reduce((sum, wallet) => sum + (Number(wallet.frozen_balance) || 0), 0) 
    : 0
  
  // Calculate P&L (simplified - in real app this would be more complex)
  const totalPnL = 0 // This would be calculated from trade history
  const totalPnLPercentage = totalBalance > 0 ? (totalPnL / totalBalance) * 100 : 0

  // Get active orders
  const activeOrders = Array.isArray(orders) ? orders.filter(order => order.status === 'pending' || order.status === 'partial') : []
  const recentOrders = Array.isArray(orders) ? orders.slice(0, 5) : []

  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="mb-6">
          <h2 className="text-3xl font-bold">Dashboard</h2>
          <p className="text-muted-foreground">Welcome back, {user.first_name || user.email}</p>
        </div>

        <div className="mb-6 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
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

        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="border-border/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Recent Orders
              </CardTitle>
            </CardHeader>
            <CardContent>
              {ordersLoading ? (
                <div className="flex h-32 items-center justify-center">
                  <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                </div>
              ) : recentOrders.length === 0 ? (
                <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
                  No orders yet
                </div>
              ) : (
                <div className="space-y-3">
                  {recentOrders.map((order) => (
                    <div
                      key={order.id}
                      className="flex items-center justify-between rounded-lg border border-border/50 p-3"
                    >
                      <div>
                        <p className="font-medium">
                          {order.side.toUpperCase()} {order.order_type.toUpperCase()}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {order.quantity} @ {order.price ? `$${order.price}` : 'Market'}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className={`text-sm font-medium ${
                          order.status === 'filled' ? 'text-primary' :
                          order.status === 'cancelled' ? 'text-destructive' :
                          'text-muted-foreground'
                        }`}>
                          {order.status.toUpperCase()}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(order.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="border-border/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Wallet className="h-5 w-5" />
                Wallet Balances
              </CardTitle>
            </CardHeader>
            <CardContent>
              {walletsLoading ? (
                <div className="flex h-32 items-center justify-center">
                  <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
                </div>
              ) : wallets.length === 0 ? (
                <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
                  No wallets found
                </div>
              ) : (
                <div className="space-y-3">
                  {Array.isArray(wallets) ? wallets.slice(0, 5).map((wallet) => (
                    <div
                      key={wallet.id}
                      className="flex items-center justify-between rounded-lg border border-border/50 p-3"
                    >
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/20">
                          <span className="text-sm font-bold text-primary">
                            {wallet.currency.symbol[0]}
                          </span>
                        </div>
                        <div>
                          <p className="font-medium">{wallet.currency.symbol}</p>
                          <p className="text-sm text-muted-foreground">{wallet.currency.name}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{Number(wallet.balance).toFixed(6)}</p>
                        <p className="text-xs text-muted-foreground">
                          Available: {Number(wallet.available_balance).toFixed(6)}
                        </p>
                      </div>
                    </div>
                  )) : null}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}
