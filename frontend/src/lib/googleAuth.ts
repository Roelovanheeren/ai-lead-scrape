/**
 * Google OAuth Authentication for Google Sheets API
 * Handles user authentication and token management
 */

export interface GoogleAuthConfig {
  clientId: string
  apiKey: string
  discoveryDocs: string[]
  scopes: string[]
}

export interface GoogleUser {
  id: string
  name: string
  email: string
  picture: string
}

export interface GoogleSheet {
  id: string
  name: string
  url: string
  lastModified: string
  owners: string[]
  writers: string[]
  readers: string[]
}

class GoogleAuthService {
  private gapi: any = null
  private isInitialized = false
  private isSignedIn = false
  private currentUser: GoogleUser | null = null

  constructor() {
    // Initialize GAPI when the script loads
    this.initializeGapi()
  }

  private async initializeGapi() {
    if (typeof window === 'undefined') return

    try {
      // Load the Google API script
      await this.loadGapiScript()
      
      // Initialize the API
      await this.gapi.load('client:auth2', async () => {
        await this.gapi.client.init({
          apiKey: process.env.REACT_APP_GOOGLE_API_KEY || '',
          clientId: process.env.REACT_APP_GOOGLE_CLIENT_ID || '',
          discoveryDocs: ['https://sheets.googleapis.com/$discovery/rest?version=v4'],
          scope: 'https://www.googleapis.com/auth/spreadsheets.readonly https://www.googleapis.com/auth/drive.readonly'
        })

        this.isInitialized = true
        
        // Check if user is already signed in
        const authInstance = this.gapi.auth2.getAuthInstance()
        this.isSignedIn = authInstance.isSignedIn.get()
        
        if (this.isSignedIn) {
          this.currentUser = this.getCurrentUser()
        }
      })
    } catch (error) {
      console.error('Failed to initialize Google API:', error)
    }
  }

  private loadGapiScript(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (window.gapi) {
        this.gapi = window.gapi
        resolve()
        return
      }

      const script = document.createElement('script')
      script.src = 'https://apis.google.com/js/api.js'
      script.onload = () => {
        this.gapi = window.gapi
        resolve()
      }
      script.onerror = reject
      document.head.appendChild(script)
    })
  }

  async signIn(): Promise<GoogleUser> {
    if (!this.isInitialized) {
      throw new Error('Google API not initialized')
    }

    try {
      const authInstance = this.gapi.auth2.getAuthInstance()
      const user = await authInstance.signIn()
      
      this.isSignedIn = true
      this.currentUser = this.getCurrentUser()
      
      return this.currentUser!
    } catch (error) {
      console.error('Sign in failed:', error)
      throw error
    }
  }

  async signOut(): Promise<void> {
    if (!this.isInitialized) return

    try {
      const authInstance = this.gapi.auth2.getAuthInstance()
      await authInstance.signOut()
      
      this.isSignedIn = false
      this.currentUser = null
    } catch (error) {
      console.error('Sign out failed:', error)
      throw error
    }
  }

  getCurrentUser(): GoogleUser | null {
    if (!this.isInitialized || !this.isSignedIn) return null

    try {
      const authInstance = this.gapi.auth2.getAuthInstance()
      const user = authInstance.currentUser.get()
      const profile = user.getBasicProfile()

      return {
        id: profile.getId(),
        name: profile.getName(),
        email: profile.getEmail(),
        picture: profile.getImageUrl()
      }
    } catch (error) {
      console.error('Failed to get current user:', error)
      return null
    }
  }

  isUserSignedIn(): boolean {
    return this.isSignedIn
  }

  async getSheets(): Promise<GoogleSheet[]> {
    if (!this.isInitialized || !this.isSignedIn) {
      throw new Error('User must be signed in to access sheets')
    }

    try {
      const response = await this.gapi.client.drive.files.list({
        q: "mimeType='application/vnd.google-apps.spreadsheet'",
        fields: 'files(id,name,webViewLink,modifiedTime,owners,writers,readers)',
        orderBy: 'modifiedTime desc',
        pageSize: 50
      })

      return response.result.files.map((file: any) => ({
        id: file.id,
        name: file.name,
        url: file.webViewLink,
        lastModified: file.modifiedTime,
        owners: file.owners?.map((owner: any) => owner.emailAddress) || [],
        writers: file.writers?.map((writer: any) => writer.emailAddress) || [],
        readers: file.readers?.map((reader: any) => reader.emailAddress) || []
      }))
    } catch (error) {
      console.error('Failed to fetch sheets:', error)
      throw error
    }
  }

  async getSheetData(sheetId: string, range: string = 'A:Z'): Promise<any[][]> {
    if (!this.isInitialized || !this.isSignedIn) {
      throw new Error('User must be signed in to access sheet data')
    }

    try {
      const response = await this.gapi.client.sheets.spreadsheets.values.get({
        spreadsheetId: sheetId,
        range: range
      })

      return response.result.values || []
    } catch (error) {
      console.error('Failed to fetch sheet data:', error)
      throw error
    }
  }

  extractSheetId(url: string): string | null {
    const match = url.match(/\/spreadsheets\/d\/([a-zA-Z0-9-_]+)/)
    return match ? match[1] : null
  }
}

// Create a singleton instance
export const googleAuthService = new GoogleAuthService()

// Add GAPI to window type
declare global {
  interface Window {
    gapi: any
  }
}
