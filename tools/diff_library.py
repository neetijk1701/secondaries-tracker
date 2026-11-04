"""Summarize what changed between two builds of library.js, as Markdown.

python3 -I tools/diff_library.py OLD_library.js NEW_library.js
(e.g. git show origin/main:public/library.js > /tmp/old.js first)
"""
import json, re, sys

def load(path):
    t = open(path).read()
    return json.loads(t[t.index('{'):t.rindex('}') + 1])
norm = lambda t: re.sub(r'\W+', ' ', t.lower()).strip()

a, b = load(sys.argv[1]), load(sys.argv[2])
A = {x['name']: x for x in a['schools']}
B = {x['name']: x for x in b['schools']}
cyc = b['cycle']
def own(x): return [] if (x.get('pc') or not x) else x['prompts']   # prompts that belong to this build's cycle
def dual(x): m = x.get('mdphd'); return [] if not m or m.get('cycle') else m['prompts']

posted, changed, removed, dual_new, dual_changed = [], [], [], [], []
for name, x in sorted(B.items()):
    o = A.get(name) or {'prompts': []}
    op, np_ = {norm(p['p']): p for p in (o['prompts'] if o.get('pc') is None and a['cycle'] == cyc else [])}, {norm(p['p']): p for p in own(x)}
    if np_ and not op: posted.append((name, len(np_)))
    elif op or np_:
        add = [np_[k] for k in np_ if k not in op]; gone = [op[k] for k in op if k not in np_]
        lim = [(op[k], np_[k]) for k in np_ if k in op and (op[k]['limit'], op[k]['unit']) != (np_[k]['limit'], np_[k]['unit'])]
        if add or gone or lim: changed.append((name, add, gone, lim))
    od = {norm(p['p']) for p in (dual(o) if a['cycle'] == cyc else [])}; nd = {norm(p['p']) for p in dual(x)}
    if nd and not od: dual_new.append((name, len(nd)))
    elif nd != od and (nd or od): dual_changed.append((name, len(nd - od), len(od - nd)))
for name in sorted(set(A) - set(B)): removed.append(name)

print(f"## Library changes ({a['cycle']} {a.get('updated','')} -> {cyc} {b['updated']})\n")
print(f"Schools with {cyc} prompts: {a.get('fresh','?') if a['cycle']==cyc else 0} -> {b.get('fresh','?')} of {len(B)}\n")
if posted:
    print(f"### Newly posted ({len(posted)})"); [print(f"- {n}: {k} prompt{'s' if k != 1 else ''}") for n, k in posted]; print()
if changed:
    print(f"### Changed ({len(changed)})")
    for n, add, gone, lim in changed:
        print(f"- **{n}**")
        for p in add: print(f"  - added: {p['p'][:160]}")
        for p in gone: print(f"  - removed: {p['p'][:160]}")
        for o, p in lim: print(f"  - limit {o['limit']} {o['unit']} -> {p['limit']} {p['unit']}: {p['p'][:80]}")
    print()
if dual_new or dual_changed:
    print("### MD/PhD")
    for n, k in dual_new: print(f"- {n}: {k} new")
    for n, ad, gn in dual_changed: print(f"- {n}: +{ad} / -{gn}")
    print()
if removed: print("### Schools no longer in the library\n" + "\n".join('- ' + n for n in removed) + "\n")
if not (posted or changed or dual_new or dual_changed or removed): print("No prompt changes.")
