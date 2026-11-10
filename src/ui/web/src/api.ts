/// <reference types="vite/client" />

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api'

type CaseSummary = {
  case_id: string
  title: string
  tenant_id: string
  status: string
  created_at: string
  updated_at: string
}

type CaseListResponse = {
  cases: CaseSummary[]
  page: number
  page_size: number
  total: number
}

async function request(path: string, options: RequestInit = {}): Promise<any> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`${res.status} ${res.statusText} ${text}`)
  }
  if (res.status === 204) return null
  return res.json()
}

export const api = {
  // Cases
  listCases: async (params: { page?: number; page_size?: number; q?: string; status?: string } = {}): Promise<CaseListResponse> => {
    const query = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '') query.set(key, String(value))
    })
    const response = await request(`/cases/?${query.toString()}`)
    if (!Array.isArray(response?.cases)) {
      throw new Error('Neplatná odpověď API při načítání případů.')
    }

    // Starší backend vrací v seznamu pouze ID; načteme v takovém případě detail každého případu.
    const cases: CaseSummary[] = await Promise.all(response.cases.map(async (item: unknown) => {
      const summary = typeof item === 'string'
        ? await api.getCase(item)
        : item
      if (!summary || typeof summary.case_id !== 'string' || typeof summary.title !== 'string') {
        throw new Error('API vrátilo neplatný záznam případu.')
      }
      return summary as CaseSummary
    }))

    return {
      cases,
      page: Number(response.page ?? params.page ?? 1),
      page_size: Number(response.page_size ?? params.page_size ?? cases.length),
      total: Number(response.total ?? cases.length),
    }
  },
  createCase: (payload: CaseCreate) => request('/cases/', { method: 'POST', body: JSON.stringify(payload) }),
  getCase: (caseId: string) => request(`/cases/${caseId}`),
  updateCase: (caseId: string, payload: { title?: string; context?: Record<string, string> }) =>
    request(`/cases/${caseId}`, { method: 'PATCH', body: JSON.stringify(payload) }),
  deleteCase: (caseId: string) => request(`/cases/${caseId}`, { method: 'DELETE' }),
  updateCaseContext: (caseId: string, context: Record<string, unknown>) =>
    request(`/cases/${caseId}/context`, { method: 'PATCH', body: JSON.stringify(context) }),
  runCase: (caseId: string) => request(`/cases/${caseId}/run`, { method: 'POST' }),
  getLedger: (caseId: string) => request(`/cases/${caseId}/ledger`),

  // Agents
  listAgents: () => request('/agents/'),
  runAgent: (agentName: string, payload: Record<string, unknown> = {}) =>
    request(`/agents/${agentName}/run`, { method: 'POST', body: JSON.stringify(payload) }),

  // Knowledge
  listKnowledge: () => request('/knowledge/'),
  searchKnowledge: (query: string, topK = 5) =>
    request('/knowledge/search', { method: 'POST', body: JSON.stringify({ query, top_k: topK }) }),
  ingestKnowledge: (payload: Record<string, unknown>) =>
    request('/knowledge/ingest', { method: 'POST', body: JSON.stringify(payload) }),
  verifyKnowledge: (payload: Record<string, unknown>) =>
    request('/knowledge/verify', { method: 'POST', body: JSON.stringify(payload) }),

  // Quant
  quantROI: (payload: Record<string, unknown>) =>
    request('/quant/roi', { method: 'POST', body: JSON.stringify(payload) }),
  quantSensitivity: (payload: Record<string, unknown>) =>
    request('/quant/sensitivity', { method: 'POST', body: JSON.stringify(payload) }),
  quantMonteCarlo: (payload: Record<string, unknown>) =>
    request('/quant/monte-carlo', { method: 'POST', body: JSON.stringify(payload) }),
  quantAddAssumption: (payload: Record<string, unknown>) =>
    request('/quant/assumptions', { method: 'POST', body: JSON.stringify(payload) }),
}

interface CaseCreate {
  title: string
  tenant_id?: string
  plan?: string[]
  context?: Record<string, unknown>
}