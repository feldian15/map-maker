# Map Maker

Map Maker generates loop route geometry for walking and running. The MVP is a
CLI named `routegen` that accepts a start coordinate, target distance, route
shape, and GeoJSON output path.

## Install

```bash
uv sync
```

## Verify

```bash
uv run ruff check
uv run ruff format
uv run pytest
```

## Run

```bash
uv run routegen --start 41.881,-87.623 --distance 5000 --shape square --output route.geojson
```

`--start` is latitude and longitude as `lat,lon`. `--distance` is meters only
and must be from 1000 to 25000 inclusive. `--shape` supports:

- `square`
- `equilateral-triangle`
- `right-triangle`

The output file is a GeoJSON `FeatureCollection` with one route `LineString`.
The route feature includes metadata for the requested shape, target distance,
actual distance, distance delta percent, start location, and whether the route
met the five percent distance tolerance.

Open the generated `.geojson` file in a mapping tool that supports GeoJSON, or
inspect it directly to confirm the route coordinates and metadata properties.
