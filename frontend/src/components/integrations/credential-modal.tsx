// components/integrations/credential-modal.tsx

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface CredentialModalProps {
  integration: {
    id: string
    name: string
    authType: string
  }
  onClose: () => void
}

export function CredentialModal({ integration, onClose }: CredentialModalProps) {
  const [credentials, setCredentials] = useState<Record<string, string>>({})

  const handleInputChange = (key: string, value: string) => {
    setCredentials((prev) => ({ ...prev, [key]: value }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Here you would typically send the credentials to your backend
    console.log("Submitting credentials:", credentials)
    onClose()
  }

  const renderFields = () => {
    switch (integration.authType) {
      case "oauth2":
        return (
          <>
            <Label htmlFor="client_id">Client ID</Label>
            <Input
              id="client_id"
              value={credentials.client_id || ""}
              onChange={(e) => handleInputChange("client_id", e.target.value)}
            />
            <Label htmlFor="client_secret">Client Secret</Label>
            <Input
              id="client_secret"
              type="password"
              value={credentials.client_secret || ""}
              onChange={(e) => handleInputChange("client_secret", e.target.value)}
            />
          </>
        )
      case "api_key":
        return (
          <>
            <Label htmlFor="api_key">API Key</Label>
            <Input
              id="api_key"
              type="password"
              value={credentials.api_key || ""}
              onChange={(e) => handleInputChange("api_key", e.target.value)}
            />
          </>
        )
      case "basic":
        return (
          <>
            <Label htmlFor="username">Username</Label>
            <Input
              id="username"
              value={credentials.username || ""}
              onChange={(e) => handleInputChange("username", e.target.value)}
            />
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              value={credentials.password || ""}
              onChange={(e) => handleInputChange("password", e.target.value)}
            />
          </>
        )
      default:
        return null
    }
  }

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Activate {integration.name}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          {renderFields()}
          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit">Activate</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}



