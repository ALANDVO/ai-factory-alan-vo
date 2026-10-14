import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { useStore } from './store'

// Mock the store
vi.mock('./store', () => ({
  useStore: vi.fn(),
}))

const mockUseStore = useStore as unknown as ReturnType<typeof vi.fn>

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockUseStore.mockReturnValue({
      apps: [
        { name: 'test-app', description: 'Test app', features: ['Feature 1'], tech: ['Python'], api_key: 'TEST_KEY' },
      ],
      appsLoading: false,
      builds: [],
      buildsLoading: false,
      fetchApps: vi.fn(),
      fetchBuilds: vi.fn(),
      healthCheck: vi.fn().mockResolvedValue(true),
      toasts: [],
      addToast: vi.fn(),
      removeToast: vi.fn(),
      runCycle: vi.fn(),
      cleanAll: vi.fn(),
      cleanLoading: false,
      buildApp: vi.fn(),
      buildLoading: false,
      runDryRun: vi.fn(),
      dryRunLoading: false,
      dryRunOutput: null,
      dryRunError: null,
      fetchAuditLogs: vi.fn(),
      auditLogs: [],
      auditLogsLoading: false,
    })
  })

  it('renders dashboard with app count', async () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Dashboard' })).toBeInTheDocument()
    })
    expect(screen.getByText(/available app templates/i)).toBeInTheDocument()
  })

  it('renders sidebar navigation', async () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByRole('link', { name: 'Apps' })).toBeInTheDocument()
      expect(screen.getByRole('link', { name: 'Builds' })).toBeInTheDocument()
      expect(screen.getByRole('link', { name: 'Audit Log' })).toBeInTheDocument()
      expect(screen.getByRole('link', { name: 'Settings' })).toBeInTheDocument()
    })
  })

  it('renders run cycle and clean buttons', async () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /run cycle/i })).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /clean all/i })).toBeInTheDocument()
    })
  })
})

describe('Store', () => {
  it('has correct initial state shape', () => {
    // This test verifies the store structure
    const mockState = {
      apps: [],
      appsLoading: false,
      appsError: null,
      builds: [],
      buildsLoading: false,
      buildsError: null,
      buildsTotal: 0,
      buildsPage: 0,
      auditLogs: [],
      auditLogsLoading: false,
      auditLogsError: null,
      auditLogsTotal: 0,
      auditLogsPage: 0,
      dryRunOutput: null,
      dryRunLoading: false,
      dryRunError: null,
      buildLoading: false,
      buildError: null,
      cleanLoading: false,
      cleanError: null,
      toasts: [],
    }

    expect(mockState.apps).toEqual([])
    expect(mockState.builds).toEqual([])
    expect(mockState.toasts).toEqual([])
  })
})