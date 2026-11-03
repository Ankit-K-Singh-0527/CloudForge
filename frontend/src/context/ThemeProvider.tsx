import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'

import { ThemeContext } from './useTheme'
import type { Theme } from './theme-types'

const STORAGE_KEY = 'cloudforge-theme'

function getSystemTheme(): 'light' | 'dark' {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function getInitialTheme(): Theme {
  const savedTheme = localStorage.getItem(STORAGE_KEY)

  if (savedTheme === 'light' || savedTheme === 'dark' || savedTheme === 'system') {
    return savedTheme
  }

  return 'system'
}

interface ThemeProviderProps {
  children: ReactNode
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [theme, setThemeState] = useState<Theme>(getInitialTheme)
  const [systemTheme, setSystemTheme] = useState<'light' | 'dark'>(getSystemTheme)

  const resolvedTheme = theme === 'system' ? systemTheme : theme

  const setTheme = useCallback((newTheme: Theme) => {
    localStorage.setItem(STORAGE_KEY, newTheme)
    setThemeState(newTheme)
  }, [])

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')

    const handleChange = (event: MediaQueryListEvent) => {
      setSystemTheme(event.matches ? 'dark' : 'light')
    }

    mediaQuery.addEventListener('change', handleChange)

    return () => {
      mediaQuery.removeEventListener('change', handleChange)
    }
  }, [])

  useEffect(() => {
    document.documentElement.classList.toggle('dark', resolvedTheme === 'dark')
    document.documentElement.style.colorScheme = resolvedTheme
  }, [resolvedTheme])

  const value = useMemo(
    () => ({ theme, resolvedTheme, setTheme }),
    [theme, resolvedTheme, setTheme],
  )

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}
