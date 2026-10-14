import { useEffect, useState } from 'react'
import { Loader2, CheckCircle, AlertCircle, ChevronLeft, ChevronRight, Filter, X } from 'lucide-react'
import { useStore } from '../store'
import { formatDistanceToNow } from 'date-fns'

export default function Audit() {
  const { auditLogs, auditLogsLoading, auditLogsTotal, auditLogsPage, fetchAuditLogs } = useStore()
  const [page, setPage] = useState(auditLogsPage)
  const [limit] = useState(100)
  const [actionFilter, setActionFilter] = useState<string>('')
  const [successFilter, setSuccessFilter] = useState<'all' | 'true' | 'false'>('all')

  useEffect(() => {
    fetchAuditLogs(page, limit)
  }, [fetchAuditLogs, page, limit])

  const totalPages = Math.ceil(auditLogsTotal / limit) || 1
  const uniqueActions = Object.keys(
    auditLogs.reduce((acc: Record<string, true>, log) => {
      acc[log.action] = true
      return acc
    }, {})
  ).sort()

  const filteredLogs = auditLogs.filter(log => {
    if (actionFilter && log.action !== actionFilter) return false
    if (successFilter !== 'all' && log.success.toString() !== successFilter) return false
    return true
  })

  return (
    <div className="container" style={{ padding: 'var(--spacing-xl) var(--spacing-md)' }}>
      <header style={{ marginBottom: 'var(--spacing-xl)' }}>
        <h1 style={{ fontSize: '1.875rem', fontWeight: 700, marginBottom: 'var(--spacing-xs)' }}>Audit Log</h1>
        <p style={{ color: 'var(--color-text-muted)' }}>{auditLogsTotal} total log entries</p>
      </header>

      <div className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-md)', alignItems: 'flex-end' }}>
          <div style={{ flex: 1, minWidth: 200 }}>
            <label className="form-label">Filter by Action</label>
            <select
              value={actionFilter}
              onChange={e => { setActionFilter(e.target.value); setPage(0); }}
              className="form-input"
            >
              <option value="">All Actions</option>
              {uniqueActions.map(action => (
                <option key={action} value={action}>{action}</option>
              ))}
            </select>
          </div>
          <div style={{ minWidth: 160 }}>
            <label className="form-label">Filter by Status</label>
            <select
              value={successFilter}
              onChange={e => { setSuccessFilter(e.target.value as 'all' | 'true' | 'false'); setPage(0); }}
              className="form-input"
            >
              <option value="all">All</option>
              <option value="true">Success</option>
              <option value="false">Failed</option>
            </select>
          </div>
          {(actionFilter || successFilter !== 'all') && (
            <button onClick={() => { setActionFilter(''); setSuccessFilter('all'); setPage(0); }} className="btn btn-secondary" style={{ height: 'fit-content' }}>
              <X size={16} />
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {auditLogsLoading && auditLogs.length === 0 ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: 'var(--spacing-xl)' }}>
          <Loader2 size={32} className="loading-spinner" />
        </div>
      ) : filteredLogs.length === 0 ? (
        <div className="card empty-state">
          <Filter size={48} />
          <p>No audit logs match the current filters</p>
        </div>
      ) : (
        <>
          <div className="card">
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Action</th>
                    <th>Resource</th>
                    <th>Resource ID</th>
                    <th>User</th>
                    <th>Status</th>
                    <th>Details</th>
                    <th>Time</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredLogs.map(log => (
                    <tr key={log.id}>
                      <td style={{ fontWeight: 500, fontFamily: 'var(--font-mono)', fontSize: '0.8125rem' }}>{log.action}</td>
                      <td><span className="badge badge-info">{log.resource_type}</span></td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>{log.resource_id || '—'}</td>
                      <td style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>{log.user_id || 'system'}</td>
                      <td>
                        <span className={`badge ${log.success ? 'badge-success' : 'badge-error'}`}>
                          {log.success ? <CheckCircle size={12} /> : <AlertCircle size={12} />}
                          {log.success ? 'Success' : 'Failed'}
                        </span>
                      </td>
                      <td style={{ fontSize: '0.8125rem', maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {log.details || '—'}
                      </td>
                      <td style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)' }}>
                        {log.created_at ? formatDistanceToNow(new Date(log.created_at), { addSuffix: true }) : '—'}
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