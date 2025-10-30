"use client"

import { useState, useEffect } from "react"
import { apiClient, type TradingPair, type Order, type Wallet } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"

export function useTradingPairs() {
  const [pairs, setPairs] = useState<TradingPair[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchPairs = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const data = await apiClient.getTradingPairs()
        setPairs(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch trading pairs')
      } finally {
        setIsLoading(false)
      }
    }

    fetchPairs()
  }, [])

  return { pairs, isLoading, error, refetch: () => {
    const fetchPairs = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const data = await apiClient.getTradingPairs()
        setPairs(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch trading pairs')
      } finally {
        setIsLoading(false)
      }
    }
    fetchPairs()
  }}
}

export function useOrders() {
  const [orders, setOrders] = useState<Order[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { toast } = useToast()

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const data = await apiClient.getOrders()
        setOrders(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch orders')
      } finally {
        setIsLoading(false)
      }
    }

    fetchOrders()
  }, [])

  const placeOrder = async (orderData: {
    trading_pair: number
    order_type: 'market' | 'limit'
    side: 'buy' | 'sell'
    quantity: number
    price?: number
  }) => {
    try {
      const newOrder = await apiClient.placeOrder(orderData)
      setOrders(prev => [newOrder, ...prev])
      toast({
        title: "Order Placed",
        description: `${orderData.side.toUpperCase()} order placed successfully`,
      })
      return newOrder
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to place order'
      toast({
        title: "Order Failed",
        description: errorMessage,
        variant: "destructive",
      })
      throw err
    }
  }

  const cancelOrder = async (orderId: number) => {
    try {
      await apiClient.cancelOrder(orderId)
      setOrders(prev => prev.map(order => 
        order.id === orderId ? { ...order, status: 'cancelled' as const } : order
      ))
      toast({
        title: "Order Cancelled",
        description: "Order has been cancelled successfully",
      })
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to cancel order'
      toast({
        title: "Cancel Failed",
        description: errorMessage,
        variant: "destructive",
      })
      throw err
    }
  }

  return { 
    orders, 
    isLoading, 
    error, 
    placeOrder, 
    cancelOrder,
    refetch: async () => {
      try {
        setIsLoading(true)
        setError(null)
        const data = await apiClient.getOrders()
        setOrders(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch orders')
      } finally {
        setIsLoading(false)
      }
    }
  }
}

export function useWallets() {
  const [wallets, setWallets] = useState<Wallet[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchWallets = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const data = await apiClient.getWallets()
        setWallets(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch wallets')
      } finally {
        setIsLoading(false)
      }
    }

    fetchWallets()
  }, [])

  return { 
    wallets, 
    isLoading, 
    error,
    refetch: async () => {
      try {
        setIsLoading(true)
        setError(null)
        const data = await apiClient.getWallets()
        setWallets(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch wallets')
      } finally {
        setIsLoading(false)
      }
    }
  }
}

export function useApiKeys() {
  const [apiKeys, setApiKeys] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { toast } = useToast()

  useEffect(() => {
    const fetchApiKeys = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const data = await apiClient.getApiKeys()
        setApiKeys(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch API keys')
      } finally {
        setIsLoading(false)
      }
    }

    fetchApiKeys()
  }, [])

  const createApiKey = async (data: { name: string; permissions: string[] }) => {
    try {
      const newKey = await apiClient.createApiKey(data)
      setApiKeys(prev => [...prev, newKey])
      toast({
        title: "API Key Created",
        description: "New API key has been created successfully",
      })
      return newKey
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create API key'
      toast({
        title: "Creation Failed",
        description: errorMessage,
        variant: "destructive",
      })
      throw err
    }
  }

  const deleteApiKey = async (keyId: number) => {
    try {
      await apiClient.deleteApiKey(keyId)
      setApiKeys(prev => prev.filter(key => key.id !== keyId))
      toast({
        title: "API Key Deleted",
        description: "API key has been deleted successfully",
      })
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete API key'
      toast({
        title: "Deletion Failed",
        description: errorMessage,
        variant: "destructive",
      })
      throw err
    }
  }

  return { 
    apiKeys, 
    isLoading, 
    error, 
    createApiKey, 
    deleteApiKey,
    refetch: async () => {
      try {
        setIsLoading(true)
        setError(null)
        const data = await apiClient.getApiKeys()
        setApiKeys(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch API keys')
      } finally {
        setIsLoading(false)
      }
    }
  }
}
