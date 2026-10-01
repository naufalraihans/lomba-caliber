import fs from "node:fs";
const D = JSON.parse(fs.readFileSync("analysis/embed_data.json", "utf8"));
const RCA = JSON.parse(fs.readFileSync("analysis/rca_structured.json", "utf8"));
const AI = JSON.parse(fs.readFileSync("analysis/ai_eval.json", "utf8"));
const OPEN = new Set(["NEW REGISTERED", "RCA PROCESS", "CA/PA EXECUTION", "MONITORING RESULT"]);

const inc = D.incidents.map((r) => ({
  serial: +r.serial, mto: r.mto, ar: r.ar, plant: r.plant, tag: r.tag, eq_class: r.eq_class,
  date: r.date, title: r.title, pre_risk: r.pre_risk, risk_score: +r.risk_score || 0, pic: r.pic,
  status: r.status, discipline: r.discipline, mech: r.mech, component: r.component,
  downtime: +r.downtime || 0, total_loss: +r.total_loss || 0, rca_due: r.rca_due, month: r.month,
}));

const eqc = [];
for (const [tag, d] of Object.entries(D.equipment)) {
  const info = {};
  for (const row of (d["Condition History"] || []).slice(0, 0)) { }
  const rows = d["Equipment Info"] || [];
  for (const row of rows) { if (row[0] != null && row[1] != null && info[String(row[0])] === undefined) info[String(row[0])] = row[1]; }
  const ch = (d["Condition History"] || []).slice(1);
  const hdr = d["Condition History"][0];
  const colIdx = {};
  hdr.forEach((h, i) => { colIdx[String(h).split("\n")[0]] = i; });
  const sts = ch.map((r) => String(r[hdr.length - 2] || "").trim());
  const ai = sts.findIndex((s) => s === "ALARM"), ti = sts.findIndex((s) => s === "TRIP");
  const alarm = sts.filter((s) => s === "ALARM").length;
  const lead = (ai >= 0 && ti >= 0) ? (ti - ai) * 7 : 0;
  const status = lead >= 70 ? "Critical" : lead >= 42 ? "Warning" : "Healthy";
  const params = [];
  for (let i = 2; i < hdr.length - 2; i++) {
    const nm = String(hdr[i]).replace(/\n/g, " ").trim();
    if (!nm || nm === "null") continue;
    params.push({ n: nm, series: ch.map((r) => +r[i]).filter((v) => isFinite(v)).map((v) => +v.toFixed(2)) });
  }
  eqc.push({
    tag, name: info["Equipment Name"] || tag, type: info["Equipment Type"] || "",
    plant: info["Plant / Unit"] || "", disc: info["Discipline"] || "", crit: info["Criticality"] || "",
    mode: info["Dominant Failure Mode"] || "", status, alarm, lead, params,
  });
}

const rca = {};
for (const [tag, r] of Object.entries(RCA)) {
  rca[tag] = {
    title: r.title, ar: r.ar, pic_rca: r.pic_rca, date_occ: r.date_occ,
    root_cause: r.root_cause, chronology: (r.chronology || []).map((c) => ({ ts: c.ts, event: c.event })),
    capa: (r.capa || []).map((c) => ({ action: c.action, pic: c.pic, status: c.status })),
    proactive: (r.proactive || []).map((c) => ({ action: c.action, pic: c.pic, status: c.status })),
    pm_schedule: (r.pm_schedule || []).map((p) => ({ desc: p.desc || p.pm_no })),
  };
}

const prod = [];
for (const [tag, d] of Object.entries(D.production)) {
  const keys = Object.keys(d);
  const key = keys.includes("Sheet2") ? "Sheet2" : keys.find((k) => k !== "PI Tag");
  const raw = d[key];
  const hdr = raw[0];
  const fi = (n) => hdr.findIndex((h) => String(h).includes(n));
  const iT = 0, iF = fi("FEED"), iV = fi("VIB"), iT2 = fi("TEMP"), iA = fi("AMP"), iR = fi("RUN_STATUS");
  const rows2 = raw.slice(1).filter((r) => r[0] != null);
  const last = rows2[rows2.length - 1];
  const win = rows2.slice(-24);
  const avg = (ix) => win.reduce((a, r) => a + (+r[ix] || 0), 0) / win.length;
  prod.push({
    tag, feed: +(+last[iF]).toFixed(1), vib: +(+last[iV]).toFixed(2), temp: +(+last[iT2]).toFixed(1),
    amp: +(+last[iA]).toFixed(1), run: String(last[iR]),
    feed24: win.map((r) => +(+r[iF] || 0).toFixed(1)),
    avgFeed: +avg(iF).toFixed(1), avgVib: +avg(iV).toFixed(2),
  });
  const pit = (d["PI Tag"] || []).slice(1, 7).map((r) => ({ name: r[0], desc: r[1], unit: r[3] }));
  prod[prod.length - 1].pit = pit;
}

let kwh = 0, hours = 0;
const eKwh = [];
for (const [tag, d] of Object.entries(D.production)) {
  const keys = Object.keys(d);
  const key = keys.includes("Sheet2") ? "Sheet2" : keys.find((k) => k !== "PI Tag");
  const raw = d[key];
  const hdr = raw[0];
  const iA = hdr.findIndex((h) => String(h).includes("AMP")), iR = hdr.findIndex((h) => String(h).includes("RUN_STATUS"));
  let k = 0, h = 0;
  for (const r of raw.slice(1)) { if (r[0] == null) continue; if (String(r[iR]).toUpperCase() === "ON") { h++; k += Math.sqrt(3) * 400 * (+r[iA] || 0) * 0.86 / 1000; } }
  kwh += k; hours += h;
  eKwh.push({ tag, kwh: Math.round(k) });
}

const mo = {};
for (const r of inc) { if (!r.month) continue; mo[r.month] = mo[r.month] || { k: r.month, v: 0 }; mo[r.month].v += (+r.total_loss || 0) * 1000; }
const order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const moArr = Object.values(mo).sort((x, y) => { const pa = x.k.split("-"), pb = y.k.split("-"); return (+pa[1] * 12 + order.indexOf(pa[0])) - (+pb[1] * 12 + order.indexOf(pb[0])); }).map((x) => ({ k: x.k, v: Math.round(x.v) }));

const J = (o) => JSON.stringify(o).replace(/</g, "\\u003c");
let t = fs.readFileSync("_main_template.html", "utf8");
const rep = {
  "/*__INC__*/": () => J(inc),
  "/*__EQC__*/": () => J(eqc),
  "/*__RCA__*/": () => J(rca),
  "/*__PROD__*/": () => J(prod),
  "/*__PIT__*/": () => "[]",
  "/*__META__*/": () => J({ dt: +inc.reduce((a, r) => a + r.downtime, 0).toFixed(1), p1: +AI.retrieval.full_p1.pct.toFixed(1), p5: +AI.retrieval.full_p5.pct.toFixed(1), kwh: Math.round(kwh), hours, co2: +(kwh * 0.794 / 1000).toFixed(1), eKwh, mo: moArr }),
};
for (const [k, fn] of Object.entries(rep)) {
  if (!t.includes(k)) { console.log("ANCHOR MISSING", k); process.exit(1); }
  t = t.split(k).join(fn());
}
fs.writeFileSync("index.html", t);
console.log("index.html", t.length, "bytes | inc", inc.length, "eqc", eqc.length);
