# Build data-centric deck.html from real baseline numbers. No deps.
import json, datetime, base64, html
from collections import defaultdict

D = json.load(open('analysis/embed_data.json'))
AI = json.load(open('analysis/ai_eval.json'))
inc = D['incidents']
OPEN = {"NEW REGISTERED","RCA PROCESS","CA/PA EXECUTION","MONITORING RESULT"}
TODAY = datetime.date(2026, 8, 19)

def esc(s): return html.escape(str(s))

# ---------- facts ----------
tot  = sum(float(x.get('total_loss') or 0) for x in inc)          # kUSD
dt   = sum(float(x.get('downtime') or 0) for x in inc)            # hours
od   = [x for x in inc if x['status'] in OPEN and x.get('rca_due') and x['rca_due'] < '2026-08-19']
op   = [x for x in inc if x['status'] in OPEN]
odl  = sum(float(x['total_loss']) for x in od)
n    = len(inc)

M = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
mo = defaultdict(float)
for x in inc:
    if x.get('month'):
        mn, yy = x['month'].split('-'); mo[(int(yy), M.index(mn)+1)] += float(x.get('total_loss') or 0)
series = sorted(mo.items())
mvals  = [v for _, v in series]
mmean  = sum(mvals)/len(mvals)
y24    = [v for k, v in series if k[0] == 2024]
y26    = [v for k, v in series if k[0] == 2026]
avg24, avg26 = sum(y24)/len(y24), sum(y26)/len(y26)
growth = (avg26-avg24)/avg24*100

# aging buckets
ag = {'0-30':0,'31-90':0,'91-180':0,'181-365':0,'>365':0}
for x in od:
    a = (TODAY - datetime.date(*map(int, x['rca_due'].split('-')))).days
    k = '0-30' if a<=30 else '31-90' if a<=90 else '91-180' if a<=180 else '181-365' if a<=365 else '>365'
    ag[k] += 1
over1y = ag['>365']

# mechanisms
mc = defaultdict(lambda: [0, 0.0])
for x in inc:
    k = x.get('mech') or '?'; mc[k][0] += 1; mc[k][1] += float(x.get('total_loss') or 0)
mechs = sorted(mc.items(), key=lambda kv: -kv[1][1])
top3 = sum(v[1] for _, v in mechs[:3])
top3share = top3/tot*100

# units
un = defaultdict(lambda: [0, 0.0, 0])
for x in inc:
    k = x['plant']; un[k][0] += 1; un[k][1] += float(x.get('total_loss') or 0)
for x in od: un[x['plant']][2] += 1
units = sorted(un.items(), key=lambda kv: -kv[1][1])

# lead time from condition history
leads = []
for t, d in D['equipment'].items():
    ch = d['Condition History']; hdr = ch[0]; rows = ch[1:]
    sc = len(hdr) - 2
    ai = ti = None
    for i, r in enumerate(rows):
        s = str(r[sc]).strip()
        if s == 'ALARM' and ai is None: ai = i
        if s == 'TRIP' and ti is None: ti = i
    leads.append((t, (ti-ai)*7 if ai is not None and ti is not None else 0))
leads.sort(key=lambda x: x[1])
leadMean = sum(l[1] for l in leads)/len(leads)

p1  = AI['retrieval']['full_p1']['pct'];  p1lo = AI['retrieval']['full_p1']['ci_lo']; p1hi = AI['retrieval']['full_p1']['ci_hi']
p5  = AI['retrieval']['full_p5']['pct']
b1  = AI['retrieval']['base_p1']['pct']
lift = p1 - b1

# ---------- svg chart builders (no libs, offline) ----------
C = dict(blue='#1A56DB', sky='#3B82F6', red='#DC2626', amber='#D97706',
         green='#16A34A', grid='#E5E7EB', mut='#6B7280', navy='#0A2342', gray='#9CA3AF')

def esc2(s): return esc(s)

def line_chart(vals, w=560, h=170, color=None, avg=None, band=None):
    color = color or C['blue']
    pad = dict(l=46, r=10, t=12, b=22)
    mx = max(vals) * 1.08
    iw, ih = w-pad['l']-pad['r'], h-pad['t']-pad['b']
    def X(i): return pad['l'] + (i/(len(vals)-1))*iw
    def Y(v): return pad['t'] + ih - (v/mx)*ih
    o = [f'<svg viewBox="0 0 {w} {h}" class="chart" role="img">']
    for k in range(4):
        v = mx*k/3; y = Y(v)
        o.append(f'<line x1="{pad["l"]}" y1="{y:.1f}" x2="{w-pad["r"]}" y2="{y:.1f}" stroke="{C["grid"]}" stroke-width="1"/>')
        o.append(f'<text x="{pad["l"]-6}" y="{y+3.5:.1f}" text-anchor="end" font-size="9" fill="{C["mut"]}">{v/1000:.1f}M</text>')
    pts = ' '.join(f'{X(i):.1f},{Y(v):.1f}' for i, v in enumerate(vals))
    o.append(f'<polygon points="{pad["l"]},{Y(0):.1f} {pts} {w-pad["r"]},{Y(0):.1f}" fill="{color}" opacity=".10"/>')
    o.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.2" stroke-linejoin="round"/>')
    if avg is not None:
        y = Y(avg)
        o.append(f'<line x1="{pad["l"]}" y1="{y:.1f}" x2="{w-pad["r"]}" y2="{y:.1f}" stroke="{C["amber"]}" stroke-width="1.6" stroke-dasharray="5 4"/>')
        o.append(f'<text x="{w-pad["r"]}" y="{y-5:.1f}" text-anchor="end" font-size="9" font-weight="700" fill="{C["amber"]}">avg {avg/1000:.1f}M</text>')
    # peak marker
    pi = vals.index(max(vals))
    o.append(f'<circle cx="{X(pi):.1f}" cy="{Y(vals[pi]):.1f}" r="3.6" fill="{C["red"]}"/>')
    o.append(f'<text x="{X(pi):.1f}" y="{Y(vals[pi])-7:.1f}" text-anchor="middle" font-size="9" font-weight="700" fill="{C["red"]}">peak {vals[pi]/1000:.1f}M</text>')
    for i, lab in [(0,'Jan 24'),(len(vals)//2,'Jan 25'),(len(vals)-1,'Jul 26')]:
        o.append(f'<text x="{X(i):.1f}" y="{h-6}" text-anchor="middle" font-size="9" fill="{C["mut"]}">{lab}</text>')
    o.append('</svg>')
    return ''.join(o)

def hbars(items, w=540, rowh=30, color=None, unit='$', sub=None, maxval=None):
    """items: [(label, value, extra)]"""
    color = color or C['blue']
    mx = maxval or max(i[1] for i in items) or 1
    lw = 128; bw = w - lw - 62
    h = rowh*len(items) + 6
    o = [f'<svg viewBox="0 0 {w} {h}" class="chart" role="img">']
    for i, it in enumerate(items):
        lab, val = it[0], it[1]
        extra = it[2] if len(it) > 2 else None
        y = i*rowh + 4
        bwd = max(2, (val/mx)*bw)
        o.append(f'<text x="{lw-8}" y="{y+13}" text-anchor="end" font-size="11" font-weight="700" fill="{C["navy"]}">{esc2(lab)}</text>')
        o.append(f'<rect x="{lw}" y="{y+2}" width="{bw}" height="15" rx="4" fill="#F1F5F9"/>')
        o.append(f'<rect x="{lw}" y="{y+2}" width="{bwd:.1f}" height="15" rx="4" fill="{color}"/>')
        if unit == '$':
            txt = f'{val/1000:.2f}M'
        else:
            txt = f'{val:,.0f}'
        o.append(f'<text x="{lw+bw+6}" y="{y+13}" font-size="10.5" font-weight="700" fill="{C["navy"]}">{txt}</text>')
        if extra:
            o.append(f'<text x="{lw+6}" y="{y+13}" font-size="9.5" font-weight="700" fill="#fff">{esc2(extra)}</text>')
    o.append('</svg>')
    return ''.join(o)

def pareto(items, w=540, h=190):
    """items sorted desc: [(label, loss, count)]"""
    pad = dict(l=8, r=8, t=14, b=34)
    mx = items[0][1]
    tot_all = sum(i[1] for i in items)
    n = len(items); slot = (w-pad['l']-pad['r'])/n; bw = slot*0.56
    ih = h-pad['t']-pad['b']
    o = [f'<svg viewBox="0 0 {w} {h}" class="chart" role="img">']
    cum = 0; cpts = []
    for i, (lab, val, cnt) in enumerate(items):
        cum += val
        bh = max(3, (val/mx)*ih)
        x = pad['l'] + i*slot + (slot-bw)/2
        y = pad['t'] + ih - bh
        col = C['blue'] if i < 3 else C['gray']
        o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="4" fill="{col}"/>')
        o.append(f'<text x="{x+bw/2:.1f}" y="{y-5:.1f}" text-anchor="middle" font-size="10" font-weight="800" fill="{C["navy"]}">{val/1000:.1f}M</text>')
        o.append(f'<text x="{x+bw/2:.1f}" y="{h-20}" text-anchor="middle" font-size="9.5" font-weight="700" fill="{C["navy"]}">{esc2(lab[:14])}</text>')
        o.append(f'<text x="{x+bw/2:.1f}" y="{h-8}" text-anchor="middle" font-size="9" fill="{C["mut"]}">{cnt} cases</text>')
        cx = x+bw/2; cy = pad['t'] + ih - (cum/tot_all)*ih
        cpts.append((cx, cy, cum/tot_all))
    o.append('<polyline points="' + ' '.join(f'{c[0]:.1f},{c[1]:.1f}' for c in cpts) +
             f'" fill="none" stroke="{C["red"]}" stroke-width="1.8" stroke-dasharray="4 3"/>')
    for cx, cy, pc in cpts:
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3" fill="{C["red"]}"/>')
    c3 = cpts[2]
    o.append(f'<text x="{c3[0]:.1f}" y="{c3[1]-8:.1f}" text-anchor="middle" font-size="10.5" font-weight="800" fill="{C["red"]}">cum {c3[2]*100:.0f}%</text>')
    o.append('</svg>')
    return ''.join(o)

def ba_bar(before, after, blab, alab, w=250, h=170, bcol=None, acol=None, fmt='pct', note=''):
    bcol = bcol or C['red']; acol = acol or C['green']
    mx = max(before, after)*1.18
    pad = dict(t=24, b=46, l=16, r=16)
    ih = h-pad['t']-pad['b']; bw = 62; gap = 46
    x0 = (w-(bw*2+gap))/2
    o = [f'<svg viewBox="0 0 {w} {h}" class="chart" role="img">']
    for i, (v, col, lab) in enumerate([(before, bcol, blab), (after, acol, alab)]):
        bh = max(4, (v/mx)*ih)
        x = x0 + i*(bw+gap); y = pad['t']+ih-bh
        txt = f'{v:.1f}%' if fmt == 'pct' else f'{v/1000:.1f}M' if fmt == 'usd' else f'{v:,.0f}'
        o.append(f'<rect x="{x}" y="{y:.1f}" width="{bw}" height="{bh:.1f}" rx="6" fill="{col}"/>')
        o.append(f'<text x="{x+bw/2}" y="{y-7:.1f}" text-anchor="middle" font-size="14" font-weight="800" fill="{col}">{txt}</text>')
        o.append(f'<text x="{x+bw/2}" y="{h-26}" text-anchor="middle" font-size="10" font-weight="800" fill="{C["navy"]}">{lab}</text>')
        if i == 0:
            o.append(f'<text x="{x+bw/2}" y="{h-13}" text-anchor="middle" font-size="9" fill="{C["mut"]}">{esc2(note[:16])}</text>')
    o.append(f'<text x="{w/2}" y="{pad["t"]-8}" text-anchor="middle" font-size="11" font-weight="800" fill="{C["mut"]}">&#8594;</text>')
    o.append('</svg>')
    return ''.join(o)

def aging_chart(ag, w=540, h=175):
    keys = ['0-30','31-90','91-180','181-365','>365']
    vals = [ag[k] for k in keys]
    cols = [C['green'], C['sky'], C['amber'], '#EA580C', C['red']]
    pad = dict(l=40, r=10, t=14, b=40)
    mx = max(vals)*1.15
    slot = (w-pad['l']-pad['r'])/len(keys); bw = slot*0.6
    ih = h-pad['t']-pad['b']
    o = [f'<svg viewBox="0 0 {w} {h}" class="chart" role="img">']
    for k in range(3):
        y = pad['t']+ih-(mx*k/3)/mx*ih
        o.append(f'<line x1="{pad["l"]}" y1="{y:.1f}" x2="{w-pad["r"]}" y2="{y:.1f}" stroke="{C["grid"]}"/>')
        o.append(f'<text x="{pad["l"]-6}" y="{y+3.5:.1f}" text-anchor="end" font-size="9" fill="{C["mut"]}">{round(mx*k/3)}</text>')
    for i, k in enumerate(keys):
        bh = max(3, (vals[i]/mx)*ih)
        x = pad['l']+i*slot+(slot-bw)/2; y = pad['t']+ih-bh
        o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="5" fill="{cols[i]}"/>')
        o.append(f'<text x="{x+bw/2:.1f}" y="{y-6:.1f}" text-anchor="middle" font-size="11" font-weight="800" fill="{cols[i]}">{vals[i]}</text>')
        o.append(f'<text x="{x+bw/2:.1f}" y="{h-22}" text-anchor="middle" font-size="9.5" font-weight="700" fill="{C["navy"]}">{k}</text>')
        o.append(f'<text x="{x+bw/2:.1f}" y="{h-10}" text-anchor="middle" font-size="8.5" fill="{C["mut"]}">days</text>')
    o.append('</svg>')
    return ''.join(o)

def lead_chart(leads, w=540, h=165):
    pad = dict(l=40, r=10, t=14, b=38)
    mx = max(l[1] for l in leads)*1.2
    slot = (w-pad['l']-pad['r'])/len(leads); bw = slot*0.56
    ih = h-pad['t']-pad['b']
    o = [f'<svg viewBox="0 0 {w} {h}" class="chart" role="img">']
    for k in range(3):
        y = pad['t']+ih-(mx*k/3)/mx*ih
        o.append(f'<line x1="{pad["l"]}" y1="{y:.1f}" x2="{w-pad["r"]}" y2="{y:.1f}" stroke="{C["grid"]}"/>')
        o.append(f'<text x="{pad["l"]-6}" y="{y+3.5:.1f}" text-anchor="end" font-size="9" fill="{C["mut"]}">{round(mx*k/3)}d</text>')
    for i, (t, v) in enumerate(leads):
        bh = max(3, (v/mx)*ih)
        x = pad['l']+i*slot+(slot-bw)/2; y = pad['t']+ih-bh
        o.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="5" fill="{C["green"]}"/>')
        o.append(f'<text x="{x+bw/2:.1f}" y="{y-6:.1f}" text-anchor="middle" font-size="10.5" font-weight="800" fill="{C["green"]}">{v}d</text>')
        o.append(f'<text x="{x+bw/2:.1f}" y="{h-20}" text-anchor="middle" font-size="9.5" font-weight="700" fill="{C["navy"]}">{esc2(t)}</text>')
    o.append('</svg>')
    return ''.join(o)

def spark(vals, w=200, h=40, color=None):
    color = color or C['sky']
    mx = max(vals)*1.05 or 1
    pts = ' '.join(f'{(i/(len(vals)-1))*w:.1f},{h-(v/mx)*h:.1f}' for i, v in enumerate(vals))
    return (f'<svg viewBox="0 0 {w} {h}" class="spark" aria-hidden="true">'
            f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round"/></svg>')

facts = dict(tot=tot, dt=dt, n=n, nopen=len(op), nod=len(od), odl=odl, odlp=odl/tot*100,
             over1y=over1y, ag=ag, growth=growth, avg24=avg24, avg26=avg26, mmean=mmean,
             top3=top3, top3share=top3share, p1=p1, p1lo=p1lo, p1hi=p1hi, p5=p5, b1=b1, lift=lift,
             leadMean=leadMean, mvals=mvals, mechs=mechs, units=units, leads=leads)
json.dump({k: (v if isinstance(v, (int, float, str)) else str(type(v))) for k, v in facts.items()},
          open('_facts.json', 'w'), indent=1)
print("facts ok: tot", round(tot,1), "od", len(od), "over1y", over1y, "growth", round(growth,1),
      "top3share", round(top3share,1), "lift", round(lift,1), "lead", round(leadMean))
print("charts:", len(line_chart(mvals)), len(pareto([(k, v[1], v[0]) for k, v in mechs[:6]])),
      len(aging_chart(ag)), len(lead_chart(leads)))

# expose for next step
import pickle
pickle.dump(facts, open('_facts.pkl', 'wb'))
print("saved _facts.pkl")