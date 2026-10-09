"""Portable campaign bundles; bounded, additive imports and safe media paths."""
import copy
import io
import json
import re
import uuid
import zipfile
from pathlib import PurePosixPath

MEDIA=re.compile(r'/media/[A-Za-z0-9_.-]+')

def walk(value,replace):
    if isinstance(value,dict): return {k:walk(v,replace) for k,v in value.items()}
    if isinstance(value,list): return [walk(v,replace) for v in value]
    if isinstance(value,str): return MEDIA.sub(replace,value)
    return value

def export_bundle(context):
    campaign=context.active_campaign()
    payload={'format':'scrying-glass-campaign','version':1,'campaign':context.read_campaigns()['campaigns'][campaign],'characters':context.STORAGE.load_characters(campaign) or [],'setups':{name:context.STORAGE.load_setup(campaign,name) for name in context.STORAGE.list_setups(campaign)},'encounter':copy.deepcopy(context.STATE)}
    media=set()
    def collect(match): media.add(match[0]);return match[0]
    walk(payload,collect)
    manifest=json.dumps(payload,ensure_ascii=False,indent=2).encode()
    if len(manifest)>10*1024*1024: raise context.HTTPException(413,'Manifest exceeds 10 MiB')
    if len(media)>999: raise context.HTTPException(413,'Too many media files')
    output=io.BytesIO();total=len(manifest)
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr('campaign.json',manifest)
        for url in sorted(media):
            name=url.removeprefix('/media/');path=(context.UPLOAD_DIR/name).resolve()
            if path.parent!=context.UPLOAD_DIR.resolve() or not path.is_file(): raise context.HTTPException(409,'Missing/unsafe media: '+name)
            total+=path.stat().st_size
            if total>100*1024*1024: raise context.HTTPException(413,'Expanded bundle exceeds 100 MiB')
            bundle.writestr('media/'+name,path.read_bytes())
    if output.tell()>25*1024*1024: raise context.HTTPException(413,'Compressed bundle exceeds 25 MiB')
    return output.getvalue()

def import_bundle(context,raw):
    if len(raw)>25*1024*1024: raise context.HTTPException(413,'Bundle exceeds 25 MiB')
    written=[]
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as bundle:
            entries=bundle.infolist();names=[m.filename for m in entries]
            if len(entries)>1000 or sum(m.file_size for m in entries)>100*1024*1024: raise ValueError('Expansion limit exceeded')
            if len(set(names))!=len(names): raise ValueError('Duplicate members')
            if 'campaign.json' not in names or bundle.getinfo('campaign.json').file_size>10*1024*1024: raise ValueError('Missing/oversized manifest')
            for member in entries:
                p=PurePosixPath(member.filename)
                if member.filename!='campaign.json' and (len(p.parts)!=2 or p.parts[0]!='media' or p.name in ('.','..') or chr(92) in member.filename): raise ValueError('Unsafe member path')
            payload=json.loads(bundle.read('campaign.json'))
            if not isinstance(payload,dict) or payload.get('format')!='scrying-glass-campaign' or payload.get('version')!=1: raise ValueError('Unsupported bundle format')
            metadata=payload['campaign'];name=metadata['name'];description=metadata.get('description','')
            if not isinstance(name,str) or not 1<=len(name)<=100 or not isinstance(description,str) or len(description)>2000: raise ValueError('Invalid campaign metadata')
            setups=payload['setups']
            if not isinstance(setups,dict) or not 1<=len(setups)<=200: raise ValueError('Invalid setup collection')
            validated={}
            for key,state in setups.items():
                if context.setup_slug(key)!=key: raise ValueError('Invalid setup name')
                validated[key]=context.normalize_state(state)
                if validated[key]['characters']: raise ValueError('Setup contains characters')
            characters=context.normalize_state({'characters':payload['characters']})['characters']
            encounter=context.normalize_state(payload['encounter']);mapping={};staged=[]
            for member in entries:
                if member.filename=='campaign.json': continue
                old=PurePosixPath(member.filename).name;suffix=PurePosixPath(old).suffix.lower()
                if suffix not in ('.png','.jpg','.jpeg','.gif','.webp','.avif','.bmp'): raise ValueError('Unsupported media format')
                new=uuid.uuid4().hex+suffix;mapping['/media/'+old]='/media/'+new
                staged.append((context.UPLOAD_DIR/new,bundle.read(member)))
            def rewrite(match):
                if match[0] not in mapping: raise ValueError('Missing referenced media')
                return mapping[match[0]]
            validated=walk(validated,rewrite);characters=walk(characters,rewrite);encounter=walk(encounter,rewrite)
            base=name;i=2
            while context.STORAGE.campaign_name_exists(name):
                suffix=f' (import {i})';name=base[:100-len(suffix)]+suffix;i+=1
            campaign=context.STORAGE.create_campaign(name,description,context.now_iso())
            context.STORAGE.save_characters(campaign,characters)
            for key,state in validated.items(): state['active_setup']=None;context.STORAGE.save_setup(campaign,key,state)
            if encounter['active_setup']:
                key=encounter['active_setup']['name']
                if key not in validated: raise ValueError('Runtime references absent setup')
                encounter['active_setup']={'campaign_id':str(campaign),'name':key}
            checkpoint=context.features.store.save_snapshot(campaign,encounter,'checkpoint','Imported encounter')
            for path,data in staged:
                context._bundle_files.append(path)
                path.write_bytes(data);written.append(path)
            return {'campaign_id':str(campaign),'name':name,'checkpoint_id':checkpoint}
    except (ValueError,KeyError,TypeError,zipfile.BadZipFile,RuntimeError,OSError) as exc:
        for path in written:
            try: path.unlink(missing_ok=True)
            except OSError: pass
        raise context.HTTPException(422,'Invalid campaign bundle: '+str(exc)) from exc
