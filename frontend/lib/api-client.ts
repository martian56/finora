// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

// Debug: Log API base URL
if (typeof window !== 'undefined') {
  console.log('API Base URL:', API_BASE_URL)
}

// API Client with authentication
class ApiClient {
  private baseURL: string
  private token: string | null = null

  constructor(baseURL: string) {
    this.baseURL = baseURL
    this.token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
  }

  setToken(token: string | null) {
    this.token = token
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('access_token', token)
      } else {
        localStorage.removeItem('access_token')
      }
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    }

    if (this.token) {
      (headers as Record<string, string>).Authorization = `Bearer ${this.token}`
    }

    try {
      console.log(`Making request to: ${url}`)
      const response = await fetch(url, {
        ...options,
        headers,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        console.error(`API Error [${response.status}]:`, errorData)
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      return response.json()
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        console.error(`Network error connecting to: ${url}`)
        throw new Error(`Network error: Unable to connect to backend at ${url}. Make sure the Django server is running.`)
      }
      throw error
    }
  }

  // Authentication endpoints
  async login(email: string, password: string) {
    const data = await this.request<{ access: string; refresh: string }>('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    this.setToken(data.access)
    return data
  }

  async register(email: string, password: string, firstName?: string, lastName?: string) {
    const data = await this.request<{ access: string; refresh: string }>('/auth/register/', {
      method: 'POST',
      body: JSON.stringify({ 
        username: email, 
        email: email,
        password: password,
        confirm_password: password,
        first_name: firstName, 
        last_name: lastName 
      }),
    })
    this.setToken(data.access)
    return data
  }

  async refreshToken() {
    const refreshToken = typeof window !== 'undefined' ? localStorage.getItem('refresh_token') : null
    if (!refreshToken) throw new Error('No refresh token available')
    
    const data = await this.request<{ access: string }>('/auth/refresh/', {
      method: 'POST',
      body: JSON.stringify({ refresh: refreshToken }),
    })
    this.setToken(data.access)
    return data
  }

  async logout() {
    this.setToken(null)
    if (typeof window !== 'undefined') {
      localStorage.removeItem('refresh_token')
    }
  }

  // User endpoints
  async getCurrentUser() {
    return this.request<{
      id: number
      email: string
      username: string
      first_name?: string
      last_name?: string
      is_verified: boolean
      trading_enabled: boolean
      kyc_status: string
      created_at: string
    }>('/auth/profile/')
  }

  async updateProfile(data: { first_name?: string; last_name?: string }) {
    return this.request('/auth/profile/', {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  // Markets endpoints
  async getTradingPairs() {
    const response = await this.request<{ results: TradingPair[] }>('/markets/trading-pairs/')
    return response.results || []
  }

  async getMarketData(symbol: string) {
    return this.request<{
      symbol: string
      price: number
      change_24h: number
      change_percent_24h: number
      volume_24h: number
      high_24h: number
      low_24h: number
    }>(`/markets/ticker/${encodeURIComponent(symbol)}/`)
  }

  async getPriceHistory(pairId: number, timeframe: string = '1h') {
    return this.request<Array<{
      id: number
      trading_pair: number
      price: number
      volume: number
      timestamp: string
    }>>(`/markets/history/${pairId}/?timeframe=${timeframe}`)
  }

  // Trading endpoints
  async getOrders() {
    const response = await this.request<{ results: Order[] }>('/trading/orders/')
    return response.results || []
  }

  async placeOrder(data: {
    trading_pair: number
    order_type: 'market' | 'limit'
    side: 'buy' | 'sell'
    quantity: number
    price?: number
  }) {
    // Transform trading_pair to trading_pair_id for backend
    const payload = {
      trading_pair_id: data.trading_pair,
      order_type: data.order_type,
      side: data.side,
      quantity: data.quantity,
      price: data.price,
    }
    
    return this.request<Order>('/trading/orders/', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  }

  async cancelOrder(orderId: number) {
    return this.request(`/trading/orders/${orderId}/cancel/`, {
      method: 'POST',
    })
  }

  async getTrades() {
    const response = await this.request<{ results: Array<{
      id: number
      order: number
      quantity: number
      price: number
      timestamp: string
    }> }>('/trading/trades/')
    return response.results || []
  }

  // Wallet endpoints
  async getWallets() {
    const response = await this.request<{ results: Wallet[] }>('/wallets/')
    return response.results || []
  }

  async getTransactions() {
    const response = await this.request<{ results: Array<{
      id: number
      wallet: number
      transaction_type: 'deposit' | 'withdrawal' | 'trade' | 'transfer'
      amount: number
      balance_after: number
      description: string
      timestamp: string
    }> }>('/wallets/transactions/')
    return response.results || []
  }

  // API Keys endpoints
  async getApiKeys() {
    const response = await this.request<{ results: Array<{
      id: number
      name: string
      key: string
      secret: string
      permissions: string[]
      is_active: boolean
      created_at: string
      last_used?: string
    }> }>('/api-keys/')
    return response.results || []
  }

  async createApiKey(data: { name: string; permissions: string[] }) {
    return this.request<{
      id: number
      name: string
      key: string
      secret: string
      permissions: string[]
      is_active: boolean
      created_at: string
    }>('/api-keys/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async deleteApiKey(keyId: number) {
    return this.request(`/api-keys/${keyId}/`, {
      method: 'DELETE',
    })
  }
}

// Create singleton instance
export const apiClient = new ApiClient(API_BASE_URL)

// Export types
export type User = {
  id: number
  email: string
  username: string
  first_name?: string
  last_name?: string
  is_verified: boolean
  trading_enabled: boolean
  kyc_status: string
  created_at: string
}

export type TradingPair = {
  id: number
  symbol: string
  base_currency: { symbol: string; name: string }
  quote_currency: { symbol: string; name: string }
  market_type: 'spot' | 'futures'
  status: 'active' | 'inactive' | 'maintenance'
  min_order_size: number
  max_order_size: number
  price_precision: number
  quantity_precision: number
  maker_fee: number
  taker_fee: number
  created_at: string
  // Client-side fields for display
  price?: number
  change?: number
}

export type Order = {
  id: number
  trading_pair: TradingPair
  order_type: 'market' | 'limit'
  side: 'buy' | 'sell'
  quantity: number
  price?: number
  status: 'pending' | 'filled' | 'cancelled' | 'partial' | 'partial_filled'
  created_at: string
  updated_at: string
}

export type Wallet = {
  id: number
  currency: { symbol: string; name: string }
  balance: number
  frozen_balance: number
  available_balance: number
}
