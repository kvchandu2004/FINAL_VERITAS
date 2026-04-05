"use client"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { useState } from "react"

interface ClaimResult {
  claim: string
  label: "entailment" | "contradiction" | "neutral"
  confidence: number
  scores: {
    entailment: number
    contradiction: number
    neutral: number
  }
}

interface ClaimVerification {
  claim_results: ClaimResult[]
  consistency_score: number
  num_claims: number
  num_supported: number
  num_contradicted: number
  num_neutral: number
  flagged: boolean
}

interface ClaimVerificationCardProps {
  data: ClaimVerification | null | undefined
}

const labelConfig: Record<string, { color: string; bg: string; icon: string; border: string }> = {
  entailment: {
    color: "text-emerald-400",
    bg: "bg-emerald-500/10",
    icon: "✓",
    border: "border-emerald-500/30",
  },
  contradiction: {
    color: "text-rose-400",
    bg: "bg-rose-500/10",
    icon: "✗",
    border: "border-rose-500/30",
  },
  neutral: {
    color: "text-amber-400",
    bg: "bg-amber-500/10",
    icon: "?",
    border: "border-amber-500/30",
  },
}

export function ClaimVerificationCard({ data }: ClaimVerificationCardProps) {
  const [expanded, setExpanded] = useState(false)

  if (!data || !data.claim_results || data.claim_results.length === 0) {
    return (
      <Card className="border-border bg-background/70 backdrop-blur">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary text-sm font-bold">
              NLI
            </span>
            Claim Verification
          </CardTitle>
          <CardDescription>No claim verification data available for this manuscript.</CardDescription>
        </CardHeader>
      </Card>
    )
  }

  const consistencyPct = (data.consistency_score * 100).toFixed(1)

  // Determine overall verdict
  const getVerdict = (score: number) => {
    if (score >= 0.8) return { text: "Highly Consistent", variant: "default" as const, color: "text-emerald-400" }
    if (score >= 0.6) return { text: "Mostly Consistent", variant: "secondary" as const, color: "text-blue-400" }
    if (score >= 0.4) return { text: "Partially Consistent", variant: "secondary" as const, color: "text-amber-400" }
    return { text: "Low Consistency", variant: "destructive" as const, color: "text-rose-400" }
  }

  const verdict = getVerdict(data.consistency_score)

  return (
    <Card className="border-border bg-background/70 backdrop-blur overflow-hidden">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary text-sm font-bold">
              NLI
            </span>
            Claim Verification
          </CardTitle>
          {data.flagged && (
            <Badge variant="destructive" className="animate-pulse">
              ⚠ Flagged
            </Badge>
          )}
        </div>
        <CardDescription>
          NLI-based entailment analysis — each abstract claim is verified against the conclusion.
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-5">
        {/* ---- Summary Stats Row ---- */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {/* Consistency Score */}
          <div className="rounded-xl border border-border bg-background/50 p-4 text-center">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Consistency</p>
            <p className={`text-3xl font-bold tabular-nums ${verdict.color}`}>{consistencyPct}%</p>
            <Badge variant={verdict.variant} className="mt-2 text-[10px]">
              {verdict.text}
            </Badge>
          </div>

          {/* Supported */}
          <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4 text-center">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Supported</p>
            <p className="text-3xl font-bold text-emerald-400 tabular-nums">{data.num_supported}</p>
            <p className="text-xs text-muted-foreground mt-1">of {data.num_claims} claims</p>
          </div>

          {/* Contradicted */}
          <div className="rounded-xl border border-rose-500/20 bg-rose-500/5 p-4 text-center">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Contradicted</p>
            <p className="text-3xl font-bold text-rose-400 tabular-nums">{data.num_contradicted}</p>
            <p className="text-xs text-muted-foreground mt-1">of {data.num_claims} claims</p>
          </div>

          {/* Neutral */}
          <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 text-center">
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-1">Neutral</p>
            <p className="text-3xl font-bold text-amber-400 tabular-nums">{data.num_neutral}</p>
            <p className="text-xs text-muted-foreground mt-1">of {data.num_claims} claims</p>
          </div>
        </div>

        {/* ---- Consistency Bar ---- */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>Claim Support Distribution</span>
            <span>{data.num_claims} total claims</span>
          </div>
          <div className="flex h-3 w-full overflow-hidden rounded-full bg-background/50 border border-border">
            {data.num_supported > 0 && (
              <div
                className="bg-emerald-500 transition-all duration-700"
                style={{ width: `${(data.num_supported / data.num_claims) * 100}%` }}
                title={`${data.num_supported} supported`}
              />
            )}
            {data.num_neutral > 0 && (
              <div
                className="bg-amber-500 transition-all duration-700"
                style={{ width: `${(data.num_neutral / data.num_claims) * 100}%` }}
                title={`${data.num_neutral} neutral`}
              />
            )}
            {data.num_contradicted > 0 && (
              <div
                className="bg-rose-500 transition-all duration-700"
                style={{ width: `${(data.num_contradicted / data.num_claims) * 100}%` }}
                title={`${data.num_contradicted} contradicted`}
              />
            )}
          </div>
          <div className="flex gap-4 text-xs text-muted-foreground">
            <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-emerald-500" /> Supported</span>
            <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-amber-500" /> Neutral</span>
            <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-rose-500" /> Contradicted</span>
          </div>
        </div>

        {/* ---- Expand/Collapse ---- */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-center gap-2 py-2 text-sm font-medium text-primary hover:text-primary/80 transition-colors rounded-lg border border-border/50 hover:border-primary/30 hover:bg-primary/5"
        >
          {expanded ? "Hide" : "Show"} Detailed Claim Analysis
          <svg
            className={`h-4 w-4 transition-transform duration-300 ${expanded ? "rotate-180" : ""}`}
            fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {/* ---- Per-Claim Details ---- */}
        {expanded && (
          <div className="space-y-3 animate-in fade-in-0 slide-in-from-top-2 duration-300">
            {data.claim_results.map((cr, i) => {
              const cfg = labelConfig[cr.label] ?? labelConfig.neutral
              return (
                <div
                  key={i}
                  className={`
                    rounded-xl border ${cfg.border} ${cfg.bg}
                    p-4 transition-all duration-200 hover:shadow-md
                  `}
                >
                  <div className="flex items-start gap-3">
                    {/* Label Icon */}
                    <span className={`inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-sm font-bold ${cfg.bg} ${cfg.color} border ${cfg.border}`}>
                      {cfg.icon}
                    </span>

                    <div className="flex-1 min-w-0 space-y-2">
                      {/* Claim text */}
                      <p className="text-sm text-foreground leading-relaxed">{cr.claim}</p>

                      {/* Labels row */}
                      <div className="flex flex-wrap items-center gap-2">
                        <Badge
                          variant={cr.label === "entailment" ? "default" : cr.label === "contradiction" ? "destructive" : "secondary"}
                          className="capitalize text-[10px]"
                        >
                          {cr.label}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          Confidence: <strong className={cfg.color}>{(cr.confidence * 100).toFixed(1)}%</strong>
                        </span>
                      </div>

                      {/* Score bars */}
                      <div className="space-y-1">
                        {(["entailment", "neutral", "contradiction"] as const).map((key) => (
                          <div key={key} className="flex items-center gap-2">
                            <span className="text-[10px] text-muted-foreground w-20 capitalize">{key}</span>
                            <div className="flex-1 h-1.5 rounded-full bg-background/50 overflow-hidden">
                              <div
                                className={`h-full rounded-full transition-all duration-500 ${
                                  key === "entailment" ? "bg-emerald-500" :
                                  key === "contradiction" ? "bg-rose-500" : "bg-amber-500"
                                }`}
                                style={{ width: `${cr.scores[key] * 100}%` }}
                              />
                            </div>
                            <span className="text-[10px] text-muted-foreground tabular-nums w-12 text-right">
                              {(cr.scores[key] * 100).toFixed(1)}%
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
