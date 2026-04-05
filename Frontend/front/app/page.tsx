"use client"

import type React from "react"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/components/ui/use-toast"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [name, setName] = useState("")
  const [role, setRole] = useState("")
  const [affiliation, setAffiliation] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const { toast } = useToast()

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
          name,
          role,
          affiliation
        }),
      });

      const data = await response.json();

      if (response.status === 400) {
        toast({
          title: "Registration Failed",
          description: data.detail || "Email already registered",
          variant: "destructive",
          duration: 4000,
        });
        return;
      }

      if (!response.ok) {
        throw new Error(data.detail || 'Registration failed. Please try again.');
      }

      // Show success message
      toast({
        title: "Success",
        description: "Successfully registered! Please log in.",
        duration: 3000,
      });

      // Clear form and switch to login tab
      setEmail("")
      setPassword("")
      setName("")
      setRole("")
      setAffiliation("")
      
    } catch (error) {
      console.error('Signup error:', error);
      toast({
        title: "Error",
        description: "Unable to connect to the server. Please try again later.",
        variant: "destructive",
        duration: 4000,
      });
    } finally {
      setIsLoading(false);
    }
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      const data = await response.json();

      if (response.status === 401) {
        toast({
          title: "Invalid Credentials",
          description: "Please check your email and password and try again",
          variant: "destructive",
          duration: 4000,
        });
        return;
      }

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed. Please try again.');
      }

      // Store the token in localStorage
      localStorage.setItem('token', data.access_token);
      
      // Show success message
      toast({
        title: "Success",
        description: "Successfully logged in!",
        duration: 3000,
      });

      // Redirect to dashboard
      router.push("/dashboard");
    } catch (error) {
      console.error('Login error:', error);
      toast({
        title: "Error",
        description: "Unable to connect to the server. Please try again later.",
        variant: "destructive",
        duration: 4000,
      });
    } finally {
      setIsLoading(false);
    }
  }

  const handleSocialLogin = (provider: string) => {
    console.log("[v0] Social login with:", provider)
  }

  return (
    <main className="relative min-h-dvh theme-login login-hero overflow-hidden">
      {/* soft background pattern to match login */}
      {/* <svg className="h-full w-full" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
            <circle cx="1" cy="1" r="1" className="fill-primary/30" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#dots)" />
      </svg> */}

      <section className="mx-auto flex max-w-6xl items-center justify-start md:justify-start px-4 py-24">
        <Card
          className="max-w-md hover-lift shadow-2xl relative z-10 opacity-100 w-[126%] mx-[0] border-transparent"
          style={{
            background: "rgba(255, 255, 255, 0.25)",
            backdropFilter: "blur(40px) saturate(250%)",
            border: "1px solid rgba(255, 255, 255, 0.4)",
            boxShadow:
              "0 32px 80px rgba(0, 0, 0, 0.3), 0 16px 64px rgba(255, 255, 255, 0.2), inset 0 3px 0 rgba(255, 255, 255, 0.6), inset 0 -1px 0 rgba(255, 255, 255, 0.3)",
          }}
        >
          <CardHeader className="text-center space-y-2">
            <CardTitle className="text-3xl font-bold font-sans text-white">ResearchGuard</CardTitle>
            <CardDescription className="text-white/90 font-sans">Sign in or sign up to continue</CardDescription>
          </CardHeader>

          <CardContent className="space-y-6">
            <Tabs defaultValue="login" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="login" className="text-white">Login</TabsTrigger>
                <TabsTrigger value="signup" className="text-white">Sign Up</TabsTrigger>
              </TabsList>
              
              <TabsContent value="login">
                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="login-email" className="text-sm font-medium text-white font-sans">
                      Email Address
                    </Label>
                    <Input
                      id="login-email"
                      type="email"
                      placeholder="Enter your email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="border-white/50 bg-white/10 placeholder:text-white/70 text-white py-3 focus:ring-2 focus:ring-white/40 focus:border-white/60 focus:bg-white/15 transition-all duration-200"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="login-password" className="text-sm font-medium text-white font-sans">
                      Password
                    </Label>
                    <Input
                      id="login-password"
                      type="password"
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="border-white/50 bg-white/10 placeholder:text-white/70 text-white py-3 focus:ring-2 focus:ring-white/40 focus:border-white/60 focus:bg-white/15 transition-all duration-200"
                      required
                    />
                  </div>

                  <Button
                    type="submit"
                    className="w-full ripple-effect hover-lift font-sans font-bold py-5 transition-all duration-300"
                    style={{ backgroundColor: "#0C115B", color: "white" }}
                    disabled={isLoading}
                  >
                    {isLoading ? "Processing..." : "Sign In"}
                  </Button>
                </form>
              </TabsContent>

              <TabsContent value="signup">
                <form onSubmit={handleSignup} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="signup-name" className="text-sm font-medium text-white font-sans">
                      Full Name
                    </Label>
                    <Input
                      id="signup-name"
                      type="text"
                      placeholder="Enter your full name"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="border-white/50 bg-white/10 placeholder:text-white/70 text-white py-3 focus:ring-2 focus:ring-white/40 focus:border-white/60 focus:bg-white/15 transition-all duration-200"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="signup-email" className="text-sm font-medium text-white font-sans">
                      Email Address
                    </Label>
                    <Input
                      id="signup-email"
                      type="email"
                      placeholder="Enter your email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="border-white/50 bg-white/10 placeholder:text-white/70 text-white py-3 focus:ring-2 focus:ring-white/40 focus:border-white/60 focus:bg-white/15 transition-all duration-200"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="signup-password" className="text-sm font-medium text-white font-sans">
                      Password
                    </Label>
                    <Input
                      id="signup-password"
                      type="password"
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="border-white/50 bg-white/10 placeholder:text-white/70 text-white py-3 focus:ring-2 focus:ring-white/40 focus:border-white/60 focus:bg-white/15 transition-all duration-200"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="signup-role" className="text-sm font-medium text-white font-sans">
                      Role
                    </Label>
                    <Input
                      id="signup-role"
                      type="text"
                      placeholder="Enter your role"
                      value={role}
                      onChange={(e) => setRole(e.target.value)}
                      className="border-white/50 bg-white/10 placeholder:text-white/70 text-white py-3 focus:ring-2 focus:ring-white/40 focus:border-white/60 focus:bg-white/15 transition-all duration-200"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="signup-affiliation" className="text-sm font-medium text-white font-sans">
                      Affiliation
                    </Label>
                    <Input
                      id="signup-affiliation"
                      type="text"
                      placeholder="Enter your affiliation"
                      value={affiliation}
                      onChange={(e) => setAffiliation(e.target.value)}
                      className="border-white/50 bg-white/10 placeholder:text-white/70 text-white py-3 focus:ring-2 focus:ring-white/40 focus:border-white/60 focus:bg-white/15 transition-all duration-200"
                      required
                    />
                  </div>

                  <Button
                    type="submit"
                    className="w-full ripple-effect hover-lift font-sans font-bold py-5 transition-all duration-300"
                    style={{ backgroundColor: "#0C115B", color: "white" }}
                    disabled={isLoading}
                  >
                    {isLoading ? "Processing..." : "Sign Up"}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>

            <div className="relative">
              <div className="relative flex justify-center text-xs uppercase">
                <span className="px-2 text-white/90 font-sans">Or continue with</span>
              </div>
            </div>

            <div className="space-y-3">
              <Button
                onClick={() => handleSocialLogin("Google")}
                className="w-full font-sans font-semibold py-4 hover:brightness-110 focus:ring-2 focus:ring-white/30 border border-white/20 text-white"
                style={{ backgroundColor: "#0C115B" }}
              >
                <svg className="w-5 h-5 mr-2 shrink-0" viewBox="0 0 48 48" aria-hidden="true" focusable="false">
                  <g fill="currentColor">
                    <path d="M43.611 20.083H42V20H24v8h11.303c-1.649 4.657-6.08 8-11.303 8-6.627 0-12-5.373-12-12S17.373 12 24 12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C33.17 6.053 28.805 4 24 4 12.955 4 4 12.955 4 24s8.955 20 20 20 20-8.955 20-20c0-1.341-.138-2.65-.389-3.917Z" />
                    <path d="M6.306 14.691 12.877 19.51C14.655 16.108 19.007 14 24 14c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C33.17 6.053 28.805 4 24 4 16.318 4 9.656 8.337 6.306 14.691Z" />
                    <path d="M24 44c5.185 0 9.86-1.985 13.409-5.216l-6.191-5.238C29.086 35.091 26.655 36 24 36c-5.204 0-9.613-3.317-11.247-7.946l-6.507 5.017C9.58 39.77 16.228 44 24 44Z" />
                    <path d="M43.611 20.083H42V20H24v8h11.303a11.98 11.98 0 0 1-4.109 5.564l6.191 5.238C39.481 35.789 44 30.5 44 24c0-1.341-.138-2.65-.389-3.917Z" />
                  </g>
                </svg>
                <span className="text-white">Continue with Google</span>
              </Button>

            </div>

            <div className="text-center">
              <a href="#" className="text-sm text-white/80 hover:text-white font-sans transition-colors">
                Forgot your password?
              </a>
            </div>
          </CardContent>
        </Card>
      </section>
    </main>
  )
}
