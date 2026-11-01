"""FDM print estimates for a solid: printed volume, mass and time for given walls, top/bottom
thickness and infill (voxel distance transform), and downward-facing overhang area clustered
by location. Estimates for slicer settings like 6 walls, 6 top/bottom layers, 25 % infill."""
import numpy as np
from scipy import ndimage

from .probe import columns, tess


def mass_time(shape, rho=1.07, walls=2.4, tops=1.2, infill=0.25, vox=0.4):
    bb = shape.bounding_box()
    nx, ny = int(bb.size.X / vox) + 3, int(bb.size.Y / vox) + 3
    cols = columns(shape, bb.min.X - vox, bb.min.Y - vox, nx, ny, vox, tol=0.05)
    nz = int(bb.size.Z / (vox / 2)) + 3
    vol = np.zeros((nx, ny, nz), bool)
    zc = bb.min.Z - vox / 2 + (np.arange(nz) + 0.5) * vox / 2
    for (i, j), iv in cols.items():
        for za, zb in iv:
            vol[i, j, (zc > za) & (zc < zb)] = True
    # anisotropic: z distances scaled so that 'tops' mm counts like 'walls' mm
    dist = ndimage.distance_transform_edt(vol, sampling=(vox, vox, vox / 2 * walls / tops))
    v_vox = vox * vox * vox / 2
    v_all = vol.sum() * v_vox
    v_core = (dist > walls).sum() * v_vox
    v_print = v_all - v_core * (1 - infill)
    layers = bb.size.Z / 0.2
    t_s = (v_all - v_core) / 4.0 + v_core * infill / 8.0 + layers * 2.0    # 4 / 8 mm3/s, 2 s/layer
    return dict(v_solid=shape.volume / 1000, v_vox=v_all / 1000, v_print=v_print / 1000,
                g=v_print / 1000 * rho, t_h=t_s / 3600)


def overhangs(shape, flip=False, nz_lim=-0.75):
    V, T = tess(shape, 0.05)
    if flip:
        V = V * np.array([1, -1, -1])
    V[:, 2] -= V[:, 2].min()
    tri = V[T]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    area = np.linalg.norm(n, axis=1) / 2
    nzu = n[:, 2] / (np.linalg.norm(n, axis=1) + 1e-12)
    zmin = tri[:, :, 2].min(axis=1)
    m = (nzu < nz_lim) & (zmin > 0.05) & (area > 0)
    cen = tri[m].mean(axis=1)
    clusters = {}
    for c, a in zip(cen, area[m], strict=True):
        k = (round(c[0] / 6) * 6, round(c[1] / 6) * 6, round(c[2], 1))
        clusters[k] = clusters.get(k, 0) + a
    return float(area[m].sum()), sorted(clusters.items(), key=lambda kv: -kv[1])
