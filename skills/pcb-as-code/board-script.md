# Board script skeleton

A working order of passes, condensed from a 46 × 40 mm two-layer board (buck regulator,
ESP32 module, relay, sense inputs). Replace the parts, keep the order.

```python
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools", "hw-design", "src"))
import pcbnew  # noqa: E402
from hwdesign.kicad.board import (Board, acute_angles, drc, foreign_copper,  # noqa: E402
                                  narrow_tracks, path_length, render)

BUILD = os.path.join(HERE, "build")
PCB = os.path.join(HERE, "my-board.kicad_pcb")

b = Board(os.path.join(BUILD, "my-board.net"), track=0.25, clearance=0.2, via=(0.6, 0.3), min_drill=0.2,
          declared=os.path.join(HERE, "intended_netlist.json"), fp_dirs=[os.path.join(HERE, "lib")])
b.netclass("Power", ["+12V", "GND"], track=0.4)
b.netclass("Harness", ["LINE_A", "LINE_B"], track=0.4, clearance=0.5)   # lines that leave the box
b.outline_rounded(100, 100, 46, 40, r=1.5)

# 1. placement: datasheet-critical parts fixed, the rest near what they serve
b.place("U1", 121.0, 111.6, 270)
b.place_near("R6", *b.pad_xy("Q1", "1"))
for f in ("FID1", "FID2", "FID3"):                  # Freerouting ignores pad-local clearance
    p = b.fps[f].GetPosition()
    x, y = pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)
    b.keepout(x - 1.8, y - 1.8, 3.6, 3.6, layers=(pcbnew.F_Cu,), name=f + "-clear")
assert not b.courtyard_overlaps()


# 2. hand routes: the paths the circuit depends on, pad to pad (see SKILL.md on vias)
def hand_route():
    T = b.track
    T("SW", [("U1", 6), ("C3", 2), ("D3", 1), ("L1", 1)], 0.6)   # hot loop, top layer only
    T("FB", [("R9", 2), ("R10", 1), (120.05, 110.8)], 0.25)       # may end inside a pad
    b.via("GND", 115.6, 110.8)                                     # own ground via into the plane


hand_route()
b.chamfer_corners()                                   # after ALL hand routes
b.keepout(116.2, 102.0, 15.4, 20.0, layers=(pcbnew.B_Cu,), name="buck-plane",
          tracks=True, vias=False, fills=False)       # plane stays whole, vias allowed

# 3. autoroute, then clean up in this order
b.autoroute(BUILD, passes=150)
print("unrouted after autorouting:", b.unrouted())
b.remove_redundant()                                  # autorouter duplicates of hand routes
b.widen()                                             # neck-downs back to class width
b.straighten()                                        # micro-jogs
for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    b.zone("GND", layer)
b.fill_zones()
b.remove_redundant(nets=["GND"])                      # ground tracks the pours cover
b.stitch("GND", pitch=3.0)
b.prune_dangling()
assert b.unrouted() == 0, "unrouted connections"

b.save(PCB)
b.write_project(os.path.join(HERE, "my-board.kicad_pro"), min_track=0.12)
drc(PCB, os.path.join(BUILD, "drc.rpt"))

# 4. checks DRC cannot do; fail the build on any of them
pb = pcbnew.LoadBoard(PCB)
bad = []
for net, a, c, limit_mm, max_vias in [("SW", "U1.6", "L1.1", 8, 0), ("FB", "U1.3", "R10.1", 3, 0)]:
    r = path_length(pb, b.resolve(net), a, c)
    if r is None or r[0] > limit_mm or r[1] > max_vias:
        bad.append((net, a, c, r))
bad += foreign_copper(pb, (119.5, 113.3, 126.0, 117.8), {b.resolve(n) for n in ("SW", "+12V", "GND")})
bad += [n for n in narrow_tracks(pb, b.classes, b.rules["track"]) if n[-1] == "auto"]
bad += acute_angles(pb)
print("layout problems:", bad or "none")
render(PCB, os.path.join(BUILD, "front.png"), layers="F.Cu,F.SilkS,Edge.Cuts", width=2000)
render(PCB, os.path.join(BUILD, "back.png"), layers="B.Cu,Edge.Cuts", width=2000)
sys.exit(1 if bad else 0)
```

Notes:
- `track()` points are `(x, y)` in mm or `(ref, pad)`. A point inside a pad connects; it does
  not have to be the pad centre. That lets a route enter a pad straight instead of jogging to
  its centre.
- `via_near(net, ref, pad)` after autorouting adds a ground via where a small top-layer island
  would otherwise hang on one via.
- `place_near` searches outwards for the first free spot; check the result in the render.
  Fixed placement with a comment saying why is easier to review.
