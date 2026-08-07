#!/usr/bin/env python3
"""Replace the invalid quantitative Panel C with a nonquantitative design-aware panel."""

import io
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[3]
SOURCE = REPO / "Manuskrip" / "COPD_ACS_Two_Clock_Model_Review (Hendri Susilo).docx"
OUTPUT = REPO / "research" / "stage-1" / "assets" / "central-illustration-stage1.png"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def centered(draw, box, text, font, fill=(20, 28, 30)):
    left, top, right, bottom = box
    bounds = draw.multiline_textbbox((0, 0), text, font=font, align="center", spacing=2)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    draw.multiline_text(
        (left + (right - left - width) / 2, top + (bottom - top - height) / 2),
        text,
        font=font,
        fill=fill,
        align="center",
        spacing=2,
    )


def main():
    missing_fonts = [path for path in (FONT, BOLD) if not Path(path).is_file()]
    if missing_fonts:
        raise RuntimeError("Required DejaVu font files are missing: " + ", ".join(missing_fonts))
    with zipfile.ZipFile(SOURCE) as archive:
        source_image = archive.read("word/media/image1.png")
    image = Image.open(io.BytesIO(source_image)).convert("RGB")
    if image.size != (1024, 559):
        raise RuntimeError(f"Unexpected central illustration size: {image.size}")
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.truetype(BOLD, 14)
    lane_font = ImageFont.truetype(BOLD, 11)
    body_font = ImageFont.truetype(FONT, 10)
    note_font = ImageFont.truetype(BOLD, 10)
    panel_font = ImageFont.truetype(BOLD, 18)

    draw.rectangle((0, 284, 511, 526), fill=(235, 244, 244))
    draw.line((511, 284, 511, 526), fill=(205, 216, 216), width=2)
    draw.text((6, 288), "C", font=panel_font, fill=(15, 20, 22))
    centered(
        draw,
        (30, 287, 505, 328),
        "Evidence streams answer different questions\nand use different scales",
        title_font,
    )

    lanes = [
        ((11, 330, 166, 474), (215, 235, 239), "OBSERVATIONAL", "Patients with versus\nwithout COPD\n\nConfounding and\nselection remain"),
        ((178, 330, 337, 474), (228, 234, 222), "GENETIC ANALYSES", "COPD liability, FEV₁,\nFVC and FEV₁/FVC\n\nDifferent instruments\nand units"),
        ((349, 330, 500, 474), (242, 224, 222), "ACUTE TRIGGER", "Within-person risk after\nan exacerbation\n\nDefined by the acute\nrisk window"),
    ]
    for box, colour, heading, body in lanes:
        draw.rounded_rectangle(box, radius=9, fill=colour, outline=(90, 115, 118), width=1)
        left, top, right, bottom = box
        centered(draw, (left + 4, top + 5, right - 4, top + 28), heading, lane_font)
        centered(draw, (left + 6, top + 30, right - 6, bottom - 5), body, body_font)

    centered(
        draw,
        (8, 477, 503, 524),
        "Compare direction and precision within each lane.\nMagnitudes are not on a common axis.",
        note_font,
        fill=(24, 77, 80),
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, format="PNG", optimize=False, compress_level=9)
    print(OUTPUT)


if __name__ == "__main__":
    main()
