import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Box, GitBranch, CheckCircle, AlertCircle, Clock, Zap, ArrowUpRight, TrendingUp } from 'lucide-react'
import { useStore } from '../store'
import { formatDistanceToNow } from 'date-fns'

export default function Dashboard() {
  const { apps, builds, buildsLoading, fetchBuilds } = useStore()

  useEffect(() => {
    fetchBuilds()
  }, [fetchBuilds])
  const totalApps = apps.length
  const totalBuilds = builds.length
  const successfulBuilds = builds.filter(b => b.status === 'completed').length
  const failedBuilds = builds.filter(b => b.status === 'failed').length
  const recentBuilds = builds.slice(0, 5)

  const statusBadge = (status: string) => {
    switch (status) {
      case 'completed': return <span className="badge badge-success"><CheckCircle size={12} /> Completed</span>
      case 'failed': return <span className="badge badge-error"><AlertCircle size={12} /> Failed</span>
      case 'building': case 'pushing': return <span className="badge badge-info"><Clock size={12} /> In Progress</span>
      default: return <span className="badge badge-pending"><Clock size={12} /> {status}</span>
    }
  }

  return (
    <div className="container" style={{ padding: 'var(--spacing-xl) var(--spacing-md)' }}>
      <header style={{ marginBottom: 'var(--spacing-xl)' }}>
        <h1 style={{ fontSize: '1.875rem', fontWeight: 700, marginBottom: 'var(--spacing-xs)' }}>Dashboard</h1>
        <p style={{ color: 'var(--color-text-muted)' }}>AI/ML Application Factory — Generate and publish complete applications</p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-xl)' }}>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: 'var(--spacing-xs)' }}>Total Apps</p>
              <p style={{ fontSize: '2rem', fontWeight: 700 }}>{totalApps}</p>
            </div>
            <Box size={32} style={{ color: 'var(--color-primary)', opacity: 0.5 }} />
          </div>
        </div>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: 'var(--spacing-xs)' }}>Total Builds</p>
              <p style={{ fontSize: '2rem', fontWeight: 700 }}>{totalBuilds}</p>
            </div>
            <GitBranch size={32} style={{ color: 'var(--color-primary)', opacity: 0.5 }} />
          </div>
        </div>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--color-success)', marginBottom: 'var(--spacing-xs)' }}>Successful</p>
              <p style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--color-success)' }}>{successfulBuilds}</p>
            </div>
            <CheckCircle size={32} style={{ color: 'var(--color-success)', opacity: 0.5 }} />
          </div>
        </div>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <p style={{ fontSize: '0.875rem', color: 'var(--color-error)', marginBottom: 'var(--spacing-xs)' }}>Failed</p>
              <p style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--color-error)' }}>{failedBuilds}</p>
            </div>
            <AlertCircle size={32} style={{ color: 'var(--color-error)', opacity: 0.5 }} />
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: 'var(--spacing-lg)' }}>
        <section className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--spacing-md)' }}>
            <h2 style={{ fontSize: '1.125rem', fontWeight: 600 }}>Recent Builds</h2>
            <Link to="/builds" style={{ fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}>
              View all <ArrowUpRight size={14} />
            </Link>
          </div>
          {buildsLoading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: 'var(--spacing-xl)' }}>
              <div className="loading-spinner" />
            </div>
          ) : builds.length === 0 ? (
            <div className="empty-state">
              <GitBranch size={48} />
              <p>No builds yet</p>
              <p style={{ fontSize: '0.875rem', marginTop: 'var(--spacing-xs)' }}>Run a factory cycle or build an app to get started</p>
            </div>
          ) : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>App</th>
                    <th>Repo</th>
                    <th>Status</th>
                    <th>Type</th>
                    <th>Time</th>
                  </tr>
                </thead>
                <tbody>
                  {recentBuilds.map(build => (
                    <tr key={build.id}>
                      <td style={{ fontWeight: 500 }}>{build.app_name}</td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8125rem' }}>{build.repo_name}</td>
                      <td>{statusBadge(build.status)}</td>
                      <td>
                        <span className={`badge ${build.is_update ? 'badge-info' : 'badge-success'}`}>
                          {build.is_update ? 'Update' : 'New'}
                        </span>
                      </td>
                      <td style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                        {build.created_at ? formatDistanceToNow(new Date(build.created_at), { addSuffix: true }) : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <section className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--spacing-md)' }}>
            <h2 style={{ fontSize: '1.125rem', fontWeight: 600 }}>Quick Actions</h2>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)' }}>
            <Link to="/apps" className="card" style={{ textDecoration: 'none', color: 'inherit', transition: 'border-color 0.15s', border: '1px solid var(--color-border)' }}>
              <Zap size={24} style={{ color: 'var(--color-primary)', marginBottom: 'var(--spacing-sm)' }} />
              <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 'var(--spacing-xs)' }}>Browse Apps</h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>View all {totalApps} available app templates</p>
            </Link>
            <Link to="/builds" className="card" style={{ textDecoration: 'none', color: 'inherit', transition: 'border-color 0.15s', border: '1px solid var(--color-border)' }}>
              <TrendingUp size={24} style={{ color: 'var(--color-success)', marginBottom: 'var(--spacing-sm)' }} />
              <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 'var(--spacing-xs)' }}>Build History</h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>View all {totalBuilds} build records</p>
            </Link>
            <Link to="/audit" className="card" style={{ textDecoration: 'none', color: 'inherit', transition: 'border-color 0.15s', border: '1px solid var(--color-border)' }}>
              <Box size={24} style={{ color: 'var(--color-warning)', marginBottom: 'var(--spacing-sm)' }} />
              <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 'var(--spacing-xs)' }}>Audit Logs</h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Review operation history</p>
            </Link>
            <Link to="/settings" className="card" style={{ textDecoration: 'none', color: 'inherit', transition: 'border-color 0.15s', border: '1px solid var(--color-border)' }}>
              <Box size={24} style={{ color: 'var(--color-text-muted)', marginBottom: 'var(--spacing-sm)' }} />
              <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 'var(--spacing-xs)' }}>Settings</h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Configure GitHub and LLM providers</p>
            </Link>
          </div>
        </section>
      </div>
    </div>
  )
}