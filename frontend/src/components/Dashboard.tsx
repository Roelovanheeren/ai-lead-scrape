import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  TrendingUp, 
  Users, 
  Briefcase, 
  Target,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  CheckCircle
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import { apiClient, DashboardMetrics } from '@/lib/api'

// Mock data
const metrics = [
  {
    label: 'Total Leads',
    value: '2,847',
    delta: '+12.5%',
    trend: 'up',
    icon: Users,
  },
  {
    label: 'Active Jobs',
    value: '23',
    delta: '+3',
    trend: 'up',
    icon: Briefcase,
  },
  {
    label: 'Success Rate',
    value: '94.2%',
    delta: '+2.1%',
    trend: 'up',
    icon: Target,
  },
  {
    label: 'Verified Contacts',
    value: '1,923',
    delta: '+8.7%',
    trend: 'up',
    icon: CheckCircle,
  },
]

const chartData = [
  { name: 'Jan', leads: 400, verified: 320, campaigns: 12 },
  { name: 'Feb', leads: 300, verified: 280, campaigns: 8 },
  { name: 'Mar', leads: 500, verified: 420, campaigns: 15 },
  { name: 'Apr', leads: 450, verified: 380, campaigns: 10 },
  { name: 'May', leads: 600, verified: 520, campaigns: 18 },
  { name: 'Jun', leads: 550, verified: 480, campaigns: 14 },
]

const sourceData = [
  { name: 'Google Search', value: 45, color: '#139187' },
  { name: 'LinkedIn', value: 25, color: '#0f736b' },
  { name: 'Company Websites', value: 20, color: '#0b5550' },
  { name: 'Other', value: 10, color: '#073734' },
]

const recentActivity = [
  { id: 1, type: 'job_completed', message: 'AI Startups Research completed', time: '2 min ago', status: 'success' },
  { id: 2, type: 'lead_verified', message: '15 new contacts verified', time: '5 min ago', status: 'success' },
  { id: 3, type: 'campaign_sent', message: 'Outreach campaign sent to 50 leads', time: '1 hour ago', status: 'success' },
  { id: 4, type: 'job_failed', message: 'Manufacturing leads job failed', time: '2 hours ago', status: 'error' },
]

function StatCard({ label, value, delta, trend, icon: Icon }: {
  label: string
  value: string
  delta: string
  trend: 'up' | 'down'
  icon: React.ComponentType<{ className?: string }>
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="hover:shadow-glow transition-all duration-200">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted">{label}</p>
              <p className="text-2xl font-bold mt-1">{value}</p>
              <div className="flex items-center gap-1 mt-2">
                {trend === 'up' ? (
                  <ArrowUpRight className="h-4 w-4 text-green-500" />
                ) : (
                  <ArrowDownRight className="h-4 w-4 text-red-500" />
                )}
                <span className={`text-sm font-medium ${
                  trend === 'up' ? 'text-green-500' : 'text-red-500'
                }`}>
                  {delta}
                </span>
                <span className="text-xs text-muted">this week</span>
              </div>
            </div>
            <div className="h-12 w-12 rounded-xl bg-brand/10 flex items-center justify-center">
              <Icon className="h-6 w-6 text-brand" />
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

function ActivityItem({ type, message, time, status }: {
  type: string
  message: string
  time: string
  status: string
}) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-green-500'
      case 'error': return 'text-red-500'
      default: return 'text-muted'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return '✓'
      case 'error': return '✗'
      default: return '•'
    }
  }

  return (
    <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-white/5 transition-colors">
      <div className={`h-2 w-2 rounded-full mt-2 ${getStatusColor(status)}`} />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium">{message}</p>
        <p className="text-xs text-muted">{time}</p>
      </div>
      <span className={`text-xs ${getStatusColor(status)}`}>
        {getStatusIcon(status)}
      </span>
    </div>
  )
}

export default function Dashboard() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true)
        const data = await apiClient.getDashboardMetrics()
        setMetrics(data)
      } catch (err) {
        console.error('Failed to fetch dashboard metrics:', err)
        setError('Failed to load dashboard metrics')
        // Fallback to mock data for demo
        setMetrics({
          total_leads: 2847,
          active_jobs: 23,
          success_rate: 94.2,
          verified_contacts: 1923
        })
      } finally {
        setLoading(false)
      }
    }

    fetchMetrics()
  }, [])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-white/10 rounded w-64 mb-2"></div>
          <div className="h-4 bg-white/10 rounded w-96"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="h-32 bg-white/10 rounded-2xl animate-pulse"></div>
          ))}
        </div>
      </div>
    )
  }

  const metricsData = metrics ? [
    {
      label: 'Total Leads',
      value: metrics.total_leads.toLocaleString(),
      delta: '+12.5%',
      trend: 'up' as const,
      icon: Users,
    },
    {
      label: 'Active Jobs',
      value: metrics.active_jobs.toString(),
      delta: '+3',
      trend: 'up' as const,
      icon: Briefcase,
    },
    {
      label: 'Success Rate',
      value: `${metrics.success_rate}%`,
      delta: '+2.1%',
      trend: 'up' as const,
      icon: Target,
    },
    {
      label: 'Verified Contacts',
      value: metrics.verified_contacts.toLocaleString(),
      delta: '+8.7%',
      trend: 'up' as const,
      icon: CheckCircle,
    },
  ] : []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted mt-1">Welcome back! Here's what's happening with your lead generation.</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="flex items-center gap-1">
            <Activity className="h-3 w-3" />
            All systems operational
          </Badge>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metricsData.map((metric, index) => (
          <motion.div
            key={metric.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <StatCard {...metric} />
          </motion.div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Leads Over Time */}
        <Card>
          <CardHeader>
            <CardTitle>Leads Generated</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="name" stroke="rgba(255,255,255,0.6)" />
                <YAxis stroke="rgba(255,255,255,0.6)" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(18,19,20,0.9)', 
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '12px'
                  }} 
                />
                <Area 
                  type="monotone" 
                  dataKey="leads" 
                  stackId="1" 
                  stroke="#139187" 
                  fill="rgba(19,145,135,0.2)" 
                />
                <Area 
                  type="monotone" 
                  dataKey="verified" 
                  stackId="1" 
                  stroke="#0f736b" 
                  fill="rgba(15,115,107,0.2)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Lead Sources */}
        <Card>
          <CardHeader>
            <CardTitle>Lead Sources</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={sourceData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {sourceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(18,19,20,0.9)', 
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '12px'
                  }} 
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {sourceData.map((source, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div 
                      className="h-3 w-3 rounded-full" 
                      style={{ backgroundColor: source.color }}
                    />
                    <span className="text-sm">{source.name}</span>
                  </div>
                  <span className="text-sm font-medium">{source.value}%</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-1">
            {recentActivity.map((activity) => (
              <ActivityItem key={activity.id} {...activity} />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
