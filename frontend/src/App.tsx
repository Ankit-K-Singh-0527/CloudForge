import { Navigate, Route, Routes } from 'react-router'

import ThemeToggle from '@/components/theme/ThemeToggle'
import DashboardPage from '@/pages/DashboardPage'
import ProjectsPage from '@/pages/ProjectsPage'
import DeploymentsPage from '@/pages/DeploymentsPage'
import SettingsPage from '@/pages/SettingsPage'
import NotFoundPage from '@/pages/NotFoundPage'

function App() {
  return (
    <div className="min-h-screen p-6">
      <div className="mb-6 flex justify-end">
        <ThemeToggle />
      </div>

      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/deployments" element={<DeploymentsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </div>
  )
}

export default App
