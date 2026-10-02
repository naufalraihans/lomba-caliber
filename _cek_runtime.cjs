const fs = require("fs");
const t = fs.readFileSync("index.html", "utf8");
const m = t.match(/<script>([\s\S]*)<\/script>/);

// ---- DOM shim ----
const els = {};
function mkEl(id) {
  return {
    id, innerHTML: "", textContent: "", value: "", dataset: {},
    classList: { toggle() {}, add() {}, remove() {}, contains() { return false; } },
    querySelectorAll() { return []; },
    onclick: null, style: {},
  };
}
["views", "modal", "toast", "bellN", "bdgAlm", "bdgFol", "clock", "onduty", "mnav", "q", "roster", "incList"].forEach((id) => { els[id] = mkEl(id); });
const store = {};
const sandbox = {
  document: {
    getElementById: (id) => els[id] || (els[id] = mkEl(id)),
    querySelectorAll: () => [],
    querySelector: () => null,
    createElement: () => ({ href: "", download: "", click() {}, style: {} }),
  },
  window: { open() {}, scrollTo() {} },
  localStorage: {
    getItem: (k) => (k in store ? store[k] : null),
    setItem: (k, v) => { store[k] = String(v); },
  },
  confirm: () => false,
  setInterval: () => 0,
  setTimeout: () => 0,
  URL: { createObjectURL: () => "blob:x" },
  Blob: function () {},
};
const vm = require("vm");
const ctx = vm.createContext(Object.assign({ console }, sandbox));
const api = vm.runInContext(m[1] + "\n;({render, go, state, V: (typeof V!=='undefined'?V:null), INC, EQC, META, eff, agg, alarms, plantAgg: (typeof plantAgg!=='undefined'?plantAgg:null), plantCards: (typeof plantCards!=='undefined'?plantCards:null)});", ctx);

// note: incdet is rendered via openInc() modal flow, not via state.v; skip direct render
const views = ["lobby", "overview", "assets", "assetdet", "incidents", "logsheet", "condition", "production", "energy", "rca", "followup", "alarm", "personnel", "reports"];
const errs = [];
// goa state-dependent views need setup
const setup = {
  incdet: () => { ctx.state.sub = "ov"; },
  assetdet: () => {},
  condition: () => {},
  rca: () => {},
};
for (const v of views) {
  try {
    if (setup[v]) setup[v]();
    vm.runInContext("state.v=" + JSON.stringify(v) + ";render();", ctx);
    const html = els.views.innerHTML;
    if (!html || html.length < 200) errs.push(v + ": EMPTY (" + html.length + ")");
    if (/\bundefined\b/.test(html)) {
      const i = html.search(/\bundefined\b/);
      errs.push(v + ": UNDEFINED near ..." + JSON.stringify(html.slice(Math.max(0, i - 80), i + 40)));
    }
    if (/\bNaN\b/.test(html)) {
      const i = html.search(/\bNaN\b/);
      errs.push(v + ": NaN near ..." + JSON.stringify(html.slice(Math.max(0, i - 80), i + 40)));
    }
    console.log(v + ": " + html.length + " chars");
  } catch (e) { errs.push(v + ": THROW " + e.message); }
}
// ---- checks ----
const ov = (() => { vm.runInContext("state.v='overview';render();", ctx); return els.views.innerHTML; })();
const inc = (() => { vm.runInContext("state.v='incidents';render();", ctx); return els.views.innerHTML; })();
const per = (() => { vm.runInContext("state.v='personnel';render();", ctx); return els.views.innerHTML; })();
const lob = (() => { vm.runInContext("state.v='lobby';render();", ctx); return els.views.innerHTML; })();
const cond = (() => { vm.runInContext("state.v='condition';render();", ctx); return els.views.innerHTML; })();
const en = (() => { vm.runInContext("state.v='energy';render();", ctx); return els.views.innerHTML; })();
const fol = (() => { vm.runInContext("state.v='followup';render();", ctx); return els.views.innerHTML; })();
const log = (() => { vm.runInContext("state.v='logsheet';render();", ctx); return els.views.innerHTML; })();
const checks = [
  ["overview has 380", /380/.test(ov)],
  ["overview has US$", /US\$/.test(ov)],
  ["overview clickable KPI", /clickable/.test(ov)],
  ["overview plant units section", /Unit ranking|Plant Overview/.test(ov)],
  ["overview top-3 mech", /Top 3 failure|Fix-first/.test(ov)],
  ["incidents plant map", /Plant map/.test(inc)],
  ["incidents CCTV", /CCTV/.test(inc)],
  ["personnel demo numbers", /62812345678/.test(per)],
  ["personnel group dispatch", /group dispatch|Group dispatch|WhatsApp group/i.test(per)],
  ["personnel duty roster", /uty roster/.test(per)],
  ["lobby hero", /Which unit needs you|CALIBER/.test(lob)],
  ["condition thresholds", /alarm|Alarm/.test(cond)],
  ["condition KPI last reading", /Last reading/.test(cond)],
  ["energy share table", /Share/.test(en)],
  ["followup pipeline", /Report/.test(fol) && /Verify/.test(fol)],
  ["no emoji nav (svg count)", (t.match(/<span class="ic"><svg/g) || []).length >= 10],
  ["logo-mark present", t.includes("logo-mark")],
  ["import CSV button", /Import CSV/.test(inc)],
  ["duty badge topbar", t.includes('id="onduty"')],
  ["logsheet trip header", /TRIP LOGSHEET/.test(log)],
  ["logsheet trip columns", /Trip/.test(log) && /Normal/.test(log) && /Duration/.test(log)],
  ["logsheet followup col", /Follow-up/.test(log)],
  ["logsheet cause col", /Cause/.test(log)],
  ["logsheet nav entry", t.includes('data-v="logsheet"')],
];
// Indonesian leftovers in UI strings (exclude data titles which may contain ID? data is EN; check common words)
const idWords = ["\u00c9diting", "tindak lanjut", "petugas", "gangguan", "tambah", "simpan", "Lihat", "Cari ", "Beranda", "Laporan", "Pemantauan", "Pengaturan", "Bantuan", "Selamat", "Pagi", "bulan", "tahun", "dengan", "untuk", "dari ", "yang ", "adalah", "tidak", "sudah", "belum"];
const idFound = [];
for (const w of idWords) {
  const rx = new RegExp(w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
  if (rx.test(t.split("const INC=")[0] + t.split("const EQC=")[1].split("const RCA=")[0])) { /* skip data */ }
}
// simpler: scan whole file except embedded JSON lines
const nonData = t.split("\n").filter((l) => !(l.startsWith("const INC=") || l.startsWith("const EQC=") || l.startsWith("const RCA=") || l.startsWith("const PROD=") || l.startsWith("const META="))).join("\n");
for (const w of idWords) { if (nonData.includes(w)) idFound.push(w); }
console.log("\n--- checks ---");
let fail = 0;
for (const [k, v] of checks) { console.log((v ? "PASS" : "FAIL") + " " + k); if (!v) fail++; }
console.log("--- ID leftovers (non-data):", idFound.length ? idFound.join(" | ") : "NONE");
console.log("\n--- view errors ---");
console.log(errs.length ? errs.join("\n") : "0 ERRORS");
console.log("RESULT:", (errs.length === 0 && fail === 0 && idFound.length === 0) ? "ALL GREEN" : "NEEDS FIX");
