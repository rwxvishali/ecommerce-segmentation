"""
05_build_dashboard.py — Assemble a self-contained interactive HTML dashboard.
Reads the analysis JSON artifacts and injects them as a JS object, then writes
dashboard/index.html (no external data dependencies, no build step).
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
OUT = BASE / "dashboard" / "index.html"

def load(name):
    with open(DATA / name) as f:
        return json.load(f)

payload = {
    "audit": load("cleaning_audit.json"),
    "sql": load("sql_results.json"),
    "segments": load("segments.json"),
    "insights": load("insights.json"),
}

DATA_JS = json.dumps(payload, separators=(",", ":"))

HTML = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Online Retail — Customer Segmentation Dashboard</title>
<style>
  :root{
    --surface-1:#fcfcfb; --page:#f9f9f7; --text-primary:#0b0b0b; --text-secondary:#52514e;
    --muted:#898781; --grid:#e1e0d9; --axis:#c3c2b7; --border:rgba(11,11,11,.10);
    --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s4:#e87ba4; --good:#006300;
    --seq1:#cde2fb;--seq2:#9ec5f4;--seq3:#5598e7;--seq4:#2a78d6;--seq5:#184f95;
  }
  :root[data-theme="dark"]{
    --surface-1:#1a1a19; --page:#0d0d0d; --text-primary:#fff; --text-secondary:#c3c2b7;
    --muted:#898781; --grid:#2c2c2a; --axis:#383835; --border:rgba(255,255,255,.10);
    --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#d55181; --good:#0ca30c;
    --seq1:#104281;--seq2:#184f95;--seq3:#256abf;--seq4:#3987e5;--seq5:#86b6ef;
  }
  *{box-sizing:border-box}
  html,body{margin:0}
  body{background:var(--page);color:var(--text-primary);
    font-family:system-ui,-apple-system,"Segoe UI",sans-serif;line-height:1.45}
  .wrap{max-width:1180px;margin:0 auto;padding:28px 22px 64px}
  header.top{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap}
  h1{font-size:24px;margin:0 0 4px}
  .subtitle{color:var(--text-secondary);font-size:14px;max-width:640px}
  .toggle{border:1px solid var(--border);background:var(--surface-1);color:var(--text-secondary);
    border-radius:8px;padding:8px 12px;font-size:13px;cursor:pointer}
  .toggle:hover{color:var(--text-primary)}
  section{background:var(--surface-1);border:1px solid var(--border);border-radius:14px;
    padding:20px 22px;margin-top:18px}
  .sec-title{font-size:16px;font-weight:600;margin:0 0 2px}
  .sec-sub{color:var(--text-secondary);font-size:13px;margin:0 0 14px}
  .kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
  .kpi{background:var(--surface-1);border:1px solid var(--border);border-radius:12px;padding:16px}
  .kpi .v{font-size:30px;font-weight:650;letter-spacing:-.5px}
  .kpi .l{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-top:2px}
  .kpi .s{font-size:12px;color:var(--text-secondary);margin-top:6px}
  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px}
  .facets{display:grid;grid-template-columns:1fr 1fr;gap:12px}
  svg{display:block;width:100%;height:auto;overflow:visible}
  .ax{fill:var(--muted);font-size:11px;font-variant-numeric:tabular-nums}
  .axlab{fill:var(--text-secondary);font-size:11px}
  .gl{stroke:var(--grid);stroke-width:1}
  .baseline{stroke:var(--axis);stroke-width:1}
  .bar-lab{fill:var(--text-primary);font-size:11px;font-variant-numeric:tabular-nums}
  .bar-name{fill:var(--text-secondary);font-size:12px}
  .facet-title{fill:var(--text-primary);font-size:12px;font-weight:600}
  .facet-sub{fill:var(--muted);font-size:10px}
  table{border-collapse:collapse;width:100%;font-size:13px;margin-top:4px}
  th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--border)}
  th{color:var(--muted);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.05em}
  td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
  .cards{display:grid;grid-template-columns:1fr 1fr;gap:14px}
  .card{border:1px solid var(--border);border-radius:12px;padding:14px 16px}
  .card .seg{font-weight:650;font-size:14px}
  .card .act{font-size:13px;margin:6px 0}
  .card .why{font-size:12px;color:var(--text-secondary)}
  .pill{display:inline-block;font-size:11px;padding:2px 8px;border-radius:999px;
    background:color-mix(in srgb,var(--s1) 16%,transparent);color:var(--text-primary);margin-bottom:6px}
  ul.find{margin:0;padding-left:18px}
  ul.find li{margin:7px 0;font-size:14px}
  .note{font-size:12px;color:var(--muted);margin-top:10px;font-style:italic}
  .tip{position:fixed;pointer-events:none;background:var(--surface-1);border:1px solid var(--border);
    border-radius:8px;padding:7px 10px;font-size:12px;box-shadow:0 6px 20px rgba(0,0,0,.18);
    opacity:0;transition:opacity .08s;z-index:20;max-width:240px}
  .tip b{font-weight:650}
  .legend{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:var(--text-secondary);margin-top:8px}
  .legend .sw{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:5px;vertical-align:middle}
  footer{color:var(--muted);font-size:12px;margin-top:22px;text-align:center}
  @media(max-width:820px){.kpis{grid-template-columns:repeat(2,1fr)}.grid2,.cards,.facets{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div>
      <h1>Online Retail — Customer Segmentation & Analytics</h1>
      <div class="subtitle" id="subtitle"></div>
    </div>
    <button class="toggle" id="themeBtn">◐ Theme</button>
  </header>

  <section>
    <div class="kpis" id="kpis"></div>
  </section>

  <section>
    <div class="sec-title">Monthly revenue trend</div>
    <div class="sec-sub">Gross revenue by month across the trading year. Hover for detail.</div>
    <div id="chart-trend"></div>
    <div class="note" id="trend-note"></div>
  </section>

  <div class="grid2">
    <section>
      <div class="sec-title">Revenue concentration (Pareto)</div>
      <div class="sec-sub">Customers split into 5 equal groups by spend — share of total revenue.</div>
      <div id="chart-pareto"></div>
    </section>
    <section>
      <div class="sec-title">Top markets by revenue</div>
      <div class="sec-sub">Share of total revenue by country (top 6).</div>
      <div id="chart-country"></div>
    </section>
  </div>

  <section>
    <div class="sec-title">Customer segments — RFM scoring</div>
    <div class="sec-sub">Rule-based Recency–Frequency–Monetary segments, ranked by revenue contribution.</div>
    <div id="chart-seg"></div>
  </section>

  <section>
    <div class="sec-title">KMeans clusters — RFM structure</div>
    <div class="sec-sub" id="km-sub"></div>
    <div class="facets" id="facets"></div>
    <div class="legend"><span><span class="sw" style="background:var(--s1)"></span>Cluster in focus</span>
      <span><span class="sw" style="background:var(--axis)"></span>All other customers</span>
      <span>Axes: Recency (days, →older) vs Monetary (£, log)</span></div>
    <table id="km-table" style="margin-top:16px"></table>
  </section>

  <section>
    <div class="sec-title">Top products by revenue</div>
    <div class="sec-sub">The 8 best-selling SKUs by gross revenue.</div>
    <div id="chart-products"></div>
  </section>

  <div class="grid2">
    <section>
      <div class="sec-title">Key findings</div>
      <div class="sec-sub">What the data says.</div>
      <ul class="find" id="findings"></ul>
    </section>
    <section>
      <div class="sec-title">Recommended actions</div>
      <div class="sec-sub">What to do about it — by segment.</div>
      <div class="cards" id="recs"></div>
    </section>
  </div>

  <footer id="foot"></footer>
</div>

<div class="tip" id="tip"></div>
<script>
const DATA = __DATA__;
const SVGNS="http://www.w3.org/2000/svg";
const tip=document.getElementById('tip');
function fmtGBP(n){return '£'+Math.round(n).toLocaleString();}
function fmtM(n){return '£'+(n/1e6).toFixed(2)+'M';}
function el(tag,attrs={},parent){const e=document.createElementNS(SVGNS,tag);
  for(const k in attrs)e.setAttribute(k,attrs[k]); if(parent)parent.appendChild(e); return e;}
function svg(w,h){const s=el('svg',{viewBox:`0 0 ${w} ${h}`,role:'img'});return s;}
function showTip(html,evt){tip.innerHTML=html;tip.style.opacity=1;
  const pad=14;let x=evt.clientX+pad,y=evt.clientY+pad;
  if(x+250>innerWidth)x=evt.clientX-tip.offsetWidth-pad;
  tip.style.left=x+'px';tip.style.top=y+'px';}
function hideTip(){tip.style.opacity=0;}

// subtitle + kpis
const A=DATA.audit;
document.getElementById('subtitle').textContent=
  `UK-based online gift retailer · ${A["6_final_rows"].toLocaleString()} clean transactions · `+
  `${A.date_min} to ${A.date_max} · built with Python, SQL & scikit-learn.`;
const kw=document.getElementById('kpis');
DATA.insights.kpis.forEach(k=>{
  const d=document.createElement('div');d.className='kpi';
  d.innerHTML=`<div class="v">${k.value}</div><div class="l">${k.label}</div><div class="s">${k.sub}</div>`;
  kw.appendChild(d);});

/* ---------- Monthly revenue trend (area + line, single series) ---------- */
(function(){
  const rows=DATA.sql.monthly_revenue;
  const W=1080,H=320,m={t:16,r:20,b:36,l:64};
  const iw=W-m.l-m.r, ih=H-m.t-m.b;
  const s=svg(W,H);document.getElementById('chart-trend').appendChild(s);
  const maxV=Math.max(...rows.map(r=>r.revenue))*1.08;
  const x=i=>m.l+(rows.length===1?iw/2:iw*i/(rows.length-1));
  const y=v=>m.t+ih-ih*v/maxV;
  // gridlines
  const ticks=5;
  for(let i=0;i<=ticks;i++){const v=maxV*i/ticks;const yy=y(v);
    el('line',{x1:m.l,y1:yy,x2:m.l+iw,y2:yy,class:'gl'},s);
    const t=el('text',{x:m.l-8,y:yy+4,class:'ax','text-anchor':'end'},s);
    t.textContent='£'+Math.round(v/1000)+'k';}
  // area
  let dArea=`M ${x(0)} ${y(0)}`;rows.forEach((r,i)=>dArea+=` L ${x(i)} ${y(r.revenue)}`);
  dArea+=` L ${x(rows.length-1)} ${y(0)} Z`;
  const grad=el('linearGradient',{id:'ga',x1:0,y1:0,x2:0,y2:1},s);
  el('stop',{offset:'0%','stop-color':'var(--s1)','stop-opacity':.28},grad);
  el('stop',{offset:'100%','stop-color':'var(--s1)','stop-opacity':.02},grad);
  el('path',{d:dArea,fill:'url(#ga)'},s);
  let dLine='';rows.forEach((r,i)=>dLine+=(i?' L ':'M ')+x(i)+' '+y(r.revenue));
  el('path',{d:dLine,fill:'none',stroke:'var(--s1)','stroke-width':2,'stroke-linejoin':'round'},s);
  el('line',{x1:m.l,y1:m.t+ih,x2:m.l+iw,y2:m.t+ih,class:'baseline'},s);
  rows.forEach((r,i)=>{
    const partial=(i===rows.length-1);
    el('circle',{cx:x(i),cy:y(r.revenue),r:partial?4.5:3.5,
      fill:partial?'var(--surface-1)':'var(--s1)',
      stroke:'var(--s1)','stroke-width':2},s);
    const lab=el('text',{x:x(i),y:H-10,class:'ax','text-anchor':'middle'},s);
    lab.textContent=r.ym.slice(2);
    const hit=el('rect',{x:x(i)-24,y:m.t,width:48,height:ih,fill:'transparent'},s);
    hit.addEventListener('mousemove',e=>showTip(
      `<b>${r.ym}</b>${partial?' (partial)':''}<br>Revenue ${fmtGBP(r.revenue)}<br>`+
      `Orders ${r.orders.toLocaleString()} · ${r.active_customers} active<br>`+
      `MoM ${r.mom_growth_pct==null?'—':r.mom_growth_pct+'%'}`,e));
    hit.addEventListener('mouseleave',hideTip);
  });
  document.getElementById('trend-note').textContent=DATA.insights.notes[0];
})();

/* ---------- horizontal bar helper (single sequential hue by rank) ---------- */
function hbars(mount,items,{label,value,valueFmt,barMax,colorBy}){
  const rowH=34,padL=190,padR=64,W=520,top=6;
  const H=top*2+items.length*rowH;
  const s=svg(W,H);mount.appendChild(s);
  const maxV=barMax||Math.max(...items.map(value));
  const seq=['var(--seq5)','var(--seq4)','var(--seq3)','var(--seq2)','var(--seq1)'];
  items.forEach((it,i)=>{
    const y=top+i*rowH;const bw=(W-padL-padR)*value(it)/maxV;
    const nm=el('text',{x:padL-10,y:y+rowH/2+4,class:'bar-name','text-anchor':'end'},s);
    nm.textContent=label(it);
    const col=colorBy?colorBy(it,i):seq[Math.min(i,4)];
    const bar=el('rect',{x:padL,y:y+7,width:Math.max(bw,2),height:rowH-16,rx:4,fill:col},s);
    const vl=el('text',{x:padL+Math.max(bw,2)+8,y:y+rowH/2+4,class:'bar-lab'},s);
    vl.textContent=valueFmt(it);
    bar.addEventListener('mousemove',e=>showTip(`<b>${label(it)}</b><br>${valueFmt(it)}`,e));
    bar.addEventListener('mouseleave',hideTip);
  });
}

/* Pareto */
(function(){
  const q=DATA.sql.pareto_quintiles;
  const names=['Top 20%','2nd 20%','3rd 20%','4th 20%','Bottom 20%'];
  hbars(document.getElementById('chart-pareto'),q,{
    label:(d)=>names[d.quintile-1],
    value:(d)=>d.pct_of_revenue,
    valueFmt:(d)=>d.pct_of_revenue+'%  ('+fmtM(d.revenue)+')',
    barMax:100});
})();

/* Top countries */
(function(){
  const c=DATA.sql.top_countries.slice(0,6);
  hbars(document.getElementById('chart-country'),c,{
    label:(d)=>d.Country,
    value:(d)=>d.revenue,
    valueFmt:(d)=>d.pct_of_total+'%  ('+fmtM(d.revenue)+')'});
})();

/* Segments (rule-based) — full width, by % revenue */
(function(){
  const segs=DATA.segments.rule_based_segments;
  const mount=document.getElementById('chart-seg');
  const rowH=38,padL=210,padR=210,W=1080,top=6;
  const H=top*2+segs.length*rowH;
  const s=svg(W,H);mount.appendChild(s);
  const maxV=Math.max(...segs.map(d=>d.pct_revenue));
  segs.forEach((d,i)=>{
    const y=top+i*rowH;const bw=(W-padL-padR)*d.pct_revenue/maxV;
    const nm=el('text',{x:padL-10,y:y+rowH/2+4,class:'bar-name','text-anchor':'end'},s);
    nm.textContent=d.Segment;
    const bar=el('rect',{x:padL,y:y+8,width:Math.max(bw,2),height:rowH-18,rx:4,fill:'var(--s1)'},s);
    const vl=el('text',{x:padL+Math.max(bw,2)+8,y:y+rowH/2+4,class:'bar-lab'},s);
    vl.textContent=d.pct_revenue.toFixed(1)+'% rev · '+d.customers+' cust · avg '+fmtGBP(d.avg_monetary);
    bar.addEventListener('mousemove',e=>showTip(
      `<b>${d.Segment}</b><br>${d.pct_revenue}% of revenue<br>`+
      `${d.customers} customers (${d.pct_customers}%)<br>`+
      `Avg spend ${fmtGBP(d.avg_monetary)} · ${d.avg_frequency.toFixed(1)} orders<br>`+
      `Avg recency ${Math.round(d.avg_recency)}d`,e));
    bar.addEventListener('mouseleave',hideTip);
  });
})();

/* KMeans facets (2x2 small multiples) */
(function(){
  const meta=DATA.segments.meta;
  document.getElementById('km-sub').textContent=
    `k=${meta.kmeans_best_k} chosen by silhouette (${meta.kmeans_silhouette}). `+
    `Each panel highlights one cluster; grey points are everyone else. Log axes.`;
  const pts=DATA.segments.scatter;
  const clusters=DATA.segments.kmeans_segments.map(d=>d.ClusterName);
  const wrap=document.getElementById('facets');
  const Rlog=v=>Math.log10(Math.max(v,1));
  const Mlog=v=>Math.log10(Math.max(v,1));
  const rMin=Math.min(...pts.map(p=>Rlog(p.Recency))),rMax=Math.max(...pts.map(p=>Rlog(p.Recency)));
  const mMin=Math.min(...pts.map(p=>Mlog(p.Monetary))),mMax=Math.max(...pts.map(p=>Mlog(p.Monetary)));
  clusters.forEach(cn=>{
    const box=document.createElement('div');wrap.appendChild(box);
    const W=520,H=300,m={t:34,r:16,b:34,l:44},iw=W-m.l-m.r,ih=H-m.t-m.b;
    const s=svg(W,H);box.appendChild(s);
    const prof=DATA.segments.kmeans_segments.find(d=>d.ClusterName===cn);
    const x=v=>m.l+iw*(Rlog(v)-rMin)/(rMax-rMin);
    const y=v=>m.t+ih-ih*(Mlog(v)-mMin)/(mMax-mMin);
    for(let i=0;i<=3;i++){const yy=m.t+ih*i/3;el('line',{x1:m.l,y1:yy,x2:m.l+iw,y2:yy,class:'gl'},s);}
    // background points
    pts.forEach(p=>{if(p.ClusterName!==cn)el('circle',{cx:x(p.Recency),cy:y(p.Monetary),r:2.2,
      fill:'var(--axis)','fill-opacity':.5},s);});
    // highlighted cluster
    pts.forEach(p=>{if(p.ClusterName===cn)el('circle',{cx:x(p.Recency),cy:y(p.Monetary),r:2.8,
      fill:'var(--s1)','fill-opacity':.85},s);});
    el('line',{x1:m.l,y1:m.t+ih,x2:m.l+iw,y2:m.t+ih,class:'baseline'},s);
    const t=el('text',{x:m.l,y:18,class:'facet-title'},s);t.textContent=cn;
    const sub=el('text',{x:m.l,y:30,class:'facet-sub'},s);
    sub.textContent=`${prof.customers} cust · ${prof.pct_revenue}% rev · avg £${Math.round(prof.avg_monetary).toLocaleString()}`;
    const xl=el('text',{x:m.l+iw,y:H-8,class:'axlab','text-anchor':'end'},s);xl.textContent='Recency →';
    const yl=el('text',{x:m.l-34,y:m.t+8,class:'axlab'},s);yl.textContent='£ ↑';
  });
  // table
  const tb=document.getElementById('km-table');
  let h='<thead><tr><th>Cluster</th><th class="num">Customers</th><th class="num">Avg Recency</th>'+
    '<th class="num">Avg Orders</th><th class="num">Avg Spend</th><th class="num">% Revenue</th></tr></thead><tbody>';
  DATA.segments.kmeans_segments.forEach(d=>{h+=`<tr><td>${d.ClusterName}</td>`+
    `<td class="num">${d.customers}</td><td class="num">${Math.round(d.avg_recency)}d</td>`+
    `<td class="num">${d.avg_frequency.toFixed(1)}</td><td class="num">${fmtGBP(d.avg_monetary)}</td>`+
    `<td class="num">${d.pct_revenue}%</td></tr>`;});
  tb.innerHTML=h+'</tbody>';
})();

/* Top products */
(function(){
  const p=DATA.sql.top_products.slice(0,8);
  const mount=document.getElementById('chart-products');
  const rowH=34,padL=300,padR=120,W=1080,top=6;
  const H=top*2+p.length*rowH;const s=svg(W,H);mount.appendChild(s);
  const maxV=Math.max(...p.map(d=>d.revenue));
  p.forEach((d,i)=>{
    const y=top+i*rowH;const bw=(W-padL-padR)*d.revenue/maxV;
    const nm=(d.description||d.StockCode||'').toLowerCase().replace(/\b\w/g,c=>c.toUpperCase());
    const t=el('text',{x:padL-10,y:y+rowH/2+4,class:'bar-name','text-anchor':'end'},s);
    t.textContent=nm.length>40?nm.slice(0,38)+'…':nm;
    const bar=el('rect',{x:padL,y:y+7,width:Math.max(bw,2),height:rowH-16,rx:4,fill:'var(--s3)'},s);
    const vl=el('text',{x:padL+Math.max(bw,2)+8,y:y+rowH/2+4,class:'bar-lab'},s);
    vl.textContent=fmtGBP(d.revenue);
    bar.addEventListener('mousemove',e=>showTip(`<b>${nm}</b><br>${fmtGBP(d.revenue)} · ${d.units_sold.toLocaleString()} units`,e));
    bar.addEventListener('mouseleave',hideTip);
  });
})();

/* Findings + recommendations */
(function(){
  const f=document.getElementById('findings');
  DATA.insights.findings.forEach(x=>{const li=document.createElement('li');li.textContent=x;f.appendChild(li);});
  const r=document.getElementById('recs');
  DATA.insights.recommendations.forEach(c=>{const d=document.createElement('div');d.className='card';
    d.innerHTML=`<span class="pill">${c.segment}</span><div class="act">${c.action}</div><div class="why">${c.why}</div>`;
    r.appendChild(d);});
  document.getElementById('foot').textContent=
    `Data: UCI/Kaggle Online Retail · cleaned to ${DATA.audit.retained_pct}% of raw rows · `+
    `snapshot ${DATA.segments.meta.snapshot_date}. Built by Vishali A.`;
})();

/* theme toggle */
document.getElementById('themeBtn').addEventListener('click',()=>{
  const r=document.documentElement;
  r.setAttribute('data-theme', r.getAttribute('data-theme')==='dark'?'light':'dark');
});
</script>
</body>
</html>
"""

OUT.write_text(HTML.replace("__DATA__", DATA_JS))
print("wrote", OUT, f"({OUT.stat().st_size/1024:.0f} KB)")
