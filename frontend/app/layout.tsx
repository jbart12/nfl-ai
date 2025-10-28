import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Link from 'next/link'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'NFL AI Predictions - Data-Driven Player Prop Analysis',
  description: 'Get AI-powered NFL player prop predictions with confidence scores, historical context, and expert analysis. Backed by 3 seasons of data.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen flex flex-col">
          <header className="border-b">
            <div className="container mx-auto px-4 py-4">
              <div className="flex items-center justify-between">
                <Link href="/">
                  <h1 className="text-2xl font-bold text-primary hover:opacity-80 transition-opacity">
                    NFL AI Predictions
                  </h1>
                </Link>
                <nav className="flex gap-6">
                  <Link
                    href="/opportunities"
                    className="text-sm font-medium hover:text-primary transition-colors"
                  >
                    Opportunities
                  </Link>
                  <Link
                    href="/predict"
                    className="text-sm font-medium hover:text-primary transition-colors"
                  >
                    Predict
                  </Link>
                </nav>
              </div>
            </div>
          </header>
          <main className="flex-1">
            {children}
          </main>
          <footer className="border-t py-6">
            <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
              <p>Powered by Claude AI • Historical data from 2023-2025 seasons</p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  )
}
