# Production Engine Selection

## Single production path

The only production analysis path is:

`backend.api.analysis._run`

It acquires real Earth Engine data, preserves canonical `cell_id`, computes the
active statistical ensemble, spectral-proxy geology, per-cell historical
surface/LULC change, 30 m thermal context, surface-context suppression and
final evidence ranking.

## Legacy engines

The old `full_analysis_engine*.py`, `zone_intelligence.py`, and related
orchestrator/fusion modules are retained as **research/audit assets**. They are
not imported into the production fusion unless explicitly promoted after
passing the current scientific contract.

In particular, no legacy engine may inject a fixed `AI=100`, fabricated
confidence, or a second copy of the same statistical model into the production
score.

## Scientific naming

- `strength_percent` = relative evidence/ranking score within the AOI.
- It is **not** a probability.
- Thermal evidence is 30 m context.
- Iron/clay ratios use 20 m source bands and are spectral proxies.
- Historical change means observed surface/LULC change; it is not proof of
  human intervention, age, excavation, or a subsurface object.
