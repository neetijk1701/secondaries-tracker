"""Start a new application cycle: python3 -I tools/new_cycle.py 2027-2028

Creates empty data files for the new cycle with the same school list as the current one
(names kept identical so the build can match schools across cycles), then points
data/cycle.json at the new cycle with the old one as "prev". Until a school's new prompts
are harvested, the app shows last cycle's prompts for it, labeled as such.
"""
import json, os, re, sys

new = sys.argv[1] if len(sys.argv) > 1 else ''
if not re.fullmatch(r'\d{4}-\d{4}', new) or int(new[5:]) != int(new[:4]) + 1:
    sys.exit('usage: new_cycle.py YYYY-YYYY (e.g. 2027-2028)')
cfg = json.load(open('data/cycle.json'))
old = cfg['cycle']
if old == new: sys.exit(f'already on {new}')
# MD/PhD rows are named a little differently; give them the regular school's name (matched by thread URL)
names = {}
for kind in ('md', 'do'):
    p = f'data/{kind}-prompts-{old}.json'
    if os.path.exists(p):
        for s in json.load(open(p)):
            for u in (s.get('school_thread_url'), s.get('source_url')):
                if u: names[re.sub(r'/page-\d+/?$', '', u).rstrip('/')] = s['school']
for kind in ('md', 'do', 'mdphd'):
    src, dst = f'data/{kind}-prompts-{old}.json', f'data/{kind}-prompts-{new}.json'
    if not os.path.exists(src): continue
    if os.path.exists(dst): sys.exit(f'{dst} already exists; not overwriting')
    rows = []
    for s in json.load(open(src)):
        r = {'school': s['school'], 'state': s['state'], 'school_thread_url': None, 'source_url': None,
             'prev_thread_url': s.get('school_thread_url') or s.get('source_url'), 'prompts': []}
        if kind == 'mdphd':
            r['school'] = names.get(re.sub(r'/page-\d+/?$', '', s.get('school_thread_url') or '').rstrip('/'), s['school'])
            r.update({'program': s.get('program') or 'MD/PhD', 'md_secondary': s.get('md_secondary') or 'unknown',
                      'cycle': None, 'source_type': None, 'source_note': ''})
        rows.append(r)
    json.dump(rows, open(dst, 'w'), ensure_ascii=False, indent=1)
    print('created', dst, len(rows), 'schools')
json.dump({'cycle': new, 'prev': old}, open('data/cycle.json', 'w'))
print(f'data/cycle.json -> cycle {new}, prev {old}. Now run tools/build_library.py')
