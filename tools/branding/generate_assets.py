#!/usr/bin/env python3
"""
SPDX-FileCopyrightText: 2026 SeaByte
SPDX-License-Identifier: GPL-2.0-or-later

Generate SeaByte Cloud application, installer and integration artwork.

Inputs are read from branding/source and are never modified. All output is
derived deterministically from the SVG source files.
"""

from __future__ import annotations

import base64
import io
import os
import shutil
import struct
from pathlib import Path
from xml.etree import ElementTree

# Homebrew's cairo is keg-linked outside the system loader paths on macOS.
if os.uname().sysname == "Darwin":
    fallback_paths = [path for path in ("/opt/homebrew/lib", "/usr/local/lib") if Path(path).is_dir()]
    current_fallback = os.environ.get("DYLD_FALLBACK_LIBRARY_PATH", "")
    os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = ":".join(fallback_paths + ([current_fallback] if current_fallback else []))

import cairosvg
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "branding" / "source"
GENERATED = ROOT / "branding" / "generated"
SYMBOL_SVG = SOURCE / "seabyte-only-logo.svg"
WORDMARK_SVG = SOURCE / "seabyte-full-logo.svg"

APP_SIZES = (16, 20, 24, 32, 40, 48, 64, 128, 256, 512, 1024)
STATUS_SIZES = (16, 32, 64, 128, 256)
ICO_SIZES = (16, 20, 24, 32, 40, 48, 64, 128, 256)
STATES = ("error", "ok", "pause", "sync", "offline", "warning", "info")
STATE_COLORS = {
    "error": "#d94141",
    "ok": "#2f9e62",
    "pause": "#e39a25",
    "sync": "#2c89b9",
    "offline": "#77838c",
    "warning": "#e39a25",
    "info": "#2c89b9",
}


def ensure_sources() -> None:
    for source in (SYMBOL_SVG, WORDMARK_SVG):
        if not source.is_file():
            raise SystemExit(f"Missing source asset: {source}")


def svg_dimensions(path: Path) -> tuple[float, float]:
    root = ElementTree.fromstring(path.read_bytes())
    view_box = root.attrib.get("viewBox")
    if not view_box:
        raise ValueError(f"{path} has no viewBox")
    _, _, width, height = (float(value) for value in view_box.split())
    return width, height


def trimmed_svg(path: Path, maximum_axis: int = 2048) -> Image.Image:
    width, height = svg_dimensions(path)
    scale = maximum_axis / max(width, height)
    png = cairosvg.svg2png(
        bytestring=path.read_bytes(),
        output_width=max(1, round(width * scale)),
        output_height=max(1, round(height * scale)),
    )
    image = Image.open(io.BytesIO(png)).convert("RGBA")
    bounds = image.getchannel("A").getbbox()
    if bounds is None:
        raise ValueError(f"{path} rendered empty")
    return image.crop(bounds)


def fit(image: Image.Image, width: int, height: int, padding: float = 0.1) -> Image.Image:
    available_width = max(1, round(width * (1 - 2 * padding)))
    available_height = max(1, round(height * (1 - 2 * padding)))
    scale = min(available_width / image.width, available_height / image.height)
    resized = image.resize(
        (max(1, round(image.width * scale)), max(1, round(image.height * scale))),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    canvas.alpha_composite(resized, ((width - resized.width) // 2, (height - resized.height) // 2))
    return canvas


def save_png(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", compress_level=9, optimize=False)


def save_icns(image: Image.Image, path: Path) -> None:
    """Write modern PNG-backed ICNS entries, including 16 px and Retina peers."""
    entries = (
        (b"icp4", 16),
        (b"icp5", 32),
        (b"icp6", 64),
        (b"ic07", 128),
        (b"ic08", 256),
        (b"ic09", 512),
        (b"ic10", 1024),
        (b"ic11", 32),
        (b"ic12", 64),
        (b"ic13", 256),
        (b"ic14", 512),
    )
    chunks: list[bytes] = []
    for kind, size in entries:
        buffer = io.BytesIO()
        image.resize((size, size), Image.Resampling.LANCZOS).save(
            buffer,
            format="PNG",
            compress_level=9,
            optimize=False,
        )
        payload = buffer.getvalue()
        chunks.append(kind + struct.pack(">I", 8 + len(payload)) + payload)
    body = b"".join(chunks)
    path.write_bytes(b"icns" + struct.pack(">I", 8 + len(body)) + body)


def recolor(image: Image.Image, rgb: tuple[int, int, int]) -> Image.Image:
    result = Image.new("RGBA", image.size, (*rgb, 0))
    result.putalpha(image.getchannel("A"))
    return result


def draw_status_mark(draw: ImageDraw.ImageDraw, state: str, box: tuple[int, int, int, int], color: str) -> None:
    left, top, right, bottom = box
    size = right - left
    width = max(1, round(size * 0.12))
    ink = "white" if color != "#ffffff" else "black"
    cx, cy = (left + right) // 2, (top + bottom) // 2
    if state == "ok":
        draw.line(
            [(left + size * 0.23, cy), (left + size * 0.43, top + size * 0.70), (left + size * 0.78, top + size * 0.30)],
            fill=ink,
            width=width,
            joint="curve",
        )
    elif state == "error":
        draw.line([(left + size * 0.3, top + size * 0.3), (right - size * 0.3, bottom - size * 0.3)], fill=ink, width=width)
        draw.line([(right - size * 0.3, top + size * 0.3), (left + size * 0.3, bottom - size * 0.3)], fill=ink, width=width)
    elif state == "pause":
        draw.rounded_rectangle((left + size * 0.28, top + size * 0.25, left + size * 0.43, bottom - size * 0.25), radius=width, fill=ink)
        draw.rounded_rectangle((right - size * 0.43, top + size * 0.25, right - size * 0.28, bottom - size * 0.25), radius=width, fill=ink)
    elif state == "sync":
        draw.arc((left + size * 0.2, top + size * 0.2, right - size * 0.2, bottom - size * 0.2), 25, 190, fill=ink, width=width)
        draw.arc((left + size * 0.2, top + size * 0.2, right - size * 0.2, bottom - size * 0.2), 205, 370, fill=ink, width=width)
        draw.polygon([(right - size * 0.12, cy), (right - size * 0.34, top + size * 0.35), (right - size * 0.36, top + size * 0.62)], fill=ink)
        draw.polygon([(left + size * 0.12, cy), (left + size * 0.34, bottom - size * 0.35), (left + size * 0.36, bottom - size * 0.62)], fill=ink)
    elif state == "offline":
        draw.line([(left + size * 0.25, bottom - size * 0.25), (right - size * 0.25, top + size * 0.25)], fill=ink, width=width)
    elif state == "warning":
        draw.line([(cx, top + size * 0.25), (cx, top + size * 0.62)], fill=ink, width=width)
        draw.ellipse((cx - width / 2, bottom - size * 0.28, cx + width / 2, bottom - size * 0.18), fill=ink)
    else:
        draw.ellipse((cx - width / 2, top + size * 0.22, cx + width / 2, top + size * 0.32), fill=ink)
        draw.line([(cx, top + size * 0.42), (cx, bottom - size * 0.22)], fill=ink, width=width)


def status_icon(base: Image.Image, size: int, state: str, flavor: str) -> Image.Image:
    icon = fit(base, size, size, 0.08)
    if flavor == "black":
        icon = recolor(icon, (0, 0, 0))
        color = "#000000"
        outline = "#ffffff"
    elif flavor == "white":
        icon = recolor(icon, (255, 255, 255))
        color = "#ffffff"
        outline = "#000000"
    else:
        color = STATE_COLORS[state]
        outline = "#ffffff"

    draw = ImageDraw.Draw(icon)
    diameter = max(7, round(size * 0.46))
    right = size - max(0, round(size * 0.02))
    bottom = right
    box = (right - diameter, bottom - diameter, right, bottom)
    outline_width = max(1, round(size * 0.035))
    draw.ellipse(box, fill=color, outline=outline, width=outline_width)
    draw_status_mark(draw, state, box, color)
    return icon


def embedded_png_svg(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", compress_level=9, optimize=False)
    payload = base64.b64encode(buffer.getvalue()).decode("ascii")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">\n'
        f'  <image width="256" height="256" href="data:image/png;base64,{payload}"/>\n'
        "</svg>\n"
    )


def monochrome_svg(source: Path, color: str) -> str:
    text = source.read_text(encoding="utf-8")
    marker = text.find(">")
    style = f'<style>svg * {{ fill: {color} !important; stroke: {color} !important; }}</style>'
    return text[: marker + 1] + style + text[marker + 1 :]


def make_background(width: int, height: int, wordmark: Image.Image, scale: float) -> Image.Image:
    image = Image.new("RGB", (width, height), "#f4f9fc")
    draw = ImageDraw.Draw(image)
    for y in range(height):
        ratio = y / max(1, height - 1)
        red = round(244 + (226 - 244) * ratio)
        green = round(249 + (242 - 249) * ratio)
        blue = round(252 + (248 - 252) * ratio)
        draw.line((0, y, width, y), fill=(red, green, blue))
    fitted = fit(wordmark, round(width * scale), round(height * 0.45), 0.03)
    image.paste(fitted, ((width - fitted.width) // 2, round(height * 0.08)), fitted)
    # A simple arrow remains font-independent and therefore reproducible.
    cx = width // 2
    y = round(height * 0.70)
    draw.line((cx - width * 0.12, y, cx + width * 0.08, y), fill="#2c89b9", width=max(2, width // 120))
    draw.polygon(
        [(cx + width * 0.08, y - height * 0.04), (cx + width * 0.16, y), (cx + width * 0.08, y + height * 0.04)],
        fill="#2c89b9",
    )
    return image


def main() -> None:
    ensure_sources()
    GENERATED.mkdir(parents=True, exist_ok=True)

    symbol = trimmed_svg(SYMBOL_SVG)
    wordmark = trimmed_svg(WORDMARK_SVG)
    app_master = fit(symbol, 1024, 1024, 0.09)

    colored = ROOT / "theme" / "colored"
    icons = colored / "icons"
    shutil.copyfile(SYMBOL_SVG, colored / "SeaByte-icon.svg")
    shutil.copyfile(SYMBOL_SVG, colored / "SeaByte-w10startmenu.svg")
    shutil.copyfile(SYMBOL_SVG, icons / "SeaByte-icon-win-folder.svg")
    (colored / "SeaByte-sidebar.svg").write_text(monochrome_svg(SYMBOL_SVG, "#000000"), encoding="utf-8")
    shutil.copyfile(WORDMARK_SVG, colored / "wizard_logo.svg")

    for size in APP_SIZES:
        padding = 0.04 if size <= 24 else 0.09
        save_png(fit(symbol, size, size, padding), colored / f"{size}-SeaByte-icon.png")

    save_png(fit(wordmark, 320, 120, 0.03), colored / "wizard_logo.png")
    save_png(fit(wordmark, 640, 240, 0.03), colored / "wizard_logo@2x.png")
    save_png(fit(symbol, 150, 150, 0.08), colored / "150-SeaByte-w10startmenu.png")
    save_png(fit(symbol, 70, 70, 0.08), colored / "70-SeaByte-w10startmenu.png")

    for flavor in ("colored", "black", "white"):
        output_dir = ROOT / "theme" / flavor / "seabyte"
        for state in STATES:
            large = status_icon(symbol, 256, state, flavor)
            (output_dir / f"state-{state}.svg").parent.mkdir(parents=True, exist_ok=True)
            (output_dir / f"state-{state}.svg").write_text(embedded_png_svg(large), encoding="utf-8")
            for size in STATUS_SIZES:
                save_png(status_icon(symbol, size, state, flavor), output_dir / f"state-{state}-{size}.png")

    app_master.save(GENERATED / "SeaByteCloud.ico", format="ICO", sizes=[(size, size) for size in ICO_SIZES])
    save_icns(app_master, GENERATED / "SeaByteCloud.icns")
    shutil.copyfile(GENERATED / "SeaByteCloud.ico", ROOT / "admin" / "win" / "nsi" / "installer.ico")

    template_dir = GENERATED / "macos-template"
    for size in (16, 18, 32, 36):
        template = recolor(fit(symbol, size, size, 0.08), (0, 0, 0))
        save_png(template, template_dir / f"SeaByteTemplate-{size}.png")

    overlay_dir = GENERATED / "windows-overlays"
    overlay_dir.mkdir(parents=True, exist_ok=True)
    for state in STATES:
        overlay = status_icon(symbol, 256, state, "colored")
        overlay.save(overlay_dir / f"SeaByte-{state}.ico", format="ICO", sizes=[(size, size) for size in ICO_SIZES])

    save_png(fit(symbol, 512, 512, 0.08), GENERATED / "macos-file-provider.png")
    save_png(fit(symbol, 512, 512, 0.08), GENERATED / "macos-finder-extension.png")

    banner = make_background(493, 58, wordmark, 0.38)
    banner.save(ROOT / "admin" / "win" / "msi" / "gui" / "banner.bmp", format="BMP")
    dialog = make_background(493, 314, wordmark, 0.68)
    dialog.save(ROOT / "admin" / "win" / "msi" / "gui" / "dialog.bmp", format="BMP")
    make_background(150, 57, wordmark, 0.90).save(ROOT / "admin" / "win" / "nsi" / "page_header.bmp", format="BMP")
    make_background(164, 314, wordmark, 0.92).save(ROOT / "admin" / "win" / "nsi" / "welcome.bmp", format="BMP")

    save_png(make_background(501, 351, wordmark, 0.72), ROOT / "admin" / "osx" / "DMGBackground.png")
    save_png(make_background(320, 200, wordmark, 0.78), ROOT / "admin" / "osx" / "installer-background.png")
    save_png(make_background(640, 400, wordmark, 0.78), ROOT / "admin" / "osx" / "installer-background_2x.png")

    print(f"Generated SeaByte assets in {ROOT}")


if __name__ == "__main__":
    main()
