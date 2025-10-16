import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Search, 
  Target, 
  Settings, 
  Play, 
  Pause, 
  RotateCcw,
  CheckCircle,
  AlertCircle,
  Clock,
  TrendingUp,
  Users,
  Building,
  MapPin,
  Filter,
  Download,
  Eye,
  Zap
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { apiClient } from '@/lib/api'
import { cn } from '@/lib/utils'
import ResultsViewer from './ResultsViewer'

interface ResearchJob {
  id: string
  name: string
  status: 'draft' | 'running' | 'completed' | 'failed'
  progress: number
  created_at: string
  updated_at: string
  results_count?: number
  error_message?: string
}

interface ResearchInput {
  // Targeting
  industry: string
  location: string
  company_size: string
  keywords: string[]
  exclude_keywords: string[]
  
  // Research Parameters
  research_depth: 'basic' | 'standard' | 'comprehensive'
  data_sources: string[]
  quality_threshold: number
  
  // Output Configuration
  target_count: number
  output_format: 'summary' | 'detailed' | 'comprehensive'
  include_contacts: boolean
  include_company_data: boolean
}

const industryOptions = [
  'Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail', 'Education',
  'Real Estate', 'Automotive', 'Energy', 'Telecommunications', 'Media', 'Other'
]

const locationOptions = [
  'United States', 'Canada', 'United Kingdom', 'Germany', 'France', 'Australia',
  'Netherlands', 'Sweden', 'Norway', 'Denmark', 'Other'
]

const companySizeOptions = [
  'Startup (1-10)', 'Small (11-50)', 'Medium (51-200)', 'Large (201-1000)', 'Enterprise (1000+)'
]

const dataSourceOptions = [
  { id: 'google_search', name: 'Google Search', enabled: true },
  { id: 'linkedin', name: 'LinkedIn', enabled: true },
  { id: 'company_websites', name: 'Company Websites', enabled: true },
  { id: 'apollo', name: 'Apollo.io', enabled: false },
  { id: 'clearbit', name: 'Clearbit', enabled: false },
  { id: 'hunter', name: 'Hunter.io', enabled: false },
]

export default function ResearchDashboard() {
  const [activeTab, setActiveTab] = useState('input')
  const [researchInput, setResearchInput] = useState<ResearchInput>({
    industry: '',
    location: '',
    company_size: '',
    keywords: [],
    exclude_keywords: [],
    research_depth: 'standard',
    data_sources: ['google_search', 'linkedin', 'company_websites'],
    quality_threshold: 0.8,
    target_count: 100,
    output_format: 'detailed',
    include_contacts: true,
    include_company_data: true,
  })
  
  const [jobs, setJobs] = useState<ResearchJob[]>([])
  const [loading, setLoading] = useState(false)
  const [keywordInput, setKeywordInput] = useState('')
  const [excludeKeywordInput, setExcludeKeywordInput] = useState('')

  // Load existing jobs
  useEffect(() => {
    loadJobs()
  }, [])

  const loadJobs = async () => {
    try {
      const response = await apiClient.getJobs()
      // Convert JobResponse[] to ResearchJob[]
      const researchJobs: ResearchJob[] = response.jobs.map((job: any) => ({
        id: job.job_id || job.id,
        name: job.prompt || 'Research Job',
        status: job.status || 'draft',
        progress: 0,
        created_at: job.created_at || new Date().toISOString(),
        updated_at: job.updated_at || new Date().toISOString(),
        results_count: 0
      }))
      setJobs(researchJobs)
    } catch (error) {
      console.error('Failed to load jobs:', error)
    }
  }

  const addKeyword = (keyword: string) => {
    if (keyword.trim() && !researchInput.keywords.includes(keyword.trim())) {
      setResearchInput(prev => ({
        ...prev,
        keywords: [...prev.keywords, keyword.trim()]
      }))
    }
  }

  const removeKeyword = (keyword: string) => {
    setResearchInput(prev => ({
      ...prev,
      keywords: prev.keywords.filter(k => k !== keyword)
    }))
  }

  const addExcludeKeyword = (keyword: string) => {
    if (keyword.trim() && !researchInput.exclude_keywords.includes(keyword.trim())) {
      setResearchInput(prev => ({
        ...prev,
        exclude_keywords: [...prev.exclude_keywords, keyword.trim()]
      }))
    }
  }

  const removeExcludeKeyword = (keyword: string) => {
    setResearchInput(prev => ({
      ...prev,
      exclude_keywords: prev.exclude_keywords.filter(k => k !== keyword)
    }))
  }

  const toggleDataSource = (sourceId: string) => {
    setResearchInput(prev => ({
      ...prev,
      data_sources: prev.data_sources.includes(sourceId)
        ? prev.data_sources.filter(s => s !== sourceId)
        : [...prev.data_sources, sourceId]
    }))
  }

  const startResearch = async () => {
    setLoading(true)
    try {
      const jobData = {
        prompt: `Research ${researchInput.industry} companies in ${researchInput.location} with ${researchInput.company_size} employees. Focus on: ${researchInput.keywords.join(', ')}. Exclude: ${researchInput.exclude_keywords.join(', ')}.`,
        target_count: researchInput.target_count,
        quality_threshold: researchInput.quality_threshold,
        industry: researchInput.industry,
        location: researchInput.location,
        company_size: researchInput.company_size,
        keywords: researchInput.keywords,
        exclude_keywords: researchInput.exclude_keywords,
        data_sources: {
          google_search: researchInput.data_sources.includes('google_search'),
          linkedin: researchInput.data_sources.includes('linkedin'),
          company_websites: researchInput.data_sources.includes('company_websites'),
          apollo: researchInput.data_sources.includes('apollo'),
          clearbit: researchInput.data_sources.includes('clearbit'),
          hunter: researchInput.data_sources.includes('hunter'),
        },
        verification_level: 'standard',
        output_format: researchInput.output_format
      }
      
      const response = await apiClient.createJob(jobData)
      console.log('Research job created:', response)
      
      // Refresh jobs list
      await loadJobs()
      setActiveTab('jobs')
    } catch (error) {
      console.error('Failed to start research:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'running': return <Clock className="h-4 w-4 text-blue-500" />
      case 'failed': return <AlertCircle className="h-4 w-4 text-red-500" />
      default: return <Clock className="h-4 w-4 text-muted" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success'
      case 'running': return 'default'
      case 'failed': return 'destructive'
      default: return 'secondary'
    }
  }

  return (
    <div className="space-y-6">
      {/* Content starts here - header handled by AppShell */}

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="input">Research Input</TabsTrigger>
          <TabsTrigger value="jobs">Active Jobs</TabsTrigger>
          <TabsTrigger value="results">Results</TabsTrigger>
        </TabsList>

        {/* Research Input Tab */}
        <TabsContent value="input" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Targeting Section */}
            <Card className="shadow-glow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5 text-brand" />
                  Targeting Parameters
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Industry</label>
                    <select
                      value={researchInput.industry}
                      onChange={(e) => setResearchInput(prev => ({ ...prev, industry: e.target.value }))}
                      className="w-full rounded-xl bg-white/5 border border-white/10 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand/50"
                    >
                      <option value="">Select industry...</option>
                      {industryOptions.map(industry => (
                        <option key={industry} value={industry}>{industry}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Location</label>
                    <select
                      value={researchInput.location}
                      onChange={(e) => setResearchInput(prev => ({ ...prev, location: e.target.value }))}
                      className="w-full rounded-xl bg-white/5 border border-white/10 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand/50"
                    >
                      <option value="">Select location...</option>
                      {locationOptions.map(location => (
                        <option key={location} value={location}>{location}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Company Size</label>
                  <select
                    value={researchInput.company_size}
                    onChange={(e) => setResearchInput(prev => ({ ...prev, company_size: e.target.value }))}
                    className="w-full rounded-xl bg-white/5 border border-white/10 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand/50"
                  >
                    <option value="">Select company size...</option>
                    {companySizeOptions.map(size => (
                      <option key={size} value={size}>{size}</option>
                    ))}
                  </select>
                </div>

                {/* Keywords */}
                <div>
                  <label className="block text-sm font-medium mb-2">Include Keywords</label>
                  <div className="flex gap-2 mb-2">
                    <Input
                      placeholder="Add keyword..."
                      value={keywordInput}
                      onChange={(e) => setKeywordInput(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          addKeyword(keywordInput)
                          setKeywordInput('')
                        }
                      }}
                    />
                    <Button onClick={() => {
                      addKeyword(keywordInput)
                      setKeywordInput('')
                    }}>
                      Add
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {researchInput.keywords.map(keyword => (
                      <Badge key={keyword} variant="secondary" className="flex items-center gap-1">
                        {keyword}
                        <button onClick={() => removeKeyword(keyword)} className="ml-1">
                          ×
                        </button>
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Exclude Keywords */}
                <div>
                  <label className="block text-sm font-medium mb-2">Exclude Keywords</label>
                  <div className="flex gap-2 mb-2">
                    <Input
                      placeholder="Add exclusion keyword..."
                      value={excludeKeywordInput}
                      onChange={(e) => setExcludeKeywordInput(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          addExcludeKeyword(excludeKeywordInput)
                          setExcludeKeywordInput('')
                        }
                      }}
                    />
                    <Button onClick={() => {
                      addExcludeKeyword(excludeKeywordInput)
                      setExcludeKeywordInput('')
                    }}>
                      Add
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {researchInput.exclude_keywords.map(keyword => (
                      <Badge key={keyword} variant="destructive" className="flex items-center gap-1">
                        {keyword}
                        <button onClick={() => removeExcludeKeyword(keyword)} className="ml-1">
                          ×
                        </button>
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Research Configuration */}
            <Card className="shadow-glow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5 text-brand" />
                  Research Configuration
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Research Depth</label>
                  <select
                    value={researchInput.research_depth}
                    onChange={(e) => setResearchInput(prev => ({ ...prev, research_depth: e.target.value as any }))}
                    className="w-full rounded-xl bg-white/5 border border-white/10 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand/50"
                  >
                    <option value="basic">Basic (Quick scan)</option>
                    <option value="standard">Standard (Comprehensive)</option>
                    <option value="comprehensive">Comprehensive (Deep analysis)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Data Sources</label>
                  <div className="grid grid-cols-2 gap-2">
                    {dataSourceOptions.map(source => (
                      <label key={source.id} className="flex items-center gap-2 p-2 rounded-lg bg-white/5 hover:bg-white/10 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={researchInput.data_sources.includes(source.id)}
                          onChange={() => toggleDataSource(source.id)}
                          className="rounded border-white/20"
                        />
                        <span className="text-sm">{source.name}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Quality Threshold: {Math.round(researchInput.quality_threshold * 100)}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={researchInput.quality_threshold}
                    onChange={(e) => setResearchInput(prev => ({ ...prev, quality_threshold: parseFloat(e.target.value) }))}
                    className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Target Count</label>
                  <Input
                    type="number"
                    value={researchInput.target_count}
                    onChange={(e) => setResearchInput(prev => ({ ...prev, target_count: parseInt(e.target.value) || 0 }))}
                    placeholder="100"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Output Format</label>
                  <select
                    value={researchInput.output_format}
                    onChange={(e) => setResearchInput(prev => ({ ...prev, output_format: e.target.value as any }))}
                    className="w-full rounded-xl bg-white/5 border border-white/10 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand/50"
                  >
                    <option value="summary">Summary</option>
                    <option value="detailed">Detailed</option>
                    <option value="comprehensive">Comprehensive</option>
                  </select>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-center gap-4">
            <Button
              onClick={startResearch}
              disabled={loading || !researchInput.industry || !researchInput.location}
              className="shadow-glow bg-brand hover:bg-brand/90 text-white px-8 py-3 text-lg"
            >
              {loading ? (
                <>
                  <RotateCcw className="h-5 w-5 mr-2 animate-spin" />
                  Starting Research...
                </>
              ) : (
                <>
                  <Play className="h-5 w-5 mr-2" />
                  Start Research Job
                </>
              )}
            </Button>
          </div>
        </TabsContent>

        {/* Active Jobs Tab */}
        <TabsContent value="jobs" className="space-y-6">
          <Card className="shadow-glow">
            <CardHeader>
              <CardTitle>Active Research Jobs</CardTitle>
            </CardHeader>
            <CardContent>
              {jobs.length === 0 ? (
                <div className="text-center py-8">
                  <Search className="h-12 w-12 text-muted mx-auto mb-4" />
                  <p className="text-muted">No research jobs found</p>
                  <p className="text-sm text-muted">Create your first research job to get started</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {jobs.map((job) => (
                    <motion.div
                      key={job.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/10"
                    >
                      <div className="flex items-center gap-4">
                        {getStatusIcon(job.status)}
                        <div>
                          <h3 className="font-medium">{job.name}</h3>
                          <p className="text-sm text-muted">
                            Created: {new Date(job.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <Badge variant={getStatusColor(job.status)}>
                          {job.status}
                        </Badge>
                        {job.status === 'running' && (
                          <div className="text-sm text-muted">
                            {job.progress}% complete
                          </div>
                        )}
                        {job.results_count && (
                          <div className="text-sm text-muted">
                            {job.results_count} results
                          </div>
                        )}
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Results Tab */}
        <TabsContent value="results" className="space-y-6">
          <ResultsViewer />
        </TabsContent>
      </Tabs>
    </div>
  )
}
