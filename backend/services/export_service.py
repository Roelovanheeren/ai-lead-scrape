"""
Export Service
Handles data export to Google Sheets, CRM systems, and other delivery channels
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from ..database.connection import DatabaseConnection
from ..integrations.google_sheets import GoogleSheetsClient
from ..integrations.aimfox_client import AimfoxClient
from ..integrations.ghl_client import GHLClient
from ..integrations.slack_client import SlackClient
from ..integrations.email_client import EmailClient
from ..utils.data_formatter import DataFormatter
from ..utils.csv_generator import CSVGenerator
from ..utils.json_export import JSONExporter

logger = logging.getLogger(__name__)

class ExportService:
    """Service for exporting and delivering lead generation results"""
    
    def __init__(self):
        self.google_sheets = GoogleSheetsClient()
        self.aimfox_client = AimfoxClient()
        self.ghl_client = GHLClient()
        self.slack_client = SlackClient()
        self.email_client = EmailClient()
        self.data_formatter = DataFormatter()
        self.csv_generator = CSVGenerator()
        self.json_exporter = JSONExporter()
    
    async def export_job_results(self, job_id: str) -> Dict[str, Any]:
        """Export complete job results to all configured channels"""
        try:
            logger.info(f"Starting export for job {job_id}")
            
            # Get job data
            job_data = await self._get_job_data(job_id)
            companies = await self._get_job_companies(job_id)
            contacts = await self._get_job_contacts(job_id)
            outreach_content = await self._get_job_outreach(job_id)
            
            export_results = {
                'job_id': job_id,
                'export_timestamp': datetime.utcnow(),
                'companies_exported': len(companies),
                'contacts_exported': len(contacts),
                'outreach_exported': len(outreach_content),
                'export_channels': [],
                'download_urls': {},
                'delivery_status': {}
            }
            
            # 1. Google Sheets Export
            sheets_result = await self._export_to_google_sheets(job_data, companies, contacts, outreach_content)
            export_results['export_channels'].append('google_sheets')
            export_results['download_urls']['google_sheets'] = sheets_result.get('url')
            export_results['delivery_status']['google_sheets'] = sheets_result.get('status')
            
            # 2. CSV Export
            csv_result = await self._export_to_csv(job_data, companies, contacts, outreach_content)
            export_results['export_channels'].append('csv')
            export_results['download_urls']['csv'] = csv_result.get('url')
            export_results['delivery_status']['csv'] = csv_result.get('status')
            
            # 3. JSON Export
            json_result = await self._export_to_json(job_data, companies, contacts, outreach_content)
            export_results['export_channels'].append('json')
            export_results['download_urls']['json'] = json_result.get('url')
            export_results['delivery_status']['json'] = json_result.get('status')
            
            # 4. Slack Notification
            slack_result = await self._send_slack_notification(job_data, export_results)
            export_results['delivery_status']['slack'] = slack_result.get('status')
            
            # 5. Email Summary
            email_result = await self._send_email_summary(job_data, export_results)
            export_results['delivery_status']['email'] = email_result.get('status')
            
            # Store export results
            await self._store_export_results(job_id, export_results)
            
            logger.info(f"Export completed for job {job_id}")
            return export_results
            
        except Exception as e:
            logger.error(f"Error exporting job {job_id}: {str(e)}")
            raise
    
    async def export_to_google_sheets(self, db: DatabaseConnection, job_id: str) -> Dict[str, Any]:
        """Export job results to Google Sheets"""
        try:
            # Get job data
            job_data = await self._get_job_data(job_id)
            companies = await self._get_job_companies(job_id)
            contacts = await self._get_job_contacts(job_id)
            outreach_content = await self._get_job_outreach(job_id)
            
            # Create Google Sheets workbook
            workbook_id = await self.google_sheets.create_workbook(f"Lead Generation - {job_data['name']}")
            
            # Export companies
            companies_sheet = await self._create_companies_sheet(workbook_id, companies)
            
            # Export contacts
            contacts_sheet = await self._create_contacts_sheet(workbook_id, contacts)
            
            # Export outreach content
            outreach_sheet = await self._create_outreach_sheet(workbook_id, outreach_content)
            
            # Export research summaries
            research_sheet = await self._create_research_sheet(workbook_id, companies)
            
            # Format sheets
            await self._format_google_sheets(workbook_id, [companies_sheet, contacts_sheet, outreach_sheet, research_sheet])
            
            # Share workbook
            share_url = await self.google_sheets.share_workbook(workbook_id)
            
            logger.info(f"Google Sheets export completed for job {job_id}")
            return {
                'status': 'success',
                'workbook_id': workbook_id,
                'url': share_url,
                'sheets': [companies_sheet, contacts_sheet, outreach_sheet, research_sheet]
            }
            
        except Exception as e:
            logger.error(f"Error exporting to Google Sheets for job {job_id}: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def deliver_to_aimfox(self, db: DatabaseConnection, job_id: str) -> Dict[str, Any]:
        """Deliver outreach content to Aimfox for automation"""
        try:
            # Get approved outreach content
            outreach_content = await self._get_approved_outreach_content(job_id)
            
            if not outreach_content:
                logger.warning(f"No approved outreach content found for job {job_id}")
                return {'status': 'no_content', 'message': 'No approved outreach content'}
            
            delivery_results = []
            
            for content in outreach_content:
                # Prepare Aimfox payload
                aimfox_payload = await self._prepare_aimfox_payload(content)
                
                # Send to Aimfox
                aimfox_result = await self.aimfox_client.create_sequence(aimfox_payload)
                
                if aimfox_result.get('success'):
                    # Store automation tracking
                    await self._store_automation_tracking(content['id'], 'aimfox', aimfox_result.get('sequence_id'))
                    delivery_results.append({
                        'outreach_id': content['id'],
                        'aimfox_sequence_id': aimfox_result.get('sequence_id'),
                        'status': 'success'
                    })
                else:
                    delivery_results.append({
                        'outreach_id': content['id'],
                        'status': 'failed',
                        'error': aimfox_result.get('error')
                    })
            
            success_count = len([r for r in delivery_results if r['status'] == 'success'])
            
            logger.info(f"Aimfox delivery completed for job {job_id}: {success_count}/{len(delivery_results)} successful")
            return {
                'status': 'success',
                'delivered_count': success_count,
                'total_count': len(delivery_results),
                'results': delivery_results
            }
            
        except Exception as e:
            logger.error(f"Error delivering to Aimfox for job {job_id}: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def deliver_to_ghl(self, db: DatabaseConnection, job_id: str) -> Dict[str, Any]:
        """Deliver contacts and research to GoHighLevel"""
        try:
            # Get companies and contacts
            companies = await self._get_job_companies(job_id)
            contacts = await self._get_job_contacts(job_id)
            research_profiles = await self._get_job_research_profiles(job_id)
            
            delivery_results = {
                'companies_synced': 0,
                'contacts_synced': 0,
                'opportunities_created': 0,
                'campaigns_created': 0,
                'errors': []
            }
            
            # Sync companies to GHL
            for company in companies:
                try:
                    ghl_company = await self._prepare_ghl_company(company)
                    ghl_result = await self.ghl_client.create_company(ghl_company)
                    
                    if ghl_result.get('success'):
                        delivery_results['companies_synced'] += 1
                        company['ghl_company_id'] = ghl_result.get('company_id')
                    else:
                        delivery_results['errors'].append({
                            'type': 'company',
                            'id': company['id'],
                            'error': ghl_result.get('error')
                        })
                        
                except Exception as e:
                    delivery_results['errors'].append({
                        'type': 'company',
                        'id': company['id'],
                        'error': str(e)
                    })
            
            # Sync contacts to GHL
            for contact in contacts:
                try:
                    ghl_contact = await self._prepare_ghl_contact(contact)
                    ghl_result = await self.ghl_client.create_contact(ghl_contact)
                    
                    if ghl_result.get('success'):
                        delivery_results['contacts_synced'] += 1
                        contact['ghl_contact_id'] = ghl_result.get('contact_id')
                    else:
                        delivery_results['errors'].append({
                            'type': 'contact',
                            'id': contact['id'],
                            'error': ghl_result.get('error')
                        })
                        
                except Exception as e:
                    delivery_results['errors'].append({
                        'type': 'contact',
                        'id': contact['id'],
                        'error': str(e)
                    })
            
            # Create opportunities
            for company in companies:
                if company.get('ghl_company_id'):
                    try:
                        opportunity = await self._prepare_ghl_opportunity(company, research_profiles.get(company['id']))
                        opp_result = await self.ghl_client.create_opportunity(opportunity)
                        
                        if opp_result.get('success'):
                            delivery_results['opportunities_created'] += 1
                        else:
                            delivery_results['errors'].append({
                                'type': 'opportunity',
                                'company_id': company['id'],
                                'error': opp_result.get('error')
                            })
                            
                    except Exception as e:
                        delivery_results['errors'].append({
                            'type': 'opportunity',
                            'company_id': company['id'],
                            'error': str(e)
                        })
            
            # Create email campaigns
            outreach_content = await self._get_approved_outreach_content(job_id)
            for content in outreach_content:
                if content.get('channel') == 'email':
                    try:
                        campaign = await self._prepare_ghl_campaign(content)
                        campaign_result = await self.ghl_client.create_campaign(campaign)
                        
                        if campaign_result.get('success'):
                            delivery_results['campaigns_created'] += 1
                        else:
                            delivery_results['errors'].append({
                                'type': 'campaign',
                                'outreach_id': content['id'],
                                'error': campaign_result.get('error')
                            })
                            
                    except Exception as e:
                        delivery_results['errors'].append({
                            'type': 'campaign',
                            'outreach_id': content['id'],
                            'error': str(e)
                        })
            
            logger.info(f"GHL delivery completed for job {job_id}")
            return {
                'status': 'success',
                'results': delivery_results
            }
            
        except Exception as e:
            logger.error(f"Error delivering to GHL for job {job_id}: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def _export_to_csv(self, job_data: Dict[str, Any], companies: List[Dict[str, Any]], 
                           contacts: List[Dict[str, Any]], outreach_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Export data to CSV files"""
        try:
            # Generate CSV files
            companies_csv = await self.csv_generator.generate_companies_csv(companies)
            contacts_csv = await self.csv_generator.generate_contacts_csv(contacts)
            outreach_csv = await self.csv_generator.generate_outreach_csv(outreach_content)
            
            # Upload to storage
            companies_url = await self._upload_csv_file(companies_csv, f"companies_{job_data['id']}.csv")
            contacts_url = await self._upload_csv_file(contacts_csv, f"contacts_{job_data['id']}.csv")
            outreach_url = await self._upload_csv_file(outreach_csv, f"outreach_{job_data['id']}.csv")
            
            return {
                'status': 'success',
                'url': {
                    'companies': companies_url,
                    'contacts': contacts_url,
                    'outreach': outreach_url
                }
            }
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def _export_to_json(self, job_data: Dict[str, Any], companies: List[Dict[str, Any]], 
                            contacts: List[Dict[str, Any]], outreach_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Export data to JSON file"""
        try:
            # Generate JSON export
            json_data = await self.json_exporter.generate_export(job_data, companies, contacts, outreach_content)
            
            # Upload to storage
            json_url = await self._upload_json_file(json_data, f"export_{job_data['id']}.json")
            
            return {
                'status': 'success',
                'url': json_url
            }
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def _send_slack_notification(self, job_data: Dict[str, Any], export_results: Dict[str, Any]) -> Dict[str, Any]:
        """Send Slack notification with export summary"""
        try:
            message = await self._format_slack_message(job_data, export_results)
            result = await self.slack_client.send_message(message)
            
            return {
                'status': 'success' if result.get('ok') else 'error',
                'message_id': result.get('ts')
            }
            
        except Exception as e:
            logger.error(f"Error sending Slack notification: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def _send_email_summary(self, job_data: Dict[str, Any], export_results: Dict[str, Any]) -> Dict[str, Any]:
        """Send email summary with export results"""
        try:
            email_content = await self._format_email_summary(job_data, export_results)
            result = await self.email_client.send_email(
                to=job_data.get('user_email'),
                subject=f"Lead Generation Complete - {job_data['name']}",
                body=email_content
            )
            
            return {
                'status': 'success' if result.get('success') else 'error',
                'message_id': result.get('message_id')
            }
            
        except Exception as e:
            logger.error(f"Error sending email summary: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    # Helper methods
    async def _get_job_data(self, job_id: str) -> Dict[str, Any]:
        """Get job data from database"""
        # Implementation would fetch from database
        return {}
    
    async def _get_job_companies(self, job_id: str) -> List[Dict[str, Any]]:
        """Get companies for a job"""
        # Implementation would fetch from database
        return []
    
    async def _get_job_contacts(self, job_id: str) -> List[Dict[str, Any]]:
        """Get contacts for a job"""
        # Implementation would fetch from database
        return []
    
    async def _get_job_outreach(self, job_id: str) -> List[Dict[str, Any]]:
        """Get outreach content for a job"""
        # Implementation would fetch from database
        return []
    
    async def _get_approved_outreach_content(self, job_id: str) -> List[Dict[str, Any]]:
        """Get approved outreach content for a job"""
        # Implementation would fetch from database
        return []
    
    async def _get_job_research_profiles(self, job_id: str) -> Dict[str, Any]:
        """Get research profiles for a job"""
        # Implementation would fetch from database
        return {}
    
    async def _create_companies_sheet(self, workbook_id: str, companies: List[Dict[str, Any]]) -> str:
        """Create companies sheet in Google Sheets"""
        # Implementation would create sheet
        return "companies"
    
    async def _create_contacts_sheet(self, workbook_id: str, contacts: List[Dict[str, Any]]) -> str:
        """Create contacts sheet in Google Sheets"""
        # Implementation would create sheet
        return "contacts"
    
    async def _create_outreach_sheet(self, workbook_id: str, outreach_content: List[Dict[str, Any]]) -> str:
        """Create outreach sheet in Google Sheets"""
        # Implementation would create sheet
        return "outreach"
    
    async def _create_research_sheet(self, workbook_id: str, companies: List[Dict[str, Any]]) -> str:
        """Create research sheet in Google Sheets"""
        # Implementation would create sheet
        return "research"
    
    async def _format_google_sheets(self, workbook_id: str, sheet_names: List[str]):
        """Format Google Sheets with styling"""
        # Implementation would format sheets
        pass
    
    async def _prepare_aimfox_payload(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare payload for Aimfox"""
        # Implementation would prepare payload
        return {}
    
    async def _prepare_ghl_company(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare company data for GHL"""
        # Implementation would prepare company data
        return {}
    
    async def _prepare_ghl_contact(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare contact data for GHL"""
        # Implementation would prepare contact data
        return {}
    
    async def _prepare_ghl_opportunity(self, company: Dict[str, Any], research_profile: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare opportunity data for GHL"""
        # Implementation would prepare opportunity data
        return {}
    
    async def _prepare_ghl_campaign(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare campaign data for GHL"""
        # Implementation would prepare campaign data
        return {}
    
    async def _upload_csv_file(self, csv_content: str, filename: str) -> str:
        """Upload CSV file to storage"""
        # Implementation would upload to S3 or similar
        return f"https://storage.example.com/{filename}"
    
    async def _upload_json_file(self, json_content: str, filename: str) -> str:
        """Upload JSON file to storage"""
        # Implementation would upload to S3 or similar
        return f"https://storage.example.com/{filename}"
    
    async def _format_slack_message(self, job_data: Dict[str, Any], export_results: Dict[str, Any]) -> str:
        """Format Slack message"""
        # Implementation would format message
        return "Lead generation completed"
    
    async def _format_email_summary(self, job_data: Dict[str, Any], export_results: Dict[str, Any]) -> str:
        """Format email summary"""
        # Implementation would format email
        return "Lead generation completed"
    
    async def _store_export_results(self, job_id: str, export_results: Dict[str, Any]):
        """Store export results in database"""
        # Implementation would store results
        pass
    
    async def _store_automation_tracking(self, outreach_id: str, platform: str, external_id: str):
        """Store automation tracking information"""
        # Implementation would store tracking
        pass
