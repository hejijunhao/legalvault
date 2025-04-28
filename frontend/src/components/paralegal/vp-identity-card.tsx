// src/components/paralegal/vp-identity-card.tsx

import Image from "next/image"
import { Card } from "@/components/ui/card"
import { Shield, Mail, Phone, Calendar } from "lucide-react"
import { VirtualParalegalResponse } from "@/services/paralegal/paralegal-api-types"
import { format } from "date-fns"

interface VPIdentityCardProps {
  paralegal: VirtualParalegalResponse
}

export function VPIdentityCard({ paralegal }: VPIdentityCardProps) {
  return (
    <div className="grid gap-6 md:grid-cols-[400px_1fr]">
      {/* Identity Card */}
      <Card className="relative overflow-hidden rounded-3xl border-none h-[250px] group">
        {/* Elegant gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/90 via-teal-500/80 to-cyan-500/90">
          <div className="absolute inset-0 bg-[url('/textures/paper.png')] opacity-[0.03] mix-blend-overlay" />
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shimmer" />
          <div className="absolute inset-0">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.1),transparent_70%)]" />
            <div className="absolute inset-0 bg-[linear-gradient(45deg,transparent,rgba(255,255,255,0.1)_50%,transparent)] animate-pulse" />
          </div>
        </div>

        <div className="absolute inset-0 backdrop-blur-[2px] bg-black/5" />

        {/* Card Content */}
        <div className="relative h-full p-6 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 relative">
                <LegalVaultLogo />
                <div className="absolute inset-0 blur-sm opacity-50 animate-pulse" />
              </div>
              <span className="text-white/90 text-sm font-medium tracking-wide uppercase">Virtual Paralegal</span>
            </div>
            <Shield className="w-5 h-5 text-white/80" />
          </div>

          <div className="space-y-4">
            <div>
              <h2 className="text-white font-semibold text-2xl tracking-tight">
                {paralegal.first_name} {paralegal.last_name}
              </h2>
              {paralegal.email && (
                <div className="flex items-center space-x-2 text-white/90 text-sm mt-2">
                  <Mail className="w-4 h-4" />
                  <span>{paralegal.email}</span>
                </div>
              )}
              {paralegal.phone && (
                <div className="flex items-center space-x-2 text-white/90 text-sm mt-1.5">
                  <Phone className="w-4 h-4" />
                  <span>{paralegal.phone}</span>
                </div>
              )}
            </div>
          </div>

          {/* Holographic effect */}
          <div className="absolute bottom-0 right-0 w-32 h-32 bg-gradient-to-tr from-white/20 to-transparent rounded-tl-full opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        </div>
      </Card>

      {/* Profile Details */}
      <div className="space-y-8">
        <div>
          <h3 className="font-['Libre_Baskerville'] text-xl text-gray-900 italic mb-4">Profile Details</h3>
          <dl className="grid gap-6 text-sm">
            <div className="flex items-start space-x-4 text-gray-600">
              <Calendar className="w-5 h-5 mt-0.5" />
              <div>
                <dt className="font-medium text-gray-900">Date Joined</dt>
                <dd>{format(new Date(paralegal.created_at), "MMMM d, yyyy")}</dd>
              </div>
            </div>
            {paralegal.whatsapp && (
              <div className="flex items-start space-x-4 text-gray-600">
                <svg className="w-5 h-5 mt-0.5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12.012 2c-5.506 0-9.989 4.478-9.99 9.984a9.964 9.964 0 001.333 4.993L2 22l5.233-1.237a9.981 9.981 0 004.779 1.217h.004c5.505 0 9.988-4.478 9.988-9.984 0-2.669-1.037-5.176-2.922-7.062A9.932 9.932 0 0012.012 2zm-.004 2c2.295 0 4.446.894 6.062 2.51a8.518 8.518 0 012.51 6.062c-.001 4.723-3.846 8.566-8.57 8.566a8.563 8.563 0 01-4.277-1.144l-.301-.18-3.182.75.77-2.822-.197-.312a8.534 8.534 0 01-1.172-4.306c0-4.723 3.844-8.567 8.567-8.567zm0 2c-3.641 0-6.567 2.926-6.567 6.567 0 1.278.37 2.463 1.002 3.47l.153.232-.649 2.368 2.449-.578.243.145a6.518 6.518 0 003.37.93h.002c3.641 0 6.566-2.926 6.566-6.567s-2.925-6.567-6.566-6.567z"/>
                </svg>
                <div>
                  <dt className="font-medium text-gray-900">WhatsApp</dt>
                  <dd>{paralegal.whatsapp}</dd>
                </div>
              </div>
            )}
            {paralegal.gender && (
              <div className="flex items-start space-x-4 text-gray-600">
                <svg className="w-5 h-5 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 12a6 6 0 100 12 6 6 0 000-12z M15 9V3h6 M21 3l-6 6"/>
                </svg>
                <div>
                  <dt className="font-medium text-gray-900">Gender</dt>
                  <dd className="capitalize">{paralegal.gender}</dd>
                </div>
              </div>
            )}
          </dl>
        </div>
      </div>
    </div>
  )
}

function LegalVaultLogo() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="w-full h-full text-white"
    >
      <path
        d="M12 2L2 7V17L12 22L22 17V7L12 2Z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}