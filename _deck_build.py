# Build data-centric deck.html. Reuses _deck_facts.py (facts + SVG chart builders).
import json, base64, html, datetime

G = {}
exec(open('_deck_facts.py', encoding='utf-8').read(), G)

line_chart, hbars, pareto, ba_bar, aging_chart, lead_chart, spark = (
    G['line_chart'], G['hbars'], G['pareto'], G['ba_bar'], G['aging_chart'], G['lead_chart'], G['spark'])
facts = G['facts']
C = G['C']

tot, dt, n = facts['tot'], facts['dt'], facts['n']
nopen, nod, odl, odlp = facts['nopen'], facts['nod'], facts['odl'], facts['odlp']
over1y, ag = facts['over1y'], facts['ag']
growth, avg24, avg26, mmean = facts['growth'], facts['avg24'], facts['avg26'], facts['mmean']
top3, top3share = facts['top3'], facts['top3share']
p1, p1lo, p1hi, p5, b1, lift = facts['p1'], facts['p1lo'], facts['p1hi'], facts['p5'], facts['b1'], facts['lift']
leadMean, mvals, mechs, units, leads = facts['leadMean'], facts['mvals'], facts['mechs'], facts['units'], facts['leads']

logo = base64.b64encode(open('ca-logo.png', 'rb').read()).decode()

# modeled target: recover to 2024 monthly level
tgt_mo = avg24
tgt_mo_cut = (avg26 - tgt_mo) / avg26 * 100

ch_line   = line_chart(mvals, avg=mmean)
ch_pareto = pareto([(k, v[1], v[0]) for k, v in mechs[:6]])
ch_units  = hbars([(k, v[1], f"{v[2]} od") for k, v in units[:6]], unit='$')
ch_aging  = aging_chart(ag)
ch_lead   = lead_chart(leads)
ch_spark  = spark(mvals)

ch_ba_mo   = ba_bar(avg26, tgt_mo, 'BASELINE 2026', 'TARGET', fmt='usd', note=f'+{growth:.0f}% vs 2024')
ch_ba_od   = ba_bar(nod, nod - over1y, 'OVERDUE NOW', 'TARGET', fmt='int', note=f'{over1y} >1 year')
ch_ba_ret  = ba_bar(b1, p1, 'BASELINE MODEL', 'FULL MODEL', fmt='pct', note='feature-lite')
ch_ba_lead = ba_bar(0.1, leadMean, 'REACTIVE', 'WITH CONDITION', fmt='int', note='no early warn')

mech_rows = ''.join(
    f'<tr><td><b>{i+1}</b></td><td>{html.escape(k)}</td><td class="num">{v[0]}</td>'
    f'<td class="num">${v[1]/1000:.2f}M</td><td class="num">{v[1]/tot*100:.1f}%</td>'
    f'<td><span class="bar"><i style="width:{v[1]/mechs[0][1][1]*100:.0f}%"></i></span></td></tr>'
    for i, (k, v) in enumerate(mechs[:5]))

unit_rows = ''.join(
    f'<tr><td><b>{i+1}</b></td><td><span class="tag">{html.escape(k)}</span></td><td class="num">{v[0]}</td>'
    f'<td class="num">{v[2]}</td><td class="num">${v[1]/1000:.2f}M</td>'
    f'<td><span class="bar"><i style="width:{v[1]/units[0][1][1]*100:.0f}%"></i></span></td></tr>'
    for i, (k, v) in enumerate(units[:6]))

lead_rows = ''.join(
    f'<tr><td><span class="tag">{html.escape(t)}</span></td><td class="num">{v} d</td>'
    f'<td class="num">{"Before trip" if v>=70 else "Actionable"}</td></tr>' for t, v in leads)

# before/after matrix
BAS = [
    ('Monthly loss', f'${avg26/1000:.2f}M/mo', f'${tgt_mo/1000:.2f}M/mo', f'-{tgt_mo_cut:.0f}%',
     f'2026 running rate vs 2024 level. Fix-first on top-3 mechanisms covers {top3share:.0f}% of exposure.', 'line'),
    ('Overdue actions', f'{nod} of {nopen}', f'{nod-over1y}', '-61%',
     f'{over1y} actions already past due by 1 year+. Board forces an owner and a due date at creation.', 'int'),
    ('Retrieval @1', f'{b1:.1f}%', f'{p1:.1f}%', f'+{lift:.1f} pts',
     f'Both measured leave-one-out on n={n}. Full model CI {p1lo:.1f}-{p1hi:.1f}%.', 'pct'),
    ('Warning window', 'reactive', f'{leadMean:.0f} days', 'new',
     'Mean gap between first ALARM week and TRIP week across all 5 assets, from 26-week condition history.', 'int'),
]

def badge(delta, kind):
    col = 'g' if kind == 'good' else 'a'
    return f'<span class="dlt {col}">{html.escape(delta)}</span>'

bas_html = ''
for i, (name, before, after, delta, method, _k) in enumerate(BAS):
    bas_html += f'''<tr><td class="bn">{html.escape(name)}</td><td class="bb">{html.escape(before)}</td>
<td class="ar">&#8594;</td><td class="ba">{html.escape(after)}</td><td>{badge(delta,'good')}</td>
<td class="meth">{html.escape(method)}</td></tr>'''

def foot(l, r): return f'<div class="foot"><span>{l}</span><span>{r}</span></div>'
def kick(s): return f'<div class="kick">{s}</div>'

HTML = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CALIBER 2026 - Case 2 - Presentation Deck</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{--navy:#0A2342;--blue:#1A56DB;--sky:#3B82F6;--bg:#F3F5F9;--mut:#5B6B82;--red:#DC2626;--green:#16A34A;--amber:#D97706;--line:#E5E7EB}}
html,body{{background:#0B1526;-webkit-font-smoothing:antialiased}}
body{{font:15.5px/1.5 "Plus Jakarta Sans",-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:#111928}}
.stage{{min-height:92vh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:20px}}
.slide{{width:min(1200px,96vw);aspect-ratio:16/9;background:#fff;border-radius:16px;padding:44px 52px 54px;display:none;flex-direction:column;position:relative;overflow:hidden}}
.slide.on{{display:flex}}
.slide.dark{{background:linear-gradient(135deg,#0A2342 0%,#16336E 55%,#1A56DB 100%);color:#fff}}
.kick{{font-size:11.5px;font-weight:800;letter-spacing:2.4px;color:var(--sky);text-transform:uppercase;margin-bottom:8px}}
.dark .kick{{color:#9FB3D1}}
h1{{font-size:44px;line-height:1.1;letter-spacing:-.025em;font-weight:800}}
h2{{font-size:31px;line-height:1.15;letter-spacing:-.02em;font-weight:800}}
h3{{font-size:14px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--mut);margin-bottom:8px}}
.dark h1,.dark h2{{color:#fff}}
.sub{{color:var(--mut);font-size:15.5px;max-width:940px;margin-top:6px}}
.dark .sub{{color:#C9D5E8}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:16px;align-items:start}}
.grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:13px;margin-top:16px}}
.grid4{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:14px}}
.grid23{{display:grid;grid-template-columns:1.15fr 1fr;gap:24px;margin-top:14px;align-items:start}}
.stat{{background:var(--bg);border:1px solid var(--line);border-radius:12px;padding:13px 15px}}
.stat b{{display:block;font-size:27px;letter-spacing:-.03em;line-height:1.1}}
.stat span{{font-size:11.5px;color:var(--mut);font-weight:600;display:block;margin-top:3px;line-height:1.35}}
.dark .stat{{background:rgba(255,255,255,.11);border-color:rgba(255,255,255,.18)}}
.dark .stat span{{color:#C9D5E8}}
.stat .sp{{margin-top:8px;display:block}}
.spark{{width:100%;height:34px;display:block}}
.chart{{width:100%;height:auto;display:block}}
.pane{{border:1.5px solid var(--line);border-radius:13px;padding:14px 16px 10px;background:#fff}}
.pane h3{{margin-bottom:6px}}
.pane .cap{{font-size:11.5px;color:var(--mut);margin-top:2px;line-height:1.4}}
table{{width:100%;border-collapse:collapse;font-size:12.5px}}
th{{text-align:left;font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--mut);padding:7px 6px;border-bottom:1.5px solid var(--line)}}
td{{padding:7px 6px;border-bottom:1px solid #F1F5F9;vertical-align:middle}}
td.num{{text-align:right;font-weight:700;font-variant-numeric:tabular-nums}}
th.num{{text-align:right}}
.tag{{display:inline-block;font-weight:800;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12px}}
.bar{{display:block;height:7px;background:#F1F5F9;border-radius:99px;overflow:hidden;min-width:70px}}
.bar i{{display:block;height:100%;background:var(--blue);border-radius:99px}}
.chain{{display:flex;gap:0;margin-top:16px;flex-wrap:wrap;align-items:stretch}}
.step{{flex:1;min-width:110px;background:var(--bg);border:1px solid var(--line);padding:12px 10px;font-size:12.5px;font-weight:800;text-align:center}}
.step small{{display:block;font-weight:600;color:var(--mut);font-size:10.5px;margin-top:3px;font-variant-numeric:tabular-nums}}
.step:first-child{{border-radius:11px 0 0 11px}}
.step:last-child{{border-radius:0 11px 11px 0;background:#DBEAFE;border-color:#BFDBFE}}
.arr{{align-self:center;padding:0 7px;color:var(--sky);font-weight:800;font-size:16px}}
.logo{{height:42px;background:#fff;border-radius:9px;padding:5px 13px}}
ul.tight{{list-style:none;margin-top:11px}}
ul.tight li{{font-size:14.5px;padding:5px 0 5px 26px;position:relative;line-height:1.45}}
ul.tight li:before{{content:"";position:absolute;left:2px;top:9px;width:11px;height:11px;border-radius:3px;background:var(--sky)}}
ul.tight li.g:before{{background:var(--green)}}ul.tight li.r:before{{background:var(--red)}}ul.tight li.a:before{{background:var(--amber)}}
.pill{{display:inline-block;font-size:11.5px;font-weight:800;border-radius:999px;padding:3px 11px;margin:2px 5px 2px 0}}
.p-r{{background:#FEE2E2;color:#991B1B}}.p-g{{background:#DCFCE7;color:#166534}}.p-a{{background:#FEF3C7;color:#92400E}}.p-b{{background:#DBEAFE;color:#1D4ED8}}
.baml{{width:100%;border-collapse:collapse;font-size:13px;margin-top:10px}}
.baml td{{padding:9px 7px;border-bottom:1px solid var(--line)}}
.baml .bn{{font-weight:800;width:15%}}
.baml .bb{{color:var(--red);font-weight:700;width:12%;font-variant-numeric:tabular-nums}}
.baml .ar{{color:#9CA3AF;width:3%;text-align:center}}
.baml .ba{{color:var(--green);font-weight:800;width:13%;font-variant-numeric:tabular-nums}}
.baml .meth{{color:var(--mut);font-size:11.5px;line-height:1.4}}
.dlt{{display:inline-block;font-size:11px;font-weight:800;border-radius:7px;padding:2px 8px}}
.dlt.g{{background:#DCFCE7;color:#166534}}
.foot{{position:absolute;bottom:17px;left:52px;right:52px;display:flex;justify-content:space-between;font-size:11px;color:#9AA7BD;font-weight:600}}
.dark .foot{{color:#9FB3D1}}
.src{{font-size:10.5px;color:#9AA7BD;margin-top:7px;font-weight:600}}
.nav{{display:flex;align-items:center;gap:13px;color:#C9D5E8;font-size:12.5px;font-weight:700;padding:4px 0 18px}}
.nav button{{background:rgba(255,255,255,.14);color:#fff;border:0;border-radius:9px;padding:8px 17px;font-size:13.5px;font-weight:700;cursor:pointer;font-family:inherit}}
.nav button:hover{{background:rgba(255,255,255,.3)}}
.dots{{display:flex;gap:7px}}
.dots i{{width:9px;height:9px;border-radius:50%;background:rgba(255,255,255,.28);cursor:pointer}}
.dots i.on{{background:#fff}}
@keyframes rise{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:none}}}}
.slide.on>*{{animation:rise .4s both}}
@media print{{
html,body{{background:#fff}}.stage{{padding:0;display:block;min-height:auto}}
.slide{{display:flex;width:100%;aspect-ratio:auto;height:100vh;max-height:100vh;page-break-after:always;page-break-inside:avoid;border-radius:0;overflow:hidden;padding:44px 52px 54px}}
.slide:last-child{{page-break-after:auto}}
.nav{{display:none}}.slide.on>*{{animation:none}}
}}
</style>
</head>
<body>
<div class="stage">

<!-- 1 COVER -->
<section class="slide dark on">
<img class="logo" src="data:image/png;base64,{logo}" alt="Chandra Asri">
<div class="kick" style="margin-top:16px">CALIBER 2026 &mdash; Case 2: Intelligent Manufacturing</div>
<h1>One file. One truth.<br>From data to decision.</h1>
<p class="sub">380 incidents over 31 months, read from a single governed table. No server, no internet, no install.</p>
<div class="grid4">
<div class="stat"><b>${tot/1000:.2f}M</b><span>USD exposure in scope</span></div>
<div class="stat"><b>${dt:,.0f} h</b><span>downtime across {n} records</span></div>
<div class="stat"><b>{nod}</b><span>overdue actions ({over1y} past 1 year)</span></div>
<div class="stat"><b>{p1:.1f}%</b><span>AI retrieval @ rank 1</span><span class="sp">{ch_spark}</span></div>
</div>
<div class="src" style="color:#9FB3D1">Monthly loss exposure, Jan 2024 &rarr; Jul 2026 &mdash; peak ${max(mvals)/1000:.1f}M, average ${mmean/1000:.2f}M per month.</div>
{foot('Jenny &middot; Hafidz &middot; Naufal &mdash; Advisor: Mr. Bayu Aji', '01 / 11')}
</section>

<!-- 2 PROBLEM WITH DATA -->
<section class="slide">
{kick('The problem, quantified')}
<h2>The loss curve is going up, not down.</h2>
<div class="grid23">
<div class="pane"><h3>Monthly loss exposure &mdash; 31 months</h3>
{ch_line}
<div class="cap">Real baseline from the incident database. Dashed line = long-run average ${mmean/1000:.2f}M/month.</div></div>
<div>
<div class="grid2" style="margin-top:0">
<div class="stat"><b style="color:var(--red)">+{growth:.0f}%</b><span>2026 run-rate vs 2024 (${avg24/1000:.2f}M &rarr; ${avg26/1000:.2f}M/mo)</span></div>
<div class="stat"><b style="color:var(--red)">${max(mvals)/1000:.2f}M</b><span>worst single month (Apr 2026)</span></div>
<div class="stat"><b style="color:var(--red)">${odlp:.0f}%</b><span>of exposure sits behind an overdue action</span></div>
<div class="stat"><b style="color:var(--red)">{over1y}</b><span>actions already overdue by more than a year</span></div>
</div>
<ul class="tight">
<li class="r">Six functions, six dashboards, six KPI definitions &mdash; time spent validating before deciding.</li>
<li class="a">Alerts fire, but nobody owns them: {nopen} actions open, {nod} past due.</li>
<li class="r">Root cause found late, so the same mechanism keeps repeating.</li>
</ul>
</div>
</div>
{foot('Source: baseline Incident Database, 380 records x 23 columns', '02 / 11')}
</section>

<!-- 3 BASELINE SCORECARD -->
<section class="slide">
{kick('Baseline scorecard')}
<h2>What we inherited &mdash; measured, not asserted.</h2>
<div class="grid23">
<div class="pane"><h3>Exposure by failure mechanism</h3>
<table><thead><tr><th>#</th><th>Mechanism</th><th class="num">Cases</th><th class="num">Loss</th><th class="num">Share</th><th></th></tr></thead>
<tbody>{mech_rows}</tbody></table>
<div class="cap">Top 3 mechanisms = {top3share:.0f}% of total exposure (${top3/1000:.2f}M of ${tot/1000:.2f}M) in just {sum(v[0] for _, v in mechs[:3])} of {n} records.</div></div>
<div class="pane"><h3>Where the money is, by unit</h3>
<table><thead><tr><th>#</th><th>Unit</th><th class="num">Cases</th><th class="num">Overdue</th><th class="num">Loss</th><th></th></tr></thead>
<tbody>{unit_rows}</tbody></table>
<div class="cap">Unit {units[0][0]} alone carries ${units[0][1][1]/1000:.2f}M and {units[0][1][2]} overdue actions.</div></div>
</div>
<div class="grid4" style="margin-top:14px">
<div class="stat"><b>{n}</b><span>incidents / 23 columns</span></div>
<div class="stat"><b>5</b><span>assets x 26 weeks condition</span></div>
<div class="stat"><b>5 x 721</b><span>hourly PI production rows</span></div>
<div class="stat"><b>5</b><span>structured RCA decks (4P / 4M+1E)</span></div>
</div>
{foot('Every figure on this slide is recomputed from the same table', '03 / 11')}
</section>

<!-- 4 Q1 FOUNDATION -->
<section class="slide">
{kick('Key question 1 &mdash; Data foundation')}
<h2>Four sources in. One governed table out.</h2>
<p class="sub">Every chart on every tab reads the same incident table. Edit one record, every figure recomputes.</p>
<div class="chain">
<div class="step">Incident DB<small>{n} x 23 cols</small></div><span class="arr">&rarr;</span>
<div class="step">Equipment<small>5 x 26 weeks</small></div><span class="arr">&rarr;</span>
<div class="step">Production PI<small>5 x 721 rows</small></div><span class="arr">&rarr;</span>
<div class="step">Downtime<small>{dt:,.1f} h total</small></div><span class="arr">&rarr;</span>
<div class="step">ONE TABLE<small>feeds {11} views</small></div>
</div>
<div class="grid3" style="margin-top:18px">
<div class="pane"><h3>Single definition</h3><div class="cap">One KPI contract: the same metric computed from incident DB, PI tags, or declared value, side by side &mdash; divergence is visible instead of hidden.</div></div>
<div class="pane"><h3>Governed, not scraped</h3><div class="cap">Baseline defects are published in a Data Governance tab rather than silently patched: nulls, inconsistent units, and gaps are listed.</div></div>
<div class="pane"><h3>Offline by design</h3><div class="cap">One HTML file. Runs from a USB stick with no install, no build step, no server &mdash; survives a judge's machine with no internet.</div></div>
</div>
{foot('Declared additions: energy proxy + CCTV illustration, both labeled', '04 / 11')}
</section>

<!-- 5 Q2 SINGLE PANE -->
<section class="slide">
{kick('Key question 2 &mdash; Single pane of glass')}
<h2>The executive view, in one screen.</h2>
<div class="grid2">
<div class="pane"><h3>Fix-first priority &mdash; Pareto of loss</h3>{ch_pareto}
<div class="cap">Blue = top 3. Red dashes = cumulative share. Tapping a bar filters the incident list to that mechanism.</div></div>
<div class="pane"><h3>Unit ranking &mdash; loss with overdue count</h3>{ch_units}
<div class="cap">Bar = loss in USD. <b>od</b> = overdue actions behind that unit. Tap to filter.</div></div>
</div>
<div class="grid4" style="margin-top:13px">
<div class="stat"><b>${tot/1000:.2f}M</b><span>hero exposure card</span></div>
<div class="stat"><b>{nod}</b><span>overdue, owner + age on every row</span></div>
<div class="stat"><b>11</b><span>views, every KPI clickable to source</span></div>
<div class="stat"><b>0</b><span>charts without a data provenance link</span></div>
</div>
{foot('Trip logsheet: one row per trip, colored duration + follow-up dot', '05 / 11')}
</section>

<!-- 6 OVERDUE AGING -->
<section class="slide">
{kick('Action tracking &mdash; aging of overdue')}
<h2>{over1y} actions are more than a year late.</h2>
<div class="grid23">
<div class="pane"><h3>Overdue actions by age ({nod} total)</h3>{ch_aging}
<div class="cap">Real distribution of {nod} overdue actions measured at 19-Aug-2026. Median age 463 days, oldest 926 days.</div></div>
<div class="pane"><h3>Before vs target</h3>{ch_ba_od}
<div class="cap"><b>Target basis:</b> every action gets an owner and a due date at creation, so nothing can age past its due date &mdash; the board blocks closure without evidence.</div>
<ul class="tight" style="margin-top:6px">
<li class="g">Red dot = nobody on it. Purple = in progress. Green = done.</li>
<li class="a">Overdue carries ${odl/1000:.2f}M of exposure ({odlp:.0f}% of total).</li>
</ul></div>
</div>
{foot('Target is a modeled commitment, not a measured result', '06 / 11')}
</section>

<!-- 7 Q3 AI -->
<section class="slide">
{kick('Key question 3 &mdash; AI root cause')}
<h2>AI suggests. Humans close.</h2>
<div class="grid23">
<div class="pane"><h3>Similar-incident retrieval, before vs after</h3>
<div class="grid2" style="margin-top:4px">
<div>{ch_ba_ret}</div>
<div class="pane" style="border:0;padding:0">
<ul class="tight" style="margin-top:4px">
<li class="g"><b>{p1:.1f}%</b> correct match at rank 1 (full model)</li>
<li class="g"><b>{p5:.1f}%</b> at rank 5</li>
<li class="a">Baseline model with thin features: <b>{b1:.1f}%</b></li>
<li><b>+{lift:.1f} points</b> from uniting the four sources</li>
</ul></div></div>
<div class="cap">Both numbers measured leave-one-out on all {n} records &mdash; not a demo set. Full model 95% CI {p1lo:.1f}–{p1hi:.1f}%.</div></div>
<div>
<div class="grid2" style="margin-top:0">
<div class="stat"><b>{p1:.1f}%</b><span>rank-1 retrieval, CI {p1lo:.1f}-{p1hi:.1f}%</span></div>
<div class="stat"><b>+{lift:.1f} pts</b><span>vs feature-lite baseline ({b1:.1f}%)</span></div>
</div>
<ul class="tight">
<li class="g">Problem tank &rarr; root-cause indication &rarr; prioritized alerts &rarr; tracked action.</li>
<li class="g"><b>Top-10 exposure plan</b> drafted in one click, each row with owner + PM schedule.</li>
<li class="r">Human-in-the-loop: AI never closes an action, the PIC does.</li>
</ul>
<div class="src">Full method, confidence intervals and honest limits published in the Model Evaluation tab.</div>
</div>
</div>
{foot('Measurable, reproducible, published', '07 / 11')}
</section>

<!-- 8 KO-3201 + LEAD -->
<section class="slide">
{kick('Case reconstruction &mdash; compressor KO-3201')}
<h2>From signal to owner, and {leadMean:.0f} days of warning.</h2>
<div class="chain">
<div class="step">Signal<small>vibration trend</small></div><span class="arr">&rarr;</span>
<div class="step">Alarm<small>week flagged</small></div><span class="arr">&rarr;</span>
<div class="step">Trip<small>downtime logged</small></div><span class="arr">&rarr;</span>
<div class="step">Loss<small>USD in table</small></div><span class="arr">&rarr;</span>
<div class="step">Owner + CAPA<small>PIC &middot; PM schedule</small></div>
</div>
<div class="grid23" style="margin-top:14px">
<div class="pane"><h3>Warning window per asset &mdash; first ALARM &rarr; TRIP</h3>{ch_lead}
<div class="cap">Real gap from 26-week condition history. Mean <b>{leadMean:.0f} days</b>, range {min(v for _, v in leads)}&ndash;{max(v for _, v in leads)} days &mdash; the time available to act before a trip.</div></div>
<div class="pane"><h3>Why it matters</h3>
<table><thead><tr><th>Asset</th><th class="num">Lead</th><th class="num">Read</th></tr></thead><tbody>{lead_rows}</tbody></table>
<div class="cap">All 5 RCA decks integrated (4P / 4M+1E, CAPA, PIC, status, PM schedule) &mdash; chronology and correlation one tap from any row.</div></div>
</div>
{foot('Demo path: RCA tab &rarr; KO-3201', '08 / 11')}
</section>

<!-- 9 BEFORE vs AFTER -->
<section class="slide dark">
{kick('Impact &mdash; before vs target')}
<h2>Four numbers we commit to moving.</h2>
<p class="sub">Baseline column = measured from the committee data. Target column = modeled commitment with its basis stated.</p>
<table class="baml" style="background:rgba(255,255,255,.07);border-radius:12px;overflow:hidden">
<thead><tr><th class="bn" style="color:#9FB3D1">Metric</th><th class="bb" style="color:#FCA5A5">Before</th><th class="ar" style="color:#9FB3D1"></th><th class="ba" style="color:#86EFAC">Target</th><th style="color:#9FB3D1"></th><th class="meth" style="color:#C9D5E8">Basis</th></tr></thead>
<tbody>{bas_html}</tbody></table>
<div class="src" style="color:#9FB3D1;margin-top:11px">Targets are modeled from this baseline, not measured results. We publish the basis so the assumption can be challenged, not the number.</div>
{foot('Loss recovery target = return to 2024 monthly level', '09 / 11')}
</section>

<!-- 10 HONEST -->
<section class="slide">
{kick('Impact &mdash; stated honestly')}
<h2>What we measure, what we label, what we skip.</h2>
<div class="grid3">
<div class="pane"><h3>Measured</h3><ul class="tight" style="margin-top:2px">
<li class="g">Loss, downtime, overdue aging &mdash; from {n} real records</li>
<li class="g">Retrieval {p1:.1f}% / {p5:.1f}% leave-one-out</li>
<li class="g">Warning window {leadMean:.0f} days from condition history</li></ul></div>
<div class="pane"><h3>Labeled, not hidden</h3><ul class="tight" style="margin-top:2px">
<li class="a">Energy = derived proxy, formula printed on the slide</li>
<li class="a">CCTV wall = illustration, unit aggregates underneath are real</li>
<li class="a">Baseline defects listed in Data Governance</li></ul></div>
<div class="pane"><h3>Out of scope</h3><ul class="tight" style="margin-top:2px">
<li class="r">No live streaming (not required) &mdash; ready for PI stream</li>
<li class="r">No automated closure &mdash; human-in-the-loop by design</li>
<li class="r">No extra data beyond two declared additions</li></ul></div>
</div>
<div class="grid4" style="margin-top:15px">
<div class="stat"><b>{top3share:.0f}%</b><span>of exposure fixable by top-3 focus</span></div>
<div class="stat"><b>${top3/1000:.2f}M</b><span>addressable in 3 mechanisms</span></div>
<div class="stat"><b>{over1y}</b><span>stale actions surfaced with age</span></div>
<div class="stat"><b>{leadMean:.0f} d</b><span>average early-warning window</span></div>
</div>
{foot('Honest limits score higher than hidden guesses', '10 / 11')}
</section>

<!-- 11 TEAM -->
<section class="slide dark">
{kick('Team &amp; next')}
<h2>Jenny &middot; Hafidz &middot; Naufal</h2>
<p class="sub">Advisor: Mr. Bayu Aji. Built from the official baseline only, plus two declared additions.</p>
<div class="grid3" style="margin-top:20px">
<div class="stat"><b style="font-size:19px">1 &mdash; Meter it</b><span>5 metered energy tags to replace the proxy formula</span></div>
<div class="stat"><b style="font-size:19px">2 &mdash; Connect it</b><span>EDMS / AIMS / Digital Twin for asset context</span></div>
<div class="stat"><b style="font-size:19px">3 &mdash; Stream it</b><span>PI live feed, architecture already decoupled for it</span></div>
</div>
<p style="margin-top:26px;font-size:20px;color:#fff;font-weight:700">One file. One truth. From data to decision.</p>
{foot('CALIBER 2026 &mdash; Case 2: Intelligent Manufacturing', '11 / 11')}
</section>

</div>
<div class="stage" style="min-height:auto;padding-top:0">
<div class="nav">
<button onclick="go(-1)">&#8592; Prev</button>
<div class="dots" id="dots"></div>
<button onclick="go(1)">Next &#8594;</button>
<span id="cnt">1 / 11</span>
<span style="opacity:.65">Arrows or click &middot; F11 fullscreen &middot; Print to PDF</span>
</div>
</div>
<script>
let i=0;const S=[...document.querySelectorAll(".slide")];const D=document.getElementById("dots");
S.forEach((_,k)=>{{const d=document.createElement("i");d.onclick=()=>show(k);D.appendChild(d);}});
function show(k){{i=(k+S.length)%S.length;S.forEach((s,j)=>s.classList.toggle("on",j===i));[...D.children].forEach((d,j)=>d.classList.toggle("on",j===i));document.getElementById("cnt").textContent=(i+1)+" / "+S.length;}}
function go(d){{show(i+d);}}
document.addEventListener("keydown",e=>{{if(e.key==="ArrowRight"||e.key===" ")go(1);if(e.key==="ArrowLeft")go(-1);}});
document.querySelector(".stage").addEventListener("click",e=>{{if(e.target.closest(".slide")&&!e.target.closest("button"))go(1);}});
show(0);
</script>
</body>
</html>
'''

open('deck.html', 'w', encoding='utf-8').write(HTML)
import os
print("deck.html", os.path.getsize('deck.html'), "bytes | slides:", HTML.count('<section class="slide'))
print("targets:", round(avg24), "cut%", round(tgt_mo_cut, 1))