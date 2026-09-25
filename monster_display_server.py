#!/usr/bin/env python3
"""Monster Display v4.14 (Python 3.14+).

Dependencies:
  python3.14 -m pip install 'fastapi>=0.115' 'uvicorn[standard]>=0.30' 'PyYAML>=6.0' python-multipart

Run:
  python3.14 monster_display_server_v4_14.py --config config.yaml

v4.14 fixes the admin-page initialization error introduced in v4.13. The Add
Character form is restored, and UI listeners are registered defensively.
"""
from __future__ import annotations
import argparse, asyncio, copy, hashlib, hmac, json, re, secrets, shutil, sys, uuid
from pathlib import Path
from typing import Any, Literal
from urllib.parse import quote
from urllib.request import Request, urlopen
import yaml
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request as FastAPIRequest, UploadFile, WebSocket
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn
import random

DEFAULT_CONFIG={"network":{"bind":"0.0.0.0","admin_port":3000,"client_port":4000},"storage_dir":"./monster-display-data","security":{"users":[{"username":"admin","role":"admin","password":"CHANGE-ME"},{"username":"client","role":"client","password":"CHANGE-ME"}]},"display":{"background":"#080b14","entry_direction":"from_bottom","exit_direction":"to_bottom","monster_width_percent":45,"dndbeyond_image_lookup":True}}
CONFIG:dict[str,Any]={}; STATE:dict[str,Any]={"monsters":[],"characters":[],"battle_order":[]}; LOCK=asyncio.Lock(); SESSIONS:dict[str,dict[str,str]]={}; SOCKETS:set[WebSocket]=set(); DATA_DIR:Path; STATE_FILE:Path; UPLOAD_DIR:Path; SETUPS_DIR:Path

def merge(a:dict[str,Any],b:dict[str,Any])->dict[str,Any]:
    out=dict(a)
    for k,v in b.items():out[k]=merge(out[k],v)if isinstance(v,dict)and isinstance(out.get(k),dict)else v
    return out

def load_config(p:Path|None)->dict[str,Any]:
    if p is None:return DEFAULT_CONFIG
    raw=p.read_text(encoding="utf-8");x=json.loads(raw)if p.suffix.lower()==".json" else yaml.safe_load(raw)
    if not isinstance(x,dict):raise ValueError("Configuration root must be a mapping/object")
    return merge(DEFAULT_CONFIG,x)

def password_hash(password:str,salt:bytes|None=None)->str:
    salt=salt or secrets.token_bytes(16);digest=hashlib.scrypt(password.encode(),salt=salt,n=2**14,r=8,p=1);return f"scrypt${salt.hex()}${digest.hex()}"
def password_ok(password:str,stored:str)->bool:
    if stored.startswith("scrypt$"):
        _,salt,digest=stored.split("$",2);return hmac.compare_digest(password_hash(password,bytes.fromhex(salt)).split("$",2)[2],digest)
    return hmac.compare_digest(password,stored)
def user(name:str)->dict[str,Any]|None:return next((x for x in CONFIG["security"]["users"]if x.get("username")==name),None)
def entities()->list[dict[str,Any]]:return[*STATE["monsters"],*STATE["characters"]]
def entity(ident:str)->dict[str,Any]|None:return next((x for x in entities()if x["id"]==ident),None)
def normalize_state(raw:dict[str,Any])->dict[str,Any]:
    state={"monsters":raw.get("monsters",[]),"characters":raw.get("characters",[]),"battle_order":raw.get("battle_order",[])}
    if not isinstance(state["monsters"],list)or not isinstance(state["characters"],list)or not isinstance(state["battle_order"],list):raise ValueError("Setup has invalid monsters, characters, or battle_order data")
    for m in state["monsters"]:
        if not isinstance(m,dict):raise ValueError("Setup contains an invalid monster")
        m.setdefault("id",uuid.uuid4().hex);m.setdefault("name","Unnamed Monster");m.setdefault("monster_type","unknown");m.setdefault("ac",0);m.setdefault("hp",1);m.setdefault("original_hp",m.get("max_hp",m["hp"]));m.setdefault("max_hp",m["original_hp"]);m.setdefault("color","#842029");m.setdefault("image_url",None);m.setdefault("alive",m["hp"]>=0);m.setdefault("active",False);m.setdefault("visible",False);m.setdefault("ally",False);m.setdefault("initiative",None);m.setdefault("original_initiative",m.get("initiative"));m.setdefault("show_ac",False);m.setdefault("show_hp",False);m.setdefault("show_initiative",False);m.setdefault("in_turn",False)
    for c in state["characters"]:
        if not isinstance(c,dict):raise ValueError("Setup contains an invalid character")
        c.setdefault("id",uuid.uuid4().hex);c.setdefault("name","Unnamed Character");c.setdefault("color","#1f4e79");c.setdefault("hp",1);c.setdefault("max_hp",c["hp"]);c.setdefault("original_hp",c["max_hp"]);c.setdefault("original_initiative",c.get("initiative"));c.setdefault("alive",c["hp"]>=0);c.setdefault("active",False);c.setdefault("visible",False);c.setdefault("in_turn",False)
    known={x["id"]for x in[*state["monsters"],*state["characters"]]};state["battle_order"]=[x for x in state["battle_order"]if x in known]
    return state
def load_state()->None:
    global STATE
    STATE=normalize_state(json.loads(STATE_FILE.read_text(encoding="utf-8")))if STATE_FILE.exists()else normalize_state(STATE)
def save_state()->None:
    temp=STATE_FILE.with_suffix(".tmp");temp.write_text(json.dumps(STATE,indent=2),encoding="utf-8");temp.replace(STATE_FILE)
def public_state()->dict[str,Any]:
    d=CONFIG["display"];return{"monsters":STATE["monsters"],"characters":STATE["characters"],"battle_order":STATE["battle_order"],"display":{"background":d["background"],"entry_direction":d["entry_direction"],"exit_direction":d["exit_direction"],"monster_width_percent":d["monster_width_percent"]}}
def setup_slug(name:str)->str:
    slug=re.sub(r"[^a-z0-9]+","-",name.strip().lower()).strip("-")
    if not slug:raise HTTPException(400,"Setup name must contain letters or numbers")
    return slug[:80]
def setup_path(name:str)->Path:return SETUPS_DIR/(setup_slug(name)+".json")
def list_setups()->list[str]:return sorted((p.stem for p in SETUPS_DIR.glob("*.json")),key=str.casefold)
def reset_imported_monster(source:dict[str,Any])->dict[str,Any]:
    item=copy.deepcopy(source);item['id']=uuid.uuid4().hex;item['hp']=item['original_hp'];item['max_hp']=item['original_hp'];item['initiative']=item.get('original_initiative');item['active']=False;item['alive']=True;item['visible']=False;item['in_turn']=False;item['show_ac']=False;item['show_hp']=False;item['show_initiative']=False;return item
def reset_imported_character(source:dict[str,Any])->dict[str,Any]:
    item=copy.deepcopy(source);item['id']=uuid.uuid4().hex;item['hp']=item['max_hp'];item['initiative']=item.get('original_initiative');item['active']=False;item['alive']=True;item['visible']=False;item['in_turn']=False;return item
async def broadcast()->None:
    message=json.dumps({"type":"state","state":public_state()});stale=[]
    for ws in SOCKETS:
        try:await ws.send_text(message)
        except Exception:stale.append(ws)
    for ws in stale:SOCKETS.discard(ws)
async def changed()->None:
    async with LOCK:save_state()
    await broadcast()
def require(role:Literal["admin","client"]):
    async def dependency(request:FastAPIRequest)->dict[str,str]:
        session=SESSIONS.get(request.cookies.get("monster_session",""))
        if not session or(role=="admin"and session["role"]!="admin"):raise HTTPException(401,"Sign in required")
        return session
    return dependency
def parse_monster(raw:bytes)->dict[str,Any]:
    try:x=json.loads(raw.decode("utf-8"))
    except Exception as exc:raise HTTPException(400,".monster must contain UTF-8 JSON")from exc
    name=str(x.get("name","")).strip();kind=str(x.get("type","")).strip();hp=re.search(r"-?\d+",str(x.get("hpText",x.get("hp",""))));acraw=x.get("ac")or x.get("armorClass")or x.get("otherArmorDesc")or x.get("natArmorBonus");ac=re.search(r"\d+",str(acraw))if acraw is not None else None
    if not name or not kind or not hp or not ac:raise HTTPException(400,".monster needs usable name, type, AC, and HP")
    return{"name":name,"monster_type":kind,"ac":int(ac.group()),"hp":int(hp.group())}
def save_image(upload:UploadFile)->str:
    ext=Path(upload.filename or "").suffix.lower()
    if ext not in{".png",".jpg",".jpeg",".gif",".webp"}:raise HTTPException(400,"Image must be PNG, JPG, GIF, or WebP")
    dst=UPLOAD_DIR/f"{uuid.uuid4().hex}{ext}"
    with dst.open("wb")as f:shutil.copyfileobj(upload.file,f)
    return"/media/"+dst.name
def dnd_image(kind:str)->str|None:
    if not CONFIG["display"].get("dndbeyond_image_lookup",True):return None
    try:
        q=Request("https://www.dndbeyond.com/monsters?filter-search="+quote(kind),headers={"User-Agent":"MonsterDisplay/1.0"})
        with urlopen(q,timeout=5)as r:html=r.read(1_000_000).decode("utf-8","replace")
        found=re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)',html,re.I);return found.group(1)if found else None
    except Exception:return None
def make_monster(fields:dict[str,Any],color:str,upload:UploadFile|None,image_url:str|None=None)->dict[str,Any]:
    hp=fields["hp"];return{"id":uuid.uuid4().hex,**fields,"max_hp":hp,"original_hp":hp,"color":color,"image_url":image_url if image_url is not None else(save_image(upload)if upload and upload.filename else dnd_image(fields["monster_type"])),"active":False,"alive":True,"visible":False,"ally":False,"initiative":None,"original_initiative":None,"show_ac":False,"show_hp":False,"show_initiative":False,"in_turn":False}
def clear_turns()->None:
    for x in entities():x["in_turn"]=False
def clean_order()->None:
    known={x["id"]for x in entities()};STATE["battle_order"]=[x for x in STATE["battle_order"]if x in known]
def insert_into_battle_order(combatant: dict[str, Any]) -> None:
    """Insert a newly activated living combatant into an existing battle order.

    Higher numeric initiative acts first. On equal initiative, the newly added
    combatant is placed after all existing combatants with that same initiative.
    Combatants without initiative are placed after numeric initiatives.
    """

    if not STATE["battle_order"]:
        return

    if not combatant.get("active") or not combatant.get("alive", True):
        return

    combatant_id = combatant["id"]

    if combatant_id in STATE["battle_order"]:
        return

    combatant_initiative = combatant.get("initiative")
    has_numeric_initiative = (
        isinstance(combatant_initiative, int)
        and not isinstance(combatant_initiative, bool)
    )

    insert_at = len(STATE["battle_order"])

    for index, existing_id in enumerate(STATE["battle_order"]):
        existing = entity(existing_id)

        if existing is None:
            continue

        existing_initiative = existing.get("initiative")
        existing_has_numeric_initiative = (
            isinstance(existing_initiative, int)
            and not isinstance(existing_initiative, bool)
        )

        # A combatant without initiative is always after numeric initiatives.
        if not has_numeric_initiative:
            continue

        # A numeric initiative is before all initiative-less combatants.
        if not existing_has_numeric_initiative:
            insert_at = index
            break

        # Descending initiative: insert before the first lower initiative.
        # Equal values are deliberately skipped, so the new combatant ends up
        # after existing combatants with the same initiative.
        if existing_initiative < combatant_initiative:
            insert_at = index
            break

    STATE["battle_order"].insert(insert_at, combatant_id)
def reset_entity(x:dict[str,Any])->None:
    x["active"]=False;x["alive"]=True;x["visible"]=False;x["in_turn"]=False;x["initiative"]=x.get("original_initiative")
    if"monster_type"in x:x["hp"]=x["original_hp"];x["max_hp"]=x["original_hp"];x["show_ac"]=False;x["show_hp"]=False;x["show_initiative"]=False
    else:x["hp"]=x["max_hp"]
def admin_initiative_key(x:dict[str,Any])->tuple[int,str]:
    value=x.get("initiative");initiative=value if isinstance(value,int)and not isinstance(value,bool)else-999
    return(-initiative,str(x.get("name","")).casefold())
def admin_max_hp_key(x:dict[str,Any])->tuple[int,str]:return(-int(x.get("max_hp",0)),str(x.get("name","")).casefold())
def sort_admin_by_initiative()->None:STATE["monsters"].sort(key=admin_initiative_key);STATE["characters"].sort(key=admin_initiative_key)
def sort_admin_by_max_hp()->None:STATE["monsters"].sort(key=admin_max_hp_key);STATE["characters"].sort(key=admin_max_hp_key)
def set_turn(x:dict[str,Any],requested:bool|None)->None:
    if requested is False:x["in_turn"]=False;return
    if requested is not True:return
    if not x.get("active")or not x.get("alive",True):raise HTTPException(400,"Only an active living combatant may have the battle turn")
    clear_turns();x["in_turn"]=True;x["visible"]=True
def numeric_initiative(x:dict[str,Any])->int:
    v=x.get("initiative");return v if isinstance(v,int)and not isinstance(v,bool)else -999
def eligible()->list[dict[str,Any]]:return[x for x in entities()if x.get("active")and x.get("alive",True)]
def begin_battle(order:list[str])->None:
    wanted={x["id"]for x in eligible()}
    if len(order)!=len(wanted)or set(order)!=wanted:raise HTTPException(400,"Battle order must include every active living combatant exactly once")
    STATE["battle_order"]=order;clear_turns()
    if order:entity(order[0])["in_turn"]=True;entity(order[0])["visible"]=True
def advance_turn()->dict[str,Any]|None:
    ids={x["id"]for x in eligible()}
    if not ids:clear_turns();STATE["battle_order"]=[];return None
    order=[i for i in STATE["battle_order"]if i in ids];order += [x["id"]for x in sorted(eligible(),key=lambda z:(-numeric_initiative(z),z["name"].lower()))if x["id"]not in order];STATE["battle_order"]=order
    pos=next((n for n,i in enumerate(order)if entity(i).get("in_turn")),-1);clear_turns();target=entity(order[(pos+1)%len(order)]);target["in_turn"]=True;target["visible"]=True;return target

class MonsterUpdate(BaseModel):
    name:str|None=Field(default=None,min_length=1,max_length=100);monster_type:str|None=Field(default=None,min_length=1,max_length=100);ac:int|None=Field(default=None,ge=0,le=999);max_hp:int|None=Field(default=None,ge=0,le=99999);original_hp:int|None=Field(default=None,ge=0,le=99999);color:str|None=Field(default=None,min_length=1,max_length=40);active:bool|None=None;ally:bool|None=None;visible:bool|None=None;initiative:int|None=Field(default=None,ge=-100,le=100);hp:int|None=Field(default=None,ge=-99999,le=99999);hp_delta:int|None=Field(default=None,ge=-99999,le=99999);show_ac:bool|None=None;show_hp:bool|None=None;show_initiative:bool|None=None;in_turn:bool|None=None
class CharacterCreate(BaseModel):
    name:str=Field(min_length=1,max_length=100);color:str=Field(min_length=1,max_length=40);hp:int=Field(default=1,ge=0,le=99999);initiative:int|None=Field(default=None,ge=-100,le=100)
class CharacterUpdate(BaseModel):
    name:str|None=Field(default=None,min_length=1,max_length=100);color:str|None=Field(default=None,min_length=1,max_length=40);active:bool|None=None;alive:bool|None=None;visible:bool|None=None;initiative:int|None=Field(default=None,ge=-100,le=100);hp:int|None=Field(default=None,ge=-99999,le=99999);max_hp:int|None=Field(default=None,ge=0,le=99999);hp_delta:int|None=Field(default=None,ge=-99999,le=99999);in_turn:bool|None=None
class BattleStart(BaseModel):order:list[str]
class SetupName(BaseModel):name:str=Field(min_length=1,max_length=100)
class SetupImport(BaseModel):name:str=Field(min_length=1,max_length=100);kind:Literal['characters','monsters','both']

admin=FastAPI(title="Monster Display Admin");client=FastAPI(title="Monster Display Client")
LOGIN='''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sign in</title><style>body{font-family:system-ui;background:#111827;color:#eef2ff;display:grid;place-items:center;height:100vh;margin:0}form{background:#1f2937;padding:2rem;border-radius:12px;display:grid;gap:.7rem;width:min(360px,90vw)}input,button{padding:.7rem;border-radius:6px;border:0}button{background:#2563eb;color:#fff}.error{color:#fca5a5}</style></head><body><form method="post"><h1>Monster Display</h1><input name="username" placeholder="Username" required autofocus><input name="password" type="password" placeholder="Password" required><button>Sign in</button>{error}</form></body></html>'''
def login(error:str="")->HTMLResponse:return HTMLResponse(LOGIN.replace("{error}",f'<p class="error">{error}</p>'if error else ""))
ADMIN_HTML=r'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Monster Display Admin</title><style>body{font-family:system-ui,sans-serif;background:#111827;color:#eef2ff;margin:0;padding:1rem}main{max-width:1260px;margin:auto}section{background:#1f2937;border-radius:10px;padding:1rem;margin:1rem 0}input,button,select{padding:.55rem;margin:.18rem;border-radius:6px;border:1px solid #64748b}button{cursor:pointer;background:#2563eb;color:#fff}.danger{background:#b91c1c}.on{background:#047857}.battle{background:#7f1d1d}.reset{background:#4c1d95}.edit{background:#0f766e}.import{background:#7c3aed}.roll{background:#b45309}table{width:100%;border-collapse:collapse}th,td{padding:.45rem;border-bottom:1px solid #475569;text-align:left;vertical-align:top}.row{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center}.message{min-height:1.4rem;color:#fbbf24}.dead{opacity:.55;text-decoration:line-through}.modal{position:fixed;inset:0;background:#000a;display:grid;place-items:center;z-index:10}.modal[hidden]{display:none!important}.modal>div{background:#1f2937;padding:1.25rem;border-radius:10px;width:min(700px,94vw);max-height:94vh;overflow:auto}.tie{display:grid;grid-template-columns:minmax(10rem,1fr) 7rem;gap:.45rem;align-items:center;margin:.35rem 0}.tie select{width:100%}.tie-title{font-weight:700;margin-top:.85rem}.hp-edit{width:5.5rem}.setup-name{min-width:14rem}.edit-form{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.55rem}.edit-form label{display:grid;gap:.25rem}.edit-form .full{grid-column:1/-1}.edit-form .actions{grid-column:1/-1;display:flex;gap:.5rem;margin-top:.4rem}.import-form{display:grid;gap:.7rem}.import-form label{display:grid;gap:.25rem}.import-form .actions{display:flex;gap:.5rem}</style></head><body><main><h1>Monster Display — Admin</h1><p id="message" class="message"></p><section class="row"><input id="setupName" class="setup-name" placeholder="Battle setup name"><button id="newSetup" class="reset">New</button><button id="saveSetup">Save</button><select id="setupSelect"><option value="">Load saved setup…</option></select><button id="loadSetup">Load</button><button id="openImport" class="import">Import from setup</button></section><section class="row"><button id="startBattle" class="battle">Start battle</button><button id="nextBattle" class="battle">Next</button><button id="resetAll" class="reset">Reset All</button><span id="battleInfo"></span></section><section><h2>Add monster</h2><form id="monsterForm" class="row"><input name="name" placeholder="Name" required><input name="monster_type" placeholder="Monster type" required><input name="ac" type="number" placeholder="AC" required><input name="hp" type="number" placeholder="HP" required><input name="quantity" type="number" min="1" max="50" value="1" title="Number of monsters"><input name="color" type="color" value="#842029"><input name="image" type="file" accept="image/*"><button>Add manually</button></form><p>Or import a JSON <code>.monster</code> file:</p><form id="monsterUpload" class="row"><input name="monster_file" type="file" accept=".monster,application/json" required><input name="quantity" type="number" min="1" max="50" value="1" title="Number of monsters"><input name="color" type="color" value="#842029"><input name="image" type="file" accept="image/*"><button>Import .monster</button></form></section><section><h2>Add character</h2><form id="characterForm" class="row"><input name="name" placeholder="Name" required><input name="color" type="color" value="#1f4e79"><input name="hp" type="number" min="0" value="1" required><input name="initiative" type="number" placeholder="Initiative (optional)"><button>Add character</button></form></section><section><div class="row"><h2>Monsters</h2><button id="rollMonsterInitiative" class="roll">Roll monster initiatives (d20)</button></div><div id="monsters"></div></section><section><h2>Characters</h2><div id="characters"></div></section></main><div id="tieModal" class="modal" hidden><div><h2>Resolve tied initiative</h2><p>Choose a unique position for every combatant in each tied initiative group. Position 1 acts first within that group.</p><div id="tieGroups"></div><button id="confirmOrder">Start battle</button><button id="cancelOrder">Cancel</button></div></div><div id="editModal" class="modal" hidden><div><h2 id="editTitle">Edit combatant</h2><form id="editForm" class="edit-form"></form></div></div><div id="importModal" class="modal" hidden><div><h2>Import combatants from a saved setup</h2><p>Imported combatants receive new IDs and reset runtime state. The current battle order is not changed.</p><form id="importForm" class="import-form"><label>Saved setup<select id="importSetup" name="name" required></select></label><label>Import<select name="kind"><option value="characters">Characters only</option><option value="monsters">Monsters only</option><option value="both">Characters and monsters</option></select></label><div class="actions"><button class="import">Import</button><button type="button" id="cancelImport">Cancel</button></div></form></div></div><script>let latest,editing=null;const message=t=>document.querySelector('#message').textContent=t;const all=()=>[...latest.monsters,...latest.characters];const editModal=document.querySelector('#editModal'),importModal=document.querySelector('#importModal');function closeEdit(){editModal.hidden=true;editing=null;document.querySelector('#editForm').innerHTML=''}function closeImport(){importModal.hidden=true}async function request(url,opt={}){const r=await fetch(url,opt);if(!r.ok)throw new Error((await r.json().catch(()=>({detail:r.statusText}))).detail);return r.json().catch(()=>null)}function esc(v){return String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}function numberValue(form,name,fallback){let v=form.elements[name].value;return v===''?fallback:+v}async function patch(kind,id,data){try{await request('/api/'+kind+'/'+id,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});await load()}catch(e){message(e.message)}}function monsterRow(x){return `<tr class="${x.alive?'':'dead'}"><td>${esc(x.name)}<br><small>${esc(x.monster_type)}</small></td><td>${x.ac}</td><td>${x.hp}/${x.max_hp}</td><td><input data-mi="${x.id}" type="number" value="${x.initiative??''}" placeholder="init"></td><td><button data-edit="${x.id}" data-kind="monsters" class="edit">Edit</button><button class="${x.active?'on':''}" data-ma="${x.id}">${x.active?'Active':'Off'}</button><button class="${x.ally?'on':''}" data-mally="${x.id}">Ally</button><button class="${x.visible?'on':''}" data-mv="${x.id}">Visible</button><button data-mt="${x.id}" class="${x.in_turn?'on':''}">Turn</button><button data-r="${x.id}" class="reset">Reset</button><button data-t="${x.id}" data-f="show_ac">AC ${x.show_ac?'on':'off'}</button><button data-t="${x.id}" data-f="show_hp">HP ${x.show_hp?'on':'off'}</button><button data-t="${x.id}" data-f="show_initiative">Init ${x.show_initiative?'on':'off'}</button></td><td><button data-d="${x.id}" class="danger">Damage</button><button data-h="${x.id}">Heal</button></td></tr>`}function characterRow(x){return `<tr class="${x.alive?'':'dead'}"><td>${esc(x.name)}</td><td><input class="hp-edit" data-chp="${x.id}" type="number" min="0" value="${x.hp}"> / <input class="hp-edit" data-cmaxhp="${x.id}" type="number" min="0" value="${x.max_hp}"></td><td><input data-ci="${x.id}" type="number" value="${x.initiative??''}" placeholder="init"></td><td><button data-edit="${x.id}" data-kind="characters" class="edit">Edit</button><button class="${x.active?'on':''}" data-ca="${x.id}">${x.active?'Active':'Off'}</button><button class="${x.alive?'on':''}" data-cl="${x.id}">${x.alive?'Alive':'Dead'}</button><button class="${x.visible?'on':''}" data-cv="${x.id}">Visible</button><button data-ct="${x.id}" class="${x.in_turn?'on':''}">Turn</button><button data-cr="${x.id}" class="reset">Reset</button></td><td><button data-cd="${x.id}" class="danger">Damage</button><button data-ch="${x.id}">Heal</button></td></tr>`}function monsterEdit(x){return `<label>Name<input name="name" required value="${esc(x.name)}"></label><label>Monster type<input name="monster_type" required value="${esc(x.monster_type)}"></label><label>AC<input name="ac" type="number" min="0" value="${x.ac}"></label><label>Color<input name="color" type="color" value="${esc(x.color)}"></label><label>Current HP<input name="hp" type="number" value="${x.hp}"></label><label>Max HP<input name="max_hp" type="number" min="0" value="${x.max_hp}"></label><label>Reset HP<input name="original_hp" type="number" min="0" value="${x.original_hp}"></label><label>Initiative<input name="initiative" type="number" min="-100" max="100" value="${x.initiative??''}"></label><label>Ally<select name="ally"><option value="false" ${x.ally?'':'selected'}>No</option><option value="true" ${x.ally?'selected':''}>Yes</option></select></label><label>Replace image<input name="image" type="file" accept="image/*"></label><div class="actions"><button>Save monster</button><button type="button" id="cancelEdit">Cancel</button></div>`}function characterEdit(x){return `<label>Name<input name="name" required value="${esc(x.name)}"></label><label>Color<input name="color" type="color" value="${esc(x.color)}"></label><label>Current HP<input name="hp" type="number" value="${x.hp}"></label><label>Max HP<input name="max_hp" type="number" min="0" value="${x.max_hp}"></label><label>Initiative<input name="initiative" type="number" min="-100" max="100" value="${x.initiative??''}"></label><div class="actions"><button>Save character</button><button type="button" id="cancelEdit">Cancel</button></div>`}function openEdit(kind,id){let item=(kind==='monsters'?latest.monsters:latest.characters).find(x=>x.id===id);if(!item)return;editing={kind,id};document.querySelector('#editTitle').textContent='Edit '+(kind==='monsters'?'monster':'character')+': '+item.name;document.querySelector('#editForm').innerHTML=kind==='monsters'?monsterEdit(item):characterEdit(item);document.querySelector('#cancelEdit').onclick=closeEdit;editModal.hidden=false}async function setups(){try{let s=await request('/api/setups');let select=document.querySelector('#setupSelect'),old=select.value;select.innerHTML='<option value="">Load saved setup…</option>'+s.names.map(n=>'<option value="'+esc(n)+'">'+esc(n)+'</option>').join('');if(s.names.includes(old))select.value=old;let imp=document.querySelector('#importSetup'),previous=imp.value;imp.innerHTML='<option value="">Choose setup…</option>'+s.names.map(n=>'<option value="'+esc(n)+'">'+esc(n)+'</option>').join('');if(s.names.includes(previous))imp.value=previous}catch(e){message(e.message)}}async function load(){try{latest=await request('/api/state');document.querySelector('#monsters').innerHTML='<table><tr><th>Monster</th><th>AC</th><th>HP</th><th>Initiative</th><th>Display/status</th><th>HP change</th></tr>'+latest.monsters.map(monsterRow).join('')+'</table>';document.querySelector('#characters').innerHTML='<table><tr><th>Character</th><th>Current / Max HP</th><th>Initiative</th><th>Display/status</th><th>HP change</th></tr>'+latest.characters.map(characterRow).join('')+'</table>';document.querySelector('#battleInfo').textContent=latest.battle_order.length?'Order: '+latest.battle_order.map(id=>all().find(x=>x.id===id)?.name).filter(Boolean).join(' → '):'No battle order set'}catch(e){message(e.message)}}document.querySelector('#editForm').onsubmit=async e=>{e.preventDefault();if(!editing)return;let f=e.target,data={name:f.elements.name.value.trim(),color:f.elements.color.value,hp:numberValue(f,'hp',0),max_hp:numberValue(f,'max_hp',0),initiative:f.elements.initiative.value===''?null:+f.elements.initiative.value};if(editing.kind==='monsters'){data.monster_type=f.elements.monster_type.value.trim();data.ac=numberValue(f,'ac',0);data.original_hp=numberValue(f,'original_hp',0);data.ally=f.elements.ally.value==='true';let image=f.elements.image.files[0];try{if(image){let fd=new FormData();Object.entries(data).forEach(([k,v])=>fd.append(k,v===null?'':String(v)));fd.append('image',image);let r=await fetch('/api/monsters/'+editing.id+'/edit',{method:'POST',body:fd});if(!r.ok)throw new Error((await r.json().catch(()=>({detail:r.statusText}))).detail)}else await request('/api/monsters/'+editing.id,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)})}catch(x){message(x.message);return}}else{if(data.initiative===null)delete data.initiative;try{await request('/api/characters/'+editing.id,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)})}catch(x){message(x.message);return}}closeEdit();await load()};document.querySelector('#openImport').onclick=async()=>{await setups();importModal.hidden=false};document.querySelector('#cancelImport').onclick=closeImport;document.querySelector('#importForm').onsubmit=async e=>{e.preventDefault();let f=new FormData(e.target),name=f.get('name'),kind=f.get('kind');if(!name){message('Choose a saved setup to import from');return}if(!confirm('Import '+kind+' from '+name+' into the current setup?'))return;try{let result=await request('/api/setups/import',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,kind})});closeImport();await load();message('Imported '+result.characters+' character(s) and '+result.monsters+' monster(s) from '+result.name)}catch(x){message(x.message)}};document.querySelector('#rollMonsterInitiative').onclick=async()=>{if(!latest.monsters.length){message('There are no monsters to roll initiative for');return}if(!confirm('Overwrite initiative for every monster with a random d20 roll?'))return;try{let result=await request('/api/monsters/roll-initiative',{method:'POST'});await load();message('Rolled d20 initiative for '+result.count+' monster(s)')}catch(e){message(e.message)}};editModal.addEventListener('click',e=>{if(e.target===editModal)closeEdit()});importModal.addEventListener('click',e=>{if(e.target===importModal)closeImport()});document.addEventListener('keydown',e=>{if(e.key==='Escape'){if(!editModal.hidden)closeEdit();if(!importModal.hidden)closeImport()}});document.querySelector('#newSetup').onclick=async()=>{if(!confirm('Discard the current battle setup and create a new blank setup?'))return;try{await request('/api/setups/new',{method:'POST'});document.querySelector('#setupName').value='';document.querySelector('#setupSelect').value='';await load()}catch(e){message(e.message)}};document.querySelector('#saveSetup').onclick=async()=>{let name=document.querySelector('#setupName').value.trim();if(!name){message('Enter a battle setup name before saving');return}try{let result=await request('/api/setups/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name})});document.querySelector('#setupName').value=result.name;await setups();document.querySelector('#setupSelect').value=result.name;message('Saved setup: '+result.name)}catch(e){message(e.message)}};document.querySelector('#loadSetup').onclick=async()=>{let name=document.querySelector('#setupSelect').value;if(!name){message('Choose a saved setup to load');return}if(!confirm('Load '+name+' and replace the current battle setup?'))return;try{let result=await request('/api/setups/load',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name})});document.querySelector('#setupName').value=result.name;await load();message('Loaded setup: '+result.name)}catch(e){message(e.message)}};document.querySelector('#monsterForm').onsubmit=async e=>{e.preventDefault();try{let result=await request('/api/monsters',{method:'POST',body:new FormData(e.target)});message('Added '+result.length+' monster'+(result.length===1?'':'s'));e.target.reset();await load()}catch(x){message(x.message)}};document.querySelector('#monsterUpload').onsubmit=async e=>{e.preventDefault();try{let result=await request('/api/monsters/import',{method:'POST',body:new FormData(e.target)});message('Imported '+result.length+' monster'+(result.length===1?'':'s'));e.target.reset();await load()}catch(x){message(x.message)}};document.querySelector('#characterForm').onsubmit=async e=>{e.preventDefault();let f=new FormData(e.target);try{await request('/api/characters',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:f.get('name'),color:f.get('color'),hp:+f.get('hp'),initiative:f.get('initiative')===''?null:+f.get('initiative')})});e.target.reset();await load()}catch(x){message(x.message)}};document.addEventListener('click',e=>{let b=e.target;if(b.dataset.edit)return openEdit(b.dataset.kind,b.dataset.edit);let id=b.dataset.ma||b.dataset.mally||b.dataset.mv||b.dataset.mt||b.dataset.t||b.dataset.d||b.dataset.h||b.dataset.r||b.dataset.ca||b.dataset.cl||b.dataset.cv||b.dataset.ct||b.dataset.cd||b.dataset.ch||b.dataset.cr;if(!id)return;if(b.dataset.ma)return patch('monsters',id,{active:!b.classList.contains('on')});if(b.dataset.mally)return patch('monsters',id,{ally:!b.classList.contains('on')});if(b.dataset.mv)return patch('monsters',id,{visible:!b.classList.contains('on')});if(b.dataset.mt)return patch('monsters',id,{in_turn:!b.classList.contains('on')});if(b.dataset.r)return request('/api/combatants/'+id+'/reset',{method:'POST'}).then(load).catch(x=>message(x.message));if(b.dataset.t)return patch('monsters',id,{[b.dataset.f]:!b.textContent.endsWith('on')});if(b.dataset.d){let v=+prompt('Damage to remove:','1');if(Number.isFinite(v))return patch('monsters',id,{hp_delta:-Math.abs(v)})}if(b.dataset.h){let v=+prompt('Healing to add:','1');if(Number.isFinite(v))return patch('monsters',id,{hp_delta:Math.abs(v)})}if(b.dataset.ca)return patch('characters',id,{active:!b.classList.contains('on')});if(b.dataset.cl)return patch('characters',id,{alive:!b.classList.contains('on')});if(b.dataset.cv)return patch('characters',id,{visible:!b.classList.contains('on')});if(b.dataset.ct)return patch('characters',id,{in_turn:!b.classList.contains('on')});if(b.dataset.cd){let v=+prompt('Damage to remove:','1');if(Number.isFinite(v))return patch('characters',id,{hp_delta:-Math.abs(v)})}if(b.dataset.ch){let v=+prompt('Healing to add:','1');if(Number.isFinite(v))return patch('characters',id,{hp_delta:Math.abs(v)})}if(b.dataset.cr)return request('/api/combatants/'+id+'/reset',{method:'POST'}).then(load).catch(x=>message(x.message))});document.addEventListener('change',e=>{if(e.target.dataset.mi&&e.target.value!=='')patch('monsters',e.target.dataset.mi,{initiative:+e.target.value});if(e.target.dataset.ci&&e.target.value!=='')patch('characters',e.target.dataset.ci,{initiative:+e.target.value});if(e.target.dataset.chp&&e.target.value!=='')patch('characters',e.target.dataset.chp,{hp:+e.target.value});if(e.target.dataset.cmaxhp&&e.target.value!=='')patch('characters',e.target.dataset.cmaxhp,{max_hp:+e.target.value})});function living(){return all().filter(x=>x.active&&x.alive)}function initiativeOf(x){return typeof x.initiative==='number'&&Number.isFinite(x.initiative)?x.initiative:null}function initiativeBuckets(){const buckets=new Map();for(const x of living()){const i=initiativeOf(x),key=i===null?'blank':'n:'+i;const bucket=buckets.get(key)||{initiative:i,members:[]};bucket.members.push(x);buckets.set(key,bucket)}return[...buckets.values()].sort((a,b)=>{if(a.initiative===null&&b.initiative===null)return 0;if(a.initiative===null)return 1;if(b.initiative===null)return-1;return b.initiative-a.initiative})}function tiedBuckets(){return initiativeBuckets().filter(bucket=>bucket.initiative!==null&&bucket.members.length>1)}function normalOrder(){return initiativeBuckets().flatMap(bucket=>bucket.members.map(x=>x.id))}function tieUI(){const ties=tiedBuckets();return ties.map((bucket,bucketIndex)=>`<div class="tie-title">Initiative ${bucket.initiative}</div>${bucket.members.map((member,memberIndex)=>`<label class="tie">${esc(member.name)}<select data-tie-bucket="${bucketIndex}" data-tie-member="${member.id}">${bucket.members.map((_,position)=>'<option value="'+(position+1)+'" '+(position===memberIndex?'selected':'')+'>'+ (position+1) +'</option>').join('')}</select></label>`).join('')}`).join('')}function readTieOrder(){const ties=tiedBuckets(),byBucket=[];for(let i=0;i<ties.length;i++){const bucket=ties[i],choices=[...document.querySelectorAll('[data-tie-bucket="'+i+'"]')];if(choices.length!==bucket.members.length)throw new Error('Tie selection data is incomplete');const positions=choices.map(select=>Number(select.value));if(new Set(positions).size!==positions.length)throw new Error('Each combatant in an initiative tie must have a unique position');const map=new Map(choices.map(select=>[select.dataset.tieMember,Number(select.value)]));byBucket.push(bucket.members.slice().sort((a,b)=>map.get(a.id)-map.get(b.id)).map(x=>x.id))}return byBucket}async function startBattle(order){try{await request('/api/battle/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({order})});await load()}catch(e){message(e.message)}}document.querySelector('#startBattle').onclick=()=>{const order=normalOrder();if(!order.length){message('Activate at least one living combatant first');return}if(!tiedBuckets().length){startBattle(order);return}document.querySelector('#tieGroups').innerHTML=tieUI();document.querySelector('#tieModal').hidden=false};document.querySelector('#confirmOrder').onclick=()=>{try{const ties=tiedBuckets(),orderedTies=readTieOrder();let tieIndex=0,order=[];for(const bucket of initiativeBuckets()){if(bucket.initiative!==null&&bucket.members.length>1)order.push(...orderedTies[tieIndex++]);else order.push(...bucket.members.map(x=>x.id))}document.querySelector('#tieModal').hidden=true;startBattle(order)}catch(e){message(e.message)}};document.querySelector('#cancelOrder').onclick=()=>document.querySelector('#tieModal').hidden=true;document.querySelector('#nextBattle').onclick=async()=>{try{await request('/api/battle/next',{method:'POST'});await load()}catch(e){message(e.message)}};document.querySelector('#resetAll').onclick=async()=>{if(!confirm('Reset every monster and character?'))return;try{await request('/api/battle/reset-all',{method:'POST'});await load()}catch(e){message(e.message)}};load();setups();</script></body></html>'''
CLIENT_HTML=r'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Battle Display</title><style>*{box-sizing:border-box}body{margin:0;min-height:100vh;background:#080b14;color:#fff;font-family:system-ui,sans-serif;overflow:hidden}#initiative{height:10vh;min-height:54px;background:#111827e8;display:flex;align-items:center;gap:.6rem;padding:.5rem 1vw;overflow-x:auto;position:relative;z-index:5}.token{white-space:nowrap;border-radius:999px;padding:.45rem .75rem;border:3px solid #fff;font-weight:800;text-shadow:0 1px 2px rgba(0,0,0,.55)}.token.dead{border-color:#000;filter:grayscale(1);opacity:.6}.token.turn{border-color:#ef4444;box-shadow:0 0 15px #ef4444}#stage{height:90vh;position:relative;display:grid;grid-auto-flow:row;gap:.7vh .7vw;padding:.7vh .7vw;overflow:hidden;align-items:stretch;justify-items:stretch;align-content:start}.monster{min-width:0;min-height:0;position:relative;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;padding:1vh 1vw;border-radius:12px;background:linear-gradient(135deg,rgba(0,0,0,.58),rgba(0,0,0,.2));border:2px solid currentColor;box-shadow:0 6px 18px rgba(0,0,0,.45);overflow:hidden;transition:transform .7s ease,opacity .7s ease}.monster img{max-height:53%;max-width:92%;object-fit:contain;border-radius:12px;filter:drop-shadow(0 7px 14px #000)}h1{font-size:clamp(1rem,calc(5vmin / var(--grid-scale,1)),5.7rem);margin:.25rem;text-shadow:0 3px 8px #000;line-height:1.05}.type{font-size:clamp(.75rem,calc(2.1vmin / var(--grid-scale,1)),2.5rem)}.stats{font-size:clamp(.72rem,calc(1.9vmin / var(--grid-scale,1)),2.5rem);margin-top:.45rem}.enter-bottom{transform:translateY(120%);opacity:0}.enter-top{transform:translateY(-120%);opacity:0}.exit-bottom{transform:translateY(120%);opacity:0}.exit-top{transform:translateY(-120%);opacity:0}.empty{height:100%;display:flex;align-items:center;justify-content:center}</style></head><body><div id="initiative"></div><div id="stage"></div><script>let previous=new Map();function esc(v){return String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}function readableText(hex){const z=String(hex||'').replace('#','');if(!/^[0-9a-fA-F]{6}$/.test(z))return'#fff';const r=parseInt(z.slice(0,2),16),g=parseInt(z.slice(2,4),16),b=parseInt(z.slice(4,6),16);return(0.2126*r+0.7152*g+0.0722*b)/255>.55?'#111827':'#fff'}function ent(d){return d.entry_direction==='from_top'?'enter-top':'enter-bottom'}function ext(d){return d.exit_direction==='to_top'?'exit-top':'exit-bottom'}function gridSize(n){if(n<=1)return[1,1];let rows=1,cols=1;while(rows*cols<n){if(cols===rows)cols++;else rows++}return[rows,cols]}function render(s){document.body.style.background=s.display.background;const map=new Map([...s.characters,...s.monsters].map(x=>[x.id,x]));const ordered=s.battle_order.map(id=>map.get(id)).filter(Boolean);const extras=[...map.values()].filter(x=>x.active&&x.visible&&!ordered.some(y=>y.id===x.id)).sort((a,b)=>(b.initiative??-999)-(a.initiative??-999));const bar=[...ordered.filter(x=>x.visible),...extras];document.querySelector('#initiative').innerHTML=bar.map(x=>`<span class="token ${x.alive?'':'dead'} ${x.in_turn?'turn':''}" style="background:${esc(x.color)};color:${readableText(x.color)}">${esc(x.name)}</span>`).join('');const active=s.monsters.filter(x=>x.active&&x.alive),stage=document.querySelector('#stage');if(!active.length){stage.style.gridTemplateColumns='';stage.style.gridTemplateRows='';stage.innerHTML='<div class="empty"></div>';previous.clear();return}const[rows,cols]=gridSize(active.length);stage.style.gridAutoFlow='row';stage.style.gridTemplateColumns=`repeat(${cols},minmax(0,1fr))`;stage.style.gridTemplateRows=`repeat(${rows},minmax(0,1fr))`;stage.style.setProperty('--grid-scale',String(Math.max(rows,cols)));const now=new Map(active.map(x=>[x.id,x]));for(const[id]of previous)if(!now.has(id)){const old=document.getElementById('m-'+id);if(old){old.classList.add(ext(s.display));setTimeout(()=>old.remove(),750)}}active.forEach((m,index)=>{let e=document.getElementById('m-'+m.id);if(!e){e=document.createElement('article');e.id='m-'+m.id;e.className='monster '+ent(s.display);stage.appendChild(e);requestAnimationFrame(()=>e.classList.remove('enter-bottom','enter-top'))}const row=Math.floor(index/cols)+1,col=(index%cols)+1;e.style.gridRow=String(row);e.style.gridColumn=String(col);e.style.color=m.color;const st=[];if(m.show_ac)st.push('AC '+m.ac);if(m.show_hp)st.push('HP '+m.hp+'/'+m.max_hp);if(m.show_initiative&&m.initiative!==null)st.push('Initiative '+m.initiative);e.innerHTML=`${m.image_url?'<img src="'+esc(m.image_url)+'" alt="">':''}<h1>${esc(m.name)}${m.in_turn?' ◀':''}</h1><div class="type">${esc(m.monster_type)}</div><div class="stats">${st.join(' · ')}</div>`});previous=now}async function initial(){const r=await fetch('/api/state');if(r.ok)render(await r.json())}initial();const ws=new WebSocket((location.protocol==='https:'?'wss://':'ws://')+location.host+'/ws');ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.type==='state')render(m.state)};ws.onclose=()=>setTimeout(()=>location.reload(),1500);</script></body></html>'''

@admin.get('/login')
def admin_login_get():return login()
@admin.post('/login')
def admin_login_post(username:str=Form(...),password:str=Form(...)):
    u=user(username)
    if not u or u.get('role')!='admin' or not password_ok(password,str(u.get('password',''))):return login('Invalid admin credentials')
    token=secrets.token_urlsafe(32);SESSIONS[token]={'username':username,'role':'admin'};r=RedirectResponse('/',303);r.set_cookie('monster_session',token,httponly=True,samesite='lax',secure=False);return r
@admin.get('/')
def admin_home(request:FastAPIRequest):return HTMLResponse(ADMIN_HTML)if SESSIONS.get(request.cookies.get('monster_session',''),{}).get('role')=='admin' else RedirectResponse('/login',303)
@client.get('/login')
def client_login_get():return login()
@client.post('/login')
def client_login_post(username:str=Form(...),password:str=Form(...)):
    u=user(username)
    if not u or u.get('role')not in{'admin','client'}or not password_ok(password,str(u.get('password',''))):return login('Invalid credentials')
    token=secrets.token_urlsafe(32);SESSIONS[token]={'username':username,'role':u['role']};r=RedirectResponse('/display',303);r.set_cookie('monster_session',token,httponly=True,samesite='lax',secure=False);return r
@client.get('/display')
def client_home(request:FastAPIRequest):return HTMLResponse(CLIENT_HTML)if SESSIONS.get(request.cookies.get('monster_session',''))else RedirectResponse('/login',303)
@admin.get('/api/state')
@client.get('/api/state')
def get_state(request:FastAPIRequest):
    if not SESSIONS.get(request.cookies.get('monster_session','')):raise HTTPException(401,'Sign in required')
    return public_state()
@client.websocket('/ws')
async def ws(websocket:WebSocket):
    await websocket.accept();SOCKETS.add(websocket);await websocket.send_text(json.dumps({'type':'state','state':public_state()}))
    try:
        while True:await websocket.receive_text()
    except Exception:SOCKETS.discard(websocket)
@admin.get('/api/setups')
def get_setups(_:dict[str,str]=Depends(require('admin'))):return{'names':list_setups()}
@admin.post('/api/setups/new')
async def new_setup(_:dict[str,str]=Depends(require('admin'))):
    global STATE
    STATE=normalize_state({'monsters':[],'characters':[],'battle_order':[]});await changed();return public_state()
@admin.post('/api/setups/save')
async def save_setup(payload:SetupName,_:dict[str,str]=Depends(require('admin'))):
    name=setup_slug(payload.name);path=setup_path(name);temp=path.with_suffix('.tmp');temp.write_text(json.dumps(STATE,indent=2),encoding='utf-8');temp.replace(path);return{'name':name}
@admin.post('/api/setups/load')
async def load_setup(payload:SetupName,_:dict[str,str]=Depends(require('admin'))):
    global STATE
    name=setup_slug(payload.name);path=setup_path(name)
    if not path.exists():raise HTTPException(404,'Saved setup not found')
    try:STATE=normalize_state(json.loads(path.read_text(encoding='utf-8')))
    except(OSError,json.JSONDecodeError,ValueError)as exc:raise HTTPException(400,f'Unable to load setup: {exc}')from exc
    await changed();return{'name':name}
@admin.post('/api/setups/import')
async def import_setup(payload:SetupImport,_:dict[str,str]=Depends(require('admin'))):
    name=setup_slug(payload.name);path=setup_path(name)
    if not path.exists():raise HTTPException(404,'Saved setup not found')
    try:source=normalize_state(json.loads(path.read_text(encoding='utf-8')))
    except(OSError,json.JSONDecodeError,ValueError)as exc:raise HTTPException(400,f'Unable to read setup: {exc}')from exc
    imported_characters=[];imported_monsters=[]
    if payload.kind in {'characters','both'}:imported_characters=[reset_imported_character(item)for item in source['characters']]
    if payload.kind in {'monsters','both'}:imported_monsters=[reset_imported_monster(item)for item in source['monsters']]
    STATE['characters'].extend(imported_characters);STATE['monsters'].extend(imported_monsters);await changed();return{'name':name,'characters':len(imported_characters),'monsters':len(imported_monsters)}
@admin.post('/api/monsters/roll-initiative')
async def roll_monster_initiative(_:dict[str,str]=Depends(require('admin'))):
    for monster in STATE['monsters']:monster['initiative']=random.randint(1,20)
    await changed();return{'count':len(STATE['monsters'])}
@admin.post('/api/monsters')
async def create_monster(name:str=Form(...),monster_type:str=Form(...),ac:int=Form(...),hp:int=Form(...),color:str=Form(...),quantity:int=Form(1,ge=1,le=50),image:UploadFile|None=File(None),_:dict[str,str]=Depends(require('admin'))):
    fields={'name':name.strip(),'monster_type':monster_type.strip(),'ac':ac,'hp':hp};image_url=save_image(image)if image and image.filename else dnd_image(fields['monster_type']);created=[make_monster(fields,color,None,image_url)for _ in range(quantity)];STATE['monsters'].extend(created);await changed();return created
@admin.post('/api/monsters/import')
async def import_monster(monster_file:UploadFile=File(...),color:str=Form(...),quantity:int=Form(1,ge=1,le=50),image:UploadFile|None=File(None),_:dict[str,str]=Depends(require('admin'))):
    if not(monster_file.filename or '').lower().endswith('.monster'):raise HTTPException(400,'Upload a .monster file')
    fields=parse_monster(await monster_file.read());image_url=save_image(image)if image and image.filename else dnd_image(fields['monster_type']);created=[make_monster(fields,color,None,image_url)for _ in range(quantity)];STATE['monsters'].extend(created);await changed();return created
@admin.post('/api/monsters/{ident}/edit')
async def edit_monster(ident:str,name:str=Form(...),monster_type:str=Form(...),ac:int=Form(...),hp:int=Form(...),max_hp:int=Form(...),original_hp:int=Form(...),color:str=Form(...),initiative:str=Form(""),ally:str=Form("false"),image:UploadFile|None=File(None),_:dict[str,str]=Depends(require('admin'))):
    m=next((x for x in STATE['monsters']if x['id']==ident),None)
    if not m:raise HTTPException(404,'Monster not found')
    parsed_initiative=None if initiative.strip()=='' else int(initiative)
    if parsed_initiative is not None and not -100<=parsed_initiative<=100:raise HTTPException(400,'Initiative must be between -100 and 100')
    m.update({'name':name.strip(),'monster_type':monster_type.strip(),'ac':ac,'hp':hp,'max_hp':max_hp,'original_hp':original_hp,'color':color,'initiative':parsed_initiative,'ally':ally.lower()=='true'})
    if image and image.filename:m['image_url']=save_image(image)
    if m['hp']<0:m['alive']=False;m['visible']=True;m['in_turn']=False
    clean_order();await changed();return m
@admin.patch('/api/monsters/{ident}')
async def update_monster(ident:str,update:MonsterUpdate,_:dict[str,str]=Depends(require('admin'))):
    m=next((x for x in STATE['monsters']if x['id']==ident),None)
    if not m:raise HTTPException(404,'Monster not found')
    values=update.model_dump(exclude_unset=True,exclude_none=True)
    if'hp_delta'in values:m['hp']+=values.pop('hp_delta')
    for k,v in values.items():
        if k!='in_turn':m[k]=v
    if values.get("active") is True:
        insert_into_battle_order(m)
    if m['hp']<0:m['alive']=False;m['visible']=True;m['in_turn']=False
    if values.get('active')is False:m['in_turn']=False
    set_turn(m,values.get('in_turn'));clean_order();await changed();return m
@admin.post('/api/characters')
async def create_character(character:CharacterCreate,_:dict[str,str]=Depends(require('admin'))):
    c={'id':uuid.uuid4().hex,**character.model_dump(),'max_hp':character.hp,'original_hp':character.hp,'original_initiative':character.initiative,'active':False,'alive':character.hp>=0,'visible':False,'in_turn':False};STATE['characters'].append(c);await changed();return c
@admin.patch('/api/characters/{ident}')
async def update_character(ident:str,update:CharacterUpdate,_:dict[str,str]=Depends(require('admin'))):
    c=next((x for x in STATE['characters']if x['id']==ident),None)
    if not c:raise HTTPException(404,'Character not found')
    values=update.model_dump(exclude_unset=True,exclude_none=True)
    if'hp_delta'in values:c['hp']+=values.pop('hp_delta')
    if'max_hp'in values:c['original_hp']=values['max_hp']
    for k,v in values.items():
        if k!='in_turn':c[k]=v
    if values.get("active") is True:
        insert_into_battle_order(c)
    if c['hp']<0:c['alive']=False;c['visible']=True;c['in_turn']=False
    if values.get('alive')is False:c['visible']=True;c['in_turn']=False
    if values.get('active')is False:c['in_turn']=False
    set_turn(c,values.get('in_turn'));clean_order();await changed();return c
@admin.post('/api/combatants/{ident}/reset')
async def reset_one(ident:str,_:dict[str,str]=Depends(require('admin'))):
    x=entity(ident)
    if not x:raise HTTPException(404,'Combatant not found')
    reset_entity(x);clean_order();await changed();return x
@admin.post('/api/battle/reset-all')
async def reset_all(_:dict[str,str]=Depends(require('admin'))):
    for x in entities():reset_entity(x)
    sort_admin_by_max_hp();STATE['battle_order']=[];await changed();return{'status':'reset'}
@admin.post('/api/battle/start')
async def battle_start(payload:BattleStart,_:dict[str,str]=Depends(require('admin'))):begin_battle(payload.order);sort_admin_by_initiative();await changed();return public_state()
@admin.post('/api/battle/next')
async def battle_next(_:dict[str,str]=Depends(require('admin'))):x=advance_turn();await changed();return{'current':x}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='GM-controlled real-time battle display');parser.add_argument('--config',type=Path);parser.add_argument('--bind');parser.add_argument('--admin-port',type=int);parser.add_argument('--client-port',type=int);parser.add_argument('--storage-dir',type=Path);args=parser.parse_args()
    try:CONFIG=load_config(args.config)
    except Exception as exc:sys.exit(f'Invalid configuration: {exc}')
    if args.bind:CONFIG['network']['bind']=args.bind
    if args.admin_port:CONFIG['network']['admin_port']=args.admin_port
    if args.client_port:CONFIG['network']['client_port']=args.client_port
    if args.storage_dir:CONFIG['storage_dir']=str(args.storage_dir)
    DATA_DIR=Path(CONFIG['storage_dir']).expanduser().resolve();UPLOAD_DIR=DATA_DIR/'uploads';SETUPS_DIR=DATA_DIR/'setups';UPLOAD_DIR.mkdir(parents=True,exist_ok=True);SETUPS_DIR.mkdir(parents=True,exist_ok=True);STATE_FILE=DATA_DIR/'state.json';load_state();admin.mount('/media',StaticFiles(directory=str(UPLOAD_DIR)),name='admin-media');client.mount('/media',StaticFiles(directory=str(UPLOAD_DIR)),name='client-media')
    async def serve():
        common={'host':CONFIG['network']['bind'],'log_level':'info','access_log':False};await asyncio.gather(uvicorn.Server(uvicorn.Config(admin,port=CONFIG['network']['admin_port'],**common)).serve(),uvicorn.Server(uvicorn.Config(client,port=CONFIG['network']['client_port'],**common)).serve())
    asyncio.run(serve())
