"use client"

import type React from "react"
import Link from "next/link" // add Link for back button
import { TopNav } from "@/components/top-nav"
import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [doi, setDoi] = useState("")
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setSuccess(false)

    // Get access token from localStorage
    const accessToken = localStorage.getItem('token');
    if (!accessToken) {
      setLoading(false);
      // You might want to add error handling here or redirect to login
      console.error('No access token found');
      return;
    }

    const body = new FormData();
    if (file) body.append("file", file);   // binary file
    body.append("title", "title");
    body.append("abstract", "abstract");
    body.append("doi", doi);

    console.log([...body.entries()]);  // to check data

    const res = await fetch("http://localhost:8000/manuscripts/upload", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${accessToken}`, // 🔑 Auth header from localStorage
      },
      body, 
    });


    setLoading(false)
    if (res.ok) {
    const data = await res.json(); // Capture the backend response 
    setSuccess(true);
    setDoi("");
    setFile(null);

    // Automatically redirect to the report page after a short delay
    setTimeout(() => {
      // Access the ID from the returned manuscript object 
      window.location.href = `/reports/${data.manuscript.id}`;
    }, 1500);
  } else {
    // Optional: handle server errors
    console.error("Upload failed");
  }
}

  return (
    <main className="relative min-h-dvh bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-background to-background">
      <div className="absolute inset-0 -z-20" aria-hidden>
        <img
          src="/images/dashboard-bg-gemini-v3.png"
          alt=""
          className="h-full w-full object-cover opacity-70 brightness-110 saturate-125 select-none pointer-events-none"
        />
      </div>

      <div className="absolute inset-0 -z-10 opacity-40" aria-hidden>
        <svg className="h-full w-full" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
              <circle cx="1" cy="1" r="1" className="fill-primary/30" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#dots)" />
        </svg>
      </div>

      <TopNav />
      <section className="mx-auto w-full max-w-3xl px-4 py-8">
        <div className="mb-4">
          <Button asChild variant="outline" className="border-white/60 text-white hover:bg-white/10 bg-transparent">
            <Link href="/dashboard">Back to Dashboard</Link>
          </Button>
        </div>

        <Card className="border-border bg-background/70 backdrop-blur">
          <CardHeader>
            <CardTitle>Upload</CardTitle>
            <CardDescription>Upload a PDF or provide a DOI to analyze citation integrity.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={onSubmit} className="grid gap-5">
              <div className="grid gap-2">
                <Label htmlFor="pdf">Upload PDF</Label>
                <Input
                  id="pdf"
                  type="file"
                  accept="application/pdf"
                  onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                  className="bg-background/60"
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="doi">Enter DOI</Label>
                <Input
                  id="doi"
                  placeholder="10.1000/xyz123"
                  value={doi}
                  onChange={(e) => setDoi(e.target.value)}
                  className="bg-background/60"
                />
              </div>

              <div className="flex items-center gap-3">
                <Button type="submit" disabled={loading}>
                  {loading ? "Uploading..." : "Upload & Analyze"}
                </Button>
                <span className="text-sm text-muted-foreground">Connects to VERITAS Analysis Engine</span>
              </div>

              {success && (
                <Alert className="border-border">
                  <AlertTitle>Success</AlertTitle>
                  <AlertDescription>
                    Your file/DOI was submitted. Analysis will appear in Reports shortly.
                  </AlertDescription>
                </Alert>
              )}
            </form>
          </CardContent>
        </Card>
      </section>
    </main>
  )
}
