import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont("F", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("FB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
W, H = landscape(A3)
RED = (0.70, 0.18, 0.12)
c = canvas.Canvas(sys.argv[1], pagesize=(W, H))
c.setTitle("Таҳхона — нақшаҳои корӣ барои устоҳо")

# ---------------- geometry (metres, outer corner = 0,0) ----------------
L, D = 13.0, 8.0          # outer size
TE, TI = 0.4, 0.2         # exterior / interior wall thickness
XD = 4.0                  # divider axis (left room 4 m, main room 9 m)
# stair (net box 3.5 x 2.0 against front wall, right of divider)
SX0, SY0 = XD + TI / 2, TE            # 4.10, 0.40
SL, SW = 3.5, 2.0
FW, GAP = 0.9, 0.2
NR, RISE, TREAD = 16, 2750 / 16, 0.26  # 16 x 171.9 mm
NT = 7                                 # treads per flight
START = 0.48                           # floor landing length at divider
LAND = SL - START - NT * TREAD         # mid landing 1.20
COLS = [(XD, 4.0), (XD + 4.5, 4.0)]
DOOR_DIV = (4.4, 5.3)                  # door in divider (y range)
WIN = [(6.3, 7.2), (9.3, 10.1)]        # windows in back wall (x range)
DOOR_BACK = (7.6, 8.4)                 # door in back wall ("дар: 4 м")


def frame(title, sheet, scale):
    c.setLineWidth(0.6); c.setStrokeGray(0)
    c.rect(10 * mm, 10 * mm, W - 20 * mm, H - 20 * mm)
    c.rect(W - 190 * mm, 10 * mm, 180 * mm, 24 * mm)
    c.setFont("FB", 11); c.setFillGray(0)
    c.drawString(W - 186 * mm, 27 * mm, "Хонаи истиқоматӣ — ТАҲХОНА (аз модели 3D)")
    c.setFont("F", 9)
    c.drawString(W - 186 * mm, 21 * mm, title)
    c.drawString(W - 186 * mm, 15 * mm, f"Миқёс {scale} · андозаҳо бо мм · сатҳҳо бо м")
    c.setFont("FB", 14); c.drawRightString(W - 14 * mm, 15 * mm, f"Варақ {sheet}/4")
    c.setFont("F", 7.5); c.setFillColorRGB(*RED)
    c.drawString(14 * mm, 14 * mm, "Лоиҳаи консептуалӣ. Арматура, плита, шифт ва сейсмикаро (8–9 балл) "
                 "муҳандиси конструктор бояд ҳисоб ва имзо кунад. Андозаҳоро дар ҷой санҷед.")
    c.setFillGray(0)


class View:
    def __init__(s, ox, oy, scale):
        s.ox, s.oy, s.k = ox, oy, 1000 / scale * mm  # page units per metre

    def p(s, x, y):
        return s.ox + x * s.k, s.oy + y * s.k

    def rect(s, x, y, w, h, fill=None, stroke=True, lw=0.5):
        X, Y = s.p(x, y)
        if fill is not None:
            c.setFillGray(fill) if isinstance(fill, float) else c.setFillColorRGB(*fill)
        c.setLineWidth(lw)
        c.rect(X, Y, w * s.k, h * s.k, stroke=1 if stroke else 0, fill=1 if fill is not None else 0)
        c.setFillGray(0)

    def line(s, x1, y1, x2, y2, lw=0.4, gray=0, dash=None):
        c.setLineWidth(lw); c.setStrokeGray(gray)
        c.setDash(list(dash)) if dash else c.setDash()
        c.line(*s.p(x1, y1), *s.p(x2, y2))
        c.setDash(); c.setStrokeGray(0)

    def text(s, x, y, t, size=8, bold=False, center=True, color=None):
        X, Y = s.p(x, y)
        c.setFont("FB" if bold else "F", size)
        if color: c.setFillColorRGB(*color)
        (c.drawCentredString if center else c.drawString)(X, Y, t)
        c.setFillGray(0)

    def dimh(s, x1, x2, y, t=None, size=7):
        """horizontal dimension at height y (metres)"""
        X1, Y = s.p(x1, y); X2, _ = s.p(x2, y)
        c.setLineWidth(0.3); c.line(X1 - 2 * mm, Y, X2 + 2 * mm, Y)
        for X in (X1, X2):
            c.line(X - 1.2 * mm, Y - 1.2 * mm, X + 1.2 * mm, Y + 1.2 * mm)
            c.line(X, Y - 2 * mm, X, Y + 2 * mm)
        c.setFont("F", size)
        c.drawCentredString((X1 + X2) / 2, Y + 1.2 * mm, t or f"{round((x2 - x1) * 1000):d}")

    def dimv(s, y1, y2, x, t=None, size=7):
        X, Y1 = s.p(x, y1); _, Y2 = s.p(x, y2)
        c.setLineWidth(0.3); c.line(X, Y1 - 2 * mm, X, Y2 + 2 * mm)
        for Y in (Y1, Y2):
            c.line(X - 1.2 * mm, Y - 1.2 * mm, X + 1.2 * mm, Y + 1.2 * mm)
            c.line(X - 2 * mm, Y, X + 2 * mm, Y)
        c.saveState(); c.translate(X - 1.2 * mm, (Y1 + Y2) / 2); c.rotate(90)
        c.setFont("F", size); c.drawCentredString(0, 0, t or f"{round((y2 - y1) * 1000):d}")
        c.restoreState()

    def level(s, x, y, t, left=False):
        X, Y = s.p(x, y)
        c.setLineWidth(0.4)
        p = c.beginPath(); p.moveTo(X, Y); p.lineTo(X - 1.5 * mm, Y + 2.2 * mm); p.lineTo(X + 1.5 * mm, Y + 2.2 * mm); p.close()
        c.drawPath(p, stroke=1, fill=0)
        c.line(X, Y + 2.2 * mm, X + (-14 if left else 14) * mm, Y + 2.2 * mm)
        c.setFont("F", 7.5)
        (c.drawRightString if left else c.drawString)(X + (-1 if left else 1) * mm, Y + 3.2 * mm, t)

    def arrow(s, pts, lw=0.7):
        c.setLineWidth(lw)
        P = [s.p(*q) for q in pts]
        path = c.beginPath(); path.moveTo(*P[0])
        for q in P[1:]: path.lineTo(*q)
        c.drawPath(path, stroke=1, fill=0)
        c.circle(*P[0], 0.8 * mm, stroke=0, fill=1)
        (x1, y1), (x2, y2) = P[-2], P[-1]
        import math
        a = math.atan2(y2 - y1, x2 - x1)
        hl, hw = 2.6 * mm, 1.1 * mm
        bx, by = x2 - hl * math.cos(a), y2 - hl * math.sin(a)
        path = c.beginPath(); path.moveTo(x2, y2)
        path.lineTo(bx + hw * math.sin(a), by - hw * math.cos(a)); path.lineTo(bx - hw * math.sin(a), by + hw * math.cos(a)); path.close()
        c.drawPath(path, stroke=0, fill=1)


def axis_bubble(X, Y, t):
    c.setStrokeColorRGB(*RED); c.setFillColorRGB(1, 1, 1); c.setLineWidth(0.5)
    c.circle(X, Y, 3.2 * mm, stroke=1, fill=1)
    c.setFillColorRGB(*RED); c.setFont("FB", 8); c.drawCentredString(X, Y - 1.1 * mm, t)
    c.setFillGray(0); c.setStrokeGray(0)


def stair_plan(v, fine=False):
    """U-stair in plan: flight 1 (room side) goes +x, flight 2 (wall side) goes -x."""
    v.rect(SX0, SY0, SL, SW, fill=0.93, stroke=False)
    yA = SY0 + FW + GAP   # flight 1 (outer, room side)  y in [yA, yA+FW]
    yB = SY0              # flight 2 (against wall)      y in [yB, yB+FW]
    x0 = SX0 + START
    for i in range(NT + 1):
        x = x0 + i * TREAD
        v.line(x, yA, x, yA + FW, lw=0.45)
        v.line(x, yB, x, yB + FW, lw=0.45)
    v.rect(SX0, yB + FW, START + NT * TREAD, GAP, fill=0.6, stroke=False)   # central wall / gap
    v.line(SX0 + START + NT * TREAD, SY0, SX0 + START + NT * TREAD, SY0 + SW, lw=0.6)  # landing edge
    ym1, ym2 = yA + FW / 2, yB + FW / 2
    xe = SX0 + START + NT * TREAD + LAND / 2
    v.arrow([(x0 - 0.15, ym1), (xe, ym1), (xe, ym2), (x0 - 0.2, ym2)])
    sz = 9 if fine else 6.5
    if fine:
        for i in range(NT):   # step numbers 1..16
            v.text(x0 + (i + 0.5) * TREAD, ym1 + 0.2, str(i + 1), size=6.5)
            v.text(x0 + (NT - 1 - i + 0.5) * TREAD, ym2 - 0.32, str(NT + 2 + i), size=6.5)
        v.text(xe, ym1 + 0.2, "8", size=6.5)
        v.text(x0 - 0.24, ym2 - 0.32, "16", size=6.5)
        v.text(x0 - 0.24, ym2 + 0.12, "+1,750", size=6)
        v.text(x0 - 0.24, ym1 - 0.35, "−1,000", size=6.5)
    v.text(x0 + 1.0, ym1 + (0.22 if not fine else -0.33), "боло ↑", size=sz, bold=True)
    v.text(xe, SY0 + SW / 2 - 0.1, "майдонча", size=sz - 1)


# =============================== SHEET 1: PLAN ===============================
frame("Варақ 1 — Нақшаи таҳхона бо андозаҳо", 1, "1:50")
v = View(60 * mm, 80 * mm, 50)
# walls (solid fill)
v.rect(0, 0, L, D, fill=0.18, stroke=False)
v.rect(TE, TE, XD - TI / 2 - TE, D - 2 * TE, fill=(0.86, 0.86, 0.84), stroke=False)   # left room
v.rect(XD + TI / 2, TE, L - TE - XD - TI / 2, D - 2 * TE, fill=(0.96, 0.94, 0.88), stroke=False)  # main
# tiles in main room (light grid 600)
c.setStrokeGray(0.85)
x = XD + TI / 2
while x < L - TE: v.line(x, TE, x, D - TE, lw=0.2, gray=0.82); x += 0.6
y = TE
while y < D - TE: v.line(XD + TI / 2, y, L - TE, y, lw=0.2, gray=0.82); y += 0.6
# openings
v.rect(XD - TI / 2 - 0.01, DOOR_DIV[0], TI + 0.02, DOOR_DIV[1] - DOOR_DIV[0], fill=1.0, stroke=False)
X, Y = v.p(XD + TI / 2, DOOR_DIV[0]); r = (DOOR_DIV[1] - DOOR_DIV[0]) * v.k
c.setLineWidth(0.4); c.line(X, Y, X + r, Y); c.setDash(2, 1.5); c.arc(X - r, Y - r, X + r, Y + r, 0, 90); c.setDash()
for a, b in WIN:
    v.rect(a, D - TE - 0.01, b - a, TE + 0.02, fill=1.0, stroke=True, lw=0.4)
    v.line(a, D - TE / 2, b, D - TE / 2, lw=0.4)
v.rect(DOOR_BACK[0], D - TE - 0.01, DOOR_BACK[1] - DOOR_BACK[0], TE + 0.02, fill=1.0, stroke=False)
X, Y = v.p(DOOR_BACK[1], D - TE); r = (DOOR_BACK[1] - DOOR_BACK[0]) * v.k
c.line(X, Y, X, Y - r); c.setDash(2, 1.5); c.arc(X - r, Y - r, X + r, Y + r, 180, 90); c.setDash()
# columns
for cx, cy in COLS:
    v.rect(cx - 0.2, cy - 0.2, 0.4, 0.4, fill=0.0, stroke=False)
# stair
stair_plan(v)
v.line(SX0, SY0 + SW, SX0 + SL, SY0 + SW, lw=0.3, dash=(3, 2))
v.text(SX0 + SL + 0.08, SY0 + SW + 0.12, "сӯрохии шифт 3500×2000", size=6.5, center=False)
# axes
for ax, t in ((0.2, "1"), (XD, "2"), (XD + 4.5, "3"), (L - 0.2, "4")):
    v.line(ax, -1.9, ax, D + 1.9, lw=0.25, dash=(6, 2, 1, 2))
    X, Y = v.p(ax, D + 2.25); axis_bubble(X, Y, t)
for ay, t in ((D - 0.2, "А"), (4.0, "Б"), (0.2, "В")):
    v.line(-2.2, ay, L + 0.6, ay, lw=0.25, dash=(6, 2, 1, 2))
    X, Y = v.p(-2.55, ay); axis_bubble(X, Y, t)
c.setStrokeGray(0)
# room labels
v.text((TE + XD) / 2, 5.2, "Ҳуҷраи 1 (анбор)", size=9, bold=True)
v.text((TE + XD) / 2, 4.75, "тоза 3500 × 7200", size=7.5)
v.text((TE + XD) / 2, 4.35, "S = 25,2 м² · h = 2000", size=7.5, color=RED)
v.text((TE + XD) / 2, 3.55, "фарш −0,500", size=7.5)
v.text(9.0, 5.6, "Ҳуҷраи 2 (асосӣ)", size=9, bold=True)
v.text(9.0, 5.15, "тоза 8500 × 7200 (бо зина)", size=7.5)
v.text(9.0, 4.75, "S = 61,2 м² · h = 2500", size=7.5, color=RED)
v.text(9.0, 4.35, "фарш −1,000 · кошин 600×600", size=7.5)
v.text(XD + 0.55, (DOOR_DIV[0] + DOOR_DIV[1]) / 2 - 0.05, "Д-1 900", size=6.5)
v.text(XD + 0.75, DOOR_DIV[0] - 0.3, "зинача 500 ↓", size=6.5, color=RED)
v.text((DOOR_BACK[0] + DOOR_BACK[1]) / 2, D - TE - 0.95, "Д-2 800", size=6.5)
for i, (a, b) in enumerate(WIN, 1):
    v.text((a + b) / 2, D - TE - 0.35, f"Т-{i}", size=6.5)
v.text(COLS[1][0] + 0.25, COLS[1][1] - 0.5, "сутун 400×400", size=6.5, center=False)
# --- dimensions ---
# bottom: overall + axes + stair
v.dimh(0, L, -1.5, "13000")
v.dimh(0, XD, -1.0); v.dimh(XD, L, -1.0, "9000")
v.dimh(0, TE, -0.5); v.dimh(TE, XD - TI / 2, -0.5); v.dimh(XD - TI / 2, SX0, -0.5)
v.dimh(SX0, SX0 + SL, -0.5); v.dimh(SX0 + SL, L - TE, -0.5); v.dimh(L - TE, L, -0.5)
# top: openings on back wall
yT = D + 0.5
pts = [XD + TI / 2, WIN[0][0], WIN[0][1], DOOR_BACK[0], DOOR_BACK[1], WIN[1][0], WIN[1][1], L - TE]
for a, b in zip(pts, pts[1:]): v.dimh(a, b, yT, size=6.5)
v.dimh(XD, XD + 4.5, D + 1.0, "4500"); v.dimh(XD + 4.5, L, D + 1.0, "4500")
# left: overall + walls
v.dimv(0, D, -1.6, "8000")
v.dimv(0, TE, -1.0); v.dimv(TE, D - TE, -1.0); v.dimv(D - TE, D, -1.0)
# right: stair + column + doors
xr = L + 1.0
v.dimv(0, TE, xr); v.dimv(TE, SY0 + SW, xr); v.dimv(SY0 + SW, 4.0, xr); v.dimv(4.0, D - TE, xr); v.dimv(D - TE, D, xr)
v.dimv(0, 4.0, L + 1.5, "4000"); v.dimv(4.0, D, L + 1.5, "4000")
# divider door dims inside left room
v.dimv(TE, DOOR_DIV[0], XD - 0.55, size=6.5); v.dimv(DOOR_DIV[0], DOOR_DIV[1], XD - 0.55, size=6.5)
v.dimv(DOOR_DIV[1], D - TE, XD - 0.55, size=6.5)
# section mark 1-1 (horizontal cut through flight 1)
ycut = SY0 + FW + GAP + FW / 2
for xx, side in ((-0.6, 1), (L + 0.6, -1)):
    X, Y = v.p(xx, ycut)
    c.setLineWidth(1.4); c.line(X, Y, X + side * 5 * mm, Y)
    c.line(X, Y, X, Y - 4 * mm); c.setFont("FB", 9); c.drawCentredString(X - side * 3 * mm, Y - 6 * mm, "1")
v.line(-0.4, ycut, L + 0.4, ycut, lw=0.3, dash=(8, 3))
# legend
c.setFont("FB", 8.5); c.drawString(14 * mm, 41 * mm, "Шартҳо:")
c.setFont("F", 7.2)
leg = ["Девори берунӣ — оҳану бетон 400", "Девори дохилӣ — 200",
       "Сутун 400×400 (дар кунҷҳо ва тирҳо низ)", "Д — дар, Т — тиреза (ҷадвал дар варақ 4)",
       "Андозаҳо аз тирҳо ва рӯи деворҳо, мм", "Тирҳои 1–4 ва А–В — тири сутунҳо",
       "1-1 — хати буриш (варақ 2)", "Зина 16 пиллакон, тафсилот — варақ 3"]
for i, t in enumerate(leg):
    c.drawString((14 + (i // 4) * 105) * mm, (36 - (i % 4) * 4.6) * mm, t)
c.showPage()

# ===================== SHEET 2: SECTION 1-1 + STAIR DETAIL =====================
frame("Варақ 2 — Буриши 1-1", 2, "1:50")
s = View(70 * mm, 150 * mm, 50)  # section: x along 13 m, y = level (m), 0 = ground
SLAB = 0.25; TOP = 1.5            # ceiling underside +1,500; floor-1 +1,750
# ground line
s.line(-1.2, 0, L + 1.2, 0, lw=0.8)
c.setFont("F", 7); X, Y = s.p(L + 0.6, 0.08); c.drawString(X, Y, "замин ±0,000")
# foundation plate -1.5..-1.0
s.rect(-0.1, -1.5, L + 0.2, 0.5, fill=0.55, stroke=True)
s.text(L / 2 + 1.5, -1.33, "плитаи таҳкурсӣ 500 (арматура — аз муҳандис)", size=7, color=(1, 1, 1))
s.rect(-0.1, -1.6, L + 0.2, 0.1, fill=0.8, stroke=True)
s.text(L + 0.35, -1.62, "бетони тайёрӣ 100", size=6.5, center=False)
# left room raised floor fill 500
s.rect(TE, -1.0, XD - TI / 2 - TE, 0.5, fill=(0.82, 0.76, 0.62), stroke=True)
s.text((TE + XD) / 2, -0.8, "хок/шағал + бетон 500", size=6.5)
# walls
for x0, w in ((0, TE), (L - TE, TE)):
    s.rect(x0, -1.0, w, TOP + 1.0, fill=0.18, stroke=False)
s.rect(XD - TI / 2, -0.5, TI, TOP + 0.5, fill=0.35, stroke=False)
s.rect(XD - TI / 2, -1.0, TI, 0.5, fill=0.35, stroke=False)
# ceiling slab with stair opening
s.rect(-0.1, TOP, SX0 + 0.1, SLAB, fill=0.35, stroke=False)
s.rect(SX0 + SL, TOP, L + 0.1 - SX0 - SL, SLAB, fill=0.35, stroke=False)
s.text(10.5, TOP + 0.45, "плитаи шифт 250 (+1,500…+1,750)", size=6.5)
s.text(SX0 + SL / 2, TOP + 0.45, "сӯрохӣ 3500", size=6.5, color=RED)
# stair flight 1 (cut, +x), going from -1.000 to landing at -1.000 + 8 risers
r = RISE / 1000
x0 = SX0 + START
yy = -1.0
pts = [(SX0, -1.0), (x0, -1.0)]
for i in range(NT):
    pts += [(x0 + i * TREAD, -1.0 + (i + 1) * r), (x0 + (i + 1) * TREAD, -1.0 + (i + 1) * r)]
land_y = -1.0 + 8 * r
pts += [(x0 + NT * TREAD, land_y), (SX0 + SL, land_y)]
c.setLineWidth(0.6)
path = c.beginPath(); path.moveTo(*s.p(*pts[0]))
for q in pts[1:]: path.lineTo(*s.p(*q))
# underside of flight and landing (thickness ~180)
th = 0.18
path.lineTo(*s.p(SX0 + SL, land_y - th)); path.lineTo(*s.p(x0 + NT * TREAD, land_y - th))
path.lineTo(*s.p(x0 + 0.15, -1.0)); path.close()
c.setFillGray(0.55); c.drawPath(path, stroke=1, fill=1); c.setFillGray(0)
# flight 2 (beyond, outline only, going -x up to +1.750)
c.setDash(2, 1.5); c.setLineWidth(0.4)
path = c.beginPath(); path.moveTo(*s.p(x0 + NT * TREAD, land_y))
for i in range(NT):
    xa = x0 + (NT - i) * TREAD
    path.lineTo(*s.p(xa, land_y + (i + 1) * r)); path.lineTo(*s.p(xa - TREAD, land_y + (i + 1) * r))
path.lineTo(*s.p(SX0, land_y + 8 * r))
c.drawPath(path, stroke=1, fill=0); c.setDash()
# handrail line
s.line(x0, -1.0 + 0.9, x0 + NT * TREAD, -1.0 + 0.9 + 7 * r, lw=0.5, gray=0.3)
s.text(x0 + 0.9, -1.0 + 0.9 + 4 * r + 0.15, "дастак h = 900", size=6.5)
# levels
s.level(L + 0.6, TOP + SLAB, "+1,750 фарши ошёнаи 1")
s.level(L + 0.6, TOP, "+1,500 зери шифт")
s.level(L + 0.6, -1.0, "−1,000 фарши ҳуҷраи 2")
s.level(L + 0.6, -1.5, "−1,500 зери плита")
s.level(1.0, -0.5, "−0,500 фарши ҳуҷраи 1")
s.level(SX0 + SL + 0.2, land_y, f"{land_y:+.3f}".replace(".", ",") + " майдонча")
# heights
s.dimv(-0.5, TOP, XD - 1.2, "h 2000")
s.dimv(-1.0, TOP, 10.8, "h 2500")
s.dimv(-1.5, TOP + SLAB, -1.0, "3250")
s.dimh(0, XD, -2.1); s.dimh(XD, L, -2.1, "9000")
s.dimh(x0, x0 + NT * TREAD, -2.5, f"7×260={NT * 260}"); s.dimh(x0 + NT * TREAD, SX0 + SL, -2.5)
s.dimh(SX0, x0, -2.5)
c.setFont("FB", 10); X, Y = s.p(0, 3.0); c.drawString(X, Y, "БУРИШИ 1-1  (1:50)")
c.setFont("F", 7); c.setFillColorRGB(*RED)
c.drawString(X, Y - 4.5 * mm, "Гидроизолятсия: аз берун ба девор ва зери плита (мастика/рулон) + дренажи атроф.")
c.setFillGray(0)

c.showPage()
frame("Варақ 3 — Нақшаи зина", 3, "1:25")
# stair detail plan 1:25
d = View(40 * mm, 90 * mm, 25)
off = (SX0 - 0.35, SY0 - 0.4)
class Shift(View):
    def p(s2, x, y): return View.p(s2, x - off[0], y - off[1])
d.__class__ = Shift
d.rect(SX0 - 0.35, SY0 - TE, SL + 0.7, TE, fill=0.18, stroke=False)      # front wall
d.rect(SX0 - TI, SY0, TI, SW + 0.25, fill=0.35, stroke=False)            # divider
stair_plan(d, fine=True)
d.dimh(SX0, x0, SY0 - 0.6); d.dimh(x0, x0 + NT * TREAD, SY0 - 0.6, f"7×260 = 1820")
d.dimh(x0 + NT * TREAD, SX0 + SL, SY0 - 0.6)
d.dimh(SX0, SX0 + SL, SY0 - 0.95, "3500 (тоза)")
d.dimv(SY0, SY0 + FW, SX0 + SL + 0.3); d.dimv(SY0 + FW, SY0 + FW + GAP, SX0 + SL + 0.3)
d.dimv(SY0 + FW + GAP, SY0 + SW, SX0 + SL + 0.3)
d.dimv(SY0, SY0 + SW, SX0 + SL + 0.65, "2000 (тоза)")
c.setFont("FB", 10); X, Y = d.p(SX0 - 0.3, SY0 + SW + 0.35); c.drawString(X, Y, "НАҚШАИ ЗИНА  (1:25)")
tx = 255 * mm; ty = 200 * mm
c.setFont("FB", 9); c.drawString(tx, ty, "Зинаи U-шакл, оҳану бетон (монолит)")
c.setFont("F", 8)
for i, t in enumerate([
        f"Аз −1,000 то +1,750 = 2750 мм",
        f"16 пиллакон × {RISE:.1f} мм (баландӣ)".replace(".", ","),
        "Умқи пиллапоя 260 мм · 2 марш × 8 пиллакон",
        "Бари марш 900 · байни маршҳо 200 (девор/фосила)",
        f"Майдончаи мобайнӣ {LAND * 1000:.0f} × 2000, сатҳ {land_y:+.3f}".replace(".", ","),
        "Ғафсии марш ва майдонча ≈ 180 мм",
        "Дастак h = 900 аз лаби пиллапоя",
        "Рақамҳо дар нақша — тартиби пиллакон 1…16",
        "Сӯрохии шифт 3500×2000 — зинаи ошёнаи 1",
        "   дар ҳамин ҷо давом мекунад",
        "Аз сари пиллапоя то шифт ≥ 2000 мм санҷед"]):
    c.drawString(tx, ty - (i + 1) * 5 * mm, t)
c.showPage()

# =============================== SHEET 3: TABLES ===============================
frame("Варақ 4 — Ҷадвалҳо, дару тиреза, саволҳо", 4, "—")
def table(x, y, cols, widths, rows, title):
    c.setFont("FB", 10); c.drawString(x, y + 4 * mm, title)
    rh = 6.5 * mm
    allr = [cols] + rows
    for i, row in enumerate(allr):
        yy = y - i * rh
        if i == 0:
            c.setFillGray(0.9); c.rect(x, yy - rh, sum(widths), rh, stroke=0, fill=1); c.setFillGray(0)
        xx = x
        for j, (val, w) in enumerate(zip(row, widths)):
            c.setLineWidth(0.3); c.rect(xx, yy - rh, w, rh)
            c.setFont("FB" if i == 0 else "F", 7.8)
            c.drawString(xx + 1.5 * mm, yy - rh + 2.1 * mm, str(val))
            xx += w
table(20 * mm, 265 * mm, ["Ҳуҷра", "Андозаи тоза, мм", "Масоҳат, м²", "Баландӣ, мм", "Фарш"],
      [55 * mm, 45 * mm, 28 * mm, 28 * mm, 25 * mm],
      [["1 — анбор (чап)", "3500 × 7200", "25,20", "2000", "−0,500"],
       ["2 — асосӣ (бо зина)", "8500 × 7200", "61,20", "2500", "−1,000"],
       ["   аз он зина", "3500 × 2000", "7,00", "—", "−1,000"],
       ["Ҳамагӣ тоза", "", "86,40", "", ""],
       ["Умумӣ (бо девор)", "13000 × 8000", "104,00", "", ""]],
      "Ҷадвали ҳуҷраҳо")
table(20 * mm, 205 * mm, ["Рамз", "Ҷой", "Бар × баландӣ, мм", "Аз фарш, мм", "Эзоҳ"],
      [18 * mm, 62 * mm, 38 * mm, 25 * mm, 60 * mm],
      [["Д-1", "девори байни ҳуҷраҳо", "900 × 2000", "аз −0,500", "+ 3 зинача ба −1,000 (3×167)"],
       ["Д-2", "девори қафо, 4 м аз девори чап", "800 × 1900", "—", "мувофиқи модели 3D (тахминӣ)"],
       ["Т-1", "девори қафо", "900 × 500", "1900", "тирезаи болои (тахминӣ)"],
       ["Т-2", "девори қафо", "800 × 500", "1900", "тирезаи болои (тахминӣ)"]],
      "Ҷадвали дарҳо ва тирезаҳо")
table(20 * mm, 155 * mm, ["Кор", "Ҳаҷм", "Эзоҳ"], [70 * mm, 40 * mm, 80 * mm],
      [["Кандани хок", "≈ 13,6×8,6×1,6 ≈ 187 м³", "бо 300 мм фосила аз ҳар тараф"],
       ["Бетони тайёрӣ 100", "≈ 11 м³", ""],
       ["Плитаи таҳкурсӣ 500", "≈ 54 м³", "арматура — аз ҳисоби муҳандис"],
       ["Деворҳои берунӣ 400 (h 2,5)", "≈ 40 м³", "оҳану бетон"],
       ["Плитаи шифт 250", "≈ 24 м³", "бе сӯрохии зина"],
       ["Зина (2 марш + майдонча)", "≈ 2 м³", "монолит"]],
      "Ҳаҷмҳои тахминӣ (барои нарх, на барои фармоиш)")
qx = 240 * mm
c.setFont("FB", 10); c.setFillColorRGB(*RED); c.drawString(qx, 269 * mm, "Пеш аз сохтан тасдиқ кунед"); c.setFillGray(0)
c.setFont("F", 8)
for i, t in enumerate([
        "1. Сатҳҳо аз модели 3D гирифта шуданд: −100 см = фарши ҳуҷраи 2,",
        "   −50 см = фарши ҳуҷраи 1, шифти умумӣ +1,500. Агар нодуруст бошад,",
        "   баландии зина ва пиллакон иваз мешавад.",
        "2. Ҷойи дари Д-2 ва тирезаҳо дар модели 3D аниқ нест — дар ҷой чен кунед.",
        "3. Зина дар паҳлӯи девори байни ҳуҷраҳо, ба девори пеш гузошта шуд —",
        "   бояд бо зинаи ошёнаи 1 як ҷо бошад.",
        "4. Арматураи плита, девор, шифт ва зинаро муҳандиси конструктор",
        "   ҳисоб мекунад (сейсмика 8–9 балл). Ин варақҳо танҳо андозаҳоянд.",
        "5. Агар болои таҳхона мошин гузарад, шифт бояд барои он ҳисоб шавад.",
        "6. Гидроизолятсия ва дренаж ҳатмист.",
        ]):
    c.drawString(qx, (262 - i * 5.2) * mm, t)
c.save()
