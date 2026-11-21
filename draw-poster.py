#!/usr/bin/env python3
"""Draw the travel poster for VELMARA, a place that isn't there.

Velmara is a cliff-top garden city floating above a sea of clouds at
sunset. Its one landmark is the Lantern Tower: a slender stone tower
wearing a glowing golden ring, the light every traveller steers by.

Drawn programmatically with PIL only: flat vintage-poster shapes, a
sunset gradient sky, a soft cloud sea, a dark cliff silhouette with a
tiny lit town, and the place name set in large type. No external images.
Deterministic: the same run always writes the same bytes.

Run: python3 draw-poster.py   (writes entry.png beside this file)
"""
import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SIZE = 1024
OUTFILE = "entry.png"

# ---- palette: a warm sunset over a cloud sea ----
INDIGO = (28, 32, 66)
VIOLET = (96, 62, 110)
CORAL = (224, 112, 63)
GOLD = (246, 183, 60)
CREAM = (247, 234, 215)
PINK = (238, 178, 158)
LILAC = (178, 148, 190)
CLIFF = (38, 30, 58)
CLIFF2 = (52, 40, 74)
WINDOW = (255, 196, 92)
RING = (255, 214, 120)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def sky_gradient(img):
    """Vertical sunset gradient, indigo at top to gold at the horizon."""
    stops = [(0.0, INDIGO), (0.30, VIOLET), (0.52, CORAL), (0.68, GOLD),
             (1.0, GOLD)]
    d = ImageDraw.Draw(img)
    for y in range(720):
        t = y / 720.0
        for i in range(len(stops) - 1):
            if stops[i][0] <= t <= stops[i + 1][0]:
                f = (t - stops[i][0]) / (stops[i + 1][0] - stops[i][0])
                d.line([(0, y), (SIZE, y)], fill=lerp(stops[i][1], stops[i + 1][1], f))
                break


def soft_layer(draw_fn, blur=18):
    """Draw shapes on a transparent layer, blur it, return the layer."""
    layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_fn(d)
    return layer.filter(ImageFilter.GaussianBlur(blur))


def cloud_sea(img):
    """The sea of clouds below the horizon: soft overlapping puffs."""
    rnd = random.Random(20261121)
    # warm haze hugging the horizon so sky melts into cloud, no hard line
    haze = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    for y in range(600, 720):
        t = (y - 600) / 120.0
        c = lerp((246, 183, 60), (247, 234, 215), t)
        hd.line([(0, y), (SIZE, y)], fill=c + (int(150 * (1 - t)) + 30,))
    img.alpha_composite(haze.filter(ImageFilter.GaussianBlur(8)))

    def puffs(d):
        for _ in range(130):
            x = rnd.uniform(-80, SIZE + 80)
            y = rnd.uniform(660, 1010)
            rx = rnd.uniform(60, 190)
            ry = rnd.uniform(18, 55)
            c = rnd.choice([CREAM, (250, 220, 190), PINK, (255, 226, 180)])
            a = rnd.randint(140, 210)
            d.ellipse([x - rx, y - ry, x + rx, y + ry], fill=c + (a,))

    img.alpha_composite(soft_layer(puffs, 12))
    # a calm band of cloud right under the horizon, catching the light
    band = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    for i in range(26):
        x = -60 + i * 44
        bd.ellipse([x, 648, x + 150, 700], fill=CREAM + (170,))
    img.alpha_composite(band.filter(ImageFilter.GaussianBlur(10)))


def sun(img):
    """Low sun disc with a halo, sitting just above the cloud sea."""
    cx, cy, r = 430, 545, 85

    def glow(d):
        d.ellipse([cx - r - 70, cy - r - 70, cx + r + 70, cy + r + 70],
                  fill=(255, 214, 130, 70))
        d.ellipse([cx - r - 30, cy - r - 30, cx + r + 30, cy + r + 30],
                  fill=(255, 226, 160, 110))

    img.alpha_composite(soft_layer(glow, 22))
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 238, 196))
    d.ellipse([cx - r + 14, cy - r + 14, cx + r - 14, cy + r - 14],
              fill=(255, 246, 220))


def stars(d):
    rnd = random.Random(7)
    for _ in range(70):
        x = rnd.uniform(20, SIZE - 20)
        y = rnd.uniform(40, 300)
        s = rnd.uniform(1.0, 2.6)
        a = rnd.randint(90, 200)
        d.ellipse([x - s, y - s, x + s, y + s], fill=(255, 240, 210, a))


def birds(d):
    for (x, y, s) in [(150, 360, 16), (215, 340, 12), (285, 370, 14),
                      (560, 250, 13), (610, 292, 11)]:
        d.arc([x - s, y - s, x, y + s], 200, 340, fill=CLIFF, width=3)
        d.arc([x, y - s, x + s, y + s], 200, 340, fill=CLIFF, width=3)


def cliff_and_town(d):
    """The cliff on the right, its little town, and the Lantern Tower."""
    # main cliff mass, rising out of the cloud sea
    cliff = [(560, 1024), (600, 760), (640, 640), (700, 560), (780, 520),
             (860, 500), (930, 520), (990, 600), (1024, 660), (1024, 1024)]
    d.polygon(cliff, fill=CLIFF)
    # a second, nearer ridge at the bottom left for depth
    d.polygon([(0, 1024), (0, 900), (120, 830), (260, 880), (330, 960),
               (300, 1024)], fill=CLIFF2)
    # cliff rim highlight where the sunset catches it
    d.line([(600, 760), (640, 640), (700, 560), (780, 520), (860, 500),
            (930, 520), (990, 600)], fill=(214, 128, 84), width=5)
    # tiny town: houses with lit windows along the cliff top
    rnd = random.Random(42)
    for _ in range(26):
        x = rnd.uniform(640, 1000)
        y = rnd.uniform(505, 545) - (x - 640) * 0.02
        w, h = rnd.uniform(14, 26), rnd.uniform(12, 22)
        d.rectangle([x, y - h, x + w, y], fill=(30, 24, 48))
        d.polygon([(x, y - h), (x + w / 2, y - h - 8), (x + w, y - h)],
                  fill=(24, 19, 40))
        if rnd.random() < 0.8:
            d.rectangle([x + w * 0.3, y - h * 0.65, x + w * 0.6, y - h * 0.3],
                        fill=WINDOW)
    # the Lantern Tower: slender stone tower with a glowing ring
    tx = 835
    d.polygon([(tx - 16, 505), (tx - 9, 300), (tx + 9, 300), (tx + 16, 505)],
              fill=(46, 36, 68))
    d.rectangle([tx - 20, 292, tx + 20, 306], fill=(46, 36, 68))
    d.polygon([(tx - 20, 292), (tx, 268), (tx + 20, 292)], fill=(36, 28, 56))
    for wy in (320, 350, 380, 410, 440, 470):
        d.rectangle([tx - 4, wy, tx + 4, wy + 12], fill=WINDOW)
    # the ring: a glowing halo the tower wears
    d.ellipse([tx - 58, 250, tx + 58, 306], outline=RING, width=7)
    d.ellipse([tx - 58, 250, tx + 58, 306], outline=(255, 240, 190), width=2)
    # beacon light at the tower top
    d.ellipse([tx - 7, 258, tx + 7, 272], fill=(255, 246, 220))


def tracked_text(d, xy, text, font, fill, spacing=10):
    """Draw text with letter spacing, centred on xy."""
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = xy[0] - total / 2
    for ch, w in zip(text, widths):
        d.text((x, xy[1]), ch, font=font, fill=fill)
        x += w + spacing


def poster_type(d):
    """The place name, set big and legible, with a subtitle and tagline."""
    title = ImageFont.truetype(SERIF_B, 118)
    sub = ImageFont.truetype(SANS_B, 34)
    tag = ImageFont.truetype(SANS, 25)
    # soft shadow under the title so it reads over the sky
    tracked_text(d, (514, 100), "VELMARA", title, (20, 18, 44, 160), spacing=14)
    tracked_text(d, (510, 96), "VELMARA", title, CREAM, spacing=14)
    # rule + subtitle
    d.line([(342, 268), (682, 268)], fill=GOLD, width=3)
    tracked_text(d, (512, 292), "ABOVE THE SEA OF CLOUDS", sub, GOLD, spacing=8)
    # tagline low over the cloud sea
    tracked_text(d, (512, 928), "WHERE THE SKY COMES TO STAY",
                 tag, (247, 234, 215), spacing=6)


def frame(d):
    d.rectangle([26, 26, SIZE - 27, SIZE - 27], outline=CREAM, width=4)
    d.rectangle([38, 38, SIZE - 39, SIZE - 39], outline=(247, 234, 215, 140),
                width=1)


def main():
    img = Image.new("RGB", (SIZE, SIZE), INDIGO)
    sky_gradient(img)
    img = img.convert("RGBA")
    stars(ImageDraw.Draw(img))
    sun(img)
    birds(ImageDraw.Draw(img))
    cloud_sea(img)
    cliff_and_town(ImageDraw.Draw(img))
    poster_type(ImageDraw.Draw(img))
    frame(ImageDraw.Draw(img))
    img = img.convert("RGB")
    img.save(OUTFILE, "PNG", optimize=True)
    import os
    print("wrote %s (%d bytes)" % (OUTFILE, os.path.getsize(OUTFILE)))


if __name__ == "__main__":
    main()
