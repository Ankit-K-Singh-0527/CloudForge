import { Bell, ChevronRight, Search } from 'lucide-react'
import { useLocation } from 'react-router'
import ThemeToggle from '@/components/theme/ThemeToggle'
import { Button } from '@/components/ui/button'

const pageTitles: Record<string, string> = {
  '/dashboard': 'Overview',
  '/projects': 'Projects',
  '/deployments': 'Deployments',
  '/settings': 'Settings',
}

export default function AppHeader() {
  const location = useLocation()
  const currentPage = pageTitles[location.pathname] ?? 'CloudForge'

  return (
    <header className="sticky top-0 z-30 flex h-20 items-center justify-between gap-4 border-b border-border/70 bg-background/75 pl-14 pr-5 backdrop-blur-xl md:px-8 lg:pl-8">
      {' '}
      <div className="min-w-0">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>CloudForge</span>
          <ChevronRight className="size-3" />
          <span className="font-medium text-foreground">{currentPage}</span>
        </div>

        <h2 className="mt-1 truncate text-xl font-semibold tracking-tight">{currentPage}</h2>
      </div>
      <div className="flex shrink-0 items-center gap-2">
        <div className="hidden items-center gap-2 rounded-xl border border-border/70 bg-card/70 px-3 py-2 text-sm text-muted-foreground lg:flex">
          <Search className="size-4" />
          <span>Search platform...</span>
          <kbd className="ml-6 rounded border border-border px-1.5 py-0.5 text-[10px]">Ctrl K</kbd>
        </div>

        <Button
          type="button"
          variant="ghost"
          size="icon"
          aria-label="Notifications"
          title="Notifications"
        >
          <Bell className="size-[18px]" />
        </Button>

        <ThemeToggle />

        <div className="hidden h-9 w-px bg-border sm:block" />

        <div className="flex size-9 items-center justify-center rounded-xl border border-primary/20 bg-primary/10 text-sm font-semibold text-primary">
          CF
        </div>
      </div>
    </header>
  )
}
