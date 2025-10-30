"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { X } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

export function Toaster() {
  const { toasts, dismiss } = useToast()

  return (
    <div className="fixed top-0 z-[100] flex max-h-screen w-full flex-col-reverse p-4 sm:bottom-0 sm:right-0 sm:top-auto sm:flex-col md:max-w-[420px]">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={cn(
            "group pointer-events-auto relative flex w-full items-center justify-between space-x-4 overflow-hidden rounded-md border p-6 pr-8 shadow-lg transition-all",
            "bg-background text-foreground",
            toast.variant === "destructive" && "border-destructive bg-destructive text-destructive-foreground"
          )}
        >
          <div className="grid gap-1">
            {toast.title && <div className="text-sm font-semibold">{toast.title}</div>}
            {toast.description && (
              <div className="text-sm opacity-90">{toast.description}</div>
            )}
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="absolute right-2 top-2 h-6 w-6 rounded-md opacity-0 transition-opacity hover:text-foreground focus:opacity-100 focus:outline-none focus:ring-2 group-hover:opacity-100"
            onClick={() => dismiss(toast.id)}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      ))}
    </div>
  )
}
