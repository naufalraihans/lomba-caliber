# CALIBER 2026 — Case 2: Intelligent Manufacturing

Single-file dashboard prototype (English). No build step, no backend, no dependencies — open `index.html` in any browser.

**Live demo:** deploy this repo on Vercel (static, no settings needed) or open `index.html` locally.

## What's inside

| Tab | Content |
|-----|---------|
| Overview | US$67.19M loss, 2,261.1 h downtime, 380 incidents at a glance |
| RCA & CAPA | All 5 RCA decks integrated (4P, 4M+1E, CAPA, PM schedule) |
| Case Reconstruction | KO-3201 traced end to end: signal → alarm → gap → trip → loss → owner |
| KPI Contract | One KPI computed three ways (incident DB / PI tags / declared) |
| Energy / Production / Emissions | Derived estimates, labeled as estimates |
| Downtime | Portfolio downtime patterns |
| Problem Queue | Active degradation ranked by exposure |
| AI Pilot | Autopilot loop: detect → queue → assign → guide → verify (top-10 plan, one click) |
| Asset Detail | Per-asset deep dive with similar-incident retrieval |
| Action Tracking | 179 of 220 overdue actions, oldest due Feb 2024 |
| Model Evaluation | Retrieval @1 87.1%, honest limits published |
| Data Governance | Defects found in the baseline itself |

## Reproduce

```bash
bun run prototype/build-dasbor.ts   # rebuild prototype/dasbor.html (31 checks)
bun prototype/cek-dasbor.ts         # runtime verify all 14 tabs (figures + English)
```

Sources: `prototype/src/dasbor.ts` + `analysis/*.json`. Edit the source, rebuild, done.
