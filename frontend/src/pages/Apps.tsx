import { useEffect, useState } from 'react'
import { Search, Play, Code, Loader2, ChevronDown, ChevronUp } from 'lucide-react'
import { useStore } from '../store'

export default function Apps() {
  const { apps, appsLoading, fetchApps, runDryRun, dryRunLoading, dryRunOutput, dryRunError, buildApp, buildLoading } = useStore()
  const [search, setSearch] = useState('')
  const [expandedApp, setExpandedApp] = useState<string | null>(null)

  useEffect(() => {
    fetchApps()
  }, [fetchApps])

  const filteredApps = apps.filter(app =>
    app.name.toLowerCase().includes(search.toLowerCase()) ||
    app.description.toLowerCase().includes(search.toLowerCase()) ||
    app.features.some(f => f.toLowerCase().includes(search.toLowerCase()))
  )

  return (
    <div className="container" style={{ padding: 'var(--spacing-xl) var(--spacing-md)' }}>
      <header style={{ marginBottom: 'var(--spacing-xl)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--spacing-md)' }}>
        <div>
          <h1 style={{ fontSize: '1.875rem', fontWeight: 700, marginBottom: 'var(--spacing-xs)' }}>App Catalog</h1>
          <p style={{ color: 'var(--color-text-muted)' }}>{apps.length} available app templates</p>
        </div>
        <div style={{ position: 'relative', maxWidth: 400 }}>
          <Search size={18} style={{ position: 'absolute', left: 'var(--spacing-md)', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)' }} />
          <input
            type="search"
            placeholder="Search apps..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="form-input"
            style={{ paddingLeft: '40px' }}
          />
        </div>
      </header>

      {appsLoading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: 'var(--spacing-xl)' }}>
          <Loader2 size={32} className="loading-spinner" />
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: 'var(--spacing-lg)' }}>
          {filteredApps.map(app => (
            <AppCard
              key={app.name}
              app={app}
              isExpanded={expandedApp === app.name}
              onToggle={() => setExpandedApp(expandedApp === app.name ? null : app.name)}
              onDryRun={runDryRun}
              onBuild={buildApp}
              dryRunLoading={dryRunLoading}
              buildLoading={buildLoading}
            />
          ))}
        </div>
      )}

      {dryRunOutput && (
        <DryRunModal output={dryRunOutput} error={dryRunError} onClose={() => setExpandedApp(null)} />
      )}
    </div>
  )
}

function AppCard({
  app,
  isExpanded,
  onToggle,
  onDryRun,
  onBuild,
  dryRunLoading,
  buildLoading,
}: {
  app: { name: string; description: string; features: string[]; tech: string[]; api_key: string }
  isExpanded: boolean
  onToggle: () => void
  onDryRun: (name: string) => Promise<void>
  onBuild: (name: string, isUpdate?: boolean) => Promise<void>
  dryRunLoading: boolean
  buildLoading: boolean
}) {
  const handleDryRun = (e: React.MouseEvent) => {
    e.stopPropagation()
    onDryRun(app.name)
  }

  const handleBuild = (e: React.MouseEvent, isUpdate = false) => {
    e.stopPropagation()
    onBuild(app.name, isUpdate)
  }

  return (
    <div className="card" style={{ cursor: isExpanded ? 'default' : 'pointer', transition: 'border-color 0.15s', borderColor: isExpanded ? 'var(--color-primary)' : 'var(--color-border)' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 'var(--spacing-md)' }}>
        <div style={{ flex: 1 }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: 'var(--spacing-xs)' }}>{app.name}</h3>
          <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', lineHeight: 1.5 }}>{app.description}</p>
        </div>
        <button onClick={onToggle} style={{ padding: 'var(--spacing-xs)', color: 'var(--color-text-muted)' }}>
          {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </button>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--spacing-xs)', marginBottom: 'var(--spacing-md)' }}>
        {app.tech.map((t: string) => (
          <span key={t} className="badge badge-info" style={{ fontSize: '0.7rem', padding: '2px 6px' }}>{t}</span>
        ))}
      </div>

      {isExpanded && (
        <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: 'var(--spacing-md)', marginTop: 'var(--spacing-md)', animation: 'slideIn 0.2s ease' }}>
          <div style={{ marginBottom: 'var(--spacing-md)' }}>
            <h4 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: 'var(--spacing-sm)', color: 'var(--color-text-muted)' }}>Features</h4>
            <ul style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xs)' }}>
              {app.features.map((feature: string, i: number) => (
                <li key={i} style={{ fontSize: '0.8125rem', display: 'flex', alignItems: 'flex-start', gap: 'var(--spacing-sm)', color: 'var(--color-text)' }}>
                  <Code size={14} style={{ color: 'var(--color-primary)', flexShrink: 0, marginTop: 2 }} />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
          </div>
          <div style={{ display: 'flex', gap: 'var(--spacing-sm)', flexWrap: 'wrap' }}>
            <button
              onClick={handleDryRun}
              disabled={dryRunLoading}
              className="btn btn-secondary"
              style={{ flex: 1, minWidth: 140 }}
            >
              <Code size={16} />
              {dryRunLoading ? 'Running...' : 'Dry Run'}
            </button>
            <button
              onClick={e => handleBuild(e, false)}
              disabled={buildLoading}
              className="btn btn-primary"
              style={{ flex: 1, minWidth: 140 }}
            >
              <Play size={16} />
              {buildLoading ? 'Building...' : 'Build & Push'}
            </button>
            <button
              onClick={e => handleBuild(e, true)}
              disabled={buildLoading}
              className="btn btn-secondary"
              style={{ flex: 1, minWidth: 140 }}
            >
              <Code size={16} />
              Update
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function DryRunModal({ output, error, onClose }: { output: string; error: string | null; onClose: () => void }) {
  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0,0,0,0.7)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 100,
      padding: 'var(--spacing-md)',
    }} onClick={onClose}>
      <div className="card" style={{ width: '100%', maxWidth: 800, maxHeight: '80vh', display: 'flex', flexDirection: 'column' }} onClick={e => e.stopPropagation()}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--spacing-md)', paddingBottom: 'var(--spacing-md)', borderBottom: '1px solid var(--color-border)' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600 }}>Dry Run Output</h3>
          <button onClick={onClose} style={{ padding: 'var(--spacing-xs)', color: 'var(--color-text-muted)' }} aria-label="Close">
            <Code size={20} />
          </button>
        </div>
        <div style={{ flex: 1, overflow: 'auto', background: 'var(--color-code-bg)', borderRadius: 'var(--radius-md)', padding: 'var(--spacing-md)' }}>
          <pre style={{ fontSize: '0.75rem', lineHeight: 1.6, whiteSpace: 'pre-wrap', wordBreak: 'break-word', color: error ? 'var(--color-error)' : 'var(--color-text)' }}>
            {error ? `Error: ${error}\n\n${output}` : output}
          </pre>
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 'var(--spacing-md)', gap: 'var(--spacing-sm)' }}>
          <button onClick={onClose} className="btn btn-primary">Close</button>
        </div>
      </div>
    </div>
  )
}