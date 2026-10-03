import json, html, base64
D = json.load(open('analysis/embed_data.json'))
AI = json.load(open('analysis/ai_eval.json'))
inc = D['incidents']
OPEN = {"NEW REGISTERED", "RCA PROCESS", "CA/PA EXECUTION", "MONITORING RESULT"}
TODAY = "2026-08-19"

tot = sum(float(x.get('total_loss') or 0) for x in inc)
dt = sum(float(x.get('downtime') or 0) for x in inc)
n = len(inc)
op = [x for x in inc if x['status'] in OPEN]
od = [x for x in op if x.get('rca_due') and x['rca_due'] < TODAY]
odl = sum(float(x['total_loss']) for x in od)
closed = [x for x in inc if x['status'] in ('RISK CLOSED', 'RISK CANCELED')]

M = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
mo = {}
for x in inc:
    if x.get('month'):
        mn, yy = x['month'].split('-')
        k = (int(yy), M.index(mn)+1)
        mo[k] = mo.get(k, 0) + float(x.get('total_loss') or 0)
ser = sorted(mo.items())
mv = [v for _, v in ser]
mmean = sum(mv)/len(mv)
a24 = sum(v for k, v in ser if k[0] == 2024)/12
y26 = [v for k, v in ser if k[0] == 2026]
a26 = sum(y26)/len(y26)
growth = (a26-a24)/a24*100

ag = {'0-30':0,'31-90':0,'91-180':0,'181-365':0,'>365':0}
for x in od:
    d = x['rca_due']
    import datetime as _dt
    a = (_dt.date(2026,8,19) - _dt.date(*map(int, d.split('-')))).days
    k = '0-30' if a<=30 else '31-90' if a<=90 else '91-180' if a<=180 else '181-365' if a<=365 else '>365'
    ag[k] += 1
o1y = ag['>365']
import statistics as _st
ages = [ (_dt.date(2026,8,19) - _dt.date(*map(int,x['rca_due'].split('-')))).days for x in od ]
medage = int(_st.median(ages)); maxage = max(ages)

mc = {}
for x in inc:
    k = x.get('mech') or '?'
    a = mc.setdefault(k, [0,0.0,0.0]); a[0]+=1; a[1]+=float(x.get('total_loss') or 0); a[2]+=float(x.get('downtime') or 0)
mk = sorted(mc, key=lambda k: -mc[k][1])
top3 = sum(mc[k][1] for k in mk[:3]); top3share = top3/tot*100

un = {}
for x in inc:
    a = un.setdefault(x['plant'], [0,0.0,0]); a[0]+=1; a[1]+=float(x.get('total_loss') or 0)
for x in od: un[x['plant']][2]+=1
uk = sorted(un, key=lambda k: -un[k][1])

leads = []
for t, d in D['equipment'].items():
    ch = d['Condition History']; hdr = ch[0]; rows = ch[1:]
    sc = len(hdr)-2; ai = ti = None
    for i, r in enumerate(rows):
        s = str(r[sc]).strip()
        if s=='ALARM' and ai is None: ai=i
        if s=='TRIP' and ti is None: ti=i
    leads.append((t, (ti-ai)*7 if ai is not None and ti is not None else 0))
leads.sort(key=lambda x: x[1])
lmean = sum(l[1] for l in leads)/len(leads)

r = AI['retrieval']
p1 = r['full_p1']['pct']; p1lo = r['full_p1']['ci_lo']; p1hi = r['full_p1']['ci_hi']
p5 = r['full_p5']['pct']; b1 = r['base_p1']['pct']; lift = p1-b1

# KO-3201 vibration
ch = D['equipment']['KO-3201']['Condition History']; hdr = ch[0]; rows = ch[1:]
vib = [float(x[2]) for x in rows]
vst = [str(x[6]).strip() for x in rows]

clsA = sum(1 for x in inc if x['eq_class']=='A')

F = dict(tot=tot, dt=dt, n=n, nopen=len(op), nod=len(od), nclosed=len(closed), odl=odl,
         o1y=o1y, medage=medage, maxage=maxage, growth=growth, a24=a24, a26=a26, mmean=mmean,
         top3=top3, top3share=top3share, p1=p1, p1lo=p1lo, p1hi=p1hi, p5=p5, b1=b1, lift=lift,
         lmean=lmean, clsA=clsA, medcase=medage)
json.dump(F, open('_F.json','w'), indent=1)
json.dump({'ser':[[k[0],k[1],round(v,1)] for k,v in ser], 'mv':[round(v,1) for v in mv],
           'ag':ag, 'mk':mk[:6], 'mech':{k:mc[k] for k in mk[:6]}, 'uk':uk[:6], 'unit':{k:un[k] for k in uk[:6]},
           'leads':leads, 'vib':vib, 'vst':vst}, open('_S.json','w'))
print('facts ok')
for k in ['tot','dt','n','nopen','nod','nclosed','o1y','medage','maxage','growth','top3share','p1','b1','lift','lmean','clsA']:
    v=F[k]; print(' ', k, round(v,2) if isinstance(v,float) else v)