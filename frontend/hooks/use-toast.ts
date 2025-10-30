"use client"

import * as React from "react"

interface Toast {
  id: string
  title?: string
  description?: string
  variant?: "default" | "destructive"
}

interface ToastContextType {
  toasts: Toast[]
  toast: (toast: Omit<Toast, "id">) => void
  dismiss: (id: string) => void
}

const ToastContext = React.createContext<ToastContextType | undefined>(undefined)

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<Toast[]>([])

  const toast = React.useCallback((toastData: Omit<Toast, "id">) => {
    const id = Math.random().toString(36).substr(2, 9)
    const newToast = { ...toastData, id }
    setToasts((prev) => [...prev, newToast])
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 5000)
  }, [])

  const dismiss = React.useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const contextValue = React.useMemo(() => ({
    toasts,
    toast,
    dismiss
  }), [toasts, toast, dismiss])

  return React.createElement(
    ToastContext.Provider,
    { value: contextValue },
    children
  )
}

export function useToast() {
  const context = React.useContext(ToastContext)
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider")
  }
  return context
}