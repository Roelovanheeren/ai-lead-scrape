import React, { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Upload, 
  FileText, 
  Bot, 
  Users, 
  Target, 
  Brain,
  MessageCircle,
  Send,
  X,
  CheckCircle,
  RefreshCw,
  Table,
  Link,
  Database,
  RotateCcw,
  Edit,
  Trash2,
  ExternalLink
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'

interface UploadedDocument {
  id: string
  name: string
  size: number
  type: string
  content?: string
  uploadedAt: Date
}

interface ChatMessage {
  id: string
  type: 'user' | 'ai'
  content: string
  timestamp: Date
}

interface AudienceProfile {
  demographics: {
    ageRange: string
    gender: string
    location: string
    income: string
  }
  psychographics: {
    interests: string[]
    painPoints: string[]
    goals: string[]
    values: string[]
  }
  firmographics: {
    companySize: string
    industry: string[]
    jobTitles: string[]
    technology: string[]
  }
  behavior: {
    channels: string[]
    content: string[]
    timing: string
  }
}

interface GoogleSheet {
  id: string
  name: string
  url: string
  columns: string[]
  lastSync: Date
  isConnected: boolean
}

interface LeadData {
  company: string
  contact: string
  email: string
  phone: string
  title: string
  industry: string
  location: string
  message: string
  confidence: number
  source: string
}

export default function TargetAudienceIntelligence() {
  const [activeTab, setActiveTab] = useState<'upload' | 'chat' | 'profile' | 'sheets'>('upload')
  const [uploadedDocs, setUploadedDocs] = useState<UploadedDocument[]>([])
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      type: 'ai',
      content: "Hi! I'm your AI Audience Intelligence Assistant. I'll help you discover your perfect target audience. Let's start with your business - what product or service are you offering?",
      timestamp: new Date()
    }
  ])
  const [currentMessage, setCurrentMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [audienceProfile, setAudienceProfile] = useState<AudienceProfile>({
    demographics: {
      ageRange: '',
      gender: '',
      location: '',
      income: ''
    },
    psychographics: {
      interests: [],
      painPoints: [],
      goals: [],
      values: []
    },
    firmographics: {
      companySize: '',
      industry: [],
      jobTitles: [],
      technology: []
    },
    behavior: {
      channels: [],
      content: [],
      timing: ''
    }
  })
  const [isGeneratingProfile, setIsGeneratingProfile] = useState(false)
  const [connectedSheets, setConnectedSheets] = useState<GoogleSheet[]>([])
  const [newSheetUrl, setNewSheetUrl] = useState('')
  const [isConnectingSheet, setIsConnectingSheet] = useState(false)
  const [isSyncing, setIsSyncing] = useState(false)
  const [leadData, setLeadData] = useState<LeadData[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files) return

    Array.from(files).forEach(file => {
      const newDoc: UploadedDocument = {
        id: Math.random().toString(36).substr(2, 9),
        name: file.name,
        size: file.size,
        type: file.type,
        uploadedAt: new Date()
      }
      setUploadedDocs(prev => [...prev, newDoc])
    })
  }

  const removeDocument = (id: string) => {
    setUploadedDocs(prev => prev.filter(doc => doc.id !== id))
  }

  const sendMessage = async () => {
    if (!currentMessage.trim()) return

    const userMessage: ChatMessage = {
      id: Math.random().toString(36).substr(2, 9),
      type: 'user',
      content: currentMessage,
      timestamp: new Date()
    }

    setChatMessages(prev => [...prev, userMessage])
    setCurrentMessage('')
    setIsTyping(true)

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: ChatMessage = {
        id: Math.random().toString(36).substr(2, 9),
        type: 'ai',
        content: generateAIResponse(currentMessage),
        timestamp: new Date()
      }
      setChatMessages(prev => [...prev, aiResponse])
      setIsTyping(false)
    }, 1500)
  }

  const generateAIResponse = (userMessage: string): string => {
    const responses = [
      "That's interesting! Can you tell me more about the main problem your product solves?",
      "Great! What's the typical company size of your ideal customers?",
      "Perfect! What industry or industries are you targeting?",
      "Excellent! What job titles or roles would be most interested in your solution?",
      "Interesting! What's the biggest challenge your target audience faces?",
      "Good point! What channels do you think your audience uses most?",
      "That's helpful! What's the typical budget range for your solution?",
      "Great insight! What technology stack does your ideal customer use?",
      "Perfect! What's the decision-making process like for your customers?",
      "Excellent! What content types does your audience engage with most?"
    ]
    return responses[Math.floor(Math.random() * responses.length)]
  }

  const generateAudienceProfile = async () => {
    setIsGeneratingProfile(true)
    
    // Simulate AI analysis
    setTimeout(() => {
      setAudienceProfile({
        demographics: {
          ageRange: '25-45',
          gender: 'Mixed',
          location: 'North America, Europe',
          income: '$50k-$150k'
        },
        psychographics: {
          interests: ['Technology', 'Innovation', 'Efficiency'],
          painPoints: ['Manual processes', 'Data silos', 'Time constraints'],
          goals: ['Increase productivity', 'Reduce costs', 'Scale operations'],
          values: ['Innovation', 'Reliability', 'Customer success']
        },
        firmographics: {
          companySize: '50-500 employees',
          industry: ['Technology', 'SaaS', 'E-commerce'],
          jobTitles: ['CTO', 'VP Engineering', 'Product Manager'],
          technology: ['Cloud platforms', 'APIs', 'Modern frameworks']
        },
        behavior: {
          channels: ['LinkedIn', 'Industry forums', 'Webinars'],
          content: ['Technical blogs', 'Case studies', 'Product demos'],
          timing: 'Q4 planning, Q1 implementation'
        }
      })
      setIsGeneratingProfile(false)
    }, 3000)
  }

  const connectGoogleSheet = async () => {
    if (!newSheetUrl.trim()) return
    
    setIsConnectingSheet(true)
    
    // Simulate Google Sheets API connection
    setTimeout(() => {
      const newSheet: GoogleSheet = {
        id: Math.random().toString(36).substr(2, 9),
        name: 'Lead Database',
        url: newSheetUrl,
        columns: ['Company', 'Contact', 'Email', 'Phone', 'Title', 'Industry', 'Location', 'Message', 'Confidence', 'Source'],
        lastSync: new Date(),
        isConnected: true
      }
      
      setConnectedSheets(prev => [...prev, newSheet])
      setNewSheetUrl('')
      setIsConnectingSheet(false)
    }, 2000)
  }

  const syncWithSheets = async () => {
    setIsSyncing(true)
    
    // Simulate syncing lead data to Google Sheets
    setTimeout(() => {
      const mockLeadData: LeadData[] = [
        {
          company: 'TechCorp Inc',
          contact: 'John Smith',
          email: 'john@techcorp.com',
          phone: '+1-555-0123',
          title: 'CTO',
          industry: 'Technology',
          location: 'San Francisco, CA',
          message: 'Hi John, I noticed TechCorp is expanding their engineering team. Our AI platform could help streamline your development process...',
          confidence: 0.85,
          source: 'LinkedIn'
        },
        {
          company: 'DataFlow Systems',
          contact: 'Sarah Johnson',
          email: 'sarah@dataflow.com',
          phone: '+1-555-0456',
          title: 'VP Engineering',
          industry: 'SaaS',
          location: 'Austin, TX',
          message: 'Hi Sarah, DataFlow\'s growth in the data analytics space caught my attention. Our solution could help optimize your data processing...',
          confidence: 0.92,
          source: 'Company Website'
        }
      ]
      
      setLeadData(mockLeadData)
      setIsSyncing(false)
    }, 3000)
  }

  const disconnectSheet = (sheetId: string) => {
    setConnectedSheets(prev => prev.filter(sheet => sheet.id !== sheetId))
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold font-poppins">Target Audience Intelligence</h1>
          <p className="text-muted-foreground mt-1">
            Upload documents and chat with AI to discover your perfect target audience
          </p>
        </div>
        <Badge variant="outline" className="bg-brand/20 text-brand border-brand/30">
          <Brain className="h-3 w-3 mr-1" />
          AI-Powered
        </Badge>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 bg-card/50 p-1 rounded-xl">
        <Button
          variant={activeTab === 'upload' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('upload')}
          className="flex-1"
        >
          <Upload className="h-4 w-4 mr-2" />
          Documents
        </Button>
        <Button
          variant={activeTab === 'chat' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('chat')}
          className="flex-1"
        >
          <MessageCircle className="h-4 w-4 mr-2" />
          AI Chat
        </Button>
        <Button
          variant={activeTab === 'profile' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('profile')}
          className="flex-1"
        >
          <Target className="h-4 w-4 mr-2" />
          Profile
        </Button>
        <Button
          variant={activeTab === 'sheets' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('sheets')}
          className="flex-1"
        >
          <Table className="h-4 w-4 mr-2" />
          Google Sheets
        </Button>
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        {activeTab === 'upload' && (
          <motion.div
            key="upload"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <Card className="shadow-glow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Knowledge Base Upload
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="border-2 border-dashed border-brand/30 rounded-xl p-8 text-center hover:border-brand/50 transition-colors">
                  <Upload className="h-12 w-12 mx-auto text-brand mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Upload Your Documents</h3>
                  <p className="text-muted-foreground mb-4">
                    Upload PDFs, Word docs, or text files about your target audience, customer research, or market analysis
                  </p>
                  <Button 
                    onClick={() => fileInputRef.current?.click()}
                    className="shadow-glow"
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Choose Files
                  </Button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".pdf,.doc,.docx,.txt"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </div>

                {uploadedDocs.length > 0 && (
                  <div className="space-y-3">
                    <h4 className="font-semibold">Uploaded Documents ({uploadedDocs.length})</h4>
                    {uploadedDocs.map((doc) => (
                      <div key={doc.id} className="flex items-center justify-between p-3 bg-card/50 rounded-lg border border-white/10">
                        <div className="flex items-center gap-3">
                          <FileText className="h-5 w-5 text-brand" />
                          <div>
                            <p className="font-medium">{doc.name}</p>
                            <p className="text-sm text-muted-foreground">
                              {formatFileSize(doc.size)} • {doc.uploadedAt.toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button variant="ghost" size="icon">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon" onClick={() => removeDocument(doc.id)}>
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}

        {activeTab === 'chat' && (
          <motion.div
            key="chat"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <Card className="shadow-glow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bot className="h-5 w-5" />
                  AI Audience Discovery Chat
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-96 overflow-y-auto space-y-4 mb-4 p-4 bg-card/30 rounded-lg">
                  {chatMessages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          message.type === 'user'
                            ? 'bg-brand text-white'
                            : 'bg-card border border-white/10 text-foreground'
                        }`}
                      >
                        <p className="text-sm">{message.content}</p>
                        <p className="text-xs opacity-70 mt-1">
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))}
                  {isTyping && (
                    <div className="flex justify-start">
                      <div className="bg-card border border-white/10 text-foreground px-4 py-2 rounded-lg">
                        <div className="flex items-center gap-1">
                          <div className="w-2 h-2 bg-brand rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-brand rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-brand rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                <div className="flex gap-2">
                  <Input
                    value={currentMessage}
                    onChange={(e) => setCurrentMessage(e.target.value)}
                    placeholder="Ask about your target audience..."
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    className="flex-1"
                  />
                  <Button onClick={sendMessage} disabled={!currentMessage.trim()}>
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {activeTab === 'profile' && (
          <motion.div
            key="profile"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <Card className="shadow-glow">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Users className="h-5 w-5" />
                    Ideal Customer Profile
                  </div>
                  <Button 
                    onClick={generateAudienceProfile}
                    disabled={isGeneratingProfile}
                    className="shadow-glow"
                  >
                    {isGeneratingProfile ? (
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Brain className="h-4 w-4 mr-2" />
                    )}
                    {isGeneratingProfile ? 'Analyzing...' : 'Generate Profile'}
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Demographics */}
                <div>
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <Users className="h-4 w-4" />
                    Demographics
                  </h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm text-muted-foreground">Age Range</label>
                      <p className="font-medium">{audienceProfile.demographics.ageRange || 'Not specified'}</p>
                    </div>
                    <div>
                      <label className="text-sm text-muted-foreground">Gender</label>
                      <p className="font-medium">{audienceProfile.demographics.gender || 'Not specified'}</p>
                    </div>
                    <div>
                      <label className="text-sm text-muted-foreground">Location</label>
                      <p className="font-medium">{audienceProfile.demographics.location || 'Not specified'}</p>
                    </div>
                    <div>
                      <label className="text-sm text-muted-foreground">Income</label>
                      <p className="font-medium">{audienceProfile.demographics.income || 'Not specified'}</p>
                    </div>
                  </div>
                </div>

                {/* Psychographics */}
                <div>
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <Brain className="h-4 w-4" />
                    Psychographics
                  </h4>
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm text-muted-foreground">Interests</label>
                      <div className="flex flex-wrap gap-2 mt-1">
                        {audienceProfile.psychographics.interests.map((interest, index) => (
                          <Badge key={index} variant="outline">{interest}</Badge>
                        ))}
                      </div>
                    </div>
                    <div>
                      <label className="text-sm text-muted-foreground">Pain Points</label>
                      <div className="flex flex-wrap gap-2 mt-1">
                        {audienceProfile.psychographics.painPoints.map((pain, index) => (
                          <Badge key={index} variant="destructive">{pain}</Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Firmographics */}
                <div>
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <Target className="h-4 w-4" />
                    Firmographics
                  </h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm text-muted-foreground">Company Size</label>
                      <p className="font-medium">{audienceProfile.firmographics.companySize || 'Not specified'}</p>
                    </div>
                    <div>
                      <label className="text-sm text-muted-foreground">Industries</label>
                      <div className="flex flex-wrap gap-2 mt-1">
                        {audienceProfile.firmographics.industry.map((industry, index) => (
                          <Badge key={index} variant="secondary">{industry}</Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Behavior */}
                <div>
                  <h4 className="font-semibold mb-3 flex items-center gap-2">
                    <MessageCircle className="h-4 w-4" />
                    Behavior Patterns
                  </h4>
                  <div className="space-y-3">
                    <div>
                      <label className="text-sm text-muted-foreground">Preferred Channels</label>
                      <div className="flex flex-wrap gap-2 mt-1">
                        {audienceProfile.behavior.channels.map((channel, index) => (
                          <Badge key={index} variant="outline">{channel}</Badge>
                        ))}
                      </div>
                    </div>
                    <div>
                      <label className="text-sm text-muted-foreground">Content Preferences</label>
                      <div className="flex flex-wrap gap-2 mt-1">
                        {audienceProfile.behavior.content.map((content, index) => (
                          <Badge key={index} variant="outline">{content}</Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {activeTab === 'sheets' && (
          <motion.div
            key="sheets"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Connect Google Sheet */}
            <Card className="shadow-glow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Link className="h-5 w-5" />
                  Connect Google Sheets
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <label className="text-sm font-medium">Google Sheets URL</label>
                  <div className="flex gap-2">
                    <Input
                      value={newSheetUrl}
                      onChange={(e) => setNewSheetUrl(e.target.value)}
                      placeholder="https://docs.google.com/spreadsheets/d/..."
                      className="flex-1"
                    />
                    <Button 
                      onClick={connectGoogleSheet}
                      disabled={!newSheetUrl.trim() || isConnectingSheet}
                      className="shadow-glow"
                    >
                      {isConnectingSheet ? (
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <Link className="h-4 w-4 mr-2" />
                      )}
                      {isConnectingSheet ? 'Connecting...' : 'Connect'}
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Paste your Google Sheets URL to connect and sync lead data
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Connected Sheets */}
            {connectedSheets.length > 0 && (
              <Card className="shadow-glow">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Database className="h-5 w-5" />
                      Connected Sheets ({connectedSheets.length})
                    </div>
                    <Button 
                      onClick={syncWithSheets}
                      disabled={isSyncing}
                      className="shadow-glow"
                    >
                      {isSyncing ? (
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <RotateCcw className="h-4 w-4 mr-2" />
                      )}
                      {isSyncing ? 'Syncing...' : 'Sync All'}
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {connectedSheets.map((sheet) => (
                    <div key={sheet.id} className="p-4 bg-card/50 rounded-lg border border-white/10">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <Table className="h-5 w-5 text-brand" />
                          <div>
                            <h4 className="font-semibold">{sheet.name}</h4>
                            <p className="text-sm text-muted-foreground">
                              Last synced: {sheet.lastSync.toLocaleString()}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button variant="ghost" size="icon" asChild>
                            <a href={sheet.url} target="_blank" rel="noopener noreferrer">
                              <ExternalLink className="h-4 w-4" />
                            </a>
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            onClick={() => disconnectSheet(sheet.id)}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      
                      <div className="space-y-2">
                        <p className="text-sm font-medium">Detected Columns:</p>
                        <div className="flex flex-wrap gap-2">
                          {sheet.columns.map((column, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {column}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}

            {/* Lead Data Preview */}
            {leadData.length > 0 && (
              <Card className="shadow-glow">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="h-5 w-5" />
                    Lead Data Preview ({leadData.length} contacts)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {leadData.map((lead, index) => (
                      <div key={index} className="p-4 bg-card/50 rounded-lg border border-white/10">
                        <div className="grid grid-cols-2 gap-4 mb-3">
                          <div>
                            <p className="text-sm text-muted-foreground">Company</p>
                            <p className="font-medium">{lead.company}</p>
                          </div>
                          <div>
                            <p className="text-sm text-muted-foreground">Contact</p>
                            <p className="font-medium">{lead.contact} ({lead.title})</p>
                          </div>
                          <div>
                            <p className="text-sm text-muted-foreground">Email</p>
                            <p className="font-medium">{lead.email}</p>
                          </div>
                          <div>
                            <p className="text-sm text-muted-foreground">Confidence</p>
                            <Badge variant={lead.confidence > 0.8 ? 'default' : 'secondary'}>
                              {Math.round(lead.confidence * 100)}%
                            </Badge>
                          </div>
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground mb-1">Personalized Message</p>
                          <p className="text-sm bg-card/30 p-2 rounded border">
                            {lead.message}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="mt-4 p-4 bg-brand/10 border border-brand/20 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle className="h-4 w-4 text-brand" />
                      <span className="font-medium text-brand">Ready to Sync</span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {leadData.length} contacts are ready to be added to your Google Sheets. 
                      Click "Sync All" to update your connected sheets with this data.
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
