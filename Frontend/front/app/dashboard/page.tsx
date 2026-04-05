"use client"

import { useEffect, useState } from "react"
import { TopNav } from "@/components/top-nav"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { Suspense } from "react"
import Link from "next/link"

type RecentItem = {
  id: number
  title: string
  filename: string
  status: string
  risk_score: number | null
  created_at: string | null
}

type DashboardStats = {
  user_name: string
  total_manuscripts: number
  avg_risk_score: number | null
  integrity_score: number | null
  recent_activity: RecentItem[]
}

function DashboardInner() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const token = localStorage.getItem("token")
        const res = await fetch("http://localhost:8000/dashboard/stats", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
        if (res.ok) {
          const data = await res.json()
          setStats(data)
        }
      } catch (err) {
        console.error("Failed to fetch dashboard stats:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  if (loading) {
    return (
      <div className="mx-auto w-full max-w-6xl px-4 py-8">
        <p className="text-white/70 animate-pulse text-lg">Loading dashboard...</p>
      </div>
    )
  }

  const statusBadgeVariant = (status: string) => {
    switch (status) {
      case "completed": return "secondary"
      case "analyzing": return "outline"
      default: return "outline"
    }
  }

  const statusLabel = (status: string) => {
    switch (status) {
      case "completed": return "Analyzed"
      case "analyzing": return "Analyzing..."
      default: return "Uploaded"
    }
  }

  const getRiskLabel = (score: number | null) => {
    if (score === null) return { text: "Pending", variant: "outline" as const }
    const riskPct = Math.round(score * 100)
    if (riskPct <= 30) return { text: "Low Risk", variant: "secondary" as const }
    if (riskPct <= 60) return { text: "Moderate", variant: "outline" as const }
    return { text: "High Risk", variant: "destructive" as const }
  }

  return (
    <div className="mx-auto w-full max-w-6xl px-4 py-8">
      <div className="mb-6">
        <h2 className="text-balance text-5xl font-semibold tracking-tight text-white">
          Welcome, {stats?.user_name || "Analyst"}
        </h2>
        <p className="text-lg text-gray-100/80">Your research integrity snapshots at a glance.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Integrity Risk Score Card */}
        <Card className="border-border bg-background/70 backdrop-blur">
          <CardHeader className="pb-2">
            <CardTitle className="text-2xl text-blue-900">Integrity Risk Score</CardTitle>
            <CardDescription className="text-lg text-blue-700/80">Average assessment</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-3">
              <div className="text-5xl font-bold tracking-tight text-black">
                {stats?.avg_risk_score !== null && stats?.avg_risk_score !== undefined
                  ? (stats.avg_risk_score * 100).toFixed(1) + "%"
                  : "—"}
              </div>
              {stats?.avg_risk_score !== null && stats?.avg_risk_score !== undefined && (
                <Badge
                  variant={getRiskLabel(stats.avg_risk_score).variant}
                  className="border-white/30 bg-white/10 text-blue-700"
                >
                  {getRiskLabel(stats.avg_risk_score).text}
                </Badge>
              )}
            </div>
            <Separator className="my-4" />
            <p className="text-m text-blue-700/80">
              This score aggregates CSAD, semantic consistency, and AI likelihood risk across all your manuscripts. Lower is better.
            </p>
          </CardContent>
        </Card>

        {/* Total Manuscripts Card */}
        <Card className="border-border bg-background/70 backdrop-blur">
          <CardHeader className="pb-2">
            <CardTitle className="text-2xl text-blue-900">Manuscripts</CardTitle>
            <CardDescription className="text-lg text-blue-700/80">Total uploaded</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-5xl font-bold tracking-tight text-black">
              {stats?.total_manuscripts ?? 0}
            </div>
            <Separator className="my-4" />
            <p className="text-m text-blue-700/80">
              Total research papers you have submitted for integrity analysis.
            </p>
          </CardContent>
        </Card>

        {/* Avg Risk Score Card */}
        <Card className="border-border bg-background/70 backdrop-blur">
          <CardHeader className="pb-2">
            <CardTitle className="text-2xl text-blue-900">Avg Risk Score</CardTitle>
            <CardDescription className="text-lg text-blue-700/80">Across all manuscripts</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-5xl font-bold tracking-tight text-black">
              {stats?.avg_risk_score !== null && stats?.avg_risk_score !== undefined
                ? (stats.avg_risk_score * 100).toFixed(1) + "%"
                : "—"}
            </div>
            <Separator className="my-4" />
            <p className="text-m text-blue-700/80">
              Lower risk score indicates better research integrity.
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="mt-6">
        <Card className="border-border bg-background/70 backdrop-blur">
          <CardHeader className="pb-2">
            <CardTitle className="text-2xl text-blue-900">Recent Activity</CardTitle>
            <CardDescription className="text-lg text-blue-700/80">Your latest uploads and analyses</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {stats?.recent_activity && stats.recent_activity.length > 0 ? (
              stats.recent_activity.map((item) => (
                <Link
                  key={item.id}
                  href={`/reports/${item.id}`}
                  className="flex items-center justify-between rounded-lg px-3 py-2 transition-colors hover:bg-blue-50/50"
                >
                  <div className="flex flex-col">
                    <span className="text-sm font-medium text-blue-900">{item.title}</span>
                    <span className="text-xs text-blue-700/60">{item.filename}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {item.risk_score !== null && (
                      <span className="text-xs text-blue-700/70 font-mono">
                        Risk: {(item.risk_score * 100).toFixed(1)}%
                      </span>
                    )}
                    <Badge className="border-white/30 text-blue-700" variant={statusBadgeVariant(item.status)}>
                      {statusLabel(item.status)}
                    </Badge>
                  </div>
                </Link>
              ))
            ) : (
              <p className="text-sm text-blue-700/60 py-4 text-center">
                No manuscripts uploaded yet. Start by uploading a PDF!
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  return (
    <main className="relative min-h-dvh bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/20 via-background to-background text-blue-700">
      <div className="absolute inset-0 -z-20" aria-hidden>
        <img
          src="/images/dashboard-bg-gemini-v3.png"
          alt=""
          className="h-full w-full object-cover opacity-70 md:opacity-80 brightness-125 saturate-150"
        />
      </div>
      <div className="absolute inset-0 -z-10 opacity-25" aria-hidden>
        <svg className="h-full w-full" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
              <circle cx="1" cy="1" r="1" className="fill-primary/30" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#dots)" />
        </svg>
      </div>

      <Suspense>
        <TopNav />
      </Suspense>
      <DashboardInner />
    </main>
  )
}
