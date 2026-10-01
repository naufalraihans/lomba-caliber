/**
 * build-dasbor.ts — build the "Single Pane of Glass" dashboard into one standalone file.
 *
 *   bun run build-dasbor.ts
 *
 * Sumber : src/dasbor.html + src/dasbor.ts
 * Data   : analysis/embed_data.json, ai_eval.json, reconciliation.json
 * Output : prototype/dasbor.html   (double-click, no internet)
 */

import { readFileSync, writeFileSync, statSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const AKAR = join(dirname(fileURLToPath(import.meta.url)), "..");
const SRC = join(AKAR, "prototype", "src");
const KELUARAN = join(AKAR, "prototype", "dasbor.html");

const baca = (n: string) => JSON.parse(readFileSync(join(AKAR, "analysis", n), "utf8"));
const bersih = (o: unknown) => JSON.stringify(o).replace(/</g, "\\u003c");

/* ---------- 1. baca sumber + data ---------- */
const ts = readFileSync(join(SRC, "dasbor.ts"), "utf8");
const data = baca("embed_data.json");
const aiEval = baca("ai_eval.json");
const recon = baca("reconciliation.json");
const rca = baca("rca_structured.json");

/* ---------- 2. siapkan sumber TS ----------
   Komentar di posisi ekspresi (`const X = /*_*␣/;`) tidak diterima transpiler,
   jadi placeholder diganti lebih dulu, baru di-transpile.

   PENTING: penggantinya memakai FUNGSI, bukan string. Pada String.replace,
   string pengganti menafsirkan pola khusus ($&, $', $1, ...) — dan JSON data
   memuat tanda "$", sehingga penggantian dengan string bisa merusak hasilnya. */
const isi = (o: unknown) => () => bersih(o);

const tsSiap = ts
  .replace(/^import\s+type\s*\{[\s\S]*?\}\s*from\s*["'][^"']+["'];?\s*$/gm, "")
  .replace(/^declare\s+const\s+DATA\s*:\s*\w+\s*;?\s*$/gm, "")
  .replace("/*__AI_EVAL__*/", isi(aiEval))
  .replace("/*__RECON__*/", isi(recon))
  .replace("/*__RCA__*/", isi(rca));

/* ---------- 3. transpile ---------- */
const transpiler = new Bun.Transpiler({ loader: "ts", target: "browser" });
const js = transpiler.transformSync(tsSiap);

const blokLengkap = "const DATA = " + bersih(data) + ";\n" + js;

/* ---------- 4. sisipkan ke kerangka ---------- */
const html = readFileSync(join(SRC, "dasbor.html"), "utf8").replace(/\r\n/g, "\n");
const PENANDA = "/*__KODE__*/";

if (!html.includes(PENANDA)) {
  console.error("GAGAL: penanda " + PENANDA + " tidak ada di src/dasbor.html");
  process.exit(1);
}

const akhir = html.replace(PENANDA, blokLengkap).replace(/\r\n/g, "\n");
writeFileSync(KELUARAN, akhir, { encoding: "utf8" });

/* ---------- 5. periksa ---------- */
const cek: [string, boolean][] = [
  ["diawali <!DOCTYPE", akhir.trimStart().toLowerCase().startsWith("<!doctype")],
  ["ditutup </html>", akhir.includes("</html>")],
  ["page language en", akhir.includes('<html lang="en">')],
  ["tanpa <script src=", !/<script[^>]+src=/.test(akhir)],
  ["tanpa <link href=", !/<link[^>]+href=/.test(akhir)],
  ["tanpa fetch/XHR/module", !/\b(fetch|XMLHttpRequest)\s*\(/.test(akhir) && !akhir.includes('type="module"')],
  ["penanda terganti", !akhir.includes(PENANDA)],
  ["380 insiden", (akhir.match(/"total_loss"/g) || []).length >= 380],
  ["5 aset equipment", (akhir.match(/"Condition History"/g) || []).length >= Object.keys(data.equipment).length],
  ["5 aset production", (akhir.match(/"PI Tag"/g) || []).length >= Object.keys(data.production).length],
  ["data evaluasi AI ada", akhir.includes("retrieval") && akhir.includes("detector")],
  ["data rekonsiliasi ada", akhir.includes("B_per_asset")],
  ["data RCA terstruktur ada", akhir.includes("four_m_1e") && akhir.includes("pm_schedule")],
  ["5 RCA ter-embed (satu per aset)", Object.keys(rca).every((t) => akhir.includes('"' + t + '"'))],
  ["setiap RCA punya root cause", Object.values(rca).every((d: any) => d.root_cause)],
  ["setiap RCA punya 4P lengkap", Object.values(rca).every((d: any) => d.four_p && d.four_p.length >= 4)],
  ["setiap RCA punya CAPA+PIC", Object.values(rca).every((d: any) => d.capa && d.capa.length >= 1 && d.capa.every((c: any) => c.pic))],
  ["nav RCA & CAPA", akhir.includes('"RCA & CAPA"')],
  ["tak ada sisa import", !/^\s*import\s/m.test(js)],
  ["tak ada placeholder sisa", !/\/\*__(DATA|AI_EVAL|RECON|RCA)__\*\//.test(akhir)],
  ["title Single Pane of Glass", akhir.includes("Single Pane of Glass")],
  ["nav Overview", akhir.includes('"Overview"')],
  ["nav KPI Contract", akhir.includes('"KPI Contract"')],
  ["nav Action Tracking", akhir.includes('"Action Tracking"')],
  ["nav Data Governance", akhir.includes('"Data Governance"')],
  ["KPI Total loss", akhir.includes("Total loss")],
  ["has 'Total loss (31 mo)'", akhir.includes("Total loss (31 mo)")],
  ["has 'Actions overdue'", akhir.includes("Actions overdue")],
  ["has 'Case Reconstruction'", akhir.includes("Case Reconstruction")],
  ["has 'Data Governance'", akhir.includes("Data Governance")],
  ["has 'Problem Queue'", akhir.includes("Problem Queue")],
];

console.log("TULIS " + KELUARAN);
const ukuran = statSync(KELUARAN).size;
console.log("  ts   : " + ts.length.toLocaleString("id-ID") + " byte");
console.log("  js   : " + js.length.toLocaleString("id-ID") + " byte");
console.log("  data : " + bersih(data).length.toLocaleString("id-ID") + " byte");
console.log("  hasil: " + ukuran.toLocaleString("id-ID") + " byte = " + (ukuran / 1048576).toFixed(2) + " MB\n");

console.log("PEMERIKSAAN:");
let gagal = 0;
for (const [nama, lolos] of cek) {
  console.log("  [" + (lolos ? "OK  " : "GAGAL") + "] " + nama);
  if (!lolos) gagal++;
}
console.log("\nHASIL: " + (gagal === 0 ? "SEMUA LOLOS (" + cek.length + " pemeriksaan)" : gagal + " GAGAL"));
if (gagal > 0) process.exit(1);
