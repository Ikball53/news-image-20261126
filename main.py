#!/usr/bin/env python3
"""news-image-20261126 v2 — deterministic PIL front page renderer.

Draws the full 1024x1024 front page from the 36 verified 26-Nov stories:
header, headline strip, 15 illustrated cards (5x3), schematic world map
with region dots, UTC day-parts strip, 21-story text list, date-check
strip and ticker footer. Stdlib + PIL only, no network, deterministic.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
NAVY = (16, 32, 62)
NAVY2 = (24, 48, 88)
CREAM = (250, 246, 236)
PAPER = (255, 253, 247)
INK = (18, 24, 38)
RED = (178, 34, 34)
GOLD = (198, 142, 38)
BLUE = (43, 108, 163)
TEAL = (32, 128, 118)
GREY = (96, 102, 116)
LIGHT = (232, 228, 218)
MAPBG = (214, 230, 238)


def font(size, bold=False):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_one(draw, text, fnt, max_w):
    """Truncate a single line with an ellipsis so it fits max_w."""
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    while text and draw.textlength(text + "...", font=fnt) > max_w:
        text = text[:-1]
    return text + "..."


def card_art(d, idx, x0, y0, w, h):
    """Small flat illustration per card, drawn in the card's art band."""
    cx, cy = x0 + w // 2, y0 + h // 2
    if idx == 0:  # tariffs: rising bars + %
        for i, bh in enumerate((18, 30, 44)):
            bx = cx - 42 + i * 30
            d.rectangle([bx, cy + 22 - bh, bx + 20, cy + 22], fill=NAVY2)
        d.text((cx + 26, cy - 26), "%", font=font(30, True), fill=RED)
    elif idx == 1:  # tanker fire: tank + flame
        d.rounded_rectangle([cx - 52, cy - 6, cx + 52, cy + 18], 8, fill=NAVY2)
        d.ellipse([cx - 52, cy - 6, cx - 28, cy + 18], fill=NAVY2)
        d.polygon([(cx - 8, cy - 8), (cx + 2, cy - 30), (cx + 12, cy - 8)],
                  fill=GOLD)
        d.polygon([(cx + 2, cy - 6), (cx + 10, cy - 22), (cx + 18, cy - 6)],
                  fill=RED)
        d.ellipse([cx - 44, cy + 18, cx - 32, cy + 30], fill=INK)
        d.ellipse([cx + 32, cy + 18, cx + 44, cy + 30], fill=INK)
    elif idx == 2:  # parade balloon
        d.ellipse([cx - 34, cy - 30, cx + 34, cy + 16], fill=RED)
        d.polygon([(cx - 10, cy + 14), (cx + 10, cy + 14), (cx, cy + 26)],
                  fill=RED)
        d.line([cx, cy + 26, cx, cy + 34], fill=INK, width=2)
        for dx, dy, c in ((-52, -18, GOLD), (52, -20, BLUE), (-58, 8, BLUE),
                          (58, 6, GOLD)):
            d.ellipse([cx + dx - 3, cy + dy - 3, cx + dx + 3, cy + dy + 3],
                      fill=c)
    elif idx == 3:  # refinery towers
        for bx, tw in ((-48, 16), (-16, 22), (18, 16)):
            d.rectangle([cx + bx, cy - 26, cx + bx + tw, cy + 26], fill=NAVY2)
        d.polygon([(cx + 34, cy - 26), (cx + 42, cy - 30), (cx + 50, cy - 26)],
                  fill=GOLD)
        d.ellipse([cx + 36, cy - 34, cx + 48, cy - 24], fill=RED)
    elif idx == 4:  # jets
        for jx, jy in ((-38, -8), (8, 8)):
            d.polygon([(jx + cx - 26, jy + cy), (jx + cx + 26, jy + cy + 4),
                       (jx + cx - 26, jy + cy + 8)], fill=NAVY2)
            d.polygon([(jx + cx - 4, jy + cy - 12), (jx + cx + 6, jy + cy),
                       (jx + cx - 4, jy + cy + 8)], fill=NAVY2)
        d.text((cx - 8, cy - 30), "x5", font=font(15, True), fill=RED)
    elif idx == 5:  # guitar
        d.ellipse([cx - 26, cy - 4, cx + 18, cy + 30], fill=GOLD)
        d.ellipse([cx - 8, cy + 8, cx + 4, cy + 20], fill=NAVY)
        d.rectangle([cx - 2, cy - 32, cx + 8, cy + 6], fill=NAVY2)
        d.ellipse([cx - 4, cy - 38, cx + 10, cy - 26], fill=NAVY2)
    elif idx == 6:  # crown
        d.polygon([(cx - 40, cy + 18), (cx - 40, cy - 12), (cx - 20, cy + 2),
                   (cx, cy - 22), (cx + 20, cy + 2), (cx + 40, cy - 12),
                   (cx + 40, cy + 18)], fill=GOLD)
        d.rectangle([cx - 40, cy + 18, cx + 40, cy + 26], fill=NAVY2)
        d.ellipse([cx - 4, cy - 6, cx + 4, cy + 2], fill=RED)
    elif idx == 7:  # chess board + piece
        for r in range(4):
            for c in range(4):
                if (r + c) % 2 == 0:
                    d.rectangle([cx - 36 + c * 18, cy - 28 + r * 14,
                                 cx - 18 + c * 18, cy - 14 + r * 14],
                                fill=NAVY2)
        d.ellipse([cx - 14, cy - 40, cx + 14, cy - 14], fill=RED)
        d.rectangle([cx - 18, cy - 16, cx + 18, cy - 8], fill=RED)
    elif idx == 8:  # football + goal
        d.rectangle([cx - 52, cy - 22, cx + 52, cy + 26], outline=NAVY2,
                    width=3)
        d.ellipse([cx - 18, cy - 2, cx + 18, cy + 26], fill=INK)
        d.ellipse([cx - 6, cy + 6, cx + 6, cy + 18], fill=PAPER)
        d.text((cx - 52, cy - 34), "3-0", font=font(15, True), fill=RED)
    elif idx == 9:  # satellite
        d.rectangle([cx - 30, cy - 8, cx - 8, cy + 8], fill=BLUE)
        d.rectangle([cx + 8, cy - 8, cx + 30, cy + 8], fill=BLUE)
        d.rectangle([cx - 8, cy - 10, cx + 8, cy + 10], fill=NAVY2)
        d.line([cx + 14, cy - 10, cx + 34, cy - 30], fill=GOLD, width=3)
        for dx, dy in ((-48, -26), (48, 22), (-40, 26), (44, -28)):
            d.ellipse([cx + dx - 2, cy + dy - 2, cx + dx + 2, cy + dy + 2],
                      fill=GOLD)
    elif idx == 10:  # astronaut helmet
        d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=PAPER,
                  outline=NAVY2, width=3)
        d.ellipse([cx - 18, cy - 14, cx + 18, cy + 14], fill=NAVY2)
        d.ellipse([cx - 10, cy - 8, cx - 2, cy + 0], fill=PAPER)
        d.ellipse([cx + 4, cy - 8, cx + 12, cy + 0], fill=PAPER)
        for dx, dy in ((-48, -24), (48, -20), (-52, 14), (50, 18)):
            d.ellipse([cx + dx - 2, cy + dy - 2, cx + dx + 2, cy + dy + 2],
                      fill=GOLD)
    elif idx == 11:  # memorial candle
        d.rectangle([cx - 8, cy - 8, cx + 8, cy + 26], fill=PAPER,
                    outline=NAVY2, width=2)
        d.polygon([(cx, cy - 30), (cx - 8, cy - 12), (cx + 8, cy - 12)],
                  fill=GOLD)
        d.rectangle([cx - 22, cy + 26, cx + 22, cy + 32], fill=NAVY2)
        d.text((cx + 30, cy - 28), "18", font=font(13, True), fill=RED)
    elif idx == 12:  # protest placards
        for px, py in ((-34, -6), (0, -14), (34, -4)):
            d.line([cx + px, cy + py + 12, cx + px, cy + 34], fill=INK,
                   width=3)
            d.rectangle([cx + px - 16, cy + py - 12, cx + px + 16,
                         cy + py + 12], fill=RED if px else NAVY2)
    elif idx == 13:  # plane over waves
        d.polygon([(cx - 40, cy - 12), (cx + 34, cy - 12), (cx + 44, cy - 6),
                   (cx - 30, cy - 2)], fill=NAVY2)
        d.polygon([(cx - 6, cy - 26), (cx + 6, cy - 12), (cx - 6, cy - 2)],
                  fill=NAVY2)
        for wy in (14, 24):
            d.arc([cx - 52, cy + wy - 8, cx - 12, cy + wy + 8], 0, 180,
                  fill=BLUE, width=3)
            d.arc([cx + 12, cy + wy - 8, cx + 52, cy + wy + 8], 0, 180,
                  fill=BLUE, width=3)
    else:  # EU clash: circle of stars, split
        for k in range(8):
            import math
            a = math.pi * 2 * k / 8 - math.pi / 2
            sx, sy = cx + 30 * math.cos(a), cy + 30 * math.sin(a)
            d.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=GOLD)
        d.line([cx, cy - 34, cx, cy + 34], fill=RED, width=4)
        d.text((cx - 26, cy - 8), "45", font=font(16, True), fill=NAVY2)


CARDS = [
    ("US TARIFFS",
     "US proposes new tariffs on 14 partners incl. China, EU, Japan, India"),
    ("CAIRO TANKER FIRE",
     "Fuel tanker fire kills 31, injures 21 on Cairo ring road"),
    ("MACY'S PARADE POSTPONED",
     "100th parade moved to Sat 28 Nov, first weather postponement in 100 years"),
    ("HOUTHIS HIT SAUDI REFINERY",
     "Ras Tanura refinery attacked, oil prices climb"),
    ("UKRAINE STRIKES AIRBASE",
     "Five jets damaged at Savasleyka airbase, Russia"),
    ("ANDY TAYLOR DIES",
     "Duran Duran guitarist and songwriter dies aged 65"),
    ("MISS UNIVERSE",
     "Jennifer Barreto of Puerto Rico crowned Miss Universe 2026, first married mother to win"),
    ("GUKESH\u2013SINDAROV GAME 3",
     "World Chess Championship 2026, Game 3 played today"),
    ("LIVERPOOL BEAT BRUGGE 3-0",
     "Isak brace, Wirtz on target, Champions League"),
    ("SPACEX 1M SATELLITES",
     "US regulators approve plan for a million data satellites"),
    ("PAKISTANI ASTRONAUT",
     "Muhammad Zeeshan Ali, first foreigner aboard China's Tiangong station"),
    ("MUMBAI REMEMBERS",
     "India marks 18 years since 26/11 attacks; Constitution Day"),
    ("BANGLADESH WAGE PROTESTS",
     "Minimum-wage hike falls short, fresh protests"),
    ("PLANE CRASH",
     "Six dead, incl. two children, off Mississippi coast"),
    ("EU LEADERS CLASH",
     "Brussels split over 45bn euro Ukraine loan and next budget"),
]

MORE = [
    "North Korea expels Swiss diplomat in sanctions row",
    "Kim calls for wider deployment of tactical nuclear weapons",
    "Russia hits two grain ships near Odesa ports",
    "Iran claims mine strikes on ships near Hormuz; oil rises",
    "Indonesia: 13 miners trapped in flooded gold mine near Bogor",
    "Hong Kong renovation blaze killed 168",
    "India asks Netflix not to air Pakistani show",
    "Congress party sues Meta in India over blocked posts",
    "Nasdaq nears bear market as AI sell-off deepens",
    "Birthright citizenship order blocked by a second judge",
    "Puerto Rico court cancels Luma power contract, 5-4",
    "London Tube strike disrupts travel Thursday and Friday",
    "Spain heads to snap election on Sunday",
    "New UK-EU treaty has 10-year termination clause",
    "Murmansk governor detained in corruption probe",
    "Kenyan cult leader convicted of new charges",
    "Zambia bans protest over term-limit push",
    "Lebanon to open second airport next month",
    "ISIL suicide attack kills two in Hasakah, Syria",
    "Pitt and Jolie settle Miraval winery fight",
    "BBC and Netflix launch CBeebies streaming hub",
]

# (label, x, y) dots on the schematic map panel (panel coords, 1024 wide)
DOTS = [
    ("N. AMERICA", 168, 30), ("EUROPE", 492, 26), ("MID EAST", 575, 30),
    ("AFRICA", 498, 70), ("S. ASIA", 648, 56), ("E. ASIA", 756, 34),
    ("SE ASIA", 716, 64),
]


def draw_map(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=MAPBG)
    d.text((x0 + 10, y0 + 6),
           "WORLD MAP \u2014 WHERE THE NEWS HAPPENED  \u00b7  SPORT, CULTURE & SPACE ARE WORLDWIDE",
           font=font(12, True), fill=NAVY)
    # Schematic continents (simple flat blobs, kept inside the panel)
    cx0, cy0 = x0, y0 + 20
    d.polygon([(cx0 + 60, cy0 + 4), (cx0 + 190, cy0 + 0), (cx0 + 208, cy0 + 22),
               (cx0 + 150, cy0 + 42), (cx0 + 112, cy0 + 62), (cx0 + 70, cy0 + 38)],
              fill=(168, 196, 172))  # N America
    d.polygon([(cx0 + 168, cy0 + 64), (cx0 + 206, cy0 + 64), (cx0 + 198, cy0 + 92),
               (cx0 + 176, cy0 + 88)], fill=(168, 196, 172))  # S America
    d.polygon([(cx0 + 440, cy0 + 4), (cx0 + 500, cy0 + 0), (cx0 + 512, cy0 + 24),
               (cx0 + 470, cy0 + 36), (cx0 + 442, cy0 + 22)],
              fill=(168, 196, 172))  # Europe
    d.polygon([(cx0 + 450, cy0 + 42), (cx0 + 530, cy0 + 40), (cx0 + 545, cy0 + 78),
               (cx0 + 505, cy0 + 100), (cx0 + 468, cy0 + 80)],
              fill=(168, 196, 172))  # Africa
    d.polygon([(cx0 + 560, cy0 + 2), (cx0 + 820, cy0 + 0), (cx0 + 850, cy0 + 34),
               (cx0 + 780, cy0 + 56), (cx0 + 700, cy0 + 48), (cx0 + 640, cy0 + 58),
               (cx0 + 580, cy0 + 36)], fill=(168, 196, 172))  # Asia
    d.polygon([(cx0 + 800, cy0 + 80), (cx0 + 850, cy0 + 78), (cx0 + 852, cy0 + 96),
               (cx0 + 806, cy0 + 98)], fill=(168, 196, 172))  # Australia
    for label, dx, dy in DOTS:
        d.ellipse([x0 + dx - 6, y0 + 20 + dy - 6, x0 + dx + 6, y0 + 20 + dy + 6],
                  fill=RED, outline=PAPER, width=2)
        d.text((x0 + dx + 9, y0 + 20 + dy - 6), label, font=font(10, True),
               fill=NAVY)


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # --- Header ---
    d.rectangle([0, 0, W, 86], fill=NAVY)
    d.rectangle([0, 86, W, 90], fill=GOLD)
    d.text((24, 12), "WORLD IN ONE IMAGE", font=font(34, True), fill=PAPER)
    d.text((W - 24 - d.textlength("THE DAILY FRONT PAGE", font=font(16, True)),
            26), "THE DAILY FRONT PAGE", font=font(16, True), fill=GOLD)
    d.text((24, 56), "THURSDAY, 26 NOVEMBER 2026  \u00b7  36 STORIES  \u00b7  10 REGIONS",
           font=font(15, True), fill=PAPER)

    # --- Headline strip ---
    d.rectangle([0, 90, W, 128], fill=PAPER)
    d.text((24, 98),
           "Macy's parade postponed  \u00b7  Mumbai marks 18 years since 26/11  \u00b7  Gukesh\u2013Sindarov Game 3",
           font=font(16, True), fill=RED)
    d.line([0, 128, W, 128], fill=NAVY, width=2)

    # --- 15 cards, 5 x 3 grid ---
    gx, gy = 16, 136
    cw, ch, gap = 190, 160, 8
    for i, (head, sub) in enumerate(CARDS):
        r, c = divmod(i, 5)
        x0 = gx + c * (cw + gap)
        y0 = gy + r * (ch + gap)
        d.rounded_rectangle([x0, y0, x0 + cw, y0 + ch], 6, fill=PAPER,
                            outline=LIGHT, width=1)
        d.rectangle([x0, y0, x0 + cw, y0 + 4], fill=RED)
        card_art(d, i, x0, y0 + 8, cw, 62)
        d.line([x0 + 10, y0 + 74, x0 + cw - 10, y0 + 74], fill=LIGHT, width=1)
        hl = wrap(d, head, font(13, True), cw - 16)
        ty = y0 + 80
        for ln in hl[:2]:
            d.text((x0 + 8, ty), ln, font=font(13, True), fill=NAVY)
            ty += 16
        sl = wrap(d, sub, font(10), cw - 16)
        for ln in sl[:3]:
            d.text((x0 + 8, ty), ln, font=font(10), fill=INK)
            ty += 13

    # --- World map strip ---
    my = gy + 3 * ch + 2 * gap + 12  # 644
    draw_map(d, 16, my, W - 32, 112)

    # --- UTC day-parts strip (no clock times) ---
    uy = my + 112 + 8
    parts = [("OVERNIGHT", "ASIA"), ("MORNING", "EUROPE"),
             ("MIDDAY", "AMERICAS"), ("EVENING", "WORLDWIDE")]
    pw = (W - 32) // 4
    d.text((16, uy), "THE DAY IN UTC — FOUR PARTS", font=font(12, True),
           fill=NAVY)
    for i, (a, b) in enumerate(parts):
        x0 = 16 + i * pw
        d.rounded_rectangle([x0, uy + 20, x0 + pw - 6, uy + 50], 5,
                            fill=NAVY2 if i % 2 == 0 else TEAL)
        d.text((x0 + 10, uy + 25), a, font=font(13, True), fill=PAPER)
        d.text((x0 + pw - 16 - d.textlength(b, font=font(12, True)), uy + 27),
               b, font=font(12, True), fill=GOLD)

    # --- The rest of the day: 21 more stories, 3 columns ---
    ry = uy + 58
    d.text((16, ry), "THE REST OF THE DAY \u2014 21 MORE STORIES",
           font=font(13, True), fill=NAVY)
    d.line([16, ry + 20, W - 16, ry + 20], fill=RED, width=2)
    colw = (W - 32 - 2 * 16) // 3
    for col in range(3):
        x0 = 16 + col * (colw + 16)
        for row in range(7):
            s = MORE[col * 7 + row]
            y = ry + 28 + row * 14
            d.text((x0, y), "\u2022", font=font(11, True), fill=RED)
            d.text((x0 + 12, y),
                   fit_one(d, s, font(9), colw - 14), font=font(9),
                   fill=INK)

    # --- Date-check strip ---
    dy = ry + 28 + 7 * 14 + 6
    d.rounded_rectangle([16, dy, W - 16, dy + 24], 5, fill=(232, 240, 232))
    d.text((28, dy + 5),
           "DATE CHECK \u2014 Thursday 26 November 2026 \u00b7 Stories verified against Reuters, BBC and One Turn reporting of 26 November 2026.",
           font=font(11, True), fill=NAVY)

    # --- Ticker footer ---
    fy = H - 34
    d.rectangle([0, fy, W, H], fill=NAVY)
    d.text((16, fy + 8),
           "Cairo fire 31 dead  \u00b7  US tariffs on 14 partners  \u00b7  Andy Taylor 65  \u00b7  SpaceX 1m satellites  \u00b7  Liverpool 3-0 Brugge",
           font=font(12, True), fill=PAPER)

    out = os.environ.get("MAKEFUN_OUTPUT_DIR") or (
        "/output" if os.path.isdir("/output") else os.getcwd())
    path = os.path.join(out, "entry.png")
    img.save(path, "PNG", optimize=True)
    print("saved", path)


if __name__ == "__main__":
    main()
