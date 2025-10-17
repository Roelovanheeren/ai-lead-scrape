#!/usr/bin/env python3
"""
Test: Hazen Road Institutional Investor Discovery

This tests whether the AI correctly understands:
1. We want LP INVESTORS, not developers
2. Focus on institutional investors (REITs, PE firms, fund managers)
3. BTR (Build-to-Rent) + OZ (Opportunity Zone) + Sunbelt focus
4. Target roles: Investment Directors, Portfolio Managers, Fund Managers
"""

import asyncio
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Set test API keys if not already set
if not os.getenv('GOOGLE_API_KEY'):
    os.environ['GOOGLE_API_KEY'] = 'AIzaSyBBhkKvctGs4ivVaquySztFmKXa7oQ3fjg'
if not os.getenv('GOOGLE_CSE_ID'):
    os.environ['GOOGLE_CSE_ID'] = '404c0e0620566459a'

from services.real_research import extract_targeting_criteria, search_companies

# Abbreviated version of Hazen Road research guide
HAZEN_ROAD_GUIDE = """
🧠 Hazen Road Institutional Investor Discovery & Research Framework

1. Mission
You are an AI Research Analyst working on behalf of Hazen Road, a 178-unit Build-to-Rent (BTR) 
development located in Buckeye, Arizona, within an Opportunity Zone (OZ).

Your mission is:
Discover new potential institutional investors — companies that invest as Limited Partners (LPs) 
in third-party real estate developments.

NOT developers - we ARE developers ourselves. We need INVESTORS.

3. The Ideal Target Investor

A company qualifies if it meets at least three of these conditions:

✅ LP Investor: Invests capital into other developers' projects (not only their own)
✅ BTR / Multifamily Focus: Has invested in build-to-rent or multifamily communities
✅ OZ Activity: Has done Opportunity Zone projects or manages a Qualified Opportunity Fund
✅ Sunbelt Presence: Invests in Phoenix or other Sunbelt states (AZ, TX, FL, GA, NC)
✅ Institutional Scale: Manages $500M+ AUM or deploys $5-50M equity tickets

❌ What We Are NOT Looking For:
- Pure developers that only fund their own builds
- Small syndicators (<$100M AUM)
- Industrial/office-only real estate funds

EXAMPLE TARGET COMPANIES:
- Kennedy Wilson (REIT, Beverly Hills CA) - $30B AUM, multifamily + BTR + OZ
- Argosy Real Estate Partners (LP investor, Dallas TX)
- Fund managers who invest in other developers' projects

TARGET CONTACT ROLES:
- Investment Director
- Portfolio Manager  
- Fund Manager
- Investment Committee Member
- Managing Director (Investment)
- VP of Acquisitions (at investment firms, not developers)
"""

async def main():
    """Test AI extraction with Hazen Road investor guide"""
    
    logger.info("="*80)
    logger.info("🧪 TEST: Hazen Road Institutional Investor Discovery")
    logger.info("="*80)
    logger.info("")
    
    # Check API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    google_cse = os.getenv("GOOGLE_CSE_ID")
    
    logger.info("📋 API Keys:")
    logger.info(f"   OPENAI_API_KEY: {'✅ SET' if openai_key else '❌ MISSING'}")
    logger.info(f"   GOOGLE_API_KEY: {'✅ SET' if google_key else '❌ MISSING'}")
    logger.info(f"   GOOGLE_CSE_ID: {'✅ SET' if google_cse else '❌ MISSING'}")
    logger.info("")
    
    if not openai_key:
        logger.error("❌ Need OPENAI_API_KEY to test AI extraction!")
        return
    
    # Step 1: Extract targeting criteria
    logger.info("="*80)
    logger.info("STEP 1: AI Extracts Targeting Criteria")
    logger.info("="*80)
    
    prompt = "Generate leads as explained in the knowledge base"
    prompt_with_guide = f"{prompt}\n\nKNOWLEDGE BASE:\n{HAZEN_ROAD_GUIDE}"
    
    targeting_criteria = await extract_targeting_criteria(prompt_with_guide)
    
    logger.info("")
    logger.info("✅ AI Extraction Results:")
    logger.info(f"   Industry: {targeting_criteria.get('industry')}")
    logger.info(f"   Keywords: {targeting_criteria.get('keywords', [])[:5]}")
    logger.info(f"   Location: {targeting_criteria.get('location')}")
    logger.info(f"   Target Roles: {targeting_criteria.get('target_roles', [])[:3]}")
    logger.info("")
    
    logger.info("📊 Generated Search Queries:")
    for i, query in enumerate(targeting_criteria.get('search_queries', [])[:5], 1):
        logger.info(f"   {i}. {query}")
    logger.info("")
    
    # Validation
    logger.info("="*80)
    logger.info("🔍 VALIDATION: Did AI Correctly Understand the Guide?")
    logger.info("="*80)
    
    industry = targeting_criteria.get('industry', '').lower()
    keywords = [k.lower() for k in targeting_criteria.get('keywords', [])]
    search_queries = [q.lower() for q in targeting_criteria.get('search_queries', [])]
    target_roles = [r.lower() for r in targeting_criteria.get('target_roles', [])]
    
    # Check 1: Industry should be investment/fund management, NOT development
    logger.info("\n✓ CHECK 1: Industry Type")
    if any(word in industry for word in ['investment', 'investor', 'fund', 'reit', 'private equity']):
        logger.info(f"   ✅ CORRECT: Industry is '{targeting_criteria.get('industry')}'")
        logger.info("      (Investment/fund management, not development)")
    elif 'development' in industry and 'investment' not in industry:
        logger.error(f"   ❌ WRONG: Industry is '{targeting_criteria.get('industry')}'")
        logger.error("      Should be 'Investment Management', not 'Development'")
        logger.error("      We want INVESTORS, not developers!")
    else:
        logger.warning(f"   ⚠️  UNCLEAR: Industry is '{targeting_criteria.get('industry')}'")
    
    # Check 2: Keywords should focus on investors/LPs
    logger.info("\n✓ CHECK 2: Keywords Focus")
    investor_keywords = [k for k in keywords if any(term in k for term in ['investor', 'lp', 'limited partner', 'fund', 'reit', 'private equity', 'institutional'])]
    developer_keywords = [k for k in keywords if 'developer' in k or 'development' in k]
    
    if investor_keywords:
        logger.info(f"   ✅ GOOD: Found investor keywords: {investor_keywords[:3]}")
    if developer_keywords:
        logger.error(f"   ❌ BAD: Found developer keywords: {developer_keywords}")
        logger.error("      Should focus on investors, not developers")
    
    # Check 3: Search queries should target investment firms
    logger.info("\n✓ CHECK 3: Search Query Focus")
    all_queries_text = ' '.join(search_queries)
    if any(term in all_queries_text for term in ['investor', 'fund', 'reit', 'private equity', 'institutional', 'lp']):
        logger.info(f"   ✅ GOOD: Queries target investment firms")
    else:
        logger.error(f"   ❌ BAD: Queries don't mention investors/funds")
    
    if 'developer' in all_queries_text or 'development companies' in all_queries_text:
        logger.error(f"   ❌ BAD: Queries mention developers (we DON'T want developers!)")
    
    # Check 4: Target roles should be investment-focused
    logger.info("\n✓ CHECK 4: Target Roles")
    investment_roles = [r for r in target_roles if any(term in r for term in ['investment', 'portfolio', 'fund', 'acquisitions', 'managing director'])]
    developer_roles = [r for r in target_roles if 'development' in r or 'project manager' in r]
    
    if investment_roles:
        logger.info(f"   ✅ GOOD: Found investment roles: {investment_roles[:3]}")
    if developer_roles:
        logger.warning(f"   ⚠️  QUESTIONABLE: Found developer roles: {developer_roles}")
        logger.warning("      These might be okay IF at investment firms, not development companies")
    
    # Check 5: BTR, OZ, Sunbelt mentioned
    logger.info("\n✓ CHECK 5: Specific Investment Focus")
    all_text = ' '.join(keywords + search_queries).lower()
    
    if 'btr' in all_text or 'build to rent' in all_text or 'build-to-rent' in all_text:
        logger.info("   ✅ GOOD: Mentions BTR (Build-to-Rent)")
    else:
        logger.warning("   ⚠️  Missing: No BTR/build-to-rent mention")
    
    if 'opportunity zone' in all_text or 'oz fund' in all_text:
        logger.info("   ✅ GOOD: Mentions Opportunity Zones")
    else:
        logger.warning("   ⚠️  Missing: No Opportunity Zone mention")
    
    if 'sunbelt' in all_text or 'phoenix' in all_text or 'arizona' in all_text:
        logger.info("   ✅ GOOD: Mentions Sunbelt/Phoenix/Arizona")
    else:
        logger.warning("   ⚠️  Missing: No geographic focus")
    
    # Overall verdict
    logger.info("")
    logger.info("="*80)
    logger.info("📊 OVERALL VERDICT")
    logger.info("="*80)
    
    if (any(word in industry for word in ['investment', 'investor', 'fund']) and 
        investor_keywords and 
        'investor' in all_queries_text):
        logger.info("🎉 ✅ SUCCESS!")
        logger.info("   AI correctly understood: We want INVESTORS, not developers")
        logger.info("   Queries will find: REITs, PE firms, fund managers, LP investors")
    else:
        logger.error("❌ FAILURE!")
        logger.error("   AI is confused about investors vs developers")
        logger.error("   Needs prompt improvement or more explicit guidance")
    
    logger.info("")
    logger.info("="*80)

if __name__ == "__main__":
    asyncio.run(main())
