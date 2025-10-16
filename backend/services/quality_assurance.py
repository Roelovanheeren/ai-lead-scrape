"""
Quality Assurance Service
Handles automated QA validation and human review workflows
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from ..database.connection import DatabaseConnection
from ..models.schemas import QAReviewRequest, QAReviewResponse, QAStatus, QualityMetrics
from ..utils.schema_validator import SchemaValidator
from ..utils.email_validator import EmailValidator
from ..utils.content_validator import ContentValidator
from ..utils.scoring_engine import ScoringEngine
from ..integrations.notification_service import NotificationService

logger = logging.getLogger(__name__)

class QualityAssuranceService:
    """Service for quality assurance and validation"""
    
    def __init__(self):
        self.schema_validator = SchemaValidator()
        self.email_validator = EmailValidator()
        self.content_validator = ContentValidator()
        self.scoring_engine = ScoringEngine()
        self.notification_service = NotificationService()
    
    async def run_qa_pipeline(self, job_id: str) -> Dict[str, Any]:
        """Run comprehensive QA pipeline for a job"""
        try:
            logger.info(f"Starting QA pipeline for job {job_id}")
            
            # Get all records for the job
            companies = await self._get_job_companies(job_id)
            contacts = await self._get_job_contacts(job_id)
            outreach_content = await self._get_job_outreach(job_id)
            
            qa_results = {
                'job_id': job_id,
                'companies_checked': 0,
                'contacts_checked': 0,
                'outreach_checked': 0,
                'companies_passed': 0,
                'contacts_passed': 0,
                'outreach_passed': 0,
                'issues_found': [],
                'human_review_required': []
            }
            
            # QA Companies
            company_results = await self._qa_companies(companies)
            qa_results['companies_checked'] = len(companies)
            qa_results['companies_passed'] = company_results['passed']
            qa_results['issues_found'].extend(company_results['issues'])
            qa_results['human_review_required'].extend(company_results['human_review'])
            
            # QA Contacts
            contact_results = await self._qa_contacts(contacts)
            qa_results['contacts_checked'] = len(contacts)
            qa_results['contacts_passed'] = contact_results['passed']
            qa_results['issues_found'].extend(contact_results['issues'])
            qa_results['human_review_required'].extend(contact_results['human_review'])
            
            # QA Outreach Content
            outreach_results = await self._qa_outreach_content(outreach_content)
            qa_results['outreach_checked'] = len(outreach_content)
            qa_results['outreach_passed'] = outreach_results['passed']
            qa_results['issues_found'].extend(outreach_results['issues'])
            qa_results['human_review_required'].extend(outreach_results['human_review'])
            
            # Calculate overall quality score
            overall_score = await self._calculate_overall_quality_score(qa_results)
            qa_results['overall_quality_score'] = overall_score
            
            # Store QA results
            await self._store_qa_results(job_id, qa_results)
            
            # Send notifications if issues found
            if qa_results['issues_found'] or qa_results['human_review_required']:
                await self.notification_service.send_qa_issues_notification(job_id, qa_results)
            
            logger.info(f"QA pipeline completed for job {job_id}: {overall_score:.2f} quality score")
            return qa_results
            
        except Exception as e:
            logger.error(f"Error running QA pipeline for job {job_id}: {str(e)}")
            raise
    
    async def _qa_companies(self, companies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run QA checks on companies"""
        try:
            results = {
                'passed': 0,
                'issues': [],
                'human_review': []
            }
            
            for company in companies:
                company_issues = []
                
                # Schema validation
                schema_valid = await self.schema_validator.validate_company(company)
                if not schema_valid['valid']:
                    company_issues.extend(schema_valid['errors'])
                
                # Business rule validation
                business_valid = await self._validate_company_business_rules(company)
                if not business_valid['valid']:
                    company_issues.extend(business_valid['errors'])
                
                # Data quality checks
                quality_valid = await self._validate_company_data_quality(company)
                if not quality_valid['valid']:
                    company_issues.extend(quality_valid['errors'])
                
                if not company_issues:
                    results['passed'] += 1
                else:
                    results['issues'].append({
                        'record_type': 'company',
                        'record_id': company['id'],
                        'issues': company_issues
                    })
                    
                    # Determine if human review needed
                    if await self._requires_human_review(company_issues):
                        results['human_review'].append({
                            'record_type': 'company',
                            'record_id': company['id'],
                            'reason': 'complex_validation_issues'
                        })
            
            return results
            
        except Exception as e:
            logger.error(f"Error QA-ing companies: {str(e)}")
            return {'passed': 0, 'issues': [], 'human_review': []}
    
    async def _qa_contacts(self, contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run QA checks on contacts"""
        try:
            results = {
                'passed': 0,
                'issues': [],
                'human_review': []
            }
            
            for contact in contacts:
                contact_issues = []
                
                # Schema validation
                schema_valid = await self.schema_validator.validate_contact(contact)
                if not schema_valid['valid']:
                    contact_issues.extend(schema_valid['errors'])
                
                # Email validation
                if contact.get('email'):
                    email_valid = await self.email_validator.validate_email(contact['email'])
                    if not email_valid['valid']:
                        contact_issues.extend(email_valid['errors'])
                
                # LinkedIn URL validation
                if contact.get('linkedin_url'):
                    linkedin_valid = await self._validate_linkedin_url(contact['linkedin_url'])
                    if not linkedin_valid['valid']:
                        contact_issues.extend(linkedin_valid['errors'])
                
                # Contact quality checks
                quality_valid = await self._validate_contact_quality(contact)
                if not quality_valid['valid']:
                    contact_issues.extend(quality_valid['errors'])
                
                if not contact_issues:
                    results['passed'] += 1
                else:
                    results['issues'].append({
                        'record_type': 'contact',
                        'record_id': contact['id'],
                        'issues': contact_issues
                    })
                    
                    # Determine if human review needed
                    if await self._requires_human_review(contact_issues):
                        results['human_review'].append({
                            'record_type': 'contact',
                            'record_id': contact['id'],
                            'reason': 'email_verification_failed'
                        })
            
            return results
            
        except Exception as e:
            logger.error(f"Error QA-ing contacts: {str(e)}")
            return {'passed': 0, 'issues': [], 'human_review': []}
    
    async def _qa_outreach_content(self, outreach_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run QA checks on outreach content"""
        try:
            results = {
                'passed': 0,
                'issues': [],
                'human_review': []
            }
            
            for content in outreach_content:
                content_issues = []
                
                # Schema validation
                schema_valid = await self.schema_validator.validate_outreach_content(content)
                if not schema_valid['valid']:
                    content_issues.extend(schema_valid['errors'])
                
                # Content validation
                content_valid = await self.content_validator.validate_outreach_content(content)
                if not content_valid['valid']:
                    content_issues.extend(content_valid['errors'])
                
                # Tone and style validation
                tone_valid = await self._validate_outreach_tone(content)
                if not tone_valid['valid']:
                    content_issues.extend(tone_valid['errors'])
                
                # Grammar and readability validation
                grammar_valid = await self._validate_outreach_grammar(content)
                if not grammar_valid['valid']:
                    content_issues.extend(grammar_valid['errors'])
                
                if not content_issues:
                    results['passed'] += 1
                else:
                    results['issues'].append({
                        'record_type': 'outreach',
                        'record_id': content['id'],
                        'issues': content_issues
                    })
                    
                    # Determine if human review needed
                    if await self._requires_human_review(content_issues):
                        results['human_review'].append({
                            'record_type': 'outreach',
                            'record_id': content['id'],
                            'reason': 'content_quality_issues'
                        })
            
            return results
            
        except Exception as e:
            logger.error(f"Error QA-ing outreach content: {str(e)}")
            return {'passed': 0, 'issues': [], 'human_review': []}
    
    async def get_pending_reviews(self, db: DatabaseConnection) -> List[Dict[str, Any]]:
        """Get items pending QA review"""
        try:
            results = await db.fetch_all(
                """
                SELECT qr.*, 
                       CASE 
                           WHEN qr.record_type = 'company' THEN c.name
                           WHEN qr.record_type = 'contact' THEN CONCAT(ct.first_name, ' ', ct.last_name)
                           WHEN qr.record_type = 'outreach' THEN oc.body
                       END as record_summary
                FROM qa_reviews qr
                LEFT JOIN companies c ON qr.record_type = 'company' AND qr.record_id = c.id
                LEFT JOIN contacts ct ON qr.record_type = 'contact' AND qr.record_id = ct.id
                LEFT JOIN outreach_content oc ON qr.record_type = 'outreach' AND qr.record_id = oc.id
                WHERE qr.status = 'pending'
                ORDER BY qr.created_at DESC
                """
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting pending reviews: {str(e)}")
            raise
    
    async def submit_review(self, db: DatabaseConnection, review: QAReviewRequest) -> QAReviewResponse:
        """Submit QA review for an item"""
        try:
            review_id = str(uuid.uuid4())
            
            # Create review record
            review_record = {
                "id": review_id,
                "record_type": review.record_type,
                "record_id": review.record_id,
                "status": review.status,
                "feedback": review.feedback,
                "score": review.score,
                "reviewed_at": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
            
            # Store review
            await db.execute(
                """
                INSERT INTO qa_reviews (id, record_type, record_id, status, feedback, score, reviewed_at, created_at)
                VALUES (%(id)s, %(record_type)s, %(record_id)s, %(status)s, %(feedback)s, %(score)s, %(reviewed_at)s, %(created_at)s)
                """,
                review_record
            )
            
            # Update record status based on review
            await self._update_record_status(db, review.record_type, review.record_id, review.status)
            
            logger.info(f"QA review submitted for {review.record_type} {review.record_id}")
            return QAReviewResponse(**review_record)
            
        except Exception as e:
            logger.error(f"Error submitting QA review: {str(e)}")
            raise
    
    async def get_quality_metrics(self, db: DatabaseConnection, days: int = 30) -> QualityMetrics:
        """Get quality assurance metrics"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Overall quality score
            quality_score_result = await db.fetch_one(
                """
                SELECT AVG(score) as avg_score
                FROM qa_reviews 
                WHERE created_at >= %s AND score IS NOT NULL
                """,
                (start_date,)
            )
            overall_quality_score = quality_score_result['avg_score'] or 0.0
            
            # Contact accuracy
            contact_accuracy_result = await db.fetch_one(
                """
                SELECT 
                    COUNT(CASE WHEN ct.email_status = 'valid' THEN 1 END) as valid_emails,
                    COUNT(ct.id) as total_contacts
                FROM contacts ct
                JOIN companies c ON ct.company_id = c.id
                JOIN jobs j ON c.job_id = j.id
                WHERE j.created_at >= %s
                """,
                (start_date,)
            )
            contact_accuracy = 0.0
            if contact_accuracy_result['total_contacts'] > 0:
                contact_accuracy = contact_accuracy_result['valid_emails'] / contact_accuracy_result['total_contacts']
            
            # Email verification rate
            email_verification_result = await db.fetch_one(
                """
                SELECT 
                    COUNT(CASE WHEN email_confidence >= 0.7 THEN 1 END) as verified_emails,
                    COUNT(CASE WHEN email IS NOT NULL THEN 1 END) as total_emails
                FROM contacts ct
                JOIN companies c ON ct.company_id = c.id
                JOIN jobs j ON c.job_id = j.id
                WHERE j.created_at >= %s
                """,
                (start_date,)
            )
            email_verification_rate = 0.0
            if email_verification_result['total_emails'] > 0:
                email_verification_rate = email_verification_result['verified_emails'] / email_verification_result['total_emails']
            
            # Outreach approval rate
            outreach_approval_result = await db.fetch_one(
                """
                SELECT 
                    COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved_outreach,
                    COUNT(id) as total_outreach
                FROM outreach_content oc
                JOIN companies c ON oc.company_id = c.id
                JOIN jobs j ON c.job_id = j.id
                WHERE j.created_at >= %s
                """,
                (start_date,)
            )
            outreach_approval_rate = 0.0
            if outreach_approval_result['total_outreach'] > 0:
                outreach_approval_rate = outreach_approval_result['approved_outreach'] / outreach_approval_result['total_outreach']
            
            # QA failure rate
            qa_failure_result = await db.fetch_one(
                """
                SELECT 
                    COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected_items,
                    COUNT(id) as total_reviews
                FROM qa_reviews 
                WHERE created_at >= %s
                """,
                (start_date,)
            )
            qa_failure_rate = 0.0
            if qa_failure_result['total_reviews'] > 0:
                qa_failure_rate = qa_failure_result['rejected_items'] / qa_failure_result['total_reviews']
            
            # Human review rate
            human_review_result = await db.fetch_one(
                """
                SELECT 
                    COUNT(CASE WHEN status IN ('approved', 'rejected') THEN 1 END) as reviewed_items,
                    COUNT(id) as total_pending
                FROM qa_reviews 
                WHERE created_at >= %s
                """,
                (start_date,)
            )
            human_review_rate = 0.0
            if human_review_result['total_pending'] > 0:
                human_review_rate = human_review_result['reviewed_items'] / human_review_result['total_pending']
            
            return QualityMetrics(
                overall_quality_score=float(overall_quality_score),
                contact_accuracy=float(contact_accuracy),
                email_verification_rate=float(email_verification_rate),
                outreach_approval_rate=float(outreach_approval_rate),
                qa_failure_rate=float(qa_failure_rate),
                human_review_rate=float(human_review_rate)
            )
            
        except Exception as e:
            logger.error(f"Error getting quality metrics: {str(e)}")
            raise
    
    # Helper methods
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
    
    async def _validate_company_business_rules(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Validate company against business rules"""
        # Add business rule validation logic here
        return {'valid': True, 'errors': []}
    
    async def _validate_company_data_quality(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Validate company data quality"""
        # Add data quality validation logic here
        return {'valid': True, 'errors': []}
    
    async def _validate_contact_quality(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """Validate contact data quality"""
        # Add contact quality validation logic here
        return {'valid': True, 'errors': []}
    
    async def _validate_linkedin_url(self, url: str) -> Dict[str, Any]:
        """Validate LinkedIn URL format"""
        # Add LinkedIn URL validation logic here
        return {'valid': True, 'errors': []}
    
    async def _validate_outreach_tone(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate outreach tone and style"""
        # Add tone validation logic here
        return {'valid': True, 'errors': []}
    
    async def _validate_outreach_grammar(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate outreach grammar and readability"""
        # Add grammar validation logic here
        return {'valid': True, 'errors': []}
    
    async def _requires_human_review(self, issues: List[str]) -> bool:
        """Determine if record requires human review"""
        # Add human review logic here
        return len(issues) > 3
    
    async def _calculate_overall_quality_score(self, qa_results: Dict[str, Any]) -> float:
        """Calculate overall quality score"""
        try:
            total_checked = (qa_results['companies_checked'] + 
                           qa_results['contacts_checked'] + 
                           qa_results['outreach_checked'])
            
            if total_checked == 0:
                return 0.0
            
            total_passed = (qa_results['companies_passed'] + 
                           qa_results['contacts_passed'] + 
                           qa_results['outreach_passed'])
            
            return total_passed / total_checked
            
        except Exception as e:
            logger.error(f"Error calculating overall quality score: {str(e)}")
            return 0.0
    
    async def _store_qa_results(self, job_id: str, qa_results: Dict[str, Any]):
        """Store QA results in database"""
        # Implementation would store results
        pass
    
    async def _update_record_status(self, db: DatabaseConnection, record_type: str, record_id: str, status: QAStatus):
        """Update record status based on QA review"""
        # Implementation would update record status
        pass
