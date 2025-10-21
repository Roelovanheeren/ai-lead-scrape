#!/usr/bin/env python3
"""
Test script to show how the improved search disambiguation works
"""

def extract_context_keywords(prompt):
    """Simulate the improved context extraction logic"""
    context_keywords = []
    exclusion_keywords = []
    
    prompt_lower = prompt.lower()
    
    # Investment/finance related keywords (HIGH PRIORITY for disambiguation)
    if any(word in prompt_lower for word in ['investment', 'investor', 'investing', 'capital', 'fund', 'private equity', 'reit', 'portfolio', 'lp', 'limited partner']):
        context_keywords.append('investment management')
        context_keywords.append('institutional investor')
        # Exclude data centers and news sites
        exclusion_keywords.extend(['-data center', '-datacenter', '-news', '-media'])
    
    # Real estate keywords
    if any(word in prompt_lower for word in ['real estate', 'property', 'realty', 'multifamily', 'residential', 'commercial', 'btr', 'build to rent']):
        context_keywords.append('real estate')
        # If combined with investment, be even more specific
        if any(word in prompt_lower for word in ['investment', 'investor', 'fund']):
            context_keywords.append('REIT')
            exclusion_keywords.extend(['-construction', '-developer', '-builder'])
    
    # Development keywords (but not if it's clearly an investor request)
    if 'development' in prompt_lower and not any(word in prompt_lower for word in ['investor', 'investing', 'lp', 'limited partner', 'fund']):
        context_keywords.append('development')
    
    # Technology keywords
    if any(word in prompt_lower for word in ['tech', 'technology', 'software', 'saas', 'ai', 'startup']):
        context_keywords.append('technology')
    
    return context_keywords, exclusion_keywords


def build_search_query(company_name, context_keywords, exclusion_keywords):
    """Build the enhanced search query"""
    if context_keywords:
        context_str = ' '.join(context_keywords)
        exclusion_str = ' '.join(exclusion_keywords) if exclusion_keywords else ''
        return f'{context_str} "{company_name}" official website {exclusion_str}'
    else:
        return f'"{company_name}" official website'


# Test cases
test_cases = [
    {
        "prompt": "Find leads at CenterSquare real estate investment",
        "company": "CenterSquare",
        "expected": "Should find CenterSquare Investment Management (centersquare.com)"
    },
    {
        "prompt": "Get contacts from Center Square Investment Management",
        "company": "Center Square Investment Management",
        "expected": "Should find investment firm, not data center"
    },
    {
        "prompt": "Find leads at Blackstone real estate",
        "company": "Blackstone",
        "expected": "Should find Blackstone Group (investment firm)"
    },
    {
        "prompt": "Find leads at Amazon",
        "company": "Amazon",
        "expected": "Should use basic search (no specific industry)"
    },
    {
        "prompt": "Find leads at Greystar real estate development",
        "company": "Greystar",
        "expected": "Should find Greystar (development company)"
    }
]

print("=" * 80)
print("IMPROVED GOOGLE SEARCH DISAMBIGUATION TEST")
print("=" * 80)

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*80}")
    print(f"TEST {i}")
    print(f"{'='*80}")
    print(f"📝 User Prompt: {test['prompt']}")
    print(f"🏢 Company Name: {test['company']}")
    print(f"🎯 Expected: {test['expected']}")
    print()
    
    # Extract context
    context, exclusions = extract_context_keywords(test['prompt'])
    print(f"✅ Context Keywords: {context}")
    print(f"🚫 Exclusion Keywords: {exclusions}")
    print()
    
    # Build query
    query = build_search_query(test['company'], context, exclusions)
    print(f"🔎 OLD QUERY: \"{test['company']}\" official website")
    print(f"🔎 NEW QUERY: {query}")
    print()
    
    # Explain improvements
    if context:
        print("💡 IMPROVEMENTS:")
        if 'investment management' in context:
            print("   ✓ Added 'investment management' + 'institutional investor' for finance context")
        if 'real estate' in context:
            print("   ✓ Added 'real estate' for industry context")
        if 'REIT' in context:
            print("   ✓ Added 'REIT' for real estate investment specificity")
        if exclusions:
            print(f"   ✓ Excluding wrong industries: {', '.join(exclusions)}")
    else:
        print("💡 Using basic search (no specific industry context detected)")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
The improved search adds:
1. Industry context keywords BEFORE company name (better Google ranking)
2. Exclusion terms to filter out wrong companies (-datacenter, -news, etc.)
3. Smart combinations (real estate + investment → add REIT)
4. More specific investor keywords (LP, institutional, portfolio)

This should fix the issue where CenterSquare data center was found instead of
CenterSquare Investment Management!
""")
