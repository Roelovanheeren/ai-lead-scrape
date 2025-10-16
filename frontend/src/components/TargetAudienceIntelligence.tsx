import React, { useState, useRef, useEffect } from 'react'
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
import { googleSheetsService, GoogleSheetData } from '@/lib/googleSheets'
import { storageService, ConnectedSheet, UploadedDocument as StorageUploadedDocument, AudienceProfile as StorageAudienceProfile, ChatMessage as StorageChatMessage } from '@/lib/storage'

// UploadedDocument interface is now imported from storage service

// ChatMessage interface is now imported from storage service

// AudienceProfile interface is now imported from storage service

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
  const [uploadedDocs, setUploadedDocs] = useState<StorageUploadedDocument[]>([])
  const [chatMessages, setChatMessages] = useState<StorageChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hi! I'm your AI Audience Intelligence Assistant. I'll help you discover your perfect target audience. Let's start with your business - what product or service are you offering?",
      timestamp: new Date().toISOString()
    }
  ])
  const [currentMessage, setCurrentMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [audienceProfile, setAudienceProfile] = useState<StorageAudienceProfile>({
    id: 'default',
    name: 'Default Profile',
    description: 'Default audience profile',
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
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  })
  const [isGeneratingProfile, setIsGeneratingProfile] = useState(false)
  const [connectedSheets, setConnectedSheets] = useState<ConnectedSheet[]>([])
  const [newSheetUrl, setNewSheetUrl] = useState('https://docs.google.com/spreadsheets/d/1fIUwNP7cOhIvOlKpDMIe2ukfmLoCGxEs9MHrRKZj1yA/edit?usp=sharing')
  const [isConnectingSheet, setIsConnectingSheet] = useState(false)
  const [isSyncing, setIsSyncing] = useState(false)
  const [leadData, setLeadData] = useState<LeadData[]>([])
  const [connectionMessage, setConnectionMessage] = useState('')
  const [selectedSheet, setSelectedSheet] = useState<ConnectedSheet | null>(null)
  const [sheetHeaders, setSheetHeaders] = useState<string[]>([])
  const [headerMapping, setHeaderMapping] = useState<Record<string, string>>({})
  const [isLoadingHeaders, setIsLoadingHeaders] = useState(false)
  const [isMappingHeaders, setIsMappingHeaders] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Handle URL parameters for OAuth callback
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const connected = urlParams.get('connected')
    const error = urlParams.get('error')
    const message = urlParams.get('message')
    
    if (connected === 'true' && message) {
      setConnectionMessage(message)
      // Clear URL parameters
      window.history.replaceState({}, document.title, window.location.pathname)
    } else if (error === 'true' && message) {
      setSheetConnectionError(message)
      // Clear URL parameters
      window.history.replaceState({}, document.title, window.location.pathname)
    }
  }, [])

  // Load persisted data on component mount
  useEffect(() => {
    const loadPersistedData = async () => {
      try {
        // Load connected sheets
        const sheets = await storageService.getConnectedSheets()
        setConnectedSheets(sheets)

        // Load uploaded documents
        const documents = await storageService.getUploadedDocuments()
        setUploadedDocs(documents)

        // Load audience profiles
        const profiles = await storageService.getAudienceProfiles()
        if (profiles.length > 0) {
          setAudienceProfile(profiles[0]) // Use the first profile for now
        }

        // Load chat history
        const chatHistory = await storageService.getChatHistory()
        setChatMessages(chatHistory)
      } catch (error) {
        console.error('Failed to load persisted data:', error)
      }
    }

    loadPersistedData()
  }, [])

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files) return

    for (const file of Array.from(files)) {
      const newDoc: StorageUploadedDocument = {
        id: Math.random().toString(36).substr(2, 9),
        name: file.name,
        size: file.size,
        type: file.type,
        content: '', // We'll extract text content later
        uploadedAt: new Date().toISOString(),
        processed: false
      }

      // Save to persistent storage
      try {
        await storageService.addUploadedDocument(newDoc)
        setUploadedDocs(prev => [...prev, newDoc])
      } catch (error) {
        console.error('Failed to save uploaded document:', error)
      }
    }
  }

  const removeDocument = async (id: string) => {
    try {
      await storageService.removeUploadedDocument(id)
      setUploadedDocs(prev => prev.filter(doc => doc.id !== id))
    } catch (error) {
      console.error('Failed to remove document:', error)
    }
  }

  const sendMessage = async () => {
    if (!currentMessage.trim()) return

    const userMessage: StorageChatMessage = {
      id: Math.random().toString(36).substr(2, 9),
      role: 'user',
      content: currentMessage,
      timestamp: new Date().toISOString()
    }

    // Save user message to persistent storage
    try {
      await storageService.addChatMessage(userMessage)
      setChatMessages(prev => [...prev, userMessage])
    } catch (error) {
      console.error('Failed to save user message:', error)
    }

    setCurrentMessage('')
    setIsTyping(true)

    // Send message to real AI chat API
    try {
      const response = await fetch('/ai-chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: currentMessage,
          conversation_history: chatMessages,
          current_stage: 'introduction' // You could track this in state
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        
        const aiResponse: StorageChatMessage = {
          id: Math.random().toString(36).substr(2, 9),
          role: 'assistant',
          content: result.response,
          timestamp: new Date().toISOString()
        }
        
        // Save AI response to persistent storage
        try {
          await storageService.addChatMessage(aiResponse)
          setChatMessages(prev => [...prev, aiResponse])
        } catch (error) {
          console.error('Failed to save AI response:', error)
        }
        
        // Check if conversation is complete
        if (result.is_complete) {
          // Generate final audience profile
          await generateAudienceProfile()
        }
      } else {
        throw new Error('Failed to get AI response')
      }
    } catch (error) {
      console.error('Error sending message:', error)
      
      // Fallback response
      const fallbackResponse: StorageChatMessage = {
        id: Math.random().toString(36).substr(2, 9),
        role: 'assistant',
        content: "I'm having trouble processing your message. Could you please try again?",
        timestamp: new Date().toISOString()
      }
      
      try {
        await storageService.addChatMessage(fallbackResponse)
        setChatMessages(prev => [...prev, fallbackResponse])
      } catch (error) {
        console.error('Failed to save fallback response:', error)
      }
    } finally {
      setIsTyping(false)
    }
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
    
    try {
      // Send conversation to AI to generate profile
      const response = await fetch('/ai-chat/generate-profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_history: chatMessages
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        const aiProfile = result.profile
        
        // Convert AI profile to our format
        const generatedProfile: StorageAudienceProfile = {
          id: 'ai-generated-profile',
          name: 'AI Generated Profile',
          description: 'AI-generated audience profile based on conversation',
          demographics: {
            ageRange: aiProfile.demographics?.age_range || '25-45',
            gender: aiProfile.demographics?.gender || 'Mixed',
            location: aiProfile.demographics?.location || 'North America, Europe',
            income: aiProfile.demographics?.income || '$50k-$150k'
          },
          psychographics: {
            interests: aiProfile.psychographics?.interests || ['Technology', 'Innovation'],
            painPoints: aiProfile.psychographics?.pain_points || ['Manual processes', 'Time constraints'],
            goals: aiProfile.psychographics?.goals || ['Increase productivity', 'Reduce costs'],
            values: aiProfile.psychographics?.values || ['Innovation', 'Reliability']
          },
          firmographics: {
            companySize: aiProfile.firmographics?.company_size || '50-500 employees',
            industry: aiProfile.firmographics?.industry || ['Technology', 'SaaS'],
            jobTitles: aiProfile.firmographics?.job_titles || ['CTO', 'VP Engineering'],
            technology: aiProfile.firmographics?.technology || ['Cloud platforms', 'APIs']
          },
          behavior: {
            channels: aiProfile.behavior?.channels || ['LinkedIn', 'Industry forums'],
            content: aiProfile.behavior?.content || ['Technical blogs', 'Case studies'],
            timing: aiProfile.behavior?.timing || 'Q4 planning, Q1 implementation'
          },
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
        
        setAudienceProfile(generatedProfile)
        
        // Save to persistent storage
        try {
          await storageService.saveAudienceProfiles([generatedProfile])
        } catch (error) {
          console.error('Failed to save audience profile:', error)
        }
      } else {
        throw new Error('Failed to generate audience profile')
      }
    } catch (error) {
      console.error('Error generating audience profile:', error)
      
      // Fallback to mock profile
      setAudienceProfile({
        id: 'fallback-profile',
        name: 'Fallback Profile',
        description: 'Fallback profile due to AI error',
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
        },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      })
    } finally {
      setIsGeneratingProfile(false)
    }
  }

  const connectGoogleSheet = async () => {
    setIsConnectingSheet(true)
    
    try {
      // Start Google OAuth flow
      const authResponse = await fetch('/auth/google/authorize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 'user_123' }) // In real app, use actual user ID
      })
      
      if (!authResponse.ok) {
        throw new Error('Failed to start Google authentication')
      }
      
      const authResult = await authResponse.json()
      if (!authResult.success) {
        throw new Error(authResult.error || 'Failed to start Google authentication')
      }
      
      // Redirect user to Google OAuth
      window.location.href = authResult.auth_url
      
    } catch (error) {
      console.error('Error connecting to Google Sheet:', error)
      setIsConnectingSheet(false)
    }
  }

  const loadUserSheets = async () => {
    try {
      const response = await fetch('/auth/google/sheets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 'user_123' })
      })
      
      if (response.ok) {
        const result = await response.json()
        if (result.success) {
          // Convert Google Sheets to ConnectedSheet format
          const sheets: ConnectedSheet[] = result.sheets.map((sheet: any) => ({
            id: `googlesheets_${sheet.id}`,
            name: sheet.name,
            url: sheet.url,
            lastSync: new Date().toISOString(),
            columns: ['Company', 'Contact', 'Email', 'Phone', 'Industry', 'Status', 'Source', 'Date'],
            rowCount: 0,
            isConnected: true,
            permissions: {
              canRead: true,
              canWrite: true,
              canShare: false
            }
          }))
          
          setConnectedSheets(prev => [...prev, ...sheets])
        }
      }
    } catch (error) {
      console.error('Error loading user sheets:', error)
    }
  }

  const selectSheet = async (sheet: ConnectedSheet) => {
    setSelectedSheet(sheet)
    setIsLoadingHeaders(true)
    
    try {
      // Extract sheet ID from the sheet object
      const sheetId = sheet.id.replace('googlesheets_', '')
      
      // Read sheet headers
      const response = await fetch(`/auth/google/sheets/${sheetId}/read`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          user_id: 'user_123',
          range: 'A1:Z1' // Read first row for headers
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        if (result.success && result.data.length > 0) {
          const headers = result.data[0] // First row contains headers
          setSheetHeaders(headers)
          
          // Initialize header mapping with empty values
          const initialMapping: Record<string, string> = {}
          headers.forEach((header: string) => {
            initialMapping[header] = ''
          })
          setHeaderMapping(initialMapping)
        }
      }
    } catch (error) {
      console.error('Error reading sheet headers:', error)
    } finally {
      setIsLoadingHeaders(false)
    }
  }

  const saveHeaderMapping = async () => {
    setIsMappingHeaders(true)
    
    try {
      // Save header mapping to knowledge base
      const mappingData = {
        sheetId: selectedSheet?.id,
        sheetName: selectedSheet?.name,
        headers: sheetHeaders,
        mapping: headerMapping,
        timestamp: new Date().toISOString()
      }
      
      // Save to persistent storage
      await storageService.saveHeaderMapping(mappingData)
      
      console.log('Header mapping saved:', mappingData)
      setConnectionMessage('Sheet configuration saved successfully!')
    } catch (error) {
      console.error('Error saving header mapping:', error)
      setSheetConnectionError('Failed to save sheet configuration')
    } finally {
      setIsMappingHeaders(false)
    }
  }

  const syncWithSheets = async () => {
    setIsSyncing(true)
    
    try {
      // Prepare lead data for Make.com
      const mockLeadData = [
        {
          company: 'TechCorp Inc',
          contact_name: 'John Smith',
          email: 'john@techcorp.com',
          phone: '+1-555-0123',
          industry: 'Technology',
          location: 'San Francisco, CA',
          status: 'New'
        },
        {
          company: 'DataFlow Systems',
          contact_name: 'Sarah Johnson',
          email: 'sarah@dataflow.com',
          phone: '+1-555-0456',
          industry: 'SaaS',
          location: 'Austin, TX',
          status: 'New'
        }
      ]
      
      // Send leads to Google Sheets via OAuth
      const response = await fetch('/auth/google/sheets/sync-leads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          leads: mockLeadData,
          user_id: 'user_123', // In real app, use actual user ID
          sheet_id: 'demo_sheet_id', // In real app, use actual sheet ID
          sheet_name: 'Leads'
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('Sync result:', result)
        
        // Update connected sheets with sync status
        setConnectedSheets(prev => prev.map(sheet => ({
          ...sheet,
          lastSync: new Date().toISOString(),
          rowCount: sheet.rowCount + mockLeadData.length
        })))
      } else {
        throw new Error('Failed to sync with Make.com')
      }
      
      setIsSyncing(false)
    } catch (error) {
      console.error('Sync error:', error)
      setIsSyncing(false)
    }
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
                              {formatFileSize(doc.size)} • {new Date(doc.uploadedAt).toLocaleDateString()}
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
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          message.role === 'user'
                            ? 'bg-brand text-white'
                            : 'bg-card border border-white/10 text-foreground'
                        }`}
                      >
                        <p className="text-sm">{message.content}</p>
                        <p className="text-xs opacity-70 mt-1">
                          {new Date(message.timestamp).toLocaleTimeString()}
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
            {/* Google Sheets Integration */}
            <Card className="shadow-glow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  Google Sheets Integration
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  Connect your Google account to sync lead data directly to your sheets
                </p>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-card/50 rounded-lg border border-white/10">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-teal-500/20 rounded-lg">
                        <Database className="h-5 w-5 text-teal-400" />
                      </div>
                      <div>
                        <h4 className="font-medium">Google Sheets</h4>
                        <p className="text-sm text-muted-foreground">
                          Connect your Google account to access and sync with your sheets
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button 
                        onClick={connectGoogleSheet}
                        disabled={isConnectingSheet}
                        className="shadow-glow"
                      >
                        {isConnectingSheet ? (
                          <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        ) : (
                          <Link className="h-4 w-4 mr-2" />
                        )}
                        {isConnectingSheet ? 'Connecting...' : 'Connect Google Account'}
                      </Button>
                      <Button 
                        onClick={loadUserSheets}
                        variant="outline"
                        className="border-white/20"
                      >
                        <Database className="h-4 w-4 mr-2" />
                        Load My Sheets
                      </Button>
                    </div>
                  </div>
                  
                  <div className="text-xs text-muted-foreground space-y-1">
                    <p>• Secure OAuth authentication with Google</p>
                    <p>• Access to all your Google Sheets</p>
                    <p>• Automatic lead data synchronization</p>
                    <p>• No technical setup required</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Connection Messages */}
            {connectionMessage && (
              <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
                <div className="flex items-center gap-2 text-green-400">
                  <CheckCircle className="h-4 w-4" />
                  <span className="text-sm font-medium">{connectionMessage}</span>
                </div>
              </div>
            )}

            {sheetConnectionError && (
              <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                <div className="flex items-center gap-2 text-red-400">
                  <X className="h-4 w-4" />
                  <span className="text-sm font-medium">{sheetConnectionError}</span>
                </div>
              </div>
            )}

            {/* Sheet Selection */}
            {connectedSheets.length > 0 && !selectedSheet && (
              <Card className="shadow-glow">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5" />
                    Select Target Sheet
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">
                    Choose which Google Sheet to use for lead data synchronization
                  </p>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-3">
                    {connectedSheets.map((sheet) => (
                      <div
                        key={sheet.id}
                        className="p-4 bg-card/50 rounded-lg border border-white/10 hover:border-teal-500/50 cursor-pointer transition-colors"
                        onClick={() => selectSheet(sheet)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-teal-500/20 rounded-lg">
                              <Table className="h-4 w-4 text-teal-400" />
                            </div>
                            <div>
                              <h4 className="font-medium">{sheet.name}</h4>
                              <p className="text-sm text-muted-foreground">
                                Last synced: {new Date(sheet.lastSync).toLocaleDateString()}
                              </p>
                            </div>
                          </div>
                          <Button variant="outline" size="sm" className="border-white/20">
                            Select
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Header Mapping */}
            {selectedSheet && sheetHeaders.length > 0 && (
              <Card className="shadow-glow">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5" />
                    Configure Data Mapping
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">
                    Map your research data fields to the columns in "{selectedSheet.name}"
                  </p>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-4">
                    {sheetHeaders.map((header, index) => (
                      <div key={index} className="flex items-center gap-4">
                        <div className="flex-1">
                          <label className="text-sm font-medium text-muted-foreground">
                            {header}
                          </label>
                          <select
                            value={headerMapping[header] || ''}
                            onChange={(e) => setHeaderMapping(prev => ({
                              ...prev,
                              [header]: e.target.value
                            }))}
                            className="w-full mt-1 p-2 bg-card border border-white/20 rounded-lg text-sm"
                          >
                            <option value="">Select data field...</option>
                            <option value="company">Company Name</option>
                            <option value="contact_name">Contact Name</option>
                            <option value="email">Email Address</option>
                            <option value="phone">Phone Number</option>
                            <option value="industry">Industry</option>
                            <option value="location">Location</option>
                            <option value="status">Status</option>
                            <option value="source">Source</option>
                            <option value="date">Date Added</option>
                            <option value="message">Outreach Message</option>
                            <option value="notes">Notes</option>
                          </select>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="flex gap-2 pt-4">
                    <Button 
                      onClick={saveHeaderMapping}
                      disabled={isMappingHeaders}
                      className="shadow-glow"
                    >
                      {isMappingHeaders ? (
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      ) : (
                        <CheckCircle className="h-4 w-4 mr-2" />
                      )}
                      {isMappingHeaders ? 'Saving...' : 'Save Configuration'}
                    </Button>
                    <Button 
                      onClick={() => setSelectedSheet(null)}
                      variant="outline"
                      className="border-white/20"
                    >
                      <X className="h-4 w-4 mr-2" />
                      Cancel
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

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
