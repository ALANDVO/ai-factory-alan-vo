import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useStore } from './store'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Apps from './pages/Apps'
import Builds from './pages/Builds'
import Audit from './pages/Audit'
import Settings from './pages/Settings'

function App() {
  const { fetchApps, fetchBuilds, healthCheck } = useStore()

  useEffect(() => {
    healthCheck().then(healthy => {
      if (healthy) {
        fetchApps()
        fetchBuilds()
      }
    })
  }, [fetchApps, fetchBuilds, healthCheck])

  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="apps" element={<Apps />} />
        <Route path="builds" element={<Builds />} />
        <Route path="audit" element={<Audit />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App