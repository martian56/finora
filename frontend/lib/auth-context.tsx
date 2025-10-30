"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { apiClient, type User } from "@/lib/api-client"

interface AuthContextType {
  user: User | null
  login: (email: string, password: string) => Promise<boolean>
  register: (email: string, password: string, firstName?: string, lastName?: string) => Promise<boolean>
  logout: () => void
  isLoading: boolean
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check for existing session
    const token = localStorage.getItem("access_token")
    if (token) {
      apiClient.setToken(token)
      refreshUser()
    } else {
      setIsLoading(false)
    }
  }, [])

  const refreshUser = async () => {
    try {
      const userData = await apiClient.getCurrentUser()
      setUser(userData)
    } catch (error) {
      console.error("Failed to refresh user:", error)
      // Token might be expired, try to refresh
      try {
        await apiClient.refreshToken()
        const userData = await apiClient.getCurrentUser()
        setUser(userData)
      } catch (refreshError) {
        console.error("Failed to refresh token:", refreshError)
        // Clear invalid tokens
        apiClient.logout()
        setUser(null)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (email: string, password: string, firstName?: string, lastName?: string): Promise<boolean> => {
    try {
      const response = await apiClient.register(email, password, firstName, lastName)
      
      // Store refresh token
      if (typeof window !== 'undefined') {
        localStorage.setItem("refresh_token", response.refresh)
      }
      
      // Get user data
      await refreshUser()
      return true
    } catch (error) {
      console.error("Registration error:", error)
      return false
    }
  }

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const response = await apiClient.login(email, password)
      
      // Store refresh token
      if (typeof window !== 'undefined') {
        localStorage.setItem("refresh_token", response.refresh)
      }
      
      // Get user data
      await refreshUser()
      return true
    } catch (error) {
      console.error("Login error:", error)
      return false
    }
  }

  const logout = () => {
    apiClient.logout()
    setUser(null)
  }

  return <AuthContext.Provider value={{ user, login, register, logout, isLoading, refreshUser }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
