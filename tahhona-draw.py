"""Basement working drawings for builders (from the 3D model). Dimensions in cm."""
import math
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
c.setTitle("Таҳхона — нақша барои устоҳо")

# ---------------- geometry (metres, outer corner = 0,0) ----------------
L, D = 13.0, 8.0
TE, TI = 0.4, 0.2
XD = 4.0
SL, SW = 3.5, 2.0
SX0, SY0 = XD + TI / 2, D - TE - SW      # corner of room 2 at back wall, next to divider
FW, GAP = 0.9, 0.2
NR, RISE, TREAD = 16, 275 / 16, 0.26      # 16 x 17,2 cm
NT = 7
START = 0.48
LAND = SL - START - NT * TREAD           # 1.20
COLS = [(XD, 4.0), (XD + 4.5, 4.0)]
DOOR_DIV = (4.4, 5.3)
WIN = [(6.3, 7.2), (9.3, 10.1)]
DOOR_BACK = (7.6, 8.4)
SHEETS = 4


def cm(v):
    return f"{round(v * 100):d}"


def frame(title, sheet):
    c.setLineWidth(0.6); c.setStrokeGray(0)
    c.rect(10 * mm, 10 * mm, W - 20 * mm, H - 20 * mm)
    c.rect(W - 170 * mm, 10 * mm, 160 * mm, 18 * mm)
    c.setFont("FB", 11); c.setFillGray(0)
    c.drawString(W - 166 * mm, 21 * mm, "ТАҲХОНА — " + title)
    c.setFont("F", 8.5)
    c.drawString(W - 166 * mm, 14.5 * mm, "Андозаҳо бо сантиметр (см)")
    c.setFont("FB", 13); c.drawRightString(W - 14 * mm, 14.5 * mm, f"{sheet}/{SHEETS}")
    c.setFont("F", 7); c.setFillColorRGB(*RED)
    c.drawString(14 * mm, 14 * mm, "Арматура ва ҳисоби конструксия — аз муҳандис.")
    c.setFillGray(0)


class View:
    def __init__(s, ox, oy, scale, off=(0, 0)):
        s.ox, s.oy, s.k, s.off = ox, oy, 1000 / scale * mm, off

    def p(s, x, y):
        return s.ox + (x - s.off[0]) * s.k, s.oy + (y - s.off[1]) * s.k

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

    def dimh(s, x1, x2, y, t=None, size=7.5):
        X1, Y = s.p(x1, y); X2, _ = s.p(x2, y)
        c.setLineWidth(0.3); c.line(X1 - 2 * mm, Y, X2 + 2 * mm, Y)
        for X in (X1, X2):
            c.line(X - 1.2 * mm, Y - 1.2 * mm, X + 1.2 * mm, Y + 1.2 * mm)
            c.line(X, Y - 2 * mm, X, Y + 2 * mm)
        c.setFont("F", size)
        c.drawCentredString((X1 + X2) / 2, Y + 1.2 * mm, t or cm(x2 - x1))

    def dimv(s, y1, y2, x, t=None, size=7.5):
        X, Y1 = s.p(x, y1); _, Y2 = s.p(x, y2)
        c.setLineWidth(0.3); c.line(X, Y1 - 2 * mm, X, Y2 + 2 * mm)
        for Y in (Y1, Y2):
            c.line(X - 1.2 * mm, Y - 1.2 * mm, X + 1.2 * mm, Y + 1.2 * mm)
            c.line(X - 2 * mm, Y, X + 2 * mm, Y)
        c.saveState(); c.translate(X - 1.2 * mm, (Y1 + Y2) / 2); c.rotate(90)
        c.setFont("F", size); c.drawCentredString(0, 0, t or cm(y2 - y1))
        c.restoreState()

    def arrow(s, pts, lw=0.7):
        c.setLineWidth(lw)
        P = [s.p(*q) for q in pts]
        path = c.beginPath(); path.moveTo(*P[0])
        for q in P[1:]: path.lineTo(*q)
        c.drawPath(path, stroke=1, fill=0)
        c.circle(*P[0], 0.8 * mm, stroke=0, fill=1)
        (x1, y1), (x2, y2) = P[-2], P[-1]
        a = math.atan2(y2 - y1, x2 - x1)
        hl, hw = 2.6 * mm, 1.1 * mm
        bx, by = x2 - hl * math.cos(a), y2 - hl * math.sin(a)
        path = c.beginPath(); path.moveTo(x2, y2)
        path.lineTo(bx + hw * math.sin(a), by - hw * math.cos(a))
        path.lineTo(bx - hw * math.sin(a), by + hw * math.cos(a)); path.close()
        c.drawPath(path, stroke=0, fill=1)


def axis_bubble(X, Y, t):
    c.setStrokeColorRGB(*RED); c.setFillColorRGB(1, 1, 1); c.setLineWidth(0.5)
    c.circle(X, Y, 3.2 * mm, stroke=1, fill=1)
    c.setFillColorRGB(*RED); c.setFont("FB", 8); c.drawCentredString(X, Y - 1.1 * mm, t)
    c.setFillGray(0); c.setStrokeGray(0)


def stair_plan(v, numbers=False):
    v.rect(SX0, SY0, SL, SW, fill=0.93, stroke=False)
    yA, yB = SY0, SY0 + FW + GAP          # yA: start flight (room side), yB: against back wall
    x0 = SX0 + START
    for i in range(NT + 1):
        x = x0 + i * TREAD
        v.line(x, yA, x, yA + FW, lw=0.45)
        v.line(x, yB, x, yB + FW, lw=0.45)
    v.rect(SX0, SY0 + FW, START + NT * TREAD, GAP, fill=0.6, stroke=False)
    v.line(x0 + NT * TREAD, SY0, x0 + NT * TREAD, SY0 + SW, lw=0.6)
    ym1, ym2 = yA + FW / 2, yB + FW / 2
    xe = x0 + NT * TREAD + LAND / 2
    v.arrow([(x0 - 0.15, ym1), (xe, ym1), (xe, ym2), (x0 - 0.2, ym2)])
    if numbers:
        for i in range(NT):
            v.text(x0 + (i + 0.5) * TREAD, ym1 - 0.32, str(i + 1), size=7)
            v.text(x0 + (NT - 1 - i + 0.5) * TREAD, ym2 + 0.2, str(NT + 2 + i), size=7)
        v.text(xe, ym1 - 0.32, "8", size=7)
        v.text(x0 - 0.24, ym2 + 0.2, "16", size=7)
    v.text(x0 + 1.0, ym1 + (-0.3 if not numbers else 0.2), "боло ↑", size=9 if numbers else 7, bold=True)


# =============================== 1: PLAN ===============================
frame("нақша", 1)
v = View(60 * mm, 70 * mm, 50)
v.rect(0, 0, L, D, fill=0.18, stroke=False)
v.rect(TE, TE, XD - TI / 2 - TE, D - 2 * TE, fill=(0.86, 0.86, 0.84), stroke=False)
v.rect(XD + TI / 2, TE, L - TE - XD - TI / 2, D - 2 * TE, fill=(0.96, 0.94, 0.88), stroke=False)
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
for cx, cy in COLS:
    v.rect(cx - 0.2, cy - 0.2, 0.4, 0.4, fill=0.0, stroke=False)
stair_plan(v)
# axes
for ax, t in ((0.2, "1"), (XD, "2"), (XD + 4.5, "3"), (L - 0.2, "4")):
    v.line(ax, -1.9, ax, D + 1.9, lw=0.25, dash=(6, 2, 1, 2))
    X, Y = v.p(ax, D + 2.25); axis_bubble(X, Y, t)
for ay, t in ((D - 0.2, "А"), (4.0, "Б"), (0.2, "В")):
    v.line(-2.2, ay, L + 0.6, ay, lw=0.25, dash=(6, 2, 1, 2))
    X, Y = v.p(-2.55, ay); axis_bubble(X, Y, t)
# labels (short)
v.text((TE + XD) / 2, 5.0, "Ҳуҷраи 1", size=10, bold=True)
v.text(10.3, 5.6, "Ҳуҷраи 2", size=10, bold=True)
v.text(XD + 0.5, (DOOR_DIV[0] + DOOR_DIV[1]) / 2 - 0.05, "Д-1", size=7.5)
v.text((DOOR_BACK[0] + DOOR_BACK[1]) / 2, D - TE - 0.95, "Д-2", size=7.5)
for i, (a, b) in enumerate(WIN, 1):
    v.text((a + b) / 2, D + 0.12, f"Т-{i}", size=7)
v.text(COLS[1][0] + 0.3, COLS[1][1] - 0.45, "сутун 40 × 40 см", size=7.5, center=False)
v.text(SX0 + SL + 0.35, SY0 + 0.1, "Зина", size=9, bold=True, center=False)
v.dimh(SX0, SX0 + SL, SY0 - 0.25, size=7)
# dimensions (cm)
v.dimh(0, L, -1.5)
v.dimh(0, XD, -1.0); v.dimh(XD, L, -1.0)
for a, b in ((0, TE), (TE, XD - TI / 2), (XD - TI / 2, XD + TI / 2), (XD + TI / 2, L - TE), (L - TE, L)):
    v.dimh(a, b, -0.5)
pts = [XD + TI / 2, WIN[0][0], WIN[0][1], DOOR_BACK[0], DOOR_BACK[1], WIN[1][0], WIN[1][1], L - TE]
for a, b in zip(pts, pts[1:]): v.dimh(a, b, D + 0.5, size=7)
v.dimh(XD, XD + 4.5, D + 1.0); v.dimh(XD + 4.5, L, D + 1.0)
v.dimv(0, D, -1.6)
v.dimv(0, TE, -1.0); v.dimv(TE, D - TE, -1.0); v.dimv(D - TE, D, -1.0)
for a, b in ((0, TE), (TE, 4.0), (4.0, SY0), (SY0, D - TE), (D - TE, D)):
    v.dimv(a, b, L + 1.0)
v.dimv(0, 4.0, L + 1.5); v.dimv(4.0, D, L + 1.5)
for a, b in ((TE, DOOR_DIV[0]), DOOR_DIV, (DOOR_DIV[1], D - TE)):
    v.dimv(a, b, XD - 0.55, size=7)
# section mark 1-1
ycut = SY0 + FW / 2
for xx, side in ((-0.6, 1), (L + 0.6, -1)):
    X, Y = v.p(xx, ycut)
    c.setLineWidth(1.4); c.line(X, Y, X + side * 5 * mm, Y)
    c.line(X, Y, X, Y - 4 * mm); c.setFont("FB", 9); c.drawCentredString(X - side * 3 * mm, Y - 6 * mm, "1")
v.line(-0.4, ycut, L + 0.4, ycut, lw=0.3, dash=(8, 3))
c.showPage()

# =============================== 2: SECTION ===============================
frame("буриши 1-1", 2)
s = View(70 * mm, 150 * mm, 50)
TOP, SLAB = 1.5, 0.25
s.rect(-0.1, -1.5, L + 0.2, 0.5, fill=0.55, stroke=True)                      # plate 50
s.rect(TE, -1.0, XD - TI / 2 - TE, 0.5, fill=(0.82, 0.76, 0.62), stroke=True)  # raised floor room 1
for x0_, w_ in ((0, TE), (L - TE, TE)):
    s.rect(x0_, -1.0, w_, TOP + 1.0, fill=0.18, stroke=False)
s.rect(XD - TI / 2, -1.0, TI, TOP + 1.0, fill=0.35, stroke=False)
s.rect(-0.1, TOP, SX0 + 0.1, SLAB, fill=0.35, stroke=False)
s.rect(SX0 + SL, TOP, L + 0.1 - SX0 - SL, SLAB, fill=0.35, stroke=False)
r = RISE / 100
x0 = SX0 + START
land_y = -1.0 + 8 * r
pts = [(SX0, -1.0), (x0, -1.0)]
for i in range(NT):
    pts += [(x0 + i * TREAD, -1.0 + (i + 1) * r), (x0 + (i + 1) * TREAD, -1.0 + (i + 1) * r)]
pts += [(x0 + NT * TREAD, land_y), (SX0 + SL, land_y)]
c.setLineWidth(0.6)
path = c.beginPath(); path.moveTo(*s.p(*pts[0]))
for q in pts[1:]: path.lineTo(*s.p(*q))
path.lineTo(*s.p(SX0 + SL, land_y - 0.18)); path.lineTo(*s.p(x0 + NT * TREAD, land_y - 0.18))
path.lineTo(*s.p(x0 + 0.15, -1.0)); path.close()
c.setFillGray(0.55); c.drawPath(path, stroke=1, fill=1); c.setFillGray(0)
c.setDash(2, 1.5); c.setLineWidth(0.4)
path = c.beginPath(); path.moveTo(*s.p(x0 + NT * TREAD, land_y))
for i in range(NT):
    xa = x0 + (NT - i) * TREAD
    path.lineTo(*s.p(xa, land_y + (i + 1) * r)); path.lineTo(*s.p(xa - TREAD, land_y + (i + 1) * r))
path.lineTo(*s.p(SX0, land_y + 8 * r))
c.drawPath(path, stroke=1, fill=0); c.setDash()
s.text(2.2, 0.6, "Ҳуҷраи 1", size=10, bold=True)
s.text(10.3, 0.6, "Ҳуҷраи 2", size=10, bold=True)
# vertical dims (cm)
s.dimv(-0.5, TOP, 1.0)                 # 200
s.dimv(-1.0, -0.5, 1.0)                # 50
s.dimv(-1.0, TOP, 11.5)                # 250
s.dimv(TOP, TOP + SLAB, L + 0.6)       # 25
s.dimv(-1.0, TOP, L + 0.6)             # 250
s.dimv(-1.5, -1.0, L + 0.6)            # 50
s.dimv(-1.5, TOP + SLAB, L + 1.2)      # 325
s.dimv(-1.0, land_y, SX0 + SL + 0.3, "137,5")
s.dimh(0, XD, -2.1); s.dimh(XD, L, -2.1)
s.dimh(SX0, x0, -2.5); s.dimh(x0, x0 + NT * TREAD, -2.5, "7 × 26 = 182"); s.dimh(x0 + NT * TREAD, SX0 + SL, -2.5)
c.setFont("FB", 10); X, Y = s.p(0, 2.6); c.drawString(X, Y, "БУРИШИ 1-1")
c.showPage()

# =============================== 3: STAIR ===============================
frame("зина", 3)
d = View(50 * mm, 95 * mm, 25, off=(SX0 - 0.35, SY0 - 0.4))
d.rect(SX0 - 0.35, SY0 + SW, SL + 0.7, TE, fill=0.18, stroke=False)
d.rect(SX0 - TI, SY0 - 0.25, TI, SW + 0.25, fill=0.35, stroke=False)
stair_plan(d, numbers=True)
d.dimh(SX0, x0, SY0 - 0.6); d.dimh(x0, x0 + NT * TREAD, SY0 - 0.6, "7 × 26 = 182")
d.dimh(x0 + NT * TREAD, SX0 + SL, SY0 - 0.6)
d.dimh(SX0, SX0 + SL, SY0 - 0.95)
d.dimv(SY0, SY0 + FW, SX0 + SL + 0.3); d.dimv(SY0 + FW, SY0 + FW + GAP, SX0 + SL + 0.3)
d.dimv(SY0 + FW + GAP, SY0 + SW, SX0 + SL + 0.3)
d.dimv(SY0, SY0 + SW, SX0 + SL + 0.65)
c.setFont("FB", 10); X, Y = d.p(SX0 - 0.3, SY0 + SW + 0.65); c.drawString(X, Y, "НАҚШАИ ЗИНА")
tx, ty = 270 * mm, 190 * mm
c.setFont("F", 9)
for i, t in enumerate(["16 пиллакон", "баландӣ 17,2 см", "умқ 26 см", "бари марш 90 см"]):
    c.drawString(tx, ty - i * 6 * mm, t)
c.showPage()

# =============================== 4: TABLES ===============================
frame("дару тиреза", 4)


def table(x, y, cols, widths, rows, title):
    c.setFont("FB", 10); c.drawString(x, y + 4 * mm, title)
    rh = 7 * mm
    for i, row in enumerate([cols] + rows):
        yy = y - i * rh
        if i == 0:
            c.setFillGray(0.9); c.rect(x, yy - rh, sum(widths), rh, stroke=0, fill=1); c.setFillGray(0)
        xx = x
        for val, w in zip(row, widths):
            c.setLineWidth(0.3); c.rect(xx, yy - rh, w, rh)
            c.setFont("FB" if i == 0 else "F", 9)
            c.drawString(xx + 2 * mm, yy - rh + 2.3 * mm, str(val))
            xx += w


table(30 * mm, 255 * mm, ["Ҳуҷра", "Андоза (тоза), см", "Баландӣ, см"],
      [50 * mm, 55 * mm, 40 * mm],
      [["Ҳуҷраи 1", "350 × 720", "200"],
       ["Ҳуҷраи 2", "850 × 720", "250"],
       ["Зина", "350 × 200", "—"]],
      "Ҳуҷраҳо")
table(30 * mm, 200 * mm, ["", "Бар × баландӣ, см", "Ҷой"],
      [25 * mm, 55 * mm, 70 * mm],
      [["Д-1", "90 × 200", "байни ҳуҷраҳо"],
       ["Д-2", "80 × 190", "девори қафо"],
       ["Т-1", "90 × 50", "девори қафо"],
       ["Т-2", "80 × 50", "девори қафо"]],
      "Дару тиреза")
c.save()
