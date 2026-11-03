import { Link } from 'react-router'

export default function NotFoundPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-4xl font-bold">404</h1>

      <p className="text-muted-foreground">The page you're looking for doesn't exist.</p>

      <Link to="/dashboard" className="text-primary underline">
        Return to Dashboard
      </Link>
    </main>
  )
}
