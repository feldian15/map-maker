# MVP Route Geometry Spec

## Problem Statement

People who walk or run want routes that begin at a chosen coordinate, return to that same coordinate, and resemble a simple visual route shape while staying on real walkable/runnable streets, trails, and paths. They need a command-line tool that can produce route geometry as GeoJSON without requiring a web UI or turn-by-turn directions.

## Solution

Build a CLI-only MVP that accepts a start location, target distance in meters, route shape, and output path. The tool loads an OpenStreetMap-backed travel network, generates candidate loop routes for the requested route shape, chooses the best-match route by distance and adherence to ordered shape samples, and writes a GeoJSON file containing the selected route geometry and metadata.

## User Stories

1. As a runner, I want to provide a start location as latitude and longitude, so that the route starts where I plan to begin.
2. As a runner, I want the generated route to return to the start location, so that I can finish where I began.
3. As a runner, I want to request a perfect square route shape, so that my route resembles a square.
4. As a runner, I want to request an equilateral triangle route shape, so that my route resembles a balanced triangle.
5. As a runner, I want to request a right triangle route shape, so that my route resembles a 45-45-90 triangle.
6. As a runner, I want to provide a target distance in meters, so that the generated route is sized for my workout.
7. As a runner, I want routes within five percent of my target distance when possible, so that the route length is useful in practice.
8. As a runner, I want the shortest matching route when no route is available within tolerance, so that I still get the closest useful route shape.
9. As a runner, I want the route to stay on walkable/runnable streets, trails, and paths, so that the route can be followed in the real world.
10. As a runner, I want highways excluded from the travel network, so that the route avoids unsafe or inappropriate segments.
11. As a runner, I want a clear error when no matching route can be generated, so that I understand the request failed.
12. As a CLI user, I want to write the result to a GeoJSON file, so that I can open the route in mapping tools.
13. As a CLI user, I want the output to include route metadata, so that I can see the requested shape, target distance, actual distance, and whether tolerance was met.
14. As a future UI developer, I want route generation separated from CLI parsing, so that a dedicated UI can reuse the same route engine later.
15. As a maintainer, I want deterministic tests around route-shape behavior, so that routing changes can be made confidently without live network dependence.

## Implementation Decisions

- V1 is CLI-only. No web UI is included, but the route engine must be reusable by a future UI.
- The CLI accepts a start location as latitude/longitude coordinates only.
- The CLI accepts target distance in meters only.
- The CLI requires an output path for the GeoJSON file.
- MVP route shapes are perfect square, equilateral triangle, and right triangle.
- Right triangle means a 45-45-90 route shape in v1.
- All MVP routes are loop routes: they start and end at the same start location.
- The start location is one ordered shape sample on the route shape outline.
- Route shapes are scaled from the target distance before matching to the travel network.
- Shape matching uses ordered shape samples, including both corners and any intermediate samples needed to preserve the visible route shape.
- Shape sample counts are fixed internally, but may vary by route shape and target distance.
- The route generator tries multiple orientations and chooses the best-match route by target distance and adherence to the requested route shape.
- Route direction is not user-facing in v1.
- Repeated segments are allowed in v1.
- The route generator loads an OpenStreetMap-backed travel network using `osmnx`, represented as `networkx` graphs.
- The travel network is walk/run oriented and excludes highways.
- The map search area is derived from target distance and bounded by the MVP's maximum practical search area.
- V1 accepts target distances from 1 km to 25 km inclusive.
- A distance-matched route is within five percent of the target distance.
- If no candidate route satisfies the target distance tolerance, output the shortest matching route.
- If no route can visit the required shape samples in order, fail with a clear error including the shape, start location, target distance, and map search area.
- GeoJSON output is a `FeatureCollection` with one route `LineString` feature and metadata properties including requested shape, target distance, actual distance, distance delta percent, start location, and whether the route met the five percent tolerance.
- `osmnx` built-in cache behavior may be used, but no custom project cache is designed in v1.

## Testing Decisions

- Test external behavior rather than implementation details.
- The primary testing seam is the reusable route-generation API: given a start location, target distance, route shape, and graph provider, it returns route geometry or a clear failure.
- CLI tests should cover argument validation, calling the route-generation API, and writing GeoJSON to the requested output path.
- Shape-generation tests should verify that each MVP route shape produces ordered shape samples scaled from target distance with the start location on the outline.
- Route-selection tests should use deterministic synthetic graph fixtures to verify distance tolerance, shortest matching fallback, repeated segment allowance, and failure when shape samples cannot be visited in order.
- Graph-loading tests should isolate OpenStreetMap access behind graph-loading boundaries so routine tests do not depend on live network calls.
- GeoJSON tests should verify the output contract from the user's perspective: one route `LineString` feature with the expected metadata.

## Out of Scope

- Web UI or desktop UI.
- Turn-by-turn directions.
- Address or place-name lookup.
- Cycling or driving route networks.
- User-supplied shapes.
- Text-shaped routes.
- Circle, heart, trapezoid, arbitrary triangles, or configurable shape parameters.
- Multiple route alternatives in one output.
- User-facing orientation controls.
- Unit parsing beyond meters.
- Custom OSM cache design.

## Further Notes

- This spec follows the glossary language in `GLOSSARY.md`.
- This spec respects the ADR to use OpenStreetMap-backed travel networks for v1.
- This spec respects the ADR to keep the v1 CLI thin and the route engine reusable.
