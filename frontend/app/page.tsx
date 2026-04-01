"use client"

import { useState } from "react"
import { Hero } from "@/components/hero"
import { Features } from "@/components/features"
import { RecentActivity } from "@/components/recent-activity"

interface ShortenedUrl {
  id: number
  long_url: string
  short_code: string
  short_url: string
  created_at: string
}

export default function Home() {
  const [recentUrls, setRecentUrls] = useState<ShortenedUrl[]>([])

  const handleNewUrl = (url: ShortenedUrl) => {
    setRecentUrls((prev) => [url, ...prev])
  }

  return (
    <main className="min-h-screen bg-background">
      <Hero onNewUrl={handleNewUrl} />
      <Features />
      <RecentActivity urls={recentUrls} />

      {/* Footer */}
      <footer className="border-t border-border px-4 py-8">
        <div className="mx-auto max-w-6xl text-center">
          <p className="text-sm text-muted-foreground">
            TinyScale &mdash; High-performance URL shortening at scale. 7-character Base62 encoding supports 3.5 trillion unique URLs.
          </p>
        </div>
      </footer>
    </main>
  )
}
