import json, base64
F = json.load(open('_F.json'))
S = json.load(open('_S.json'))
LOGO = open('_logo64.txt').read().strip()
mv = S['mv']; mx = max(mv)
MECH = [(k, S['mech'][k][0], S['mech'][k][1]) for k in S['mk']]
UNT = [(k, S['unit'][k][0], S['unit'][k][1], S['unit'][k][2]) for k in S['uk']]
AG = S['ag']; LEADS = S['leads']; VIB = S['vib']; VST = S['vst']
tot = F['tot']

def usd(v):
    return ('$%.2fM' % (v/1000))

# monthly bars (real Jan-24..Jul-26 labels)
MN = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
ser = S.get('ser', [])
bars = ''.join(
    '<i class="%s" style="--h:%.1f%%" title="%s: %s"></i>' % (
        'peak' if v == mx else '',
        v/mx*100,
        '%s %s' % (MN[m-1], str(y)[2:]), usd(v))
    for (y, m, v) in ser) if ser else ''.join(
    '<i style="--h:%.1f%%;%s" title="%s: %s"></i>' % (
        v/mx*100,
        'background:var(--red)' if v == mx else ('background:var(--amber)' if v > F['mmean'] else ''),
        'M%d' % (i+1), usd(v))
    for i, v in enumerate(mv))

# pareto svg
W, H, P = 600, 230, {'l': 8, 'r': 8, 't': 26, 'b': 52}
m0 = MECH[0][2]; tall = sum(m[2] for m in MECH)
n = len(MECH); slot = (W-P['l']-P['r'])/n; bw = slot*0.58; ih = H-P['t']-P['b']
pg = ["<svg viewBox='0 0 %d %d' class='chart'>" % (W, H)]
cum = 0; cpts = []
for i, (k, c, v) in enumerate(MECH):
    cum += v
    bh = max(4, v/m0*ih); x = P['l']+i*slot+(slot-bw)/2; y = P['t']+ih-bh
    col = '#1A56DB' if i < 3 else '#9CA3AF'
    pg.append("<rect class='grow' x='%.1f' y='%.1f' width='%.1f' height='%.1f' rx='5' fill='%s'/>" % (x, y, bw, bh, col))
    pg.append("<text x='%.1f' y='%.1f' text-anchor='middle' font-size='12' font-weight='800' fill='#0A2342'>%s</text>" % (x+bw/2, y-7, usd(v)))
    pg.append("<text x='%.1f' y='%d' text-anchor='middle' font-size='11' font-weight='700' fill='#0A2342'>%s</text>" % (x+bw/2, H-30, k[:13]))
    pg.append("<text x='%.1f' y='%d' text-anchor='middle' font-size='10' fill='#5B6B82'>%d cases</text>" % (x+bw/2, H-14, c))
    cpts.append((x+bw/2, P['t']+ih-(cum/tall)*ih, cum/tall))
pg.append("<polyline class='drawline' points='" + ' '.join('%.1f,%.1f' % (a, b) for a, b, _ in cpts) + "' fill='none' stroke='#DC2626' stroke-width='2.4'/>")
for a, b, pc in cpts:
    pg.append("<circle cx='%.1f' cy='%.1f' r='4' fill='#DC2626'/>" % (a, b))
a, b, pc = cpts[2]
pg.append("<text x='%.1f' y='%.1f' text-anchor='middle' font-size='13' font-weight='800' fill='#DC2626'>cum %.0f%%</text>" % (a, b-11, pc*100))
pg.append('</svg>')
pareto = ''.join(pg)

# unit bars html
umx = UNT[0][2]
units = ''.join(
    "<div class='urow'><span class='ulab'>%s</span><span class='utrack'><i class='fill' style='--w:%.0f%%'></i></span><b>%s</b><span class='uod'>%d od</span></div>" % (
        k, v/umx*100, usd(v), od)
    for k, c, v, od in UNT)

# aging bars
akeys = ['0-30', '31-90', '91-180', '181-365', '>365']
acols = ['#16A34A', '#3B82F6', '#D97706', '#EA580C', '#DC2626']
amx = max(AG.values())
aging = ''.join(
    "<div class='agcol'><b style='color:%s'>%d</b><span class='agtrack'><i class='fillv' style='--h:%.0f%%;background:%s'></i></span><span>%s</span><em>days</em></div>" % (
        acol, AG[k], AG[k]/amx*100, acol, k)
    for k, acol in zip(akeys, acols))

# leads bars
lmx = max(v for _, v in LEADS)
leadh = ''.join(
    "<div class='agcol'><b style='color:#16A34A'>%dd</b><span class='agtrack'><i class='fillv' style='--h:%.0f%%;background:#16A34A'></i></span><span>%s</span></div>" % (
        v, v/lmx*100, t)
    for t, v in LEADS)

# vibration svg with zones
VW, VH = 620, 200
plo, pro, pto, pbo = 44, 12, 14, 30
vlo, vhi = 20, 82
iw, ih = VW-plo-pro, VH-pto-pbo
def VX(i): return plo + i/(len(VIB)-1)*iw
def VY(v): return pto + ih - (v-vlo)/(vhi-vlo)*ih
vg = ["<svg viewBox='0 0 %d %d' class='chart' id='vibsvg'>" % (VW, VH)]
vg.append("<rect x='%d' y='%d' width='%d' height='%.1f' fill='#16A34A' opacity='.08'/>" % (plo, pto, iw, VY(37.7)-pto))
vg.append("<rect x='%d' y='%.1f' width='%d' height='%.1f' fill='#D97706' opacity='.12'/>" % (plo, VY(37.7), iw, VY(37.7)-VY(37.7)+ (VY(76.5)-VY(37.7)) if False else VY(37.7)-VY(37.7)))
vg.append("<rect x='%d' y='%.1f' width='%d' height='%.1f' fill='#D97706' opacity='.12'/>" % (plo, VY(76.5), iw, VY(37.7)-VY(76.5)))
vg.append("<line x1='%d' y1='%.1f' x2='%d' y2='%.1f' stroke='#D97706' stroke-width='1.6' stroke-dasharray='6 4'/>" % (plo, VY(37.7), VW-pro, VY(37.7)))
vg.append("<text x='%d' y='%.1f' font-size='10' font-weight='800' fill='#D97706'>ALARM ~38</text>" % (VW-pro-64, VY(37.7)-6))
vg.append("<line x1='%d' y1='%.1f' x2='%d' y2='%.1f' stroke='#DC2626' stroke-width='1.6' stroke-dasharray='6 4'/>" % (plo, VY(71.0), VW-pro, VY(71.0)))
vg.append("<text x='%d' y='%.1f' font-size='10' font-weight='800' fill='#DC2626'>TRIP ~71</text>" % (VW-pro-58, VY(71.0)-6))
pts = ' '.join('%.1f,%.1f' % (VX(i), VY(v)) for i, v in enumerate(VIB))
vg.append("<polyline id='vibline' points='%s' fill='none' stroke='#1A56DB' stroke-width='2.6' stroke-linejoin='round'/>" % pts)
vg.append("<circle id='vibdot' r='6' fill='#DC2626' stroke='#fff' stroke-width='2.5'/>")
for i in (0, 8, 20, 25):
    vg.append("<text x='%.1f' y='%d' text-anchor='middle' font-size='10' fill='#5B6B82'>W%d</text>" % (VX(i), VH-8, i+1))
vg.append('</svg>')
vibsvg = ''.join(vg)

# sparkline cover
SW, SH = 260, 44
smx = max(mv)
sp = ' '.join('%.1f,%.1f' % (i/(len(mv)-1)*SW, SH-(v/smx)*SH) for i, v in enumerate(mv))
spark = "<svg viewBox='0 0 %d %d' class='spark'><polyline points='%s' fill='none' stroke='#7DD3FC' stroke-width='2.2'/></svg>" % (SW, SH, sp)

# CI whisker
ci = ("<svg viewBox='0 0 300 54' class='chart'><line x1='20' y1='27' x2='280' y2='27' stroke='#E5E7EB' stroke-width='6' stroke-linecap='round'/>"
      "<line x1='%.1f' y1='27' x2='%.1f' y2='27' stroke='#1A56DB' stroke-width='6' stroke-linecap='round'/>"
      "<circle cx='%.1f' cy='27' r='9' fill='#1A56DB' stroke='#fff' stroke-width='3'/>"
      "<text x='20' y='50' font-size='10' fill='#5B6B82'>%.1f%%</text>"
      "<text x='280' y='50' text-anchor='end' font-size='10' fill='#5B6B82'>%.1f%%</text></svg>") % (
      20+(F['p1lo']/100)*260, 20+(F['p1hi']/100)*260, 20+(F['p1']/100)*260, F['p1lo'], F['p1hi'])

def BAB(before, after, blab, alab, kind, note=''):
    if kind == 'usd': bt, at = usd(before), usd(after)
    elif kind == 'pct': bt, at = ('%.1f%%' % before), ('%.1f%%' % after)
    else: bt, at = ('%d' % before), ('%d' % after)
    mxv = max(before, after) or 1
    hb = before/mxv*100; ha = after/mxv*100
    s = ("<div class='babar'><div class='bacol'><b class='bc-b'>" + bt + "</b>"
         "<span class='batrack'><i class='fillv' style='--h:" + ("%.0f" % hb) + "%;background:#DC2626'></i></span><span>" + blab + "</span></div>"
         "<div class='baarr'>&#8594;</div>"
         "<div class='bacol'><b class='bc-a'>" + at + "</b>"
         "<span class='batrack'><i class='fillv' style='--h:" + ("%.0f" % ha) + "%;background:#16A34A'></i></span><span>" + alab + "</span></div></div>")
    if note:
        s += "<div class='banote'>" + note + "</div>"
    return s

T = open('_deck_template.html', encoding='utf-8').read() if False else None
print('partials ok', len(bars), len(pareto), len(vibsvg))
json.dump({'bars': bars, 'pareto': pareto, 'units': units, 'aging': aging, 'leadh': leadh,
           'vibsvg': vibsvg, 'spark': spark, 'ci': ci,
           'ba_mo': BAB(F['a26'], F['a24'], 'BASELINE 2026', 'TARGET', 'usd', 'fix-first on top-3 = %.0f%% of exposure' % F['top3share']),
           'ba_od': BAB(F['nod'], F['nod']-F['o1y'], 'OVERDUE NOW', 'TARGET', 'int', '%d actions >1 year old drop out' % F['o1y']),
           'ba_ret': BAB(F['b1'], F['p1'], 'BASELINE MODEL', 'FULL MODEL', 'pct', '+%.1f pts from uniting 4 sources' % F['lift']),
           'ba_lead': BAB(1, F['lmean'], 'REACTIVE', 'WITH CONDITION', 'int', 'mean ALARM-to-TRIP gap, 26-week history')},
          open('_P.json', 'w'))
print('saved _P.json')
