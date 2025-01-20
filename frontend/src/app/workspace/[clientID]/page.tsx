import { ClientProfile } from "@/components/workspace/client/client-profile"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

// This will be replaced with real data fetching
const getDummyClient = (clientId: string) => {
  return {
    name: "Aurora Solutions",
    legal_entity_type: "corporation",
    status: "active",
    domicile: "Singapore",
    primary_email: "contact@aurorasolutions.com",
    primary_phone: "+65 6789 0123",
    address: {
      street: "71 Robinson Road",
      unit: "#14-01",
      building: "Singapore Land Tower",
      city: "Singapore",
      postal_code: "068895",
      country: "Singapore",
    },
    client_join_date: "2023-01-15T00:00:00Z",
    industry: "Technology",
    tax_id: "T23LC0123456K",
    registration_number: "202312345K",
    website: "https://aurorasolutions.com",
    client_profile: {
      summary:
        "Aurora Solutions is a leading technology company specializing in AI and machine learning solutions for the financial services industry. They have been at the forefront of developing innovative solutions for risk assessment and automated trading systems.",
      last_updated: "2024-01-20T08:00:00Z",
    },
    preferences: {
      communication_preference: "email",
      billing_currency: "SGD",
      language: "en",
      timezone: "Asia/Singapore",
    },
    tags: ["Technology", "AI/ML", "Financial Services", "Enterprise"],
    projects: [
      { id: 1, name: "Project Greenbridge", status: "ACTIVE" },
      { id: 2, name: "Project Norse", status: "PLANNING" },
    ],
    contacts: [
      { id: 1, name: "Sarah Chen", role: "CEO", email: "sarah.chen@aurorasolutions.com" },
      { id: 2, name: "Michael Wong", role: "Legal Counsel", email: "michael.wong@aurorasolutions.com" },
    ],
  }
}

export default function ClientPage({ params }: { params: { clientId: string } }) {
  const client = getDummyClient(params.clientId)

  return (
    <div className="mx-auto w-full max-w-[1440px] space-y-6 py-6">
      {/* Back Navigation and Title */}
      <div className="flex flex-col gap-4">
        <div className="flex justify-between items-center self-stretch">
          <Link href="/workspace" className="flex items-center gap-1.5 rounded-[5px] px-2 py-1 hover:bg-black/5">
            <ArrowLeft className="h-3 w-3 text-[#1C1C1C]" />
            <span className="text-xs text-[#1C1C1C]">All Clients</span>
          </Link>
        </div>
        <h1 className="flex h-11 flex-1 flex-col justify-center text-[32px] font-normal italic leading-6 text-[#111827] font-['Libre_Baskerville']">
          {client.name}
        </h1>
      </div>

      <ClientProfile client={client} />
    </div>
  )
}