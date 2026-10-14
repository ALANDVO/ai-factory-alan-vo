import { useEffect, useState } from 'react'
import { Loader2, Save, CheckCircle, AlertCircle, Key, Github, Database, Cpu, Eye, EyeOff } from 'lucide-react'
import { useStore } from '../store'

export default function Settings() {
  const { healthCheck, cleanAll, cleanLoading } = useStore()
  const [apiHealthy, setApiHealthy] = useState<boolean | null>(null)
  const [checkingHealth, setCheckingHealth] = useState(false)
  const [saved, setSaved] = useState(false)

  const envVars = [
    { key: 'GITHUB_TOKEN', label: 'GitHub Token', description: 'Personal access token with repo scope', sensitive: true, required: true },
    { key: 'GH_USER', label: 'GitHub User/Org', description: 'GitHub username or organization', sensitive: false, required: true, default: 'ALANDVO' },
    { key: 'EMAIL', label: 'Commit Email', description: 'Email for git commits', sensitive: false, required: true, default: 'alanvo@gmail.com' },
    { key: 'BASE', label: 'Base Directory', description: 'Local build directory', sensitive: false, required: false, default: '~/ai-factory/repos' },
    { key: 'LOG', label: 'Log File', description: 'Path to pushed.log', sensitive: false, required: false, default: '~/ai-factory/pushed.log' },
    { key: 'STATE', label: 'State File', description: 'Path to state.json', sensitive: false, required: false, default: '~/ai-factory/state.json' },
    { key: 'KEYCLOAK_URL', label: 'Keycloak URL', description: 'Keycloak server URL (e.g. https://auth.example.com)', sensitive: false, required: false },
    { key: 'KEYCLOAK_REALM', label: 'Keycloak Realm', description: 'Keycloak realm name', sensitive: false, required: false },
    { key: 'KEYCLOAK_CLIENT_ID', label: 'Keycloak Client ID', description: 'OIDC client ID', sensitive: false, required: false },
    { key: 'KEYCLOAK_CLIENT_SECRET', label: 'Keycloak Client Secret', description: 'OIDC client secret', sensitive: true, required: false },
    { key: 'OIDC_ISSUER_URL', label: 'OIDC Issuer URL', description: 'OpenID Connect issuer URL', sensitive: false, required: false },
    { key: 'LLM_PROVIDER', label: 'LLM Provider', description: 'openai-compatible, anthropic, gemini, ollama', sensitive: false, required: false },
    { key: 'LLM_MODEL', label: 'LLM Model', description: 'Model name (e.g. gpt-4o, claude-3-opus)', sensitive: false, required: false },
    { key: 'LLM_BASE_URL', label: 'LLM Base URL', description: 'Custom API base URL (for Ollama, LiteLLM, etc.)', sensitive: false, required: false },
    { key: 'LLM_API_KEY', label: 'LLM API Key', description: 'API key for LLM provider', sensitive: true, required: false },
  ]

  const checkHealth = async () => {
    setCheckingHealth(true)
    const healthy = await healthCheck()
    setApiHealthy(healthy)
    setCheckingHealth(false)
  }

  useEffect(() => {
    checkHealth()
  }, [])

  const getEnvValue = (key: string) => {
    // In a real app, this would come from a backend endpoint
    // For now, show from import.meta.env or localStorage demo
    if (typeof window !== 'undefined') {
      const viteEnv = (import.meta as unknown as Record<string, Record<string, string>>).env
      return localStorage.getItem(`env_${key}`) || viteEnv?.[`VITE_${key}`] || ''
    }
    return ''
  }

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget as HTMLFormElement)
    formData.forEach((value, key) => {
      if (value) {
        localStorage.setItem(`env_${key}`, value as string)
      }
    })
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({})

  return (
    <div className="container" style={{ padding: 'var(--spacing-xl) var(--spacing-md)', maxWidth: 900 }}>
      <header style={{ marginBottom: 'var(--spacing-xl)' }}>
        <h1 style={{ fontSize: '1.875rem', fontWeight: 700, marginBottom: 'var(--spacing-xs)' }}>Settings</h1>
        <p style={{ color: 'var(--color-text-muted)' }}>Configure environment variables and view system status</p>
      </header>

      <section className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--spacing-lg)' }}>
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600 }}>API Health</h2>
          <button onClick={checkHealth} disabled={checkingHealth} className="btn btn-secondary">
            <Loader2 size={16} className={checkingHealth ? 'loading-spinner' : ''} />
            {checkingHealth ? 'Checking...' : 'Check Health'}
          </button>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)', padding: 'var(--spacing-md)', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)' }}>
          {apiHealthy === null ? (
            <>
              <Loader2 size={20} className="loading-spinner" />
              <span>Click "Check Health" to verify API connectivity</span>
            </>
          ) : apiHealthy ? (
            <>
              <CheckCircle size={20} style={{ color: 'var(--color-success)' }} />
              <span style={{ color: 'var(--color-success)' }}>API is healthy and responding</span>
            </>
          ) : (
            <>
              <AlertCircle size={20} style={{ color: 'var(--color-error)' }} />
              <span style={{ color: 'var(--color-error)' }}>API is not responding. Check backend service.</span>
            </>
          )}
        </div>
      </section>

      <section className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--spacing-lg)' }}>
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600 }}>Environment Variables</h2>
          {saved && <span className="badge badge-success"><CheckCircle size={12} /> Saved to localStorage</span>}
        </div>
        <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: 'var(--spacing-lg)' }}>
          Values are stored in browser localStorage for demo purposes. In production, configure these on the server.
          Required variables are marked with <span style={{ color: 'var(--color-error)' }}> *</span>.
        </p>
        <form onSubmit={handleSave}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: 'var(--spacing-md)' }}>
            {envVars.map(({ key, label, description, sensitive, required, default: defaultValue }) => (
              <div key={key} className="form-group">
                <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-xs)' }}>
                  {label}
                  {required && <span style={{ color: 'var(--color-error)' }}> *</span>}
                </label>
                <div style={{ display: 'flex', gap: 'var(--spacing-xs)' }}>
                  <input
                    type={sensitive && !showSecrets[key] ? 'password' : 'text'}
                    name={key}
                    defaultValue={getEnvValue(key) || defaultValue || ''}
                    placeholder={description}
                    className="form-input"
                    style={{ flex: 1 }}
                    autoComplete="off"
                  />
                  {sensitive && (
                    <button
                      type="button"
                      onClick={() => setShowSecrets(prev => ({ ...prev, [key]: !prev[key] }))}
                      className="btn btn-secondary"
                      style={{ padding: 'var(--spacing-sm)', height: 'fit-content' }}
                      aria-label={showSecrets[key] ? 'Hide' : 'Show'}
                    >
                      {showSecrets[key] ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  )}
                </div>
                <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{description}</p>
              </div>
            ))}
          </div>
          <div style={{ marginTop: 'var(--spacing-lg)', display: 'flex', justifyContent: 'flex-end' }}>
            <button type="submit" className="btn btn-primary">
              <Save size={16} />
              Save to localStorage
            </button>
          </div>
        </form>
      </section>

      <section className="card" style={{ marginBottom: 'var(--spacing-lg)' }}>
        <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: 'var(--spacing-md)' }}>Danger Zone</h2>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)', padding: 'var(--spacing-md)', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--color-error)', borderRadius: 'var(--radius-md)' }}>
          <AlertCircle size={24} style={{ color: 'var(--color-error)' }} />
          <div style={{ flex: 1 }}>
            <p style={{ fontWeight: 500, color: 'var(--color-error)' }}>Clean All Local Artifacts</p>
            <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Removes all local build directories, state.json, and pushed.log. This cannot be undone.</p>
          </div>
          <button onClick={cleanAll} disabled={cleanLoading} className="btn btn-danger">
            <Key size={16} />
            {cleanLoading ? 'Cleaning...' : 'Clean All'}
          </button>
        </div>
      </section>

      <section className="card">
        <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: 'var(--spacing-md)' }}>System Information</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--spacing-md)' }}>
          <div style={{ padding: 'var(--spacing-md)', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-xs)' }}>
              <Github size={18} style={{ color: 'var(--color-primary)' }} />
              <span style={{ fontWeight: 500 }}>GitHub</span>
            </div>
            <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
              {getEnvValue('GH_USER') || 'ALANDVO'}
            </p>
          </div>
          <div style={{ padding: 'var(--spacing-md)', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-xs)' }}>
              <Database size={18} style={{ color: 'var(--color-success)' }} />
              <span style={{ fontWeight: 500 }}>Database</span>
            </div>
            <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>SQLite (ai_factory.db)</p>
          </div>
          <div style={{ padding: 'var(--spacing-md)', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-xs)' }}>
              <Cpu size={18} style={{ color: 'var(--color-warning)' }} />
              <span style={{ fontWeight: 500 }}>LLM Provider</span>
            </div>
            <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>
              {getEnvValue('LLM_PROVIDER') || 'Not configured'}
            </p>
          </div>
          <div style={{ padding: 'var(--spacing-md)', background: 'var(--color-bg)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-xs)' }}>
              <Key size={18} style={{ color: 'var(--color-text-muted)' }} />
              <span style={{ fontWeight: 500 }}>Version</span>
            </div>
            <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', fontFamily: 'var(--font-mono)' }}>1.1.0</p>
          </div>
        </div>
      </section>
    </div>
  )
}