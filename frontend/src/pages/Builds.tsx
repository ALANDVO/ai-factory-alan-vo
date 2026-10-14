import { useEffect, useState } from 'react'
import { Loader2, CheckCircle, AlertCircle, Clock, GitBranch, RefreshCw, ChevronLeft, ChevronRight, ExternalLink } from 'lucide-react'
import { useStore } from '../store'
import { formatDistanceToNow } from 'date-fns'

export default function Builds() {
  const { builds, buildsLoading, buildsTotal, buildsPage, fetchBuilds, buildLoading, runCycle } = useStore()
  const [page, setPage] = useState(buildsPage)
  const [limit] = useState(50)

  useEffect(() => {
    fetchBuilds(page, limit)
  }, [fetchBuilds, page, limit])

  const totalPages = Math.ceil(buildsTotal / limit) || 1

  const statusBadge = (status: string) => {
    switch (status) {
      case 'completed': return <span className="badge badge-success"><CheckCircle size={12} /> Completed</span>
      case 'failed': return <span className="badge badge-error"><AlertCircle size={12} /> Failed</span>
      case 'building':
      case 'pushing': return <span className="badge badge-info"><Clock size={12} /> In Progress</span>
      default: return <span className="badge badge-pending"><Clock size={12} /> {status}</span>
    }
  }

  return (
    <div className="container" style={{ padding: 'var(--spacing-xl) var(--spacing-md)' }}>
      <header style={{ marginBottom: 'var(--spacing-xl)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--spacing-md)' }}>
        <div>
          <h1 style={{ fontSize: '1.875rem', fontWeight: 700, marginBottom: 'var(--spacing-xs)' }}>Build History</h1>
          <p style={{ color: 'var(--color-text-muted)' }}>{buildsTotal} total builds</p>
        </div>
        <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
          <button onClick={runCycle} disabled={buildLoading} className="btn btn-primary">
            <RefreshCw size={16} />
            {buildLoading ? 'Running...' : 'Run Cycle'}
          </button>
        </div>
      </header>

      {buildsLoading && builds.length === 0 ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: 'var(--spacing-xl)' }}>
          <Loader2 size={32} className="loading-spinner" />
        </div>
      ) : builds.length === 0 ? (
        <div className="card empty-state">
          <GitBranch size={48} />
          <p>No builds yet</p>
          <p style={{ fontSize: '0.875rem', marginTop: 'var(--spacing-xs)' }}>Run a factory cycle or build an app to get started</p>
        </div>
      ) : (
        <>
          <div className="card">
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>App</th>
                    <th>Repository</th>
                    <th>Status</th>
                    <th>Type</th>
                    <th>Commit</th>
                    <th>Time</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {builds.map(build => (
                    <tr key={build.id}>
                      <td style={{ fontWeight: 500 }}>{build.app_name}</td>
                      <td>
                        {build.github_url ? (
                          <a href={build.github_url} target="_blank" rel="noopener noreferrer" style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}>
                            <GitBranch size={14} />
                            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8125rem' }}>{build.repo_name}</span>
                          </a>
                        ) : (
                          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8125rem' }}>{build.repo_name}</span>
                        )}
                      </td>
                      <td>{statusBadge(build.status)}</td>
                      <td>
                        <span className={`badge ${build.is_update ? 'badge-info' : 'badge-success'}`}>
                          {build.is_update ? 'Update' : 'New'}
                        </span>
                      </td>
                      <td>
                        {build.commit_sha ? (
                          <code style={{ fontSize: '0.75rem' }}>{build.commit_sha.slice(0, 8)}</code>
                        ) : (
                          <span style={{ color: 'var(--color-text-muted)', fontSize: '0.8125rem' }}>—</span>
                        )}
                      </td>
                      <td style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                        {build.created_at ? formatDistanceToNow(new Date(build.created_at), { addSuffix: true }) : '—'}
                      </td>
                      <td>
                        {build.github_url && (
                          <a href={build.github_url} target="_blank" rel="noopener noreferrer" className="btn btn-secondary" style={{ padding: 'var(--spacing-xs) var(--spacing-sm)', fontSize: '0.75rem' }}>
                            <ExternalLink size={12} />
                            View
                          </a>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {totalPages > 1 && (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 'var(--spacing-md)', marginTop: 'var(--spacing-lg)' }}>
              <button
                onClick={() => setPage(p => Math.max(0, p - 1))}
                disabled={page === 0}
                className="btn btn-secondary"
                style={{ padding: 'var(--spacing-sm) var(--spacing-md)' }}
              >
                <ChevronLeft size={16} />
              </button>
              <span style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
                Page {page + 1} of {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
                disabled={page === totalPages - 1}
                className="btn btn-secondary"
                style={{ padding: 'var(--spacing-sm) var(--spacing-md)' }}
              >
                <ChevronRight size={16} />
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}