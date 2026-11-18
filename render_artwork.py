# render_artwork.py - draws the entry artwork for news-image-20261118.
#
# The Day in One Image: a front-page poster summing up the world news of
# Wednesday 18 November 2026 on one 1024x1024 canvas. This script runs
# locally (it needs Pillow and the DejaVu fonts); the harness never runs
# it. Its output, artwork.png, is what main.py copies to the output.
#
# Stories (all reported on 18 Nov 2026; see README.md):
#   APEC Shenzhen summit, US-Iran strikes at Hormuz, Kerch Bridge strike,
#   US Senate 56-44, Nvidia's record quarter, US measles status lost,
#   Congo Ebola passes 11,000 cases, Voyager 1 at one light-day,
#   plus two one-line briefs (Knesset speaker, COP31 Antalya).

import math
import random

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
M = 46                      # page margin
CW = W - 2 * M              # content width

PAPER = (246, 241, 231)
PAPER_LT = (252, 250, 244)
INK = (26, 26, 28)
INK_SOFT = (74, 70, 62)
RED = (176, 32, 44)
NAVY = (27, 48, 84)
NAVY_DK = (16, 26, 48)
NAVY_LT = (52, 78, 122)
GOLD = (198, 148, 32)
HAIR = (150, 142, 124)
SEA = (64, 110, 150)
SAND = (206, 184, 138)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


def serif_b(size):
    return font("DejaVuSerif-Bold.ttf", size)


def serif(size):
    return font("DejaVuSerif.ttf", size)


def sans_b(size):
    return font("DejaVuSans-Bold.ttf", size)


def sans(size):
    return font("DejaVuSans.ttf", size)


def text_w(d, s, f, tracking=0):
    w = 0
    for ch in s:
        w += d.textlength(ch, font=f) + tracking
    return w - (tracking if s else 0)


def draw_tracked(d, x, y, s, f, fill, tracking=0):
    cx = x
    for ch in s:
        d.text((cx, y), ch, font=f, fill=fill)
        cx += d.textlength(ch, font=f) + tracking
    return cx


def draw_centered(d, cx, y, s, f, fill, tracking=0):
    w = text_w(d, s, f, tracking)
    return draw_tracked(d, cx - w / 2, y, s, f, fill, tracking)


def wrap(d, s, f, max_w):
    words = s.split()
    lines = []
    cur = ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if d.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, x, y, s, f, fill, max_w, leading):
    lines = wrap(d, s, f, max_w)
    for ln in lines:
        d.text((x, y), ln, font=f, fill=fill)
        y += leading
    return y


def rule(d, y, x0=M, x1=W - M, fill=INK, wdt=2):
    d.line([(x0, y), (x1, y)], fill=fill, width=wdt)


def masthead(d):
    rule(d, 32, wdt=6)
    rule(d, 44, wdt=2)
    draw_centered(d, W // 2, 54, "THE DAY IN ONE IMAGE", serif_b(43), INK, tracking=3)
    draw_centered(d, W // 2, 106, "WEDNESDAY 18 NOVEMBER 2026", sans_b(46), RED, tracking=2)
    draw_centered(d, W // 2, 158,
                  "The world's news of one day, summed in a single picture",
                  serif(24), INK_SOFT)
    rule(d, 192, wdt=2)
    rule(d, 198, wdt=1)


def hero_visual(d, x, y, w, h):
    # Navy band: Shenzhen skyline, a gold sun, and the three flags.
    for i in range(h):
        t = i / max(h - 1, 1)
        col = tuple(int(NAVY_DK[c] + (NAVY_LT[c] - NAVY_DK[c]) * t) for c in range(3))
        d.line([(x, y + i), (x + w, y + i)], fill=col)
    sun_cx, sun_cy, sun_r = x + int(w * 0.70), y + int(h * 0.32), 21
    d.ellipse([sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r], fill=GOLD)
    base = y + h
    heights = [18, 32, 24, 40, 28, 46, 34, 22, 42, 26, 36, 20, 32, 44, 25, 30, 17, 38, 23, 31]
    bw = w / len(heights)
    for i, bh in enumerate(heights):
        bx = x + i * bw
        d.rectangle([bx + 1, base - bh, bx + bw - 1, base], fill=NAVY_DK)
    pole_x = [x + 58, x + 132, x + 206]
    top = y + 4
    for px in pole_x:
        d.line([(px, top), (px, base - 12)], fill=PAPER_LT, width=3)
    fw, fh = 48, 30
    fx, fy = pole_x[0] + 3, top + 2
    d.rectangle([fx, fy, fx + fw, fy + fh], fill=(222, 41, 57))
    for sx, sy, sr in [(8, 6, 3), (16, 3, 2), (18, 8, 2), (18, 13, 2), (16, 18, 2)]:
        d.ellipse([fx + sx - sr, fy + sy - sr, fx + sx + sr, fy + sy + sr], fill=(255, 222, 0))
    fx, fy = pole_x[1] + 3, top + 2
    d.rectangle([fx, fy, fx + fw, fy + fh // 3], fill=(245, 245, 245))
    d.rectangle([fx, fy + fh // 3, fx + fw, fy + 2 * fh // 3], fill=(0, 57, 166))
    d.rectangle([fx, fy + 2 * fh // 3, fx + fw, fy + fh], fill=(213, 0, 50))
    fx, fy = pole_x[2] + 3, top + 2
    for i in range(7):
        col = (178, 34, 52) if i % 2 == 0 else (245, 245, 245)
        d.rectangle([fx, fy + i * fh / 7, fx + fw, fy + (i + 1) * fh / 7], fill=col)
    d.rectangle([fx, fy, fx + fw * 0.45, fy + fh * 4 / 7], fill=(60, 59, 110))


def hero(d):
    y = 212
    draw_tracked(d, M, y, "SHENZHEN - APEC SUMMIT", sans_b(25), RED, tracking=2)
    tag = "THE LEAD STORY"
    draw_tracked(d, W - M - text_w(d, tag, sans_b(19), 2), y + 4, tag,
                 sans_b(19), INK_SOFT, tracking=2)
    y += 36
    d.text((M, y), "THREE POWERS, ONE TABLE", font=serif_b(58), fill=INK)
    y += 70
    deck = ("Xi Jinping opens APEC in Shenzhen and meets Vladimir Putin; "
            "Trump flies in for Thursday's three-way summit.")
    y = draw_wrapped(d, M, y, deck, sans(27), INK, CW, 35)
    y += 8
    hero_visual(d, M, y, CW, 64)
    return y + 64


def hormuz_motif(d, x, y, w, h):
    # A narrow strait between two land masses, a ship, a dashed strike arc.
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    d.polygon([(x, y), (x + w * 0.52, y), (x + w * 0.34, y + h * 0.52), (x, y + h * 0.62)],
              fill=SAND)
    d.polygon([(x + w, y + h * 0.38), (x + w, y + h), (x + w * 0.40, y + h),
               (x + w * 0.60, y + h * 0.55)], fill=SAND)
    d.rectangle([x + w * 0.42, y + h * 0.40, x + w * 0.53, y + h * 0.52], fill=INK)
    d.line([(x + w * 0.36, y + h * 0.56), (x + w * 0.58, y + h * 0.53)], fill=INK, width=3)
    pts = []
    for i in range(25):
        t = i / 24
        pts.append((x + w * (0.10 + 0.78 * t), y + h * (0.90 - 1.00 * t + 0.36 * t * t)))
    for i in range(0, len(pts) - 1, 2):
        d.line([pts[i], pts[i + 1]], fill=RED, width=3)
    bx, by = pts[-1]
    for dx, dy in [(0, -6), (4, -4), (6, 0), (4, 4), (0, 6), (-4, 4), (-6, 0), (-4, -4)]:
        d.line([(bx, by), (bx + dx, by + dy)], fill=RED, width=2)


def kerch_motif(d, x, y, w, h):
    # A bridge over water; the middle span has dropped into the sea.
    sea_y = y + h - 5
    d.line([(x, sea_y), (x + w, sea_y)], fill=SEA, width=4)
    deck_y = y + h * 0.30
    for px in (x + w * 0.16, x + w * 0.84):
        d.line([(px, deck_y), (px, sea_y)], fill=INK, width=5)
        d.line([(px, deck_y - 10), (px + (w * 0.30 if px < x + w / 2 else -w * 0.30), deck_y)],
               fill=INK, width=2)
        d.line([(px, deck_y - 10), (px, deck_y)], fill=INK, width=3)
    d.line([(x, deck_y), (x + w * 0.40, deck_y)], fill=INK, width=5)
    d.line([(x + w * 0.60, deck_y), (x + w, deck_y)], fill=INK, width=5)
    d.polygon([(x + w * 0.42, deck_y + 2), (x + w * 0.58, deck_y + 2),
               (x + w * 0.55, sea_y - 3), (x + w * 0.45, sea_y - 3)], fill=INK)
    bx, by = x + w * 0.50, deck_y - 4
    for dx, dy in [(0, -8), (6, -6), (8, 0), (6, 6), (-6, -6), (-8, 0), (-6, 6)]:
        d.line([(bx, by), (bx + dx, by + dy)], fill=RED, width=3)


def war_card(d, x, y, w, kicker, headline, motif, deck):
    draw_tracked(d, x, y, kicker, sans_b(22), RED, tracking=2)
    y += 30
    y = draw_wrapped(d, x, y, headline, serif_b(32), INK, w, 39)
    y += 6
    motif(d, x, y, w, 36)
    y += 46
    draw_wrapped(d, x, y, deck, sans(22), INK, w, 27)


def war_band(d, y):
    col_w = (CW - 40) // 2
    war_card(d, M, y, col_w, "STRAIT OF HORMUZ",
             "US AND IRAN TRADE BLOWS AT HORMUZ",
             hormuz_motif,
             "US jets hit a Guards missile site on Qeshm Island; Iran strikes "
             "US bases in Kuwait and Bahrain.")
    x2 = M + col_w + 40
    d.line([(M + col_w + 20, y + 2), (M + col_w + 20, y + 240)], fill=HAIR, width=1)
    war_card(d, x2, y, col_w, "UKRAINE - CRIMEA",
             "UKRAINE CRIPPLES THE KERCH BRIDGE",
             kerch_motif,
             "A Ukrainian strike partially collapses Russia's road-and-rail "
             "lifeline to Crimea, on the eve of the summit talks.")


def voyager_panel(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY_DK)
    rng = random.Random(20261118)
    for _ in range(80):
        sx = x + rng.uniform(6, w - 6)
        sy = y + rng.uniform(6, h - 6)
        if sx > x + 112 and sy < y + 128:
            continue  # keep the text zone clear of stars
        r = rng.choice([1, 1, 1, 2])
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(220, 226, 240))
    cx, cy = x + 46, y + 48
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], outline=GOLD, width=4)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=GOLD)
    d.line([(cx, cy), (cx + 32, cy + 20)], fill=GOLD, width=4)
    d.line([(cx + 32, cy + 20), (cx + 64, cy + 20)], fill=PAPER_LT, width=3)
    d.line([(cx + 32, cy + 20), (cx + 48, cy - 12)], fill=PAPER_LT, width=3)
    tx = x + 124
    draw_tracked(d, tx, y + 14, "DEEP SPACE - SCIENCE", sans_b(19), GOLD, tracking=2)
    d.text((tx, y + 40), "ONE LIGHT-DAY", font=serif_b(33), fill=PAPER_LT)
    draw_wrapped(d, tx, y + 84,
                 "Some 16 billion miles from Earth, a first for any "
                 "human-made object.",
                 sans(20), (206, 212, 228), w - 124 - 14, 23)


def ebola_card(d, x, y, w):
    cx, cy, r = x + 30, y + 34, 15
    for i in range(8):
        a = i * math.pi / 4
        x1, y1 = cx + (r + 2) * math.cos(a), cy + (r + 2) * math.sin(a)
        x2, y2 = cx + (r + 12) * math.cos(a), cy + (r + 12) * math.sin(a)
        d.line([(x1, y1), (x2, y2)], fill=RED, width=3)
        d.ellipse([x2 - 4, y2 - 4, x2 + 4, y2 + 4], fill=RED)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    tx = x + 76
    draw_tracked(d, tx, y + 4, "CONGO - HEALTH", sans_b(22), RED, tracking=2)
    d.text((x, y + 58), "EBOLA PASSES 11,000 CASES", font=serif_b(26), fill=INK)
    draw_wrapped(d, x, y + 96,
                 "Second-largest outbreak on record; children under five "
                 "hit hardest.",
                 sans(22), INK, w, 26)


def ticker_row(d, y, segs):
    fb, fr = sans_b(19), sans(19)
    total = 0
    for bold, rest in segs:
        total += d.textlength(bold, font=fb) + 7 + d.textlength(rest, font=fr)
    total += (len(segs) - 1) * 40
    x = (W - total) / 2
    for i, (bold, rest) in enumerate(segs):
        x = draw_tracked(d, x, y, bold, fb, NAVY)
        x += 7
        x = draw_tracked(d, x, y, rest, fr, INK)
        if i < len(segs) - 1:
            x += 17
            d.ellipse([x, y + 7, x + 6, y + 13], fill=RED)
            x += 23


def numbers_ticker(d, y):
    ticker_row(d, y, [
        ("SENATE 56-44", "Peltola wins Alaska"),
        ("NVIDIA $115.8BN", "revenue +103%"),
    ])
    ticker_row(d, y + 28, [
        ("MEASLES 5,412", "US status lost"),
        ("KNESSET", "Kahana elected speaker"),
        ("COP31", "$50m pledge 'crumbs'"),
    ])


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    masthead(d)
    y = hero(d)
    rule(d, y + 12, wdt=2)
    war_band(d, y + 26)
    rule(d, 746, wdt=1)
    by = 758
    col_w = (CW - 40) // 2
    voyager_panel(d, M, by, col_w, 156)
    ebola_card(d, M + col_w + 40, by + 4, col_w)
    rule(d, 922, wdt=1)
    numbers_ticker(d, 934)
    rule(d, 994, wdt=4)
    img.save("artwork.png", optimize=True)
    print("wrote artwork.png", img.size)


if __name__ == "__main__":
    main()
