#!/usr/bin/env python3
"""Extract raster images from a DOCX for explicit visual inspection.

The script deliberately does not guess which image is a portrait. It writes all
image candidates plus a JSON manifest so the agent can inspect and select the
correct photo instead of silently using a logo or decorative asset.
"""

import argparse
import io
import json
from pathlib import Path
from zipfile import ZipFile

from PIL import Image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_docx", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    records = []
    with ZipFile(args.input_docx) as archive:
        for member in sorted(archive.namelist()):
            if not member.startswith("word/media/"):
                continue
            data = archive.read(member)
            try:
                image = Image.open(io.BytesIO(data))
                image.load()
            except Exception:
                continue
            suffix = (image.format or "png").lower().replace("jpeg", "jpg")
            output = args.output_dir / f"candidate-{len(records) + 1}.{suffix}"
            output.write_bytes(data)
            records.append(
                {
                    "source": member,
                    "output": output.name,
                    "width": image.width,
                    "height": image.height,
                    "format": image.format,
                }
            )

    manifest = args.output_dir / "manifest.json"
    manifest.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(manifest)


if __name__ == "__main__":
    main()
