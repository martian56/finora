"use client"

import type { ReactNode } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { Button } from "@/components/ui/button"
import { TrendingUp, BarChart3, TrendingDown, Key, Wallet, LogOut, Menu } from "lucide-react"
import { cn } from "@/lib/utils"
import { useState } from "react"

interface DashboardLayoutProps {
  children: ReactNode
}

const navItems = [
  { href: "/dashboard", label: "Overview", icon: BarChart3 },
  { href: "/dashboard/spot", label: "Spot Trading", icon: TrendingUp },
  { href: "/dashboard/futures", label: "Futures Trading", icon: TrendingDown },
  { href: "/dashboard/portfolio", label: "Portfolio", icon: Wallet },
  { href: "/dashboard/api-keys", label: "API Keys", icon: Key },
]

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const pathname = usePathname()
  const { user, logout } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const handleLogout = () => {
    logout()
  }

  return (
    <div className="flex min-h-screen bg-background">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 border-r border-border/50 bg-card transition-transform duration-300 lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center gap-2 border-b border-border/50 px-6">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
              <TrendingUp className="h-5 w-5 text-primary-foreground" />
            </div>
            <h1 className="text-xl font-bold">Finora</h1>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 p-4">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground",
                  )}
                >
                  <Icon className="h-5 w-5" />
                  {item.label}
                </Link>
              )
            })}
          </nav>

          {/* User info and logout */}
          <div className="border-t border-border/50 p-4">
            <div className="mb-3 rounded-lg bg-muted/50 p-3">
              <p className="text-xs font-medium text-muted-foreground">Account</p>
              <p className="text-lg font-bold">{user?.is_verified ? "Verified" : "Unverified"}</p>
            </div>
            <div className="mb-2 text-sm">
              <p className="font-medium">{user?.first_name || user?.username || "User"}</p>
              <p className="text-xs text-muted-foreground">{user?.email}</p>
            </div>
            <Button variant="outline" size="sm" onClick={handleLogout} className="w-full bg-transparent">
              <LogOut className="mr-2 h-4 w-4" />
              Logout
            </Button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col lg:pl-64">
        {/* Mobile header */}
        <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-border/50 bg-card px-4 lg:hidden">
          <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(true)}>
            <Menu className="h-5 w-5" />
          </Button>
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
              <TrendingUp className="h-5 w-5 text-primary-foreground" />
            </div>
            <h1 className="text-xl font-bold">Finora</h1>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1">{children}</main>
      </div>
    </div>
  )
}
