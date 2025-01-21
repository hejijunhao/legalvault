// components/integrations/integrations-overview.tsx

"use client"

import { useState } from "react"
import { IntegrationCard } from "./integration-card"
import { CredentialModal } from "./credential-modal"

// Mock data for integrations
const integrations = [
  {
    id: "1",
    name: "Gmail",
    description: "Google Mail Integration",
    authType: "oauth2",
    iconUrl: "/placeholder.svg",
    isActive: false,
  },
  {
    id: "2",
    name: "Dropbox",
    description: "Cloud Storage Integration",
    authType: "oauth2",
    iconUrl: "/placeholder.svg",
    isActive: true,
  },
  // Add more integrations as needed
]

export function IntegrationsOverview() {
  const [selectedIntegration, setSelectedIntegration] = useState<(typeof integrations)[0] | null>(null)

  const handleActivate = (integration: (typeof integrations)[0]) => {
    setSelectedIntegration(integration)
  }

  const handleCloseModal = () => {
    setSelectedIntegration(null)
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-6 sm:grid-cols-1 md:grid-cols-2">
        {integrations.map((integration) => (
          <IntegrationCard
            key={integration.id}
            integration={integration}
            onActivate={() => handleActivate(integration)}
          />
        ))}
      </div>
      {selectedIntegration && <CredentialModal integration={selectedIntegration} onClose={handleCloseModal} />}
    </div>
  )
}

