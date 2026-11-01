"""Measure generated solids (build123d): point-in-solid, distance to the next material
change along a ray, tessellation, vertical ray casts on a grid, and a STEP board split into
the bare board and its parts. Everything is measured on the solid, not on the CAD intent."""
import math

import numpy as np
from build123d import Vector


def inside(shape, p):
    return shape.is_inside(Vector(*p), 1e-4)


def edge_along(shape, p, d, smax, inside_start):
    """Distance from p along unit vector d to the first change of material state (bisection
    after a coarse 0.05 mm scan)."""
    p, d = np.array(p, float), np.array(d, float)
    step, t = 0.05, 0.0
    while t < smax:
        if inside(shape, p + (t + step) * d) != inside_start:
            lo, hi = t, t + step
            for _ in range(12):
                m = (lo + hi) / 2
                if inside(shape, p + m * d) == inside_start:
                    lo = m
                else:
                    hi = m
            return (lo + hi) / 2
        t += step
    return smax


def tess(shape, tol=0.03):
    v, t = shape.tessellate(tol, 0.2)
    return np.array([(q.X, q.Y, q.Z) for q in v]), np.array(t)


def columns(shape, x0, y0, nx, ny, d, tol=0.03):
    """Vertical ray casts on a grid: returns {(i, j): [(z_in, z_out), ...]}."""
    V, T = tess(shape, tol)
    hits = {}
    ox, oy = x0 + 0.00123, y0 + 0.00171            # avoid rays through mesh edges
    for tri in V[T]:
        (ax, ay, az), (bx, by, bz), (cx, cy, cz) = tri
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-12:
            continue
        i0 = max(int(math.ceil((min(ax, bx, cx) - ox) / d)), 0)
        i1 = min(int(math.floor((max(ax, bx, cx) - ox) / d)), nx - 1)
        j0 = max(int(math.ceil((min(ay, by, cy) - oy) / d)), 0)
        j1 = min(int(math.floor((max(ay, by, cy) - oy) / d)), ny - 1)
        if i1 < i0 or j1 < j0:
            continue
        I, J = np.meshgrid(np.arange(i0, i1 + 1), np.arange(j0, j1 + 1), indexing="ij")
        px, py = ox + I * d, oy + J * d
        l1 = ((by - cy) * (px - cx) + (cx - bx) * (py - cy)) / den
        l2 = ((cy - ay) * (px - cx) + (ax - cx) * (py - cy)) / den
        l3 = 1 - l1 - l2
        m = (l1 >= 0) & (l2 >= 0) & (l3 >= 0)
        z = l1 * az + l2 * bz + l3 * cz
        for i, j, zz in zip(I[m], J[m], z[m], strict=True):
            hits.setdefault((int(i), int(j)), []).append(float(zz))
    out = {}
    for k, zs in hits.items():
        zs = sorted(zs)
        if len(zs) % 2:
            zs = zs[:-1]
        out[k] = [(zs[n], zs[n + 1]) for n in range(0, len(zs), 2) if zs[n + 1] - zs[n] > 1e-4]
    return out


def leaf_parts(pcb):
    kids = list(pcb.children)
    while len(kids) == 1:
        kids = list(kids[0].children)
    board_solid = [k for k in kids if str(k.label).endswith("_PCB")][0]
    return board_solid, [k for k in kids if not str(k.label).endswith("_PCB")]
