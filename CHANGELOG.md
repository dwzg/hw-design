# Changelog

## Unreleased

- GitHub Copilot CLI support: agents list `execute` next to `Bash`, so they keep a shell on
  Windows; README shows the Copilot install.

## 0.1.0

First release, extracted from [probe-wink](https://github.com/dwzg/probe-wink).

- `hwdesign.kicad`: schematic generator, ERC and netlist parity (`verify`), board builder with
  Freerouting and cleanup passes, layout checks, JLCPCB export, enclosure geometry export.
  Netlist reading moved to `netlist.py`, so parity checks work without `pcbnew`.
- `hwdesign.mcad`: solid probing, gasket and print estimates, f3d renders (from the
  probe-wink housing checks; the colour table is now a parameter).
- Skills: `pcb-as-code`, `pcb-review`, `jlcpcb-order`, `printed-enclosure`.
- Agents: `layout-reviewer`, `placement-preview-checker`.
