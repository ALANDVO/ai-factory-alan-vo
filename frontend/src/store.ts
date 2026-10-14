import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface App {
  name: string
  description: string
  features: string[]
  tech: string[]
  api_key: string
}

export interface BuildRecord {
  id: number
  app_name: string
  repo_name: string
  status: string
  is_update: boolean
  error_message: string | null
  github_url: string | null
  commit_sha: string | null
  created_at: string | null
  updated_at: string | null
}

export interface AuditLog {
  id: number
  action: string
  resource_type: string
  resource_id: string | null
  user_id: string | null
  details: string | null
  ip_address: string | null
  success: boolean
  error_message: string | null
  created_at: string | null
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

interface Toast {
  id: string
  type: 'success' | 'error' | 'info' | 'warning'
  message: string
}

interface StoreState {
  // Apps
  apps: App[]
  appsLoading: boolean
  appsError: string | null
  fetchApps: () => Promise<void>

  // Build history
  builds: BuildRecord[]
  buildsLoading: boolean
  buildsError: string | null
  buildsTotal: number
  buildsPage: number
  fetchBuilds: (page?: number, limit?: number) => Promise<void>

  // Audit logs
  auditLogs: AuditLog[]
  auditLogsLoading: boolean
  auditLogsError: string | null
  auditLogsTotal: number
  auditLogsPage: number
  fetchAuditLogs: (page?: number, limit?: number) => Promise<void>

  // Dry run
  dryRunOutput: string | null
  dryRunLoading: boolean
  dryRunError: string | null
  runDryRun: (appName: string) => Promise<void>

  // Build
  buildLoading: boolean
  buildError: string | null
  buildApp: (appName: string, isUpdate?: boolean) => Promise<void>
  runCycle: () => Promise<void>

  // Clean
  cleanLoading: boolean
  cleanError: string | null
  cleanAll: () => Promise<void>

  // Toasts
  toasts: Toast[]
  addToast: (type: Toast['type'], message: string) => void
  removeToast: (id: string) => void

  // Health
  healthCheck: () => Promise<boolean>
}

const API_BASE = '/api/v1'

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }
  return response.json()
}

export const useStore = create<StoreState>()(
  persist(
    (set, get) => ({
      // Apps
      apps: [],
      appsLoading: false,
      appsError: null,
      fetchApps: async () => {
        set({ appsLoading: true, appsError: null })
        try {
          const data = await fetchJson<{ apps: App[]; total: number }>(`${API_BASE}/apps`)
          set({ apps: data.apps, appsLoading: false })
        } catch (e) {
          set({ appsError: (e as Error).message, appsLoading: false })
        }
      },

      // Builds
      builds: [],
      buildsLoading: false,
      buildsError: null,
      buildsTotal: 0,
      buildsPage: 0,
      fetchBuilds: async (page = 0, limit = 50) => {
        set({ buildsLoading: true, buildsError: null })
        try {
          const data = await fetchJson<PaginatedResponse<BuildRecord>>(
            `${API_BASE}/builds?limit=${limit}&offset=${page * limit}`
          )
          set({ builds: data.items, buildsTotal: data.total, buildsPage: page, buildsLoading: false })
        } catch (e) {
          set({ buildsError: (e as Error).message, buildsLoading: false })
        }
      },

      // Audit logs
      auditLogs: [],
      auditLogsLoading: false,
      auditLogsError: null,
      auditLogsTotal: 0,
      auditLogsPage: 0,
      fetchAuditLogs: async (page = 0, limit = 100) => {
        set({ auditLogsLoading: true, auditLogsError: null })
        try {
          const data = await fetchJson<PaginatedResponse<AuditLog>>(
            `${API_BASE}/audit?limit=${limit}&offset=${page * limit}`
          )
          set({ auditLogs: data.items, auditLogsTotal: data.total, auditLogsPage: page, auditLogsLoading: false })
        } catch (e) {
          set({ auditLogsError: (e as Error).message, auditLogsLoading: false })
        }
      },

      // Dry run
      dryRunOutput: null,
      dryRunLoading: false,
      dryRunError: null,
      runDryRun: async (appName: string) => {
        set({ dryRunLoading: true, dryRunError: null, dryRunOutput: null })
        try {
          const data = await fetchJson<{ app_name: string; output: string }>(
            `${API_BASE}/apps/${appName}/dry-run`,
            { method: 'POST' }
          )
          set({ dryRunOutput: data.output, dryRunLoading: false })
          get().addToast('success', `Dry run completed for ${appName}`)
        } catch (e) {
          set({ dryRunError: (e as Error).message, dryRunLoading: false })
          get().addToast('error', `Dry run failed: ${(e as Error).message}`)
        }
      },

      // Build
      buildLoading: false,
      buildError: null,
      buildApp: async (appName: string, isUpdate = false) => {
        set({ buildLoading: true, buildError: null })
        try {
          const data = await fetchJson<{
            success: boolean
            app_name: string
            repo_name: string
            error_message: string | null
            github_url: string | null
            commit_sha: string | null
          }>(`${API_BASE}/build`, {
            method: 'POST',
            body: JSON.stringify({ app_name: appName, is_update: isUpdate }),
          })
          set({ buildLoading: false })
          if (data.success) {
            get().addToast('success', `Build successful: ${data.repo_name}`)
            get().fetchBuilds(0)
          } else {
            get().addToast('error', `Build failed: ${data.error_message}`)
          }
        } catch (e) {
          set({ buildError: (e as Error).message, buildLoading: false })
          get().addToast('error', `Build failed: ${(e as Error).message}`)
        }
      },

      runCycle: async () => {
        set({ buildLoading: true, buildError: null })
        try {
          const data = await fetchJson<Array<{
            success: boolean
            app_name: string
            repo_name: string
            error_message: string | null
            github_url: string | null
            commit_sha: string | null
          }>>(`${API_BASE}/cycle`, { method: 'POST' })
          set({ buildLoading: false })
          for (const result of data) {
            if (result.success) {
              get().addToast('success', `Cycle: ${result.repo_name}`)
            } else {
              get().addToast('error', `Cycle failed: ${result.error_message}`)
            }
          }
          get().fetchBuilds(0)
        } catch (e) {
          set({ buildError: (e as Error).message, buildLoading: false })
          get().addToast('error', `Cycle failed: ${(e as Error).message}`)
        }
      },

      // Clean
      cleanLoading: false,
      cleanError: null,
      cleanAll: async () => {
        set({ cleanLoading: true, cleanError: null })
        try {
          await fetchJson<{ status: string; message: string }>(`${API_BASE}/clean`, { method: 'POST' })
          set({ cleanLoading: false })
          get().addToast('success', 'Clean completed')
          get().fetchBuilds(0)
        } catch (e) {
          set({ cleanError: (e as Error).message, cleanLoading: false })
          get().addToast('error', `Clean failed: ${(e as Error).message}`)
        }
      },

      // Toasts
      toasts: [],
      addToast: (type, message) => {
        const id = Date.now().toString()
        set({ toasts: [...get().toasts, { id, type, message }] })
        setTimeout(() => get().removeToast(id), 5000)
      },
      removeToast: (id) => {
        set({ toasts: get().toasts.filter(t => t.id !== id) })
      },

      // Health
      healthCheck: async () => {
        try {
          await fetchJson<{ status: string; version: string }>(`${API_BASE}/health`)
          return true
        } catch {
          return false
        }
      },
    }),
    { name: 'ai-factory-store', partialize: _ => ({}) } // Don't persist anything
  )
)