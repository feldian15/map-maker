# Map Maker

Terms for describing generated routes and their constraints.

## Language

**Route Geometry**:
The spatial shape of a generated route, represented as coordinates or connected path segments on a real travel network. It does not include turn-by-turn directions.
_Avoid_: Directions, navigation instructions

**Loop Route**:
A route that starts and ends at the same location. In the MVP, all generated routes are loop routes.
_Avoid_: Point-to-point route

**Repeated Segment**:
A street, trail, or path segment used more than once in the same loop route. Repeated segments are allowed in the MVP.
_Avoid_: Backtracking

**Route Shape**:
The requested visual silhouette of a loop route. MVP route shapes are perfect square, equilateral triangle, and right triangle.
_Avoid_: Route type, route archetype

**Right Triangle**:
A 45-45-90 route shape in the MVP.
_Avoid_: 3-4-5 triangle, arbitrary right triangle

**Shape Sample**:
An ordered point on a route shape that the generated route should visit in sequence on the travel network. Shape samples may include corners and intermediate points needed to preserve the visible silhouette, and the user's start location is one shape sample on the outline.
_Avoid_: Anchor, waypoint

**Start Location**:
The latitude and longitude where a loop route starts and ends.
_Avoid_: Address, place name

**Target Distance**:
The user's requested total route length. In the MVP, target distance must be 1 km to 25 km inclusive, and a generated route is distance-matched when its length is within five percent of the target distance.
_Avoid_: Exact distance

**Matching Route**:
A loop route that satisfies the requested route shape, even if it cannot satisfy the target distance tolerance.
_Avoid_: Valid route

**Best-Match Route**:
The selected generated route after comparing candidate orientations by target distance and adherence to the requested route shape.
_Avoid_: Optimal route

**Map Search Area**:
The area of the travel network loaded around the start location for route generation. Its radius is derived from the target distance and bounded by the MVP's maximum practical search area.
_Avoid_: Map extent, bounding box

**Travel Network**:
The walkable or runnable paths that a generated route may use, including streets, trails, and paths, while excluding highways.
_Avoid_: Synthetic grid, abstract graph
