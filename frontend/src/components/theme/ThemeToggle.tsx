import { Monitor, Moon, Sun } from 'lucide-react'

import { useTheme } from '@/context/useTheme'
import type { Theme } from '@/context/theme-types'
import { Button } from '@/components/ui/button'

const themes: {
  value: Theme
  label: string
  icon: typeof Sun
}[] = [
  { value: 'light', label: 'Light', icon: Sun },
  { value: 'dark', label: 'Dark', icon: Moon },
  { value: 'system', label: 'System', icon: Monitor },
]

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <div
      className="inline-flex items-center gap-1 rounded-xl border border-border/70 bg-card/70 p-1 shadow-sm backdrop-blur"
      aria-label="Theme selection"
    >
      {themes.map(({ value, label, icon: Icon }) => (
        <Button
          key={value}
          type="button"
          size="icon"
          variant={theme === value ? 'secondary' : 'ghost'}
          aria-label={`${label} theme`}
          aria-pressed={theme === value}
          title={label}
          onClick={() => setTheme(value)}
        >
          <Icon className="size-4" />
        </Button>
      ))}
    </div>
  )
}
