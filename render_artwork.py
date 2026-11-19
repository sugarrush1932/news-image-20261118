# render_artwork.py - draws the entry artwork for news-image-20261118.
#
# The Day in One Image, v2: a dense front page summing up the world news
# of Wednesday 18 November 2026 on one 1024x1024 canvas. 48 stories:
# 16 illustrated panels plus 32 one-line briefs, a UTC timeline strip, a
# dotted world map with pins for the panel stories, and a DATE CHECK box
# listing what was deliberately left out on date grounds. Every printed
# story was verified against at least two independent reports read on
# 19 Nov 2026 (AP, Reuters, AFP, Al Jazeera, BBC, AAP, NASA, WHO, IMD,
# Kyiv Independent and others); [CLAIM] marks one side's account.
#
# This script runs locally (Pillow + DejaVu fonts); the harness never
# runs it. Its output, artwork.png, is what main.ts copies to the output.
# The render is deterministic: two runs produce byte-identical PNGs.

import math
import random

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
M = 28                      # page margin
CW = W - 2 * M              # content width (968)

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
GREEN = (46, 110, 62)

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


def draw_wrapped(d, x, y, s, f, fill, max_w, leading, max_lines=None):
    lines = wrap(d, s, f, max_w)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        d.text((x, y), ln, font=f, fill=fill)
        y += leading
    return y


def rule(d, y, x0=M, x1=W - M, fill=INK, wdt=2):
    d.line([(x0, y), (x1, y)], fill=fill, width=wdt)


# ---------------------------------------------------------------- stories
# region, field, headline, deck, source tag, motif key
PANELS = [
    ("ASIA", "DIPLOMACY", "XI, PUTIN AND TRUMP CONVERGE ON SHENZHEN",
     "Xi meets Putin and greets Trump at the airport; the three meet Thursday.",
     "[CONFIRMED] AFP/AP", "apec"),
    ("MIDDLE EAST", "CONFLICT", "IRAN FIRES DRONES AT US BASE IN KUWAIT",
     "Kuwait says its defences intercepted the drones; Tehran claims Patriots hit.",
     "[CONFIRMED] AP", "drone"),
    ("EUROPE", "WAR", "ODESA STRUCK AGAIN; EU OFFERS KYIV \u20ac45BN",
     "Three strikes hit the historic centre, killing four; EU offers a \u20ac45bn loan.",
     "[CONFIRMED] AL JAZEERA", "odesa"),
    ("GLOBAL", "SPACE", "VOYAGER 1 CROSSES ONE LIGHT-DAY",
     "At 10:16 UTC it passed 25.9bn km out \u2014 light now takes a full day to reach it.",
     "[CONFIRMED] NASA", "voyager"),
    ("MIDDLE EAST", "WAR", "ISRAELI TANKS CROSS GAZA'S YELLOW LINE",
     "First ground push into Hamas-held Gaza since the truce; Hamas cries violation.",
     "[CONFIRMED] REUTERS", "tank"),
    ("AFRICA", "SECURITY", "ETHIOPIA, ERITREA MASS TROOPS AT BORDER",
     "Both armies within striking distance near Badme; reported shelling unconfirmed.",
     "[CONFIRMED] REUTERS", "border"),
    ("AMERICAS", "MARKETS", "FED MINUTES POINT TO MORE HIKES; DOW -561",
     "Almost all officials backed more hikes; the Dow shed 1.11%, Nasdaq rose 0.42%.",
     "[CONFIRMED] AP", "fed"),
    ("ASIA", "LABOUR", "WAGE PROTESTS SHUT HUNDREDS OF FACTORIES",
     "Workers seeking 30,000 taka block highways; about 500 factories shut nationwide.",
     "[CONFIRMED] AFP", "factory"),
    ("AMERICAS", "DIPLOMACY", "US SIGNS DEFENCE DEAL IN CARACAS",
     "Hegseth and Rodr\u00edguez restore military ties: joint training and intelligence.",
     "[CONFIRMED] AP", "flags"),
    ("ASIA", "CLIMATE", "COP31 ENTERS ITS DECISIVE PHASE",
     "Rival fossil-fuel wordings and a $120bn adaptation plan; a deal is due Friday.",
     "[CONFIRMED] WIRES", "leaf"),
    ("AMERICAS", "POLITICS", "DEMOCRATS PICK JEFFRIES FOR SPEAKER",
     "A 251\u201311 caucus vote makes him the likely first Black speaker; House votes 3 Jan.",
     "[CONFIRMED] AP", "gavel"),
    ("AMERICAS", "BUSINESS", "ANTHROPIC'S $81BN IPO IS LARGEST EVER",
     "Priced at $83, above range; the AI lab is valued near $1.5tn, trading Thursday.",
     "[CONFIRMED] REUTERS", "bell"),
    ("ASIA", "WEATHER", "CYCLONE AKVAN BEARS DOWN ON ODISHA",
     "Some 47,000 evacuated, red alerts on the coast; landfall expected Friday.",
     "[CONFIRMED] IMD", "cyclone"),
    ("GLOBAL", "GAMES", "GTA VI'S WORLDWIDE LAUNCH BEGINS",
     "Rolls out at midnight local time, New Zealand first, on PS5 and Xbox Series.",
     "[CONFIRMED] ROCKSTAR", "palm"),
    ("AFRICA", "HEALTH", "CONGO'S EBOLA CASES PASS 11,000",
     "WHO keeps the emergency in place; children are over a quarter of all cases.",
     "[CONFIRMED] WHO/UN", "ebola"),
    ("OCEANIA", "MUSIC", "TAME IMPALA SWEEPS AUSTRALIA'S ARIAS",
     "Seven wins in Sydney, incl. Album of the Year for Deadbeat; career tally 22.",
     "[CONFIRMED] AAP", "trophy"),
]

# text, region, source tag
BRIEFS = [
    ("UK inflation eases to 3.6%; diesel at record high", "EUROPE", "BBC"),
    ("Ukraine drones hit two Krasnodar refineries", "EUROPE", "KYIV IND."),
    ("Children ordered out of Balabyne, Zaporizhzhia", "EUROPE", "KYIV"),
    ("US sanctions Hezbollah finance network", "MIDDLE EAST", "TREASURY"),
    ("Iraq jails six French nationals over ISIL", "MIDDLE EAST", "AFP"),
    ("Japan PM Takaichi meets Putin, first since 2022", "ASIA", "WIRES"),
    ("Xi meets leaders of Mexico, Peru and Chile", "ASIA", "WIRES"),
    ("Seoul's Kospi jumps 2% on chip-stock rally", "ASIA", "WIRES"),
    ("Australia sanctions settler leader Weiss", "OCEANIA", "ABC"),
    ("Migrant boat capsizes off Senegal, one dead", "AFRICA", "AFP"),
    ("Uganda, Tanzania agree to speed oil pipeline", "AFRICA", "WIRES"),
    ("South Africa protests over HIV-care funding", "AFRICA", "WIRES"),
    ("Salvadoran troops raze Haiti gang chief's home", "AMERICAS", "AP"),
    ("Top US egg firm to cull 1.8m birds over flu", "AMERICAS", "WIRES"),
    ("Rubio: no evidence outages were an attack", "AMERICAS", "STATE"),
    ("Microsoft to use Intel chip packaging", "AMERICAS", "WIRES"),
    ("Gold falls to 14-month low under $3,750", "GLOBAL", "MKTS"),
    ("Pew: Islam set to be largest faith by 2035", "GLOBAL", "PEW"),
    ("Chelsea women beat PSG 1-0 in Europe", "EUROPE", "WIRES"),
    ("Myanmar leader to review ASEAN ties", "ASIA", "WIRES"),
    ("Anwar: multilateral order must change", "ASIA", "WIRES"),
    ("Putin: economic coercion is history", "ASIA", "WIRES"),
    ("Board of Peace warns Gaza truce at risk", "MIDDLE EAST", "AJ"),
    ("Turkey seizes an opposition broadcaster", "ASIA", "WIRES"),
    ("UK to send Ukraine 1,000+ air missiles", "EUROPE", "MOD"),
    ("Prague locomotive crash injures nine", "EUROPE", "WIRES"),
    ("Moldova shuts airspace over Russian drone", "EUROPE", "WIRES"),
    ("Russian strikes destroy two Kyiv bridges", "EUROPE", "KYIV"),
    ("Carney meets Trump at APEC sidelines", "ASIA", "PMO"),
    ("Nvidia slips ~3% after record results", "AMERICAS", "AP"),
    ("Alcaraz beats Medvedev 6-2, 6-4 in Turin", "EUROPE", "AP"),
    ("Ukraine hits Kerch Bridge a second night", "EUROPE", "AJ"),
]

TIMELINE = [
    ("OVERNIGHT", "Iran fires drones at a US base in Kuwait; Bahrain alerts"),
    ("MORNING", "Xi meets Putin in Shenzhen; Trump lands for APEC"),
    ("10:16 UTC", "Voyager 1 passes one light-day from the Sun"),
    ("AFTERNOON", "Israeli tanks cross Gaza's Yellow Line"),
    ("EVENING", "Fed minutes land; Dow closes down 561, Nasdaq up"),
    ("NIGHT", "ARIA Awards in Sydney; GTA VI reaches first players"),
]

DATE_CHECK = [
    "US strike on Iran's Qeshm Island \u2014 Tuesday's news.",
    "Alaska Senate call for Peltola \u2014 reported Tuesday.",
    "Nvidia's record $115.8bn quarter \u2014 Tuesday.",
    "Knesset elects speaker Kahana \u2014 Tuesday.",
    "US measles status loss \u2014 announced Tuesday.",
    "COP31's first draft \u2014 Monday; only Wed's endgame covered.",
    "AHEAD: COP31 ends Fri \u00b7 Akvan landfall Fri \u00b7 trilateral Thu.",
]


# ----------------------------------------------------------------- motifs
# Each motif draws inside a 64x64 box at (x, y), line-art style.

def burst(d, cx, cy, r, fill=RED, wdt=3):
    for dx, dy in [(0, -1), (0.7, -0.7), (1, 0), (0.7, 0.7), (0, 1),
                   (-0.7, 0.7), (-1, 0), (-0.7, -0.7)]:
        d.line([(cx, cy), (cx + dx * r, cy + dy * r)], fill=fill, width=wdt)


def m_apec(d, x, y):
    base = y + 58
    heights = [14, 24, 18, 30, 22, 34, 26, 16, 28, 20]
    bw = 64 / len(heights)
    for i, bh in enumerate(heights):
        bx = x + i * bw
        d.rectangle([bx + 0.5, base - bh, bx + bw - 0.5, base], fill=NAVY)
    d.line([(x, base), (x + 64, base)], fill=INK, width=2)
    for px, col in [(x + 12, (222, 41, 57)), (x + 30, (213, 0, 50)),
                    (x + 48, (178, 34, 52))]:
        d.line([(px, y + 6), (px, base - 20)], fill=INK, width=2)
        d.rectangle([px + 1, y + 6, px + 13, y + 14], fill=col)


def m_drone(d, x, y):
    cx, cy = x + 32, y + 30
    d.line([(cx - 12, cy - 8), (cx + 12, cy + 8)], fill=INK, width=3)
    d.line([(cx - 12, cy + 8), (cx + 12, cy - 8)], fill=INK, width=3)
    d.ellipse([cx - 7, cy - 5, cx + 7, cy + 5], fill=INK)
    for px, py in [(cx - 14, cy - 10), (cx + 14, cy - 10),
                   (cx - 14, cy + 10), (cx + 14, cy + 10)]:
        d.arc([px - 6, py - 3, px + 6, py + 3], 0, 360, fill=INK, width=2)
    for i, r in enumerate((12, 19, 26)):
        d.arc([x + 44 - r, y + 52 - r, x + 44 + r, y + 52 + r],
              200, 320, fill=SEA, width=2)
    d.polygon([(x + 38, y + 58), (x + 50, y + 58), (x + 44, y + 48)],
              fill=INK)


def m_odesa(d, x, y):
    base = y + 58
    d.line([(x, base), (x + 64, base)], fill=SEA, width=3)
    for cx0 in (x + 10, x + 38):
        d.line([(cx0, base), (cx0, y + 16)], fill=INK, width=3)
        d.line([(cx0, y + 16), (cx0 + 20, y + 16)], fill=INK, width=3)
        d.line([(cx0 + 16, y + 16), (cx0 + 16, base - 14)], fill=INK, width=1)
        d.rectangle([cx0 + 12, base - 14, cx0 + 20, base - 8], outline=INK)
    burst(d, x + 52, y + 10, 7)


def m_voyager(d, x, y):
    d.rectangle([x, y, x + 64, y + 64], fill=NAVY_DK)
    rng = random.Random(20261118)
    for _ in range(26):
        sx = x + rng.uniform(3, 61)
        sy = y + rng.uniform(3, 61)
        d.point((sx, sy), fill=(220, 226, 240))
    cx, cy = x + 24, y + 36
    d.arc([cx - 15, cy - 15, cx + 15, cy + 15], 300, 130, fill=GOLD, width=3)
    d.line([(cx, cy), (cx + 22, cy - 14)], fill=GOLD, width=3)
    d.line([(cx + 22, cy - 14), (cx + 46, cy - 14)], fill=PAPER_LT, width=2)
    d.line([(cx + 22, cy - 14), (cx + 34, cy - 26)], fill=PAPER_LT, width=2)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=GOLD)


def m_tank(d, x, y):
    base = y + 52
    d.line([(x, base + 6), (x + 64, base + 6)], fill=INK, width=2)
    for i in range(6):
        d.line([(x + 8 + i * 9, y + 8), (x + 8 + i * 9, base + 4)],
               fill=GOLD, width=2)
    d.polygon([(x + 8, base), (x + 14, base - 10), (x + 50, base - 10),
               (x + 56, base)], fill=INK)
    d.rectangle([x + 22, base - 20, x + 42, base - 10], fill=INK)
    d.line([(x + 42, base - 17), (x + 62, base - 20)], fill=INK, width=4)
    for wx in (x + 16, x + 28, x + 40, x + 50):
        d.ellipse([wx - 4, base - 5, wx + 4, base + 3], fill=PAPER)


def m_border(d, x, y):
    base = y + 56
    d.line([(x + 32, y + 6), (x + 32, base)], fill=RED, width=2)
    for yy in range(y + 10, base, 8):
        d.line([(x + 32, yy), (x + 32, yy + 4)], fill=PAPER, width=3)
    d.polygon([(x + 2, base), (x + 14, y + 30), (x + 26, base)], fill=NAVY)
    d.polygon([(x + 38, base), (x + 50, y + 30), (x + 62, base)], fill=NAVY)
    d.polygon([(x + 8, y + 34), (x + 26, y + 34), (x + 17, y + 44)],
              fill=INK)
    d.polygon([(x + 38, y + 34), (x + 56, y + 34), (x + 47, y + 44)],
              fill=INK)


def m_fed(d, x, y):
    d.polygon([(x + 32, y + 6), (x + 58, y + 18), (x + 6, y + 18)], fill=NAVY)
    for px in (x + 12, x + 25, x + 38, x + 51):
        d.rectangle([px - 3, y + 22, px + 3, y + 44], fill=NAVY)
    d.rectangle([x + 6, y + 47, x + 58, y + 51], fill=NAVY)
    pts = [(x + 8, y + 34), (x + 22, y + 40), (x + 34, y + 36),
           (x + 48, y + 46), (x + 58, y + 52)]
    d.line(pts, fill=RED, width=3)
    d.polygon([(x + 58, y + 52), (x + 50, y + 50), (x + 56, y + 44)],
              fill=RED)


def m_factory(d, x, y):
    base = y + 58
    d.rectangle([x + 6, base - 22, x + 44, base], outline=INK, width=2)
    for cx0 in (x + 12, x + 24):
        d.rectangle([cx0, base - 38, cx0 + 6, base - 22], fill=INK)
        d.ellipse([cx0 - 1, base - 46, cx0 + 7, base - 39], fill=HAIR)
    for sx in (x + 48, x + 56):
        d.line([(sx, base), (sx, base - 16)], fill=INK, width=2)
        d.rectangle([sx - 5, base - 24, sx + 5, base - 16], outline=RED,
                    width=2)
    d.line([(x, base), (x + 64, base)], fill=INK, width=2)


def m_flags(d, x, y):
    base = y + 58
    d.line([(x + 14, base), (x + 44, y + 8)], fill=INK, width=2)
    d.line([(x + 50, base), (x + 20, y + 8)], fill=INK, width=2)
    d.polygon([(x + 44, y + 8), (x + 58, y + 12), (x + 45, y + 18)],
              fill=(178, 34, 52))
    d.polygon([(x + 20, y + 8), (x + 6, y + 12), (x + 19, y + 18)],
              fill=(255, 204, 0))
    d.arc([x + 18, base - 20, x + 46, base + 4], 180, 360, fill=INK,
          width=2)


def m_leaf(d, x, y):
    d.ellipse([x + 14, y + 8, x + 52, y + 44], fill=GREEN)
    d.line([(x + 16, y + 46), (x + 50, y + 10)], fill=PAPER_LT, width=2)
    d.line([(x + 33, y + 48), (x + 33, y + 58)], fill=GREEN, width=3)
    d.ellipse([x + 44, y + 34, x + 60, y + 50], outline=GOLD, width=3)
    d.line([(x + 52, y + 42), (x + 52, y + 30)], fill=GOLD, width=2)


def m_gavel(d, x, y):
    d.line([(x + 16, y + 48), (x + 44, y + 20)], fill=INK, width=5)
    d.rectangle([x + 38, y + 8, x + 56, y + 20], fill=NAVY)
    d.rectangle([x + 34, y + 12, x + 40, y + 16], fill=NAVY)
    d.rectangle([x + 54, y + 12, x + 60, y + 16], fill=NAVY)
    d.rectangle([x + 10, y + 54, x + 42, y + 58], fill=INK)
    burst(d, x + 54, y + 44, 6, fill=GOLD, wdt=2)


def m_bell(d, x, y):
    d.arc([x + 18, y + 12, x + 46, y + 44], 180, 360, fill=INK, width=3)
    d.line([(x + 18, y + 28), (x + 18, y + 44)], fill=INK, width=3)
    d.line([(x + 46, y + 28), (x + 46, y + 44)], fill=INK, width=3)
    d.rectangle([x + 14, y + 44, x + 50, y + 48], fill=INK)
    d.ellipse([x + 28, y + 50, x + 36, y + 56], fill=INK)
    pts = [(x + 6, y + 58), (x + 20, y + 50), (x + 32, y + 52),
           (x + 46, y + 40), (x + 58, y + 30)]
    d.line(pts, fill=GREEN, width=3)
    d.polygon([(x + 58, y + 30), (x + 50, y + 30), (x + 57, y + 37)],
              fill=GREEN)


def m_cyclone(d, x, y):
    cx, cy = x + 30, y + 30
    for r, a0 in ((26, 20), (19, 140), (12, 260), (6, 60)):
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + 240, fill=SEA,
              width=4)
    d.line([(x + 52, y + 6), (x + 58, y + 58)], fill=SAND, width=5)
    d.line([(x + 58, y + 6), (x + 62, y + 58)], fill=SAND, width=3)


def m_palm(d, x, y):
    base = y + 58
    heights = [12, 20, 15, 24, 17]
    bw = 64 / len(heights)
    for i, bh in enumerate(heights):
        bx = x + i * bw
        d.rectangle([bx + 1, base - bh, bx + bw - 1, base], fill=NAVY_DK)
    d.line([(x + 44, base), (x + 46, y + 26)], fill=INK, width=3)
    for a in (200, 245, 290, 335):
        ex = x + 46 + 15 * math.cos(math.radians(a))
        ey = y + 26 + 10 * math.sin(math.radians(a))
        d.line([(x + 46, y + 26), (ex, ey)], fill=GREEN, width=3)
    d.ellipse([x + 6, y + 6, x + 18, y + 18], fill=GOLD)


def m_ebola(d, x, y):
    cx, cy, r = x + 32, y + 32, 13
    for i in range(8):
        a = i * math.pi / 4
        x1, y1 = cx + (r + 1) * math.cos(a), cy + (r + 1) * math.sin(a)
        x2, y2 = cx + (r + 10) * math.cos(a), cy + (r + 10) * math.sin(a)
        d.line([(x1, y1), (x2, y2)], fill=RED, width=3)
        d.ellipse([x2 - 3.5, y2 - 3.5, x2 + 3.5, y2 + 3.5], fill=RED)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=PAPER)


def m_trophy(d, x, y):
    d.polygon([(x + 20, y + 8), (x + 44, y + 8), (x + 42, y + 30),
               (x + 22, y + 30)], fill=GOLD)
    d.arc([x + 8, y + 10, x + 24, y + 26], 90, 270, fill=GOLD, width=3)
    d.arc([x + 40, y + 10, x + 56, y + 26], 270, 90, fill=GOLD, width=3)
    d.rectangle([x + 29, y + 30, x + 35, y + 40], fill=GOLD)
    d.rectangle([x + 22, y + 40, x + 42, y + 45], fill=INK)
    burst(d, x + 32, y + 54, 5, fill=RED, wdt=2)


MOTIFS = {
    "apec": m_apec, "drone": m_drone, "odesa": m_odesa,
    "voyager": m_voyager, "tank": m_tank, "border": m_border,
    "fed": m_fed, "factory": m_factory, "flags": m_flags,
    "leaf": m_leaf, "gavel": m_gavel, "bell": m_bell,
    "cyclone": m_cyclone, "palm": m_palm, "ebola": m_ebola,
    "trophy": m_trophy,
}


# ------------------------------------------------------------- world map
# Rough continent outlines as (lon, lat) polygons; the map is dot-sampled
# from a filled mask, so the shapes stay simple and stylised.
CONTINENTS = [
    # North America + Greenland
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-75, 62), (-65, 60), (-55, 52), (-65, 45), (-70, 42),
     (-74, 39), (-76, 35), (-80, 32), (-81, 26), (-84, 30), (-89, 30),
     (-94, 29), (-97, 26), (-97, 22), (-94, 18), (-90, 20), (-87, 21),
     (-86, 16), (-83, 10), (-79, 9), (-85, 11), (-90, 14), (-95, 16),
     (-100, 17), (-105, 20), (-110, 23), (-114, 28), (-117, 33),
     (-122, 37), (-124, 44), (-124, 48), (-130, 55), (-145, 60),
     (-158, 58), (-165, 60)],
    [(-45, 60), (-30, 68), (-22, 70), (-20, 76), (-30, 80), (-50, 78),
     (-58, 70), (-55, 62)],
    # South America
    [(-79, 9), (-72, 12), (-64, 10), (-55, 6), (-50, 0), (-44, -3),
     (-35, -8), (-39, -13), (-40, -20), (-48, -26), (-52, -32), (-57, -38),
     (-62, -41), (-65, -45), (-67, -50), (-68, -54), (-71, -54),
     (-73, -50), (-73, -44), (-73, -37), (-71, -30), (-70, -20),
     (-75, -15), (-79, -8), (-81, -4), (-80, 1), (-77, 4)],
    # Europe + Britain + Iceland
    [(-9, 43), (-9, 37), (-6, 36), (-2, 37), (0, 39), (3, 42), (7, 44),
     (10, 44), (12, 42), (16, 38), (18, 40), (15, 44), (19, 46), (23, 40),
     (26, 38), (28, 41), (30, 46), (33, 46), (38, 47), (40, 45), (36, 36),
     (30, 40), (26, 44), (23, 46), (19, 54), (18, 56), (12, 55), (8, 55),
     (8, 57), (5, 58), (5, 60), (10, 63), (16, 66), (22, 69), (30, 70),
     (35, 67), (33, 64), (28, 60), (24, 58), (21, 56), (14, 54), (8, 54),
     (4, 52), (0, 51), (-2, 50), (-5, 48), (-2, 47), (-2, 44)],
    [(-5, 50), (-3, 53), (-5, 55), (-8, 55), (-6, 58), (-3, 58), (-2, 55),
     (-1, 52)],
    [(-22, 64), (-14, 64), (-14, 66), (-22, 66)],
    # Africa + Madagascar
    [(-6, 35), (0, 36), (10, 37), (11, 34), (20, 32), (30, 31), (32, 31),
     (34, 28), (35, 24), (37, 22), (39, 20), (43, 12), (48, 11), (51, 12),
     (48, 5), (46, 0), (42, -5), (40, -12), (38, -18), (36, -22),
     (33, -26), (30, -31), (26, -34), (20, -35), (17, -32), (15, -27),
     (13, -20), (12, -15), (13, -10), (9, -5), (9, 0), (8, 4), (4, 6),
     (-2, 5), (-8, 5), (-13, 8), (-17, 12), (-17, 15), (-16, 20),
     (-15, 25), (-13, 28), (-10, 31)],
    [(44, -16), (49, -15), (50, -20), (47, -24), (45, -25), (44, -20)],
    # Asia: Siberia/Central + Arabia + India + Indochina + Japan/Korea
    [(28, 41), (36, 36), (40, 40), (44, 42), (48, 46), (50, 52), (48, 60),
     (50, 66), (55, 68), (60, 69), (70, 72), (85, 74), (100, 76),
     (120, 73), (140, 72), (160, 69), (178, 68), (178, 65), (170, 66),
     (160, 64), (150, 62), (140, 60), (130, 60), (120, 58), (110, 58),
     (100, 57), (90, 56), (80, 55), (70, 54), (66, 50), (60, 52), (55, 52),
     (50, 50), (48, 44), (44, 40), (36, 36), (33, 36), (30, 40)],
    [(36, 33), (39, 30), (42, 28), (45, 26), (48, 28), (50, 26), (52, 24),
     (55, 24), (58, 22), (59, 22), (57, 19), (55, 17), (52, 15), (48, 14),
     (44, 13), (42, 15), (40, 20), (38, 24), (35, 28), (34, 31)],
    [(72, 20), (76, 10), (78, 8), (80, 10), (82, 16), (86, 20), (88, 22),
     (91, 22), (89, 24), (86, 23), (80, 22), (76, 22)],
    [(92, 21), (95, 17), (97, 10), (98, 8), (99, 6), (100, 5), (102, 8),
     (104, 9), (106, 10), (108, 12), (109, 15), (107, 17), (105, 19),
     (103, 20), (100, 20), (98, 22), (95, 22)],
    [(95, 16), (98, 14), (100, 8), (103, 2), (104, -2), (101, 2),
     (99, 7), (97, 12)],
    [(130, 31), (133, 34), (137, 35), (140, 36), (141, 39), (141, 42),
     (142, 44), (140, 45), (138, 40), (135, 35), (132, 33)],
    [(126, 38), (128, 38), (129, 40), (127, 42), (126, 40)],
    [(114, 22), (118, 25), (120, 28), (121, 31), (119, 34), (117, 37),
     (114, 38), (110, 36), (106, 35), (102, 33), (100, 30), (102, 26),
     (106, 23), (110, 21), (112, 22)],
    # Indonesia (blobs) + Philippines
    [(95, 5), (100, 0), (103, -3), (100, -4), (96, 2)],
    [(105, -6), (110, -7), (114, -8), (110, -8), (105, -7)],
    [(110, 0), (115, 2), (119, 0), (117, -3), (112, -2)],
    [(119, -1), (123, -2), (125, -4), (121, -4)],
    [(131, -1), (136, -2), (141, -3), (141, -6), (136, -5), (132, -3)],
    [(121, 14), (122, 16), (121, 18), (120, 16)],
    # Australia + New Zealand
    [(113, -22), (114, -28), (115, -33), (118, -35), (124, -33),
     (129, -32), (132, -32), (135, -35), (138, -36), (140, -38),
     (145, -38), (150, -37), (153, -30), (153, -27), (151, -24),
     (149, -20), (146, -19), (143, -15), (142, -11), (142, -14),
     (141, -17), (140, -20), (139, -23), (136, -24), (135, -12),
     (136, -15), (132, -11), (130, -12), (126, -14), (122, -17),
     (118, -20), (114, -21)],
    [(167, -45), (170, -43), (172, -41), (174, -39), (176, -38),
     (178, -37), (176, -40), (173, -41), (171, -43), (168, -46)],
]

# panel number -> (lon, lat) for map pins; 4 (Voyager) is off-map.
PINS = {
    1: (114.1, 22.5), 2: (48.0, 29.4), 3: (30.7, 46.5), 5: (34.3, 31.4),
    6: (39.8, 14.7), 7: (-77.0, 38.9), 8: (90.4, 23.8), 9: (-66.9, 10.5),
    10: (30.7, 36.9), 11: (-75.5, 40.5), 12: (-74.0, 40.7),
    13: (84.9, 19.3), 14: (172.6, -43.5), 15: (23.5, -2.9),
    16: (151.2, -33.9),
}


def draw_map(d, x, y, w, h):
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)

    def proj(lon, lat):
        return ((lon + 180) / 360 * w, (85 - lat) / 145 * h)

    for poly in CONTINENTS:
        md.polygon([proj(lon, lat) for lon, lat in poly], fill=255)
    px = mask.load()
    step = 4
    for gy in range(step // 2, h, step):
        for gx in range(step // 2, w, step):
            if px[gx, gy]:
                d.ellipse([x + gx - 1, y + gy - 1, x + gx + 1, y + gy + 1],
                          fill=(120, 132, 148))
    f = sans_b(9)
    for num, (lon, lat) in PINS.items():
        gx, gy = proj(lon, lat)
        cx, cy = x + gx, y + gy
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED)
        s = str(num)
        tw = d.textlength(s, font=f)
        d.text((cx - tw / 2, cy - 5), s, font=f, fill=PAPER_LT)


# ---------------------------------------------------------------- layout

def masthead(d):
    rule(d, 24, wdt=6)
    rule(d, 36, wdt=2)
    draw_centered(d, W // 2, 46, "THE DAY IN ONE IMAGE", serif_b(40), INK,
                  tracking=3)
    draw_centered(d, W // 2, 92, "WEDNESDAY 18 NOVEMBER 2026", sans_b(33),
                  RED, tracking=2)
    counts = {}
    for region, *_ in PANELS:
        counts[region] = counts.get(region, 0) + 1
    for _, region, _ in BRIEFS:
        counts[region] = counts.get(region, 0) + 1
    total = sum(counts.values())
    order = ["ASIA", "EUROPE", "AMERICAS", "MIDDLE EAST", "AFRICA",
             "GLOBAL", "OCEANIA"]
    line = "%d STORIES \u00b7 " % total + " \u00b7 ".join(
        "%s %d" % (r, counts[r]) for r in order)
    draw_centered(d, W // 2, 128, line, sans_b(13), NAVY, tracking=1)
    draw_centered(d, W // 2, 148,
                  "One day of world news on a single page \u2014 every "
                  "story checked against at least two reports",
                  serif(15), INK_SOFT)
    rule(d, 170, wdt=2)
    rule(d, 176, wdt=1)
    return total


def timeline(d, y):
    d.rectangle([M, y, W - M, y + 44], fill=NAVY_DK)
    col_w = CW // 3
    for i, (when, what) in enumerate(TIMELINE):
        cx = M + (i % 3) * col_w + 12
        cy = y + 3 + (i // 3) * 21
        draw_tracked(d, cx, cy, when, sans_b(9), GOLD, tracking=1)
        draw_wrapped(d, cx + text_w(d, when, sans_b(9), 1) + 7, cy,
                     what, sans(8), (216, 221, 232), col_w - 24 -
                     text_w(d, when, sans_b(9), 1), 9, max_lines=2)


REGION_SHORT = {"MIDDLE EAST": "MIDEAST"}


def panel(d, idx, x, y, w):
    region, field, headline, deck, source, motif = PANELS[idx]
    num = idx + 1
    d.rectangle([x, y, x + 20, y + 15], fill=RED)
    s = str(num)
    f = sans_b(10)
    d.text((x + 10 - d.textlength(s, font=f) / 2, y + 2), s, font=f,
           fill=PAPER_LT)
    draw_tracked(d, x + 26, y + 3,
                 "%s \u00b7 %s" % (REGION_SHORT.get(region, region), field),
                 sans_b(8), NAVY, tracking=0)
    sw = text_w(d, source, sans_b(7), 0)
    draw_tracked(d, x + w - sw, y + 4, source, sans_b(7), INK_SOFT)
    MOTIFS[motif](d, x, y + 20)
    hl = wrap(d, headline, serif_b(13), w - 76)
    assert len(hl) <= 3, (num, hl)
    draw_wrapped(d, x + 72, y + 22, headline, serif_b(13), INK, w - 76,
                 15, max_lines=3)
    dl = wrap(d, deck, sans(10), w)
    assert len(dl) <= 2, (num, dl)
    draw_wrapped(d, x, y + 86, deck, sans(10), INK, w, 10, max_lines=2)


def panels_grid(d, y):
    col_w = CW // 4
    row_h = 114
    for idx in range(16):
        cx = M + (idx % 4) * col_w
        cy = y + (idx // 4) * row_h
        panel(d, idx, cx + 4, cy + 4, col_w - 12)
        if idx % 4 != 3:
            d.line([(cx + col_w - 2, cy + 8), (cx + col_w - 2,
                    cy + row_h - 8)], fill=HAIR, width=1)
        if idx // 4 != 3:
            d.line([(cx + 6, cy + row_h - 2), (cx + col_w - 6,
                    cy + row_h - 2)], fill=HAIR, width=1)


def bottom(d, y):
    # Left column: map + DATE CHECK.
    lx, lw = M, 302
    draw_tracked(d, lx, y, "WHERE IT HAPPENED \u2014 PANEL PINS",
                 sans_b(11), INK, tracking=1)
    draw_map(d, lx, y + 16, lw, 120)
    d.text((lx, y + 140),
           "Pin 4 (Voyager 1) is in deep space, off the map.",
           font=sans(9), fill=INK_SOFT)
    by = y + 162
    d.rectangle([lx, by, lx + lw, by + 104], outline=INK, width=2)
    draw_tracked(d, lx + 10, by + 6, "DATE CHECK \u2014 LEFT OUT, AND WHY",
                 sans_b(10), RED, tracking=1)
    ty = by + 22
    for ln in DATE_CHECK:
        d.text((lx + 10, ty), ln, font=sans(9), fill=INK)
        ty += 11
    # Right column: ALSO ON briefs, two columns of 16.
    rx = M + 330
    rw = W - M - rx
    draw_tracked(d, rx, y, "ALSO ON WEDNESDAY \u2014 32 MORE STORIES",
                 sans_b(12), RED, tracking=1)
    rule(d, y + 17, x0=rx, x1=W - M, fill=INK, wdt=1)
    col_w = rw // 2
    for i, (text, region, src) in enumerate(BRIEFS):
        cx = rx + (i // 16) * col_w
        cy = y + 25 + (i % 16) * 15
        num = 17 + i
        draw_tracked(d, cx, cy, "%d" % num, sans_b(9), NAVY)
        tx = cx + 20 if num < 10 else cx + 24
        draw_tracked(d, tx, cy, text, sans(9), INK)
        tw = text_w(d, text, sans(9))
        d.text((tx + tw + 5, cy), "[%s]" % src, font=sans(8), fill=INK_SOFT)


def footer(d):
    rule(d, 968, wdt=1)
    draw_centered(d, W // 2, 976,
                  "Every story above happened or was first reported on "
                  "Wednesday 18 November 2026; nothing older is shown as "
                  "the day's news.",
                  sans_b(10), INK)
    draw_centered(d, W // 2, 992,
                  "Sources: AP \u00b7 Reuters \u00b7 AFP \u00b7 Al Jazeera "
                  "\u00b7 BBC \u00b7 AAP \u00b7 NASA \u00b7 WHO \u00b7 IMD "
                  "\u00b7 Kyiv Independent. [CLAIM] marks one side's "
                  "account, not independently confirmed.",
                  sans(9), INK_SOFT)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    total = masthead(d)
    assert total == 48, total
    timeline(d, 186)
    panels_grid(d, 240)
    bottom(d, 700)
    footer(d)
    img.save("artwork.png", optimize=True)
    print("wrote artwork.png", img.size)


if __name__ == "__main__":
    main()
