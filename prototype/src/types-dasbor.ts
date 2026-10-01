/* ============================================================
   types-dasbor.ts — bentuk data untuk dasbor ("Satu Panel Kaca")
   Mengikuti persis struktur analysis/embed_data.json.
   Kalau kolom baru muncul di JSON, tambahkan dulu di sini.
   ============================================================ */

/** satu baris di Incident Database (380 baris) */
export interface Insiden {
  serial: number | string;
  mto: string;
  ar: string;
  plant: string;
  tag: string;
  eq_class: string;
  date: string;
  title: string;
  impact: string;
  pre_risk: string;
  risk_score: number | string;
  pic: string;
  status: string;
  discipline: string;
  eq_type: string;
  component: string;
  mech: string;
  downtime: number | string;
  act_loss: number | string;
  pot_loss: number | string;
  total_loss: number | string;
  rca_due: string;
  month: string;
}

/** tabel apa adanya dari xlsx: baris pertama = header */
export type Tabel = (string | number | null)[][];

/** satu aset di Equipment Performance */
export interface DataAset {
  "Equipment Info": Tabel;
  "Condition History": Tabel;
  "Performance Summary": Tabel;
}

/** satu aset di Production Data */
export interface DataProduksi {
  "PI Tag": Tabel;
  Sheet2?: Tabel;
  [namaSheet: string]: Tabel | undefined;
}

/** hasil analisis pencarian insiden serupa + detektor (analysis/ai_eval.json) */
export interface EvaluasiAI {
  retrieval: {
    n_eligible: number;
    full_p1: { pct: number; ci_lo: number; ci_hi: number };
    full_p5: { pct: number; ci_lo: number; ci_hi: number };
    full_p10: { pct: number; ci_lo: number; ci_hi: number };
    base_p1: { pct: number; ci_lo: number; ci_hi: number };
    base_p5: { pct: number; ci_lo: number; ci_hi: number };
    base_p10: { pct: number; ci_lo: number; ci_hi: number };
    lift_p1: number;
    lift_p5: number;
    lift_p10: number;
    prevalence_top_mech: string;
    prevalence_pct: number;
  };
  detector: {
    n_flagged: number;
    n_total: number;
    ci_lo: number;
    ci_hi: number;
    beaten_their_alarm: number;
    limitation: string;
    assets: {
      tag: string;
      first_flag_week: number | null;
      alarm_week: number | null;
      lead_weeks: number | null;
      flags: { basis: string }[];
    }[];
  };
}

/** hasil rekonsiliasi KPI (analysis/reconciliation.json) */
export interface Rekonsiliasi {
  A_incident_db: number;
  A_source: string;
  B_pi_tags: number;
  B_per_asset: Record<string, number>;
  B_source: string;
  C_declared: number;
  C_per_asset: Record<string, number>;
  C_source: string;
  mismatched_assets: string[];
  canonical: string;
  canonical_value: number;
  note: string;
}

/** seluruh data yang ditanam di dasbor */
export interface DataDasbor {
  incidents: Insiden[];
  equipment: Record<string, DataAset>;
  production: Record<string, DataProduksi>;
}

/** satu baris tabel insiden yang sudah diperkaya saat runtime */
export interface BarisInsiden extends Omit<Insiden,
  "downtime" | "total_loss" | "act_loss" | "pot_loss" | "risk_score"> {
  downtime: number;
  total_loss: number;
  act_loss: number;
  pot_loss: number;
  risk_score: number;
  dt: Date | null;
}

/** satu baris riwayat kondisi mingguan setelah diparse */
export interface KondisiMinggu {
  week: number;
  date: string;
  status: string;
  remark: string;
  [parameter: string]: string | number | null | undefined;
}

/** satu aset setelah dimodelkan */
export interface Aset {
  tag: string;
  info: Record<string, unknown>;
  limits: Record<string, string>;
  ch: KondisiMinggu[];
  kpi: Record<string, number | string>;
  alarmWeeks: number;
  leadDays: number | null;
  firstAlarm: number | null;
  tripWeek: number | null;
  params: string[];
}

/** satu aset produksi setelah dimodelkan */
export interface AsetProduksi {
  tag: string;
  series: {
    t: string;
    amp: number | null;
    kw: number | null;
    feed: number | null;
    rate: number | null;
    on: boolean;
  }[];
  onHours: number;
  offHours: number;
  kwh: number;
  avgAmp: number;
  avgKw: number;
  prod: number;
  rateKey: string | undefined;
  ampKey: string | undefined;
  hdr: string[];
}

/** satu kelompok agregat (dipakai oleh group()) */
export interface Grup {
  k: string;
  n: number;
  loss: number;
  downtime: number;
}
