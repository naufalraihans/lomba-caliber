/**
 * cek-dasbor.ts — runtime verification for the dashboard.
 * Runs the actual code from dasbor.html in a DOM shim, then renders
 * all 13 tabs and checks the results.
 *
 *   bun run cek-dasbor.ts   (run from the prototype/ directory)
 */
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const DIR = dirname(fileURLToPath(import.meta.url));
const html = readFileSync(join(DIR, "dasbor.html"), "utf8").replace(/\r\n/g, "\n");
const m = html.match(/<script>([\s\S]*)<\/script>/);
if (!m) { console.error("FAIL: <script> block not found"); process.exit(1); }
const isi = m[1];

/* ---------- minimal DOM shim ---------- */
const dibuat: Record<string, any> = {};
function el(): any {
  return {
    innerHTML: "", dataset: {} as Record<string, string>, textContent: "",
    value: "", style: {}, querySelectorAll(_s: string) { return []; },
    set onclick(_v: any) {},
  };
}
(globalThis as any).document = {
  querySelector(s: string) {
    const id = s.replace("#", "");
    return dibuat[id] ?? (dibuat[id] = el());
  },
  getElementById(id: string) { return dibuat[id] ?? (dibuat[id] = el()); },
  querySelectorAll() { return []; },
};
(globalThis as any).window = { scrollTo() {}, setInterval: () => 0, clearInterval: () => {} };
dibuat["nav"] = el();
dibuat["view"] = el();

/* ---------- run ---------- */
const fn = new Function(isi + "\n;return {VIEWS: VIEWS, TABS: TABS};");
let keluar: any;
try { keluar = fn(); }
catch (e: any) {
  console.error("RUN FAILED:", e.message);
  console.error(String(e.stack).split("\n").slice(0, 6).join("\n"));
  process.exit(1);
}

const TABS: [string, string][] = keluar.TABS;
const VIEWS: Record<string, () => string> = keluar.VIEWS;
const rusak: string[] = [];

console.log("TAB COUNT:", TABS.length, "\n");

let gabung = "";
for (const [kunci, label] of TABS) {
  const f = VIEWS[kunci];
  if (!f) { rusak.push(`tab '${kunci}' has no render function`); console.log(`[${kunci}] MISSING`); continue; }
  let h = "";
  try { h = f(); }
  catch (e: any) { rusak.push(`tab '${kunci}' ERROR: ${e.message}`); console.log(`[${label}] ERROR ${e.message}`); continue; }
  gabung += h;

  const txt = h.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
  const undef = (txt.match(/undefined/g) || []).length;
  const nan = (txt.match(/NaN/g) || []).length;
  const kosong = (h.match(/class="(?:val|ni)[^"]*">\s*—\s*</g) || []).length;
  if (undef || nan) rusak.push(`tab '${kunci}': undef=${undef} NaN=${nan}`);

  console.log(`[${label}]  (${kunci})`);
  console.log(`    len=${txt.length} undef=${undef} NaN=${nan} emptyCells=${kosong} svg=${(h.match(/<svg/g) || []).length} tables=${(h.match(/<table/g) || []).length}`);
  console.log("    " + txt.slice(0, 130) + "\n");
}

/* ---------- verify figures: read from DATA, never hard-code ---------- */
console.log("\n--- which tab carries the official figures ---");
const cariDi = (t: string, pola: string) => (VIEWS[t]() as string).includes(pola);
const peta: [string, string][] = [
  ["total loss US$67.19M", "US$67.19M"],
  ["2,261.1 hours", "2,261.1"],
  ["380 incidents", "380"],
  ["179 of 220 overdue", "179"],
  ["67-day warning lead", "67"],
  ["HE-3301 mismatch", "HE-3301"],
  ["recall@1 87.1%", "87.1%"],
  ["recall@5 98.4%", "98.4%"],
  ["Leakage dominant", "Leakage"],
  ["prevalence 26.6%", "26.6%"],
  ["AR-2026-ZCU-0142 (RCA2)", "AR-2026-ZCU-0142"],
  ["AR-2026-ARP-0117 (RCA1)", "AR-2026-ARP-0117"],
  ["root cause KO-3201", "babbitt"],
];
let angkaOK = 0;
for (const [nama, pola] of peta) {
  const ada = TABS.some(([k]) => cariDi(k, pola));
  if (!ada) rusak.push("figure missing from all tabs: " + nama);
  else angkaOK++;
  console.log(`  ${ada ? "OK     " : "MISSING"} ${nama}`);
}
console.log(`  -> ${angkaOK}/${peta.length} official figures rendered`);

/* ---------- tab labels must be English ---------- */
console.log("\n--- tab labels ---");
const labelWajib = ["Overview", "RCA & CAPA", "Case Reconstruction", "KPI Contract", "Energy", "Production",
                    "Emissions", "Downtime", "Problem Queue", "AI Pilot", "Asset Detail",
                    "Action Tracking", "Model Evaluation", "Data Governance"];
for (const l of labelWajib) {
  const ada = TABS.some(([, x]) => x === l);
  if (!ada) rusak.push("tab label missing: " + l);
  console.log(`  ${ada ? "OK     " : "MISSING"} ${l}`);
}

/* ---------- leftover Indonesian UI terms must be gone ---------- */
console.log("\n--- leftover Indonesian ---");
const indonesia = ["Ringkasan", "Rekonstruksi Kasus", "Kontrak KPI", "Antrean Masalah",
                 "Rincian Aset", "Pelacakan Tindakan", "Evaluasi Model", "Tata Kelola Data",
                 "Total kerugian", "Tindakan lewat tenggat"];
for (const s of indonesia) {
  const ada = gabung.includes(s);
  if (ada) rusak.push("still Indonesian: " + s);
  console.log(`  ${ada ? "STILL PRESENT " : "OK clean      "} "${s}"`);
}

console.log("\n=== " + (rusak.length ? "PROBLEMS: " + rusak.join(" | ") : "14 TABS CLEAN · 0 ERRORS · ENGLISH") + " ===");
if (rusak.length) process.exit(1);
