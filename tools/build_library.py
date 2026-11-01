import json,re
md=json.load(open('data/md-prompts-2026-2027.json'))
do=json.load(open('data/do-prompts-2026-2027.json'))
MDPHD_MAP={'mdphd_why':'mdphd','research':'research','research_interest':'resint','why_school':'why','challenge':'challenge','diversity':'diversity','team':'team','career':'career','service':'service','anything_else':'anything','other':'other'}
MAP={'diversity':'diversity','challenge':'challenge','why_school':'why','gap':'gap','team':'team','anything_else':'anything','career':'career','service':'service','ethics':'ethics','other':'other'}
OSTEO=re.compile(r'osteopath|observ\w* a DO|shadow\w*.{0,40}\bDO\b',re.I)
def fam(p,deg):
    f=MAP.get(p.get('type'),'other')
    if deg=='DO' and f=='other' and OSTEO.search(p['text']) and not re.search(r'hobbies',p['text'],re.I): return 'osteo'
    return f
out=[]; osteo=0
for deg,rows in (('MD',md),('DO',do)):
    for s in rows:
        ps=[]
        for p in s.get('prompts') or []:
            u=(p.get('unit') or '')
            d={'p':p['text'].strip(),'limit':p.get('limit') or 0,'unit':'chars' if u.startswith('char') else 'words','fam':fam(p,deg)}
            if d['fam']=='osteo': osteo+=1
            if p.get('required') is False: d['opt']=1
            if p.get('group'): d['group']=p['group']
            if p.get('abridged'): d['cut']=1
            ps.append(d)
        name=re.sub(r'\s*\([A-Z]{2}\)\s*$','',s['school']).strip()
        e={'name':name,'state':s['state'],'deg':deg,'url':s['source_url'],'prompts':ps}
        if not ps: e['none']='No written essays reported' if s.get('no_written_secondary_note') else 'No prompts posted yet'
        out.append(e)
# MD/PhD and DO/PhD extras, matched to schools by their SDN thread URL
import os
mp='data/mdphd-prompts-2026-2027.json'
if os.path.exists(mp):
    byurl={x['url'].rstrip('/'):x for x in out}
    unmatched=[]; n=0; moved=[]
    for s in json.load(open(mp)):
        x=byurl.get((s.get('school_thread_url') or '').rstrip('/'))
        if not x: unmatched.append(s['school']); continue
        ps=[]
        for p in s.get('prompts') or []:
            u=(p.get('unit') or '')
            t=p['text'].strip(); t=t[:1].upper()+t[1:]
            d={'p':t,'limit':p.get('limit') or 0,'unit':'chars' if u.startswith('char') else 'words','fam':MDPHD_MAP.get(p.get('type'),'other')}
            if p.get('required') is False: d['opt']=1
            if p.get('group'): d['group']=p['group']
            if p.get('abridged'): d['cut']=1
            ps.append(d)
        # drop dual-degree-only prompts that slipped into the regular list for this school
        norm=lambda t: re.sub(r'\W+',' ',t.lower()).strip()[:120]
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
            if s.get('cycle') and s['cycle']!='2026-2027': x['mdphd']['cycle']=s['cycle']
            if s.get('source_type') in ('school_website','compilation'): x['mdphd']['srcType']=s['source_type']
            n+=len(ps)
    print('mdphd prompts merged', n, 'unmatched schools', unmatched, 'moved out of regular lists', moved)
out.sort(key=lambda x:x['name'].lower())
data={'cycle':'2026-2027','updated':'2026-11-01','source':'Student Doctor Network school threads','schools':out}
js="// Secondary prompts for the 2026-2027 cycle, collected from each school's Student Doctor Network thread (MD Oct 31, DO Nov 1, 2026).\n// Regenerate from the catalogue; keep school names stable (added schools are matched by name).\nwindow.PROMPT_LIBRARY = "+json.dumps(data,ensure_ascii=False,separators=(',',':'))+";\n"
open('public/library.js','w').write(js)
print(len(out), sum(1 for x in out if x['deg']=='DO'), 'osteo prompts', osteo, 'size', len(js))
