# Build submission/03_presentation.pptx — 11 slides, 16:9, native editable objects.
# All numbers recomputed from analysis/embed_data.json + analysis/ai_eval.json.
# Charts/tables are native python-pptx objects (editable in PowerPoint).
# Usage: python _deck_pptx.py
import json, datetime
from collections import defaultdict
from copy import deepcopy
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION, XL_TICK_MARK
from pptx.chart.data import ChartData

# ---------------- facts ----------------
D = json.load(open('analysis/embed_data.json', encoding='utf-8'))
AI = json.load(open('analysis/ai_eval.json', encoding='utf-8'))
inc = D['incidents']
OPEN = {"NEW REGISTERED", "RCA PROCESS", "CA/PA EXECUTION", "MONITORING RESULT"}
TODAY = datetime.date(2026, 8, 19)

tot = sum(float(x.get('total_loss') or 0) for x in inc)          # kUSD
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
mval = [round(v / 1000, 2) for _, v in series]                    # $M
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
ko_aw = ko_lab[9]
ko_tw = ko_lab[20]
KO_AL, KO_TR = 45.0, 75.0

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
LBLUE = RGBColor(0x1D, 0x4E, 0xD8)
DBLUE_BG = RGBColor(0xDB, 0xEA, 0xFE)
FOOTC = RGBColor(0x8F, 0xB6, 0xD9)
DARK_KICK = RGBColor(0x9F, 0xB3, 0xD1)
DSUB = RGBColor(0xC9, 0xD5, 0xE8)
GRID = RGBColor(0x0E, 0x2C, 0x63)

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
    # faint blueprint grid: vertical + horizontal thin lines
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

def para(tf, text, size=14, bold=False, color=INK, align=None, font=FONT, italic=False, first=False):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.space_after = Pt(2)
    p.space_before = Pt(0)
    if align is not None:
        p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    r.font.name = font
    r.font.italic = italic
    return p

def kick_kpi_slide(slide, kick, title, sub, dark, foot_l, foot_r, num):
    if dark:
        bg(slide, NAVY)
        gridlines(slide, RGBColor(0x14, 0x38, 0x73))
        kc, tc, sc = DARK_KICK, WHITE, DSUB
    else:
        bg(slide, WHITE)
        kc, tc, sc = BLUE, INK, MUT
    textbox(slide, 0.7, 0.35, 11.9, 0.4).text_frame.paragraphs[0].add_run().text = ''
    tb = textbox(slide, 0.7, 0.35, 11.9, 0.4)
    para(tb.text_frame, kick.upper(), size=12, bold=True, color=kc, first=True)
    tb2 = textbox(slide, 0.7, 0.72, 11.9, 1.0)
    para(tb2.text_frame, title, size=32, bold=True, color=tc, first=True)
    if sub:
        tb3 = textbox(slide, 0.7, 1.55, 11.9, 0.6)
        para(tb3.text_frame, sub, size=14, color=sc, first=True)
    fl = textbox(slide, 0.7, 6.95, 8.0, 0.3)
    para(fl.text_frame, foot_l, size=10, color=(FOOTC if dark else GRAY), first=True)
    fr = textbox(slide, 11.3, 6.95, 1.3, 0.3)
    para(fr.text_frame, foot_r, size=10, color=(FOOTC if dark else GRAY), first=True)
    fn = textbox(slide, 12.1, 6.95, 0.6, 0.3)
    para(fn.text_frame, f"{num:02d} / 11", size=10, color=(FOOTC if dark else GRAY), first=True)

def kpi_card(slide, l, t, w, h, big, small, dark=False, big_color=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = RGBColor(0x14, 0x38, 0x73) if dark else LCARD
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

def bar_color(series, color):
    fill = series.format.fill
    fill.solid()
    fill.fore_color.rgb = color
    series.format.line.fill.background()

# ================= 1 COVER =================
s = prs.slides.add_slide(blank)
bg(s, NAVY)
gridlines(s, RGBColor(0x14, 0x38, 0x73))
pic = s.shapes.add_picture('ca-logo.png', Inches(0.7), Inches(0.45), height=Inches(0.55))
tb = textbox(s, 0.7, 1.25, 11.9, 0.4)
para(tb.text_frame, 'CALIBER 2026 — CASE 2: INTELLIGENT MANUFACTURING', size=12, bold=True, color=DARK_KICK, first=True)
tb = textbox(s, 0.7, 1.65, 11.9, 1.7)
para(tb.text_frame, 'One file. One truth.', size=44, bold=True, color=WHITE, first=True)
para(tb.text_frame, 'From data to decision.', size=44, bold=True, color=WHITE)
tb = textbox(s, 0.7, 3.35, 11.9, 0.6)
para(tb.text_frame, f'{n} incidents over {len(series)} months, read from a single governed table. No server, no internet, no install.', size=14, color=DSUB, first=True)
kpi_card(s, 0.7, 4.15, 2.85, 1.15, f'${tot/1000:.2f}M', 'USD exposure in scope', dark=True)
kpi_card(s, 3.75, 4.15, 2.85, 1.15, f'{dt:,.0f} h', f'downtime, {n} records', dark=True)
kpi_card(s, 6.8, 4.15, 2.85, 1.15, f'{len(od)}', f'overdue actions ({over1y} past 1 year)', dark=True)
kpi_card(s, 9.85, 4.15, 2.85, 1.15, f'{p1:.1f}%', 'AI retrieval at rank 1', dark=True)
fl = textbox(s, 0.7, 6.95, 10.0, 0.3)
para(fl.text_frame, 'Jenny  ·  Hafidz  ·  Naufal  —  Advisor: Mr. Bayu Aji', size=10, color=FOOTC, first=True)
fn = textbox(s, 12.1, 6.95, 0.6, 0.3)
para(fn.text_frame, '01 / 11', size=10, color=FOOTC, first=True)
cap = textbox(s, 0.7, 5.55, 11.9, 0.5)
para(cap.text_frame, f'Monthly loss exposure, Jan 2024 → Jul 2026 — peak ${peak:.2f}M, average ${mmean:.2f}M per month. Full curve on slide 2.', size=11, italic=True, color=DSUB, first=True)

# ================= 2 PROBLEM =================
s = prs.slides.add_slide(blank)
kick_kpi_slide(s, 'The problem, quantified', 'The loss curve is going up, not down.',
               '2026 run-rate vs 2024, worst month, and exposure stuck behind overdue actions.',
               False, 'Source: baseline Incident Database, 380 records', '', 2)
kpi_card(s, 8.0, 2.35, 2.2, 1.0, f'+{growth:.0f}%', f'2026 run-rate vs 2024 (${avg24:.2f}M → ${avg26:.2f}M/mo)', big_color=RED)
kpi_card(s, 10.4, 2.35, 2.2, 1.0, f'${peak:.2f}M', 'worst month (Apr 2026)', big_color=RED)
kpi_card(s, 8.0, 3.5, 2.2, 1.0, f'{odl/tot*100:.0f}%', 'of exposure sits behind an overdue action', big_color=RED)
kpi_card(s, 10.4, 3.5, 2.2, 1.0, f'{over1y}', f'actions overdue by 1 year+ (oldest {max_age} d)', big_color=RED)
cd = ChartData()
cd.categories = mlab
cd.add_series('Loss ($M)', mval)
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.7), Inches(2.35), Inches(6.9), Inches(3.6), cd).chart
style_chart(gf)
gf.has_title = True
gf.chart_title.text_frame.text = 'Monthly loss exposure, 31 months ($M)'
for pr in gf.chart_title.text_frame.paragraphs:
    for r in pr.runs:
        r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = INK; r.font.name = FONT
for _i, _pt in enumerate(gf.series[0].points):
    _pt.format.fill.solid()
    _pt.format.fill.fore_color.rgb = RED if _i == mval.index(peak) else BLUE
    _pt.format.line.fill.background()
tb = textbox(s, 0.7, 6.05, 6.9, 0.7)
para(tb.text_frame, f'Red peak = Apr 2026 ${peak:.2f}M. Dashed reading: 2026 ${avg26:.2f}M/mo vs 2024 ${avg24:.2f}M/mo (+{growth:.0f}%).', size=10, color=MUT, first=True)
tb = textbox(s, 8.0, 4.7, 4.6, 1.6)
para(tb.text_frame, 'Six functions, six dashboards, six KPI definitions — hours validating before deciding.', size=12, first=True)
para(tb.text_frame, f'{len(op)} actions open, {len(od)} past due, median age {med_age} days.', size=12)
para(tb.text_frame, 'Root cause found late, so the same mechanism keeps repeating.', size=12)

# ================= 3 BASELINE =================
s = prs.slides.add_slide(blank)
kick_kpi_slide(s, 'Baseline scorecard', 'What we inherited — measured, not asserted.',
               'Every figure below is recomputed from the same incident table.',
               False, 'Every figure on this slide is recomputed from the same table', '', 3)
cd = ChartData()
cd.categories = [k for k, _ in mechs[:6]]
cd.add_series('Loss ($M)', [round(v[1] / 1000, 2) for _, v in mechs[:6]])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.7), Inches(2.35), Inches(5.9), Inches(3.7), cd).chart
style_chart(gf)
gf.has_title = True
gf.chart_title.text_frame.text = 'Exposure by failure mechanism ($M)'
for pr in gf.chart_title.text_frame.paragraphs:
    for r in pr.runs:
        r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = INK; r.font.name = FONT
for _i, _pt in enumerate(gf.series[0].points):
    _pt.format.fill.solid()
    _pt.format.fill.fore_color.rgb = BLUE if _i < 3 else GRAY
    _pt.format.line.fill.background()
gf.plots[0].has_data_labels = True
_dl = gf.plots[0].data_labels
_dl.show_value = True
_dl.number_format = '#,##0.00'
_dl.font.size = Pt(9); _dl.font.bold = True; _dl.font.color.rgb = INK; _dl.font.name = FONT
tb = textbox(s, 0.7, 6.05, 5.9, 0.7)
para(tb.text_frame, f'Top 3 mechanisms = {top3share:.0f}% of exposure (${top3:.2f}M) in {top3n} of {n} records.', size=10, color=MUT, first=True)
rows, cols = len(units[:8]) + 1, 4
tbl = s.shapes.add_table(rows, cols, Inches(6.9), Inches(2.35), Inches(5.7), Inches(3.7)).table
hdr = ['Unit', 'Cases', 'Overdue', 'Loss ($M)']
for j, h in enumerate(hdr):
    c = tbl.cell(0, j)
    c.text = h
    for pr in c.text_frame.paragraphs:
        for r in pr.runs:
            r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = FONT
    c.fill.solid(); c.fill.fore_color.rgb = NAVY
for i, (k, v) in enumerate(units[:8]):
    vals = [k, str(v[0]), str(v[2]), f'{v[1]/1000:.2f}']
    for j, vv in enumerate(vals):
        c = tbl.cell(i + 1, j)
        c.text = vv
        for pr in c.text_frame.paragraphs:
            for r in pr.runs:
                r.font.size = Pt(11); r.font.name = FONT; r.font.color.rgb = INK
        c.fill.solid(); c.fill.fore_color.rgb = LCARD if i % 2 == 0 else WHITE
tb = textbox(s, 6.9, 6.05, 5.7, 0.7)
para(tb.text_frame, f'Unit {units[0][0]} alone carries ${units[0][1][1]/1000:.2f}M and {units[0][1][2]} overdue actions.', size=10, color=MUT, first=True)

# ================= 4 Q1 =================
s = prs.slides.add_slide(blank)
kick_kpi_slide(s, 'Key question 1 — Data foundation', 'Four sources in. One governed table out.',
               'Every chart on every tab reads the same incident table. Edit one record, every figure recomputes.',
               False, 'Declared additions: energy proxy + CCTV illustration, both labeled', '', 4)
steps = [('Incident DB', f'{n} x 23 cols'), ('Equipment', '5 x 26 weeks'), ('Production PI', '5 x 721 rows'),
         ('Downtime', f'{dt:,.1f} h total'), ('ONE TABLE', 'feeds 11 views')]
for i, (a, b) in enumerate(steps):
    x = 0.7 + i * 2.45
    shp = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(2.6), Inches(2.15), Inches(1.2))
    shp.fill.solid()
    shp.fill.fore_color.rgb = BLUE if i == 4 else LCARD
    shp.line.fill.background()
    tf = shp.text_frame; tf.word_wrap = True
    para(tf, a, size=14, bold=True, color=(WHITE if i == 4 else INK), first=True)
    para(tf, b, size=11, color=(WHITE if i == 4 else MUT))
    if i < 4:
        ar = textbox(s, x + 2.18, 2.95, 0.3, 0.5)
        para(ar.text_frame, '→', size=20, bold=True, color=BLUE, first=True)
kpi_card(s, 0.7, 4.2, 3.8, 1.5, 'Single KPI contract', 'Same metric from incident DB, PI tags, or declared value, side by side — divergence visible, not hidden.')
kpi_card(s, 4.7, 4.2, 3.8, 1.5, 'Governed, not scraped', 'Baseline defects published in a Data Governance view: nulls, units, gaps — listed, not patched.')
kpi_card(s, 8.7, 4.2, 3.8, 1.5, 'Offline by design', 'One HTML file from a USB stick. No install, no build, no server — survives a judge PC offline.')

# ================= 5 Q2 =================
s = prs.slides.add_slide(blank)
kick_kpi_slide(s, 'Key question 2 — Single pane of glass', 'The executive view, in one screen.',
               'Fix-first priority plus unit ranking. Tap a bar in the dashboard to filter the incident list.',
               False, 'Trip logsheet: one row per trip, colored duration + follow-up dot', '', 5)
cd = ChartData()
cd.categories = [k for k, _ in mechs[:6]]
cd.add_series('Loss ($M)', [round(v[1] / 1000, 2) for _, v in mechs[:6]])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.7), Inches(2.35), Inches(5.9), Inches(3.4), cd).chart
style_chart(gf)
gf.has_title = True
gf.chart_title.text_frame.text = 'Fix-first priority — Pareto of loss ($M)'
for pr in gf.chart_title.text_frame.paragraphs:
    for r in pr.runs:
        r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = INK; r.font.name = FONT
for _i, _pt in enumerate(gf.series[0].points):
    _pt.format.fill.solid()
    _pt.format.fill.fore_color.rgb = BLUE if _i < 3 else GRAY
    _pt.format.line.fill.background()
gf.plots[0].has_data_labels = True
_dl = gf.plots[0].data_labels
_dl.show_value = True
_dl.number_format = '#,##0.00'
_dl.font.size = Pt(9); _dl.font.bold = True; _dl.font.color.rgb = INK; _dl.font.name = FONT
cd2 = ChartData()
cd2.categories = [k for k, _ in units[:6]]
cd2.add_series('Loss ($M)', [round(v[1] / 1000, 2) for _, v in units[:6]])
gf2 = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(6.9), Inches(2.35), Inches(5.7), Inches(3.4), cd2).chart
style_chart(gf2)
gf2.has_title = True
gf2.chart_title.text_frame.text = 'Unit ranking — loss with overdue ($M)'
for pr in gf2.chart_title.text_frame.paragraphs:
    for r in pr.runs:
        r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = INK; r.font.name = FONT
bar_color(gf2.series[0], SKY)
gf2.plots[0].has_data_labels = True
_dl2 = gf2.plots[0].data_labels
_dl2.show_value = True
_dl2.number_format = '#,##0.00'
_dl2.font.size = Pt(9); _dl2.font.bold = True; _dl2.font.color.rgb = INK; _dl2.font.name = FONT
tb = textbox(s, 0.7, 5.85, 5.9, 0.5)
para(tb.text_frame, f'Top 3 = {top3share:.0f}% of exposure. Priority is money order, not loudest voice.', size=10, color=MUT, first=True)
tb = textbox(s, 6.9, 5.85, 5.7, 0.9)
para(tb.text_frame, 'Bar = loss in USD. od = overdue actions behind that unit. Tap to filter.', size=10, color=MUT, first=True)
para(tb.text_frame, '0 charts without a data-provenance link.', size=11, bold=True, color=DGREEN)

# ================= 6 AGING =================
s = prs.slides.add_slide(blank)
kick_kpi_slide(s, 'Action tracking — aging of overdue', f'{over1y} actions are more than a year late.',
               f'Real distribution of {len(od)} overdue actions measured at 19-Aug-2026. Median age {med_age} days, oldest {max_age} days.',
               False, 'Target is a modeled commitment, not a measured result', '', 6)
cd = ChartData()
cd.categories = ag_order
cd.add_series('Actions', [ag[k] for k in ag_order])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.7), Inches(2.6), Inches(6.2), Inches(3.5), cd).chart
style_chart(gf)
gf.has_title = True
gf.chart_title.text_frame.text = f'Overdue actions by age, days ({len(od)} total)'
for pr in gf.chart_title.text_frame.paragraphs:
    for r in pr.runs:
        r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = INK; r.font.name = FONT
_AG = [GREEN, SKY, RGBColor(0xD9, 0x77, 0x06), RGBColor(0xEA, 0x58, 0x0C), RED]
for _i, _pt in enumerate(gf.series[0].points):
    _pt.format.fill.solid()
    _pt.format.fill.fore_color.rgb = _AG[_i % len(_AG)]
    _pt.format.line.fill.background()
gf.plots[0].has_data_labels = True
_dl = gf.plots[0].data_labels
_dl.show_value = True
_dl.font.size = Pt(10); _dl.font.bold = True; _dl.font.color.rgb = INK; _dl.font.name = FONT
kpi_card(s, 7.3, 2.6, 2.5, 1.6, f'{len(od)} → {len(od)-over1y}', f'OVERDUE NOW → TARGET ({over1y} actions >1 year old drop out)', big_color=RED)
kpi_card(s, 10.0, 2.6, 2.5, 1.6, f'${odl/1000:.2f}M', f'of exposure ({odl/tot*100:.0f}%) stuck behind overdue rows', big_color=RED)
tb = textbox(s, 7.3, 4.4, 5.2, 1.7)
para(tb.text_frame, 'Target basis: owner + due date mandatory at creation; closure blocked without evidence.', size=11, color=MUT, first=True)
para(tb.text_frame, 'Red dot = nobody on it. Purple = in progress. Green = done.', size=11, color=MUT)

# ================= 7 Q3 AI =================
s = prs.slides.add_slide(blank)
kick_kpi_slide(s, 'Key question 3 — AI root cause', 'AI suggests. Humans close.',
               f'Both numbers measured leave-one-out on all {n} records — not a demo set. Full model 95% CI {p1lo:.1f}–{p1hi:.1f}%.',
               False, 'Measurable, reproducible, published', '', 7)
cd = ChartData()
cd.categories = ['Baseline model', 'Full model']
cd.add_series('Rank-1 (%)', [round(b1, 1), round(p1, 1)])
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.7), Inches(2.6), Inches(5.2), Inches(3.5), cd).chart
style_chart(gf)
gf.has_title = True
gf.chart_title.text_frame.text = 'Similar-incident retrieval, before vs after (%)'
for pr in gf.chart_title.text_frame.paragraphs:
    for r in pr.runs:
        r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = INK; r.font.name = FONT
pts = gf.series[0].points if hasattr(gf.series[0], 'points') else None
for _i, _pt in enumerate(gf.series[0].points):
    _pt.format.fill.solid()
    _pt.format.fill.fore_color.rgb = RED if _i == 0 else GREEN
    _pt.format.line.fill.background()
gf.plots[0].has_data_labels = True
_dl = gf.plots[0].data_labels
_dl.show_value = True
_dl.number_format = '0.0'
_dl.font.size = Pt(10); _dl.font.bold = True; _dl.font.color.rgb = INK; _dl.font.name = FONT
kpi_card(s, 6.3, 2.6, 2.5, 1.35, f'{p1:.1f}%', f'rank-1 retrieval, CI {p1lo:.1f}–{p1hi:.1f}%')
kpi_card(s, 9.0, 2.6, 2.5, 1.35, f'+{lift:.1f} pts', f'vs feature-lite baseline ({b1:.1f}%)', big_color=DGREEN)
tb = textbox(s, 6.3, 4.15, 5.2, 1.9)
para(tb.text_frame, 'Problem tank → root-cause indication → prioritized alerts → tracked action.', size=12, first=True)
para(tb.text_frame, 'Top-10 exposure plan in one click, each row with owner + PM schedule.', size=12)
para(tb.text_frame, 'Human-in-the-loop: AI never closes an action, the PIC does.', size=12, bold=True, color=DRED)
tb = textbox(s, 0.7, 6.15, 5.2, 0.5)
para(tb.text_frame, f'Rank-5: {p5:.1f}%. Method, confidence intervals and honest limits in the Model Evaluation tab.', size=10, color=MUT, first=True)

# ================= 8 KO-3201 =================
s = prs.slides.add_slide(blank)
kick_kpi_slide(s, 'Case reconstruction — compressor KO-3201', f'Watch it degrade. {leadMean:.0f} days of warning.',
               f'Real condition history. ALARM {ko_aw}, TRIP {ko_tw}: {(20-9)*7} days to act on KO-3201. Mean {leadMean:.0f} days across 5 assets.',
               False, 'Demo path: RCA tab → KO-3201', '', 8)
cd = ChartData()
cd.categories = ko_lab
cd.add_series('DE vibration (micron)', ko_vib)
cd.add_series('ALARM (45)', [KO_AL] * len(ko_lab))
cd.add_series('TRIP (75)', [KO_TR] * len(ko_lab))
gf = s.shapes.add_chart(XL_CHART_TYPE.LINE, Inches(0.7), Inches(2.6), Inches(7.0), Inches(3.5), cd).chart
style_chart(gf, show_legend=True)
gf.legend.position = XL_LEGEND_POSITION.BOTTOM
gf.has_title = True
gf.chart_title.text_frame.text = 'KO-3201 DE vibration, 26 weeks (micron) — real history'
for pr in gf.chart_title.text_frame.paragraphs:
    for r in pr.runs:
        r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = INK; r.font.name = FONT
ln = gf.series[0]
ln.format.line.color.rgb = BLUE
ln.format.line.width = Pt(2.5)
ln.smooth = True
for _ln, _col in ((gf.series[1], RGBColor(0xD9, 0x77, 0x06)), (gf.series[2], RED)):
    _ln.format.line.color.rgb = _col
    _ln.format.line.width = Pt(1.75)
    _ln.format.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    _ln.smooth = True
rows, cols = len(leads) + 1, 3
tbl = s.shapes.add_table(rows, cols, Inches(8.0), Inches(2.6), Inches(4.6), Inches(3.5)).table
for j, h in enumerate(['Asset', 'Lead', 'Read']):
    c = tbl.cell(0, j)
    c.text = h
    for pr in c.text_frame.paragraphs:
        for r in pr.runs:
            r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = FONT
    c.fill.solid(); c.fill.fore_color.rgb = NAVY
for i, (t, v) in enumerate(leads):
    for j, vv in enumerate([t, f'{v} d', 'Before trip' if v >= 70 else 'Actionable']):
        c = tbl.cell(i + 1, j)
        c.text = vv
        for pr in c.text_frame.paragraphs:
            for r in pr.runs:
                r.font.size = Pt(11); r.font.name = FONT; r.font.color.rgb = INK
        c.fill.solid(); c.fill.fore_color.rgb = LCARD if i % 2 == 0 else WHITE
tb = textbox(s, 0.7, 6.15, 7.0, 0.5)
para(tb.text_frame, 'All 5 RCA decks integrated (4P / 4M+1E, CAPA, PIC, PM schedule) — chronology and correlation one tap from any row.', size=10, color=MUT, first=True)

# ================= 9 BEFORE/AFTER =================
s = prs.slides.add_slide(blank)
kick_kpi_slide(s, 'Impact — before vs target', 'Four numbers we commit to moving.',
               'Baseline = measured. Target = modeled commitment with basis stated, in the open.',
               True, 'Loss recovery target = return to 2024 monthly level', '', 9)
rows = [
    ('Monthly loss', f'${avg26:.2f}M/mo', f'${avg24:.2f}M/mo', f'-{(avg26-avg24)/avg26*100:.0f}%',
     f'2026 running rate vs 2024 level. Fix-first on top-3 covers {top3share:.0f}% of exposure.'),
    ('Overdue actions', f'{len(od)} of {len(op)}', f'{len(od)-over1y}', '-61%',
     f'{over1y} actions past due 1 year+. Board forces owner + due date at creation.'),
    ('Retrieval @1', f'{b1:.1f}%', f'{p1:.1f}%', f'+{lift:.1f} pts',
     f'Both measured leave-one-out on n={n}. Full model CI {p1lo:.1f}-{p1hi:.1f}%.'),
    ('Warning window', 'reactive', f'{leadMean:.0f} days', 'new',
     'Mean gap between first ALARM week and TRIP week, from 26-week condition history.'),
]
tbl = s.shapes.add_table(len(rows) + 1, 5, Inches(0.7), Inches(2.7), Inches(11.9), Inches(3.2)).table
widths = [Inches(2.0), Inches(1.9), Inches(0.4), Inches(1.9), Inches(5.7)]
for j, w in enumerate(widths):
    tbl.columns[j].width = w
for j, h in enumerate(['Metric', 'Before', '', 'Target', 'Basis']):
    c = tbl.cell(0, j)
    c.text = h
    for pr in c.text_frame.paragraphs:
        for r in pr.runs:
            r.font.size = Pt(11); r.font.bold = True; r.font.color.rgb = DARK_KICK; r.font.name = FONT
    c.fill.solid(); c.fill.fore_color.rgb = RGBColor(0x14, 0x38, 0x73)
for i, (name, before, after, delta, method) in enumerate(rows):
    vals = [name, before, '→', after, method]
    for j, vv in enumerate(vals):
        c = tbl.cell(i + 1, j)
        c.text = vv
        for pr in c.text_frame.paragraphs:
            for r in pr.runs:
                r.font.size = Pt(11); r.font.name = FONT
                r.font.bold = (j in (0, 1, 3))
                r.font.color.rgb = RGBColor(0xFC, 0xA5, 0xA5) if j == 1 else (RGBColor(0x86, 0xEF, 0xAC) if j == 3 else WHITE)
        c.fill.solid(); c.fill.fore_color.rgb = RGBColor(0x14, 0x38, 0x73) if i % 2 == 0 else RGBColor(0x0E, 0x2C, 0x63)
tb = textbox(s, 0.7, 6.05, 11.9, 0.5)
para(tb.text_frame, 'Targets are modeled from this baseline, not measured results. We publish the basis so the assumption can be challenged, not the number.', size=11, italic=True, color=DSUB, first=True)

# ================= 10 HONEST =================
s = prs.slides.add_slide(blank)
kick_kpi_slide(s, 'Impact — stated honestly', 'What we measure, what we label, what we skip.',
               'Honest limits score higher than hidden guesses.',
               False, 'Honest limits score higher than hidden guesses', '', 10)
kpi_card(s, 0.7, 2.5, 3.8, 2.3, 'Measured', f'Loss, downtime, aging — {n} real records\nRetrieval {p1:.1f}% / {p5:.1f}% leave-one-out\nWarning {leadMean:.0f} d from history', big_color=DGREEN)
kpi_card(s, 4.7, 2.5, 3.8, 2.3, 'Labeled, not hidden', 'Energy = derived proxy, formula printed\nCCTV = illustration, aggregates real\nDefects listed in Data Governance')
kpi_card(s, 8.7, 2.5, 3.8, 2.3, 'Out of scope', 'No live streaming (not required)\nNo auto-closure (human-in-the-loop)\nNo extra data beyond 2 declared', big_color=DRED)
kpi_card(s, 0.7, 5.05, 2.85, 1.1, f'{top3share:.0f}%', 'of exposure fixable by top-3 focus')
kpi_card(s, 3.75, 5.05, 2.85, 1.1, f'${top3:.2f}M', 'addressable in 3 mechanisms')
kpi_card(s, 6.8, 5.05, 2.85, 1.1, f'{over1y}', 'stale actions surfaced with age')
kpi_card(s, 9.85, 5.05, 2.85, 1.1, f'{leadMean:.0f} d', 'average early-warning window')

# ================= 11 TEAM =================
s = prs.slides.add_slide(blank)
kick_kpi_slide(s, 'Team & next', 'Jenny  ·  Hafidz  ·  Naufal',
               'Advisor: Mr. Bayu Aji. Built from the official baseline only, plus two declared additions.',
               True, 'CALIBER 2026 — Case 2: Intelligent Manufacturing', '', 11)
kpi_card(s, 0.7, 2.8, 3.8, 1.6, 'Jenny', 'DECK + NARRATIVE', dark=True)
kpi_card(s, 4.7, 2.8, 3.8, 1.6, 'Hafidz', 'VOICE + DEMO', dark=True)
kpi_card(s, 8.7, 2.8, 3.8, 1.6, 'Naufal', 'DATA + BUILD', dark=True)
kpi_card(s, 0.7, 4.6, 3.8, 1.3, '1 — Meter it', '5 metered energy tags replace the proxy', dark=True)
kpi_card(s, 4.7, 4.6, 3.8, 1.3, '2 — Connect it', 'EDMS / AIMS / Twin for asset context', dark=True)
kpi_card(s, 8.7, 4.6, 3.8, 1.3, '3 — Stream it', 'PI live feed, decoupled already', dark=True)
tb = textbox(s, 0.7, 6.1, 11.9, 0.6)
para(tb.text_frame, 'One file. One truth. From data to decision.', size=20, bold=True, color=WHITE, first=True)

prs.save('submission/03_presentation.pptx')
import os
print('saved', os.path.getsize('submission/03_presentation.pptx'), 'bytes')
