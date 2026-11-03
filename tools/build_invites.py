"""Build public/invites.js from data/invites-<cycle>.json.

Each record in the data file is one school's harvest from its SDN thread:
  {"school": "<exact library name>", "thread_url": "...", "pages_total": N, "last_post": N, "checked": "YYYY-MM-DD",
   "events": [{"type": "II|preR|A|WL|R|hold", "date": "YYYY-MM-DD", "post": N, "res": "IS|OOS|null"}],
   "exclude_posts": [N, ...], "notes": "..."}
Run with: python3 -I tools/build_invites.py
"""
import json, os, datetime

cycle = json.load(open('data/cycle.json'))['cycle']
src = f'data/invites-{cycle}.json'
lib_names = set()
t = open('public/library.js').read()
for x in json.loads(t[t.index('{'):t.rindex('}') + 1])['schools']: lib_names.add(x['name'])

out = {}; unknown = []
rows = json.load(open(src)) if os.path.exists(src) else []
for r in rows:
    if r['school'] not in lib_names: unknown.append(r['school']); continue
    skip = set(r.get('exclude_posts') or [])
    ev = [e for e in r.get('events') or [] if e.get('date') and e.get('post') not in skip]
    ii = sorted(e['date'] for e in ev if e['type'] == 'II')
    acc = sorted(e['date'] for e in ev if e['type'] == 'A')
    wl = [e for e in ev if e['type'] == 'WL']
    if not ii and not acc: continue
    rec = {'url': r['thread_url'], 'checked': r.get('checked')}
    if ii: rec.update({'first': ii[0], 'last': ii[-1], 'n': len(ii)})
    if acc: rec.update({'afirst': acc[0], 'alast': acc[-1], 'an': len(acc)})
    if wl: rec['wn'] = len(wl)
    out[r['school']] = rec
data = {'cycle': cycle, 'updated': datetime.date.today().isoformat(), 'schools': out}
js = ("// Interview-invite and acceptance timing per school, summarized from applicants' posts on each school's Student Doctor Network thread.\n"
      "// Built by tools/build_invites.py from data/invites-" + cycle + ".json; don't edit by hand.\n"
      "window.INVITE_DATA = " + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ";\n")
open('public/invites.js', 'w').write(js)
print(len(out), 'schools with invite or acceptance reports;', len(rows), 'harvested;', 'unknown names:', unknown)
