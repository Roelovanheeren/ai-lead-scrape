import React, { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Search, 
  Filter, 
  Download, 
  Mail, 
  UserPlus, 
  MoreHorizontal,
  Check,
  X,
  Eye,
  Edit,
  Trash2,
  Star,
  StarOff,
  ChevronDown,
  ChevronUp,
  ArrowUpDown,
  Plus
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

// Mock data
const mockLeads = [
  {
    id: 1,
    name: 'Sarah Johnson',
    title: 'VP of Engineering',
    company: 'TechCorp Inc.',
    email: 'sarah.johnson@techcorp.com',
    phone: '+1 (555) 123-4567',
    location: 'San Francisco, CA',
    industry: 'Technology',
    companySize: '201-500',
    source: 'LinkedIn',
    status: 'verified',
    lastSeen: '2024-01-15',
    tags: ['Decision Maker', 'Series B'],
    verified: true,
    starred: false,
  },
  {
    id: 2,
    name: 'Michael Chen',
    title: 'CTO',
    company: 'DataFlow Systems',
    email: 'm.chen@dataflow.com',
    phone: '+1 (555) 234-5678',
    location: 'Austin, TX',
    industry: 'Technology',
    companySize: '51-200',
    source: 'Google Search',
    status: 'pending',
    lastSeen: '2024-01-14',
    tags: ['Technical Lead', 'Startup'],
    verified: false,
    starred: true,
  },
  {
    id: 3,
    name: 'Emily Rodriguez',
    title: 'Head of Product',
    company: 'InnovateLab',
    email: 'emily@innovatelab.io',
    phone: '+1 (555) 345-6789',
    location: 'New York, NY',
    industry: 'Technology',
    companySize: '11-50',
    source: 'Company Website',
    status: 'verified',
    lastSeen: '2024-01-13',
    tags: ['Product Manager', 'Early Stage'],
    verified: true,
    starred: false,
  },
  {
    id: 4,
    name: 'David Park',
    title: 'CEO',
    company: 'CloudScale Technologies',
    email: 'david@cloudscale.tech',
    phone: '+1 (555) 456-7890',
    location: 'Seattle, WA',
    industry: 'Technology',
    companySize: '201-500',
    source: 'LinkedIn',
    status: 'verified',
    lastSeen: '2024-01-12',
    tags: ['C-Level', 'Enterprise'],
    verified: true,
    starred: true,
  },
  {
    id: 5,
    name: 'Lisa Thompson',
    title: 'VP of Sales',
    company: 'GrowthCorp',
    email: 'lisa.thompson@growthcorp.com',
    phone: '+1 (555) 567-8901',
    location: 'Boston, MA',
    industry: 'Technology',
    companySize: '51-200',
    source: 'Google Search',
    status: 'failed',
    lastSeen: '2024-01-11',
    tags: ['Sales Leader', 'Mid-Stage'],
    verified: false,
    starred: false,
  },
]

const statusColors = {
  verified: 'success',
  pending: 'warning',
  failed: 'destructive',
} as const

const sourceColors = {
  'LinkedIn': 'default',
  'Google Search': 'secondary',
  'Company Website': 'outline',
} as const

export default function LeadsTable() {
  const [leads, setLeads] = useState(mockLeads)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedLeads, setSelectedLeads] = useState<number[]>([])
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' } | null>(null)
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterSource, setFilterSource] = useState<string>('all')
  const [showFilters, setShowFilters] = useState(false)

  // Filter and search leads
  const filteredLeads = useMemo(() => {
    return leads.filter(lead => {
      const matchesSearch = 
        lead.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        lead.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
        lead.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        lead.title.toLowerCase().includes(searchTerm.toLowerCase())
      
      const matchesStatus = filterStatus === 'all' || lead.status === filterStatus
      const matchesSource = filterSource === 'all' || lead.source === filterSource
      
      return matchesSearch && matchesStatus && matchesSource
    })
  }, [leads, searchTerm, filterStatus, filterSource])

  // Sort leads
  const sortedLeads = useMemo(() => {
    if (!sortConfig) return filteredLeads
    
    return [...filteredLeads].sort((a, b) => {
      const aValue = a[sortConfig.key as keyof typeof a]
      const bValue = b[sortConfig.key as keyof typeof b]
      
      if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1
      if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1
      return 0
    })
  }, [filteredLeads, sortConfig])

  const handleSort = (key: string) => {
    setSortConfig(prev => ({
      key,
      direction: prev?.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }))
  }

  const toggleSelectLead = (leadId: number) => {
    setSelectedLeads(prev => 
      prev.includes(leadId) 
        ? prev.filter(id => id !== leadId)
        : [...prev, leadId]
    )
  }

  const toggleSelectAll = () => {
    setSelectedLeads(prev => 
      prev.length === filteredLeads.length 
        ? [] 
        : filteredLeads.map(lead => lead.id)
    )
  }

  const toggleStar = (leadId: number) => {
    setLeads(prev => prev.map(lead => 
      lead.id === leadId ? { ...lead, starred: !lead.starred } : lead
    ))
  }

  const handleBatchAction = (action: string) => {
    console.log(`Batch action: ${action} on leads:`, selectedLeads)
    // Here you would implement the actual batch actions
  }

  const getSortIcon = (key: string) => {
    if (sortConfig?.key !== key) return <ArrowUpDown className="h-4 w-4 text-muted" />
    return sortConfig.direction === 'asc' ? 
      <ChevronUp className="h-4 w-4" /> : 
      <ChevronDown className="h-4 w-4" />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Leads</h1>
          <p className="text-muted mt-1">Manage and organize your lead database</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={() => setShowFilters(!showFilters)}>
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </Button>
          <Button className="shadow-glow">
            <Plus className="h-4 w-4 mr-2" />
            Add Lead
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted" />
              <Input
                placeholder="Search leads by name, company, email, or title..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>

          <AnimatePresence>
            {showFilters && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-white/10"
              >
                <div>
                  <label className="block text-sm font-medium mb-2">Status</label>
                  <select
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                    className="w-full rounded-xl bg-white/5 border border-white/10 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand/50"
                  >
                    <option value="all">All Statuses</option>
                    <option value="verified">Verified</option>
                    <option value="pending">Pending</option>
                    <option value="failed">Failed</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Source</label>
                  <select
                    value={filterSource}
                    onChange={(e) => setFilterSource(e.target.value)}
                    className="w-full rounded-xl bg-white/5 border border-white/10 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand/50"
                  >
                    <option value="all">All Sources</option>
                    <option value="LinkedIn">LinkedIn</option>
                    <option value="Google Search">Google Search</option>
                    <option value="Company Website">Company Website</option>
                  </select>
                </div>
                <div className="flex items-end">
                  <Button 
                    variant="ghost" 
                    onClick={() => {
                      setFilterStatus('all')
                      setFilterSource('all')
                    }}
                  >
                    Clear Filters
                  </Button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </CardContent>
      </Card>

      {/* Batch Actions */}
      {selectedLeads.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-brand/10 border border-brand/20 rounded-xl p-4"
        >
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">
              {selectedLeads.length} lead{selectedLeads.length > 1 ? 's' : ''} selected
            </span>
            <div className="flex items-center gap-2">
              <Button size="sm" variant="outline" onClick={() => handleBatchAction('add-to-campaign')}>
                <Mail className="h-4 w-4 mr-2" />
                Add to Campaign
              </Button>
              <Button size="sm" variant="outline" onClick={() => handleBatchAction('export')}>
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
              <Button size="sm" variant="outline" onClick={() => handleBatchAction('verify')}>
                <Check className="h-4 w-4 mr-2" />
                Verify Emails
              </Button>
              <Button size="sm" variant="outline" onClick={() => setSelectedLeads([])}>
                <X className="h-4 w-4 mr-2" />
                Clear
              </Button>
            </div>
          </div>
        </motion.div>
      )}

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-white/5 border-b border-white/10">
                <tr>
                  <th className="w-12 p-4">
                    <input
                      type="checkbox"
                      checked={selectedLeads.length === filteredLeads.length && filteredLeads.length > 0}
                      onChange={toggleSelectAll}
                      className="rounded border-white/20"
                    />
                  </th>
                  <th className="text-left p-4">
                    <button
                      onClick={() => handleSort('name')}
                      className="flex items-center gap-2 font-medium hover:text-brand transition-colors"
                    >
                      Name {getSortIcon('name')}
                    </button>
                  </th>
                  <th className="text-left p-4">
                    <button
                      onClick={() => handleSort('title')}
                      className="flex items-center gap-2 font-medium hover:text-brand transition-colors"
                    >
                      Title {getSortIcon('title')}
                    </button>
                  </th>
                  <th className="text-left p-4">
                    <button
                      onClick={() => handleSort('company')}
                      className="flex items-center gap-2 font-medium hover:text-brand transition-colors"
                    >
                      Company {getSortIcon('company')}
                    </button>
                  </th>
                  <th className="text-left p-4">Email</th>
                  <th className="text-left p-4">Source</th>
                  <th className="text-left p-4">Status</th>
                  <th className="text-left p-4">Last Seen</th>
                  <th className="w-12 p-4"></th>
                </tr>
              </thead>
              <tbody>
                {sortedLeads.map((lead) => (
                  <motion.tr
                    key={lead.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="border-b border-white/5 hover:bg-white/5 transition-colors"
                  >
                    <td className="p-4">
                      <input
                        type="checkbox"
                        checked={selectedLeads.includes(lead.id)}
                        onChange={() => toggleSelectLead(lead.id)}
                        className="rounded border-white/20"
                      />
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <div className="h-8 w-8 rounded-full bg-brand/20 flex items-center justify-center">
                          <span className="text-sm font-medium text-brand">
                            {lead.name.split(' ').map(n => n[0]).join('')}
                          </span>
                        </div>
                        <div>
                          <div className="font-medium">{lead.name}</div>
                          <div className="text-sm text-muted">{lead.location}</div>
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="font-medium">{lead.title}</div>
                      <div className="text-sm text-muted">{lead.companySize} employees</div>
                    </td>
                    <td className="p-4">
                      <div className="font-medium">{lead.company}</div>
                      <div className="text-sm text-muted">{lead.industry}</div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        <span className="text-sm">{lead.email}</span>
                        {lead.verified && (
                          <Check className="h-4 w-4 text-green-500" />
                        )}
                      </div>
                    </td>
                    <td className="p-4">
                      <Badge variant={sourceColors[lead.source as keyof typeof sourceColors]}>
                        {lead.source}
                      </Badge>
                    </td>
                    <td className="p-4">
                      <Badge variant={statusColors[lead.status as keyof typeof statusColors]}>
                        {lead.status}
                      </Badge>
                    </td>
                    <td className="p-4">
                      <span className="text-sm text-muted">{lead.lastSeen}</span>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => toggleStar(lead.id)}
                          className="h-8 w-8"
                        >
                          {lead.starred ? (
                            <Star className="h-4 w-4 text-yellow-500 fill-current" />
                          ) : (
                            <StarOff className="h-4 w-4 text-muted" />
                          )}
                        </Button>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted">
          Showing {filteredLeads.length} of {leads.length} leads
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" disabled>
            Previous
          </Button>
          <Button variant="outline" size="sm" disabled>
            Next
          </Button>
        </div>
      </div>
    </div>
  )
}
