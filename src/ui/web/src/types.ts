export type CaseStatus = 'DRAFT' | 'RUNNING' | 'DONE' | 'FAILED'

export interface CaseCreate {
  title: string
  tenant_id?: string
  plan?: string[]
  context?: Record<string, unknown>
}

export interface CaseResponse {
  case_id: string
  title: string
  tenant_id: string
  context: Record<string, unknown>
  status: string
  created_at: string
  updated_at: string
}

export interface CaseDetail {
  case_id: string
  title: string
  tenant_id: string
  status: string
  plan: string[]
  completed_steps: string[]
  claims: Record<string, unknown>[]
  recommendations: Record<string, unknown>[]
  created_at: string
  updated_at: string
}

export interface AgentInfo {
  name: string
  autonomy: string
  model: string
}

export interface LedgerEntry {
  step: string
  status: string
  timestamp: string
  details?: Record<string, unknown>
}

export interface KnowledgeRecord {
  id: string
  title: string
  content: string
  source: string
  tags: string[]
}