# GeoAnomaly Pro — Deep Audit Log

## Scope
Scientific, engineering, technical, security and UI review of the working tree.
No release archive is declared final by this document.

## Corrections completed in working tree
- Removed self-import corruption in anthropogenic-risk compatibility layer.
- Separated historical human-surface-change evidence from surface-artifact penalty.
- Added explicit AOI geometry type propagation (circle/square) and corrected area semantics.
- Restricted AOI radius to the intended 10–500 m product range at API level.
- Added Sentinel-2 cloud-probability matching alongside QA60 masking.
- Reworked historical temporal analysis to compare the same calendar seasons across years instead of arbitrary annual medians.
- Preserved canonical cell identity through Earth Engine sampling and DataFrame merges.
- Removed global median imputation from production fusion; missing evidence is excluded per cell and weights are renormalized per cell.
- Target selection occurs after final evidence fusion and only within the requested AOI.
- Preserved missing sample values in serialized results instead of converting them to zero evidence.
- Fixed legacy temporal compatibility wrapper so old orchestrators do not call a nonexistent function.
- Marked legacy scoring/orchestration modules explicitly as compatibility-only.
- Added client-side layer manager state synchronization with Leaflet basemap/AOI/target layers.
- Added explicit button types, language script loading and language toggle wiring.
- Added dynamic HTML escaping for server-supplied UI text.
- Added client-side request timeout handling.
- Cleared analysis state on logout.
- Reduced application CSS !important usage from the previous override-heavy state to only third-party/visibility cases.
- Added counter-case scientific tests.

## Validation
- Backend Python files parsed/compiled successfully.
- Import graph has no static local cycles.
- Production API imports successfully without Earth Engine package installed.
- Scientific contract tests: 6 passed.
- Frontend JS syntax: app.js and i18n.js pass Node syntax checking.
- HTML duplicate IDs: 0.
- HTML buttons without explicit type: 0.
- JS selector references to missing IDs: 0.
- Live Earth Engine regression remains environment-dependent and is not marked PASS here.

## Known boundary
The current audit environment does not have a usable Earth Engine Python package/credential set, so live EE acquisition cannot be truthfully marked as executed here. The release must pass a real-device EE regression before being called production-final.
