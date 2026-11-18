"""gen_image.py - build-time generator for the "ONE PLANET, ONE DAY" news image.

Deterministic: fixed seed, no timestamps, Pillow primitives only. Writes entry.png.
"""

import math
import random

from PIL import Image, ImageChops, ImageDraw, ImageFont

W = 1024
H = 1024

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

_font_cache = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)
    return _font_cache[key]


def tw(draw, text, fnt):
    """Rendered width of a text string."""
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0]


def th(draw, text, fnt):
    """Rendered height of a text string."""
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[3] - bbox[1]


RNG = random.Random(20261117)

GOLD = (201, 162, 76)
CARD_FILL = (26, 47, 92)
WHITE = (245, 248, 255)
GREY = (186, 198, 220)


def gradient_bg():
    """Deep-navy vertical gradient, top #0A1633 to bottom #13264F."""
    img = Image.new("RGB", (W, H))
    top = (0x0A, 0x16, 0x33)
    bot = (0x13, 0x26, 0x4F)
    px = img.load()
    for y in range(H):
        t = y / (H - 1.0)
        row = (
            int(top[0] + (bot[0] - top[0]) * t),
            int(top[1] + (bot[1] - top[1]) * t),
            int(top[2] + (bot[2] - top[2]) * t),
        )
        for x in range(W):
            px[x, y] = row
    return img


def add_stars(draw):
    """Faint deterministic stars, kept clear of the central globe area."""
    for _ in range(230):
        x = RNG.randrange(0, W)
        y = RNG.randrange(0, H)
        if (x - 512) ** 2 + (y - 430) ** 2 > 200 ** 2:
            s = RNG.choice((1, 1, 1, 2))
            v = RNG.randrange(150, 235)
            draw.ellipse([x, y, x + s, y + s], fill=(v, v, min(255, v + 18)))


def draw_masthead(draw):
    """Title, gold subtitle, gold rule line."""
    title = "TUESDAY 17 NOVEMBER 2026"
    fnt = font(44, bold=True)
    draw.text(((W - tw(draw, title, fnt)) / 2, 26), title, font=fnt, fill=WHITE)
    sub = "THE WORLD IN ONE DAY"
    fnt2 = font(26, bold=True)
    ls = 4
    total = sum(tw(draw, ch, fnt2) for ch in sub) + ls * (len(sub) - 1)
    x = (W - total) / 2
    y = 84
    for ch in sub:
        draw.text((x, y), ch, font=fnt2, fill=GOLD)
        x += tw(draw, ch, fnt2) + ls
    draw.line([(150, 134), (W - 150, 134)], fill=GOLD, width=3)


def _blob(g, cx, cy, rx, ry, phase, fill):
    """Abstract continent blob via modulated polar outline."""
    pts = []
    steps = 26
    for i in range(steps):
        t = 2 * math.pi * i / steps
        m = 1.0 + 0.28 * math.sin(3 * t + phase) + 0.16 * math.cos(5 * t + 2 * phase)
        pts.append((cx + rx * m * math.cos(t), cy + ry * m * math.sin(t)))
    g.polygon(pts, fill=fill)


def draw_globe(img, draw):
    """Navy globe with lighter rim, grid ellipses, abstract continents."""
    cx, cy, r = 512, 430, 165
    globe = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(globe)
    g.ellipse([cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4], fill=(88, 118, 168))
    g.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(11, 26, 56))
    # latitude ellipses (orthographic-style, tilted view)
    for lat in (-55, -28, 0, 28, 55):
        a = math.radians(lat)
        hx = r * math.cos(a)
        hy = hx * 0.35
        yy = cy - r * math.sin(a)
        g.ellipse([cx - hx, yy - hy, cx + hx, yy + hy], outline=(58, 80, 124), width=1)
    # longitude ellipses
    for dlon in (-70, -35, 0, 35, 70):
        a = math.radians(dlon)
        hx = r * math.sin(a)
        if hx < 2:
            g.line([(cx, cy - r), (cx, cy + r)], fill=(58, 80, 124), width=1)
        else:
            g.ellipse([cx - hx, cy - r, cx + hx, cy + r], outline=(58, 80, 124), width=1)
    # abstract continent blobs (not geographically precise, unlabeled)
    land = (50, 118, 104)
    _blob(g, cx + 0.20 * r, cy - 0.30 * r, 0.44 * r, 0.22 * r, 1.0, land)
    _blob(g, cx - 0.40 * r, cy + 0.12 * r, 0.26 * r, 0.36 * r, 2.2, land)
    _blob(g, cx + 0.04 * r, cy + 0.32 * r, 0.24 * r, 0.28 * r, 0.4, land)
    _blob(g, cx + 0.44 * r, cy + 0.44 * r, 0.16 * r, 0.11 * r, 4.0, land)
    _blob(g, cx + 0.36 * r, cy - 0.02 * r, 0.13 * r, 0.09 * r, 2.8, land)
    # circular mask keeps the globe a clean disc (radius r+4 keeps the rim ring)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).ellipse([cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4], fill=255)
    globe.putalpha(ImageChops.multiply(globe.getchannel("A"), mask))
    img.paste(globe, (0, 0), globe)
    # small gold caption under the globe
    cap = "ONE PLANET, ONE DAY"
    fnt = font(24, bold=True)
    draw.text((cx - tw(draw, cap, fnt) / 2, cy + r + 16), cap, font=fnt, fill=GOLD)


# ---- piece 3: cards + arcs ----
def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for wd in text.split():
        trial = (cur + " " + wd).strip()
        if tw(draw, trial, fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def icon_bridge(d, bx, by, bw, bh):
    wy = by + bh - 4
    cx = bx + bw // 2
    d.line([(bx, wy), (bx + bw, wy)], fill=(66, 118, 158), width=2)
    d.rectangle([bx + 4, wy - 18, bx + 18, wy - 11], fill=(168, 178, 194))
    d.rectangle([bx + bw - 18, wy - 18, bx + bw - 4, wy - 11], fill=(168, 178, 194))
    d.rectangle([cx - 6, wy - 13, cx + 6, wy - 9], fill=(120, 130, 146))
    cy = wy - 16
    for a in range(0, 360, 45):
        d.line([(cx, cy), (cx + 8 * math.cos(math.radians(a)), cy + 8 * math.sin(math.radians(a)))], fill=(240, 150, 50), width=2)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 200, 60))


def icon_plane(d, bx, by, bw, bh):
    gy = by + bh - 2
    for i, px in enumerate((bx + 12, bx + bw // 2, bx + bw - 16)):
        d.line([(px, gy), (px, gy - 14)], fill=(150, 160, 175), width=2)
        d.polygon([(px, gy - 14), (px + 12, gy - 11), (px, gy - 8)], fill=(90, 140, 200) if i != 1 else GOLD)
    cx, cy = bx + bw // 2, by + 7
    d.ellipse([cx - 15, cy - 3, cx + 15, cy + 3], fill=(222, 228, 240))
    d.polygon([(cx - 15, cy - 1), (cx - 28, cy - 2), (cx - 22, cy + 3)], fill=(222, 228, 240))
    d.polygon([(cx + 2, cy - 2), (cx + 9, cy - 8), (cx + 14, cy - 2)], fill=(196, 205, 220))
    d.polygon([(cx + 2, cy + 2), (cx + 9, cy + 8), (cx + 14, cy + 2)], fill=(196, 205, 220))


def icon_tanker(d, bx, by, bw, bh):
    wy = by + bh - 3
    d.line([(bx, wy), (bx + bw, wy)], fill=(66, 118, 158), width=2)
    d.polygon([(bx + 8, wy), (bx + 8, wy - 12), (bx + bw - 8, wy - 13), (bx + bw - 8, wy)], fill=(140, 152, 170))
    d.rectangle([bx + bw - 30, wy - 24, bx + bw - 14, wy - 13], fill=(162, 172, 188))
    fx = bx + bw // 2
    d.polygon([(fx - 5, wy - 13), (fx + 1, wy - 27), (fx + 7, wy - 13)], fill=(245, 160, 40))
    for i, sy in enumerate((wy - 16, wy - 22)):
        px = fx + 12 + i * 9
        d.ellipse([px - 5, sy - 4, px + 5, sy + 4], fill=(150, 155, 165))


def icon_rocket(d, bx, by, bw, bh):
    cx = bx + bw // 2
    d.polygon([(cx - 7, by + 4), (cx + 7, by + 4), (cx + 5, by + 16), (cx - 5, by + 16)], fill=(215, 222, 235))
    d.polygon([(cx - 6, by), (cx + 6, by), (cx, by + 6)], fill=(230, 90, 60))
    d.polygon([(cx - 5, by + 20), (cx + 5, by + 22), (cx + 13, by + 32), (cx + 5, by + 32)], fill=(190, 200, 215))
    d.ellipse([cx + 15, by + 12, cx + 19, by + 16], fill=(210, 215, 225))
    d.ellipse([cx - 22, by + 22, cx - 18, by + 26], fill=(210, 215, 225))
    sx, sy = cx + 20, by + 24
    d.rectangle([sx - 4, sy - 5, sx + 4, sy + 5], fill=(200, 208, 222))
    for o in (-1, 1):
        d.line([(sx, sy + o * 5), (sx - 12, sy + o * 5)], fill=(200, 208, 222), width=2)
    d.line([(sx - 12, sy - 5), (sx - 12, sy + 5)], fill=(200, 208, 222), width=2)


def icon_bank(d, bx, by, bw, bh):
    wy = by + bh - 3
    d.line([(bx + 4, wy), (bx + bw - 4, wy)], fill=(150, 160, 175), width=3)
    for px in (bx + 16, bx + 38, bx + bw - 38, bx + bw - 16):
        d.rectangle([px - 3, wy - 20, px + 3, wy - 4], fill=(168, 178, 194))
    d.polygon([(bx + 6, wy - 20), (bx + bw - 6, wy - 20), (bx + bw // 2, wy - 28)], fill=(168, 178, 194))
    tx, ty = bx + bw - 24, by + 6
    d.polygon([(tx - 7, ty + 11), (tx + 7, ty + 11), (tx, ty - 7)], outline=(245, 175, 50), width=2)
    d.line([(tx, ty - 1), (tx, ty + 6)], fill=(245, 175, 50), width=2)
    d.ellipse([tx - 1.5, ty + 8, tx + 1.5, ty + 11], fill=(245, 175, 50))


def icon_jets(d, bx, by, bw, bh):
    for k in (0, 1):
        cx = bx + bw // 2 + (8 if k else -8)
        cy = by + 10 + k * 20
        d.ellipse([cx - 18, cy - 2, cx + 12, cy + 2], fill=(205, 214, 230))
        d.polygon([(cx + 12, cy), (cx + 20, cy), (cx + 16, cy + 3)], fill=(205, 214, 230))
        d.polygon([(cx - 2, cy - 1), (cx + 6, cy - 8), (cx + 10, cy - 1)], fill=(185, 196, 214))
        d.polygon([(cx - 2, cy + 1), (cx + 6, cy + 8), (cx + 10, cy + 1)], fill=(185, 196, 214))


def dashed_bezier(d, p0, ctrl, p2, width=2):
    pts = []
    for i in range(41):
        t = i / 40.0
        mt = 1.0 - t
        pts.append((mt * mt * p0[0] + 2 * mt * t * ctrl[0] + t * t * p2[0],
                    mt * mt * p0[1] + 2 * mt * t * ctrl[1] + t * t * p2[1]))
    i = 0
    n = len(pts)
    while i < n - 1:
        j = min(i + 5, n - 1)
        d.line([pts[i], pts[j]], fill=GOLD, width=width)
        i = j + 3


CW, CH = 300, 172
CW_LEAD = 310
ROWS = (250, 430, 610)
LEFT_X, RIGHT_X = 18, 706


def card(draw, x, y, w, h, num, headline, subline, icon_fn, lead):
    outline = GOLD if lead else (110, 132, 172)
    draw.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=CARD_FILL,
                           outline=outline, width=3 if lead else 1)
    bx, by = x + 18, y + 18
    draw.ellipse([bx - 13, by - 13, bx + 13, by + 13], fill=GOLD)
    bf = font(16, bold=True)
    draw.text((bx - tw(draw, str(num), bf) / 2, by - th(draw, str(num), bf) / 2 - 1),
              str(num), font=bf, fill=(10, 22, 51))
    icon_fn(draw, x + w - 60, y + 8, 52, 40)
    maxw = w - 78
    size = 26 if lead else 24
    hf = font(size, bold=True)
    while size > 16 and tw(draw, headline, hf) > maxw:
        size -= 1
        hf = font(size, bold=True)
    if tw(draw, headline, hf) > maxw:
        hf = font(16, bold=True)
        lines = wrap(draw, headline, hf, maxw)[:2]
        hy = y + 52
        for ln in lines:
            draw.text((x + 10, hy), ln, font=hf, fill=WHITE)
            hy += th(draw, ln, hf) + 2
    else:
        hy = y + 52
        draw.text((x + 10, hy), headline, font=hf, fill=WHITE)
        hy += th(draw, headline, hf) + 4
    sf = font(16)
    for ln in wrap(draw, subline, sf, maxw)[:3]:
        draw.text((x + 10, hy), ln, font=sf, fill=GREY)
        hy += th(draw, ln, sf) + 2


CARDS = [
    (1, "KERCH BRIDGE HIT", "Ukraine strikes bridge to Crimea; road span collapses", icon_bridge, True),
    (2, "TRUMP IN MANILA", "ASEAN trip; APEC next, talks with Xi and Putin ahead", icon_plane, False),
    (3, "HORMUZ TANKERS HIT", "Mines strike two oil tankers; Iran fires drones at US radar in Bahrain", icon_tanker, False),
    (4, "VULCAN ROCKET LOST", "ULA rocket lost; 40 Amazon Leo satellites destroyed", icon_rocket, False),
    (5, "JPMORGAN OUTAGE", "Software bug, not a hack, slows banking and Zelle", icon_bank, False),
    (6, "JETS OVER JAPAN", "Suspected Russian aircraft violates Japanese airspace", icon_jets, False),
]


def draw_cards(draw):
    pos = []
    for i, c in enumerate(CARDS):
        x = LEFT_X if i < 3 else RIGHT_X
        pos.append((x, ROWS[i] if i < 3 else ROWS[i - 3], CW_LEAD if c[4] else CW))
    for i, (x, y, w) in enumerate(pos):
        yc = y + CH // 2
        if x < 512:
            ctrl = ((x + w + 343) / 2 - 30, (yc + 430) / 2 + (8 if i % 2 else -8))
            dashed_bezier(draw, (x + w, yc), ctrl, (343, 430))
        else:
            ctrl = ((x + 681) / 2 + 30, (yc + 430) / 2 + (8 if i % 2 else -8))
            dashed_bezier(draw, (x, yc), ctrl, (681, 430))
    for i, c in enumerate(CARDS):
        card(draw, pos[i][0], pos[i][1], pos[i][2], CH, *c)


# ---- piece 4: footer + main ----
FOOTER_LINES = [
    "Depardieu pleads guilty in Paris assault case",
    "Five European states plan joint migrant hub in Rwanda",
    "Nvidia reports earnings after Huang exit",
]


def draw_footer(draw):
    band = (9, 20, 44)
    draw.rectangle([0, 930, W, 1010], fill=band)
    draw.line([(0, 930), (W, 930)], fill=GOLD, width=3)
    f = font(19)
    lh = 26
    y0 = 931
    for i, ln in enumerate(FOOTER_LINES):
        draw.text(((W - tw(draw, ln, f)) / 2, y0 + i * lh), ln, font=f, fill=WHITE)
        if i < 2:
            gy = y0 + (i + 1) * lh - 1
            draw.ellipse([W / 2 - 2, gy - 2, W / 2 + 2, gy + 2], fill=GOLD)


def main():
    img = gradient_bg()
    draw = ImageDraw.Draw(img)
    add_stars(draw)
    draw_masthead(draw)
    draw_globe(img, draw)
    draw_cards(draw)
    draw_footer(draw)
    img.save("entry.png")
    print("wrote entry.png")


if __name__ == "__main__":
    main()