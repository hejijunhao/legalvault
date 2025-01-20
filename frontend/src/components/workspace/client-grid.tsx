import Image from "next/image"
import Link from "next/link"

const clients = [
  {
    id: 1,
    name: "Aurora Solutions",
    type: "CLIENT",
    logo: "/placeholder.svg",
  },
  {
    id: 2,
    name: "Elysian Ventures",
    type: "CLIENT",
    logo: "/placeholder.svg",
  },
  {
    id: 3,
    name: "Kronos Manufacturing",
    type: "CLIENT",
    logo: "/placeholder.svg",
  },
  {
    id: 4,
    name: "PureDelta Healthcare",
    type: "CLIENT",
    logo: "/placeholder.svg",
  },
  {
    id: 5,
    name: "Redwood Innovations",
    type: "CLIENT",
    logo: "/placeholder.svg",
  },
  {
    id: 6,
    name: "Silverstone Logistics",
    type: "CLIENT",
    logo: "/placeholder.svg",
  },
]

export function ClientGrid() {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
      {clients.map((client) => (
        <Link
          key={client.id}
          href={`/workspace/client/${client.id}`}
          className="flex h-[202px] flex-1 cursor-pointer flex-col items-center justify-center gap-4 rounded-[4px] bg-white/15 p-4 shadow-[0px_4px_15px_0px_rgba(0,0,0,0.05)] transition-all hover:scale-[1.02]"
        >
          <div className="relative h-24 w-24 overflow-hidden rounded-full">
            <Image
              src={client.logo || "/placeholder.svg"}
              alt={client.name}
              width={96}
              height={96}
              className="object-cover"
            />
          </div>
          <div className="text-center">
            <h3 className="text-sm font-medium text-[#1C1C1C]">{client.name}</h3>
            <p className="text-xs text-[#525766]">{client.type}</p>
          </div>
        </Link>
      ))}
    </div>
  )
}