import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  ArrowLeft,
  RefreshCw,
  Users,
  Building,
  Mail,
  Phone,
  ExternalLink
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/api'

interface JobData {
  id?: string
  job_id?: string
  status: string
  progress?: number
  message: string
  created_at?: string
  completed_at?: string
  leads?: any[]
  error?: string
}

export default function JobStatus() {
  const { jobId } = useParams<{ jobId: string }>()
  const navigate = useNavigate()
  const [jobData, setJobData] = useState<JobData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (jobId) {
      fetchJobStatus()
      // Poll for updates every 2 seconds if job is still processing
      const interval = setInterval(() => {
        if (jobData?.status === 'processing' || jobData?.status === 'started') {
          fetchJobStatus()
        }
      }, 2000)
      
      return () => clearInterval(interval)
    }
  }, [jobId, jobData?.status])

  const fetchJobStatus = async () => {
    try {
      if (!jobId) return
      
      const response = await apiClient.getJobStatus(jobId)
      setJobData(response)
      setError(null)
    } catch (err) {
      setError('Failed to fetch job status')
      console.error('Error fetching job status:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-6 w-6 text-green-400" />
      case 'processing':
      case 'started':
        return <Clock className="h-6 w-6 text-blue-400" />
      case 'failed':
        return <AlertCircle className="h-6 w-6 text-red-400" />
      default:
        return <Clock className="h-6 w-6 text-gray-400" />
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

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-teal-400" />
          <p className="text-muted-foreground">Loading job status...</p>
        </div>
      </div>
    )
  }

  if (error || !jobData) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-8 w-8 mx-auto mb-4 text-red-400" />
          <p className="text-muted-foreground mb-4">{error || 'Job not found'}</p>
          <Button onClick={() => navigate('/jobs')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Jobs
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-6xl mx-auto p-6">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <Button variant="ghost" onClick={() => navigate('/jobs')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Jobs
          </Button>
          <div>
            <h1 className="text-2xl font-bold">Job Status</h1>
            <p className="text-muted-foreground">Job ID: {jobData.id || jobData.job_id}</p>
          </div>
        </div>

        {/* Status Card */}
        <Card className="mb-6 shadow-glow">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-3">
                {getStatusIcon(jobData.status)}
                Job Status
              </CardTitle>
              <Badge className={getStatusColor(jobData.status)}>
                {jobData.status.toUpperCase()}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground mb-2">Progress</p>
                <div className="w-full bg-white/10 rounded-full h-2">
                  <motion.div
                    className="bg-teal-400 h-2 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${jobData.progress || 0}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  {jobData.progress || 0}% complete
                </p>
              </div>
              
              <div>
                <p className="text-sm text-muted-foreground mb-2">Status Message</p>
                <p className="text-sm">{jobData.message}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Created</p>
                  <p>{new Date(jobData.created_at).toLocaleString()}</p>
                </div>
                {jobData.completed_at && (
                  <div>
                    <p className="text-muted-foreground">Completed</p>
                    <p>{new Date(jobData.completed_at).toLocaleString()}</p>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        {jobData.status === 'completed' && jobData.leads && (
          <Card className="shadow-glow">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Generated Leads ({jobData.leads.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {jobData.leads.slice(0, 10).map((lead, index) => (
                  <div key={lead.id} className="p-4 bg-card/50 rounded-lg border border-white/10">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium">{lead.contact_name}</h4>
                        <p className="text-sm text-muted-foreground">{lead.company}</p>
                        <div className="flex items-center gap-4 mt-2 text-sm">
                          <div className="flex items-center gap-1">
                            <Mail className="h-3 w-3" />
                            <span>{lead.email}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Phone className="h-3 w-3" />
                            <span>{lead.phone}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Building className="h-3 w-3" />
                            <span>{lead.industry}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary">
                          {Math.round(lead.confidence * 100)}% confidence
                        </Badge>
                        <Button size="sm" variant="outline">
                          <ExternalLink className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
                {jobData.leads.length > 10 && (
                  <p className="text-sm text-muted-foreground text-center">
                    ... and {jobData.leads.length - 10} more leads
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Error Display */}
        {jobData.status === 'failed' && jobData.error && (
          <Card className="shadow-glow border-red-500/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-400">
                <AlertCircle className="h-5 w-5" />
                Job Failed
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-red-400">{jobData.error}</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
