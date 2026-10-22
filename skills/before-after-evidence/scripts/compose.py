"""Compose a before/after comparison image from two folders of step screenshots.

Usage:
  python3 -I compose.py --before DIR --after DIR --steps step06 step07 --out out.png
"""

import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

COLUMN_WIDTH = 360
GAP = 16
LABEL_HEIGHT = 60
FONT_CANDIDATES = [
    '/System/Library/Fonts/Helvetica.ttc',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    'C:\\Windows\\Fonts\\arial.ttf',
]


def load_font(size: int) -> ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def load_row(folder: str, steps: list[str]) -> list[Image.Image]:
    images = []
    for step in steps:
        path = os.path.join(folder, step if step.endswith('.png') else f'{step}.png')
        if not os.path.exists(path):
            sys.exit(f'missing screenshot: {path}')
        image = Image.open(path).convert('RGB')
        height = int(image.height * COLUMN_WIDTH / image.width)
        images.append(image.resize((COLUMN_WIDTH, height)))
    return images


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--before', required=True)
    parser.add_argument('--after', required=True)
    parser.add_argument('--steps', nargs='+', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()

    rows = [('Before', load_row(args.before, args.steps)), ('After', load_row(args.after, args.steps))]
    row_height = max(image.height for _, images in rows for image in images)
    columns = len(args.steps)

    canvas = Image.new(
        'RGB',
        (columns * COLUMN_WIDTH + (columns + 1) * GAP, 2 * (row_height + LABEL_HEIGHT) + 3 * GAP),
        'white',
    )
    draw = ImageDraw.Draw(canvas)
    font = load_font(34)

    for row_index, (label, images) in enumerate(rows):
        top = GAP + row_index * (row_height + LABEL_HEIGHT + GAP)
        draw.text((GAP, top + 10), label, fill='black', font=font)
        for column, image in enumerate(images):
            canvas.paste(image, (GAP + column * (COLUMN_WIDTH + GAP), top + LABEL_HEIGHT))

    canvas.save(args.out)
    print(args.out)


if __name__ == '__main__':
    main()
