"use client"

import { useState } from "react"
import { Link, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ResultCard } from "@/components/result-card"

interface ShortenedUrl {
  id: number
  long_url: string
  short_code: string
  short_url: string
  created_at: string
}

// API function for POST /api/shorten - Connects to Django backend
async function shortenUrl(longUrl: string): Promise<ShortenedUrl> {
  const API_URL = process.env.NEXT_PUBLIC_API_URL
  
  const response = await fetch(`${API_URL}/api/shorten/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ long_url: longUrl }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || "Failed to shorten URL")
  }

  return response.json()
}

interface HeroProps {
  readonly onNewUrl: (url: ShortenedUrl) => void
}

export function Hero({ onNewUrl }: HeroProps) {
  const [longUrl, setLongUrl] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<ShortenedUrl | null>(null)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.SubmitEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError("")

    if (!longUrl.trim()) {
      setError("Please enter a URL")
      return
    }

    // Basic URL validation - let the backend do full validation
    let urlToSubmit = longUrl.trim()
    if (!urlToSubmit.startsWith("http://") && !urlToSubmit.startsWith("https://")) {
      urlToSubmit = "https://" + urlToSubmit
    }

    setIsLoading(true)
    try {
      const shortened = await shortenUrl(urlToSubmit)
      setResult(shortened)
      onNewUrl(shortened)
      setLongUrl("")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to shorten URL. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <section className="relative flex min-h-[70vh] flex-col items-center justify-center px-4 py-20">
      {/* Subtle gradient background */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute left-1/2 top-1/2 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/10 blur-3xl" />
      </div>

      <div className="relative z-10 mx-auto w-full max-w-3xl text-center">
        {/* Logo and title */}
        <div className="mb-6 flex items-center justify-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary">
            <Link className="h-6 w-6 text-primary-foreground" />
          </div>
          <h1 className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
            TinyScale
          </h1>
        </div>

        <p className="mx-auto mb-10 max-w-xl text-lg text-muted-foreground">
          Shorten URLs at scale with near-instant redirects. Built for billions of URLs.
        </p>

        {/* URL Input Form */}
        <form onSubmit={handleSubmit} className="mx-auto mb-6 w-full max-w-2xl">
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Input
                type="url"
                placeholder="Paste your long URL here..."
                value={longUrl}
                onChange={(e) => setLongUrl(e.target.value)}
                className="h-14 rounded-xl border-border bg-card px-5 text-base text-foreground placeholder:text-muted-foreground focus-visible:ring-primary"
                disabled={isLoading}
              />
            </div>
            <Button
              type="submit"
              disabled={isLoading}
              className="h-14 rounded-xl bg-primary px-8 text-base font-semibold text-primary-foreground transition-all hover:bg-primary/90 disabled:opacity-70"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Shortening...
                </>
              ) : (
                "Shorten"
              )}
            </Button>
          </div>
          {error && (
            <p className="mt-3 text-sm text-destructive">{error}</p>
          )}
        </form>

        {/* Result Display */}
        {result && <ResultCard result={result} />}
      </div>
    </section>
  )
}
