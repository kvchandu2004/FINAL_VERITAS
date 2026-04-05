"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/components/ui/use-toast"

export default function LoginForm() {
  const router = useRouter()
  const { toast } = useToast()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
      alert('The onSubmit function was called!'); // <-- ADD THIS LINE

    setLoading(true)
    console.log("heelo")
    try {
      const response = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      // Store the token
      localStorage.setItem('token', data.access_token);
      
      // Show success message
      toast({
        title: "Success",
        description: "Successfully logged in!",
        duration: 3000,
      });

      // Redirect to dashboard
      console.log("redirecting to dashboard");
      router.push("/dashboard");
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to login",
        variant: "destructive",
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className="w-full max-w-md border-border/60 bg-background/40 backdrop-blur-md supports-[backdrop-filter]:bg-background/40 shadow-lg shadow-primary/10 text-white">
      <CardHeader>
        <div className="flex items-center gap-2">
          <span className="brand-badge brand-badge-lg h-10 w-10 text-white">
            <svg aria-hidden="true" viewBox="0 0 24 24" className="h-5 w-5" fill="currentColor">
              <path d="M12 2.5c-.3 0-.6.06-.87.18l-6 2.5a1.5 1.5 0 0 0-.93 1.39V11c0 5.52 4.23 8.69 7.02 9.94.48.22 1.06.22 1.54 0C15.55 19.69 19.78 16.52 19.78 11V6.57a1.5 1.5 0 0 0-.93-1.39l-6-2.5c-.27-.12-.57-.18-.85-.18Z" />
              <path d="M10.4 12.6l-1.6-1.6a1 1 0 1 0-1.4 1.42l2.3 2.3c.39.39 1.03.39 1.42 0l4.9-4.9a1 1 0 1 0-1.42-1.42l-4.2 4.2Z" />
            </svg>
          </span>
          <CardTitle className="text-balance text-white">ResearchGuard</CardTitle>
        </div>
        <CardDescription className="text-pretty text-white/90">Sign in or sign up to get started.</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={onSubmit} className="grid gap-4">
          <div className="grid gap-2">
            <Label htmlFor="email" className="text-white">
              Email
            </Label>
            <Input
              id="email"
              type="email"
              placeholder="you@university.edu"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="border-white/50 bg-white/10 placeholder:text-white/70 text-white focus:ring-2 focus:ring-white/40 focus:border-white/60 focus:bg-white/15 transition-all duration-200"
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="password" className="text-white">
              Password
            </Label>
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="border-white/50 bg-white/10 placeholder:text-white/70 text-white focus:ring-2 focus:ring-white/40 focus:border-white/60 focus:bg-white/15 transition-all duration-200"
            />
          </div>

          <Button
            type="submit"
            disabled={loading}
            className="mt-2 w-full font-sans font-bold py-5 hover:brightness-110 focus:ring-2 focus:ring-white/30 border border-white/20"
            style={{ backgroundColor: "#0C115B", color: "white" }}
          >
            {loading ? "Processing..." : "Sign in or sign up"}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
