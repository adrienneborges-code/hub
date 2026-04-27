#!/usr/bin/env python3
"""
Import Salesforce Opportunity CSV into hub/assets/data.js

Usage:
  1. In Salesforce: Reports → New Report → Opportunities
  2. Add columns: Opportunity Name, Account Name, Account ID, Stage, Amount,
     Close Date, Forecast Category, Next Step, Probability (%), Type, Description
  3. Export as CSV (file → Export → Formatted Report / Details Only)
  4. Run: python3 ~/hub/scripts/import_sf.py ~/Downloads/opportunities.csv

This will update PIPELINE_DEALS in ~/hub/assets/data.js
"""

import csv, json, sys, re, os
from datetime import datetime

def parse_amount(val):
    if not val: return 0
    return int(re.sub(r'[^\d]', '', val) or 0)

def parse_date(val):
    if not val: return ''
    for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%m/%d/%y']:
        try:
            return datetime.strptime(val.strip(), fmt).strftime('%Y-%m-%d')
        except: pass
    return ''

def csv_to_deals(path):
    deals = []
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            # Normalize field names (Salesforce exports vary)
            name = row.get('Opportunity Name') or row.get('Name') or ''
            account = row.get('Account Name') or row.get('Account') or ''
            sf_id = row.get('Opportunity ID') or row.get('ID') or ''
            stage = row.get('Stage') or row.get('Opportunity Stage') or 'Discovery'
            amount = parse_amount(row.get('Amount') or row.get('ARR') or '0')
            close_date = parse_date(row.get('Close Date') or row.get('CloseDate') or '')
            fc = row.get('Forecast Category') or row.get('Forecast') or 'Pipeline'
            next_step = row.get('Next Step') or ''
            prob = int(re.sub(r'[^\d]', '', row.get('Probability (%)') or row.get('Probability') or '20') or 20)
            deal_type = row.get('Type') or 'New Business'
            notes = row.get('Description') or ''

            if not account: continue

            deals.append({
                'id': sf_id or f'sf-opp-{i+1}',
                'name': name or f'{account} - B2B',
                'account': account,
                'stage': stage,
                'amount': amount,
                'closeDate': close_date,
                'forecastCategory': fc,
                'type': deal_type,
                'nextStep': next_step,
                'probability': prob,
                'daysInStage': 0,
                'meddic': {
                    'metrics': '',
                    'economicBuyer': '',
                    'decisionCriteria': '',
                    'decisionProcess': '',
                    'identifyPain': '',
                    'champion': ''
                },
                'notes': notes[:500],
                'sfUrl': sf_id,
            })

    return deals

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    csv_path = sys.argv[1]
    if not os.path.exists(csv_path):
        print(f'Error: file not found: {csv_path}')
        sys.exit(1)

    deals = csv_to_deals(csv_path)
    print(f'Parsed {len(deals)} deals from {csv_path}')

    data_js_path = os.path.expanduser('~/hub/assets/data.js')
    with open(data_js_path) as f:
        content = f.read()

    # Replace PIPELINE_DEALS
    deals_json = json.dumps(deals, indent=2)
    new_block = f'const PIPELINE_DEALS = {deals_json};'

    # Find and replace the existing PIPELINE_DEALS block
    pattern = r'const PIPELINE_DEALS = \[[\s\S]*?\];'
    if re.search(pattern, content):
        new_content = re.sub(pattern, new_block, content)
    else:
        new_content = content + '\n' + new_block

    with open(data_js_path, 'w') as f:
        f.write(new_content)

    print(f'✅ Updated data.js with {len(deals)} deals')
    print('\nDeals imported:')
    for d in deals:
        print(f'  {d["account"]:40} {d["stage"]:15} ${d["amount"]:>8,}  {d["closeDate"]}')
