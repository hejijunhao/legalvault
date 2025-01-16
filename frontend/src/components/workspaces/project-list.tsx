// src/components/workspaces/project-list.tsx

"use client"

import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area"
import Link from "next/link"

const projects = [
  {
    id: 1,
    name: "Project Greenbridge",
    status: "LIVE M&A DEAL",
    background: "from-[#9FE870]/20 to-[#BFE999]/20",
    href: "/project-greenbridge"
  },
  {
    id: 2,
    name: "Adams v. Sculley",
    status: "LIVE LITIGATION",
    background: "from-[#AF52DE]/20 to-[#E5A4FF]/20",
    href: "/adams-v-sculley"
  },
  {
    id: 3,
    name: "Project Sparta",
    status: "LIVE M&A DEAL",
    background: "from-[#FF9B9B]/20 to-[#FFC4C4]/20",
    href: "/project-sparta"
  },
  {
    id: 4,
    name: "JCLim v. PHenley",
    status: "LIVE LITIGATION",
    background: "from-[#00C7BE]/20 to-[#7DEAE5]/20",
    href: "/jclim-v-phenley"
  },
  {
    id: 5,
    name: "Project Norse",
    status: "LIVE S&P DEAL",
    background: "from-[#93C5FD]/20 to-[#BFDBFE]/20",
    href: "/project-norse"
  }
]

export function ProjectList() {
  return (
    <div className="flex h-[268px] w-full items-center gap-[15px] self-stretch overflow-x-auto">
      <ScrollArea className="w-full">
        <div className="flex space-x-4 p-1">
          {projects.map((project) => (
            <Link key={project.id} href={project.href}>
              <div
                className={`flex h-[250px] w-[200px] cursor-pointer flex-col justify-end rounded-[10px] border border-white/10 bg-gradient-to-br p-[0px_10px_10px_10px] backdrop-blur-[17.7px] transition-all duration-500 ease-in-out hover:w-[395px] hover:bg-white/23 ${project.background}`}
              >
                <div className="space-y-1 transition-all duration-500 ease-in-out hover:gap-[15px]">
                  <h3 className="font-medium text-[#1C1C1C] italic font-['Libre_Baskerville']">
                    {project.name}
                  </h3>
                  <p className="text-xs text-[#525766]">{project.status}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
        <ScrollBar orientation="horizontal" />
      </ScrollArea>
    </div>
  )
}