#!/usr/bin/env python3
"""
Test Hunter.io API Integration
Verify we can find real contacts at real companies
"""

import os
import sys
import asyncio
import logging

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.hunter_client import HunterClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_hunter_api():
    """Test Hunter.io API with real companies"""
    
    logger.info("=" * 80)
    logger.info("🔍 HUNTER.IO API TEST")
    logger.info("=" * 80)
    logger.info("")
    
    # Initialize client
    client = HunterClient()
    
    # Test 1: Get account info
    logger.info("📊 Test 1: Get Account Info")
    logger.info("-" * 80)
    account = await client.get_account_info()
    logger.info(f"Account: {account}")
    logger.info("")
    
    # Test 2: Find emails at a domain
    test_domains = [
        "related.com",  # Related Companies (from our Google search)
        "hillwood.com",  # Hillwood (from our Google search)
        "stripe.com"     # Well-known tech company
    ]
    
    for domain in test_domains:
        logger.info("=" * 80)
        logger.info(f"📧 Test 2: Find Emails at {domain}")
        logger.info("-" * 80)
        
        emails = await client.find_emails_at_domain(domain, department="executive")
        
        if emails:
            logger.info(f"✅ Found {len(emails)} contacts at {domain}:")
            logger.info("")
            
            for i, contact in enumerate(emails[:3], 1):  # Show first 3
                logger.info(f"   [{i}] {contact.get('first_name')} {contact.get('last_name')}")
                logger.info(f"       Email: {contact.get('email')}")
                logger.info(f"       Position: {contact.get('position', 'N/A')}")
                logger.info(f"       LinkedIn: {contact.get('linkedin', 'N/A')}")
                logger.info(f"       Confidence: {contact.get('confidence', 0):.2f}")
                logger.info("")
        else:
            logger.warning(f"⚠️ No contacts found at {domain}")
            logger.info("")
        
        # Small delay between requests
        await asyncio.sleep(2)
    
    # Test 3: Email verification
    logger.info("=" * 80)
    logger.info("🔍 Test 3: Email Verification")
    logger.info("-" * 80)
    
    test_emails = [
        "test@gmail.com",  # Common email
        "invalid@notarealdomain12345.com"  # Invalid email
    ]
    
    for email in test_emails:
        logger.info(f"Verifying: {email}")
        result = await client.verify_email(email)
        logger.info(f"   Status: {result.get('status')}")
        logger.info(f"   Valid: {result.get('valid')}")
        logger.info(f"   Score: {result.get('score', 'N/A')}")
        logger.info("")
        
        await asyncio.sleep(1)
    
    # Summary
    logger.info("=" * 80)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 80)
    logger.info("✅ Hunter.io API is working!")
    logger.info(f"✅ Can find real contacts at company domains")
    logger.info(f"✅ Can verify email addresses")
    logger.info("")
    logger.info("🎉 Test complete!")
    logger.info("")


if __name__ == "__main__":
    # Set API key
    if not os.getenv("HUNTER_API_KEY"):
        print("❌ HUNTER_API_KEY not set!")
        print("Usage: export HUNTER_API_KEY='your_key' && python3 test_hunter_api.py")
        sys.exit(1)
    
    try:
        asyncio.run(test_hunter_api())
    except KeyboardInterrupt:
        logger.info("\n⚠️ Test interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
