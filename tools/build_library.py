import json,re
md=json.load(open('data/md-prompts-2026-2027.json'))
do=json.load(open('data/do-prompts-2026-2027.json'))
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
out.sort(key=lambda x:x['name'].lower())
data={'cycle':'2026-2027','updated':'2026-11-01','source':'Student Doctor Network school threads','schools':out}
js="// Secondary prompts for the 2026-2027 cycle, collected from each school's Student Doctor Network thread (MD Oct 31, DO Nov 1, 2026).\n// Regenerate from the catalogue; keep school names stable (added schools are matched by name).\nwindow.PROMPT_LIBRARY = "+json.dumps(data,ensure_ascii=False,separators=(',',':'))+";\n"
open('public/library.js','w').write(js)
print(len(out), sum(1 for x in out if x['deg']=='DO'), 'osteo prompts', osteo, 'size', len(js))
