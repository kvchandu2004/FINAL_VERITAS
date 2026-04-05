"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { TopNav } from "@/components/top-nav"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { IntegrityBarChart } from "@/components/charts/integrity-bar-chart"
import { ClaimVerificationCard } from "@/components/charts/claim-verification-card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import Link from "next/link"

export default function ReportsPage() {
  const [report, setReport] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const params = useParams()
  const id = params.id

  useEffect(() => {
    if (!id) return

    // Function to fetch data
    const fetchReport = async () => {
      try {
        const res = await fetch(`http://localhost:8000/reports/${id}`)
        const data = await res.json()
        setReport(data)
        setLoading(false)
      } catch (err) {
        console.error("Failed to fetch report:", err)
      }
    }

    // Initial fetch
    fetchReport()

    // SET UP AUTO-REFRESH: Only if the report is missing or pending
    const interval = setInterval(() => {
      if (!report || report.recommendation === "pending" || report.overall_risk_score === null) {
        fetchReport()
      }
    }, 5000)

    return () => clearInterval(interval)
  }, [id, report?.recommendation])

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background text-white">
        <p className="animate-pulse">Initializing VERITAS Analysis...</p>
      </div>
    )
  }

  const integrityRiskScore = report?.overall_risk_score !== null
    ? (report.overall_risk_score * 100).toFixed(1) + "%"
    : "N/A"

  // Extract claim verification from saiv_results
  const claimVerification = report?.saiv_results?.claim_verification ?? null

  // Extract section similarity from saiv_results
  const sectionSim = report?.saiv_results?.section_similarity ?? null

  return (
    <main className="relative min-h-dvh bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-background to-background">
      <div className="absolute inset-0 -z-20" aria-hidden>
        <img
          src="/images/dashboard-bg-gemini-v3.png"
          alt=""
          className="h-full w-full object-cover opacity-70 brightness-110 saturate-125 select-none pointer-events-none"
        />
      </div>

      <TopNav />

      <section className="mx-auto w-full max-w-6xl px-4 py-8">
        <div className="mb-4">
          <Button asChild variant="outline" className="border-white/60 text-white hover:bg-white/10 bg-transparent">
            <Link href="/dashboard">Back to Dashboard</Link>
          </Button>
        </div>

        <div className="mb-6 flex justify-between items-end">
          <div>
            <h2 className="text-balance text-2xl font-semibold tracking-tight text-white">Report Viewer</h2>
            <p className="text-lg text-gray-300">Manuscript ID: {id}</p>
          </div>
          {report?.recommendation === "pending" && (
            <p className="text-sm text-primary animate-pulse font-mono">Live analyzing...</p>
          )}
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <Card className="border-border bg-background/70 backdrop-blur lg:col-span-2">
            <CardHeader>
              <CardTitle>Integrity Risk Score</CardTitle>
              <CardDescription>Overall assessment</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-6xl font-bold leading-none tracking-tight text-foreground">
                {integrityRiskScore}
              </div>
            </CardContent>
          </Card>

          <Card className="border-border bg-background/70 backdrop-blur lg:col-span-2 ">
            <CardHeader>
              <CardTitle>Integrity Components</CardTitle>
              <CardDescription>Analysis of CSAD, Semantic Consistency, and AI-likelihood</CardDescription>
            </CardHeader>
            <CardContent>
              <IntegrityBarChart
                data={[
                  {
                    source: "AI Likelihood",
                    citations: report?.saiv_results?.ai_likelihood ? Math.round(report.saiv_results.ai_likelihood * 100) : 0
                  },
                  {
                    source: "CSAD Score",
                    citations: report?.csad_results?.csad_score ? Math.round(report.csad_results.csad_score * 100) : 0
                  },
                  {
                    source: "Semantic Risk",
                    citations: report?.saiv_results?.semantic_similarity ? Math.round((1 - report.saiv_results.semantic_similarity) * 100) : 0
                  },
                  ...(claimVerification ? [{
                    source: "Claim Inconsistency",
                    citations: Math.round((1 - claimVerification.consistency_score) * 100)
                  }] : [])
                ]}
              />
            </CardContent>
          </Card>
        </div>

        {/* ---- Section Similarity (from saiv_new) ---- */}
        {sectionSim && (
          <div className="mt-6">
            <Card className="border-border bg-background/70 backdrop-blur">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/10 text-blue-400 text-sm font-bold">
                    §
                  </span>
                  Section Coherence
                </CardTitle>
                <CardDescription>Cosine similarity between manuscript sections (topic alignment)</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="rounded-xl border border-border bg-background/50 p-4 text-center">
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Abstract ↔ Body</p>
                    <p className="text-2xl font-bold text-blue-400 tabular-nums">
                      {(sectionSim.abstract_body * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="rounded-xl border border-border bg-background/50 p-4 text-center">
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Body ↔ Conclusion</p>
                    <p className="text-2xl font-bold text-blue-400 tabular-nums">
                      {(sectionSim.body_conclusion * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="rounded-xl border border-border bg-background/50 p-4 text-center">
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Abstract ↔ Conclusion</p>
                    <p className="text-2xl font-bold text-blue-400 tabular-nums">
                      {(sectionSim.abstract_conclusion * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="rounded-xl border border-border bg-background/50 p-4 text-center">
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Overall</p>
                    <p className={`text-2xl font-bold tabular-nums ${
                      sectionSim.overall >= 0.6 ? "text-emerald-400" : "text-rose-400"
                    }`}>
                      {(sectionSim.overall * 100).toFixed(1)}%
                    </p>
                    <Badge variant={sectionSim.overall >= 0.6 ? "default" : "destructive"} className="mt-1 text-[10px]">
                      {sectionSim.overall >= 0.6 ? "Coherent" : "Flagged"}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* ---- Claim Verification Card ---- */}
        <div className="mt-6">
          <ClaimVerificationCard data={claimVerification} />
        </div>

        <div className="mt-6 grid gap-4">
          <h3 className="text-lg font-semibold">Integrity Findings</h3>
          <Card className="border-border bg-background/70 backdrop-blur">
            <CardContent className="pt-6">
              <h3 className="text-lg font-bold"> CSAD Explanation</h3>

              <div className="flex items-start gap-4">
                <div className="mt-1 h-2 w-2 rounded-full bg-primary" />


                <ul>
                  {
                    report?.csad_results?.explanations.map((finding: String, i: Number) =>


                      <li key={String(i)}>
                        <p >{finding}</p>
                      </li>
                    )
                  }
                </ul>

              </div>

              <div className="mt-4 flex flex-wrap items-center gap-4 border-t border-border pt-4">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-muted-foreground">Self-Citation Ratio:</span>
                  <Badge variant={report?.csad_results?.self_cite_ratio > 0.25 ? "destructive" : "secondary"}>
                    {report?.csad_results?.self_cite_ratio ? (report.csad_results.self_cite_ratio * 100).toFixed(1) + "%" : "0%"}
                  </Badge>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-muted-foreground">Retracted References Found:</span>
                  <Badge variant={report?.csad_results?.retracted_refs_count > 0 ? "destructive" : "secondary"}>
                    {report?.csad_results?.retracted_refs_count ?? 0}
                  </Badge>
                </div>
              </div>
            </CardContent>


          </Card>




          <Card className="border-border bg-background/70 backdrop-blur">


            <CardContent className="pt-6">
              <h3 className="text-lg font-bold">SAIV Explanation</h3>
              <div className="flex items-start gap-4">
                <div className="mt-1 h-2 w-2 rounded-full bg-primary" />
                <p className="text-pretty text-foreground">{report?.saiv_results?.ai_explanation}</p>
              </div>


            </CardContent>
          </Card>

        </div>
      </section>
    </main>
  )
}