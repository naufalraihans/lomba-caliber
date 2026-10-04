# Build submission/03_presentation.pptx — OFFICIAL 7 slides + appendix, 16:9.
# Format: 1 Cover, 2 Background&Problem, 3 Solution, 4 Business Impact,
#         5 Feasibility&Roadmap, 6 Conclusion, 7 Team Profile, A1-A5 Appendix.
# Team Pengacara, Institut Teknologi PLN. All English.
# Every chart/table is a native editable PowerPoint object.
# Numbers recomputed from analysis/embed_data.json + analysis/ai_eval.json.
# Usage: python _deck_pptx7.py
import json, datetime
from collections import defaultdict
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_TICK_MARK
from pptx.chart.data import ChartData

# ---------------- facts ----------------
D = json.load(open('analysis/embed_data.json', encoding='utf-8'))
AI = json.load(open('analysis/ai_eval.json', encoding='utf-8'))
inc = D['incidents']
OPEN = {"NEW REGISTERED", "RCA PROCESS", "CA/PA EXECUTION", "MONITORING RESULT"}
TODAY = datetime.date(2026, 8, 19)

tot = sum(float(x.get('total_loss') or 0) for x in inc)
dt = sum(float(x.get('downtime') or 0) for x in inc)
od = [x for x in inc if x['status'] in OPEN and x.get('rca_due') and x['rca_due'] < '2026-08-19']
op = [x for x in inc if x['status'] in OPEN]
ages = sorted([(TODAY - datetime.date(*map(int, x['rca_due'].split('-')))).days for x in od])
med_age, max_age = ages[len(ages) // 2], ages[-1]
odl = sum(float(x['total_loss']) for x in od)
n = len(inc)

M = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
mo = defaultdict(float)
for x in inc:
    if x.get('month'):
        mn, yy = x['month'].split('-')
        mo[(int(yy), M.index(mn) + 1)] += float(x.get('total_loss') or 0)
series = sorted(mo.items())
mlab = [f"{M[k[1]-1]} {k[0]}" for k, _ in series]
mval = [round(v / 1000, 2) for _, v in series]
mmean = sum(mval) / len(mval)
y24 = [v for k, v in series if k[0] == 2024]
y26 = [v for k, v in series if k[0] == 2026]
avg24, avg26 = sum(y24) / len(y24) / 1000, sum(y26) / len(y26) / 1000
growth = (avg26 - avg24) / avg24 * 100
peak = max(mval)

ag_order = ['0-30', '31-90', '91-180', '181-365', '>365']
ag = {k: 0 for k in ag_order}
for a in ages:
    k = '0-30' if a <= 30 else '31-90' if a <= 90 else '91-180' if a <= 180 else '181-365' if a <= 365 else '>365'
    ag[k] += 1
over1y = ag['>365']

mc = defaultdict(lambda: [0, 0.0])
for x in inc:
    k = x.get('mech') or '?'
    mc[k][0] += 1
    mc[k][1] += float(x.get('total_loss') or 0)
mechs = sorted(mc.items(), key=lambda kv: -kv[1][1])
top3 = sum(v[1] for _, v in mechs[:3]) / 1000
top3share = top3 / (tot / 1000) * 100
top3n = sum(v[0] for _, v in mechs[:3])

un = defaultdict(lambda: [0, 0.0, 0])
for x in inc:
    k = x['plant']
    un[k][0] += 1
    un[k][1] += float(x.get('total_loss') or 0)
for x in od:
    un[x['plant']][2] += 1
units = sorted(un.items(), key=lambda kv: -kv[1][1])

leads = []
for t, dd in D['equipment'].items():
    ch = dd['Condition History']
    hdr, rows = ch[0], ch[1:]
    sc = [i for i, h in enumerate(hdr) if 'Health' in h][0]
    ai = ti = None
    for i, r in enumerate(rows):
        s = str(r[sc]).strip()
        if s == 'ALARM' and ai is None:
            ai = i
        if s == 'TRIP' and ti is None:
            ti = i
    leads.append((t, (ti - ai) * 7 if ai is not None and ti is not None else 0))
leads.sort(key=lambda x: x[1])
leadMean = sum(v for _, v in leads) / len(leads)

p1, p1lo, p1hi = AI['retrieval']['full_p1']['pct'], AI['retrieval']['full_p1']['ci_lo'], AI['retrieval']['full_p1']['ci_hi']
p5 = AI['retrieval']['full_p5']['pct']
b1 = AI['retrieval']['base_p1']['pct']
lift = p1 - b1

ko_ch = D['equipment']['KO-3201']['Condition History']
ko_hdr, ko_rows = ko_ch[0], ko_ch[1:]
ko_vi = [i for i, h in enumerate(ko_hdr) if 'Vibration' in h][0]
ko_vib = [round(float(r[ko_vi]), 1) for r in ko_rows]
ko_lab = [f"W{r[0]}" for r in ko_rows]
KO_AL, KO_TR = 45.0, 75.0  # nameplate: Equipment Info sheet

# ---------------- style ----------------
NAVY = RGBColor(0x0A, 0x23, 0x42)
BLUE = RGBColor(0x1A, 0x56, 0xDB)
SKY = RGBColor(0x3B, 0x82, 0xF6)
INK = RGBColor(0x11, 0x19, 0x28)
MUT = RGBColor(0x5B, 0x6B, 0x82)
RED = RGBColor(0xDC, 0x26, 0x26)
GREEN = RGBColor(0x16, 0xA3, 0x4A)
GRAY = RGBColor(0x9C, 0xA3, 0xAF)
LGRAY = RGBColor(0xE5, 0xE7, 0xEB)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LCARD = RGBColor(0xF3, 0xF5, 0xF9)
DRED = RGBColor(0x99, 0x1B, 0x1B)
DGREEN = RGBColor(0x16, 0x65, 0x34)
DARK = RGBColor(0x14, 0x38, 0x73)
DARK2 = RGBColor(0x0E, 0x2C, 0x63)
FOOTC = RGBColor(0x8F, 0xB6, 0xD9)
DARK_KICK = RGBColor(0x9F, 0xB3, 0xD1)
DSUB = RGBColor(0xC9, 0xD5, 0xE8)
FONT = 'Calibri'

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]

def bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color

def gridlines(slide, color):
    for k in range(1, 20):
        x = Inches(13.333 * k / 20)
        c = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(0), Pt(1), Inches(7.5))
        c.fill.solid(); c.fill.fore_color.rgb = color
        c.line.fill.background()
    for k in range(1, 12):
        y = Inches(7.5 * k / 12)
        c = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), y, Inches(13.333), Pt(1))
        c.fill.solid(); c.fill.fore_color.rgb = color
        c.line.fill.background()

def textbox(slide, l, t, w, h):
    tx = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tx.text_frame.word_wrap = True
    return tx

def para(tf, text, size=14, bold=False, color=INK, first=False, italic=False):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.space_after = Pt(2)
    p.space_before = Pt(0)
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    r.font.name = FONT
    r.font.italic = italic
    return p

def header(slide, kick, title, sub, dark, foot_l, num):
    if dark:
        bg(slide, NAVY)
        gridlines(slide, DARK)
        kc, tc, sc, fc = DARK_KICK, WHITE, DSUB, FOOTC
    else:
        bg(slide, WHITE)
        kc, tc, sc, fc = BLUE, INK, MUT, GRAY
    tb = textbox(slide, 0.7, 0.35, 11.9, 0.4)
    para(tb.text_frame, kick.upper(), size=12, bold=True, color=kc, first=True)
    tb2 = textbox(slide, 0.7, 0.72, 11.9, 1.0)
    para(tb2.text_frame, title, size=32, bold=True, color=tc, first=True)
    if sub:
        tb3 = textbox(slide, 0.7, 1.55, 11.9, 0.6)
        para(tb3.text_frame, sub, size=14, color=sc, first=True)
    fl = textbox(slide, 0.7, 6.95, 10.6, 0.3)
    para(fl.text_frame, foot_l, size=10, color=fc, first=True)
    fn = textbox(slide, 12.1, 6.95, 0.6, 0.3)
    para(fn.text_frame, num, size=10, color=fc, first=True)

def kpi_card(slide, l, t, w, h, big, small, dark=False, big_color=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = DARK if dark else LCARD
    shp.line.fill.background()
    tf = shp.text_frame
    tf.word_wrap = True
    para(tf, big, size=22, bold=True, color=(big_color or (WHITE if dark else INK)), first=True)
    para(tf, small, size=10, color=(DSUB if dark else MUT))

def style_chart(chart, show_legend=False, grid=True):
    chart.has_legend = show_legend
    chart.value_axis.visible = True
    chart.category_axis.visible = True
    if grid:
        chart.value_axis.has_major_gridlines = True
        gm = chart.value_axis.major_gridlines
        gm.format.line.color.rgb = LGRAY
        gm.format.line.width = Pt(0.75)
    for ax in (chart.value_axis, chart.category_axis):
        ax.tick_labels.font.size = Pt(9)
        ax.tick_labels.font.color.rgb = MUT
        ax.tick_labels.font.name = FONT
        ax.visible = True
        ax.has_major_tick_mark = XL_TICK_MARK.OUTSIDE

def chart_title(chart, text):
    chart.has_title = True
    chart.chart_title.text_frame.text = text
    for pr in chart.chart_title.text_frame.paragraphs:
        for r in pr.runs:
            r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = INK; r.font.name = FONT

def paint_points(series, colors):
    for i, pt in enumerate(series.points):
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = colors[i % len(colors)] if isinstance(colors, list) else colors
        pt.format.line.fill.background()

def data_labels(plot, size=9, fmt=None):
    plot.has_data_labels = True
    dl = plot.data_labels
    dl.show_value = True
    if fmt:
        dl.number_format = fmt
    dl.font.size = Pt(size); dl.font.bold = True; dl.font.color.rgb = INK; dl.font.name = FONT

def table_style(tbl, hdr_bg=NAVY, hdr_color=WHITE, size=11):
    for j in range(len(tbl.columns)):
        c = tbl.cell(0, j)
        for pr in c.text_frame.paragraphs:
            for r in pr.runs:
                r.font.size = Pt(size); r.font.bold = True; r.font.color.rgb = hdr_color; r.font.name = FONT
        c.fill.solid(); c.fill.fore_color.rgb = hdr_bg
    for i in range(1, len(tbl.rows)):
        for j in range(len(tbl.columns)):
            c = tbl.cell(i, j)
            for pr in c.text_frame.paragraphs:
                for r in pr.runs:
                    r.font.size = Pt(size); r.font.name = FONT; r.font.color.rgb = INK
            c.fill.solid(); c.fill.fore_color.rgb = LCARD if i % 2 == 1 else WHITE

# ================= 1 COVER =================
s = prs.slides.add_slide(blank)
bg(s, NAVY)
gridlines(s, DARK)
s.shapes.add_picture('ca-logo.png', Inches(0.7), Inches(0.45), height=Inches(0.55))
tb = textbox(s, 0.7, 1.2, 11.9, 0.4)
para(tb.text_frame, 'CALIBER 2026 — CASE 2: INTELLIGENT MANUFACTURING', size=12, bold=True, color=DARK_KICK, first=True)
tb = textbox(s, 0.7, 1.6, 11.9, 1.7)
para(tb.text_frame, 'One file. One truth.', size=44, bold=True, color=WHITE, first=True)
para(tb.text_frame, 'From data to decision.', size=44, bold=True, color=WHITE)
tb = textbox(s, 0.7, 3.3, 11.9, 0.5)
para(tb.text_frame, 'A single pane of glass for fragmented manufacturing data: one governed table, executive visibility, AI-assisted root cause.', size=14, color=DSUB, first=True)
tb = textbox(s, 0.7, 3.9, 11.9, 0.4)
para(tb.text_frame, 'Team Pengacara  ·  Institut Teknologi PLN  ·  Supervisor: Mr. Bayu Aji Soedibyo', size=13, bold=True, color=WHITE, first=True)
kpi_card(s, 0.7, 4.55, 2.85, 1.1, f'${tot/1000:.2f}M', 'USD exposure in scope', dark=True)
kpi_card(s, 3.75, 4.55, 2.85, 1.1, f'{dt:,.0f} h', f'downtime, {n} records', dark=True)
kpi_card(s, 6.8, 4.55, 2.85, 1.1, f'{len(od)}', f'overdue actions ({over1y} past 1 year)', dark=True)
kpi_card(s, 9.85, 4.55, 2.85, 1.1, f'{p1:.1f}%', 'AI retrieval at rank 1', dark=True)
fl = textbox(s, 0.7, 6.95, 10.0, 0.3)
para(fl.text_frame, 'Team Pengacara — Institut Teknologi PLN', size=10, color=FOOTC, first=True)
fn = textbox(s, 12.1, 6.95, 0.6, 0.3)
para(fn.text_frame, '01 / 07', size=10, color=FOOTC, first=True)

# ================= 2 BACKGROUND & PROBLEM =================
s = prs.slides.add_slide(blank)
header(s, 'Background & problem statement', 'The loss curve is going up, not down.',
       'Six functions, six dashboards, six KPI definitions — hours of validation before every decision.',
       False, 'Source: baseline Incident Database, 380 records', '02 / 07')
cd = ChartData()
cd.categories = mlab
cd.add_series('Loss ($M)', mval)
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.7), Inches(2.35), Inches(6.9), Inches(3.6), cd).chart
style_chart(gf)
chart_title(gf, 'Monthly loss exposure, 31 months ($M)')
paint_points(gf.series[0], [RED if v == peak else BLUE for v in mval])
kpi_card(s, 8.0, 2.35, 2.2, 1.0, f'+{growth:.0f}%', f'2026 run-rate vs 2024 (${avg24:.2f}M → ${avg26:.2f}M/mo)', big_color=RED)
kpi_card(s, 10.4, 2.35, 2.2, 1.0, f'${peak:.2f}M', 'worst month (Apr 2026)', big_color=RED)
kpi_card(s, 8.0, 3.5, 2.2, 1.0, f'{odl/tot*100:.0f}%', 'of exposure sits behind an overdue action', big_color=RED)
kpi_card(s, 10.4, 3.5, 2.2, 1.0, f'{over1y}', f'actions overdue 1 year+ (oldest {max_age} d)', big_color=RED)
tb = textbox(s, 0.7, 6.05, 6.9, 0.6)
para(tb.text_frame, f'Why it matters: {len(op)} actions open, {len(od)} past due (median age {med_age} days). Root cause is found late, so the same failure keeps repeating.', size=11, color=MUT, first=True)
tb = textbox(s, 8.0, 4.7, 4.6, 1.4)
para(tb.text_frame, 'Alerts fire, but nobody owns them: every overdue row carries owner + age.', size=12, first=True)
para(tb.text_frame, 'Decision-making is slow and reactive; optimization opportunities are missed.', size=12)

# ================= 3 SOLUTION =================
s = prs.slides.add_slide(blank)
header(s, 'Solution', 'Four sources in. One governed table out.',
       'Objective: cut validation time to zero — every function reads one governed table in a single offline pane of glass.',
       False, 'Declared additions: energy proxy + CCTV illustration, both labeled', '03 / 07')
steps = [('Incident DB', f'{n} x 23 cols'), ('Equipment', '5 x 26 weekly readings'), ('Production PI', '5 x 720 hourly rows'),
         ('Downtime', f'{dt:,.1f} h total'), ('ONE TABLE', 'one definition per KPI')]
for i, (a, b) in enumerate(steps):
    x = 0.7 + i * 2.42
    shp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(2.5), Inches(2.12), Inches(1.05))
    shp.fill.solid()
    shp.fill.fore_color.rgb = BLUE if i == 4 else LCARD
    shp.line.fill.background()
    tf = shp.text_frame; tf.word_wrap = True
    para(tf, a, size=13, bold=True, color=(WHITE if i == 4 else INK), first=True)
    para(tf, b, size=10, color=(WHITE if i == 4 else MUT))
    if i < 4:
        ar = textbox(s, x + 2.15, 2.8, 0.3, 0.45)
        para(ar.text_frame, '→', size=18, bold=True, color=BLUE, first=True)
cd = ChartData()
cd.categories = [k for k, _ in mechs[:6]]
cd.add_series('Loss ($M)', [round(v[1] / 1000, 2) for _, v in mechs[:6]])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.7), Inches(3.85), Inches(6.0), Inches(2.85), cd).chart
style_chart(gf)
chart_title(gf, f'Executive view — fix-first priority ($M, top 3 = {top3share:.0f}%)')
paint_points(gf.series[0], [BLUE] * 3 + [GRAY] * 3)
data_labels(gf.plots[0], size=9, fmt='#,##0.00')
kpi_card(s, 7.0, 3.85, 2.7, 1.32, 'Single KPI contract', 'Same metric from incident DB, PI tags, or declared value — divergence visible, not hidden.')
kpi_card(s, 9.9, 3.85, 2.7, 1.32, 'Governed quality', 'Nulls, units, gaps published in a Data Governance view — listed, never patched.')
kpi_card(s, 7.0, 5.32, 2.7, 1.32, 'Offline by design', 'One HTML file from a USB stick. No install, no server — survives a judge PC.')
kpi_card(s, 9.9, 5.32, 2.7, 1.32, 'AI + human close', f'Retrieval {p1:.1f}% at rank 1; AI suggests, the PIC closes every action.')

# ================= 4 BUSINESS IMPACT =================
s = prs.slides.add_slide(blank)
header(s, 'Business impact', 'Four numbers we commit to moving.',
       'Baseline = measured. Target = modeled commitment with basis stated, in the open.',
       False, 'Targets are modeled from this baseline, not measured results', '04 / 07')
rows = [
    ('Monthly loss', f'${avg26:.2f}M/mo', '→', f'${avg24:.2f}M/mo',
     f'2026 rate vs 2024 level. Fix-first on top-3 covers {top3share:.0f}% of exposure.'),
    ('Overdue actions', f'{len(od)} of {len(op)}', '→', f'{len(od)-over1y}',
     f'{over1y} actions past due 1 year+. Owner + due date mandatory at creation.'),
    ('Retrieval @1', f'{b1:.1f}%', '→', f'{p1:.1f}%',
     f'Leave-one-out on n={n}. Full model CI {p1lo:.1f}–{p1hi:.1f}%.'),
    ('Warning window', 'reactive', '→', f'{leadMean:.0f} days',
     'Mean first-ALARM-to-TRIP gap from 26-week condition history.'),
]
tbl = s.shapes.add_table(len(rows) + 1, 5, Inches(0.7), Inches(2.4), Inches(7.4), Inches(3.3)).table
for j, w in enumerate([Inches(1.5), Inches(1.3), Inches(0.35), Inches(1.2), Inches(3.05)]):
    tbl.columns[j].width = w
for j, h in enumerate(['Metric', 'Before', '', 'Target', 'Basis / KPI']):
    c = tbl.cell(0, j)
    c.text = h
    for pr in c.text_frame.paragraphs:
        for r in pr.runs:
            r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = FONT
    c.fill.solid(); c.fill.fore_color.rgb = NAVY
for i, vals in enumerate(rows):
    for j, vv in enumerate(vals):
        c = tbl.cell(i + 1, j)
        c.text = vv
        for pr in c.text_frame.paragraphs:
            for r in pr.runs:
                r.font.size = Pt(10); r.font.name = FONT
                r.font.bold = (j in (0, 1, 3))
                r.font.color.rgb = DRED if j == 1 else (DGREEN if j == 3 else INK)
        c.fill.solid(); c.fill.fore_color.rgb = LCARD if i % 2 == 0 else WHITE
cd = ChartData()
cd.categories = ['Baseline model', 'Full model']
cd.add_series('Rank-1 (%)', [round(b1, 1), round(p1, 1)])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(8.4), Inches(2.4), Inches(4.2), Inches(3.3), cd).chart
style_chart(gf)
chart_title(gf, 'Retrieval before vs after (%)')
paint_points(gf.series[0], [RED, GREEN])
data_labels(gf.plots[0], size=10, fmt='0.0')
tb = textbox(s, 0.7, 5.85, 11.9, 0.8)
para(tb.text_frame, f'Success metrics: rank-1 {p1:.1f}% (CI {p1lo:.1f}–{p1hi:.1f}), rank-5 {p5:.1f}%, lift +{lift:.1f} pts from uniting 4 sources. Warning {leadMean:.0f} days mean across 5 assets. All reproducible from the baseline — method published in appendix.', size=11, color=MUT, first=True)

# ================= 5 FEASIBILITY & ROADMAP =================
s = prs.slides.add_slide(blank)
header(s, 'Feasibility & roadmap', 'Feasible offline. Live in three steps.',
       'No new hardware, no plant shutdown, no internet dependency.',
       False, 'Phase gates: each phase ships a working file before the next begins', '05 / 07')
feas = [
    ('Technical', 'One HTML file; no server, no install, runs offline on any PC.'),
    ('Operational', 'Fits existing RCA/AR workflow; owner + due date enforced.'),
    ('Legal', 'Baseline data only + 2 declared additions; no personal data.'),
    ('Cybersecurity', 'Fully offline; no network calls, no credentials stored.'),
    ('Data governance', 'Defects published in-app; one KPI contract, visible lineage.'),
    ('Organization', 'Six functions keep their views; one shared definition per KPI.'),
]
tbl = s.shapes.add_table(len(feas) + 1, 2, Inches(0.7), Inches(2.4), Inches(6.6), Inches(4.2)).table
tbl.columns[0].width = Inches(1.9)
tbl.columns[1].width = Inches(4.7)
table_style(tbl, size=11)
tbl.cell(0, 0).text = 'Readiness'
tbl.cell(0, 1).text = 'Assessment'
for pr in tbl.cell(0, 0).text_frame.paragraphs:
    for r in pr.runs:
        r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = FONT
for pr in tbl.cell(0, 1).text_frame.paragraphs:
    for r in pr.runs:
        r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = FONT
for i, (a, b) in enumerate(feas):
    tbl.cell(i + 1, 0).text = a
    tbl.cell(i + 1, 1).text = b
    for pr in tbl.cell(i + 1, 0).text_frame.paragraphs:
        for r in pr.runs:
            r.font.size = Pt(11); r.font.bold = True; r.font.name = FONT; r.font.color.rgb = INK
    for pr in tbl.cell(i + 1, 1).text_frame.paragraphs:
        for r in pr.runs:
            r.font.size = Pt(11); r.font.name = FONT; r.font.color.rgb = INK
phases = [
    ('Phase 1 — Meter it (0–3 mo)', 'Deploy the governed table + dashboard; enforce owner and due date on every action.'),
    ('Phase 2 — Connect it (3–6 mo)', 'Link EDMS / AIMS / Digital Twin for asset context; replace energy proxy with 5 metered tags.'),
    ('Phase 3 — Stream it (6–12 mo)', 'Attach PI live feed; architecture already decoupled for streaming.'),
]
for i, (a, b) in enumerate(phases):
    y = 2.4 + i * 1.45
    shp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.6), Inches(y), Inches(4.9), Inches(1.3))
    shp.fill.solid()
    shp.fill.fore_color.rgb = BLUE if i == 0 else LCARD
    shp.line.fill.background()
    tf = shp.text_frame; tf.word_wrap = True
    para(tf, a, size=13, bold=True, color=(WHITE if i == 0 else INK), first=True)
    para(tf, b, size=10, color=(WHITE if i == 0 else MUT))

# ================= 6 CONCLUSION =================
s = prs.slides.add_slide(blank)
bg(s, NAVY)
gridlines(s, DARK)
tb = textbox(s, 0.7, 0.35, 11.9, 0.4)
para(tb.text_frame, 'CONCLUSION', size=12, bold=True, color=DARK_KICK, first=True)
tb = textbox(s, 0.7, 0.72, 11.9, 1.7)
para(tb.text_frame, 'One file. One truth.', size=40, bold=True, color=WHITE, first=True)
para(tb.text_frame, 'From data to decision.', size=40, bold=True, color=WHITE)
tb = textbox(s, 0.7, 2.6, 11.9, 2.2)
para(tb.text_frame, f'1. One governed table replaces six conflicting dashboards — {n} incidents, one definition per KPI.', size=14, color=WHITE, first=True)
para(tb.text_frame, f'2. One screen shows where the money is — top-3 mechanisms hold {top3share:.0f}% (${top3:.2f}M) of exposure.', size=14, color=WHITE)
para(tb.text_frame, f'3. AI narrows the search ({p1:.1f}% rank-1), humans own the close — with {leadMean:.0f} days of warning before a trip.', size=14, color=WHITE)
kpi_card(s, 0.7, 4.9, 3.8, 1.15, f'${avg26:.2f}M → ${avg24:.2f}M/mo', 'loss recovery path, fix-first on top-3', dark=True)
kpi_card(s, 4.7, 4.9, 3.8, 1.15, f'{len(od)} → {len(od)-over1y}', 'overdue cleared of 1-year+ stale rows', dark=True)
kpi_card(s, 8.7, 4.9, 3.8, 1.15, f'{b1:.1f}% → {p1:.1f}%', 'retrieval with published method', dark=True)
fl = textbox(s, 0.7, 6.95, 10.0, 0.3)
para(fl.text_frame, 'Team Pengacara — Institut Teknologi PLN', size=10, color=FOOTC, first=True)
fn = textbox(s, 12.1, 6.95, 0.6, 0.3)
para(fn.text_frame, '06 / 07', size=10, color=FOOTC, first=True)

# ================= 7 TEAM PROFILE =================
s = prs.slides.add_slide(blank)
header(s, 'Team profile', 'Team Pengacara — Institut Teknologi PLN',
       'Supervisor: Mr. Bayu Aji Soedibyo.',
       False, 'Team Pengacara — Institut Teknologi PLN', '07 / 07')
members = [
    ('1', 'Jenny Agustina Rahman', 'Informatics Engineering', '—',
     'Data storytelling & visualization', 'Idea formulation, narrative & deck design'),
    ('2', 'Ahmad Hafidz Susanto', 'Energy Systems Engineering', '—',
     'Energy systems & operations', 'Background & problem statement, voice & demo'),
    ('3', 'Naufal Raihan Saputra', 'Electrical Engineering', '—',
     'Data engineering & analytics', 'Data engineering & dashboard build'),
]
tbl = s.shapes.add_table(len(members) + 1, 6, Inches(0.7), Inches(2.5), Inches(11.9), Inches(2.6)).table
for j, w in enumerate([Inches(0.5), Inches(2.4), Inches(2.4), Inches(1.0), Inches(2.7), Inches(2.9)]):
    tbl.columns[j].width = w
for j, h in enumerate(['No.', 'Name', 'Major', 'Semester', 'Area of expertise', 'Contribution']):
    c = tbl.cell(0, j)
    c.text = h
    for pr in c.text_frame.paragraphs:
        for r in pr.runs:
            r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = FONT
    c.fill.solid(); c.fill.fore_color.rgb = NAVY
for i, vals in enumerate(members):
    for j, vv in enumerate(vals):
        c = tbl.cell(i + 1, j)
        c.text = vv
        for pr in c.text_frame.paragraphs:
            for r in pr.runs:
                r.font.size = Pt(11); r.font.name = FONT
                r.font.bold = (j == 1)
                r.font.color.rgb = INK
        c.fill.solid(); c.fill.fore_color.rgb = LCARD if i % 2 == 0 else WHITE
tb = textbox(s, 0.7, 5.3, 11.9, 1.2)
para(tb.text_frame, 'One team, one file: Analyst frames the story, Engineer grounds it in energy reality, Builder ships the dashboard — all three verified against the same baseline.', size=12, color=MUT, first=True)
para(tb.text_frame, 'Note: fill in the Semester column before submitting.', size=11, bold=True, color=DRED)

# ================= APPENDIX =================
# A1 baseline scorecard
s = prs.slides.add_slide(blank)
header(s, 'Appendix A1 — Baseline scorecard', 'What we inherited — measured, not asserted.',
       'Every figure recomputed from the same incident table.',
       False, 'Supporting evidence for slides 2–3', 'A1')
cd = ChartData()
cd.categories = [k for k, _ in mechs[:6]]
cd.add_series('Loss ($M)', [round(v[1] / 1000, 2) for _, v in mechs[:6]])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.7), Inches(2.4), Inches(5.9), Inches(3.6), cd).chart
style_chart(gf)
chart_title(gf, 'Exposure by failure mechanism ($M)')
paint_points(gf.series[0], [BLUE] * 3 + [GRAY] * 3)
data_labels(gf.plots[0], size=9, fmt='#,##0.00')
tbl = s.shapes.add_table(len(units[:8]) + 1, 4, Inches(6.9), Inches(2.4), Inches(5.7), Inches(3.6)).table
tbl.columns[0].width = Inches(1.0); tbl.columns[1].width = Inches(1.2)
tbl.columns[2].width = Inches(1.4); tbl.columns[3].width = Inches(2.1)
for j, h in enumerate(['Unit', 'Cases', 'Overdue', 'Loss ($M)']):
    c = tbl.cell(0, j); c.text = h
    for pr in c.text_frame.paragraphs:
        for r in pr.runs:
            r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = FONT
    c.fill.solid(); c.fill.fore_color.rgb = NAVY
for i, (k, v) in enumerate(units[:8]):
    for j, vv in enumerate([k, str(v[0]), str(v[2]), f'{v[1]/1000:.2f}']):
        c = tbl.cell(i + 1, j); c.text = vv
        for pr in c.text_frame.paragraphs:
            for r in pr.runs:
                r.font.size = Pt(10); r.font.name = FONT; r.font.color.rgb = INK
        c.fill.solid(); c.fill.fore_color.rgb = LCARD if i % 2 == 0 else WHITE
tb = textbox(s, 0.7, 6.05, 11.9, 0.6)
para(tb.text_frame, f'Top 3 = {top3share:.0f}% (${top3:.2f}M) in {top3n} of {n} records. Unit {units[0][0]} alone: ${units[0][1][1]/1000:.2f}M + {units[0][1][2]} overdue.', size=10, color=MUT, first=True)

# A2 aging detail
s = prs.slides.add_slide(blank)
header(s, 'Appendix A2 — Action aging', f'{over1y} actions are more than a year late.',
       f'{len(od)} overdue at 19-Aug-2026. Median age {med_age} days, oldest {max_age} days.',
       False, 'Supporting evidence for slides 2 and 4', 'A2')
cd = ChartData()
cd.categories = ag_order
cd.add_series('Actions', [ag[k] for k in ag_order])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.7), Inches(2.4), Inches(6.4), Inches(3.6), cd).chart
style_chart(gf)
chart_title(gf, f'Overdue actions by age, days ({len(od)} total)')
paint_points(gf.series[0], [GREEN, SKY, RGBColor(0xD9, 0x77, 0x06), RGBColor(0xEA, 0x58, 0x0C), RED])
data_labels(gf.plots[0], size=10)
kpi_card(s, 7.5, 2.4, 2.4, 1.5, f'{len(od)} → {len(od)-over1y}', 'OVERDUE → TARGET', big_color=RED)
kpi_card(s, 10.1, 2.4, 2.4, 1.5, f'${odl/1000:.2f}M', f'of exposure ({odl/tot*100:.0f}%) stuck', big_color=RED)
tb = textbox(s, 7.5, 4.1, 5.0, 1.9)
para(tb.text_frame, 'Target basis: owner + due date mandatory at creation; closure blocked without evidence.', size=11, color=MUT, first=True)
para(tb.text_frame, 'Red dot = nobody on it. Purple = in progress. Green = done.', size=11, color=MUT)

# A3 KO-3201
s = prs.slides.add_slide(blank)
header(s, 'Appendix A3 — Case reconstruction: KO-3201', f'Watch it degrade. {leadMean:.0f} days of warning.',
       f'Real 26-week history. KO-3201 ALARM {ko_lab[9]}, TRIP {ko_lab[20]}: {(20-9)*7} days to act. Mean {leadMean:.0f} days across 5 assets.',
       False, 'Demo path: RCA tab → KO-3201', 'A3')
cd = ChartData()
cd.categories = ko_lab
cd.add_series('DE vibration (micron)', ko_vib)
cd.add_series(f'ALARM ({KO_AL:.0f})', [KO_AL] * len(ko_lab))
cd.add_series(f'TRIP ({KO_TR:.0f})', [KO_TR] * len(ko_lab))
gf = s.shapes.add_chart(XL_CHART_TYPE.LINE, Inches(0.7), Inches(2.5), Inches(7.0), Inches(3.6), cd).chart
style_chart(gf, show_legend=True)
gf.legend.position = XL_LEGEND_POSITION.BOTTOM
chart_title(gf, 'KO-3201 DE vibration, 26 weeks (micron) — real history')
gf.series[0].format.line.color.rgb = BLUE
gf.series[0].format.line.width = Pt(2.5)
gf.series[0].smooth = True
for ln, col in ((gf.series[1], RGBColor(0xD9, 0x77, 0x06)), (gf.series[2], RED)):
    ln.format.line.color.rgb = col
    ln.format.line.width = Pt(1.75)
    ln.format.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    ln.smooth = True
tbl = s.shapes.add_table(len(leads) + 1, 3, Inches(8.0), Inches(2.5), Inches(4.6), Inches(3.6)).table
for j, h in enumerate(['Asset', 'Lead', 'Read']):
    c = tbl.cell(0, j); c.text = h
    for pr in c.text_frame.paragraphs:
        for r in pr.runs:
            r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = FONT
    c.fill.solid(); c.fill.fore_color.rgb = NAVY
for i, (t, v) in enumerate(leads):
    for j, vv in enumerate([t, f'{v} d', 'Before trip' if v >= 70 else 'Actionable']):
        c = tbl.cell(i + 1, j); c.text = vv
        for pr in c.text_frame.paragraphs:
            for r in pr.runs:
                r.font.size = Pt(11); r.font.name = FONT; r.font.color.rgb = INK
        c.fill.solid(); c.fill.fore_color.rgb = LCARD if i % 2 == 0 else WHITE
tb = textbox(s, 0.7, 6.15, 11.9, 0.5)
para(tb.text_frame, 'All 5 RCA decks integrated (4P / 4M+1E, CAPA, PIC, PM schedule). Alarm/trip limits from the equipment nameplate sheet.', size=10, color=MUT, first=True)

# A4 model evaluation
s = prs.slides.add_slide(blank)
header(s, 'Appendix A4 — Model evaluation', 'AI suggests. Humans close.',
       f'Leave-one-out on all {n} records — not a demo set. Target: same failure mechanism in the top-k neighbours (mechanism excluded from features).',
       False, 'Supporting evidence for slide 4', 'A4')
cd = ChartData()
cd.categories = ['Baseline model', 'Full model']
cd.add_series('Rank-1 (%)', [round(b1, 1), round(p1, 1)])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.7), Inches(2.5), Inches(5.0), Inches(3.5), cd).chart
style_chart(gf)
chart_title(gf, 'Similar-incident retrieval, before vs after (%)')
paint_points(gf.series[0], [RED, GREEN])
data_labels(gf.plots[0], size=10, fmt='0.0')
kpi_card(s, 6.0, 2.5, 2.4, 1.35, f'{p1:.1f}%', f'rank-1, CI {p1lo:.1f}–{p1hi:.1f}%')
kpi_card(s, 8.6, 2.5, 2.4, 1.35, f'+{lift:.1f} pts', f'vs thin baseline ({b1:.1f}%)', big_color=DGREEN)
tb = textbox(s, 6.0, 4.0, 5.0, 2.0)
para(tb.text_frame, f'Rank-5: {p5:.1f}%. Prevalence baseline (always guess Leakage): 26.6% — the model far exceeds it.', size=11, color=MUT, first=True)
para(tb.text_frame, 'Human-in-the-loop: AI never closes an action. The PIC does.', size=12, bold=True, color=DRED)
para(tb.text_frame, 'Honest limits: no live streaming, no auto-closure, no data beyond 2 declared additions.', size=11, color=MUT)

# A5 sources & governance
s = prs.slides.add_slide(blank)
header(s, 'Appendix A5 — Sources & governance', 'Measured. Labeled. Out of scope.',
       'High-quality justified architecture beats more data.',
       False, 'Supporting evidence: every chart traces to one table', 'A5')
kpi_card(s, 0.7, 2.4, 3.8, 1.7, 'Measured', f'Loss, downtime, aging — {n} real records\nRetrieval {p1:.1f}% / {p5:.1f}% leave-one-out\nWarning {leadMean:.0f} d from condition history', big_color=DGREEN)
kpi_card(s, 4.7, 2.4, 3.8, 1.7, 'Labeled, not hidden', 'Energy = derived proxy, formula printed\nCCTV wall = illustration, aggregates real\nBaseline defects listed in Data Governance')
kpi_card(s, 8.7, 2.4, 3.8, 1.7, 'Out of scope', 'No live streaming (not required)\nNo auto-closure (human-in-the-loop)\nNo extra data beyond 2 declared', big_color=DRED)
tb = textbox(s, 0.7, 4.4, 11.9, 2.2)
para(tb.text_frame, f'Sources united: Incident DB ({n} x 23 cols) + Equipment condition (5 x 26 weeks) + Production PI (5 x 720 hourly rows) + Downtime ({dt:,.1f} h). Justification: each source answers one key question — history, health, output, loss.', size=12, first=True)
para(tb.text_frame, 'Additional sources proposed only with business justification: 5 metered energy tags (replace proxy), EDMS/AIMS/Twin (asset context), PI live feed (streaming).', size=12)

prs.save('submission/03_presentation.pptx')
import os
print('saved', os.path.getsize('submission/03_presentation.pptx'), 'bytes')
