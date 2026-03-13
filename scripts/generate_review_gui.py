#!/usr/bin/env python3
"""Generate self-contained review GUI HTML for Phase D results."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PHASE_D_DIR = PROJECT_ROOT / "tests" / "results" / "source_engine" / "phase_d"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def get_version() -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        return r.stdout.strip() if r.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def collect_books() -> list[dict[str, Any]]:
    books: list[dict[str, Any]] = []
    for d in sorted(PHASE_D_DIR.iterdir()):
        if not d.is_dir() or not (d / "result.json").exists():
            continue
        res = load_json(d / "result.json")
        ext = load_json(d / "extraction.json") if (d / "extraction.json").exists() else {}
        cons = load_json(d / "consensus.json") if (d / "consensus.json").exists() else {}

        llm: dict[str, Any] = {}
        llm_dir = d / "llm_responses"
        if llm_dir.exists():
            for f in sorted(llm_dir.iterdir()):
                if f.suffix == ".json":
                    try:
                        md = load_json(f)
                        if md.get("parsed"):
                            llm[f.stem] = md["parsed"]
                    except Exception:
                        pass

        status = res.get("status", "unknown")
        author = res.get("author") or {}
        if not isinstance(author, dict):
            author = {}
        muhaqiq = res.get("muhaqiq")
        if muhaqiq and not isinstance(muhaqiq, dict):
            muhaqiq = None

        book: dict[str, Any] = {
            "id": d.name,
            "status": status,
            "is_rerun": res.get("is_rerun", False),
            "original_phase": res.get("original_phase"),
            "ext": {
                "title_full": ext.get("title_full") or ext.get("display_title", ""),
                "display_title": ext.get("display_title", ""),
                "author_name_raw": ext.get("author_name_raw", ""),
                "author_short": ext.get("author_short", ""),
                "muhaqiq_name_raw": ext.get("muhaqiq_name_raw", ""),
                "publisher": ext.get("publisher", ""),
                "shamela_category": ext.get("shamela_category", ""),
                "page_count": ext.get("page_count") or ext.get("page_count_raw"),
                "volume_count": ext.get("volume_count", 1),
                "author_death_hijri": ext.get("author_death_hijri"),
                "edition_raw": ext.get("edition_raw", ""),
            },
            "cons": {
                "agreed": cons.get("agreed", True),
                "canonical_model": cons.get("canonical_result_model", ""),
                "needs_human_gate": cons.get("needs_human_gate", False),
                "human_gate_trigger": cons.get("human_gate_trigger"),
            },
            "llm": llm,
        }

        if status == "success":
            book["meta"] = {
                "source_id": res.get("source_id", ""),
                "work_id": res.get("work_id", ""),
                "title_arabic": res.get("title_arabic", ""),
                "author": {
                    "canonical_id": author.get("canonical_id", ""),
                    "name_arabic": author.get("name_arabic", ""),
                    "confidence": author.get("confidence"),
                    "source_of_identification": author.get("source_of_identification", ""),
                },
                "muhaqiq": {
                    "canonical_id": muhaqiq.get("canonical_id", ""),
                    "name_arabic": muhaqiq.get("name_arabic", ""),
                    "confidence": muhaqiq.get("confidence"),
                } if muhaqiq else None,
                "genre": res.get("genre", ""),
                "science_scope": res.get("science_scope", []),
                "is_multi_layer": res.get("is_multi_layer"),
                "text_layers": res.get("text_layers", []),
                "trust_tier": res.get("trust_tier", ""),
                "trust_score": res.get("trust_score"),
                "trust_factors": res.get("trust_factors", []),
                "confidence_scores": res.get("confidence_scores", {}),
                "needs_review_fields": res.get("needs_review_fields", []),
                "attribution_status": res.get("attribution_status", ""),
                "authority_level": res.get("authority_level", ""),
                "structural_format": res.get("structural_format", ""),
                "publisher": res.get("publisher", ""),
                "page_count": res.get("page_count"),
                "volume_count": res.get("volume_count"),
                "level": res.get("level", ""),
            }
        else:
            book["error"] = {
                "code": res.get("error_code", ""),
                "message": res.get("error_message", ""),
                "gate_errors": res.get("gate_errors", []),
            }

        books.append(book)
    return books


def generate_html(books: list[dict], version: str) -> str:
    data_json = json.dumps(books, ensure_ascii=False, separators=(",", ":"))
    return (
        HTML_TEMPLATE
        .replace("/*__DATA__*/[]", data_json)
        .replace("__VERSION__", version)
    )


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>KR Source Engine — Step 4 Review</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&family=Amiri:wght@400;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#0c0a09;--card:#1c1917;--field:#0a0908;--text:#e7e5e4;--dim:#a8a29e;--green:#4ade80;--yellow:#fbbf24;--red:#f87171;--gold:#d4a853;--border:#292524}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:'IBM Plex Sans',sans-serif;font-size:14px;line-height:1.5}
h1{font-size:1.4em;font-weight:700}h2{font-size:1.15em;font-weight:600;margin:14px 0 6px}h3{font-size:1em;font-weight:600;margin:10px 0 4px}
.ar{font-family:'Amiri',serif;direction:rtl;unicode-bidi:embed}
.mo{font-family:'IBM Plex Mono',monospace;font-size:.85em}
.green{color:var(--green)}.yellow{color:var(--yellow)}.red{color:var(--red)}.gold{color:var(--gold)}.dim{color:var(--dim)}
.view{display:none;padding:18px 22px;max-width:1600px;margin:0 auto}.view.active{display:block}
.card{background:var(--card);border-radius:8px;padding:14px;border:1px solid var(--border);margin:6px 0}
.fr{background:var(--field);padding:5px 9px;border-radius:4px;margin:2px 0;display:flex;justify-content:space-between;align-items:center;gap:6px}
.fl{color:var(--dim);font-size:.78em;white-space:nowrap;min-width:70px}.fv{flex:1;text-align:right}
.badge{display:inline-block;padding:1px 7px;border-radius:4px;font-size:.73em;font-weight:500}
.bs{background:rgba(74,222,128,.1);color:var(--green);border:1px solid rgba(74,222,128,.25)}
.bg{background:rgba(248,113,113,.1);color:var(--red);border:1px solid rgba(248,113,113,.25)}
.bw{background:rgba(251,191,36,.1);color:var(--yellow);border:1px solid rgba(251,191,36,.25)}
.bgold{background:rgba(212,168,83,.1);color:var(--gold);border:1px solid rgba(212,168,83,.25)}
.sg{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px;margin:12px 0}
.sc{background:var(--card);border-radius:8px;padding:12px;text-align:center;border:1px solid var(--border)}
.sv{font-size:1.7em;font-weight:700}.sl{color:var(--dim);font-size:.78em;margin-top:2px}
.dr{display:flex;align-items:center;margin:2px 0}
.dl{width:170px;font-size:.78em;text-align:right;padding-right:8px;color:var(--dim);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dt{flex:1;height:16px;background:var(--field);border-radius:3px;overflow:hidden}
.df{height:100%;border-radius:3px;min-width:2px}.dc{width:32px;text-align:right;font-size:.73em;color:var(--dim);margin-left:5px;font-family:'IBM Plex Mono',monospace}
.rc{display:grid;grid-template-columns:1fr 1.4fr 1fr;gap:12px;margin:10px 0}
.ch{font-weight:600;margin-bottom:8px;padding-bottom:5px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
.mm{background:rgba(251,191,36,.12)!important}
.tb{display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid var(--border);margin-bottom:10px;flex-wrap:wrap}
.btn{padding:5px 12px;border-radius:5px;border:1px solid var(--border);background:var(--card);color:var(--text);cursor:pointer;font-size:.83em;font-family:inherit}
.btn:hover{border-color:var(--dim)}.btn.pri{background:var(--gold);color:var(--bg);border-color:var(--gold);font-weight:600}
.vbs{display:flex;gap:5px;margin:6px 0}
.vb{padding:5px 14px;border-radius:5px;border:2px solid var(--border);background:transparent;color:var(--dim);cursor:pointer;font-size:.83em;font-family:inherit;transition:all .15s}
.vb:hover{border-color:var(--dim);color:var(--text)}
.vb.vc{border-color:var(--green);color:var(--green);background:rgba(74,222,128,.08)}
.vb.vw{border-color:var(--red);color:var(--red);background:rgba(248,113,113,.08)}
.vb.vu{border-color:var(--yellow);color:var(--yellow);background:rgba(251,191,36,.08)}
.it{display:flex;flex-wrap:wrap;gap:4px;margin:5px 0}
.ig{padding:2px 7px;border-radius:3px;border:1px solid var(--border);background:var(--field);color:var(--dim);cursor:pointer;font-size:.73em;transition:all .15s}
.ig.active{background:rgba(248,113,113,.12);border-color:var(--red);color:var(--red)}
.cr{margin:5px 0}.cr label{display:block;font-size:.78em;color:var(--dim);margin-bottom:2px}
.cr input,.cr select,.cr textarea{width:100%;padding:5px 7px;background:var(--field);border:1px solid var(--border);border-radius:4px;color:var(--text);font-family:inherit;font-size:.83em}
.cr .ai{font-family:'Amiri',serif;direction:rtl}.cr textarea{min-height:50px;resize:vertical}
.fb{display:flex;gap:5px;flex-wrap:wrap;margin:6px 0}
.fbtn{padding:2px 9px;border-radius:4px;border:1px solid var(--border);background:var(--card);color:var(--dim);cursor:pointer;font-size:.78em}
.fbtn.active{border-color:var(--gold);color:var(--gold)}
.sr{display:flex;gap:6px;margin:6px 0;align-items:center}
.si{flex:1;padding:5px 9px;background:var(--field);border:1px solid var(--border);border-radius:5px;color:var(--text);font-family:'IBM Plex Sans','Amiri',sans-serif;font-size:.88em}
.ss{padding:5px 7px;background:var(--field);border:1px solid var(--border);border-radius:5px;color:var(--text);font-family:inherit;font-size:.83em}
.bl{margin-top:8px}
.br{display:grid;grid-template-columns:34px 66px 1fr 95px 65px 42px 36px;align-items:center;gap:5px;padding:7px 9px;background:var(--card);border-radius:5px;cursor:pointer;border:1px solid var(--border);margin:3px 0;font-size:.83em}
.br:hover{border-color:var(--dim)}
.cd{width:9px;height:9px;border-radius:50%;display:inline-block}
.fp{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:12px;margin-top:10px}
.na{width:100%;padding:5px 7px;background:var(--field);border:1px solid var(--border);border-radius:4px;color:var(--text);font-family:inherit;min-height:44px;resize:vertical;margin-top:4px;font-size:.83em}
.js{padding:3px 7px;background:var(--field);border:1px solid var(--border);border-radius:4px;color:var(--text);font-family:inherit;max-width:280px;font-size:.83em}
.ki{border-color:var(--yellow)!important;margin:10px 0}.ki p{color:var(--dim);margin:4px 0;font-size:.88em}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.flash{animation:fl .4s}@keyframes fl{0%{opacity:1}50%{opacity:.3}100%{opacity:1}}
@media(max-width:1200px){.rc{grid-template-columns:1fr}}@media(max-width:900px){.g2{grid-template-columns:1fr}}
</style></head><body>

<div id="vd" class="view active">
<div class="tb"><h1>KR Source Engine — Step 4 Review</h1><span class="mo" id="di"></span><div style="flex:1"></div>
<button class="btn pri" onclick="sv('vr')">Review Queue</button><button class="btn" onclick="sv('vl')">List View</button><button class="btn" onclick="doExport()">Export</button></div>
<div class="sg" id="ds"></div>
<div class="card ki" id="ki"></div>
<div class="g2"><div class="card"><h3>Genre Distribution</h3><div id="dg"></div></div><div class="card"><h3>Trust Tier</h3><div id="dtr"></div></div></div>
<div class="g2"><div class="card"><h3>Shamela Category</h3><div id="dca"></div></div><div class="card"><h3>Confidence Histogram</h3><div id="dco"></div></div></div>
<div class="card"><h3>Model Agreement</h3><div id="dag"></div></div>
</div>

<div id="vr" class="view">
<div class="tb" id="rtb"></div>
<div id="rc"></div>
<div id="rfb"></div>
</div>

<div id="vl" class="view">
<div class="tb"><h1>Book List</h1><div style="flex:1"></div><button class="btn" onclick="sv('vd')">Dashboard</button><button class="btn pri" onclick="sv('vr')">Review Queue</button><button class="btn" onclick="doExport()">Export</button></div>
<div class="sr"><input class="si" type="text" placeholder="Search by title or author..." oninput="oSrch(this.value)" id="sb">
<select class="ss" onchange="oSrt(this.value)" id="ssel"><option value="priority">Sort: Priority</option><option value="confidence">Sort: Confidence</option><option value="alpha">Sort: Alphabetical</option><option value="category">Sort: Category</option><option value="trust">Sort: Trust Score</option></select></div>
<div class="fb" id="lf"></div>
<div id="lc" class="bl"></div>
</div>

<script>
const D=/*__DATA__*/[];
const GN=['matn','sharh','hashiyah','mukhtasar','nazm','risalah','taqrirat','mawsuah','fatawa','mujam','tabaqat','fiqh_comparative','hadith_collection','tafsir','sirah','tarikh','adab','other'];
const TT=['verified','flagged','owner_override'];
const AT=['definitive','traditional','disputed','unknown'];
const MN={command_a:'Command A',claude_opus_4_6:'Claude Opus 4.6'};
const IS=['Author','Genre','Multi-layer','Sciences','Attribution','Trust','Muhaqiq','Layers','Missing data','Death date','School','Other'];
const VER='__VERSION__';

let vw='vd',ri=0,flt='all',srt='priority',sq='';
let sb=[];
let fb={};try{fb=JSON.parse(localStorage.getItem('kr_phase_d_feedback')||'{}');}catch(e){fb={};}

function h(s){return s==null?'':String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');}
function mn(k){return MN[k]||k.replace(/_/g,' ');}
function cc(v){if(v==null)return'var(--dim)';if(v>=.85)return'var(--green)';if(v>=.7)return'var(--yellow)';return'var(--red)';}
function cdot(v){return'<span class="cd" style="background:'+cc(v)+'" title="'+(v!=null?v.toFixed(2):'N/A')+'"></span>';}
function bfor(s){return s==='success'?'<span class="badge bs">SUCCESS</span>':s==='gate_abort'?'<span class="badge bg">GATE ABORT</span>':'<span class="badge bw">'+h(s)+'</span>';}
function ve(v){return v==='correct'?'✅':v==='wrong'?'❌':v==='unsure'?'❓':'';}
function ar(t){return t?'<span class="ar">'+h(t)+'</span>':'–';}
function mo(t){return t!=null?'<span class="mo">'+h(String(t))+'</span>':'–';}
function fr(l,v,a){return'<div class="fr"><span class="fl">'+h(l)+'</span><span class="fv">'+(a?ar(v):mo(v))+'</span></div>';}
function gmc(b){if(!b.meta||!b.meta.confidence_scores)return 1;const v=Object.values(b.meta.confidence_scores).filter(x=>typeof x==='number');return v.length?Math.min(...v):1;}

function psort(a){return[...a].sort((a,b)=>{
const ad=!a.cons.agreed,bd=!b.cons.agreed;if(ad!==bd)return ad?-1:1;
const ac=gmc(a),bc=gmc(b);if((ac<.85)!==(bc<.85))return ac<.85?-1:1;
if(a.status!==b.status){if(a.status==='gate_abort')return-1;if(b.status==='gate_abort')return 1;}
return a.id.localeCompare(b.id,'ar');});}

function sortB(a,m){switch(m){
case'confidence':return[...a].sort((a,b)=>gmc(a)-gmc(b));
case'alpha':return[...a].sort((a,b)=>a.id.localeCompare(b.id,'ar'));
case'category':return[...a].sort((a,b)=>(a.ext.shamela_category||'').localeCompare(b.ext.shamela_category||'','ar'));
case'trust':return[...a].sort((a,b)=>(a.meta?.trust_score||0)-(b.meta?.trust_score||0));
default:return psort(a);}}

function fltB(a,f){switch(f){
case'success':return a.filter(b=>b.status==='success');
case'gate_abort':return a.filter(b=>b.status==='gate_abort');
case'disagreements':return a.filter(b=>!b.cons.agreed);
case'flagged':return a.filter(b=>b.meta&&b.meta.trust_tier==='flagged');
case'unreviewed':return a.filter(b=>!fb[b.id]||!fb[b.id].verdict);
case'reruns':return a.filter(b=>b.is_rerun);
case'new':return a.filter(b=>!b.is_rerun);
default:return a;}}

function srchB(a,q){if(!q)return a;return a.filter(b=>b.id.includes(q)||(b.ext.title_full||'').includes(q)||(b.ext.author_name_raw||'').includes(q)||(b.meta?.author?.name_arabic||'').includes(q));}
function gfs(){return sortB(fltB(srchB(D,sq),flt),srt);}

function sfb(){localStorage.setItem('kr_phase_d_feedback',JSON.stringify(fb));}
function gfb(id){if(!fb[id])fb[id]={verdict:null,issues:[],corrections:{},notes:'',timestamp:null};return fb[id];}

function doV(v){const b=sb[ri];if(!b)return;const f=gfb(b.id);f.verdict=f.verdict===v?null:v;f.timestamp=new Date().toISOString();sfb();rR();
if(f.verdict){const el=document.getElementById('rc');if(el)el.classList.add('flash');setTimeout(()=>{el&&el.classList.remove('flash');nxu();},500);}}
function doTI(iss){const b=sb[ri];if(!b)return;const f=gfb(b.id);const i=f.issues.indexOf(iss);if(i>=0){f.issues.splice(i,1);delete f.corrections[iss];}else f.issues.push(iss);sfb();rR();}
function doUC(iss,val){const b=sb[ri];if(!b)return;gfb(b.id).corrections[iss]=val;sfb();}
function doUN(val){const b=sb[ri];if(!b)return;gfb(b.id).notes=val;sfb();}

function sv(v){vw=v;document.querySelectorAll('.view').forEach(e=>e.classList.remove('active'));document.getElementById(v).classList.add('active');
if(v==='vd')rD();else if(v==='vr'){sb=psort(D);rR();}else if(v==='vl')rL();}
function nx(){if(ri<sb.length-1){ri++;rR();}}
function pv(){if(ri>0){ri--;rR();}}
function jt(i){ri=Math.max(0,Math.min(i,sb.length-1));rR();}
function nxu(){for(let i=ri+1;i<sb.length;i++){if(!fb[sb[i].id]||!fb[sb[i].id].verdict){ri=i;rR();return;}}
for(let i=0;i<ri;i++){if(!fb[sb[i].id]||!fb[sb[i].id].verdict){ri=i;rR();return;}}nx();}
function oir(di){sb=psort(D);const idx=sb.findIndex(b=>b===D[di]);if(idx>=0)ri=idx;sv('vr');}

function cntBy(a,fn){const m={};a.forEach(b=>{const k=fn(b)||'unknown';m[k]=(m[k]||0)+1;});return Object.entries(m).sort((a,b)=>b[1]-a[1]);}
function rDist(id,entries,col,isAr){const mx=entries.length?Math.max(...entries.map(e=>e[1])):1;
document.getElementById(id).innerHTML=entries.map(([k,v])=>'<div class="dr"><span class="dl'+(isAr?' ar':'')+'">'+h(k)+'</span><div class="dt"><div class="df" style="width:'+(v/mx*100).toFixed(1)+'%;background:'+col+'"></div></div><span class="dc">'+v+'</span></div>').join('');}

function rD(){
const t=D.length,su=D.filter(b=>b.status==='success').length,ga=D.filter(b=>b.status==='gate_abort').length;
const dis=D.filter(b=>!b.cons.agreed).length,re=D.filter(b=>b.is_rerun).length;
const rv=D.filter(b=>fb[b.id]&&fb[b.id].verdict).length;
document.getElementById('di').textContent=t+' books · Pipeline '+VER+' · '+new Date().toLocaleDateString();
document.getElementById('ds').innerHTML=
'<div class="sc"><div class="sv">'+t+'</div><div class="sl">Total</div></div>'+
'<div class="sc"><div class="sv green">'+su+'</div><div class="sl">Success</div></div>'+
'<div class="sc"><div class="sv red">'+ga+'</div><div class="sl">Gate Abort</div></div>'+
'<div class="sc"><div class="sv yellow">'+dis+'</div><div class="sl">Disagreements</div></div>'+
'<div class="sc"><div class="sv">'+re+'</div><div class="sl">Reruns</div></div>'+
'<div class="sc"><div class="sv gold">'+rv+'/'+t+'</div><div class="sl">Reviewed</div></div>';
document.getElementById('ki').innerHTML='<strong class="yellow">Known Issues</strong><p>51 Phase C books gated by BUG-01 (author-science mismatch) — fixed in current pipeline, now rerun.</p><button class="btn" style="margin-top:6px" onclick="bAck()">Acknowledge all '+re+' reruns</button>';
rDist('dg',cntBy(D.filter(b=>b.status==='success'),b=>b.meta?.genre),'var(--green)');
rDist('dtr',cntBy(D.filter(b=>b.status==='success'),b=>b.meta?.trust_tier),'var(--gold)');
rDist('dca',cntBy(D,b=>b.ext.shamela_category),'var(--yellow)',true);
const bk={'<0.70':0,'0.70-0.80':0,'0.80-0.90':0,'0.90-1.00':0};
D.filter(b=>b.status==='success').forEach(b=>{const c=gmc(b);if(c<.7)bk['<0.70']++;else if(c<.8)bk['0.70-0.80']++;else if(c<.9)bk['0.80-0.90']++;else bk['0.90-1.00']++;});
const be=Object.entries(bk),cl=['var(--red)','var(--yellow)','var(--green)','var(--green)'],bmx=Math.max(...be.map(e=>e[1]),1);
document.getElementById('dco').innerHTML=be.map(([k,v],i)=>'<div class="dr"><span class="dl mo">'+k+'</span><div class="dt"><div class="df" style="width:'+(v/bmx*100).toFixed(1)+'%;background:'+cl[i]+'"></div></div><span class="dc">'+v+'</span></div>').join('');
const ag=D.filter(b=>b.cons.agreed).length,dg=D.length-ag,pct=(ag/Math.max(D.length,1)*100).toFixed(1);
document.getElementById('dag').innerHTML='<div class="dr"><span class="dl">Agreed</span><div class="dt"><div class="df" style="width:'+pct+'%;background:var(--green)"></div></div><span class="dc">'+ag+'</span></div><div class="dr"><span class="dl">Disagreed</span><div class="dt"><div class="df" style="width:'+(100-parseFloat(pct)).toFixed(1)+'%;background:var(--red)"></div></div><span class="dc">'+dg+'</span></div><div style="margin-top:6px;font-size:.83em;color:var(--dim)">Agreement rate: '+pct+'%</div>';}

function bAck(){D.filter(b=>b.is_rerun).forEach(b=>{const f=gfb(b.id);if(!f.verdict){f.verdict='correct';f.notes='Bulk acknowledged — rerun check only';f.timestamp=new Date().toISOString();}});sfb();rD();}

function rR(){
if(!sb.length)return;const b=sb[ri],f=gfb(b.id);
const opts=sb.map((x,i)=>'<option value="'+i+'"'+(i===ri?' selected':'')+'>'+h((i+1)+'. '+x.id)+'</option>').join('');
document.getElementById('rtb').innerHTML=
'<button class="btn" onclick="sv(\'vd\')">Dashboard</button>'+
'<button class="btn" onclick="sv(\'vl\')">List</button>'+
'<button class="btn" onclick="pv()">&#8592; Prev</button>'+
'<span class="mo">'+(ri+1)+' / '+sb.length+'</span>'+
'<button class="btn" onclick="nx()">Next &#8594;</button>'+
'<select class="js" onchange="jt(parseInt(this.value))">'+opts+'</select>'+
'<div style="flex:1"></div>'+
'<span style="font-size:1.2em" class="ar">'+h(b.id)+'</span> '+
bfor(b.status)+' '+
(b.is_rerun?'<span class="badge bw">RERUN</span> ':'')+
(!b.cons.agreed?'<span class="badge bg">DISAGREED</span> ':'')+
(f.verdict?ve(f.verdict):'');

let c1='',c2='',c3='';
const e=b.ext;
c1='<div class="card"><div class="ch">Extraction</div>'+
fr('Title',e.title_full||e.display_title,1)+
fr('Author',e.author_name_raw,1)+
fr('Author (short)',e.author_short,1)+
fr('Muhaqiq',e.muhaqiq_name_raw,1)+
fr('Publisher',e.publisher,1)+
fr('Category',e.shamela_category,1)+
fr('Death Date',e.author_death_hijri?e.author_death_hijri+' AH':null,0)+
fr('Pages',e.page_count,0)+
fr('Volumes',e.volume_count,0)+
fr('Edition',e.edition_raw,1)+
'</div>';

const mk=Object.keys(b.llm);
if(mk.length>=2){
const m1=mk[0],m2=mk[1],p1=b.llm[m1]||{},p2=b.llm[m2]||{};
const cm=b.cons.canonical_model||'';
function lf(lb,g,ia){
const v1=g(p1),v2=g(p2);const eq=JSON.stringify(v1)===JSON.stringify(v2);const cls=eq?'fr':'fr mm';
const r=ia?ar:mo;
return'<div class="'+cls+'"><span class="fl">'+h(lb)+'</span></div>'+
'<div style="display:grid;grid-template-columns:1fr 1fr;gap:3px"><div style="padding:1px 5px;font-size:.83em">'+r(v1)+'</div><div style="padding:1px 5px;font-size:.83em">'+r(v2)+'</div></div>';}
const ai1=p1.author_identification||{},ai2=p2.author_identification||{};
c2='<div class="card"><div class="ch">LLM Inference</div>'+
'<div style="display:grid;grid-template-columns:1fr 1fr;gap:3px;margin-bottom:6px">'+
'<div style="font-weight:600;font-size:.83em">'+h(mn(m1))+' '+(cm.includes(m1)?'<span class="badge bgold">CANONICAL</span>':'')+'</div>'+
'<div style="font-weight:600;font-size:.83em">'+h(mn(m2))+' '+(cm.includes(m2)?'<span class="badge bgold">CANONICAL</span>':'')+'</div></div>'+
lf('Author',p=>(p.author_identification||{}).canonical_name_ar,1)+
lf('Known As',p=>(p.author_identification||{}).known_as,1)+
lf('Death',p=>{const d=(p.author_identification||{}).death_date_hijri;return d?d+' AH':null;},0)+
lf('Author Conf.',p=>{const c=(p.author_identification||{}).confidence;return c!=null?c.toFixed(2):null;},0)+
lf('Genre',p=>p.genre,0)+
lf('Genre Conf.',p=>p.genre_confidence!=null?p.genre_confidence.toFixed(2):null,0)+
lf('Multi-layer',p=>p.is_multi_layer!=null?String(p.is_multi_layer):null,0)+
lf('Sciences',p=>Array.isArray(p.science_scope)?p.science_scope.join(', '):p.science_scope,0)+
lf('Structure',p=>p.structural_format,0)+
lf('Authority',p=>p.authority_level,0)+
lf('Attribution',p=>p.attribution_status,0)+
lf('Level',p=>p.level,0)+
lf('School',p=>Array.isArray(p.school_affiliations)?p.school_affiliations.join(', '):p.school_affiliations,0)+
lf('Standing',p=>p.scholarly_standing,1)+
'</div>';
}else if(mk.length===1){
c2='<div class="card"><div class="ch">LLM (single model)</div><p class="mo">'+h(mn(mk[0]))+'</p></div>';
}else{c2='<div class="card"><div class="ch">LLM Inference</div><p class="dim">No LLM data</p></div>';}

if(b.status==='success'&&b.meta){
const m=b.meta,au=m.author||{},cs=m.confidence_scores||{};
let tf='';
if(m.trust_factors&&m.trust_factors.length){
tf=m.trust_factors.map(t=>{const nm=typeof t==='object'?t.factor||t.name||'':'';const sc=typeof t==='object'?t.weighted_score||t.score||0:0;const w=typeof t==='object'?t.weight||0:0;const rs=typeof t==='object'?t.raw_score||0:0;
return'<div class="dr"><span class="dl mo" style="width:130px">'+h(nm)+' ('+w+')</span><div class="dt"><div class="df" style="width:'+(rs*100).toFixed(0)+'%;background:'+cc(rs)+'"></div></div><span class="dc">'+rs.toFixed(2)+'</span></div>';}).join('');}
c3='<div class="card"><div class="ch">Pipeline Output '+(b.cons.agreed?'<span class="badge bs">AGREED</span>':'<span class="badge bg">DISAGREED</span>')+'</div>'+
fr('Author',au.name_arabic,1)+
fr('Author ID',au.canonical_id,0)+
fr('Author Conf.',au.confidence!=null?au.confidence.toFixed(2):null,0)+
fr('Genre',m.genre,0)+
fr('Level',m.level,0)+
fr('Sciences',Array.isArray(m.science_scope)?m.science_scope.join(', '):m.science_scope,0)+
fr('Multi-layer',m.is_multi_layer!=null?String(m.is_multi_layer):null,0)+
(m.is_multi_layer&&m.text_layers?fr('Layers',m.text_layers.map(l=>typeof l==='object'?l.layer_type||JSON.stringify(l):l).join(', '),0):'')+
fr('Trust Tier',m.trust_tier,0)+
fr('Trust Score',m.trust_score!=null?m.trust_score.toFixed(4):null,0)+
(tf?'<div style="margin:4px 0"><span class="fl">Trust Factors:</span>'+tf+'</div>':'')+
fr('Attribution',m.attribution_status,0)+
fr('Authority',m.authority_level,0)+
fr('Structure',m.structural_format,0)+
fr('Publisher',m.publisher,1)+
(m.muhaqiq?fr('Muhaqiq',m.muhaqiq.name_arabic,1):'')+
'<div style="margin-top:6px"><span class="fl">Confidence Scores:</span>'+
Object.entries(cs).map(([k,v])=>'<div class="fr"><span class="fl">'+h(k)+'</span><span class="fv mo" style="color:'+cc(v)+'">'+(typeof v==='number'?v.toFixed(2):v)+'</span></div>').join('')+
'</div></div>';
}else if(b.error){
c3='<div class="card"><div class="ch">Error</div>'+
fr('Code',b.error.code,0)+fr('Message',b.error.message,0)+
(b.error.gate_errors&&b.error.gate_errors.length?'<div style="margin:4px 0"><span class="fl">Gate Errors:</span>'+b.error.gate_errors.map(e=>'<div class="fr"><span class="mo red">'+h(typeof e==='object'?JSON.stringify(e):e)+'</span></div>').join('')+'</div>':'')+
'</div>';
}else{c3='<div class="card dim">No output data</div>';}

document.getElementById('rc').innerHTML='<div class="rc">'+c1+c2+c3+'</div>';

const vc=f.verdict==='correct'?'vc':'',vw_=f.verdict==='wrong'?'vw':'',vu=f.verdict==='unsure'?'vu':'';
let corr='';
f.issues.forEach(iss=>{
const cv=f.corrections[iss]||'';
switch(iss){
case'Author':corr+='<div class="cr"><label>Correct author name:</label><input class="ai" value="'+h(cv)+'" oninput="doUC(\'Author\',this.value)"></div>';break;
case'Genre':corr+='<div class="cr"><label>Correct genre:</label><select onchange="doUC(\'Genre\',this.value)">'+GN.map(g=>'<option value="'+g+'"'+(cv===g?' selected':'')+'>'+g+'</option>').join('')+'</select></div>';break;
case'Multi-layer':corr+='<div class="cr"><label>Should be:</label><select onchange="doUC(\'Multi-layer\',this.value)"><option value="single"'+(cv==='single'?' selected':'')+'>single-layer</option><option value="multi"'+(cv==='multi'?' selected':'')+'>multi-layer</option></select></div>';break;
case'Sciences':corr+='<div class="cr"><label>Correct sciences (comma-separated):</label><input value="'+h(cv)+'" oninput="doUC(\'Sciences\',this.value)"></div>';break;
case'Death date':corr+='<div class="cr"><label>Correct death date (AH):</label><input type="number" value="'+h(cv)+'" oninput="doUC(\'Death date\',this.value)"></div>';break;
case'Muhaqiq':corr+='<div class="cr"><label>Correct muhaqiq:</label><input class="ai" value="'+h(cv)+'" oninput="doUC(\'Muhaqiq\',this.value)"></div>';break;
case'Trust':corr+='<div class="cr"><label>Trust tier:</label><select onchange="doUC(\'Trust\',this.value)">'+TT.map(t=>'<option value="'+t+'"'+(cv===t?' selected':'')+'>'+t+'</option>').join('')+'</select></div>';break;
case'Attribution':corr+='<div class="cr"><label>Attribution:</label><select onchange="doUC(\'Attribution\',this.value)">'+AT.map(a=>'<option value="'+a+'"'+(cv===a?' selected':'')+'>'+a+'</option>').join('')+'</select></div>';break;
case'School':corr+='<div class="cr"><label>School affiliations:</label><input value="'+h(cv)+'" oninput="doUC(\'School\',this.value)"></div>';break;
case'Missing data':corr+='<div class="cr"><label>What\'s missing:</label><input value="'+h(cv)+'" oninput="doUC(\'Missing data\',this.value)"></div>';break;
case'Layers':corr+='<div class="cr"><label>Correct layers:</label><textarea oninput="doUC(\'Layers\',this.value)">'+h(cv)+'</textarea></div>';break;
case'Other':corr+='<div class="cr"><label>Describe:</label><textarea oninput="doUC(\'Other\',this.value)">'+h(cv)+'</textarea></div>';break;
}});

document.getElementById('rfb').innerHTML='<div class="fp"><h3>Feedback <span class="mo dim" style="font-weight:400">(1=Correct 2=Wrong 3=Unsure &#8594;=Next &#8592;=Prev Esc=List)</span></h3>'+
'<div class="vbs"><button class="vb '+vc+'" onclick="doV(\'correct\')">✅ Correct</button><button class="vb '+vw_+'" onclick="doV(\'wrong\')">❌ Wrong</button><button class="vb '+vu+'" onclick="doV(\'unsure\')">❓ Unsure</button></div>'+
'<div class="it">'+IS.map(iss=>'<span class="ig'+(f.issues.includes(iss)?' active':'')+'" onclick="doTI(\''+iss+'\')">'+iss+'</span>').join('')+'</div>'+
corr+
'<textarea class="na" placeholder="Additional notes (visible to Claude Chat during review)" oninput="doUN(this.value)">'+h(f.notes||'')+'</textarea></div>';}

function rL(){
const fl=gfs();
const fs=[['all','All'],['success','Success'],['gate_abort','Gate Abort'],['disagreements','Disagreements'],['flagged','Flagged'],['unreviewed','Unreviewed'],['reruns','Reruns'],['new','New Books']];
document.getElementById('lf').innerHTML=fs.map(([k,l])=>'<button class="fbtn'+(flt===k?' active':'')+'" onclick="oFlt(\''+k+'\')">'+l+' ('+fltB(srchB(D,sq),k).length+')</button>').join('');
let rows='';
fl.forEach((b,i)=>{
const f=fb[b.id]||{},mc=gmc(b),ts=b.meta?.trust_score!=null?b.meta.trust_score.toFixed(2):'—',cat=b.ext.shamela_category||'';
const di=D.indexOf(b);
rows+='<div class="br" onclick="oir('+di+')"><span class="mo dim">'+(i+1)+'</span>'+bfor(b.status)+'<span class="ar" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+h(b.id)+'</span><span class="ar" style="font-size:.78em;color:var(--dim);overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+h(cat)+'</span><span class="mo">'+ts+'</span>'+cdot(mc)+'<span>'+ve(f.verdict)+'</span></div>';});
document.getElementById('lc').innerHTML=rows||'<p class="dim" style="padding:16px">No books match filters</p>';}

function oFlt(f){flt=f;rL();}
function oSrt(s){srt=s;rL();}
function oSrch(q){sq=q;rL();}

function doExport(){
const rv=Object.keys(fb).filter(k=>fb[k].verdict).length;
const wi=Object.keys(fb).filter(k=>fb[k].issues&&fb[k].issues.length).length;
const is={};Object.values(fb).forEach(f=>{(f.issues||[]).forEach(i=>{is[i]=(is[i]||0)+1;});});
const out={phase:'D',pipeline_version:VER,export_timestamp:new Date().toISOString(),total_books:D.length,reviewed:rv,with_issues:wi,issue_summary:is,books:{}};
D.forEach(b=>{const f=fb[b.id]||{};if(f.verdict){out.books[b.id]={verdict:f.verdict,issues:f.issues||[],corrections:f.corrections||{},notes:f.notes||'',timestamp:f.timestamp,book_status:b.status,is_rerun:b.is_rerun,book_genre:b.meta?.genre||'',consensus_agreed:b.cons.agreed};}});
const bl=new Blob([JSON.stringify(out,null,2)],{type:'application/json'});
const u=URL.createObjectURL(bl);const a=document.createElement('a');a.href=u;a.download='kr_phase_d_feedback.json';a.click();URL.revokeObjectURL(u);}

document.addEventListener('keydown',e=>{
if(vw!=='vr')return;
if(e.target.tagName==='INPUT'||e.target.tagName==='TEXTAREA'||e.target.tagName==='SELECT')return;
switch(e.key){
case'1':doV('correct');break;case'2':doV('wrong');break;case'3':doV('unsure');break;
case'ArrowRight':case'n':e.preventDefault();nx();break;
case'ArrowLeft':case'p':e.preventDefault();pv();break;
case'Escape':sv('vl');break;}});

rD();
</script></body></html>"""


def main() -> None:
    print("Collecting book data...")
    books = collect_books()
    version = get_version()
    print(f"  Found {len(books)} books, pipeline version {version}")

    print("Generating HTML...")
    html = generate_html(books, version)
    output = PHASE_D_DIR / "review_gui.html"
    output.write_text(html, encoding="utf-8")
    size_kb = output.stat().st_size / 1024
    print(f"  Written: {output}")
    print(f"  Size: {size_kb:.0f} KB")


if __name__ == "__main__":
    main()
