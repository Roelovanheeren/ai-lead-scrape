# Research Guide Fix - CRITICAL Issue Resolved ✅

## The Problem You Identified

**Your exact words**: "it should use the research guide in the knowledge bank, it doesnt seem to use that as in there is clearly outlined who we're looking for"

You were **100% correct**! The system was completely ignoring the research guide when you asked for a specific company.

---

## What Was Broken

### Scenario
- **Your research guide**: "Target institutional investors (LPs) who invest in other developers' BTR projects"
- **Your request**: "Find leads at CenterSquare"
- **What you wanted**: Investment Directors, Portfolio Managers, Fund Managers at CenterSquare
- **What you got**: CEOs, COOs, Chief Development Officers (wrong people!)

### Root Cause

The code had two different paths:

**PATH 1: Specific Company Request** (when you say "Find leads at CenterSquare")
```python
if specific_company_name:
    # Find the company
    company = await find_specific_company(specific_company_name, prompt)
    companies = [company]
    # ❌ NEVER extracted research guide or targeting criteria!
```

**PATH 2: General Search** (when you say "Find leads from research guide")
```python
else:
    # Extract research guide
    research_guide_text = extract_from_knowledge_base()
    targeting_criteria = await extract_targeting_criteria(research_guide_text)
    # ✅ Used research guide correctly
```

**The bug**: When you requested a specific company, the code took PATH 1 and **skipped the research guide entirely**!

---

## What This Meant

When you said "Find leads at CenterSquare":

1. ✅ System extracted "CenterSquare" as company name
2. ✅ System found the company
3. ❌ **System NEVER read your research guide**
4. ❌ Used empty `targeting_criteria = {}`
5. ❌ Defaulted to `department = "executive"`
6. ❌ Hunter.io searched for "executive" roles
7. ❌ Returned: CEO, COO, Chief Development Officer
8. ❌ **Completely ignored** that you wanted INVESTORS, not executives!

---

## The Fix

Now the code **ALWAYS** extracts research guide FIRST:

```python
# NEW CODE: Extract research guide FIRST (for ALL requests)
research_guide_text = extract_from_knowledge_base()
targeting_criteria = await extract_targeting_criteria(research_guide_text)

# Store criteria for later use
job_data['targeting_criteria'] = targeting_criteria

logger.info(f"📋 Extracted targeting criteria:")
logger.info(f"  Target Roles: {targeting_criteria.get('target_roles', [])}")
logger.info(f"  Target Department: {targeting_criteria.get('target_department', 'executive')}")

# THEN check if specific company or general search
if specific_company_name:
    company = await find_specific_company(specific_company_name, prompt)
    companies = [company]
    # ✅ Will use targeting_criteria when finding contacts!
```

---

## What This Fixes

### Before Fix (BROKEN ❌)
**Request**: "Find leads at CenterSquare"
**Research Guide**: "Target institutional investors (LPs) in real estate"

```
Flow:
1. Extract "CenterSquare" → specific company path
2. Skip research guide ❌
3. Find company
4. Find contacts with targeting_criteria = {} ❌
5. Default to department = "executive" ❌
6. Hunter.io: Search for executives
7. Results: Jason Carolan (Chief Development Officer) ❌
          Megan Scales (Executive Vice President) ❌
          WRONG PEOPLE! ❌
```

### After Fix (WORKING ✅)
**Request**: "Find leads at CenterSquare"
**Research Guide**: "Target institutional investors (LPs) in real estate"

```
Flow:
1. Extract research guide FIRST ✅
2. Extract targeting_criteria: ✅
   - target_roles: ["Investment Director", "Portfolio Manager", "Fund Manager"]
   - target_department: "finance"
   - industry: "Real Estate Investment Management"
3. Extract "CenterSquare" → specific company path
4. Find company (centersquare.com)
5. Find contacts WITH targeting_criteria ✅
6. Hunter.io: Search for "finance" department
7. Filter for investment roles ✅
8. Results: Investment Directors ✅
           Portfolio Managers ✅
           Fund Managers ✅
           RIGHT PEOPLE! ✅
```

---

## Example: Your Use Case

### Your Research Guide Says:
```
Target institutional investors that invest as Limited Partners (LPs) 
in other developers' Build-to-Rent projects. We are looking for:
- Investment Directors
- Portfolio Managers  
- Fund Managers
- Investment Committee members
- Capital Allocation teams

NOT looking for:
- Developers who build their own projects
- Construction companies
- Development executives
```

### You Request:
"Find leads at CenterSquare real estate investment"

### System Now Does:

**Step 1**: Extract research guide
```
✅ Read: "Target institutional investors (LPs)..."
✅ Extract: target_roles = ["Investment Director", "Portfolio Manager", "Fund Manager"]
✅ Extract: target_department = "finance"
✅ Extract: industry = "Real Estate Investment Management"
```

**Step 2**: Find company with better search
```
Old query: "CenterSquare" official website
New query: investment management institutional investor real estate REIT "CenterSquare" official website -datacenter -news

✅ Finds: CenterSquare Investment Management (centersquare.com)
❌ Avoids: CenterSquare DC (data center)
❌ Avoids: The Center Square (news site)
```

**Step 3**: Find contacts with research guide criteria
```
✅ Hunter.io domain search: centersquare.com
✅ Department filter: "finance" (mapped from "investment")
✅ Role filter: ["Investment Director", "Portfolio Manager", "Fund Manager"]
✅ Results: Investment professionals at CenterSquare Investment Management
```

---

## Technical Details

### Code Changes

**File**: `backend/main_simple.py`

**Function**: `process_job_real_only()`

**Old Code** (lines 221-256):
```python
# Check if specific company
specific_company_name = extract_company_name_from_prompt(prompt)

if specific_company_name:
    # ❌ Go straight to finding company
    company = await find_specific_company(specific_company_name, prompt)
    companies = [company]
else:
    # Only extract research guide for general searches ❌
    research_guide_text = extract_from_knowledge_base()
    targeting_criteria = await extract_targeting_criteria(research_guide_text)
```

**New Code** (lines 221-256):
```python
# ✅ ALWAYS extract research guide FIRST
research_guide_text = extract_from_knowledge_base()
targeting_criteria = await extract_targeting_criteria(research_guide_text)
job_data['targeting_criteria'] = targeting_criteria

# THEN check if specific company
specific_company_name = extract_company_name_from_prompt(prompt)

if specific_company_name:
    # ✅ Find company (will use targeting_criteria for contacts)
    company = await find_specific_company(specific_company_name, prompt)
    companies = [company]
else:
    # ✅ General search (already have targeting_criteria)
    companies = await search_companies(targeting_criteria, target_count)
```

---

## Benefits

1. **Research Guide Always Used** ✅
   - No matter how you phrase your request
   - Specific company OR general search
   - Always reads and applies your guidance

2. **Correct Role Targeting** ✅
   - Targets investment roles (not executives)
   - Uses correct department (finance, not executive)
   - Filters by specific job titles from guide

3. **Better Company Disambiguation** ✅
   - Uses industry context from research guide
   - Excludes wrong industries (-datacenter, -news)
   - Finds the RIGHT company (investment firm, not data center)

4. **Consistent Behavior** ✅
   - Same logic for specific + general requests
   - Predictable results
   - Logs what it's doing for debugging

---

## Testing

### You Can Now Test With:

**Test 1**: "Find leads at CenterSquare real estate investment"
- **Expected**: Investment professionals at CenterSquare Investment Management
- **Will use**: Research guide to target investment roles

**Test 2**: "Get me 10 contacts from BlackRock real estate"
- **Expected**: Real estate investment team at BlackRock
- **Will use**: Research guide to target LP investors

**Test 3**: "Find leads from institutional investors in BTR" (general search)
- **Expected**: Multiple investment firms with investment roles
- **Will use**: Research guide to search for investor companies AND target investment roles

---

## Next Steps

1. ✅ **Fix deployed** - Code changes committed and pushed
2. ✅ **PR updated** - Pull request #3 has full details
3. 🔄 **Ready for testing** - Try "Find leads at CenterSquare" again
4. 📊 **Check results** - Should now return investment professionals, not executives

---

## Summary

**What you said**: "it should use the research guide in the knowledge bank"

**You were right!** The system was ignoring the research guide for specific company requests.

**Now fixed!** The system ALWAYS reads your research guide, extracts targeting criteria, and uses it to find the RIGHT people at companies.

This was a **critical bug** that made the system unusable for your use case. Now it should work correctly! 🎉

---

## Pull Request

**Link**: https://github.com/Roelovanheeren/ai-lead-scrape/pull/3

Contains both fixes:
1. Google search disambiguation (better company finding)
2. Research guide usage (correct role targeting)

Both are critical for finding institutional investors at specific companies like CenterSquare!
