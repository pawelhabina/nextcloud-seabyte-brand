<!--
  SPDX-FileCopyrightText: 2026 SeaByte
  SPDX-License-Identifier: GPL-2.0-or-later
-->
# SeaByte source asset audit

Source directory inspected read-only:
`/Users/pravel9/Documents/seabyte.pl/seabyte-logo`.

| File | Format | Dimensions / viewBox | Transparency | Intended role |
| --- | --- | --- | --- | --- |
| `seabyte-only-logo.svg` | SVG vector | `0 0 865.41666 1014.75586` | Yes | Primary source for square application and shell icons |
| `seabyte-full-logo.svg` | SVG vector | `0 0 865.41666 324.3641` | Yes | Wizard and installer wordmark |
| `seabyte-back-logo.svg` | SVG vector | `0 0 865.41666 1014.75586` | Yes | Optional large background mark |
| `seabyte-only-logo.png` | PNG RGBA | 1651 × 1657 | Yes | Raster reference |
| `seabyte-full-logo.png` | PNG RGBA | 3479 × 1237 | Yes | Raster reference |
| `seabyte-back-logo.png` | PNG RGBA | 2242 × 3441 | Yes | Raster reference |
| `seabyte-*-logo.ai` | PDF-compatible Adobe Illustrator | one page each | Vector | Original design interchange files |
| `seabyte-logo.zip` | ZIP | archive | N/A | Original delivery archive; not used by builds |
| `.DS_Store` | Finder metadata | N/A | N/A | Ignored |

The SVG files are preferred because they preserve shape and gradient fidelity
at every output size. No separately authored light/dark files are present.
The generator therefore produces normal full-colour artwork plus
single-colour template variants for system surfaces that require them.

Small icons are rendered from the symbol-only SVG, fitted without cropping into
a square canvas with transparent safe-area padding. This retains the logo
proportions and makes 16 × 16 output more legible.

