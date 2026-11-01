"""Headless renders of build123d scenes with f3d: write shapes as OBJ + MTL (one material
per colour key), then render a camera view to PNG. Good enough to review a design by eye."""
import os
import subprocess

import numpy as np

# steel blue housing, light lid, green board, dark parts
COLOURS = {"base": (0.357, 0.498, 0.647), "lid": (0.627, 0.769, 0.886), "pcb": (0.18, 0.49, 0.2),
           "part": (0.25, 0.25, 0.27), "module": (0.75, 0.75, 0.78), "gland": (0.15, 0.15, 0.15),
           "cable": (0.1, 0.1, 0.1)}


def write_obj(items, path, colours=None):
    """items: [(name, shape, colour key)] -> OBJ + MTL. colours: {key: (r, g, b)} in 0..1."""
    colours = colours or COLOURS
    mtl = path[:-4] + ".mtl"
    with open(mtl, "w") as f:
        for k, (r, g, b) in colours.items():
            f.write("newmtl %s\nKd %.3f %.3f %.3f\nKa 0 0 0\nKs 0.1 0.1 0.1\nNs 20\n\n" % (k, r, g, b))
    off = 1
    with open(path, "w") as f:
        f.write("mtllib %s\n" % os.path.basename(mtl))
        for name, shape, col in items:
            v, t = shape.tessellate(0.03, 0.2)
            if not t:
                continue
            V = np.array([(q.X, q.Y, q.Z) for q in v])
            f.write("o %s\nusemtl %s\n" % (name, col))
            f.write("".join("v %.4f %.4f %.4f\n" % tuple(p) for p in V))
            f.write("".join("f %d %d %d\n" % (a + off, b + off, c + off) for a, b, c in t))
            off += len(V)


def f3d(obj, png, pos, focal, up="0,0,1", res="1600,1000"):
    subprocess.run(["f3d", obj, "--output", png, "--resolution", res, "--camera-position", pos,
                    "--camera-focal-point", focal, "--camera-view-up", up, "--background-color", "1,1,1",
                    "--up", "+Z", "--no-config", "--coloring-mode", "material"],
                   check=False, capture_output=True)
