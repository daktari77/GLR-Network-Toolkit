---
target: src/gui/panels/monitor_panel.py
total_score: 22
p0_count: 0
p1_count: 3
timestamp: 2026-06-05T09-33-15Z
slug: src-gui-panels-monitor-panel-py
---
## Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 2 | No live UP/DOWN summary; status bar message is ephemeral |
| 2 | Match System / Real World | 2 | Italian labels mixed with English UI |
| 3 | User Control and Freedom | 2 | Remove is instant/destructive; no undo; no multi-select |
| 4 | Consistency and Standards | 2 | All-center alignment; dark chart on light panel; language mix |
| 5 | Error Prevention | 2 | Remove has no confirmation; start-with-no-hosts shows only status bar |
| 6 | Recognition Rather Than Recall | 3 | All toolbar actions visible; no search/filter for large host lists |
| 7 | Flexibility and Efficiency | 2 | No keyboard shortcuts; no multi-select; send_to_* signals dead |
| 8 | Aesthetic and Minimalist Design | 2 | 12 columns equal weight; ALL CAPS status + full-row color noisy |
| 9 | Error Recovery | 2 | Error column clips; file parse failures silent; raw error strings |
| 10 | Help and Documentation | 1 | No tooltips; placeholder text is Italian |

Total: 22/40 Acceptable

## Priority Issues

[P1] Italian/English language mix in HistoryTable and LatencyChart
[P1] All cells center-aligned (text left, numbers right is the convention)
[P1] No empty state — blank table gives no guidance on first open
[P2] LatencyChart dark background is a visual island in a light-themed panel
[P2] Full-row pastel coloring + ALL CAPS status text — noisy and soft

## Persona Red Flags

Alex (Power User): No keyboard shortcuts on Start/Stop; send_to_* signals defined but never emitted; one-at-a-time remove; no filter/search
Riley (Stress Tester): Silent parse failures; add_host_tcp() dedup bug; unbounded queue drain
Michele (Solo Operator): Monitoring active state not persistently visible; interval change while active has no effect
