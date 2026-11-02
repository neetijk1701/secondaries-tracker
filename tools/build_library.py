"""Build public/library.js from the prompt data in data/.

The cycle being built is set in data/cycle.json: {"cycle": "2027-2028", "prev": "2026-2027"}.
Data files are data/md-prompts-<cycle>.json, data/do-prompts-<cycle>.json and
data/mdphd-prompts-<cycle>.json (optional).

When "prev" is set, any school with nothing posted yet for the new cycle falls back to last
cycle's prompts. Those schools carry "pc": "<prev cycle>" so the app can label them, and the
same goes for MD/PhD prompts (mdphd.cycle). Run with: python3 -I tools/build_library.py
"""
import json, re, os, datetime

MDPHD_MAP = {'mdphd_why':'mdphd','research':'research','research_interest':'resint','why_school':'why','challenge':'challenge','diversity':'diversity','team':'team','career':'career','service':'service','anything_else':'anything','other':'other'}
MAP = {'diversity':'diversity','challenge':'challenge','why_school':'why','gap':'gap','team':'team','anything_else':'anything','career':'career','service':'service','ethics':'ethics','other':'other'}
OSTEO = re.compile(r'osteopath|observ\w* a DO|shadow\w*.{0,40}\bDO\b', re.I)
norm = lambda t: re.sub(r'\W+',' ',(t or '').lower()).strip()[:120]
def sname(s): return re.sub(r'\s*\([A-Z]{2}\)\s*$','',s).strip()
def skey(name): return re.sub(r'\W+',' ',sname(name).lower()).strip()

def fam(p, deg):
    f = MAP.get(p.get('type'),'other')
    if deg=='DO' and f=='other' and OSTEO.search(p['text']) and not re.search(r'hobbies',p['text'],re.I): return 'osteo'
    return f

def prompt(p, f, cap=False):
    u = (p.get('unit') or '')
    t = p['text'].strip()
    if cap: t = t[:1].upper()+t[1:]
    d = {'p':t,'limit':p.get('limit') or 0,'unit':'chars' if u.startswith('char') else 'words','fam':f}
    if p.get('required') is False: d['opt']=1
    if p.get('group'): d['group']=p['group']
    if p.get('abridged'): d['cut']=1
    return d

def build(cycle, quiet=False):
    files = {deg:f'data/{deg.lower()}-prompts-{cycle}.json' for deg in ('MD','DO')}
    if not os.path.exists(files['MD']): return None
    out=[]; osteo=0
    for deg in ('MD','DO'):
        if not os.path.exists(files[deg]): continue
        for s in json.load(open(files[deg])):
            ps=[prompt(p, fam(p,deg)) for p in s.get('prompts') or []]
            osteo += sum(1 for d in ps if d['fam']=='osteo')
            e={'name':sname(s['school']),'state':s['state'],'deg':deg,'url':s.get('source_url') or s.get('school_thread_url') or '','prompts':ps}
            if not ps: e['none']='No written essays reported' if s.get('no_written_secondary_note') else 'No prompts posted yet'
            out.append(e)
    mp=f'data/mdphd-prompts-{cycle}.json'
    if os.path.exists(mp):
        byurl={x['url'].rstrip('/'):x for x in out if x['url']}
        byname={skey(x['name']):x for x in out}
        unmatched=[]; n=0; moved=[]
        for s in json.load(open(mp)):
            x=byurl.get((s.get('school_thread_url') or '').rstrip('/')) or byname.get(skey(s['school']))
            if not x: unmatched.append(s['school']); continue
            ps=[prompt(p, MDPHD_MAP.get(p.get('type'),'other'), cap=True) for p in s.get('prompts') or []]
            # drop dual-degree-only prompts that slipped into the regular list for this school
            dualtexts={norm(d['p']) for d in ps}
            before=len(x['prompts'])
            x['prompts']=[q for q in x['prompts'] if not (norm(q['p']) in dualtexts and (re.search(r'MSTP|MD/PhD|M\.D\.-Ph\.D|physician[- ]scientist',q['p'],re.I) or q['fam'] in ('research','resint','mdphd') or re.search(r'research',q['p'],re.I)))]
            if before!=len(x['prompts']): moved.append((x['name'], before-len(x['prompts'])))
            # a dual prompt that is a reworded version of a regular one (same opening) replaces it for dual applicants
            if s.get('md_secondary')!='instead':
                for d in ps:
                    for i,q in enumerate(x['prompts']):
                        if norm(q['p'])[:60]==norm(d['p'])[:60] and norm(q['p'])!=norm(d['p']): d['rep']=i
            if ps:
                x['mdphd']={'prog':s.get('program') or ('DO/PhD' if x['deg']=='DO' else 'MD/PhD'),'md':s.get('md_secondary') or 'unknown','prompts':ps,'src':s.get('source_url') or ''}
                if s.get('cycle') and s['cycle']!=cycle: x['mdphd']['cycle']=s['cycle']
                if s.get('source_type') in ('school_website','compilation'): x['mdphd']['srcType']=s['source_type']
                n+=len(ps)
        if not quiet: print(cycle,'mdphd prompts merged', n, 'unmatched schools', unmatched, 'moved out of regular lists', moved)
    if not quiet: print(cycle, len(out), 'schools,', sum(1 for x in out if x['deg']=='DO'), 'DO, osteo prompts', osteo)
    return out

cfg=json.load(open('data/cycle.json'))
cycle=cfg['cycle']; prev=cfg.get('prev')
out=build(cycle)
fresh=sum(1 for x in out if x['prompts'])
if prev:
    old={skey(x['name']):x for x in (build(prev, quiet=True) or [])}
    have={skey(x['name']) for x in out}
    fb=fbd=0
    for x in out:
        o=old.get(skey(x['name']))
        if not o: continue
        if not x['prompts'] and o['prompts']:
            x['prompts']=o['prompts']; x['pc']=prev; x.pop('none',None); fb+=1
        if not x.get('mdphd') and o.get('mdphd'):
            m=dict(o['mdphd']); m['cycle']=m.get('cycle') or prev
            # replacement indices only make sense against the same cycle's regular prompts
            if x.get('pc')!=prev: m['prompts']=[{k:v for k,v in p.items() if k!='rep'} for p in m['prompts']]
            x['mdphd']=m; fbd+=1
    for k,o in old.items():
        if k not in have:
            o=dict(o); o['pc']=prev
            if o.get('mdphd'): o['mdphd']=dict(o['mdphd'], cycle=o['mdphd'].get('cycle') or prev)
            out.append(o)
    print('fallback to', prev, 'prompts:', fb, 'schools,', fbd, 'MD/PhD lists')
out.sort(key=lambda x:x['name'].lower())
data={'cycle':cycle,'updated':datetime.date.today().isoformat(),'fresh':fresh,'source':'Student Doctor Network school threads','schools':out}
if prev: data['prev']=prev
js=("// Secondary prompts for the "+cycle+" cycle, collected from each school's Student Doctor Network thread."
    +(" Schools with nothing posted yet show last cycle's ("+prev+") prompts, marked pc." if prev else "")
    +"\n// Built by tools/build_library.py; don't edit by hand. Keep school names stable across cycles (matched by name).\nwindow.PROMPT_LIBRARY = "
    +json.dumps(data,ensure_ascii=False,separators=(',',':'))+";\n")
open('public/library.js','w').write(js)
print(len(out),'schools in library,', fresh, 'with', cycle, 'prompts; size', len(js))
