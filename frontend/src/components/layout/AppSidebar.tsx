import {
  Activity,
  FolderKanban,
  LayoutDashboard,
  Rocket,
  Settings,
  Workflow,
  Cloud,
} from 'lucide-react'
import { NavLink } from 'react-router'

const navigationItems = [
  {
    label: 'Overview',
    path: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    label: 'Projects',
    path: '/projects',
    icon: FolderKanban,
  },
  {
    label: 'Deployments',
    path: '/deployments',
    icon: Rocket,
  },
  {
    label: 'Settings',
    path: '/settings',
    icon: Settings,
  },
]

export default function AppSidebar() {
  return (
    <aside className="flex h-full w-64 shrink-0 flex-col border-r border-sidebar-border bg-sidebar/85 backdrop-blur-xl">
      {/* Brand */}
      <div className="flex h-20 items-center gap-3 border-b border-sidebar-border px-6">
        <div className="flex size-10 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-lg shadow-primary/20">
          <Cloud className="size-6" />
        </div>

        <div className="min-w-0">
          <h1 className="text-lg font-bold tracking-tight text-sidebar-foreground">CloudForge</h1>
          <p className="text-xs text-muted-foreground">Infrastructure control plane</p>
        </div>
      </div>

      {/* Workspace */}
      <div className="px-4 pb-3 pt-6">
        <p className="px-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
          Workspace
        </p>

        <div className="mt-3 flex items-center gap-3 rounded-xl border border-sidebar-border bg-background/50 p-3">
          <div className="flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Workflow className="size-5" />
          </div>

          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-sidebar-foreground">
              Personal workspace
            </p>
            <p className="text-xs text-muted-foreground">Development</p>
          </div>

          <Activity className="size-4 text-emerald-500" />
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-4 py-3" aria-label="Main navigation">
        <p className="mb-3 px-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
          Platform
        </p>

        {navigationItems.map(({ label, path, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              [
                'group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200',
                isActive
                  ? 'bg-primary text-primary-foreground shadow-md shadow-primary/15'
                  : 'text-sidebar-foreground/75 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground',
              ].join(' ')
            }
          >
            <Icon className="size-[18px] shrink-0" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-sidebar-border p-4">
        <div className="rounded-xl border border-sidebar-border bg-background/40 p-3">
          <p className="text-xs font-medium text-sidebar-foreground">CloudForge Platform</p>
          <p className="mt-1 text-xs text-muted-foreground">MVP development environment</p>
          <div className="mt-3 flex items-center gap-2">
            <span className="size-2 rounded-full bg-emerald-500" />
            <span className="text-xs text-muted-foreground">Interface initialized</span>
          </div>
        </div>
      </div>
    </aside>
  )
}
