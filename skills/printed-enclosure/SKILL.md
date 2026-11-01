---
name: printed-enclosure
description: Design a 3D-printed (FDM, ASA/ABS/PETG) enclosure for a PCB in build123d, driven by the board's exported geometry, and prove it with measured checks (fit, board clamping, gasket squeeze, screw engagement, overhangs, mass and print time). Use when building or changing a housing for a board, when a board change might affect parts already printed, or when prints warp, lift off the bed or don't seal.
---

# Printed enclosure

The housing is generated from the board, not drawn next to it. When the board changes,
rebuild the housing and run its checks in the same step.

## Inputs from the board

`hwdesign.kicad.geometry.export(pcb, json_path, extra={...})` writes `board.json`. Export the
STEP alongside it with `kicad-cli pcb export step --subst-models`. The JSON has, in mm from the
outline's top-left corner:
- the board size and thickness;
- each part's courtyard box, pads (with drill and net) and whether it is through-hole;
- mounting holes (footprints `H*`) and rule areas (keepouts);
- `extra`: numbers the KiCad data doesn't carry, such as the tallest part above the board or
  an antenna's real overhang.

Part heights come from the STEP (`probe.leaf_parts` splits it into board and parts), which
also feeds the interference checks and renders.

## Structure

- `housing.py`: parameters at the top with the reason for each value. `build()` returns all
  solids, and `export()` writes STL and STEP.
- **Snap every critical height to the layer grid** (0.2 mm). A ledge at 2.3 mm prints at
  2.2 or 2.4, and the board then rattles or binds.
- `check.py`: a table of `name, PASS/FAIL, measured, required`, measured on the generated
  solids, not on the parameters. Exit 1 on any failure. `hwdesign.mcad` provides the
  measuring:

| Module | Tools | Use for |
|---|---|---|
| `probe` | `inside`, `edge_along`, `columns`, `leaf_parts` | point tests, distances along rays, vertical ray casts, splitting the board STEP into board and parts |
| `gasket` | `gasket_cord`, `gasket_tpu`, `shore_to_E` | squeeze, force estimates |
| `printing` | `overhangs`, `mass_time` | print orientation, grams, hours |
| `render` | `write_obj`, `f3d` | headless renders for review (needs `f3d`) |

Install: `pip install "hwdesign[mcad]"`, or the submodule plus a venv with build123d, numpy
and scipy.

## Rules learned

**A board change can change printed parts.** Board-clamping fingers in the lid avoid part
courtyards and fiducials. Moving a fiducial into a corner shortened one finger by 2 mm. When
someone has already printed:
1. Rebuild the housing from the commit they printed (`git worktree add <dir> <commit>`).
2. Compare the meshes with today's: bytes, volume, and the parameters that differ.
3. Tell them exactly what changed per part. For example: "base byte-identical, lid: one
   finger 1 mm higher", and whether the old print still works.

**Sealing.**
- Use a 1.5 mm silicone cord (50–60 Shore A) in a groove, sized for 16–20 % squeeze.
- About 0.2 mm of warp on the sealing land is fine: it moves the squeeze by a few percent.
  Check after printing on glass or a tile, with paper or a feeler gauge.
- A flat lid screwed down at enough points pulls a slight bow flat. Check screw spacing with
  the gasket force estimate.

**Fasteners in ASA or ABS.**
- Heat-set inserts: M3, 4.6 mm OD, 5.7 mm long, in a 4.0 mm hole.
- Choose screw lengths so the tip stays clear of the hole bottom.
- No anaerobic threadlocker on ASA or ABS: it causes stress cracking. Use a non-anaerobic one
  or nothing.

**Printing ASA or ABS.** Details in [printing.md](printing.md). In short:
- enclosure warmed up;
- bed at 100–110 °C;
- part fan low;
- slow first layer;
- 5 mm brim when corners lift.

**Show before printing.** Render the closed, open and section views, check the board and
cable path in the section, and only then hand over the STL files.
