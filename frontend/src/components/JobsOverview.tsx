import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Plus, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  RefreshCw,
  Eye,
  Trash2,
  Play,
  Pause,
  Users,
  Building,
  Mail,
  ExternalLink
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/api'

interface Job {
  id?: string
  job_id?: string
  status: string
  progress?: number
  message: string
  created_at?: string
  completed_at?: string
  leads?: any[]
  error?: string
  prompt?: string
  target_count?: number
}

export default function JobsOverview() {
  const navigate = useNavigate()
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadJobs()
    // Poll for updates every 5 seconds
    const interval = setInterval(loadJobs, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadJobs = async () => {
    try {
      const response = await apiClient.getJobs()
      setJobs(response.jobs || [])
      setError(null)
    } catch (err) {
      setError('Failed to load jobs')
      console.error('Error loading jobs:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-400" />
      case 'processing':
      case 'started':
        return <Clock className="h-5 w-5 text-blue-400" />
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-400" />
      default:
        return <Clock className="h-5 w-5 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500/20 text-green-400 border-green-500/30'
      case 'processing':
      case 'started':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
      case 'failed':
        return 'bg-red-500/20 text-red-400 border-red-500/30'
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const getJobDuration = (job: Job) => {
    const start = new Date(job.created_at)
    const end = job.completed_at ? new Date(job.completed_at) : new Date()
    const duration = Math.floor((end.getTime() - start.getTime()) / 1000)
    
    if (duration < 60) return `${duration}s`
    if (duration < 3600) return `${Math.floor(duration / 60)}m ${duration % 60}s`
    return `${Math.floor(duration / 3600)}h ${Math.floor((duration % 3600) / 60)}m`
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-teal-400" />
          <p className="text-muted-foreground">Loading jobs...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold">Jobs</h1>
            <p className="text-muted-foreground">Monitor your lead generation jobs</p>
          </div>
          <Button 
            onClick={() => navigate('/new-job')}
            className="shadow-glow"
          >
            <Plus className="h-4 w-4 mr-2" />
            New Job
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card className="shadow-glow">
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Building className="h-5 w-5 text-teal-400" />
                <div>
                  <p className="text-2xl font-bold">{jobs.length}</p>
                  <p className="text-sm text-muted-foreground">Total Jobs</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="shadow-glow">
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-blue-400" />
                <div>
                  <p className="text-2xl font-bold">
                    {jobs.filter(job => job.status === 'processing' || job.status === 'started').length}
                  </p>
                  <p className="text-sm text-muted-foreground">Active</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="shadow-glow">
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-400" />
                <div>
                  <p className="text-2xl font-bold">
                    {jobs.filter(job => job.status === 'completed').length}
                  </p>
                  <p className="text-sm text-muted-foreground">Completed</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="shadow-glow">
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Users className="h-5 w-5 text-purple-400" />
                <div>
                  <p className="text-2xl font-bold">
                    {jobs.reduce((total, job) => total + (job.leads?.length || 0), 0)}
                  </p>
                  <p className="text-sm text-muted-foreground">Total Leads</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Jobs List */}
        {jobs.length === 0 ? (
          <Card className="shadow-glow">
            <CardContent className="p-12 text-center">
              <Building className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-xl font-semibold mb-2">No jobs yet</h3>
              <p className="text-muted-foreground mb-6">
                Create your first lead generation job to get started
              </p>
              <Button onClick={() => navigate('/new-job')} className="shadow-glow">
                <Plus className="h-4 w-4 mr-2" />
                Create New Job
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {jobs.map((job) => (
              <motion.div
                key={job.id || job.job_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <Card className="shadow-glow hover:shadow-glow-lg transition-all duration-300">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {getStatusIcon(job.status)}
                        <div>
                          <CardTitle className="text-lg">
                            {job.prompt ? job.prompt.substring(0, 50) + '...' : 'Lead Generation Job'}
                          </CardTitle>
                          <p className="text-sm text-muted-foreground">
                            Job ID: {job.id || job.job_id}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getStatusColor(job.status)}>
                          {job.status.toUpperCase()}
                        </Badge>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => navigate(`/jobs/${job.id || job.job_id}`)}
                        >
                          <Eye className="h-4 w-4 mr-2" />
                          View
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {/* Progress Bar */}
                      {job.status === 'processing' || job.status === 'started' ? (
                        <div>
                          <div className="flex justify-between text-sm mb-2">
                            <span className="text-muted-foreground">Progress</span>
                            <span className="text-muted-foreground">{job.progress || 0}%</span>
                          </div>
                          <div className="w-full bg-white/10 rounded-full h-2">
                            <motion.div
                              className="bg-teal-400 h-2 rounded-full"
                              initial={{ width: 0 }}
                              animate={{ width: `${job.progress || 0}%` }}
                              transition={{ duration: 0.5 }}
                            />
                          </div>
                          <p className="text-sm text-muted-foreground mt-2">{job.message}</p>
                        </div>
                      ) : (
                        <p className="text-sm text-muted-foreground">{job.message}</p>
                      )}

                      {/* Job Details */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-muted-foreground">Created</p>
                          <p>{formatDate(job.created_at)}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Duration</p>
                          <p>{getJobDuration(job)}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Target Count</p>
                          <p>{job.target_count || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Leads Found</p>
                          <p className="text-teal-400 font-medium">
                            {job.leads?.length || 0}
                          </p>
                        </div>
                      </div>

                      {/* Results Preview */}
                      {job.status === 'completed' && job.leads && job.leads.length > 0 && (
                        <div className="mt-4 p-4 bg-card/50 rounded-lg border border-white/10">
                          <h4 className="font-medium mb-3 flex items-center gap-2">
                            <Users className="h-4 w-4" />
                            Sample Results ({job.leads.length} leads found)
                          </h4>
                          <div className="space-y-2">
                            {job.leads.slice(0, 3).map((lead, index) => (
                              <div key={index} className="flex items-center justify-between text-sm">
                                <div className="flex items-center gap-2">
                                  <Building className="h-3 w-3 text-muted-foreground" />
                                  <span>{lead.company}</span>
                                  <span className="text-muted-foreground">•</span>
                                  <span>{lead.contact_name}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <Mail className="h-3 w-3 text-muted-foreground" />
                                  <span className="text-muted-foreground">{lead.email}</span>
                                </div>
                              </div>
                            ))}
                            {job.leads.length > 3 && (
                              <p className="text-xs text-muted-foreground">
                                ... and {job.leads.length - 3} more leads
                              </p>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Error Display */}
                      {job.status === 'failed' && job.error && (
                        <div className="mt-4 p-4 bg-red-500/10 rounded-lg border border-red-500/20">
                          <p className="text-sm text-red-400">{job.error}</p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
