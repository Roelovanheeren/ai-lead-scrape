import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Download, 
  Filter, 
  Search, 
  Eye, 
  CheckCircle, 
  AlertCircle, 
  Clock,
  Building,
  Users,
  Mail,
  Phone,
  MapPin,
  ExternalLink,
  Star,
  StarOff,
  MoreHorizontal,
  ArrowUpDown,
  ChevronDown,
  ChevronUp,
  Linkedin
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { apiClient, Lead } from '@/lib/api'
import { cn } from '@/lib/utils'

interface ResearchResult {
  id: string
  job_id: string
  company_name: string
  industry: string
  location: string
  company_size: string
  website: string
  description: string
  contacts: Contact[]
  signals: string[]
  confidence_score: number
  last_updated: string
  source_urls: string[]
}

interface Contact {
  id: string
  name: string
  title: string
  email: string
  phone?: string
  linkedin?: string
  verified: boolean
  source: string
}

// Mock data for demonstration
const mockResults: ResearchResult[] = [
  {
    id: '1',
    job_id: 'job-001',
    company_name: 'TechCorp Inc.',
    industry: 'Technology',
    location: 'San Francisco, CA',
    company_size: '201-500',
    website: 'https://techcorp.com',
    description: 'Leading AI startup focused on machine learning solutions for enterprise clients.',
    contacts: [
      {
        id: 'c1',
        name: 'Sarah Johnson',
        title: 'VP of Engineering',
        email: 'sarah.johnson@techcorp.com',
        phone: '+1 (555) 123-4567',
        linkedin: 'https://linkedin.com/in/sarahjohnson',
        verified: true,
        source: 'LinkedIn'
      },
      {
        id: 'c2',
        name: 'Michael Chen',
        title: 'CTO',
        email: 'm.chen@techcorp.com',
        phone: '+1 (555) 234-5678',
        linkedin: 'https://linkedin.com/in/michaelchen',
        verified: true,
        source: 'Company Website'
      }
    ],
    signals: ['Series B', 'AI/ML', 'Enterprise', 'Growing'],
    confidence_score: 0.92,
    last_updated: '2024-01-15T10:30:00Z',
    source_urls: ['https://techcorp.com', 'https://linkedin.com/company/techcorp']
  },
  {
    id: '2',
    job_id: 'job-001',
    company_name: 'DataFlow Systems',
    industry: 'Technology',
    location: 'Austin, TX',
    company_size: '51-200',
    website: 'https://dataflow.com',
    description: 'Data analytics platform for mid-market companies.',
    contacts: [
      {
        id: 'c3',
        name: 'Emily Rodriguez',
        title: 'Head of Product',
        email: 'emily@dataflow.com',
        phone: '+1 (555) 345-6789',
        linkedin: 'https://linkedin.com/in/emilyrodriguez',
        verified: false,
        source: 'Google Search'
      }
    ],
    signals: ['Series A', 'Data Analytics', 'Mid-Market', 'B2B'],
    confidence_score: 0.78,
    last_updated: '2024-01-15T11:15:00Z',
    source_urls: ['https://dataflow.com', 'https://crunchbase.com/dataflow']
  }
]

export default function ResultsViewer() {
  const [results, setResults] = useState<ResearchResult[]>(mockResults)
  const [filteredResults, setFilteredResults] = useState<ResearchResult[]>(mockResults)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedResults, setSelectedResults] = useState<string[]>([])
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' } | null>(null)
  const [filterIndustry, setFilterIndustry] = useState('all')
  const [filterConfidence, setFilterConfidence] = useState('all')
  const [activeTab, setActiveTab] = useState('companies')

  // Filter and search results
  useEffect(() => {
    let filtered = results.filter(result => {
      const matchesSearch = 
        result.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        result.industry.toLowerCase().includes(searchTerm.toLowerCase()) ||
        result.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
        result.description.toLowerCase().includes(searchTerm.toLowerCase())
      
      const matchesIndustry = filterIndustry === 'all' || result.industry === filterIndustry
      const matchesConfidence = filterConfidence === 'all' || 
        (filterConfidence === 'high' && result.confidence_score >= 0.8) ||
        (filterConfidence === 'medium' && result.confidence_score >= 0.6 && result.confidence_score < 0.8) ||
        (filterConfidence === 'low' && result.confidence_score < 0.6)
      
      return matchesSearch && matchesIndustry && matchesConfidence
    })

    // Sort results
    if (sortConfig) {
      filtered.sort((a, b) => {
        const aValue = a[sortConfig.key as keyof ResearchResult]
        const bValue = b[sortConfig.key as keyof ResearchResult]
        
        if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1
        if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1
        return 0
      })
    }

    setFilteredResults(filtered)
  }, [results, searchTerm, filterIndustry, filterConfidence, sortConfig])

  const handleSort = (key: string) => {
    setSortConfig(prev => ({
      key,
      direction: prev?.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }))
  }

  const toggleSelectResult = (resultId: string) => {
    setSelectedResults(prev => 
      prev.includes(resultId) 
        ? prev.filter(id => id !== resultId)
        : [...prev, resultId]
    )
  }

  const toggleSelectAll = () => {
    setSelectedResults(prev => 
      prev.length === filteredResults.length 
        ? [] 
        : filteredResults.map(result => result.id)
    )
  }

  const getSortIcon = (key: string) => {
    if (sortConfig?.key !== key) return <ArrowUpDown className="h-4 w-4 text-muted" />
    return sortConfig.direction === 'asc' ? 
      <ChevronUp className="h-4 w-4" /> : 
      <ChevronDown className="h-4 w-4" />
  }

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-500'
    if (score >= 0.6) return 'text-yellow-500'
    return 'text-red-500'
  }

  const getConfidenceBadge = (score: number) => {
    if (score >= 0.8) return 'success'
    if (score >= 0.6) return 'warning'
    return 'destructive'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Research Results</h1>
          <p className="text-muted mt-1">View and analyze your research findings</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Results
          </Button>
          <Button className="shadow-glow">
            <Filter className="h-4 w-4 mr-2" />
            Advanced Filters
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <Card className="shadow-glow">
        <CardContent className="p-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted" />
              <Input
                placeholder="Search companies, industries, locations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex items-center gap-2">
              <select
                value={filterIndustry}
                onChange={(e) => setFilterIndustry(e.target.value)}
                className="rounded-xl bg-white/5 border border-white/10 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand/50"
              >
                <option value="all">All Industries</option>
                <option value="Technology">Technology</option>
                <option value="Healthcare">Healthcare</option>
                <option value="Finance">Finance</option>
                <option value="Manufacturing">Manufacturing</option>
              </select>
              <select
                value={filterConfidence}
                onChange={(e) => setFilterConfidence(e.target.value)}
                className="rounded-xl bg-white/5 border border-white/10 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand/50"
              >
                <option value="all">All Confidence</option>
                <option value="high">High (80%+)</option>
                <option value="medium">Medium (60-79%)</option>
                <option value="low">Low (under 60%)</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Batch Actions */}
      {selectedResults.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-brand/10 border border-brand/20 rounded-xl p-4"
        >
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">
              {selectedResults.length} result{selectedResults.length > 1 ? 's' : ''} selected
            </span>
            <div className="flex items-center gap-2">
              <Button size="sm" variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Export Selected
              </Button>
              <Button size="sm" variant="outline">
                <Users className="h-4 w-4 mr-2" />
                Add to Campaign
              </Button>
              <Button size="sm" variant="outline" onClick={() => setSelectedResults([])}>
                Clear Selection
              </Button>
            </div>
          </div>
        </motion.div>
      )}

      {/* Results Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="companies">Companies</TabsTrigger>
          <TabsTrigger value="contacts">Contacts</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Companies Tab */}
        <TabsContent value="companies" className="space-y-4">
          <Card className="shadow-glow">
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-white/5 border-b border-white/10">
                    <tr>
                      <th className="w-12 p-4">
                        <input
                          type="checkbox"
                          checked={selectedResults.length === filteredResults.length && filteredResults.length > 0}
                          onChange={toggleSelectAll}
                          className="rounded border-white/20"
                        />
                      </th>
                      <th className="text-left p-4">
                        <button
                          onClick={() => handleSort('company_name')}
                          className="flex items-center gap-2 font-medium hover:text-brand transition-colors"
                        >
                          Company {getSortIcon('company_name')}
                        </button>
                      </th>
                      <th className="text-left p-4">Industry</th>
                      <th className="text-left p-4">Location</th>
                      <th className="text-left p-4">Contacts</th>
                      <th className="text-left p-4">Confidence</th>
                      <th className="text-left p-4">Last Updated</th>
                      <th className="w-12 p-4"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredResults.map((result) => (
                      <motion.tr
                        key={result.id}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="border-b border-white/5 hover:bg-white/5 transition-colors"
                      >
                        <td className="p-4">
                          <input
                            type="checkbox"
                            checked={selectedResults.includes(result.id)}
                            onChange={() => toggleSelectResult(result.id)}
                            className="rounded border-white/20"
                          />
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-3">
                            <div className="h-10 w-10 rounded-lg bg-brand/20 flex items-center justify-center">
                              <Building className="h-5 w-5 text-brand" />
                            </div>
                            <div>
                              <div className="font-medium">{result.company_name}</div>
                              <div className="text-sm text-muted">{result.company_size} employees</div>
                            </div>
                          </div>
                        </td>
                        <td className="p-4">
                          <Badge variant="outline">{result.industry}</Badge>
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-1">
                            <MapPin className="h-4 w-4 text-muted" />
                            <span className="text-sm">{result.location}</span>
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-1">
                            <Users className="h-4 w-4 text-muted" />
                            <span className="text-sm">{result.contacts.length}</span>
                          </div>
                        </td>
                        <td className="p-4">
                          <Badge variant={getConfidenceBadge(result.confidence_score)}>
                            {Math.round(result.confidence_score * 100)}%
                          </Badge>
                        </td>
                        <td className="p-4">
                          <span className="text-sm text-muted">
                            {new Date(result.last_updated).toLocaleDateString()}
                          </span>
                        </td>
                        <td className="p-4">
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Contacts Tab */}
        <TabsContent value="contacts" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredResults.flatMap(result => result.contacts).map((contact) => (
              <Card key={contact.id} className="shadow-glow">
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <div className="h-10 w-10 rounded-full bg-brand/20 flex items-center justify-center">
                      <span className="text-sm font-medium text-brand">
                        {contact.name.split(' ').map(n => n[0]).join('')}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium truncate">{contact.name}</h3>
                      <p className="text-sm text-muted truncate">{contact.title}</p>
                      <div className="flex items-center gap-2 mt-2">
                        {contact.verified ? (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : (
                          <AlertCircle className="h-4 w-4 text-yellow-500" />
                        )}
                        <span className="text-xs text-muted">{contact.source}</span>
                      </div>
                    </div>
                  </div>
                  <div className="mt-3 space-y-1">
                    <div className="flex items-center gap-2 text-sm">
                      <Mail className="h-4 w-4 text-muted" />
                      <span className="truncate">{contact.email}</span>
                    </div>
                    {contact.phone && (
                      <div className="flex items-center gap-2 text-sm">
                        <Phone className="h-4 w-4 text-muted" />
                        <span>{contact.phone}</span>
                      </div>
                    )}
                    {contact.linkedin && (
                      <a
                        href={contact.linkedin}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 text-sm text-brand hover:text-brand/80 transition-colors"
                      >
                        <Linkedin className="h-4 w-4" />
                        <span>LinkedIn</span>
                      </a>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="shadow-glow">
              <CardContent className="p-6">
                <div className="flex items-center gap-3">
                  <Building className="h-8 w-8 text-brand" />
                  <div>
                    <p className="text-sm text-muted">Total Companies</p>
                    <p className="text-2xl font-bold">{filteredResults.length}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="shadow-glow">
              <CardContent className="p-6">
                <div className="flex items-center gap-3">
                  <Users className="h-8 w-8 text-brand" />
                  <div>
                    <p className="text-sm text-muted">Total Contacts</p>
                    <p className="text-2xl font-bold">
                      {filteredResults.reduce((sum, result) => sum + result.contacts.length, 0)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="shadow-glow">
              <CardContent className="p-6">
                <div className="flex items-center gap-3">
                  <CheckCircle className="h-8 w-8 text-brand" />
                  <div>
                    <p className="text-sm text-muted">Avg Confidence</p>
                    <p className="text-2xl font-bold">
                      {Math.round(
                        filteredResults.reduce((sum, result) => sum + result.confidence_score, 0) / 
                        filteredResults.length * 100
                      )}%
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
