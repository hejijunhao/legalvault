import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Building2, Globe, Mail, Phone, MapPin, Calendar, Briefcase, FileText, Users, Settings } from "lucide-react"

interface Address {
  street: string
  unit: string
  building: string
  city: string
  postal_code: string
  country: string
}

interface Contact {
  id: number
  name: string
  role: string
  email: string
}

interface Project {
  id: number
  name: string
  status: string
}

interface ClientProfileProps {
  client: {
    name: string
    legal_entity_type: string
    status: string
    domicile: string
    primary_email: string
    primary_phone: string
    address: Address
    client_join_date: string
    industry: string
    tax_id: string
    registration_number: string
    website: string
    client_profile: {
      summary: string
      last_updated: string
    }
    preferences: {
      communication_preference: string
      billing_currency: string
      language: string
      timezone: string
    }
    tags: string[]
    projects: Project[]
    contacts: Contact[]
  }
}

export function ClientProfile({ client }: ClientProfileProps) {
  return (
    <div className="grid gap-6 lg:grid-cols-[2fr,1fr]">
      {/* Main Content */}
      <div className="space-y-6">
        {/* Overview Card */}
        <Card className="p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-[#1C1C1C]">Overview</h2>
            <Badge variant="outline" className="bg-[#9FE870]/20 text-[#09332B]">
              {client.status.toUpperCase()}
            </Badge>
          </div>
          <div className="space-y-4">
            <p className="text-sm text-[#525766]">{client.client_profile.summary}</p>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="flex items-center gap-2">
                <Building2 className="h-4 w-4 text-[#8992A9]" />
                <span className="text-sm text-[#525766]">{client.legal_entity_type}</span>
              </div>
              <div className="flex items-center gap-2">
                <Globe className="h-4 w-4 text-[#8992A9]" />
                <a href={client.website} className="text-sm text-[#525766] hover:text-[#1C1C1C]">
                  {client.website}
                </a>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-[#8992A9]" />
                <span className="text-sm text-[#525766]">{client.primary_email}</span>
              </div>
              <div className="flex items-center gap-2">
                <Phone className="h-4 w-4 text-[#8992A9]" />
                <span className="text-sm text-[#525766]">{client.primary_phone}</span>
              </div>
            </div>
          </div>
        </Card>

        {/* Tabs Section */}
        <Tabs defaultValue="details" className="w-full">
          <TabsList className="w-full justify-start gap-2 rounded-none border-b bg-transparent p-0">
            {[
              { id: "details", label: "Details" },
              { id: "projects", label: "Projects" },
              { id: "contacts", label: "Contacts" },
              { id: "preferences", label: "Preferences" },
            ].map((tab) => (
              <TabsTrigger
                key={tab.id}
                value={tab.id}
                className="rounded-none border-b-2 border-transparent bg-transparent px-4 py-2 text-[#8992A9] hover:text-[#1C1C1C] data-[state=active]:border-[#1C1C1C] data-[state=active]:bg-transparent data-[state=active]:text-[#1C1C1C]"
              >
                {tab.label}
              </TabsTrigger>
            ))}
          </TabsList>

          <TabsContent value="details" className="mt-6">
            <Card className="p-6">
              <div className="grid gap-6 sm:grid-cols-2">
                <div className="space-y-4">
                  <h3 className="font-medium text-[#1C1C1C]">Business Information</h3>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-[#8992A9]" />
                      <span className="text-sm text-[#525766]">{client.domicile}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-[#8992A9]" />
                      <span className="text-sm text-[#525766]">
                        Client since {new Date(client.client_join_date).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Briefcase className="h-4 w-4 text-[#8992A9]" />
                      <span className="text-sm text-[#525766]">{client.industry}</span>
                    </div>
                  </div>
                </div>
                <div className="space-y-4">
                  <h3 className="font-medium text-[#1C1C1C]">Registration Details</h3>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-[#8992A9]" />
                      <span className="text-sm text-[#525766]">Tax ID: {client.tax_id}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-[#8992A9]" />
                      <span className="text-sm text-[#525766]">Reg. No: {client.registration_number}</span>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="projects" className="mt-6">
            <Card className="p-6">
              <div className="space-y-4">
                {client.projects.map((project) => (
                  <div key={project.id} className="flex items-center justify-between rounded-lg border p-4">
                    <span className="font-medium text-[#1C1C1C]">{project.name}</span>
                    <Badge variant="outline" className="bg-[#9FE870]/20 text-[#09332B]">
                      {project.status}
                    </Badge>
                  </div>
                ))}
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="contacts" className="mt-6">
            <Card className="p-6">
              <div className="space-y-4">
                {client.contacts.map((contact) => (
                  <div key={contact.id} className="flex items-center justify-between rounded-lg border p-4">
                    <div className="space-y-1">
                      <div className="font-medium text-[#1C1C1C]">{contact.name}</div>
                      <div className="text-sm text-[#525766]">{contact.role}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Mail className="h-4 w-4 text-[#8992A9]" />
                      <span className="text-sm text-[#525766]">{contact.email}</span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </TabsContent>

          <TabsContent value="preferences" className="mt-6">
            <Card className="p-6">
              <div className="space-y-6">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <div className="font-medium text-[#1C1C1C]">Communication</div>
                    <div className="flex items-center gap-2">
                      <Settings className="h-4 w-4 text-[#8992A9]" />
                      <span className="text-sm capitalize text-[#525766]">
                        {client.preferences.communication_preference}
                      </span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="font-medium text-[#1C1C1C]">Billing Currency</div>
                    <div className="flex items-center gap-2">
                      <Settings className="h-4 w-4 text-[#8992A9]" />
                      <span className="text-sm text-[#525766]">{client.preferences.billing_currency}</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="font-medium text-[#1C1C1C]">Language</div>
                    <div className="flex items-center gap-2">
                      <Settings className="h-4 w-4 text-[#8992A9]" />
                      <span className="text-sm uppercase text-[#525766]">{client.preferences.language}</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="font-medium text-[#1C1C1C]">Timezone</div>
                    <div className="flex items-center gap-2">
                      <Settings className="h-4 w-4 text-[#8992A9]" />
                      <span className="text-sm text-[#525766]">{client.preferences.timezone}</span>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Sidebar */}
      <div className="space-y-6">
        {/* Address Card */}
        <Card className="p-6">
          <h3 className="mb-4 font-medium text-[#1C1C1C]">Address</h3>
          <div className="space-y-2 text-sm text-[#525766]">
            <p>{client.address.unit}</p>
            <p>{client.address.building}</p>
            <p>{client.address.street}</p>
            <p>
              {client.address.city} {client.address.postal_code}
            </p>
            <p>{client.address.country}</p>
          </div>
        </Card>

        {/* Tags Card */}
        <Card className="p-6">
          <h3 className="mb-4 font-medium text-[#1C1C1C]">Tags</h3>
          <div className="flex flex-wrap gap-2">
            {client.tags.map((tag) => (
              <Badge key={tag} variant="outline" className="bg-[rgba(191,219,254,0.20)] text-[#525766]">
                {tag}
              </Badge>
            ))}
          </div>
        </Card>

        {/* Key Contacts Card */}
        <Card className="p-6">
          <h3 className="mb-4 font-medium text-[#1C1C1C]">Key Contacts</h3>
          <div className="space-y-4">
            {client.contacts.slice(0, 2).map((contact) => (
              <div key={contact.id} className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-[#1C1C1C]">{contact.name}</div>
                  <div className="text-sm text-[#525766]">{contact.role}</div>
                </div>
                <Users className="h-4 w-4 text-[#8992A9]" />
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}