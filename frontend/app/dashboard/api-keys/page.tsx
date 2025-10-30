"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Key, Copy, Trash2, Eye, EyeOff, Plus, AlertTriangle } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { useApiKeys } from "@/hooks/use-trading"

interface ApiKey {
  id: string
  name: string
  key: string
  secret: string
  permissions: {
    spot: boolean
    futures: boolean
    withdraw: boolean
  }
  createdAt: Date
  lastUsed?: Date
}

export default function ApiKeysPage() {
  const router = useRouter()
  const { user, isLoading } = useAuth()
  const { toast } = useToast()
  const { apiKeys, isLoading: apiKeysLoading, createApiKey, deleteApiKey } = useApiKeys()
  
  const [showSecret, setShowSecret] = useState<{ [key: string]: boolean }>({})
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [newKeyName, setNewKeyName] = useState("")
  const [newKeyPermissions, setNewKeyPermissions] = useState({
    spot: true,
    futures: false,
    withdraw: false,
  })
  const [newlyCreatedKey, setNewlyCreatedKey] = useState<ApiKey | null>(null)

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login")
    }
  }, [user, isLoading, router])

  if (isLoading || !user || apiKeysLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <span className="text-lg text-muted-foreground">Loading...</span>
        </div>
      </div>
    )
  }

  const generateRandomString = (length: number) => {
    const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    let result = ""
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    return result
  }

  const handleCreateApiKey = async () => {
    if (!newKeyName.trim()) {
      toast({
        title: "Invalid Name",
        description: "Please enter a name for your API key",
        variant: "destructive",
      })
      return
    }

    try {
      const permissions = []
      if (newKeyPermissions.spot) permissions.push("spot")
      if (newKeyPermissions.futures) permissions.push("futures")
      if (newKeyPermissions.withdraw) permissions.push("withdraw")

      const newKey = await createApiKey({ name: newKeyName, permissions })
      setNewlyCreatedKey(newKey)
      setNewKeyName("")
      setNewKeyPermissions({ spot: true, futures: false, withdraw: false })
      setIsCreateDialogOpen(false)
    } catch (error) {
      // Error is already handled in the hook
    }
  }

  const handleDeleteApiKey = async (id: string) => {
    try {
      await deleteApiKey(parseInt(id))
    } catch (error) {
      // Error is already handled in the hook
    }
  }

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text)
    toast({
      title: "Copied",
      description: `${label} copied to clipboard`,
    })
  }

  const toggleShowSecret = (id: string) => {
    setShowSecret((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold">API Key Management</h2>
            <p className="text-muted-foreground">Create and manage API keys for programmatic trading</p>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Create API Key
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New API Key</DialogTitle>
                <DialogDescription>
                  Generate a new API key for programmatic access to your account. Choose permissions carefully.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div>
                  <Label htmlFor="keyName">API Key Name</Label>
                  <Input
                    id="keyName"
                    placeholder="e.g., Trading Bot"
                    value={newKeyName}
                    onChange={(e) => setNewKeyName(e.target.value)}
                    className="mt-1"
                  />
                </div>
                <div>
                  <Label className="mb-3 block">Permissions</Label>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="spot"
                        checked={newKeyPermissions.spot}
                        onCheckedChange={(checked) =>
                          setNewKeyPermissions({ ...newKeyPermissions, spot: checked as boolean })
                        }
                      />
                      <label
                        htmlFor="spot"
                        className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                      >
                        Spot Trading
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="futures"
                        checked={newKeyPermissions.futures}
                        onCheckedChange={(checked) =>
                          setNewKeyPermissions({ ...newKeyPermissions, futures: checked as boolean })
                        }
                      />
                      <label
                        htmlFor="futures"
                        className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                      >
                        Futures Trading
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="withdraw"
                        checked={newKeyPermissions.withdraw}
                        onCheckedChange={(checked) =>
                          setNewKeyPermissions({ ...newKeyPermissions, withdraw: checked as boolean })
                        }
                      />
                      <label
                        htmlFor="withdraw"
                        className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                      >
                        Withdraw (High Risk)
                      </label>
                    </div>
                  </div>
                </div>
              </div>
              <Button onClick={handleCreateApiKey} className="w-full">
                Generate API Key
              </Button>
            </DialogContent>
          </Dialog>
        </div>

        {/* Warning banner */}
        <Card className="mb-6 border-destructive/50 bg-destructive/10">
          <CardContent className="flex items-start gap-3 p-4">
            <AlertTriangle className="mt-0.5 h-5 w-5 text-destructive" />
            <div className="flex-1">
              <p className="font-medium text-destructive">Security Warning</p>
              <p className="text-sm text-muted-foreground">
                Never share your API keys or secret keys with anyone. Store them securely and rotate them regularly.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Newly created key display */}
        {newlyCreatedKey && (
          <Card className="mb-6 border-primary/50 bg-primary/10">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Key className="h-5 w-5" />
                New API Key Created
              </CardTitle>
              <CardDescription>
                Save your secret key now. You won't be able to see it again after closing this message.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <Label className="text-xs text-muted-foreground">API Key</Label>
                <div className="mt-1 flex items-center gap-2">
                  <Input value={newlyCreatedKey.key} readOnly className="font-mono text-sm" />
                  <Button size="icon" variant="outline" onClick={() => copyToClipboard(newlyCreatedKey.key, "API Key")}>
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <div>
                <Label className="text-xs text-muted-foreground">Secret Key</Label>
                <div className="mt-1 flex items-center gap-2">
                  <Input value={newlyCreatedKey.secret} readOnly className="font-mono text-sm" />
                  <Button
                    size="icon"
                    variant="outline"
                    onClick={() => copyToClipboard(newlyCreatedKey.secret, "Secret Key")}
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <Button variant="outline" onClick={() => setNewlyCreatedKey(null)} className="w-full">
                I've Saved My Keys
              </Button>
            </CardContent>
          </Card>
        )}

        {/* API Keys list */}
        {!Array.isArray(apiKeys) || apiKeys.length === 0 ? (
          <Card className="border-border/50">
            <CardContent className="flex h-64 flex-col items-center justify-center">
              <Key className="mb-4 h-12 w-12 text-muted-foreground" />
              <p className="mb-2 text-lg font-medium">No API Keys</p>
              <p className="mb-4 text-sm text-muted-foreground">Create your first API key to get started</p>
              <Button onClick={() => setIsCreateDialogOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Create API Key
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {apiKeys.map((apiKey) => (
              <Card key={apiKey.id} className="border-border/50">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{apiKey.name}</CardTitle>
                      <CardDescription>
                        Created {new Date(apiKey.created_at).toLocaleDateString()} at {new Date(apiKey.created_at).toLocaleTimeString()}
                      </CardDescription>
                    </div>
                    <Button
                      size="icon"
                      variant="ghost"
                      onClick={() => handleDeleteApiKey(apiKey.id.toString())}
                      className="text-destructive hover:bg-destructive/10 hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label className="text-xs text-muted-foreground">API Key</Label>
                    <div className="mt-1 flex items-center gap-2">
                      <Input value={apiKey.key} readOnly className="font-mono text-sm" />
                      <Button size="icon" variant="outline" onClick={() => copyToClipboard(apiKey.key, "API Key")}>
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  <div>
                    <Label className="text-xs text-muted-foreground">Secret Key</Label>
                    <div className="mt-1 flex items-center gap-2">
                      <Input
                        type={showSecret[apiKey.id] ? "text" : "password"}
                        value={apiKey.secret}
                        readOnly
                        className="font-mono text-sm"
                      />
                      <Button size="icon" variant="outline" onClick={() => toggleShowSecret(apiKey.id.toString())}>
                        {showSecret[apiKey.id] ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                      <Button
                        size="icon"
                        variant="outline"
                        onClick={() => copyToClipboard(apiKey.secret, "Secret Key")}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  <div>
                    <Label className="mb-2 block text-xs text-muted-foreground">Permissions</Label>
                    <div className="flex flex-wrap gap-2">
                      {apiKey.permissions.map((permission) => (
                        <span
                          key={permission}
                          className="rounded-full bg-primary/20 px-2 py-1 text-xs font-medium text-primary"
                        >
                          {permission}
                        </span>
                      ))}
                    </div>
                  </div>
                  {apiKey.last_used && (
                    <div className="text-xs text-muted-foreground">
                      Last used: {new Date(apiKey.last_used).toLocaleDateString()} at {new Date(apiKey.last_used).toLocaleTimeString()}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
