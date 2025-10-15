# Outputs Directory

This directory contains generated lead data files. All output files are excluded from version control to protect client information.

## Expected Files

- `leads_<vertical>.csv` - Raw leads for each vertical
- `leads_<vertical>_A.csv` - Priority A leads only
- `<vertical>_scored.csv` - Leads with scoring data
- `MASTER_LEADS_CRM_READY.csv` - All leads formatted for CRM import

## File Format

CSV files contain columns like:
- company, facility_name, city, state, zip
- confidence, score, priority
- notes, source_urls
- contact information fields (when available)
