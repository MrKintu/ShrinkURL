import { Globe, Zap, Shield } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

const features = [
  {
    icon: Globe,
    title: "Scalability",
    description:
      "Designed to handle billions of URLs using a distributed range manager. Scale horizontally without limits.",
  },
  {
    icon: Zap,
    title: "Speed",
    description:
      "Near-instant redirects powered by Redis caching. Your links resolve in milliseconds, not seconds.",
  },
  {
    icon: Shield,
    title: "Reliability",
    description:
      "7-character Base62 encoding allows for 3.5 trillion unique combinations. Built for enterprise workloads.",
  },
]

export function Features() {
  return (
    <section className="px-4 py-20">
      <div className="mx-auto max-w-6xl">
        <div className="mb-12 text-center">
          <h2 className="mb-4 text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Built for Scale
          </h2>
          <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
            Enterprise-grade architecture designed for high-performance URL shortening at any scale.
          </p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <Card
              key={feature.title}
              className="group rounded-2xl border-border bg-card transition-all hover:border-primary/50 hover:bg-card/80"
            >
              <CardContent className="p-8">
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 transition-colors group-hover:bg-primary/20">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="mb-2 text-xl font-semibold text-foreground">
                  {feature.title}
                </h3>
                <p className="leading-relaxed text-muted-foreground">
                  {feature.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
