"""Helpers measured on solids with known answers."""
import pytest

build123d = pytest.importorskip("build123d")
from build123d import Align, Box, Pos  # noqa: E402

from hwdesign.mcad.printing import mass_time, overhangs  # noqa: E402
from hwdesign.mcad.probe import edge_along, inside  # noqa: E402

BASE = (Align.CENTER, Align.CENTER, Align.MIN)


def cube():
    return Box(20, 20, 20, align=BASE)


def test_inside_and_distance_to_face():
    c = cube()
    assert inside(c, (0, 0, 10)) and not inside(c, (0, 0, 25))
    assert edge_along(c, (0, 0, 10), (1, 0, 0), 30, True) == pytest.approx(10, abs=0.01)


def test_flat_bottom_is_not_an_overhang():
    area, _ = overhangs(cube())
    assert area == pytest.approx(0, abs=1e-6)


def test_table_top_overhang():
    # 20 x 20 plate on a 4 x 4 column: its underside minus the column is overhang
    t = Box(4, 4, 10, align=BASE) + Pos(0, 0, 10) * Box(20, 20, 2, align=BASE)
    area, clusters = overhangs(t)
    assert area == pytest.approx(400 - 16, rel=0.01)
    assert clusters


def test_solid_cube_volume():
    est = mass_time(cube(), walls=50, tops=50)     # walls thicker than the part: all solid
    assert est["v_solid"] == pytest.approx(8.0, rel=1e-6)
    assert est["v_print"] == pytest.approx(8.0, rel=0.1)
