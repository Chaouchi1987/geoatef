# GeoAnomaly Pro — Deep Audit Working Log

## Policy
No release/archive is produced until scientific, engineering and technical gates pass.
The uploaded source remains the reference; this directory is a private working tree.

## Findings confirmed
- Active `/analysis/start` used real Earth Engine Sentinel-2/SRTM acquisition.
- Canonical `cell_id` was not preserved in the uploaded active sampler.
- AOI square helper had an upper-latitude typo (`lat + dlon` instead of `lat + dlat`).
- Active temporal pipeline sampled one AOI-center point per year, not each target/grid cell.
- Active thermal pipeline sampled one target point plus annulus per run, then applied the resulting score to all ranked cells.
- Legacy statistical engines were run again after the current anomaly ensemble, creating double-counted correlated evidence.
- Legacy geology engine used percentile ranks plus arbitrary slope/elevation bonuses.
- Active target selection took the top three rows without spatial non-maximum suppression; adjacent cells could become T01/T02/T03.
- Legacy anthropogenic module contained a self-import cycle and fixed `ai_score=100` path.
- Multiple historical orchestrator modules contain fixed experimental AI values and are not production-routed by `backend.main`.
- Frontend contained duplicated DOMContentLoaded control blocks; map-focus toggled `body.map-focus` while CSS expects `.app-shell.map-focus`.
- Frontend advertised v1.5.12 while source tree contained later UI changes.
- Frontend AOI radius control exposed only 10–50 m although product requirement allows up to 500 m.
- Earth Engine test suite cannot run in the current audit container because `earthengine-api` is not installed; requirements pin it correctly.

## Working corrections applied internally
- Stable `cell_id` + grid lon/lat attached before EE sampling.
- Corrected AOI rectangle latitude bound.
- Temporal sampling redesigned to per-cell 2018–2025 Sentinel comparison.
- Landsat 8/9 thermal sampling redesigned to per-cell LST with QA_PIXEL/QA_RADSAT masking.
- Geological score reduced to robust spectral-proxy anomaly; terrain is no longer silently treated as mineral evidence.
- Legacy statistical scoring isolated from final score until engine-by-engine validation.
- Surface-artifact risk layer added before ranking.
- Target selection now uses distance-based non-maximum suppression.
- Legacy anthropogenic self-import cycle removed in working tree.
- Frontend duplicate control blocks removed and map-focus unified.
- AOI radius UI expanded to 10–500 m.

## Remaining gates
1. Verify S2 cloud masking with S2 Cloud Probability/Cloud Score+ and edge masking.
2. Verify temporal seasonal comparability and observation counts per year/cell.
3. Validate thermal score semantics and source resolution limitations.
4. Audit ASTER before allowing it into any final score.
5. Audit every legacy engine for duplicated evidence and unit mismatches.
6. Validate final fusion mathematically and rename scores that are not calibrated probabilities.
7. Add regression tests for agricultural edges, vegetation, water, built-up areas, NoData and stable anomalies.
8. Run full dependency-installed tests, then a live Earth Engine scan.
9. Fix frontend/report contracts after backend is stable.
10. Only then produce one final drop-in release.

## Deep audit pass — 2026-08-27 18:35+
- Verified current working tree with pytest: 11/11 passed.
- Verified Python compilation across backend: PASS.
- Verified frontend JS syntax with Node: app.js PASS, i18n.js PASS.
- Removed unreachable AOI-outside fallback from production target ranking; production now fails rather than fabricating an outside-AOI target.
- Target result cards are semantic `<button type="button">` controls and retain keyboard/focus behavior.
- Dynamic PDF button now explicitly uses `type="button"`.
- Layer manager remains the single source of truth for AOI visibility; removed conflicting Leaflet overlay event state changes.
- Added explicit button styling for target cards to prevent browser-default button rendering from breaking the GIS card design.
- Reviewed current GitHub GIS UI patterns: MapStore2 TOC/layer management, background/CRS/navigation tools; TerriaJS hierarchical catalogs, independently toggled layers, and time-aware map workflows.
- Live Earth Engine and real-browser visual regression remain environment-dependent and are not marked PASS without actual runtime execution.

## Final local regression pass — 2026-08-27
- Full local pytest suite: 11/11 passed.
- Python compileall: PASS.
- JavaScript syntax: app.js PASS; i18n.js PASS.
- HTML ID audit: 61 IDs, 0 duplicates.
- JS-to-DOM reference audit: 0 missing references.
- CSS `!important`: 5 remaining, intentionally scoped.
- Production target path contains no random target generation.
- No production use of `eval`, `exec`, `os.system`, or `shell=True` found in the audited path.
- Score reproduction test passed within floating-point tolerance (<1e-12).
- Counter-case regression suite passed for vegetation, crops, water, built-up, land-cover boundary, missing evidence, and stable anomaly cases.
- Report/PDF contract remains single-source from final target result; report layer does not recompute target scores.
- Final release is NOT certified for live Earth Engine execution or visual browser regression from this container. These require the user's configured Earth Engine credentials/dependencies and a real browser runtime.
