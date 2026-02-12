import { ArrowUpRight, Github, Linkedin, Twitter, Globe, Mail } from 'lucide-react';
import Link from 'next/link';

export default function Home() {
  return (
    <main className="flex h-screen flex-col overflow-hidden">
      {/* Hero – vertically centered */}
      <section className="flex flex-1 items-center justify-center px-4 md:px-6">
        <div className="w-full max-w-7xl">
          <div className="rounded-3xl border border-border/80 bg-white/80 p-6 shadow-sm backdrop-blur-sm lg:p-10">
            <div className="mx-auto max-w-3xl space-y-5 text-center">
              <p className="inline-flex rounded-full border border-border/80 px-3 py-1 text-xs uppercase tracking-[0.22em] text-muted-foreground">
                Minimal DeFi Intelligence
              </p>
              <h1 className="font-body-mix text-4xl font-semibold tracking-tight sm:text-5xl lg:text-6xl">
                Detect market shifts{' '}
                <span className="font-italic-accent">before they become headlines.</span>
              </h1>
              <p className="font-body-mix max-w-2xl mx-auto text-sm leading-relaxed text-muted-foreground sm:text-base">
                ChainPulse combines whale alerts, anomaly detection, token flow visibility, and protocol
                health signals in one focused dashboard built for{' '}
                <span className="font-italic-accent">fast decisions.</span>
              </p>
              <div className="flex items-center justify-center pt-2">
                <Link
                  href="/dashboard"
                  className="inline-flex items-center gap-2 rounded-full border border-border px-5 py-2.5 text-sm font-medium transition hover:border-foreground hover:bg-foreground hover:text-background"
                >
                  Explore dashboard
                  <ArrowUpRight className="size-4" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer – social icons pinned to bottom */}
      <footer className="flex flex-col items-center gap-3 pb-6 pt-2">
        <div className="flex items-center gap-5">
          <a
            href="https://github.com/ArivunidhiA"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="GitHub"
            className="text-muted-foreground transition-colors hover:text-foreground"
          >
            <Github className="size-[18px]" strokeWidth={1.6} />
          </a>
          <a
            href="https://www.linkedin.com/in/arivunidhi-anna-arivan/"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="LinkedIn"
            className="text-muted-foreground transition-colors hover:text-foreground"
          >
            <Linkedin className="size-[18px]" strokeWidth={1.6} />
          </a>
          <a
            href="https://x.com/Ariv_2012"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="X / Twitter"
            className="text-muted-foreground transition-colors hover:text-foreground"
          >
            <Twitter className="size-[18px]" strokeWidth={1.6} />
          </a>
          <a
            href="https://arivfolio.tech"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Portfolio"
            className="text-muted-foreground transition-colors hover:text-foreground"
          >
            <Globe className="size-[18px]" strokeWidth={1.6} />
          </a>
          <a
            href="mailto:annaarivan.a@northeastern.edu"
            aria-label="Email"
            className="text-muted-foreground transition-colors hover:text-foreground"
          >
            <Mail className="size-[18px]" strokeWidth={1.6} />
          </a>
        </div>
        <p className="text-[11px] tracking-wide text-muted-foreground/50">
          Built by Arivunidhi
        </p>
      </footer>
    </main>
  );
}
