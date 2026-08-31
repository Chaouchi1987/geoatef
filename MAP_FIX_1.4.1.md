# Map Fix 1.4.1

The map is now initialized only after the authenticated app shell becomes visible.
This prevents Leaflet from measuring a display:none container and rendering only a
small strip of tiles. ResizeObserver and delayed invalidateSize calls keep the map
synchronized with the responsive grid.

No synthetic basemap is used.
