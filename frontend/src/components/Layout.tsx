import { Outlet, NavLink } from 'react-router-dom'
import { Layout as LayoutIcon, Box, GitBranch, History, Settings, Zap, X } from 'lucide-react'
import { useStore } from '../store'
const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutIcon },
  { path: '/apps', label: 'Apps', icon: Box },
  { path: '/builds', label: 'Builds', icon: GitBranch },
  { path: '/audit', label: 'Audit Log', icon: History },
  { path: '/settings', label: 'Settings', icon: Settings },
]

export default function Layout() {
  const { toasts, removeToast, buildLoading, runCycle, cleanAll, cleanLoading } = useStore()

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <aside style={{
        width: 260,
        background: 'var(--color-bg-elevated)',
        borderRight: '1px solid var(--color-border)',
        display: 'flex',
        flexDirection: 'column',
        padding: 'var(--spacing-md)',
        gap: 'var(--spacing-md)',
      }}>
        <div style={{ padding: 'var(--spacing-md)', borderBottom: '1px solid var(--color-border)', marginBottom: 'var(--spacing-sm)' }}>
          <NavLink to="/" style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', color: 'var(--color-text)', fontWeight: 700, fontSize: '1.125rem' }}>
            <Zap size={24} />
            ai-factory
          </NavLink>
          <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: 'var(--spacing-xs)' }}>AI/ML App Factory</p>
        </div>
        <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
          {navItems.map(item => (
            <NavLink
              key={item.path}
              to={item.path}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--spacing-sm)',
                padding: 'var(--spacing-sm) var(--spacing-md)',
                borderRadius: 'var(--radius-md)',
                color: isActive ? 'var(--color-primary)' : 'var(--color-text-muted)',
                background: isActive ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                fontWeight: isActive ? 600 : 400,
                fontSize: '0.875rem',
                transition: 'all 0.15s ease',
              })}
            >
              <item.icon size={18} />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: 'var(--spacing-md)', display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)' }}>
          <button
            onClick={runCycle}
            disabled={buildLoading}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 'var(--spacing-sm)',
              padding: 'var(--spacing-sm) var(--spacing-md)',
              borderRadius: 'var(--radius-md)',
              background: 'var(--color-primary)',
              color: 'white',
              fontWeight: 500,
              fontSize: '0.875rem',
              opacity: buildLoading ? 0.7 : 1,
            }}
          >
            <Zap size={16} />
            Run Cycle
          </button>
          <button
            onClick={cleanAll}
            disabled={cleanLoading}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 'var(--spacing-sm)',
              padding: 'var(--spacing-sm) var(--spacing-md)',
              borderRadius: 'var(--radius-md)',
              background: 'transparent',
              color: 'var(--color-error)',
              border: '1px solid var(--color-error)',
              fontWeight: 500,
              fontSize: '0.875rem',
              opacity: cleanLoading ? 0.7 : 1,
            }}
          >
            <X size={16} />
            Clean All
          </button>
        </div>
      </aside>
      <main style={{ flex: 1, overflow: 'auto' }}>
        <Outlet />
      </main>
      <div className="toast-container" role="region" aria-label="Notifications">
        {toasts.map(toast => (
          <div key={toast.id} className={`toast toast-${toast.type}`} role="alert">
            {toast.message}
            <button onClick={() => removeToast(toast.id)} style={{ marginLeft: 'auto', opacity: 0.7, padding: 'var(--spacing-xs)' }}>
              <X size={16} />
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}