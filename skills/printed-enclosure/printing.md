# Printing ASA and ABS enclosures

Settings that produced sealed, dimensionally right housings on an enclosed Klipper printer
with a 0.4 mm nozzle.

## Slicer

| Setting | Value | Why |
|---|---|---|
| Layer height | 0.2 mm | All critical heights in the model are on this grid |
| Walls | 6 (2.4 mm) | Solid walls around inserts and the sealing land |
| Top / bottom layers | 6 / 6 | |
| Infill | 25 % gyroid | |
| Supports | none | Design out overhangs instead; `overhangs()` reports what is left |
| Ironing | optional, on sealing faces | A smoother land for the gasket |

Orientation: the base upright on its floor, the lid outer face down, so the sealing faces
print as top surfaces.

## Warping and bed adhesion

In order of effect:
1. Enclosure closed and preheated for 15–20 minutes, no drafts.
2. Bed at 100–110 °C. Glue stick on smooth PEI; textured PEI as is.
3. Part cooling off for the first layers, then at most 20–30 %. ASA warps from the top as it
   cools, not only at the bed.
4. Slow first layer (20–30 mm/s), slightly squished.
5. A 5 mm brim when corners still lift. On these parts it sits at the floor edge or the lid's
   outer face, never on a sealing face; trim it cleanly.
6. A draft shield, if the enclosure cools fast.

If corners still lift after all that, change the design: small sacrificial discs ("mouse
ears") at the corners, or larger corner radii.

## After printing

- Stand the base upside down on glass or a tile and check the sealing land with paper or a
  0.2 mm feeler gauge.
- Fit the board before inserting heat-set inserts: a tight fit is easier to fix in bare
  plastic.
- Tap printed threads (cable glands) with the real tap. Printed threads alone don't seal.
