import {
  Activity,
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  Box,
  CheckCircle2,
  Clock3,
  Cloud,
  FolderKanban,
  GitBranch,
  Layers3,
  Plus,
  Rocket,
  Server,
  ShieldCheck,
  TriangleAlert,
  Zap,
} from 'lucide-react'
import { Link } from 'react-router'

const metrics = [
  {
    title: 'Total Projects',
    value: '08',
    description: 'Projects registered',
    change: '+2 this month',
    trend: 'up',
    icon: FolderKanban,
    accent: 'text-sky-500',
    surface: 'bg-sky-500/10',
  },
  {
    title: 'Successful Deployments',
    value: '24',
    description: 'Across all projects',
    change: '+12% this month',
    trend: 'up',
    icon: CheckCircle2,
    accent: 'text-emerald-500',
    surface: 'bg-emerald-500/10',
  },
  {
    title: 'Running Services',
    value: '06',
    description: 'Application instances',
    change: '2 environments',
    trend: 'neutral',
    icon: Activity,
    accent: 'text-violet-500',
    surface: 'bg-violet-500/10',
  },
  {
    title: 'Failed Deployments',
    value: '02',
    description: 'Require attention',
    change: 'View deployment history',
    trend: 'down',
    icon: TriangleAlert,
    accent: 'text-amber-500',
    surface: 'bg-amber-500/10',
  },
]

const deployments = [
  {
    name: 'payment-service',
    branch: 'main',
    commit: 'a82f91c',
    environment: 'Production',
    status: 'Successful',
    time: '12 minutes ago',
    icon: CheckCircle2,
    color: 'text-emerald-500',
  },
  {
    name: 'cloud-api',
    branch: 'develop',
    commit: 'f31bd20',
    environment: 'Development',
    status: 'Running',
    time: '38 minutes ago',
    icon: Clock3,
    color: 'text-sky-500',
  },
  {
    name: 'frontend-dashboard',
    branch: 'main',
    commit: 'c91e4a2',
    environment: 'Production',
    status: 'Failed',
    time: '2 hours ago',
    icon: TriangleAlert,
    color: 'text-amber-500',
  },
]

const resources = [
  { name: 'Compute instances', value: '03', icon: Server },
  { name: 'Container images', value: '12', icon: Box },
  { name: 'Infrastructure stacks', value: '04', icon: Layers3 },
]

export default function DashboardPage() {
  return (
    <div className="mx-auto w-full max-w-[1600px] space-y-8">
      {/* Page introduction */}
      <section className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            <p className="text-xs font-semibold tracking-[0.16em] text-muted-foreground uppercase">
              Infrastructure control center
            </p>
          </div>

          <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
            Good to see you again.
          </h1>

          <p className="max-w-2xl text-sm text-muted-foreground sm:text-base">
            Monitor your projects, deployment activity, and infrastructure from one place.
          </p>
        </div>

        <div className="flex flex-wrap gap-3">
          <Link
            to="/projects"
            className="inline-flex h-10 items-center justify-center gap-2 rounded-lg border border-border bg-card px-4 text-sm font-medium transition-colors hover:bg-accent"
          >
            <Plus className="size-4" />
            New project
          </Link>

          <Link
            to="/deployments"
            className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground shadow-sm transition-opacity hover:opacity-90"
          >
            <Rocket className="size-4" />
            Deployments
            <ArrowRight className="size-4" />
          </Link>
        </div>
      </section>

      {/* Demo data notice */}
      <div className="flex flex-col gap-2 rounded-xl border border-sky-500/20 bg-sky-500/5 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <ShieldCheck className="size-5 shrink-0 text-sky-500" />
          <div>
            <p className="text-sm font-medium">Preview dashboard</p>
            <p className="text-xs text-muted-foreground">
              Sample metrics and activity are displayed for interface development. No live AWS
              account is connected.
            </p>
          </div>
        </div>
        <span className="w-fit rounded-full border border-sky-500/20 px-2.5 py-1 text-[10px] font-semibold tracking-wider text-sky-500 uppercase">
          Demo data
        </span>
      </div>

      {/* Metric cards */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold">Platform overview</h2>
          <span className="text-xs text-muted-foreground">Illustrative metrics</span>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {metrics.map((metric) => {
            const Icon = metric.icon

            return (
              <div
                key={metric.title}
                className="group rounded-xl border border-border/80 bg-card p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-md"
              >
                <div className="flex items-start justify-between">
                  <p className="text-sm font-medium text-muted-foreground">{metric.title}</p>
                  <div className={`rounded-lg p-2 ${metric.surface}`}>
                    <Icon className={`size-4 ${metric.accent}`} />
                  </div>
                </div>

                <div className="mt-5">
                  <p className="text-3xl font-semibold tracking-tight tabular-nums">
                    {metric.value}
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">{metric.description}</p>
                </div>

                <div className="mt-5 flex items-center gap-1.5 border-t border-border/70 pt-3">
                  {metric.trend === 'up' && <ArrowUpRight className="size-3.5 text-emerald-500" />}
                  {metric.trend === 'down' && (
                    <ArrowDownRight className="size-3.5 text-amber-500" />
                  )}
                  <span className="text-xs text-muted-foreground">{metric.change}</span>
                </div>
              </div>
            )
          })}
        </div>
      </section>

      {/* Main dashboard panels */}
      <div className="grid gap-5 xl:grid-cols-3">
        {/* Deployment activity */}
        <section className="rounded-xl border border-border/80 bg-card p-5 shadow-sm xl:col-span-2">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="font-semibold">Recent deployments</h2>
              <p className="mt-1 text-xs text-muted-foreground">Illustrative deployment activity</p>
            </div>

            <Link
              to="/deployments"
              className="inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline"
            >
              View all <ArrowRight className="size-3.5" />
            </Link>
          </div>

          <div className="mt-5 space-y-1">
            {deployments.map((deployment) => {
              const StatusIcon = deployment.icon

              return (
                <div
                  key={deployment.name}
                  className="flex flex-col gap-3 rounded-lg px-3 py-4 transition-colors hover:bg-accent/50 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="flex min-w-0 items-center gap-3">
                    <div className="rounded-lg bg-muted p-2.5">
                      <GitBranch className="size-4 text-muted-foreground" />
                    </div>

                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">{deployment.name}</p>
                      <p className="mt-1 text-xs text-muted-foreground">
                        {deployment.branch} · {deployment.commit}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between gap-4 sm:justify-end">
                    <div className="text-left sm:text-right">
                      <p className="text-xs font-medium">{deployment.environment}</p>
                      <p className="mt-1 text-xs text-muted-foreground">{deployment.time}</p>
                    </div>

                    <span className="inline-flex items-center gap-1.5 rounded-full bg-muted px-2.5 py-1 text-xs font-medium">
                      <StatusIcon className={`size-3.5 ${deployment.color}`} />
                      {deployment.status}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </section>

        {/* Infrastructure overview */}
        <section className="rounded-xl border border-border/80 bg-card p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-semibold">Infrastructure</h2>
              <p className="mt-1 text-xs text-muted-foreground">Resource inventory preview</p>
            </div>
            <div className="rounded-lg bg-primary/10 p-2">
              <Cloud className="size-4 text-primary" />
            </div>
          </div>

          <div className="mt-6 space-y-5">
            {resources.map((resource) => {
              const Icon = resource.icon

              return (
                <div key={resource.name} className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="rounded-lg bg-muted p-2">
                      <Icon className="size-4 text-muted-foreground" />
                    </div>
                    <span className="text-sm text-muted-foreground">{resource.name}</span>
                  </div>
                  <span className="font-semibold tabular-nums">{resource.value}</span>
                </div>
              )
            })}
          </div>

          <div className="mt-7 rounded-lg border border-dashed border-border bg-muted/30 p-3">
            <div className="flex items-center gap-2">
              <Zap className="size-4 text-primary" />
              <p className="text-sm font-medium">AWS integration</p>
            </div>
            <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
              Connect an AWS account to populate this section with actual infrastructure resources.
            </p>
          </div>
        </section>
      </div>

      {/* Bottom section */}
      <section className="grid gap-5 lg:grid-cols-2">
        <div className="rounded-xl border border-border/80 bg-card p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-emerald-500/10 p-2.5">
              <Activity className="size-4 text-emerald-500" />
            </div>
            <div>
              <h2 className="text-sm font-semibold">Deployment health</h2>
              <p className="text-xs text-muted-foreground">Sample status distribution</p>
            </div>
          </div>

          <div className="mt-5 flex h-2.5 overflow-hidden rounded-full bg-muted">
            <div className="w-[86%] bg-emerald-500" />
            <div className="w-[8%] bg-sky-500" />
            <div className="w-[6%] bg-amber-500" />
          </div>

          <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-xs text-muted-foreground">
            <span className="inline-flex items-center gap-1.5">
              <span className="size-2 rounded-full bg-emerald-500" />
              Successful
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="size-2 rounded-full bg-sky-500" />
              Running
            </span>
            <span className="inline-flex items-center gap-1.5">
              <span className="size-2 rounded-full bg-amber-500" />
              Failed
            </span>
          </div>
        </div>

        <div className="flex flex-col justify-between gap-4 rounded-xl border border-primary/20 bg-gradient-to-br from-primary/10 via-card to-violet-500/5 p-5 shadow-sm sm:flex-row sm:items-center">
          <div>
            <div className="flex items-center gap-2">
              <Rocket className="size-4 text-primary" />
              <h2 className="text-sm font-semibold">Ready to deploy?</h2>
            </div>
            <p className="mt-2 max-w-sm text-xs leading-relaxed text-muted-foreground">
              Bring your source code into CloudForge and prepare your first deployment workflow.
            </p>
          </div>

          <Link
            to="/projects"
            className="inline-flex h-10 shrink-0 items-center justify-center gap-2 rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
          >
            Explore projects
            <ArrowRight className="size-4" />
          </Link>
        </div>
      </section>
    </div>
  )
}
