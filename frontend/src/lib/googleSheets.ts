/**
 * Google Sheets API Integration
 * Handles reading and writing to Google Sheets
 */

export interface GoogleSheetData {
  id: string
  name: string
  url: string
  lastSync: Date
  columns: string[]
  data: any[]
  isConnected: boolean
}

export interface GoogleSheetRow {
  [key: string]: string | number
}

class GoogleSheetsService {
  private apiKey: string = ''
  private clientId: string = ''

  constructor() {
    // These would be set from environment variables in production
    this.apiKey = import.meta.env.VITE_GOOGLE_API_KEY || ''
    this.clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || ''
  }

  /**
   * Extract Google Sheets ID from URL
   */
  extractSheetId(url: string): string | null {
    const match = url.match(/\/spreadsheets\/d\/([a-zA-Z0-9-_]+)/)
    return match ? match[1] : null
  }

  /**
   * Read data from Google Sheets using the Sheets API
   */
  async readSheetData(sheetUrl: string): Promise<GoogleSheetData | null> {
    try {
      const sheetId = this.extractSheetId(sheetUrl)
      if (!sheetId) {
        throw new Error('Invalid Google Sheets URL')
      }

      // For now, we'll use a mock implementation
      // In production, this would use the Google Sheets API
      const mockData = await this.mockSheetData(sheetId)
      return mockData
    } catch (error) {
      console.error('Error reading Google Sheet:', error)
      return null
    }
  }

  /**
   * Mock implementation for development
   * In production, this would use the real Google Sheets API
   */
  private async mockSheetData(sheetId: string): Promise<GoogleSheetData> {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Return mock data based on the actual sheet structure
    return {
      id: sheetId,
      name: 'HNWIs, Family Offices & Hedge Funds - Pablo D.',
      url: `https://docs.google.com/spreadsheets/d/${sheetId}/edit`,
      lastSync: new Date(),
      columns: [
        'Company Name',
        'Name', 
        'Person\'s LinkedIn',
        'Website',
        'Company LinkedIn',
        'Country',
        'Title',
        'Email 1',
        'Email 2',
        'Direct Phone#',
        'Connected',
        'Ben',
        'Pablo',
        'Linkedin Co'
      ],
      data: [
        {
          'Company Name': 'Cerberus Capital Management',
          'Name': 'Daniel Wolf',
          'Person\'s LinkedIn': 'https://www.linkedin.com/in/daniel-wolf-127792122/',
          'Website': 'cerberus.com',
          'Company LinkedIn': 'https://www.linkedin.com/company/cerberus-capital-management/',
          'Country': 'United States',
          'Title': 'Chief Executive Officer and Chief Investment Officer, Cerberus Business Finance, and Senior Managing Director, Cerberus Capital Management',
          'Email 1': 'dwolf@cerberus.com',
          'Email 2': 'dewolf535@gmail.com',
          'Direct Phone#': '646-207-3154',
          'Connected': 'no',
          'Ben': 'no',
          'Pablo': 'yes',
          'Linkedin Co': 'Hi Daniel, I noticed Cerberus helped finance Ann Street Lofts in Savannah\'s Opportunity Zone. We are working on Hazen Road, a Phoenix BTR community in an OZ with similar fundamentals. I think connecting could be mutually valuable.'
        },
        {
          'Company Name': 'Cerberus Capital Management',
          'Name': 'Michael Johnson',
          'Person\'s LinkedIn': 'https://www.linkedin.com/in/michael-johnson-7989392/',
          'Website': '',
          'Company LinkedIn': '',
          'Country': '',
          'Title': 'Managing Director',
          'Email 1': 'mjohnson@cerberus.com',
          'Email 2': 'msjohnson@gmail.com',
          'Direct Phone#': '917-902-5028',
          'Connected': 'no',
          'Ben': 'no',
          'Pablo': 'yes',
          'Linkedin Co': 'Hi Michael, Cerberus\'s role in OZ multifamily projects like Ann Street Lofts stood out. Hazen Road, a Phoenix BTR community in an OZ, is built on the same institutional structure and fundamentals. I believe connecting could be mutually valuable.'
        },
        {
          'Company Name': 'Cerberus Capital Management',
          'Name': 'Neha Santiago',
          'Person\'s LinkedIn': 'https://www.linkedin.com/in/neha-santiago-123456789/',
          'Website': '',
          'Company LinkedIn': '',
          'Country': '',
          'Title': 'Managing Director & Head of Real Estate',
          'Email 1': 'nsantiago@cerberus.com',
          'Email 2': 'nehasahni01@gmail.com',
          'Direct Phone#': '917-526-0223',
          'Connected': 'no',
          'Ben': 'no',
          'Pablo': 'yes',
          'Linkedin Co': 'Hi Neha, Cerberus\'s role in Opportunity Zone multifamily projects stood out. We are developing Hazen Road, a Phoenix BTR community in an OZ with similar fundamentals. I believe connecting could be mutually valuable.'
        },
        {
          'Company Name': 'Avanath Capital Management',
          'Name': 'Wesley Wilson',
          'Person\'s LinkedIn': 'https://www.linkedin.com/in/wesley-wilson-987654321/',
          'Website': 'avanath.com',
          'Company LinkedIn': 'https://www.linkedin.com/company/avanath-capital-management/',
          'Country': 'United States',
          'Title': 'Partner, Chief Investment Officer',
          'Email 1': 'wwilson@avanath.com',
          'Email 2': 'ooto_wes@cox.net',
          'Direct Phone#': '949-632-0738',
          'Connected': 'no',
          'Ben': 'no',
          'Pablo': 'yes',
          'Linkedin Co': 'Hi Wesley, Avanath\'s focus on workforce housing and Opportunity Zone investments stood out. We are developing Hazen Road, a Phoenix BTR community in an OZ, and believe connecting could be mutually valuable.'
        }
      ],
      isConnected: true
    }
  }

  /**
   * Write data to Google Sheets
   */
  async writeSheetData(sheetId: string, data: GoogleSheetRow[]): Promise<boolean> {
    try {
      // Mock implementation
      console.log('Writing data to sheet:', sheetId, data)
      return true
    } catch (error) {
      console.error('Error writing to Google Sheet:', error)
      return false
    }
  }

  /**
   * Sync data with Google Sheets
   */
  async syncSheet(sheetId: string): Promise<GoogleSheetData | null> {
    return this.readSheetData(`https://docs.google.com/spreadsheets/d/${sheetId}/edit`)
  }
}

export const googleSheetsService = new GoogleSheetsService()
