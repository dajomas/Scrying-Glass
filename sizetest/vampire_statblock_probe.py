#!/usr/bin/env python3
"""One-off Vampire source probe. Python 3.10+, standard library only.
Run from any directory; optionally pass --display-json with your display configuration.
No login, cookies, access bypass, application writes, or source substitution.
"""
import argparse
import csv
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote, urlencode, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

LIMITS = {'response': 10*1024**2, 'normalized': 512*1024, 'text': 64*1024,
          'nodes': 4096, 'depth': 16}
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
def compact(v):
    return json.dumps(v, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
def norm(v):
    return re.sub(r'[^a-z0-9]+', ' ', str(v).casefold()).strip()

class Redirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        a,b = urlsplit(req.full_url),urlsplit(newurl)
        n = getattr(req, '_redirects', 0)+1
        allowed = {a.hostname}
        if a.hostname in {'www.dndbeyond.com','dndbeyond.com'}:
            allowed |= {'www.dndbeyond.com','dndbeyond.com','marketplace.dndbeyond.com'}
        if b.scheme != 'https' or b.hostname not in allowed or b.username or b.password or n>3:
            raise ValueError('Unapproved redirect')
        r=super().redirect_request(req,fp,code,msg,headers,newurl)
        if r is not None: r._redirects=n
        return r

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]; self.anchors=[]; self.anchor=None; self.blocks=[]; self.active=None
    def handle_starttag(self, tag, attrs):
        d=dict(attrs); classes=d.get('class','').split()
        if tag=='a': self.anchor={'href':d.get('href',''),'parts':[],'legacy':'legacy' in str(attrs).casefold()}
        if self.active is None and any(c in {'mon-stat-block','mon-stat-block-2024','stat-block'} for c in classes):
            self.active={'level':len(self.stack),'segments':[],'tags':0,'max_dom_depth':0}
        if self.active is not None:
            self.active['tags']+=1
            self.active['max_dom_depth']=max(self.active['max_dom_depth'],len(self.stack)-self.active['level']+1)
        if tag not in VOID: self.stack.append((tag,d.get('class','')))
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:self.handle_endtag(tag)
    def handle_endtag(self, tag):
        if tag=='a' and self.anchor is not None:
            self.anchor['text']=' '.join(self.anchor.pop('parts'));self.anchors.append(self.anchor);self.anchor=None
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                del self.stack[i:];break
        if self.active is not None and len(self.stack)<=self.active['level']:
            self.blocks.append(self.active);self.active=None
    def handle_data(self, text):
        if self.anchor is not None:self.anchor['parts'].append(text)
        text=text.strip()
        if self.active is not None and text and not any(t in {'script','style'} for t,c in self.stack):
            self.active['segments'].append({'element':self.stack[-1][0] if self.stack else '',
                'class':self.stack[-1][1] if self.stack else '', 'text':text})

def measure(v):
    rows=[];counts={'objects':0,'arrays':0,'scalars':0,'max_depth':0}
    def walk(x,path,depth):
        counts['max_depth']=max(counts['max_depth'],depth)
        kind='objects' if isinstance(x,dict) else 'arrays' if isinstance(x,list) else 'scalars'
        counts[kind]+=1
        rows.append({'path':path,'type':type(x).__name__,'json_bytes':len(compact(x)),
            'text_utf8_bytes':len(x.encode('utf-8')) if isinstance(x,str) else '',
            'depth':depth})
        if isinstance(x,dict):
            for k,a in x.items():walk(a,path+'/'+str(k).replace('~','~0').replace('/','~1'),depth+1)
        elif isinstance(x,list):
            for i,a in enumerate(x):walk(a,path+'/'+str(i),depth+1)
    walk(v,'',0)
    counts['source_values']=counts['objects']+counts['arrays']+counts['scalars']
    counts['compact_json_bytes']=len(compact(v))
    counts['largest_string_bytes']=max((r['text_utf8_bytes'] for r in rows if r['type']=='str'),default=0)
    return counts,rows

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--display-json',type=Path)
    ap.add_argument('--out',type=Path,default=Path('vampire-probe-results'))
    ap.add_argument('--timeout',type=float,default=30)
    ap.add_argument('--max-response-mib',type=int,default=64,help='Diagnostic ceiling, deliberately above proposed 10 MiB')
    args=ap.parse_args()
    if args.timeout<=0 or not 1<=args.max_response_mib<=256:ap.error('Invalid timeout or diagnostic size ceiling')
    cfg=json.loads(args.display_json.read_text(encoding='utf-8')) if args.display_json else {}
    cfg=cfg.get('display',cfg)
    root=args.out
    if root.exists() and any(root.iterdir()):ap.error('Output directory must be absent or empty; do not overwrite earlier evidence')
    root.mkdir(parents=True,exist_ok=True)
    (root/'raw').mkdir()
    requests=[]; records=[]; issues=[]; fields=[]
    opener=build_opener(Redirects())
    def fetch(url,label,html=False):
        p=urlsplit(url)
        if p.scheme!='https' or not p.hostname or p.username or p.password:raise ValueError('HTTPS URL without credentials required')
        request=Request(url,headers={'User-Agent':'Mozilla/5.0 compatible; ScryingGlass/1.0',
            'Accept':'text/html,application/xhtml+xml' if html else 'application/json','Accept-Encoding':'identity'})
        index=len(requests)+1; started=time.monotonic()
        meta={'url':url,'label':label,'started_utc':datetime.now(timezone.utc).isoformat()}
        try:
            try: response=opener.open(request,timeout=args.timeout)
            except HTTPError as exc:response=exc
            with response:
                raw=response.read(args.max_response_mib*1024**2+1)
                meta.update(status=response.code,final_url=response.geturl(),content_type=response.headers.get('Content-Type'),
                    content_encoding=response.headers.get('Content-Encoding'),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
            name=f'raw/{index:03d}-{label}.'+('html' if html else 'json')
            (root/name).write_bytes(raw);meta['file']=name
            meta['truncated']=len(raw)>args.max_response_mib*1024**2
            if meta['truncated']:raise ValueError('Diagnostic response ceiling exceeded; saved response is truncated')
            if meta['status']!=200:raise ValueError('HTTP '+str(meta['status'])+'; saved response is not a successful statblock')
            if meta.get('content_encoding') not in {None,'identity'}:raise ValueError('Unexpected content encoding; bytes are not decompressed evidence')
            return raw.decode('utf-8') if html else json.loads(raw)
        except Exception as exc:
            meta['error']=str(exc);raise
        finally:
            meta['elapsed_seconds']=round(time.monotonic()-started,3);requests.append(meta)
    def issue(provider,exc):issues.append({'provider':provider,'error':str(exc)})
    def add(provider,identity,value,note=''):
        number=len(records)+1;name=f'{number:03d}-'+provider
        path=f'{name}.json'; (root/path).write_bytes(compact(value))
        stats,rows=measure(value)
        for row in rows:fields.append({'record':path,**row})
        records.append({'provider':provider,'identity':identity,'file':path,'note':note,**stats})
    base=str(cfg.get('open5e_base_url','https://api.open5e.com/v2')).rstrip('/')
    try:
        url=base+'/creatures/?'+urlencode({'name__iexact':'Vampire','limit':100,'format':'json'})
        seen=set();keys=set()
        for page in range(10):
            if url in seen:raise ValueError('Pagination loop')
            seen.add(url)
            if urlsplit(url).hostname!=urlsplit(base).hostname:raise ValueError('Pagination left configured host')
            obj=fetch(url,'open5e-list-'+str(page))
            if not isinstance(obj,dict) or not isinstance(obj.get('results'),list):raise ValueError('Invalid list shape')
            for item in obj['results']:
                if norm(item.get('name'))!='vampire':continue
                key=item.get('key')
                if not isinstance(key,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,199}',key):raise ValueError('Invalid creature key')
                if key in keys:continue
                keys.add(key)
                try:
                    detail=fetch(base+'/creatures/'+quote(key,safe='')+'/?format=json','open5e-detail-'+str(len(keys)))
                    if detail.get('key')!=key or norm(detail.get('name'))!='vampire':raise ValueError('Detail identity mismatch')
                    add('open5e',{'key':key,'document':detail.get('document')},detail)
                except Exception as exc:issue('open5e',exc)
            next_url=obj.get('next')
            if not next_url:break
            url=urljoin(url,next_url)
        else:raise ValueError('Pagination exceeded ten pages; discovery incomplete')
        if not keys:issue('open5e','No exact Vampire records discovered')
    except Exception as exc:issue('open5e',exc)
    base=str(cfg.get('fivetools_data_base_url','https://5e.tools/data/bestiary')).rstrip('/')
    sources=cfg.get('fivetools_sources',['MM','XMM','PHB','XPHB','DMG','XDMG'])
    if not isinstance(sources,list) or not all(isinstance(x,str) for x in sources):raise ValueError('Invalid fivetools_sources')
    try:
        index=fetch(base+'/index.json','fivetools-index');files_seen=set();matches=0
        for source in dict.fromkeys(sources):
            filename=index.get(source)
            if filename is None:
                issue('fivetools',f'{source}: no bestiary file in index');continue
            if not isinstance(filename,str) or not re.fullmatch(r'[A-Za-z0-9_.-]+\.json',filename):
                issue('fivetools',f'{source}: invalid filename');continue
            if filename in files_seen:continue
            files_seen.add(filename)
            try:
                obj=fetch(base+'/'+filename,'fivetools-dataset-'+str(len(files_seen)))
                for i,item in enumerate(obj.get('monster',[])):
                    if not isinstance(item,dict) or norm(item.get('name'))!='vampire':continue
                    matches+=1
                    add('fivetools',{'source':item.get('source'),'name':item.get('name'),'file':filename,'index':i},item,
                        'UNRESOLVED COPY: raw size is not full statblock size' if '_copy' in item else 'Raw source record; inline tags are not normalized nodes')
            except Exception as exc:issue('fivetools',exc)
        if not matches:issue('fivetools','No exact Vampire records discovered in configured sources')
    except Exception as exc:issue('fivetools',exc)
    try:
        text=fetch('https://www.dndbeyond.com/monsters?filter-search=Vampire','dndbeyond-search',True)
        parser=Page();parser.feed(text)
        hrefs=list(dict.fromkeys(a['href'] for a in parser.anchors if norm(a['text'])=='vampire' and re.fullmatch(r'/monsters/[^?#]+',a['href'])))
        if not hrefs:issue('dndbeyond','No exact Vampire links: discovery may be blocked or markup changed; not proof of absence')
        for i,href in enumerate(hrefs[:32]):
            try:
                text=fetch('https://www.dndbeyond.com'+href,'dndbeyond-detail-'+str(i),True)
                p=Page();p.feed(text)
                if not p.blocks:raise ValueError('No recognized statblock root: access gate, unsupported markup or absent content; inspect saved page')
                for n,block in enumerate(p.blocks):
                    add('dndbeyond',{'href':href,'block':n},block,'Extracted DOM text segments, NOT a verified normalized statblock; inspect raw page for gates/completeness')
            except Exception as exc:issue('dndbeyond',exc)
        if len(hrefs)>32:issue('dndbeyond','More than 32 candidates; discovery truncated explicitly')
    except Exception as exc:issue('dndbeyond',exc)
    manifest={'created_utc':datetime.now(timezone.utc).isoformat(),'target':'Vampire',
        'scope':'Three online providers; exact-name variants kept separate; no source fallback. Defaults unless --display-json supplied. Provider enable switches intentionally ignored for this diagnostic.',
        'proposed_limits':LIMITS,'requests':requests,'records':records,'issues':issues,
        'normalization':'No production normalizer exists. JSON depth/value counts and HTML DOM counts are source metrics, NOT normalized node counts/depth. No normalized-limit pass is asserted.'}
    (root/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    with (root/'fields.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['record','path','type','json_bytes','text_utf8_bytes','depth']);w.writeheader();w.writerows(fields)
    lines=['# Vampire statblock diagnostic','',manifest['normalization'],'',
        'Source responses, datasets and individual creature records are separate measurements. Raw responses are retained for reproducibility; HTML may include surrounding site content.','',
        '| Record | Compact source bytes | Largest string bytes | Source values | JSON depth |','|---|---:|---:|---:|---:|']
    for r in records:lines.append(f"| {r['file']} | {r['compact_json_bytes']} | {r['largest_string_bytes']} | {r['source_values']} | {r['max_depth']} |")
    lines+=['','## Network responses','', '| Label | HTTP | Response bytes | Above proposed 10 MiB? |','|---|---:|---:|---|']
    for r in requests:lines.append(f"| {r['label']} | {r.get('status','failed')} | {r.get('bytes','unknown')} | {r.get('bytes',0)>LIMITS['response']} |")
    lines+=['','## Failures and limitations','']+[f"- {i['provider']}: {i['error']}" for i in issues]
    lines+=['','The 512 KiB normalized limit, 4,096 normalized nodes and depth 16 require the actual normalizer or a separately specified faithful model. These measurements alone cannot validate them. A Vampire sample also cannot establish bounds for all monsters.',
        '','Timing uses socket timeouts, not an enforced total-operation deadline. This one-off sequential probe is not the proposed production fetcher. No concurrency/cache-capacity validation is performed.']
    (root/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(f'Saved {len(records)} candidate records, {len(requests)} request logs, and {len(issues)} issues in {root}')
    return 0 if records else 2

if __name__=='__main__':
    raise SystemExit(main())
