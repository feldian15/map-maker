from __future__ import annotations

import json

import pytest

from routegen import cli
from routegen.models import Coordinate, RouteResult, RouteShape


def test_cli_validates_route_request() -> None:
    args = cli.build_parser().parse_args(
        [
            "--start",
            "41.881,-87.623",
            "--distance",
            "5000",
            "--shape",
            "square",
            "--output",
            "route.geojson",
        ]
    )

    request = cli.route_request_from_args(args)

    assert request.start == Coordinate(lat=41.881, lon=-87.623)
    assert request.target_distance_meters == 5000
    assert request.shape is RouteShape.SQUARE


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (
            [
                "--start",
                "41.0,-87.0",
                "--distance",
                "999",
                "--shape",
                "square",
                "--output",
                "route.geojson",
            ],
            "distance must be between 1000 and 25000 meters",
        ),
        (
            [
                "--start",
                "91,-87.0",
                "--distance",
                "1000",
                "--shape",
                "square",
                "--output",
                "route.geojson",
            ],
            "latitude must be between -90 and 90",
        ),
    ],
)
def test_cli_rejects_out_of_scope_requests(
    argv: list[str], message: str, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit):
        cli.run(argv)

    assert message in capsys.readouterr().err


def test_cli_writes_geojson_from_route_engine(
    tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "route.geojson"

    def fake_generate_route(request, graph_provider):
        assert request.shape is RouteShape.SQUARE
        assert graph_provider is cli.load_walk_run_graph
        return RouteResult(
            coordinates=[
                Coordinate(41.0, -87.0),
                Coordinate(41.0, -86.99),
                Coordinate(41.0, -87.0),
            ],
            requested_shape=RouteShape.SQUARE,
            target_distance_meters=1000,
            actual_distance_meters=980,
            distance_delta_percent=-2,
            start=Coordinate(41.0, -87.0),
            met_distance_tolerance=True,
        )

    monkeypatch.setattr(cli, "generate_route", fake_generate_route)

    exit_code = cli.run(
        [
            "--start",
            "41.0,-87.0",
            "--distance",
            "1000",
            "--shape",
            "square",
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    feature_collection = json.loads(output.read_text())
    assert feature_collection["type"] == "FeatureCollection"
    assert feature_collection["features"][0]["geometry"]["type"] == "LineString"
