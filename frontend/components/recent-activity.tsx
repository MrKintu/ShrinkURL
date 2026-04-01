"use client"

import { Copy, Check, ExternalLink } from "lucide-react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface ShortenedUrl {
  id: number
  long_url: string
  short_code: string
  short_url: string
  created_at: string
}

interface RecentActivityProps {
  readonly urls: ShortenedUrl[]
}

export function RecentActivity({ urls }: RecentActivityProps) {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)

  const handleCopy = async (url: string, index: number) => {
    try {
      await navigator.clipboard.writeText(url)
      setCopiedIndex(index)
      setTimeout(() => setCopiedIndex(null), 2000)
    } catch (err) {
      console.error("Failed to copy:", err)
    }
  }

  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / 60000)

    if (minutes < 1) return "Just now"
    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}h ago`
    return date.toLocaleDateString()
  }

  if (urls.length === 0) {
    return null
  }

  return (
    <section className="px-4 py-20">
      <div className="mx-auto max-w-4xl">
        <Card className="rounded-2xl border-border bg-card">
          <CardHeader className="border-b border-border">
            <CardTitle className="text-xl font-semibold text-foreground">
              Recent Activity
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-border">
              {urls.slice(0, 5).map((url, index) => (
                <div
                  key={url.short_code}
                  className="flex flex-col gap-3 p-4 transition-colors hover:bg-secondary/50 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <a
                        href={url.short_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-medium text-primary transition-colors hover:text-primary/80"
                      >
                        {url.short_url.replace(/^https?:\/\//, "")}
                      </a>
                      <ExternalLink className="h-3 w-3 flex-shrink-0 text-muted-foreground" />
                    </div>
                    <p className="mt-1 truncate text-sm text-muted-foreground">
                      {url.long_url}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-muted-foreground">
                      {formatTime(url.created_at)}
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleCopy(url.short_url, index)}
                      className="h-8 w-8 rounded-lg p-0"
                    >
                      {copiedIndex === index ? (
                        <Check className="h-4 w-4 text-green-500" />
                      ) : (
                        <Copy className="h-4 w-4 text-muted-foreground" />
                      )}
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  )
}
