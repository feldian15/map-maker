# Use OpenStreetMap for V1 Travel Networks

V1 route geometry must follow actual walkable and runnable streets, trails, and paths rather than synthetic graphs or pure geometric outlines. We will use OpenStreetMap-backed network data through `osmnx`, because it loads real travel networks into `networkx` graphs and keeps the later routing model aligned with the MVP product promise.
