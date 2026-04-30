#!/usr/bin/env python3
"""
Generate ~/hub/assets/prospecting_data.js from sales-command-center accounts.json.

Filters to accounts with a rating (Hot/Warm/Cold) — the prospecting universe.
Strips fields the static tracker doesn't need to keep payload small.

Re-run after refreshing POVs in accounts.json:
  python3 ~/hub/scripts/generate_prospecting_data.py
"""

import json, os, sys
from datetime import datetime

ACCOUNTS_PATH = os.path.expanduser('~/sales-command-center/data/accounts.json')
OUT_PATH = os.path.expanduser('~/hub/assets/prospecting_data.js')

KEEP_FIELDS = [
    'id', 'name', 'website', 'domain', 'rating', 'tier',
    'industry', 'billing_state', 'salesforce_id',
    'b2b_use_case', 'notes', 'tags', 'current_platform',
    'last_activity_date', 'researched',
    'priority_score', 'size_label', 'est_revenue_usd', 'est_employees',
]


def main():
    accounts = json.load(open(ACCOUNTS_PATH))
    rated = [a for a in accounts if a.get('rating')]
    # Pre-sort: rating bucket, then priority_score DESC, then name. Browser also sorts but
    # this saves the user a wait on first paint of 2,500 cards.
    rated.sort(key=lambda a: (
        {'Hot': 0, 'Warm': 1, 'Cold': 2}.get(a.get('rating', ''), 9),
        -(a.get('priority_score') or 0),
        (a.get('name') or '').lower(),
    ))

    slim = []
    for a in rated:
        slim.append({k: a.get(k, '') for k in KEEP_FIELDS})

    # Counts for stamping into header
    by_rating = {'Hot': 0, 'Warm': 0, 'Cold': 0}
    by_pov = 0
    for a in slim:
        by_rating[a['rating']] = by_rating.get(a['rating'], 0) + 1
        if a.get('b2b_use_case'):
            by_pov += 1

    header = (
        '// Auto-generated from ~/sales-command-center/data/accounts.json\n'
        f'// Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
        f'// Total: {len(slim)} rated accounts — '
        f'{by_rating["Hot"]} Hot · {by_rating["Warm"]} Warm · {by_rating["Cold"]} Cold · '
        f'{by_pov} with POV\n'
        '// To refresh: python3 ~/hub/scripts/generate_prospecting_data.py\n\n'
    )

    payload = json.dumps(slim, ensure_ascii=False)
    body = f'const PROSPECTING_ACCOUNTS = {payload};\n'

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(header + body)

    size_kb = os.path.getsize(OUT_PATH) / 1024
    print(f'Wrote {OUT_PATH} — {len(slim)} accounts, {size_kb:.1f} KB')
    print(f'  Hot: {by_rating["Hot"]}  Warm: {by_rating["Warm"]}  Cold: {by_rating["Cold"]}  POV: {by_pov}')


if __name__ == '__main__':
    main()
