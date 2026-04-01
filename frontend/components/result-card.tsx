"use client"

import { useState } from "react"
import { Copy, Check, ExternalLink } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

interface ShortenedUrl {
  id: number
  long_url: string
  short_code: string
  short_url: string
  created_at: string
}

interface ResultCardProps {
  readonly result: ShortenedUrl
}

export function ResultCard({ result }: ResultCardProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(result.short_url)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error("Failed to copy:", err)
    }
  }

  return (
    <Card className="mx-auto w-full max-w-2xl overflow-hidden rounded-2xl border-border bg-card transition-all hover:border-primary/50">
      <CardContent className="p-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex-1 text-left">
            <p className="mb-1 text-sm text-muted-foreground">Your shortened URL</p>
            <div className="flex items-center gap-2">
              <a
                href={result.short_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xl font-semibold text-primary transition-colors hover:text-primary/80"
              >
                {result.short_url.replace(/^https?:\/\//, "")}
              </a>
              <ExternalLink className="h-4 w-4 text-muted-foreground" />
            </div>
            <p className="mt-2 truncate text-sm text-muted-foreground">
              Original: {result.long_url}
            </p>
          </div>
          <Button
            onClick={handleCopy}
            variant={copied ? "secondary" : "default"}
            className="rounded-xl px-6 transition-all"
          >
            {copied ? (
              <>
                <Check className="mr-2 h-4 w-4" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="mr-2 h-4 w-4" />
                Copy
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
