/**
 * Local Storage and State Management
 * Handles persistent storage of user data, settings, and connected sheets
 */

export interface UserProfile {
  id: string
  name: string
  email: string
  avatar?: string
  preferences: {
    theme: 'light' | 'dark'
    notifications: boolean
    autoSync: boolean
  }
  createdAt: string
  lastActive: string
}

export interface ConnectedSheet {
  id: string
  name: string
  url: string
  lastSync: string
  columns: string[]
  rowCount: number
  isConnected: boolean
  permissions: {
    canRead: boolean
    canWrite: boolean
    canShare: boolean
  }
}

export interface UploadedDocument {
  id: string
  name: string
  type: string
  size: number
  content: string
  uploadedAt: string
  processed: boolean
  extractedText?: string
  summary?: string
}

export interface AudienceProfile {
  id: string
  name: string
  description: string
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
  createdAt: string
  updatedAt: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  metadata?: {
    documentId?: string
    sheetId?: string
    context?: string
  }
}

class StorageService {
  private readonly STORAGE_KEYS = {
    USER_PROFILE: 'elvision_user_profile',
    CONNECTED_SHEETS: 'elvision_connected_sheets',
    UPLOADED_DOCUMENTS: 'elvision_uploaded_documents',
    AUDIENCE_PROFILES: 'elvision_audience_profiles',
    CHAT_HISTORY: 'elvision_chat_history',
    APP_SETTINGS: 'elvision_app_settings'
  }

  // User Profile Management
  async saveUserProfile(profile: UserProfile): Promise<void> {
    try {
      const data = { ...profile, lastActive: new Date().toISOString() }
      localStorage.setItem(this.STORAGE_KEYS.USER_PROFILE, JSON.stringify(data))
    } catch (error) {
      console.error('Failed to save user profile:', error)
      throw error
    }
  }

  async getUserProfile(): Promise<UserProfile | null> {
    try {
      const data = localStorage.getItem(this.STORAGE_KEYS.USER_PROFILE)
      return data ? JSON.parse(data) : null
    } catch (error) {
      console.error('Failed to get user profile:', error)
      return null
    }
  }

  // Connected Sheets Management
  async saveConnectedSheets(sheets: ConnectedSheet[]): Promise<void> {
    try {
      localStorage.setItem(this.STORAGE_KEYS.CONNECTED_SHEETS, JSON.stringify(sheets))
    } catch (error) {
      console.error('Failed to save connected sheets:', error)
      throw error
    }
  }

  async getConnectedSheets(): Promise<ConnectedSheet[]> {
    try {
      const data = localStorage.getItem(this.STORAGE_KEYS.CONNECTED_SHEETS)
      return data ? JSON.parse(data) : []
    } catch (error) {
      console.error('Failed to get connected sheets:', error)
      return []
    }
  }

  async addConnectedSheet(sheet: ConnectedSheet): Promise<void> {
    try {
      const sheets = await this.getConnectedSheets()
      const existingIndex = sheets.findIndex(s => s.id === sheet.id)
      
      if (existingIndex >= 0) {
        sheets[existingIndex] = sheet
      } else {
        sheets.push(sheet)
      }
      
      await this.saveConnectedSheets(sheets)
    } catch (error) {
      console.error('Failed to add connected sheet:', error)
      throw error
    }
  }

  async removeConnectedSheet(sheetId: string): Promise<void> {
    try {
      const sheets = await this.getConnectedSheets()
      const filteredSheets = sheets.filter(s => s.id !== sheetId)
      await this.saveConnectedSheets(filteredSheets)
    } catch (error) {
      console.error('Failed to remove connected sheet:', error)
      throw error
    }
  }

  // Uploaded Documents Management
  async saveUploadedDocuments(documents: UploadedDocument[]): Promise<void> {
    try {
      localStorage.setItem(this.STORAGE_KEYS.UPLOADED_DOCUMENTS, JSON.stringify(documents))
    } catch (error) {
      console.error('Failed to save uploaded documents:', error)
      throw error
    }
  }

  async getUploadedDocuments(): Promise<UploadedDocument[]> {
    try {
      const data = localStorage.getItem(this.STORAGE_KEYS.UPLOADED_DOCUMENTS)
      return data ? JSON.parse(data) : []
    } catch (error) {
      console.error('Failed to get uploaded documents:', error)
      return []
    }
  }

  async addUploadedDocument(document: UploadedDocument): Promise<void> {
    try {
      const documents = await this.getUploadedDocuments()
      documents.push(document)
      await this.saveUploadedDocuments(documents)
    } catch (error) {
      console.error('Failed to add uploaded document:', error)
      throw error
    }
  }

  async removeUploadedDocument(documentId: string): Promise<void> {
    try {
      const documents = await this.getUploadedDocuments()
      const filteredDocuments = documents.filter(d => d.id !== documentId)
      await this.saveUploadedDocuments(filteredDocuments)
    } catch (error) {
      console.error('Failed to remove uploaded document:', error)
      throw error
    }
  }

  // Audience Profiles Management
  async saveAudienceProfiles(profiles: AudienceProfile[]): Promise<void> {
    try {
      localStorage.setItem(this.STORAGE_KEYS.AUDIENCE_PROFILES, JSON.stringify(profiles))
    } catch (error) {
      console.error('Failed to save audience profiles:', error)
      throw error
    }
  }

  async getAudienceProfiles(): Promise<AudienceProfile[]> {
    try {
      const data = localStorage.getItem(this.STORAGE_KEYS.AUDIENCE_PROFILES)
      return data ? JSON.parse(data) : []
    } catch (error) {
      console.error('Failed to get audience profiles:', error)
      return []
    }
  }

  async addAudienceProfile(profile: AudienceProfile): Promise<void> {
    try {
      const profiles = await this.getAudienceProfiles()
      const existingIndex = profiles.findIndex(p => p.id === profile.id)
      
      if (existingIndex >= 0) {
        profiles[existingIndex] = profile
      } else {
        profiles.push(profile)
      }
      
      await this.saveAudienceProfiles(profiles)
    } catch (error) {
      console.error('Failed to add audience profile:', error)
      throw error
    }
  }

  // Chat History Management
  async saveChatHistory(messages: ChatMessage[]): Promise<void> {
    try {
      localStorage.setItem(this.STORAGE_KEYS.CHAT_HISTORY, JSON.stringify(messages))
    } catch (error) {
      console.error('Failed to save chat history:', error)
      throw error
    }
  }

  async getChatHistory(): Promise<ChatMessage[]> {
    try {
      const data = localStorage.getItem(this.STORAGE_KEYS.CHAT_HISTORY)
      return data ? JSON.parse(data) : []
    } catch (error) {
      console.error('Failed to get chat history:', error)
      return []
    }
  }

  async addChatMessage(message: ChatMessage): Promise<void> {
    try {
      const messages = await this.getChatHistory()
      messages.push(message)
      await this.saveChatHistory(messages)
    } catch (error) {
      console.error('Failed to add chat message:', error)
      throw error
    }
  }

  // App Settings Management
  async saveAppSettings(settings: any): Promise<void> {
    try {
      localStorage.setItem(this.STORAGE_KEYS.APP_SETTINGS, JSON.stringify(settings))
    } catch (error) {
      console.error('Failed to save app settings:', error)
      throw error
    }
  }

  async getAppSettings(): Promise<any> {
    try {
      const data = localStorage.getItem(this.STORAGE_KEYS.APP_SETTINGS)
      return data ? JSON.parse(data) : {}
    } catch (error) {
      console.error('Failed to get app settings:', error)
      return {}
    }
  }

  // Utility Methods
  async clearAllData(): Promise<void> {
    try {
      Object.values(this.STORAGE_KEYS).forEach(key => {
        localStorage.removeItem(key)
      })
    } catch (error) {
      console.error('Failed to clear all data:', error)
      throw error
    }
  }

  async exportData(): Promise<any> {
    try {
      const data = {
        userProfile: await this.getUserProfile(),
        connectedSheets: await this.getConnectedSheets(),
        uploadedDocuments: await this.getUploadedDocuments(),
        audienceProfiles: await this.getAudienceProfiles(),
        chatHistory: await this.getChatHistory(),
        appSettings: await this.getAppSettings(),
        exportedAt: new Date().toISOString()
      }
      return data
    } catch (error) {
      console.error('Failed to export data:', error)
      throw error
    }
  }

  async importData(data: any): Promise<void> {
    try {
      if (data.userProfile) await this.saveUserProfile(data.userProfile)
      if (data.connectedSheets) await this.saveConnectedSheets(data.connectedSheets)
      if (data.uploadedDocuments) await this.saveUploadedDocuments(data.uploadedDocuments)
      if (data.audienceProfiles) await this.saveAudienceProfiles(data.audienceProfiles)
      if (data.chatHistory) await this.saveChatHistory(data.chatHistory)
      if (data.appSettings) await this.saveAppSettings(data.appSettings)
    } catch (error) {
      console.error('Failed to import data:', error)
      throw error
    }
  }
}

// Create a singleton instance
export const storageService = new StorageService()
