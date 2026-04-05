"use client"

import Link from "next/link"
import { usePathname, useRouter, useSearchParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { useMemo } from "react"

export function TopNav() {
  const pathname = usePathname()
  const router = useRouter()
  const search = useSearchParams()
  const user = search.get("user") || "Analyst"

  const links = useMemo(
    () => [
      { href: "/dashboard?user=" + encodeURIComponent(user), label: "Home" },
      { href: "/upload?user=" + encodeURIComponent(user), label: "Upload" },
      { href: "/reports?user=" + encodeURIComponent(user), label: "Reports" },
    ],
    [user],
  )

  return (
    <header className="sticky top-0 z-40 w-full">
      <div className="mx-auto max-w-6xl px-4 py-3">
        <div className="flex items-center justify-between rounded-xl border border-white/20 bg-slate-900/70 px-4 py-2 backdrop-blur supports-[backdrop-filter]:bg-slate-900/70">
          <Link href={"/dashboard?user=" + encodeURIComponent(user)} className="flex items-center gap-2">
            <svg aria-hidden="true" viewBox="0 0 24 24" className="h-8 w-8 text-white" fill="currentColor"><path d="M12 2.5c-.3 0-.6.06-.87.18l-6 2.5a1.5 1.5 0 0 0-.93 1.39V11c0 5.52 4.23 8.69 7.02 9.94.48.22 1.06.22 1.54 0C15.55 19.69 19.78 16.52 19.78 11V6.57a1.5 1.5 0 0 0-.93-1.39l-6-2.5c-.27-.12-.57-.18-.85-.18Z"></path><path d="M10.4 12.6l-1.6-1.6a1 1 0 1 0-1.4 1.42l2.3 2.3c.39.39 1.03.39 1.42 0l4.9-4.9a1 1 0 1 0-1.42-1.42l-4.2 4.2Z"></path></svg>
            <span className="font-semibold tracking-tight text-white">ResearchGuard</span>
          </Link>

          <nav aria-label="Main" className="flex flex-wrap items-center gap-1">
            {links.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                className={cn(
                  "rounded-lg px-3 py-2 text-sm font-medium text-white/80 transition-colors hover:text-white",
                  pathname.startsWith(l.href.split("?")[0]) && "text-white",
                )}
              >
                {l.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <span className="hidden text-sm text-white/80 md:inline">{user}</span>
            <Button
              variant="outline"
              className="border-white/50 bg-transparent text-white hover:bg-white/10"
              onClick={() => router.push("/")}
            >
              Logout
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}
