"""Basement working drawings for builders, taken from the 3D model (khona / podval-3d).

Model coordinates (metres): x along the street, 0 = axis 2, 9 = axis 4, 13 = axis 5;
z across: -4 = axis A (street), 0 = axis Б, +4 = axis В (porch / back yard).
Plan drawing uses y = -z so the street is at the top, as on the 1st-floor plan.
All dimensions are written in centimetres.
"""
import math
import sys
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont("F", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("FB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
W, H = landscape(A3)
RED = (0.70, 0.18, 0.12)
# layout is drawn on an A3 grid and scaled down to A4 landscape for printing
PW, PH = landscape(A4)
K = PW / W
FS = 1.2   # text a bit larger so it stays readable on A4
c = canvas.Canvas(sys.argv[1], pagesize=(PW, PH))
c.setTitle("Таҳхона — нақша барои устоҳо")

# ---------------- model values ----------------
LA, LB, WD = 9.0, 4.0, 8.0          # part A (9 m), part B (4 m), width 8 m — inside sizes
L = LA + LB
T = 0.3                             # walls 30 cm, outside the inside sizes
HA, HB, DROP = 2.5, 2.0, 0.5        # clear heights, B floor 50 cm lower
SLAB, CEIL, FIN = 0.15, 0.2, 0.05   # floor slab, ceiling slab, floor-1 finish
YBT = -DROP + HB                    # B ceiling (1,5 above A floor)
F1 = HA + CEIL + FIN                # floor 1 = 2,75 above A floor
BEAM = (LA, LA + T)                 # header wall where the ceiling steps down
COLS = [(4.5, 0.0), (9.0, 0.0)]
COL = 0.4
# A/B step stair, sunk into A beside the column
NS = 3; SR = DROP / NS; ST = 0.28
SSZ0, SSZ1 = 0.3, 1.5
SSX0 = LA - (NS - 1) * ST            # 8,44
# main stair shaft (same place on every level)
SH = dict(x0=5.1, x1=8.6, z0=1.6, z1=3.6)
TR = 0.26; NR = 16; RD = F1 / NR     # 16 × 17,2 cm
SX0 = 5.25                           # floor-1 end of the flights
DX1 = SX0 + 8 * TR                   # 7,33: landing edge
MID0, MID1 = SH["z0"] + 0.9, SH["z0"] + 1.1   # core wall 2,5 … 2,7
LAND = RD * 8                        # landing height 137,5
# openings in the В wall (z = +4)
DOOR = (4.0, 4.9); DOOR_H = 2.05
WINS = [("Т-1", 0.7, 1.9), ("Т-2", 2.1, 3.3)]
SHEETS = 4


def cm(v):
    v = round(v * 100, 1)
    return f"{v:.0f}" if abs(v - round(v)) < 0.05 else f"{v:.1f}".replace(".", ",")


def frame(title, sheet):
    c.scale(K, K)
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

    def rect(s, x0, y0, x1, y1, fill=None, stroke=False, lw=0.5):
        X0, Y0 = s.p(min(x0, x1), min(y0, y1)); X1, Y1 = s.p(max(x0, x1), max(y0, y1))
        if fill is not None:
            c.setFillGray(fill) if isinstance(fill, float) else c.setFillColorRGB(*fill)
        c.setLineWidth(lw)
        c.rect(X0, Y0, X1 - X0, Y1 - Y0, stroke=1 if stroke else 0, fill=1 if fill is not None else 0)
        c.setFillGray(0)

    def line(s, x1, y1, x2, y2, lw=0.4, gray=0, dash=None):
        c.setLineWidth(lw); c.setStrokeGray(gray)
        c.setDash(list(dash)) if dash else c.setDash()
        c.line(*s.p(x1, y1), *s.p(x2, y2))
        c.setDash(); c.setStrokeGray(0)

    def poly(s, pts, fill=None, lw=0.6, dash=None, close=True):
        path = c.beginPath(); path.moveTo(*s.p(*pts[0]))
        for q in pts[1:]: path.lineTo(*s.p(*q))
        if close: path.close()
        c.setLineWidth(lw)
        c.setDash(list(dash)) if dash else c.setDash()
        if fill is not None: c.setFillGray(fill)
        c.drawPath(path, stroke=1, fill=1 if fill is not None else 0)
        c.setDash(); c.setFillGray(0)

    def text(s, x, y, t, size=8, bold=False, center=True, color=None):
        X, Y = s.p(x, y)
        c.setFont("FB" if bold else "F", size * FS)
        if color: c.setFillColorRGB(*color)
        (c.drawCentredString if center else c.drawString)(X, Y, t)
        c.setFillGray(0)

    def dimh(s, x1, x2, y, t=None, size=7.5):
        X1, Y = s.p(x1, y); X2, _ = s.p(x2, y)
        c.setLineWidth(0.3); c.line(X1 - 2 * mm, Y, X2 + 2 * mm, Y)
        for X in (X1, X2):
            c.line(X - 1.2 * mm, Y - 1.2 * mm, X + 1.2 * mm, Y + 1.2 * mm)
            c.line(X, Y - 2 * mm, X, Y + 2 * mm)
        c.setFont("F", size * FS)
        c.drawCentredString((X1 + X2) / 2, Y + 1.2 * mm, t or cm(abs(x2 - x1)))

    def dimv(s, y1, y2, x, t=None, size=7.5):
        X, Y1 = s.p(x, y1); _, Y2 = s.p(x, y2)
        c.setLineWidth(0.3); c.line(X, Y1 - 2 * mm, X, Y2 + 2 * mm)
        for Y in (Y1, Y2):
            c.line(X - 1.2 * mm, Y - 1.2 * mm, X + 1.2 * mm, Y + 1.2 * mm)
            c.line(X - 2 * mm, Y, X + 2 * mm, Y)
        c.saveState(); c.translate(X - 1.2 * mm, (Y1 + Y2) / 2); c.rotate(90)
        c.setFont("F", size * FS); c.drawCentredString(0, 0, t or cm(abs(y2 - y1)))
        c.restoreState()

    def chainh(s, xs, y, size=7.5):
        for a, b in zip(xs, xs[1:]): s.dimh(a, b, y, size=size)

    def chainv(s, ys, x, size=7.5):
        for a, b in zip(ys, ys[1:]): s.dimv(a, b, x, size=size)

    def arrow(s, pts, lw=0.7, dot=True):
        c.setLineWidth(lw)
        P = [s.p(*q) for q in pts]
        path = c.beginPath(); path.moveTo(*P[0])
        for q in P[1:]: path.lineTo(*q)
        c.drawPath(path, stroke=1, fill=0)
        if dot: c.circle(*P[0], 0.8 * mm, stroke=0, fill=1)
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


def main_stair(v, numbers=False):
    """U-stair in plan (y = -z). Flight 1 on the room side goes up toward axis 4,
    landing at axis 4 side, flight 2 along the В wall comes back up to floor 1."""
    yR0, yR1 = -MID0, -SH["z0"]          # flight 1 (room side): z 1,6 … 2,5
    yW0, yW1 = -SH["z1"], -MID1          # flight 2 (В side):    z 2,7 … 3,6
    v.rect(SH["x0"], -SH["z1"], SH["x1"], -SH["z0"], fill=0.93)
    for k in range(8):                   # flight 1 risers: 5,51 … 7,33
        x = DX1 - k * TR
        v.line(x, yR0, x, yR1, lw=0.45)
    for k in range(8):                   # flight 2 risers: 5,25 … 7,07
        x = SX0 + k * TR
        v.line(x, yW0, x, yW1, lw=0.45)
    v.rect(SX0, -MID1, SX0 + 10 * TR, -MID0, fill=0.55)    # core wall between flights
    ym1, ym2 = (yR0 + yR1) / 2, (yW0 + yW1) / 2
    xe = (DX1 + SH["x1"]) / 2
    v.arrow([(DX1 - 7 * TR - 0.2, ym1), (xe, ym1), (xe, ym2), (SX0 - 0.05, ym2)])
    sz = 9 if numbers else 7
    v.text(DX1 - 3.5 * TR, ym1 + (0.2 if numbers else 0.12), "боло ↑", size=sz, bold=True)
    v.text(SX0 + 3.5 * TR, ym2 - (0.33 if numbers else 0.3), "боло ↑", size=sz, bold=True)
    if numbers:
        for i in range(7):
            v.text(DX1 - (6 - i + 0.5) * TR, ym1 - 0.33, str(i + 1), size=7)
            v.text(SX0 + (6 - i + 0.5) * TR, ym2 + 0.2, str(9 + i), size=7)
        v.text(xe, ym1 - 0.33, "8", size=7)
        v.text(SX0 - 0.07, ym2 + 0.2, "16", size=7)


def step_stair(v, label=True):
    """3 steps from A down to B beside the column at axis 4."""
    v.rect(SSX0, -SSZ1, LA, -SSZ0, fill=(0.80, 0.62, 0.42))
    for k in range(NS):
        x = SSX0 + k * ST
        v.line(x, -SSZ1, x, -SSZ0, lw=0.45)
    v.arrow([(SSX0 - 0.25, -(SSZ0 + SSZ1) / 2), (LA + 0.45, -(SSZ0 + SSZ1) / 2)], lw=0.6, dot=True)
    if label:
        v.text(LA + 0.5, -(SSZ0 + SSZ1) / 2 + 0.25, "поён 50", size=7, center=False)


# =============================== 1: PLAN ===============================
frame("нақша", 1)
v = View(68 * mm, 145 * mm, 50)
# outer walls
v.rect(-T, -WD / 2 - T, L + T, WD / 2 + T, fill=0.18)
v.rect(0, -WD / 2, LA, WD / 2, fill=(0.96, 0.94, 0.88))          # A, tiles
v.rect(LA, -WD / 2, L, WD / 2, fill=(0.82, 0.82, 0.80))          # B, concrete, 50 lower
# A/B edge (50 cm drop) and the beam above (dashed)
v.line(LA, -WD / 2, LA, WD / 2, lw=1.0)
v.line(BEAM[1], -WD / 2, BEAM[1], WD / 2, lw=0.4, dash=(4, 2))
# openings in the В wall (bottom)
yW = -WD / 2
v.rect(DOOR[0], yW - T - 0.01, DOOR[1], yW + 0.01, fill=1.0)
X, Y = v.p(DOOR[1], yW); r = (DOOR[1] - DOOR[0]) * v.k
c.setLineWidth(0.4); c.line(X, Y, X, Y + r); c.setDash(2, 1.5); c.arc(X - r, Y - r, X + r, Y + r, 90, 90); c.setDash()
for name, a, b in WINS:
    v.rect(a, yW - T - 0.01, b, yW + 0.01, fill=1.0, stroke=True, lw=0.4)
    v.line(a, yW - T / 2, b, yW - T / 2, lw=0.4)
    v.text((a + b) / 2, yW + 0.2, name, size=7)
v.text(sum(DOOR) / 2 - 0.2, yW + 1.05, "Д-1", size=7.5)
# columns
for cx, cz in COLS:
    v.rect(cx - COL / 2, -cz - COL / 2, cx + COL / 2, -cz + COL / 2, fill=0.0)
v.text(COLS[0][0] + 0.3, -COLS[0][1] + 0.3, "сутун 40 × 40 см", size=7.5, center=False)
main_stair(v)
step_stair(v)
v.text((SH["x0"] + SH["x1"]) / 2, -SH["z0"] + 0.25, "Зина", size=9, bold=True)
v.text(3.0, 1.6, "Ҳуҷраи 1", size=10, bold=True)
v.text(L - LB / 2 + 0.15, 1.6, "Ҳуҷраи 2", size=10, bold=True)
v.text(L - LB / 2 + 0.15, 1.15, "фарш 50 см пасттар", size=7.5)
# axes as on the 1st-floor plan
for ax, t in ((0, "2"), (4.5, "3"), (LA, "4"), (L, "5")):
    v.line(ax, -WD / 2 - 2.0, ax, WD / 2 + 2.0, lw=0.25, dash=(6, 2, 1, 2))
    X_, Y_ = v.p(ax, WD / 2 + 2.35); axis_bubble(X_, Y_, t)
for az, t in ((-4, "А"), (0, "Б"), (4, "В")):
    v.line(-2.3, -az, L + 2.3, -az, lw=0.25, dash=(6, 2, 1, 2))
    X_, Y_ = v.p(-2.65, -az); axis_bubble(X_, Y_, t)
# dimensions
v.chainh([0, 4.5, LA, L], WD / 2 + 0.8)
v.chainh([-T, 0, LA, BEAM[1], L, L + T], WD / 2 + 1.3)
v.dimh(-T, L + T, WD / 2 + 1.8)
v.chainh([0, WINS[0][1], WINS[0][2], WINS[1][1], WINS[1][2], DOOR[0], DOOR[1], SH["x0"], SH["x1"], LA, L],
         -WD / 2 - 0.75, size=7)
v.chainh([SSX0, SSX0 + ST, LA], -SSZ1 - 0.35, size=6.5)
v.chainv([-4, 0, 4], -1.0)
v.dimv(-4 - T, 4 + T, -1.6)
v.chainv([-4, -SH["z1"], -SH["z0"], -SSZ1, -SSZ0, 0, 4], L + 1.0, size=7)
v.chainv([-4 - T, -4], L + 1.0, size=7); v.chainv([4, 4 + T], L + 1.0, size=7)
# section mark 1-1 through flight 1
ycut = -(SH["z0"] + MID0) / 2
for xx, side in ((-0.7, 1), (L + 0.7, -1)):
    X_, Y_ = v.p(xx, ycut)
    c.setLineWidth(1.4); c.line(X_, Y_, X_ + side * 5 * mm, Y_)
    c.line(X_, Y_, X_, Y_ - 4 * mm); c.setFont("FB", 9); c.drawCentredString(X_ - side * 3 * mm, Y_ - 6 * mm, "1")
v.line(-0.5, ycut, L + 0.5, ycut, lw=0.3, dash=(8, 3))
c.showPage()

# =============================== 2: SECTION ===============================
frame("буриши 1-1", 2)
s = View(58 * mm, 115 * mm, 45)
yB = -DROP
# slabs under floors
s.rect(-T, -SLAB, LA, 0, fill=0.55, stroke=True)
s.rect(LA, yB - SLAB, L + T, yB, fill=0.55, stroke=True)
s.rect(LA - 0.01, yB - SLAB, LA + 0.01, 0, fill=0.55)
# outer walls
s.rect(-T, -SLAB, 0, HA + CEIL, fill=0.18)
s.rect(L, yB - SLAB, L + T, YBT + CEIL, fill=0.18)
# ceilings: A with the stair opening, B lower, beam between
s.rect(-T, HA, SH["x0"], HA + CEIL, fill=0.35)
s.rect(SH["x1"], HA, LA, HA + CEIL, fill=0.35)
s.rect(LA, YBT, BEAM[1], HA + CEIL, fill=0.35)
s.rect(BEAM[1], YBT, L + T, YBT + CEIL, fill=0.35)
s.rect(-T, HA + CEIL, SH["x0"], F1, fill=0.75)                   # floor-1 finish
s.rect(SH["x1"], HA + CEIL, LA + T, F1, fill=0.75)
# earth over B (under the driveway)
s.rect(BEAM[1], YBT + CEIL, L + T, F1, fill=(0.80, 0.72, 0.58))
s.line(-T - 0.8, F1 - FIN, L + T + 0.8, F1 - FIN, lw=0.5)
# main stair flight 1 (cut), rising toward axis 4
pts = [(SH["x0"], 0), (DX1 - 7 * TR, 0)]
for i in range(7):
    xa = DX1 - (7 - i) * TR
    pts += [(xa, (i + 1) * RD), (xa + TR, (i + 1) * RD)]
pts += [(DX1, LAND), (SH["x1"], LAND), (SH["x1"], LAND - 0.18), (DX1, LAND - 0.18), (DX1 - 7 * TR + 0.15, 0)]
s.poly(pts, fill=0.55)
# flight 2 beyond (dashed), back up to floor 1
p2 = [(DX1, LAND)]
for k in range(7):
    xa = DX1 - k * TR - TR
    p2 += [(xa + TR, LAND + (k + 1) * RD), (xa, LAND + (k + 1) * RD)]
p2 += [(SX0, F1)]
s.poly(p2, lw=0.4, dash=(2, 1.5), close=False)
s.text(3.0, 1.2, "Ҳуҷраи 1", size=10, bold=True)
s.text(L - LB / 2 + 0.15, 0.6, "Ҳуҷраи 2", size=10, bold=True)
# vertical dims
s.chainv([-SLAB, 0, HA, F1], -1.0)
s.dimv(-SLAB, F1, -1.6)
s.chainv([0, LAND], SH["x0"] - 0.35)
s.chainv([YBT, HA + CEIL], LA + 0.75)
s.chainv([yB - SLAB, yB, YBT, YBT + CEIL], L + 1.0)
s.dimv(yB, 0, L + 1.6)
# horizontal dims
s.chainh([-T, 0, LA, BEAM[1], L, L + T], -1.2)
s.chainh([SH["x0"], DX1 - 7 * TR, DX1, SH["x1"], LA], -0.75, size=7)
c.setFont("FB", 10); X_, Y_ = s.p(-T, F1 + 0.7); c.drawString(X_, Y_, "БУРИШИ 1-1")
c.showPage()

# =============================== 3: STAIRS ===============================
frame("зинаҳо", 3)
d = View(30 * mm, 105 * mm, 25, off=(SH["x0"] - 0.3, -4 - T))
d.rect(SH["x0"] - 0.3, -4 - T, SH["x1"] + 0.5, -4, fill=0.18)     # В wall
main_stair(d, numbers=True)
d.chainh([SH["x0"], SX0, DX1 - 7 * TR, DX1, SH["x1"]], -SH["z0"] + 0.3, size=7)
d.dimh(SH["x0"], SH["x1"], -SH["z0"] + 0.62)
d.chainv([-4, -SH["z1"], -MID1, -MID0, -SH["z0"]], SH["x1"] + 0.3, size=7)
c.setFont("FB", 10); X_, Y_ = d.p(SH["x0"] - 0.3, -SH["z0"] + 0.95); c.drawString(X_, Y_, "ЗИНАИ АСОСӢ (ба ошёнаи 1)")
c.setFont("F", 9)
for i, t in enumerate(["16 пиллакон", f"баландӣ {cm(RD)} см", "умқ 26 см", "бари марш 90 см",
                       f"майдонча дар {cm(LAND)} см"]):
    c.drawString(32 * mm, 94 * mm - i * 6 * mm, t)

# step stair A → B: plan and profile
e = View(245 * mm, 150 * mm, 25, off=(SSX0 - 0.8, -SSZ1 - 0.3))
e.rect(SSX0 - 0.6, -SSZ1 - 0.1, LA, -SSZ0 + 0.1, fill=(0.96, 0.94, 0.88))
e.rect(LA, -SSZ1 - 0.1, LA + 0.7, -SSZ0 + 0.1, fill=(0.82, 0.82, 0.80))
step_stair(e, label=False)
e.rect(LA - COL / 2, -COL / 2 + 0.0, LA + COL / 2, COL / 2, fill=0.0)
e.chainh([SSX0, SSX0 + ST, LA], -SSZ1 - 0.25, size=7)
e.dimv(-SSZ1, -SSZ0, LA + 0.85, size=7)
e.text(LA - 0.6, -SSZ0 + 0.35, "сутун", size=7)
c.setFont("FB", 10); X_, Y_ = e.p(SSX0 - 0.8, 0.55); c.drawString(X_, Y_, "3 ПИЛЛАКОН АЗ ҲУҶРАИ 1 БА ҲУҶРАИ 2")
f = View(245 * mm, 80 * mm, 25, off=(SSX0 - 0.8, -0.7))
prof = [(SSX0 - 0.6, 0), (SSX0, 0), (SSX0, -SR), (SSX0 + ST, -SR), (SSX0 + ST, -2 * SR), (LA, -2 * SR), (LA, -DROP),
        (LA + 0.8, -DROP), (LA + 0.8, -0.7), (SSX0 - 0.6, -0.7)]
f.poly(prof, fill=0.6)
f.dimv(-DROP, 0, LA + 1.0, "3 × 16,7 = 50", size=7)
f.chainh([SSX0, SSX0 + ST, LA], 0.25, size=7)
f.text(SSX0 - 0.3, 0.08, "Ҳуҷраи 1", size=7)
f.text(LA + 0.4, -DROP + 0.08, "Ҳуҷраи 2", size=7)
c.setFont("F", 9)
for i, t in enumerate(["3 пиллакон × 16,7 см", "умқ 28 см", "бар 120 см"]):
    c.drawString(247 * mm, 66 * mm - i * 6 * mm, t)
c.showPage()

# =============================== 4: TABLES ===============================
frame("ҳуҷраҳо, дару тиреза", 4)


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


table(30 * mm, 255 * mm, ["Ҳуҷра", "Андоза (дохил), см", "Баландӣ, см", "Фарш"],
      [45 * mm, 50 * mm, 35 * mm, 50 * mm],
      [["Ҳуҷраи 1", "900 × 800", "250", "кошин"],
       ["Ҳуҷраи 2", "400 × 800", "200", "бетон, 50 см пасттар"],
       ["Зина", "350 × 200", "—", ""]],
      "Ҳуҷраҳо")
table(30 * mm, 200 * mm, ["", "Бар × баландӣ, см", "Аз фарш, см", "Ҷой"],
      [20 * mm, 50 * mm, 35 * mm, 65 * mm],
      [["Д-1", "90 × 205", "0", "девори В, дари даромад"],
       ["Т-1", "120 × 55", "175", "девори В"],
       ["Т-2", "120 × 55", "175", "девори В"]],
      "Дару тиреза")
c.save()
