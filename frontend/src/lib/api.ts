// API client for the AI Lead Generation Platform
export interface DashboardMetrics {
  total_leads: number
  active_jobs: number
  success_rate: number
  verified_contacts: number
}

export interface JobCreate {
  prompt: string
  target_count: number
  quality_threshold: number
  industry?: string
  location?: string
  company_size?: string
  keywords?: string[]
  exclude_keywords?: string[]
  data_sources?: string[] | Record<string, boolean>
  verification_level?: string
  output_format?: string
  [key: string]: any // Allow additional properties
}

export interface JobResponse {
  job_id?: string
  id?: string
  status: string
  message: string
  progress?: number
  created_at?: string
  completed_at?: string
  leads?: any[]
  error?: string
}

export interface Lead {
  id: string
  company: string
  contact_name: string
  email: string
  phone: string
  confidence: number
  source: string
  created_at: string
}

export interface Campaign {
  id: string
  name: string
  status: string
  leads_count: number
  created_at: string
}

class ApiClient {
  private baseUrl: string

  constructor() {
    // Use environment variable or detect current domain for production
    const envUrl = (import.meta as any).env?.VITE_API_URL
    if (envUrl) {
      this.baseUrl = envUrl
    } else if (typeof window !== 'undefined') {
      // In browser, use current domain
      this.baseUrl = window.location.origin
    } else {
      // Fallback for development
      this.baseUrl = 'http://localhost:8000'
    }
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  // Dashboard endpoints
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    return this.request<DashboardMetrics>('/dashboard/metrics')
  }

  // Job endpoints
  async createJob(job: JobCreate): Promise<JobResponse> {
    return this.request<JobResponse>('/jobs/', {
      method: 'POST',
      body: JSON.stringify(job),
    })
  }

  async getJobs(): Promise<{jobs: JobResponse[]}> {
    return this.request<{jobs: JobResponse[]}>('/jobs/')
  }

  async getJobStatus(jobId: string): Promise<JobResponse> {
    return this.request<JobResponse>(`/jobs/${jobId}`)
  }

  // Leads endpoints
  async getLeads(): Promise<Lead[]> {
    return this.request<Lead[]>('/leads/')
  }

  async getLeadById(id: string): Promise<Lead> {
    return this.request<Lead>(`/leads/${id}`)
  }

  // Campaigns endpoints
  async getCampaigns(): Promise<Campaign[]> {
    return this.request<Campaign[]>('/campaigns/')
  }

  async createCampaign(campaign: Omit<Campaign, 'id' | 'created_at'>): Promise<Campaign> {
    return this.request<Campaign>('/campaigns/', {
      method: 'POST',
      body: JSON.stringify(campaign),
    })
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.request<{ status: string; timestamp: string }>('/health')
  }
}

export const apiClient = new ApiClient()