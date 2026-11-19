# render_artwork.py - draws the entry artwork for news-image-20261118.
#
# The Day in One Image, v4: a dense front page summing up the world news
# of Wednesday 18 November 2026 on one 1024x1024 canvas. 58 stories:
# 16 illustrated panels plus 42 one-line briefs, two taxonomy strips
# (by region and by field), an 8-slot UTC timeline, a DAY IN NUMBERS
# stat row, a filled world map with pins for the panel stories, and a
# DATE CHECK strip listing what was deliberately left out on date
# grounds. Every printed story was verified against at least two
# independent reports read on 19 Nov 2026 (AP, Reuters, AFP, Al Jazeera,
# BBC, AAP, NASA, WHO, IMD, Amnesty, GFZ, EMSC, Kyiv Independent and
# others); [CLAIM] marks one side's account.
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
GOLD = (198, 148, 32)
HAIR = (150, 142, 124)
SEA = (64, 110, 150)
SAND = (206, 184, 138)
GREEN = (46, 110, 62)
SIL = (43, 39, 33)          # silhouette ink for scene bands

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


def serif_b(size):
    return font("DejaVuSerif-Bold.ttf", size)


def serif(size):
    return font("DejaVuSerif.ttf", size)


def serif_i(size):
    # No serif italic in this DejaVu set; the subline uses regular serif.
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


def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(pts, fill=fill)


def burst(d, cx, cy, r, fill=RED):
    pts = []
    for i in range(16):
        ang = i * math.pi / 8
        rad = r if i % 2 == 0 else r * 0.38
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(pts, fill=fill)


def gradient(d, box, top, bottom):
    x0, y0, x1, y1 = box
    steps = max(1, int(y1 - y0))
    for i in range(steps):
        t = i / steps
        c = tuple(round(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)


def palm(d, bx, by, s, color):
    """A palm silhouette: curved trunk plus five drooping fronds."""
    top = (bx + 0.35 * s, by - s)
    pts = []
    for i in range(9):
        t = i / 8
        pts.append((bx + 0.35 * s * t * t, by - s * t))
    d.line(pts, fill=color, width=max(2, int(s * 0.1)))
    for ang in (-165, -125, -85, -45, -8):
        ex = top[0] + 0.62 * s * math.cos(math.radians(ang))
        ey = top[1] + 0.34 * s * math.sin(math.radians(ang)) + 0.16 * s
        mid = (top[0] + 0.34 * s * math.cos(math.radians(ang)),
               top[1] + 0.40 * s * math.sin(math.radians(ang)))
        d.line([top, mid, (ex, ey)], fill=color,
               width=max(2, int(s * 0.07)))


# ---------------------------------------------------------------- stories
# Panels: region, tag field, headline, deck, source tag, scene key,
# taxonomy field. Taxonomy fields are the nine BY FIELD categories.
PANELS = [
    ("ASIA", "DIPLOMACY", "XI, PUTIN AND TRUMP CONVERGE ON SHENZHEN",
     "Xi meets Putin and greets Trump at the airport; the three meet Thursday.",
     "[CONFIRMED] AFP/AP", "apec", "DIPLOMACY"),
    ("MIDDLE EAST", "CONFLICT", "IRAN FIRES DRONES AT US BASE IN KUWAIT",
     "Kuwait says its defences intercepted the drones; Tehran claims Patriots hit.",
     "[CONFIRMED] AP", "drone", "WAR & SECURITY"),
    ("EUROPE", "WAR", "ODESA STRUCK AGAIN; EU OFFERS KYIV \u20ac45BN",
     "141 drones overnight, 126 downed; four die in Odesa as EU offers a \u20ac45bn loan.",
     "[CONFIRMED] AL JAZEERA", "odesa", "WAR & SECURITY"),
    ("GLOBAL", "SPACE", "VOYAGER 1 CROSSES ONE LIGHT-DAY",
     "At 10:16 UTC it passed 25.9bn km out \u2014 light now takes a full day to reach it.",
     "[CONFIRMED] NASA", "voyager", "SCIENCE & HEALTH"),
    ("MIDDLE EAST", "WAR", "ISRAELI TANKS CROSS GAZA'S YELLOW LINE",
     "First ground push into Hamas-held Gaza since the truce; Hamas cries violation.",
     "[CONFIRMED] REUTERS", "tank", "WAR & SECURITY"),
    ("AFRICA", "SECURITY", "ETHIOPIA, ERITREA MASS TROOPS AT BORDER",
     "Both armies within striking distance near Badme; reported shelling unconfirmed.",
     "[CONFIRMED] REUTERS", "border", "WAR & SECURITY"),
    ("AMERICAS", "MARKETS", "FED MINUTES POINT TO MORE HIKES; DOW -561",
     "Almost all officials backed more hikes; the Dow shed 1.11%, Nasdaq rose 0.42%.",
     "[CONFIRMED] AP", "fed", "ECONOMY & MARKETS"),
    ("ASIA", "LABOUR", "WAGE PROTESTS SHUT HUNDREDS OF FACTORIES",
     "Workers seeking 30,000 taka block highways; about 500 factories shut nationwide.",
     "[CONFIRMED] AFP", "factory", "LABOUR & SOCIETY"),
    ("AMERICAS", "DIPLOMACY", "US SIGNS DEFENCE DEAL IN CARACAS",
     "Hegseth and Rodr\u00edguez restore military ties: joint training and intelligence.",
     "[CONFIRMED] AP", "flags", "DIPLOMACY"),
    ("ASIA", "CLIMATE", "COP31 ENTERS ITS DECISIVE PHASE",
     "Rival fossil-fuel wordings and a $120bn adaptation plan; a deal is due Friday.",
     "[CONFIRMED] WIRES", "cop", "CLIMATE & DISASTERS"),
    ("AMERICAS", "POLITICS", "DEMOCRATS PICK JEFFRIES FOR SPEAKER",
     "A 251\u201311 caucus vote makes him the likely first Black speaker; House votes 3 Jan.",
     "[CONFIRMED] AP", "gavel", "POLITICS & COURTS"),
    ("AMERICAS", "BUSINESS", "ANTHROPIC'S $81BN IPO IS LARGEST EVER",
     "Priced at $83, above range; the AI lab is valued near $1.5tn, trading Thursday.",
     "[CONFIRMED] REUTERS", "bell", "BUSINESS & TECH"),
    ("ASIA", "WEATHER", "CYCLONE AKVAN BEARS DOWN ON ODISHA",
     "Some 47,000 evacuated, red alerts on the coast; landfall expected Friday.",
     "[CONFIRMED] IMD", "cyclone", "CLIMATE & DISASTERS"),
    ("GLOBAL", "GAMES", "GTA VI'S WORLDWIDE LAUNCH BEGINS",
     "Rolls out at midnight local time, New Zealand first, on PS5 and Xbox Series.",
     "[CONFIRMED] ROCKSTAR", "gta", "CULTURE & SPORT"),
    ("AFRICA", "HEALTH", "CONGO'S EBOLA CASES PASS 11,300",
     "WHO keeps the emergency in place; 5,500 dead, children over a quarter of cases.",
     "[CONFIRMED] WHO/UN", "ebola", "SCIENCE & HEALTH"),
    ("OCEANIA", "MUSIC", "TAME IMPALA SWEEPS AUSTRALIA'S ARIAS",
     "Seven wins in Sydney, incl. Album of the Year for Deadbeat; career tally 22.",
     "[CONFIRMED] AAP", "trophy", "CULTURE & SPORT"),
]

# Briefs: text, region, taxonomy field. Place-prefix one-liners.
BRIEFS = [
    ("UK: inflation eases to 3.6%", "EUROPE", "ECONOMY & MARKETS"),
    ("Kyiv: drones hit Krasnodar refineries", "EUROPE", "WAR & SECURITY"),
    ("Zaporizhzhia: children ordered out", "EUROPE", "WAR & SECURITY"),
    ("US: sanctions on Hezbollah finance web", "MIDDLE EAST", "WAR & SECURITY"),
    ("Iraq: six French jailed over ISIL", "MIDDLE EAST", "POLITICS & COURTS"),
    ("Tokyo: Takaichi meets Putin, a first", "ASIA", "DIPLOMACY"),
    ("Shenzhen: Xi meets Mexico, Peru, Chile", "ASIA", "DIPLOMACY"),
    ("Seoul: Kospi jumps 2% on chip rally", "ASIA", "ECONOMY & MARKETS"),
    ("Canberra: settler Weiss sanctioned", "OCEANIA", "DIPLOMACY"),
    ("Dakar: migrant boat capsizes, one dead", "AFRICA", "CLIMATE & DISASTERS"),
    ("Uganda, Tanzania speed oil pipeline", "AFRICA", "ECONOMY & MARKETS"),
    ("Pretoria: protests over HIV-care funds", "AFRICA", "LABOUR & SOCIETY"),
    ("Haiti: Salvadoran troops raze gang HQ", "AMERICAS", "WAR & SECURITY"),
    ("US: top egg firm culls 1.8m birds, flu", "AMERICAS", "SCIENCE & HEALTH"),
    ("US: no sign outages were an attack", "AMERICAS", "POLITICS & COURTS"),
    ("Tech: Microsoft to use Intel packaging", "AMERICAS", "BUSINESS & TECH"),
    ("Markets: gold falls to 14-month low", "GLOBAL", "ECONOMY & MARKETS"),
    ("Pew: Islam largest faith by 2035", "GLOBAL", "CULTURE & SPORT"),
    ("Football: Chelsea women beat PSG 1-0", "EUROPE", "CULTURE & SPORT"),
    ("Myanmar: leader to review ASEAN ties", "ASIA", "DIPLOMACY"),
    ("Anwar: multilateral order must change", "ASIA", "DIPLOMACY"),
    ("Putin: economic coercion is history", "ASIA", "DIPLOMACY"),
    ("Board of Peace: Gaza truce at risk", "MIDDLE EAST", "DIPLOMACY"),
    ("Ankara: opposition broadcaster seized", "ASIA", "POLITICS & COURTS"),
    ("UK: 1,000+ air missiles for Ukraine", "EUROPE", "WAR & SECURITY"),
    ("Prague: locomotive crash injures nine", "EUROPE", "CLIMATE & DISASTERS"),
    ("Moldova shuts airspace over drone", "EUROPE", "WAR & SECURITY"),
    ("Kyiv: strikes wreck two bridges", "EUROPE", "WAR & SECURITY"),
    ("APEC: Carney meets Trump on sidelines", "ASIA", "DIPLOMACY"),
    ("Markets: Nvidia slips 3% after results", "AMERICAS", "ECONOMY & MARKETS"),
    ("Turin: Alcaraz beats Medvedev 6-2, 6-4", "EUROPE", "CULTURE & SPORT"),
    ("Kerch Bridge hit a second night", "EUROPE", "WAR & SECURITY"),
    ("Riyadh: Houthi missiles downed", "MIDDLE EAST", "WAR & SECURITY"),
    ("El Obeid: Amnesty \u2014 RSF drones kill 37", "AFRICA", "WAR & SECURITY"),
    ("Berlin: coalition agrees power-tax cut", "EUROPE", "ECONOMY & MARKETS"),
    ("Kashmir: Lashkar chief Bhat killed", "ASIA", "WAR & SECURITY"),
    ("Bucharest: 5.3 quake felt in capital", "EUROPE", "CLIMATE & DISASTERS"),
    ("PNG: magnitude 6.0 quake strikes", "OCEANIA", "CLIMATE & DISASTERS"),
    ("Shenzhen: Xi pledges role on Korea peace", "ASIA", "DIPLOMACY"),
    ("Beirut: World Bank \u2014 rebuilding too slow", "MIDDLE EAST",
     "ECONOMY & MARKETS"),
    ("Brasilia: Senate passes Lula $10bn plan", "AMERICAS",
     "ECONOMY & MARKETS"),
    ("Manila: Trump hails 'biggest' trade deal", "ASIA",
     "ECONOMY & MARKETS"),
]

FIELDS = ["DIPLOMACY", "WAR & SECURITY", "ECONOMY & MARKETS",
          "POLITICS & COURTS", "CULTURE & SPORT", "BUSINESS & TECH",
          "LABOUR & SOCIETY", "CLIMATE & DISASTERS", "SCIENCE & HEALTH"]

REGIONS = ["ASIA", "EUROPE", "AMERICAS", "MIDDLE EAST", "AFRICA",
           "GLOBAL", "OCEANIA"]

REGION_COLORS = {
    "ASIA": (166, 61, 64), "EUROPE": (46, 95, 138),
    "AMERICAS": (61, 122, 68), "MIDDLE EAST": (181, 84, 30),
    "AFRICA": (176, 132, 26), "GLOBAL": (96, 96, 104),
    "OCEANIA": (64, 110, 150),
}

TIMELINE = [
    ("OVERNIGHT", "Iran fires drones at US base in Kuwait"),
    ("07:00 UTC", "UK inflation: 3.6%"),
    ("MORNING", "Xi greets Trump in Shenzhen"),
    ("10:16 UTC", "Voyager 1: one light-day"),
    ("11:00 UTC", "GTA VI unlocks in NZ"),
    ("19:00 UTC", "Fed minutes: more hikes"),
    ("21:00 UTC", "Dow closes down 561"),
    ("LATE", "Anthropic prices record IPO"),
]

NUMBERS = [
    ("25.9bn km", "Voyager 1: one light-day out"),
    ("251\u201311", "Democrats' Speaker vote"),
    ("$81.3bn", "Anthropic's record IPO"),
    ("~500", "Bangladesh factories shut"),
    ("11,300+", "Ebola cases in DR Congo"),
    ("47,000", "evacuated for Cyclone Akvan"),
]

DATE_CHECK = [
    "Qeshm strike \u00b7 Peltola call \u00b7 Nvidia quarter \u2014 Tuesday",
    "Knesset speaker vote \u00b7 measles status loss \u2014 Tuesday",
    "Kemerovo An-12 crash, 19 dead \u2014 Tuesday evening",
    "NSA classified-network failure \u2014 broke Tuesday",
    "Quad summit, Manila \u00b7 Tha\u00e7i sentence \u2014 Tuesday",
    "COP31 first draft \u2014 Monday; Wed endgame only",
    "AHEAD: COP31 ends Fri \u00b7 Akvan lands Fri \u00b7 summit Thu",
]


# ----------------------------------------------------------------- scenes
# Each scene fills a wide, short band (w x 32) at (x, y): a tinted
# backdrop with a small flat-colour scene, not a bare icon.

SKY = (213, 226, 238)
DUSK = (233, 208, 186)
PALE = (226, 232, 214)
GREY = (230, 227, 220)
SANDT = (240, 228, 198)


def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 57))
    star(d, x + w * 0.28, y + h * 0.34, h * 0.2, (255, 222, 0))
    for dx, dy in ((0.52, 0.18), (0.58, 0.38), (0.58, 0.58), (0.5, 0.74)):
        d.ellipse([x + w * dx - 1.5, y + h * dy - 1.5,
                   x + w * dx + 1.5, y + h * dy + 1.5], fill=(255, 222, 0))


def flag_us(d, x, y, w, h):
    stripe = h / 5
    for i in range(5):
        c = (178, 34, 52) if i % 2 == 0 else (250, 248, 244)
        d.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe],
                    fill=c)
    d.rectangle([x, y, x + w * 0.42, y + stripe * 3], fill=(60, 59, 110))


def flag_ru(d, x, y, w, h):
    third = h / 3
    for i, c in enumerate(((250, 248, 244), (0, 57, 166), (213, 43, 30))):
        d.rectangle([x, y + i * third, x + w, y + (i + 1) * third],
                    fill=c)


def flag_ve(d, x, y, w, h):
    third = h / 3
    for i, c in enumerate(((252, 209, 22), (0, 56, 147), (206, 17, 39))):
        d.rectangle([x, y + i * third, x + w, y + (i + 1) * third],
                    fill=c)


def sc_apec(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    base = y + h
    heights = [10, 16, 8, 20, 13, 18, 9, 15, 11, 17, 8, 14]
    bw = w / len(heights)
    for i, bh in enumerate(heights):
        bx = x + i * bw
        d.rectangle([bx + 0.5, base - bh, bx + bw - 0.5, base], fill=NAVY)
    cx = x + w / 2
    for k, fn in enumerate((flag_cn, flag_us, flag_ru)):
        fx = cx + (k - 1) * 44 - 13
        d.line([(fx + 13, base), (fx + 13, y + 3)], fill=SIL, width=2)
        fn(d, fx, y + 3, 26, 13)


def sc_drone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=DUSK)
    base = y + h
    for i, bh in enumerate((7, 11, 6, 9)):
        bx = x + 8 + i * 26
        d.rectangle([bx, base - bh, bx + 18, base], fill=SIL)
    cx, cy = x + w * 0.52, y + h * 0.42
    d.line([(cx - 13, cy - 7), (cx + 13, cy + 7)], fill=SIL, width=3)
    d.line([(cx - 13, cy + 7), (cx + 13, cy - 7)], fill=SIL, width=3)
    d.ellipse([cx - 6, cy - 4, cx + 6, cy + 4], fill=SIL)
    for px, py in [(cx - 15, cy - 9), (cx + 15, cy - 9),
                   (cx - 15, cy + 9), (cx + 15, cy + 9)]:
        d.arc([px - 5, py - 3, px + 5, py + 3], 0, 360, fill=SIL, width=2)
    for r in (9, 15, 21):
        d.arc([x + w - 34 - r, base - 4 - r, x + w - 34 + r,
               base - 4 + r], 200, 320, fill=SEA, width=2)
    burst(d, x + w - 20, y + 8, 6, RED)


def sc_odesa(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    base = y + h
    for cx0 in (x + 30, x + 84):
        d.line([(cx0, base), (cx0, y + 6)], fill=SIL, width=3)
        d.line([(cx0, y + 6), (cx0 + 30, y + 6)], fill=SIL, width=3)
        d.line([(cx0 + 25, y + 6), (cx0 + 25, base - 9)], fill=SIL,
               width=1)
        d.rectangle([cx0 + 21, base - 9, cx0 + 29, base - 4], outline=SIL)
    burst(d, x + w - 42, y + 10, 8, RED)
    burst(d, x + w - 22, y + 18, 5, GOLD)
    for sx in range(int(x + 8), int(x + w - 8), 18):
        d.line([(sx, base - 2), (sx + 9, base - 2)], fill=SEA, width=2)


def sc_voyager(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY_DK)
    rng = random.Random(20261118)
    for _ in range(46):
        sx = x + rng.uniform(2, w - 2)
        sy = y + rng.uniform(2, h - 2)
        d.point((sx, sy), fill=(220, 226, 240))
    cx, cy = x + w * 0.42, y + h * 0.55
    d.arc([cx - 13, cy - 13, cx + 13, cy + 13], 300, 130, fill=GOLD,
          width=3)
    d.line([(cx, cy), (cx + 20, cy - 11)], fill=GOLD, width=2)
    d.line([(cx + 20, cy - 11), (cx + 52, cy - 11)], fill=PAPER_LT,
           width=2)
    d.line([(cx + 20, cy - 11), (cx + 33, cy - 21)], fill=PAPER_LT,
           width=2)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=GOLD)
    d.ellipse([x + 12, y + h - 12, x + 22, y + h - 2], fill=SEA)
    d.line([(x + 26, y + h - 7), (cx - 18, cy + 6)], fill=(150, 160, 190),
           width=1)


def sc_tank(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SANDT)
    base = y + h - 3
    d.line([(x, base + 2), (x + w, base + 2)], fill=SIL, width=2)
    hx = x + w * 0.3
    d.polygon([(hx, base), (hx + 7, base - 8), (hx + 52, base - 8),
               (hx + 59, base)], fill=SIL)
    d.rectangle([hx + 17, base - 15, hx + 40, base - 8], fill=SIL)
    d.line([(hx + 40, base - 13), (hx + 66, base - 15)], fill=SIL, width=3)
    for k in range(4):
        wx = hx + 9 + k * 13
        d.ellipse([wx, base - 5, wx + 8, base + 1], fill=SIL)
    for px in (x + w * 0.72, x + w * 0.82, x + w * 0.92):
        d.line([(px, y + 5), (px, base)], fill=GOLD, width=3)
        d.line([(px, y + 11), (px, base)], fill=SIL, width=1)


def sc_border(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PALE)
    base = y + h
    d.polygon([(x + 8, base), (x + 52, y + 8), (x + 96, base)], fill=NAVY)
    d.polygon([(x + w - 96, base), (x + w - 52, y + 8), (x + w - 8, base)],
              fill=NAVY)
    d.polygon([(x + 44, y + 13), (x + 52, y + 8), (x + 60, y + 13)],
              fill=PAPER_LT)
    d.polygon([(x + w - 60, y + 13), (x + w - 52, y + 8),
               (x + w - 44, y + 13)], fill=PAPER_LT)
    cx = x + w / 2
    d.rectangle([cx - 2, y + 8, cx + 2, base], fill=RED)
    d.rectangle([cx - 2, y + 14, cx + 2, y + 19], fill=PAPER_LT)
    d.polygon([(cx - 52, base), (cx - 40, base - 9), (cx - 28, base)],
              fill=SIL)
    d.polygon([(cx + 28, base), (cx + 40, base - 9), (cx + 52, base)],
              fill=SIL)


def sc_fed(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=GREY)
    bx = x + 16
    d.polygon([(bx + 30, y + 3), (bx + 62, y + 11), (bx - 2, y + 11)],
              fill=NAVY)
    for px in (bx + 4, bx + 17, bx + 30, bx + 43):
        d.rectangle([px, y + 14, px + 6, y + h - 6], fill=NAVY)
    d.rectangle([bx - 2, y + h - 5, bx + 62, y + h - 2], fill=NAVY)
    pts = [(x + w * 0.48, y + 8), (x + w * 0.6, y + 13),
           (x + w * 0.7, y + 10), (x + w * 0.84, y + 19),
           (x + w * 0.95, y + 25)]
    d.line(pts, fill=RED, width=3)
    ex, ey = pts[-1]
    d.polygon([(ex, ey), (ex - 9, ey - 1), (ex - 2, ey - 8)], fill=RED)
    d.text((x + w * 0.48, y + h - 11), "-561", font=sans_b(10), fill=RED)


def sc_factory(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=GREY)
    base = y + h
    d.rectangle([x + 14, base - 15, x + 92, base], outline=SIL, width=2)
    for cx0 in (x + 22, x + 38):
        d.rectangle([cx0, base - 27, cx0 + 6, base - 15], fill=SIL)
        d.ellipse([cx0 - 2, base - 33, cx0 + 8, base - 26], fill=HAIR)
    for k, sx in enumerate((x + w * 0.55, x + w * 0.68, x + w * 0.81)):
        d.line([(sx, base), (sx, base - 12)], fill=SIL, width=2)
        d.rectangle([sx - 8, base - 21, sx + 8, base - 12], outline=RED,
                    width=2)


def sc_flags(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    base = y + h
    cx = x + w / 2
    d.line([(cx - 34, base), (cx + 22, y + 4)], fill=SIL, width=2)
    d.line([(cx + 34, base), (cx - 22, y + 4)], fill=SIL, width=2)
    flag_us(d, cx + 22, y + 4, 30, 14)
    flag_ve(d, cx - 52, y + 4, 30, 14)
    d.arc([cx - 26, base - 15, cx + 26, base + 5], 180, 360, fill=SIL,
          width=2)


def sc_cop(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PALE)
    cx, cy = x + w * 0.3, y + h / 2
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], outline=SEA, width=3)
    d.ellipse([cx - 5, cy - 12, cx + 5, cy + 12], outline=SEA, width=1)
    d.line([(cx - 12, cy), (cx + 12, cy)], fill=SEA, width=1)
    lx = x + w * 0.58
    d.ellipse([lx, y + 5, lx + 30, y + 23], fill=GREEN)
    d.line([(lx + 2, y + 24), (lx + 28, y + 6)], fill=PAPER_LT, width=2)
    d.ellipse([x + w - 30, y + 4, x + w - 16, y + 18], fill=GOLD)
    d.text((x + w * 0.78, y + h - 12), "$120bn", font=sans_b(10),
           fill=GREEN)


def sc_gavel(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=GREY)
    base = y + h - 2
    cx = x + w * 0.34
    d.arc([cx - 22, y + 6, cx + 22, y + 34], 180, 360, fill=NAVY)
    d.rectangle([cx - 26, base - 8, cx + 26, base], fill=NAVY)
    for px in (cx - 20, cx - 7, cx + 6, cx + 18):
        d.rectangle([px, base - 16, px + 4, base - 8], fill=NAVY)
    bx = x + w * 0.66
    d.rectangle([bx, y + 7, bx + 30, y + 27], outline=SIL, width=2)
    d.line([(bx + 6, y + 17), (bx + 13, y + 23)], fill=GREEN, width=3)
    d.line([(bx + 13, y + 23), (bx + 25, y + 10)], fill=GREEN, width=3)
    d.text((bx + 38, y + 12), "251\u201311", font=sans_b(11), fill=SIL)


def sc_bell(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PALE)
    bx = x + 26
    d.arc([bx, y + 5, bx + 26, y + 29], 180, 360, fill=SIL, width=3)
    d.line([(bx, y + 17), (bx, y + 26)], fill=SIL, width=3)
    d.line([(bx + 26, y + 17), (bx + 26, y + 26)], fill=SIL, width=3)
    d.rectangle([bx - 3, y + 26, bx + 29, y + 29], fill=SIL)
    pts = [(x + w * 0.42, y + 24), (x + w * 0.56, y + 18),
           (x + w * 0.68, y + 20), (x + w * 0.82, y + 11),
           (x + w * 0.95, y + 5)]
    d.line(pts, fill=GREEN, width=3)
    ex, ey = pts[-1]
    d.polygon([(ex, ey), (ex - 9, ey), (ex - 2, ey + 7)], fill=GREEN)
    d.text((x + w * 0.42, y + 3), "$83", font=sans_b(11), fill=SIL)


def sc_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    cx, cy = x + w * 0.26, y + h / 2
    for r, a0 in ((13, 20), (9, 140), (5, 260)):
        d.arc([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], a0, a0 + 240,
              fill=SEA, width=3)
    d.line([(x + w * 0.62, y + 2), (x + w * 0.58, y + h - 2)], fill=SAND,
           width=5)
    for k in range(4):
        rx = x + w * (0.72 + 0.07 * k)
        d.line([(rx, y + 5), (rx - 4, y + 11)], fill=SEA, width=2)
        d.line([(rx, y + 16), (rx - 4, y + 22)], fill=SEA, width=2)
    d.text((x + w * 0.7, y + h - 11), "RED ALERT", font=sans_b(9),
           fill=RED)


def sc_gta(d, x, y, w, h):
    gradient(d, (x, y, x + w, y + h), (196, 82, 130), (246, 150, 80))
    base = y + h
    cx = x + w * 0.52
    d.ellipse([cx - 10, base - 20, cx + 10, base], fill=(255, 205, 92))
    for i, bh in enumerate((8, 14, 6, 17, 10, 13, 7, 15, 9)):
        bx = x + 6 + i * (w - 12) / 9
        d.rectangle([bx, base - bh, bx + (w - 12) / 9 - 4, base],
                    fill=(30, 8, 34))
    palm(d, x + 26, base, 24, (30, 8, 34))
    palm(d, x + w - 40, base, 18, (30, 8, 34))


def sc_ebola(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SANDT)
    cx, cy = x + w * 0.36, y + h / 2
    r = 8
    for i in range(8):
        a = i * math.pi / 4
        x1 = cx + (r + 1) * math.cos(a)
        y1 = cy + (r + 1) * math.sin(a)
        x2 = cx + (r + 6) * math.cos(a)
        y2 = cy + (r + 6) * math.sin(a)
        d.line([(x1, y1), (x2, y2)], fill=RED, width=3)
        d.ellipse([x2 - 2.5, y2 - 2.5, x2 + 2.5, y2 + 2.5], fill=RED)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    bx = x + w * 0.62
    d.rectangle([bx, y + 5, bx + 22, y + 27], fill=PAPER_LT, outline=SIL)
    d.rectangle([bx + 8, y + 9, bx + 14, y + 23], fill=RED)
    d.rectangle([bx + 5, y + 13, bx + 17, y + 19], fill=RED)
    d.text((bx + 30, y + 11), "11,300+", font=sans_b(11), fill=SIL)


def sc_trophy(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=DUSK)
    base = y + h
    cx = x + w / 2
    d.polygon([(cx - 11, y + 3), (cx + 11, y + 3), (cx + 9, base - 9),
               (cx - 9, base - 9)], fill=GOLD)
    d.arc([cx - 20, y + 5, cx - 8, y + 17], 90, 270, fill=GOLD, width=3)
    d.arc([cx + 8, y + 5, cx + 20, y + 17], 270, 90, fill=GOLD, width=3)
    d.rectangle([cx - 8, base - 4, cx + 8, base], fill=SIL)
    for bw, bh in ((74, 3), (52, 6), (30, 9)):
        d.rectangle([cx - bw / 2, base - bh, cx + bw / 2, base],
                    fill=SIL)
    burst(d, cx - 52, y + 9, 5, RED)
    burst(d, cx + 52, y + 9, 5, RED)
    star(d, cx + 78, y + 14, 4, GOLD)
    star(d, cx - 78, y + 14, 4, GOLD)


SCENES = {
    "apec": sc_apec, "drone": sc_drone, "odesa": sc_odesa,
    "voyager": sc_voyager, "tank": sc_tank, "border": sc_border,
    "fed": sc_fed, "factory": sc_factory, "flags": sc_flags,
    "cop": sc_cop, "gavel": sc_gavel, "bell": sc_bell,
    "cyclone": sc_cyclone, "gta": sc_gta, "ebola": sc_ebola,
    "trophy": sc_trophy,
}


# ------------------------------------------------------------- world map
# Rough continent outlines as (lon, lat) polygons, drawn filled so the
# landmasses read cleanly at small size.
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

LAND = (178, 192, 160)
SEAC = (206, 222, 235)


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SEAC)

    def proj(lon, lat):
        return (x + (lon + 180) / 360 * w, y + (85 - lat) / 145 * h)

    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND)
    f = sans_b(9)
    for num, (lon, lat) in PINS.items():
        cx, cy = proj(lon, lat)
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED)
        s = str(num)
        tw = d.textlength(s, font=f)
        d.text((cx - tw / 2, cy - 5), s, font=f, fill=PAPER_LT)


# ---------------------------------------------------------------- layout

def counts_of(items, idx):
    counts = {}
    for it in items:
        counts[it[idx]] = counts.get(it[idx], 0) + 1
    return counts


def masthead(d):
    rule(d, 16, wdt=6)
    rule(d, 24, wdt=1)
    draw_tracked(d, M, 33, "THE WORLD'S NEWS OF ONE DAY, ON ONE PAGE",
                 sans_b(10), INK, tracking=1)
    region_counts = counts_of(PANELS, 0)
    for region, n in counts_of(BRIEFS, 1).items():
        region_counts[region] = region_counts.get(region, 0) + n
    total = sum(region_counts.values())
    right = "%d STORIES \u00b7 7 REGIONS \u00b7 9 FIELDS" % total
    rw = text_w(d, right, sans_b(10), 1)
    draw_tracked(d, W - M - rw, 33, right, sans_b(10), NAVY, tracking=1)
    draw_centered(d, W // 2, 46, "Wednesday 18 November 2026",
                  serif_b(50), INK)
    draw_centered(d, W // 2, 104,
                  "Everything on this page happened, or was first "
                  "reported, on Wednesday 18 November 2026.",
                  serif_i(14), INK_SOFT)
    return total, region_counts


def region_strip(d, y, region_counts):
    total = sum(region_counts.values())
    widths = []
    for r in REGIONS:
        widths.append(max(62, CW * region_counts[r] / total))
    # Rebalance so the segments sum exactly to CW.
    drift = CW - sum(widths)
    widths[0] += drift
    x = M
    f = sans_b(9)
    for r, wdt in zip(REGIONS, widths):
        d.rectangle([x, y, x + wdt - 2, y + 18], fill=REGION_COLORS[r])
        label = "%s %d" % (r, region_counts[r])
        lw = d.textlength(label, font=f)
        assert lw <= wdt - 6, (r, lw, wdt)
        d.text((x + (wdt - 2 - lw) / 2, y + 4), label, font=f,
               fill=PAPER_LT)
        x += wdt
    return total


def field_strip(d, y):
    field_counts = counts_of(PANELS, 6)
    for _, _, fld in BRIEFS:
        field_counts[fld] = field_counts.get(fld, 0) + 1
    assert sum(field_counts.values()) == len(PANELS) + len(BRIEFS), \
        field_counts
    ordered = sorted(FIELDS, key=lambda f: -field_counts[f])
    items = " \u00b7 ".join("%s %d" % (f, field_counts[f])
                            for f in ordered)
    d.rectangle([M, y, W - M, y + 15], fill=PAPER_LT, outline=HAIR)
    lx = draw_tracked(d, M + 8, y + 3, "BY FIELD", sans_b(8), RED)
    rest = " \u2014 " + items
    size = 8
    while text_w(d, rest, sans(size)) > (W - M - 8) - lx and size > 6:
        size -= 0.5
    draw_tracked(d, lx, y + 3, rest, sans(size), INK)
    return field_counts


def timeline(d, y):
    d.rectangle([M, y, W - M, y + 38], fill=NAVY_DK)
    slot_w = CW / len(TIMELINE)
    for i, (when, what) in enumerate(TIMELINE):
        cx = M + i * slot_w + 7
        draw_tracked(d, cx, y + 4, when, sans_b(8), GOLD, tracking=0)
        lines = wrap(d, what, sans(8), slot_w - 12)
        assert len(lines) <= 2, (when, lines)
        draw_wrapped(d, cx, y + 16, what, sans(8), (216, 221, 232),
                     slot_w - 12, 10, max_lines=2)
        if i:
            d.line([(M + i * slot_w, y + 5), (M + i * slot_w, y + 33)],
                   fill=(52, 78, 122), width=1)


REGION_SHORT = {"MIDDLE EAST": "MIDEAST"}


def panel(d, idx, x, y, w):
    region, field, headline, deck, source, scene, _tax = PANELS[idx]
    num = idx + 1
    SCENES[scene](d, x, y, w, 32)
    d.rectangle([x, y, x + 20, y + 15], fill=RED)
    s = str(num)
    f = sans_b(10)
    d.text((x + 10 - d.textlength(s, font=f) / 2, y + 2), s, font=f,
           fill=PAPER_LT)
    draw_tracked(d, x, y + 37,
                 "%s \u00b7 %s" % (REGION_SHORT.get(region, region),
                                    field),
                 sans_b(8), NAVY)
    sw = text_w(d, source, sans_b(7))
    draw_tracked(d, x + w - sw, y + 38, source, sans_b(7), INK_SOFT)
    hl = wrap(d, headline, serif_b(13), w)
    assert len(hl) <= 3, (num, hl)
    draw_wrapped(d, x, y + 50, headline, serif_b(13), INK, w, 15,
                 max_lines=3)
    dl = wrap(d, deck, sans(10), w)
    assert len(dl) <= 2, (num, dl)
    draw_wrapped(d, x, y + 98, deck, sans(10), INK, w, 12, max_lines=2)


def panels_grid(d, y):
    col_w = CW // 4
    row_h = 126
    for idx in range(16):
        cx = M + (idx % 4) * col_w
        cy = y + (idx // 4) * row_h
        panel(d, idx, cx + 4, cy + 2, col_w - 12)
        if idx % 4 != 3:
            d.line([(cx + col_w - 2, cy + 6), (cx + col_w - 2,
                    cy + row_h - 6)], fill=HAIR, width=1)
        if idx // 4 != 3:
            d.line([(cx + 6, cy + row_h - 2), (cx + col_w - 6,
                    cy + row_h - 2)], fill=HAIR, width=1)


def numbers_row(d, y):
    col_w = CW / len(NUMBERS)
    for i, (num, cap) in enumerate(NUMBERS):
        cx = M + i * col_w + 4
        d.text((cx, y), num, font=serif_b(20), fill=INK)
        d.text((cx, y + 24), cap, font=sans(8), fill=INK_SOFT)
        if i:
            d.line([(M + i * col_w - 2, y + 2),
                    (M + i * col_w - 2, y + 30)], fill=HAIR, width=1)


def bottom(d, y):
    lx, lw = M, 300
    draw_tracked(d, lx, y, "WHERE IT HAPPENED", sans_b(11), INK,
                 tracking=1)
    draw_map(d, lx, y + 16, lw, 118)
    draw_wrapped(d, lx, y + 140,
                 "Red pins: the 16 drawn stories. Pin 4 (Voyager 1) is "
                 "in deep space, off the map.",
                 sans(8), INK_SOFT, lw, 10)
    # Legend: a colour dot per region, matching the strip up top.
    f_leg = sans(7.5)
    names = [(r, REGION_SHORT.get(r, r)) for r in REGIONS]
    total_w = sum(8 + text_w(d, nm, f_leg) + 3 for _r, nm in names) - 3
    assert total_w <= lw, total_w
    cx = lx
    for r, nm in names:
        d.ellipse([cx, y + 165, cx + 5, y + 170], fill=REGION_COLORS[r])
        cx = draw_tracked(d, cx + 8, y + 163, nm, f_leg, INK) + 3
    # How-sure line: what the panel tags mean.
    hx = draw_tracked(d, lx, y + 176, "HOW SURE", sans_b(8), RED)
    draw_tracked(d, hx, y + 176,
                 " \u2014 [CONFIRMED] checked in 2+ reports",
                 sans(8), INK)
    rx = M + 322
    rw = W - M - rx
    draw_tracked(d, rx, y, "ALSO ON WEDNESDAY \u2014 %d MORE STORIES"
                 % len(BRIEFS), sans_b(12), RED, tracking=1)
    rule(d, y + 15, x0=rx, x1=W - M, fill=INK, wdt=1)
    col_w = rw / 3
    per_col = (len(BRIEFS) + 2) // 3
    step = 11.9 if per_col <= 13 else 11.4
    for i, (text, _region, _fld) in enumerate(BRIEFS):
        cx = rx + (i // per_col) * col_w
        cy = y + 23 + (i % per_col) * step
        num = 17 + i
        draw_tracked(d, cx, cy, "%d" % num, sans_b(8), NAVY)
        tw = text_w(d, text, sans(9))
        assert 15 + tw <= col_w - 4, (num, text, tw)
        draw_tracked(d, cx + 15, cy, text, sans(9), INK)


def date_check(d, y):
    d.rectangle([M, y, W - M, y + 48], outline=INK, width=2)
    draw_tracked(d, M + 10, y + 6, "DATE CHECK", sans_b(9), RED)
    d.text((M + 10, y + 19), "left out,", font=sans(8), fill=INK_SOFT)
    d.text((M + 10, y + 29), "and why", font=sans(8), fill=INK_SOFT)
    col_x = [M + 92, M + 92 + (CW - 102) // 2]
    col_w = (CW - 102) // 2 - 8
    for i, item in enumerate(DATE_CHECK):
        cx = col_x[i // 4]
        cy = y + 5 + (i % 4) * 10.5
        assert text_w(d, item, sans(8)) <= col_w, item
        d.text((cx, cy), item, font=sans(8), fill=INK)


def footer(d):
    rule(d, 1000, wdt=1)
    draw_centered(d, W // 2, 1005,
                  "Sources: AP \u00b7 Reuters \u00b7 AFP \u00b7 Al Jazeera "
                  "\u00b7 BBC \u00b7 AAP \u00b7 NASA \u00b7 WHO \u00b7 IMD "
                  "\u00b7 Amnesty \u00b7 GFZ \u00b7 EMSC \u00b7 Kyiv "
                  "Independent. [CLAIM] marks one side's account, not "
                  "independently confirmed.",
                  sans(8), INK_SOFT)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    total, region_counts = masthead(d)
    assert total == len(PANELS) + len(BRIEFS), total
    assert region_strip(d, 124, region_counts) == total
    field_strip(d, 146)
    timeline(d, 166)
    panels_grid(d, 210)
    numbers_row(d, 722)
    bottom(d, 762)
    date_check(d, 948)
    footer(d)
    img.save("artwork.png", optimize=True)
    print("wrote artwork.png", img.size)


if __name__ == "__main__":
    main()
