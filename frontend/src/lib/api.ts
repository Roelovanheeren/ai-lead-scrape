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
  linkedin_url?: string
  linkedin?: string
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
    console.log(`🔍 API Request: ${options.method || 'GET'} ${url}`)
    console.log(`🔍 Base URL: ${this.baseUrl}`)
    console.log(`🔍 Endpoint: ${endpoint}`)
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    console.log(`🔍 Response Status: ${response.status} ${response.statusText}`)
    console.log(`🔍 Response Headers:`, Object.fromEntries(response.headers.entries()))
    
    if (!response.ok) {
      const errorText = await response.text()
      console.error(`❌ API Error: ${response.status} ${response.statusText}`)
      console.error(`❌ Error Response:`, errorText)
      throw new Error(`API request failed: ${response.status} ${response.statusText}`)
    }

    const responseText = await response.text()
    console.log(`🔍 Response Text (first 200 chars):`, responseText.substring(0, 200))
    
    try {
      const jsonData = JSON.parse(responseText)
      console.log(`✅ Parsed JSON:`, jsonData)
      return jsonData
    } catch (parseError) {
      console.error(`❌ JSON Parse Error:`, parseError)
      console.error(`❌ Response was not JSON:`, responseText)
      throw new Error(`Invalid JSON response: ${parseError}`)
    }
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
