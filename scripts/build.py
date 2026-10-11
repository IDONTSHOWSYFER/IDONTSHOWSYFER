import json, os, urllib.request, math, html, datetime, collections, pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]; AS=ROOT/'assets'; AS.mkdir(exist_ok=True)
USER='IDONTSHOWSYFER'; HEAD={'Accept':'application/vnd.github+json','User-Agent':'syfer-profile-builder'}
def get(url):
 req=urllib.request.Request(url,headers=HEAD)
 token=os.getenv('GH_TOKEN') or os.getenv('GITHUB_TOKEN')
 if token:req.add_header('Authorization','Bearer '+token)
 with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
user=get(f'https://api.github.com/users/{USER}')
repos=[];page=1
while True:
 batch=get(f'https://api.github.com/users/{USER}/repos?per_page=100&page={page}&type=owner&sort=updated')
 if not batch:break
 repos.extend(r for r in batch if not r.get('fork') and not r.get('private'))
 if len(batch)<100:break
 page+=1
repos.sort(key=lambda r:r.get('stargazers_count',0),reverse=True)
stars=sum(r.get('stargazers_count',0) for r in repos)
lang=collections.Counter(r.get('language') or 'Other' for r in repos)
def esc(s):return html.escape(str(s),quote=True)
def svg(name,content,dark=False,height=310):
 bg='#0d1117' if dark else '#ffffff';fg='#e6edf3' if dark else '#24292f';muted='#8b949e' if dark else '#57606a';grid='#30363d' if dark else '#d0d7de'
 doc=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 {height}" role="img"><title>{esc(name)}</title><rect width="900" height="{height}" rx="18" fill="{bg}"/><style>text{{font-family:system-ui,-apple-system,Segoe UI,sans-serif;fill:{fg}}}.muted{{fill:{muted}}}.grid{{stroke:{grid}}}</style>{content}</svg>'''
 (AS/f'{name}-{"dark" if dark else "light"}.svg').write_text(doc,encoding='utf-8')
def txt(x,y,s,size=16,weight=400,cl=''):
 return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" class="{cl}">{esc(s)}</text>'
def chart(name,fn,height=310):
 for dark in (False,True):svg(name,fn(dark),dark,height)
chart('stats',lambda d:txt(40,55,'SYFER / GITHUB',24,700)+''.join(txt(40+i*290,148,v,54,750)+txt(40+i*290,185,k,17,400,'muted') for i,(v,k) in enumerate([(len(repos),'public source repos'),(stars,'repository stars'),(user.get('followers',0),'followers')])) ,235)
# Planet-inspired orbital chart, entirely native SVG; static image (GitHub strips JS)
def planet(d):
 s=txt(40,52,'Repository universe',25,700)+txt(40,82,'One orbiting point per public source repository',14,400,'muted')
 s+='<circle cx="450" cy="207" r="98" fill="none" stroke="#6e40c9" stroke-width="2"/><ellipse cx="450" cy="207" rx="280" ry="85" fill="none" stroke="#6e40c9" opacity=".5" transform="rotate(-18 450 207)"/>'
 for i,r in enumerate(repos):
  a=i*2.399963; radius=75+min(190,20*math.sqrt(i+1));x=450+radius*math.cos(a);y=207+radius*.38*math.sin(a)
  s+=f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{min(11,3+math.log1p(r.get("stargazers_count",0))*2):.1f}" fill="{["#a371f7","#2f81f7","#3fb950","#d29922"][i%4]}" opacity=".88"/>'
 return s
chart('planet',planet,420)
def top(d):
 s=txt(40,44,'Top starred repositories',23,700)
 for i,r in enumerate(repos[:8]):
  y=72+i*32;v=r.get('stargazers_count',0);w=590*(math.log1p(v)/max(1,math.log1p(repos[0].get('stargazers_count',0))))
  s+=txt(40,y+16,r['name'][:32],13)+f'<rect x="285" y="{y}" width="{max(2,w):.1f}" height="19" rx="4" fill="#8957e5"/>'+txt(300+w,y+15,str(v),12)
 return s
chart('top-stars',top,365)
def city(d):
 s=txt(40,44,'Repository city',23,700)+txt(40,69,'Tower height reflects stars · one tower per repository',13,400,'muted')
 for i,r in enumerate(repos[:70]):
  col=i%14;row=i//14;x=45+col*60+row*10;y=335-row*38;h=12+min(110,math.log1p(r.get('stargazers_count',0))*23)
  s+=f'<rect x="{x}" y="{y-h:.1f}" width="34" height="{h:.1f}" fill="{["#8957e5","#2f81f7","#3fb950"][row%3]}" opacity=".85"/>'
 return s
chart('city',city,380)
def growth(d):
 s=txt(40,43,'Repository growth',23,700)
 dates=sorted(datetime.datetime.fromisoformat(r['created_at'].replace('Z','+00:00')) for r in repos)
 if not dates:return s+txt(40,100,'No repositories yet')
 start=dates[0].timestamp();end=max(dates[-1].timestamp(),start+1)
 pts=['40,290'];
 for i,dt in enumerate(dates):pts.append(f'{40+810*(dt.timestamp()-start)/(end-start):.1f},{290-200*(i+1)/len(dates):.1f}')
 s+=f'<polyline points="{" ".join(pts)}" fill="none" stroke="#8957e5" stroke-width="4"/>'
 return s+txt(40,327,dates[0].strftime('%Y'),13,400,'muted')+txt(810,327,dates[-1].strftime('%Y'),13,400,'muted')
chart('growth',growth,350)
def languages(d):
 s=txt(40,43,'Languages',23,700); total=sum(lang.values()) or 1
 cx=240;cy=200;rad=110;circ=2*math.pi*rad;offset=0
 for i,(k,v) in enumerate(lang.most_common(8)):
  frac=v/total;color=['#8957e5','#2f81f7','#3fb950','#d29922','#f778ba','#79c0ff','#db6d28','#8b949e'][i]
  s+=f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="none" stroke="{color}" stroke-width="40" stroke-dasharray="{circ*frac:.2f} {circ:.2f}" stroke-dashoffset="{-offset:.2f}" transform="rotate(-90 {cx} {cy})"/>'
  s+=f'<rect x="490" y="{90+i*30}" width="12" height="12" fill="{color}"/>'+txt(515,101+i*30,f'{k}: {v}',15)
  offset+=circ*frac
 return s
chart('languages',languages,365)
def punch(d):
 s=txt(40,43,'Repository creation punchcard',23,700)+txt(40,66,'UTC · weekday by hour',13,400,'muted');counts=collections.Counter((datetime.datetime.fromisoformat(r['created_at'].replace('Z','+00:00')).weekday(),datetime.datetime.fromisoformat(r['created_at'].replace('Z','+00:00')).hour) for r in repos)
 maxv=max(counts.values(),default=1)
 for day in range(7):
  s+=txt(35,107+day*33,['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][day],12)
  for hr in range(24):
   n=counts[(day,hr)];x=110+hr*31;y=103+day*33
   if n:s+=f'<circle cx="{x}" cy="{y}" r="{2+10*math.sqrt(n/maxv):.1f}" fill="#8957e5"/>'
 for hr in (0,6,12,18,23):s+=txt(104+hr*31,350,str(hr),12,400,'muted')
 return s
chart('punchcard',punch,375)
def picture(name,alt):
 return f'<p align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="./assets/{name}-dark.svg"/><source media="(prefers-color-scheme: light)" srcset="./assets/{name}-light.svg"/><img alt="{esc(alt)}" src="./assets/{name}-light.svg" width="100%"/></picture></p>'
lines=['<h1 align="center">Syfer</h1>','<p align="center"><b>Developer · Web applications · Crypto &amp; creative technology</b></p>','<p align="center"><a href="https://github.com/IDONTSHOWSYFER?tab=followers"><img alt="Followers" src="https://img.shields.io/github/followers/IDONTSHOWSYFER?style=for-the-badge&amp;logo=github&amp;label=followers"/></a> <a href="https://github.com/IDONTSHOWSYFER?tab=repositories"><img alt="Repositories" src="https://img.shields.io/badge/repositories-'+str(len(repos))+'-6250d6?style=for-the-badge&amp;logo=github"/></a> <a href="https://x.com/0xSyfer"><img alt="X" src="https://img.shields.io/badge/X-0xSyfer-000000?style=for-the-badge&amp;logo=x"/></a></p>',picture('stats','GitHub overview'),picture('planet','Repository universe'), '## Start here']
if repos:
 for r in repos[:6]:lines.append(f'- [{r["name"]}]({r["html_url"]}) ★{r.get("stargazers_count",0)}: {esc((r.get("description") or "Source code and documentation")[:150])}')
else:lines.append('Projects will appear here as public repositories are published.')
lines.extend([picture('top-stars','Most starred repositories'),'## By the numbers',picture('city','Repository city'),picture('growth','Repository growth'),picture('languages','Programming languages'),picture('punchcard','Repository creation by hour'),'## All repositories'])
for r in sorted(repos,key=lambda r:r['name'].lower()):lines.append(f'- [{r["name"]}]({r["html_url"]}) ★{r.get("stargazers_count",0)}: {esc((r.get("description") or "")[:140])}')
lines.extend(['## Say hi','Follow me on [GitHub](https://github.com/IDONTSHOWSYFER) or [X @0xSyfer](https://x.com/0xSyfer).',f'<p align="center"><sub>Auto-generated from GitHub public repositories · {len(repos)} repositories · {stars} stars.</sub></p>'])
(ROOT/'README.md').write_text('\n\n'.join(lines)+'\n',encoding='utf-8')
(ROOT/'repos.json').write_text(json.dumps([{'name':r['name'],'url':r['html_url'],'description':r.get('description'),'stars':r.get('stargazers_count',0),'language':r.get('language')} for r in repos],indent=2,ensure_ascii=False)+'\n')
print(f'Generated {len(repos)} repositories, {stars} stars')
