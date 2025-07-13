from PIL import Image, ImageDraw, ImageFont
from typing import Iterable, Tuple, List

BBox = Tuple[int, int, int, int]

def draw_boxes(
    image: Image.Image,
    boxes: Iterable[BBox],
    label: str = "object",
    color: str = "red",
    width: int = 3,
    font_path: str = "content/times.ttf",
    font_size: int = 16
) -> Image.Image:
    im = image.copy().convert("RGBA")
    draw = ImageDraw.Draw(im, "RGBA")
    font = ImageFont.truetype(font_path, font_size)

    for (x1, y1, x2, y2) in boxes:
        draw.rectangle([x1, y1, x2, y2], outline=color, width=width)
        draw.text((x1 + 4, y1 + 4), label, fill=color, font=font)
    return im
