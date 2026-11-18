#!/usr/bin/env python3
"""Procedural pixel-art generator for DOG MARIO (all sprites drawn with Pillow)."""
import math
import os
import random

from PIL import Image, ImageDraw

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
SPR = os.path.join(ROOT, "sprites")
random.seed(42)

# ---------------- palette ----------------
OUT = (34, 24, 28, 255)
WHITE = (250, 248, 240, 255)
SHADE = (214, 206, 196, 255)
BROWN = (150, 90, 46, 255)
DBROWN = (104, 60, 30, 255)
RED = (214, 40, 40, 255)
DRED = (140, 20, 28, 255)
GOLD = (255, 204, 40, 255)
DGOLD = (196, 136, 20, 255)
BLACK = (16, 12, 16, 255)
PINK = (240, 120, 150, 255)
CLEAR = (0, 0, 0, 0)


def new(w, h, color=CLEAR):
    return Image.new("RGBA", (w, h), color)


def save(img, *path):
    p = os.path.join(SPR, *path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    img.save(p)
    return p


def sheet(frames):
    w, h = frames[0].size
    s = new(w * len(frames), h)
    for i, f in enumerate(frames):
        s.paste(f, (i * w, 0), f)
    return s


def R(d, x, y, w, h, c):
    if w > 0 and h > 0:
        d.rectangle([x, y, x + w - 1, y + h - 1], fill=c)


def E(d, x0, y0, x1, y1, c, o=OUT):
    d.ellipse([x0, y0, x1, y1], fill=c, outline=o)


def outline_img(img, color=OUT):
    """Add a 1px outline around all opaque pixels."""
    w, h = img.size
    src = img.load()
    res = img.copy()
    dst = res.load()
    for y in range(h):
        for x in range(w):
            if src[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and src[nx, ny][3] > 0:
                        dst[x, y] = color
                        break
    return res


def tint(img, rgb, amount):
    img = img.copy()
    px = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (int(r + (rgb[0] - r) * amount), int(g + (rgb[1] - g) * amount),
                            int(b + (rgb[2] - b) * amount), a)
    return img


def alpha_mul(img, k):
    img = img.copy()
    px = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            r, g, b, a = px[x, y]
            px[x, y] = (r, g, b, int(a * k))
    return img


def star_shape(d, cx, cy, r, c, o=OUT):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=c, outline=o)


def tiny_star(d, x, y, c=GOLD):
    d.point((x, y), fill=WHITE)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        d.point((x + dx, y + dy), fill=c)


# =====================================================================
# DOGUINHO
# =====================================================================
def draw_dog(body_dy=0, legs=(0, 0, 0, 0), eye="open", tongue=False, tail=0,
             ear=0, mouth=False, paws_up=False, stretch=0):
    """Side-view dog facing right. legs = vertical lift per leg (back-far, back, front-far, front)."""
    img = new(32, 32)
    d = ImageDraw.Draw(img)
    by = 13 + body_dy
    # tail (wagging)
    tx = [(4, by - 3), (3, by - 4), (5, by - 5)][tail % 3]
    d.line([(8, by + 3), tx], fill=OUT, width=3)
    d.line([(8, by + 3), tx], fill=BROWN, width=1)
    d.point(tx, fill=WHITE)
    # legs (far legs darker)
    leg_x = [9, 11, 19, 21]
    for i, lx in enumerate(leg_x):
        lift = legs[i]
        col = SHADE if i in (0, 2) else WHITE
        top = by + 8
        if paws_up and i >= 2:
            # front paws raised in celebration
            R(d, lx, by - 1, 3, 6, OUT)
            R(d, lx + 1, by, 1, 4, col)
            continue
        ln = 6 - abs(lift) + stretch
        R(d, lx - 1, top, 4, ln + 1, OUT)
        R(d, lx, top, 2, ln, col)
        R(d, lx - 1, top + ln - 1, 4, 1, OUT)
        if lift < 0:  # leg kicked back
            d.point((lx - 1, top + ln - 2), fill=col)
    # body
    E(d, 6, by, 24, by + 10, WHITE)
    R(d, 9, by + 7, 13, 2, SHADE)
    E(d, 10, by + 1, 15, by + 5, BROWN, None)  # brown spot
    d.point((16, by + 6), fill=BROWN)
    d.point((17, by + 6), fill=BROWN)
    # head
    hy = by - 8
    E(d, 17, hy, 29, hy + 11, WHITE)
    # snout
    E(d, 24, hy + 5, 31, hy + 10, WHITE)
    R(d, 29, hy + 5, 2, 2, BLACK)  # nose
    d.point((29, hy + 5), fill=(90, 80, 90, 255))
    # spot around eye
    E(d, 21, hy + 1, 26, hy + 6, (238, 222, 200, 255), None)
    # ear (brown, flops)
    ey = hy - 1 + ear
    d.polygon([(17, ey + 1), (21, ey), (22, ey + 7), (18, ey + 9)], fill=BROWN, outline=OUT)
    d.point((19, ey + 3), fill=DBROWN)
    # eye (big)
    if eye == "open":
        R(d, 23, hy + 2, 3, 4, BLACK)
        d.point((23, hy + 2), fill=WHITE)
        d.point((24, hy + 2), fill=WHITE)
    elif eye == "closed":
        R(d, 22, hy + 4, 4, 1, BLACK)
    elif eye == "happy":
        d.line([(22, hy + 4), (23, hy + 3), (24, hy + 3), (25, hy + 4)], fill=BLACK)
    elif eye == "x":
        d.line([(22, hy + 2), (25, hy + 5)], fill=BLACK)
        d.line([(22, hy + 5), (25, hy + 2)], fill=BLACK)
    elif eye == "hurt":
        d.line([(22, hy + 2), (25, hy + 4)], fill=BLACK)
        d.line([(22, hy + 6), (25, hy + 4)], fill=BLACK)
    # mouth / tongue
    if mouth or tongue:
        R(d, 26, hy + 9, 4, 1, OUT)
    if tongue:
        R(d, 27, hy + 10, 2, 3, PINK)
        d.point((27, hy + 12), fill=(200, 80, 110, 255))
    # cheek blush
    d.point((26, hy + 7), fill=(255, 170, 170, 255))
    # red collar + golden tag
    R(d, 19, by - 1, 5, 3, RED)
    R(d, 19, by + 1, 5, 1, DRED)
    R(d, 21, by + 2, 2, 2, GOLD)
    d.point((21, by + 3), fill=DGOLD)
    return img


def make_player():
    out = []
    # idle: breathing + blink
    idle = [draw_dog(0, eye="open"), draw_dog(1, eye="open", tail=1),
            draw_dog(1, eye="closed", tail=2), draw_dog(0, eye="open", tail=1)]
    out.append(save(sheet(idle), "player", "doguinho_idle.png"))
    # walk 6 frames
    walk_legs = [(0, -1, -1, 0), (-1, 0, 0, -1), (-2, 0, 0, -2), (0, -2, -2, 0), (0, -1, -1, 0), (-1, 0, 0, -1)]
    walk = [draw_dog(i % 2, legs=walk_legs[i], tail=i % 3, ear=i % 2) for i in range(6)]
    out.append(save(sheet(walk), "player", "doguinho_walk.png"))
    # run 6 frames: bigger strides, tongue out, ears flapping
    run_legs = [(-3, 0, 0, -3), (-2, -1, -1, -2), (0, -3, -3, 0), (0, -3, -3, 0), (-1, -2, -2, -1), (-3, 0, 0, -3)]
    run = [draw_dog([0, -1, -2, 0, -1, -2][i], legs=run_legs[i], tongue=True, tail=i % 3,
                    ear=[-1, 0, 1, -1, 0, 1][i]) for i in range(6)]
    out.append(save(sheet(run), "player", "doguinho_run.png"))
    # jump
    jump = [draw_dog(-1, legs=(-2, -2, -3, -3), ear=-2, mouth=True),
            draw_dog(-2, legs=(-3, -3, -4, -4), ear=-2, mouth=True, tail=1)]
    out.append(save(sheet(jump), "player", "doguinho_jump.png"))
    # fall: legs stretched, ears up, worried
    fall = [draw_dog(-1, legs=(0, 0, 0, 0), ear=-3, eye="open", mouth=True, stretch=1),
            draw_dog(-1, legs=(0, 0, 0, 0), ear=-2, eye="open", mouth=True, stretch=1, tail=2)]
    out.append(save(sheet(fall), "player", "doguinho_fall.png"))
    # land: squash
    land = [draw_dog(3, legs=(-3, -3, -3, -3), ear=2, eye="closed"), draw_dog(1, legs=(-1, -1, -1, -1), ear=1)]
    out.append(save(sheet(land), "player", "doguinho_land.png"))
    # hurt: red flash + hurt eyes
    h1 = tint(draw_dog(0, eye="hurt", mouth=True, ear=-2), (255, 60, 60), 0.45)
    h2 = alpha_mul(draw_dog(-1, eye="hurt", mouth=True, ear=-1), 0.6)
    out.append(save(sheet([h1, h2]), "player", "doguinho_hurt.png"))
    # death: funny spin with dizzy stars
    base = draw_dog(0, eye="x", tongue=True, ear=-2)
    death = []
    for i, ang in enumerate([0, 90, 180, 270]):
        f = new(32, 32)
        r = base.rotate(-ang, resample=Image.NEAREST, center=(16, 16))
        f.paste(r, (0, -i * 2 + 2), r)
        d = ImageDraw.Draw(f)
        for k in range(3):
            a = i * 1.2 + k * 2.09
            tiny_star(d, int(16 + 9 * math.cos(a)), int(5 + 3 * math.sin(a)))
        death.append(f)
    out.append(save(sheet(death), "player", "doguinho_death.png"))
    # victory: hop with paws up + sparkles
    vic = []
    for i in range(4):
        f = draw_dog([0, -3, -4, -1][i], eye="happy", tongue=True, paws_up=i in (1, 2), tail=i % 3, ear=[0, -2, -2, 0][i])
        d = ImageDraw.Draw(f)
        if i in (1, 2):
            tiny_star(d, 3 + i * 2, 4)
            tiny_star(d, 13, 2 + i)
        vic.append(f)
    out.append(save(sheet(vic), "player", "doguinho_victory.png"))
    return out


# =====================================================================
# ENEMIES
# =====================================================================
SL_G = (90, 210, 90, 255)
SL_D = (40, 140, 60, 255)
SL_L = (180, 255, 170, 255)


def draw_slime(squash=0, eyes="open"):
    img = new(32, 32)
    d = ImageDraw.Draw(img)
    w = 11 + squash
    h = 10 - squash
    top = 30 - h * 2
    d.pieslice([16 - w, top, 16 + w, 30 + h], 180, 360, fill=SL_G, outline=OUT)
    R(d, 16 - w, 29, 2 * w + 1, 2, SL_D)
    d.line([(16 - w, 30), (16 + w, 30)], fill=OUT)
    # drips & highlights
    E(d, 16 - w + 3, top + 3, 16 - w + 7, top + 7, SL_L, None)
    d.point((16 - w + 9, top + 4), fill=SL_L)
    R(d, 16 + w - 5, 27, 2, 2, SL_D)
    # eyes
    ey = top + h - 1
    if eyes == "open":
        for ex in (12, 19):
            R(d, ex, ey, 3, 4, WHITE)
            R(d, ex + 1, ey + 1, 2, 3, BLACK)
    else:
        for ex in (12, 19):
            d.line([(ex, ey), (ex + 2, ey + 2)], fill=BLACK)
            d.line([(ex, ey + 2), (ex + 2, ey)], fill=BLACK)
    R(d, 15, ey + 5, 3, 1, SL_D)
    return img


def draw_bird(wing=0, dive=False):
    img = new(32, 32)
    d = ImageDraw.Draw(img)
    Y = (255, 214, 50, 255)
    YD = (220, 160, 30, 255)
    if dive:
        d.polygon([(8, 4), (22, 16), (18, 30), (6, 14)], fill=Y, outline=OUT)
        d.polygon([(16, 26), (22, 31), (14, 30)], fill=(255, 130, 30, 255), outline=OUT)
        R(d, 15, 20, 3, 3, WHITE)
        R(d, 16, 21, 2, 2, BLACK)
        d.polygon([(8, 4), (4, 0), (12, 4)], fill=RED, outline=OUT)
        d.polygon([(8, 10), (0, 6 + wing * 2), (4, 14)], fill=YD, outline=OUT)
        return img
    by = 14 + [0, -1, 0, 1][wing]
    # tail
    d.polygon([(5, by + 2), (1, by - 1), (2, by + 6)], fill=RED, outline=OUT)
    E(d, 5, by - 3, 22, by + 8, Y)
    E(d, 8, by + 2, 18, by + 8, (255, 240, 170, 255), None)
    # head
    E(d, 16, by - 9, 27, by + 1, Y)
    # crest
    d.polygon([(19, by - 9), (18, by - 14), (22, by - 9)], fill=RED, outline=OUT)
    d.polygon([(21, by - 9), (23, by - 13), (24, by - 8)], fill=RED, outline=OUT)
    # beak
    d.polygon([(26, by - 5), (31, by - 3), (26, by - 1)], fill=(255, 130, 30, 255), outline=OUT)
    # angry eye
    R(d, 22, by - 6, 3, 3, WHITE)
    R(d, 23, by - 5, 2, 2, BLACK)
    d.line([(21, by - 8), (25, by - 6)], fill=OUT)
    # wing
    wy = [-8, -3, 3, -3][wing]
    d.polygon([(9, by), (16, by), (11, by + wy)], fill=YD, outline=OUT)
    # feet
    d.line([(12, by + 8), (12, by + 10)], fill=(255, 130, 30, 255))
    d.line([(15, by + 8), (15, by + 10)], fill=(255, 130, 30, 255))
    return img


TG = (70, 170, 70, 255)
TS = (40, 120, 60, 255)
TSL = (110, 200, 90, 255)
SKIN = (200, 230, 120, 255)


def draw_shell(d, cx, bottom, spin=0):
    d.pieslice([cx - 11, bottom - 16, cx + 11, bottom + 6], 180, 360, fill=TS, outline=OUT)
    R(d, cx - 11, bottom - 6, 23, 3, (240, 230, 180, 255))
    d.line([(cx - 11, bottom - 3), (cx + 11, bottom - 3)], fill=OUT)
    # hex plates
    off = [0, 3, 6, -3][spin % 4]
    for hx in (cx - 6 + off, cx + off, cx + 6 + off):
        if cx - 9 <= hx <= cx + 9:
            d.polygon([(hx - 2, bottom - 9), (hx, bottom - 12), (hx + 2, bottom - 9), (hx, bottom - 7)],
                      fill=TSL, outline=(30, 90, 40, 255))
    d.point((cx - 5, bottom - 13), fill=TSL)


def draw_turtle(step=0):
    img = new(32, 32)
    d = ImageDraw.Draw(img)
    # legs
    for i, lx in enumerate((8, 19)):
        lift = (step + i) % 2
        R(d, lx, 25 - lift, 5, 5, OUT)
        R(d, lx + 1, 26 - lift, 3, 3, SKIN)
    # head
    hy = 14 + (step % 2)
    E(d, 21, hy, 30, hy + 8, SKIN)
    R(d, 26, hy + 2, 2, 3, BLACK)
    d.point((26, hy + 2), fill=WHITE)
    R(d, 27, hy + 6, 3, 1, OUT)
    # tail
    d.polygon([(4, 24), (1, 26), (5, 26)], fill=SKIN, outline=OUT)
    draw_shell(d, 14, 28, step)
    return img


def draw_turtle_shell(spin):
    img = new(32, 32)
    d = ImageDraw.Draw(img)
    draw_shell(d, 16, 30, spin)
    if spin % 2:
        d.line([(2, 26), (4, 26)], fill=WHITE)
        d.line([(1, 22), (3, 22)], fill=WHITE)
    return img


def draw_spike_live(h):
    img = new(32, 32)
    d = ImageDraw.Draw(img)
    R(d, 0, 28, 32, 4, (90, 90, 100, 255))
    d.line([(0, 28), (31, 28)], fill=OUT)
    for i in range(4):
        x = i * 8
        if h > 0:
            d.polygon([(x + 1, 28), (x + 4, 28 - h), (x + 7, 28)], fill=(200, 205, 215, 255), outline=OUT)
            d.line([(x + 4, 28 - h + 2), (x + 4, 27)], fill=WHITE)
        else:
            R(d, x + 2, 29, 5, 1, (40, 40, 48, 255))
    return img


GH = (170, 110, 230)
GHD = (110, 60, 170)


def draw_ghost_dog(size=32, phase=0, eye_col=(255, 255, 255, 255), angry=False, alpha=190, mouth_open=0):
    """Purple floating ghost dog. Drawn at 32 grid then scaled by size/32."""
    s = size // 32
    img = new(32, 32)
    d = ImageDraw.Draw(img)
    bob = [0, -1, -2, -1][phase % 4]
    col = GH + (255,)
    dcol = GHD + (255,)
    # wavy tail body
    y0 = 10 + bob
    d.rounded_rectangle([5, y0 + 2, 22, y0 + 15], radius=6, fill=col, outline=OUT)
    for i in range(4):
        x = 5 + i * 4 + (phase % 2)
        d.pieslice([x, y0 + 13, x + 4, y0 + 18], 0, 180, fill=col, outline=OUT)
    R(d, 6, y0 + 12, 16, 3, col)
    E(d, 8, y0 + 8, 18, y0 + 13, (200, 160, 245, 255), None)
    # head
    E(d, 14, y0 - 7, 28, y0 + 7, col)
    E(d, 22, y0 - 1, 31, y0 + 5, col)
    R(d, 29, y0, 2, 2, dcol)
    # ears
    d.polygon([(15, y0 - 5), (13, y0 - 10), (19, y0 - 6)], fill=dcol, outline=OUT)
    d.polygon([(20, y0 - 7), (22, y0 - 11), (24, y0 - 6)], fill=dcol, outline=OUT)
    # eyes
    R(d, 19, y0 - 3, 3, 4, eye_col)
    R(d, 24, y0 - 3, 3, 4, eye_col)
    R(d, 20, y0 - 1, 2, 2, BLACK)
    R(d, 25, y0 - 1, 2, 2, BLACK)
    if angry:
        d.line([(18, y0 - 5), (22, y0 - 3)], fill=OUT)
        d.line([(28, y0 - 5), (24, y0 - 3)], fill=OUT)
    # mouth
    if mouth_open:
        R(d, 23, y0 + 3, 6, 2 + mouth_open, BLACK)
        R(d, 24, y0 + 3, 1, 1, WHITE)
        R(d, 27, y0 + 3, 1, 1, WHITE)
    else:
        d.line([(23, y0 + 4), (25, y0 + 5), (27, y0 + 4)], fill=OUT)
    # wispy tail
    d.line([(5, y0 + 6), (2, y0 + 3 + (phase % 2)), (1, y0)], fill=col, width=2)
    img = alpha_mul(img, alpha / 255)
    if s > 1:
        img = img.resize((size, size), Image.NEAREST)
    return img


def make_enemies():
    out = []
    out.append(save(sheet([draw_slime(s) for s in (0, 2, 4, 2)]), "enemies", "slime.png"))
    d1 = draw_slime(6, "x")
    d2 = new(32, 32)
    dd = ImageDraw.Draw(d2)
    E(dd, 3, 26, 29, 31, SL_G)
    for ex in (11, 19):
        dd.line([(ex, 27), (ex + 2, 29)], fill=BLACK)
        dd.line([(ex, 29), (ex + 2, 27)], fill=BLACK)
    out.append(save(sheet([d1, d2]), "enemies", "slime_dead.png"))
    out.append(save(sheet([draw_bird(i) for i in range(4)]), "enemies", "bird.png"))
    out.append(save(sheet([draw_bird(0, True), draw_bird(1, True)]), "enemies", "bird_dive.png"))
    out.append(save(sheet([draw_turtle(i) for i in range(4)]), "enemies", "turtle.png"))
    out.append(save(sheet([draw_turtle_shell(0), draw_turtle_shell(1)]), "enemies", "turtle_shell.png"))
    out.append(save(sheet([draw_spike_live(h) for h in (0, 4, 10, 16)]), "enemies", "spike_live.png"))
    out.append(save(sheet([draw_ghost_dog(32, i) for i in range(4)]), "enemies", "ghost_dog.png"))
    return out


# =====================================================================
# BOSS (64x64)
# =====================================================================
def boss_frame(phase, mode="idle"):
    f = new(64, 64)
    eye = (255, 60, 60, 255)
    g = draw_ghost_dog(64, phase, eye_col=eye, angry=True, alpha=235,
                       mouth_open=(phase % 2 + 1) if mode == "attack" else 0)
    if mode == "hurt":
        g = tint(g, (255, 255, 255), 0.6 if phase == 0 else 0.0)
        g = tint(g, (255, 80, 80), 0.0 if phase == 0 else 0.4)
    if mode == "death":
        g = alpha_mul(g, [1.0, 0.75, 0.5, 0.25][phase])
        g = g.rotate([0, -10, 15, -25][phase], resample=Image.NEAREST, center=(32, 32))
    f.paste(g, (0, 0), g)
    d = ImageDraw.Draw(f)
    bob = [0, -2, -4, -2][phase % 4]
    # golden crown
    if mode != "death" or phase < 2:
        cy = 4 + bob
        d.polygon([(30, cy + 8), (30, cy), (34, cy + 4), (38, cy - 1), (42, cy + 4), (46, cy), (46, cy + 8)],
                  fill=GOLD, outline=OUT)
        R(d, 37, cy + 4, 2, 2, RED)
        d.point((32, cy + 5), fill=(80, 200, 255, 255))
        d.point((44, cy + 5), fill=(80, 200, 255, 255))
    if mode == "attack":
        # purple energy orbs
        for k in range(phase + 1):
            ox, oy = 58 - k * 3, 30 + bob + k * 4
            E(d, ox - 3, oy - 3, ox + 3, oy + 3, (220, 120, 255, 255), (90, 20, 140, 255))
            d.point((ox - 1, oy - 1), fill=WHITE)
        # aura
        for k in range(10):
            a = k * 0.63 + phase
            d.point((int(32 + 30 * math.cos(a)), int(32 + 28 * math.sin(a))), fill=(220, 150, 255, 255))
    if mode == "hurt":
        for k in range(4):
            tiny_star(d, 10 + k * 14, 6 + (k % 2) * 4)
    if mode == "death":
        for k in range(phase * 4 + 3):
            x, y = random.randint(4, 60), random.randint(4, 60)
            tiny_star(d, x, y, (220, 150, 255, 255))
    return f


def make_boss():
    out = []
    out.append(save(sheet([boss_frame(i, "idle") for i in range(4)]), "boss", "boss_idle.png"))
    out.append(save(sheet([boss_frame(i, "attack") for i in range(4)]), "boss", "boss_attack.png"))
    out.append(save(sheet([boss_frame(i, "hurt") for i in range(2)]), "boss", "boss_hurt.png"))
    out.append(save(sheet([boss_frame(i, "death") for i in range(4)]), "boss", "boss_death.png"))
    return out


# =====================================================================
# TILESETS (128x128 = 4x4 tiles of 32x32)
# =====================================================================
def noise_fill(d, x, y, w, h, base, dots, n):
    R(d, x, y, w, h, base)
    for _ in range(n):
        d.point((x + random.randrange(w), y + random.randrange(h)), fill=random.choice(dots))


def tileset(theme):
    img = new(128, 128)
    d = ImageDraw.Draw(img)
    if theme == "grass":
        top, topd, dirt, dirtd = (96, 200, 70, 255), (60, 150, 50, 255), (170, 110, 60, 255), (130, 80, 40, 255)
        dots = [dirtd, (190, 130, 80, 255), (120, 120, 120, 255)]
    elif theme == "forest":
        top, topd, dirt, dirtd = (40, 110, 60, 255), (25, 75, 40, 255), (80, 60, 50, 255), (55, 40, 35, 255)
        dots = [dirtd, (100, 80, 60, 255), (60, 90, 60, 255)]
    else:
        top, topd, dirt, dirtd = (150, 150, 165, 255), (110, 110, 125, 255), (95, 95, 110, 255), (65, 65, 80, 255)
        dots = [dirtd, (120, 120, 135, 255)]

    def ground(tx, ty, left=False, right=False, has_top=True):
        x, y = tx * 32, ty * 32
        if theme == "castle":
            R(d, x, y, 32, 32, dirt)
            for row in range(4):
                off = 8 if row % 2 else 0
                for col in range(-1, 3):
                    bx = x + col * 16 + off
                    x0, x1 = max(bx, x), min(bx + 15, x + 31)
                    if x1 > x0:
                        d.rectangle([x0, y + row * 8, x1, y + row * 8 + 7], fill=top if row == 0 and has_top else dirt,
                                    outline=dirtd)
                        d.point((x0 + 1, y + row * 8 + 1), fill=(130, 130, 145, 255))
        else:
            noise_fill(d, x, y, 32, 32, dirt, dots, 40)
            if has_top:
                R(d, x, y, 32, 8, top)
                R(d, x, y + 8, 32, 2, topd)
                for i in range(0, 32, 4):
                    R(d, x + i + 1, y + 10, 2, 1 + (i * 7) % 3, topd)
                    d.point((x + i + 2, y), fill=(160, 240, 120, 255) if theme == "grass" else (70, 150, 80, 255))
        if left:
            R(d, x, y, 2, 32, OUT)
        if right:
            R(d, x + 30, y, 2, 32, OUT)
        if has_top:
            R(d, x, y, 32, 1, OUT)

    # row 0: top-left, top-mid, top-right, single
    ground(0, 0, left=True)
    ground(1, 0)
    ground(2, 0, right=True)
    ground(3, 0, left=True, right=True)
    # row 1: fill-left, fill, fill-right, platform (thin)
    ground(0, 1, left=True, has_top=False)
    ground(1, 1, has_top=False)
    ground(2, 1, right=True, has_top=False)
    x, y = 96, 32
    R(d, x, y, 32, 12, topd)
    R(d, x, y, 32, 5, top)
    d.rectangle([x, y, x + 31, y + 11], outline=OUT)
    # row 2: theme blocks
    if theme == "grass":
        # ? block, brick, bush, flower
        R(d, 0, 64, 32, 32, GOLD)
        d.rectangle([0, 64, 31, 95], outline=OUT)
        for px, py in ((2, 66), (28, 66), (2, 92), (28, 92)):
            d.point((px, py), fill=DGOLD)
        d.text((12, 72), "?", fill=WHITE)
        R(d, 32, 64, 32, 32, (190, 90, 50, 255))
        for row in range(4):
            off = 8 if row % 2 else 0
            for c in range(-1, 3):
                bx = 32 + c * 16 + off
                if min(bx + 15, 63) > max(bx, 32):
                    d.rectangle([max(bx, 32), 64 + row * 8, min(bx + 15, 63), 71 + row * 8], outline=(110, 50, 30, 255))
        E(d, 66, 76, 94, 95, (60, 170, 60, 255))
        E(d, 72, 70, 88, 86, (80, 200, 70, 255))
        d.line([(112, 95), (112, 80)], fill=(40, 130, 40, 255), width=2)
        for a in range(5):
            ang = a * 1.256
            E(d, int(112 + 4 * math.cos(ang)) - 3, int(77 + 4 * math.sin(ang)) - 3,
              int(112 + 4 * math.cos(ang)) + 3, int(77 + 4 * math.sin(ang)) + 3, (255, 120, 160, 255))
        E(d, 109, 74, 115, 80, GOLD)
    elif theme == "forest":
        # log, mushroom, tree trunk, thorn bush
        R(d, 0, 76, 32, 14, (110, 70, 40, 255))
        d.rectangle([0, 76, 31, 89], outline=OUT)
        E(d, 24, 76, 31, 89, (190, 150, 100, 255))
        d.line([(4, 80), (20, 80)], fill=(80, 50, 30, 255))
        E(d, 36, 66, 60, 84, RED)
        for px, py in ((42, 72), (50, 70), (54, 77)):
            E(d, px, py, px + 3, py + 3, WHITE, None)
        R(d, 44, 84, 8, 11, (240, 230, 210, 255))
        d.rectangle([44, 84, 51, 94], outline=OUT)
        R(d, 72, 64, 16, 32, (90, 60, 40, 255))
        d.rectangle([72, 64, 87, 95], outline=OUT)
        for yy in range(66, 95, 5):
            d.line([(75, yy), (78, yy + 2)], fill=(60, 40, 25, 255))
        E(d, 98, 74, 126, 95, (30, 80, 40, 255))
        for k in range(8):
            ang = k * 0.785
            d.line([(112, 85), (int(112 + 14 * math.cos(ang)), int(85 + 11 * math.sin(ang)))], fill=(200, 200, 160, 255))
    else:
        # torch, window, chain, banner
        R(d, 14, 74, 4, 16, (100, 70, 40, 255))
        E(d, 10, 64, 22, 78, (255, 150, 30, 255), None)
        E(d, 13, 68, 19, 76, (255, 230, 100, 255), None)
        d.rectangle([36, 66, 59, 93], fill=(20, 20, 40, 255), outline=OUT)
        d.line([(47, 66), (47, 93)], fill=OUT)
        d.line([(36, 79), (59, 79)], fill=OUT)
        d.point((40, 70), fill=WHITE)
        for yy in range(64, 96, 6):
            d.ellipse([76, yy, 82, yy + 6], outline=(140, 140, 150, 255))
        d.polygon([(100, 64), (124, 64), (124, 92), (112, 86), (100, 92)], fill=(120, 30, 140, 255), outline=OUT)
        star_shape(d, 112, 74, 6, GOLD)
    # row 3: decorations / hazard-ish
    for i in range(4):
        x = i * 32
        if theme == "grass":
            # grass tufts and rocks
            if i < 2:
                for k in range(5):
                    d.line([(x + 4 + k * 6, 127), (x + 3 + k * 6 + i, 116 + (k % 3) * 2)], fill=(80, 190, 60, 255), width=2)
            else:
                E(d, x + 4, 110, x + 28, 127, (140, 140, 150, 255))
                E(d, x + 8, 113, x + 16, 119, (180, 180, 190, 255), None)
        elif theme == "forest":
            if i < 2:
                for k in range(3):
                    E(d, x + 2 + k * 9, 104 + (k % 2) * 6, x + 14 + k * 9, 124, (20, 70 + k * 15, 35, 255))
            else:
                d.line([(x + 16, 96), (x + 16, 127)], fill=(50, 110, 50, 255), width=2)
                for yy in range(100, 126, 6):
                    E(d, x + 17, yy, x + 23, yy + 4, (60, 140, 60, 255), None)
        else:
            noise_fill(d, x, 96, 32, 32, (60, 60, 75, 255), [(40, 40, 50, 255), (80, 80, 95, 255)], 50)
            if i % 2:
                for k in range(3):
                    d.line([(x + 6 + k * 10, 96), (x + 4 + k * 10, 110)], fill=(30, 30, 40, 255))
            d.rectangle([x, 96, x + 31, 127], outline=OUT)
    return img


# =====================================================================
# ENVIRONMENT ITEMS
# =====================================================================
def coin_frame(i, red=False):
    f = new(16, 16)
    d = ImageDraw.Draw(f)
    widths = [6, 4, 1, 4]
    w = widths[i]
    c1, c2, c3 = ((255, 80, 60, 255), (170, 20, 30, 255), (255, 190, 170, 255)) if red else (GOLD, DGOLD, (255, 250, 180, 255))
    d.ellipse([8 - w - 1, 1, 8 + w, 14], fill=c1, outline=OUT)
    if w >= 4:
        d.ellipse([8 - w + 2, 4, 8 + w - 3, 11], outline=c2)
        R(d, 7, 5, 2, 6, c2)
        d.point((8 - w + 1, 4), fill=c3)
    if red and w >= 4:
        # tiny skull marking
        R(d, 6, 6, 4, 3, WHITE)
        d.point((6, 7), fill=BLACK)
        d.point((9, 7), fill=BLACK)
    if i == 0:
        d.point((13, 2), fill=WHITE)
    return f


def make_environment():
    out = []
    for th in ("grass", "forest", "castle"):
        out.append(save(tileset(th), "environment", f"tileset_{th}.png"))
    out.append(save(sheet([coin_frame(i) for i in range(4)]), "environment", "coin.png"))
    out.append(save(sheet([coin_frame(i, True) for i in range(4)]), "environment", "coin_trap.png"))
    # checkpoint flag 32x48
    frames = []
    for active in (False, True):
        f = new(32, 48)
        d = ImageDraw.Draw(f)
        R(d, 6, 44, 14, 4, (120, 120, 130, 255))
        d.rectangle([6, 44, 19, 47], outline=OUT)
        R(d, 11, 4, 3, 40, (220, 220, 220, 255))
        d.rectangle([11, 4, 13, 43], outline=OUT)
        E(d, 9, 1, 15, 7, GOLD)
        if active:
            d.polygon([(14, 7), (30, 13), (14, 20)], fill=(60, 220, 90, 255), outline=OUT)
            # paw print
            E(d, 18, 12, 22, 16, WHITE, None)
            for px in (17, 20, 23):
                d.point((px, 10 if px == 20 else 11), fill=WHITE)
            tiny_star(d, 27, 4)
        else:
            d.polygon([(14, 26), (26, 30), (14, 35)], fill=(150, 150, 160, 255), outline=OUT)
        frames.append(f)
    out.append(save(sheet(frames), "environment", "checkpoint.png"))
    # lava 32x16
    lf = []
    for i in range(4):
        f = new(32, 16)
        d = ImageDraw.Draw(f)
        R(d, 0, 0, 32, 16, (220, 60, 20, 255))
        for x in range(32):
            h = int(3 + 2 * math.sin((x + i * 4) * 0.4))
            R(d, x, 0, 1, h, CLEAR)
            d.point((x, h), fill=(255, 200, 60, 255))
            d.point((x, h + 1), fill=(255, 140, 30, 255))
        for k in range(6):
            d.point(((k * 7 + i * 3) % 32, 8 + (k * 5) % 7), fill=(255, 170, 40, 255))
        bx = (i * 9 + 5) % 28
        E(d, bx, 5 - i % 2, bx + 3, 8 - i % 2, (255, 230, 120, 255), (200, 40, 10, 255))
        lf.append(f)
    out.append(save(sheet(lf), "environment", "lava.png"))
    return out


# =====================================================================
# TRAPS
# =====================================================================
def plank(w, h, base, dark, light):
    f = new(w, h)
    d = ImageDraw.Draw(f)
    R(d, 0, 0, w, h, base)
    R(d, 0, 0, w, 3, light)
    R(d, 0, h - 3, w, 3, dark)
    for x in range(8, w, 12):
        d.line([(x, 3), (x, h - 4)], fill=dark)
    d.rectangle([0, 0, w - 1, h - 1], outline=OUT)
    return f, d


def make_traps():
    out = []
    f, d = plank(32, 16, BROWN, DBROWN, (190, 130, 80, 255))
    d.line([(10, 4), (14, 9), (12, 12)], fill=OUT)  # crack
    out.append(save(f, "traps", "platform_fall.png"))
    f, d = plank(32, 16, (200, 50, 50, 255), (130, 20, 30, 255), (250, 110, 100, 255))
    out.append(save(f, "traps", "platform_fake.png"))
    f, d = plank(48, 16, (60, 120, 220, 255), (30, 70, 150, 255), (130, 180, 255, 255))
    for x in (6, 40):
        E(d, x - 2, 6, x + 2, 10, (200, 200, 210, 255))
    d.polygon([(20, 8), (24, 5), (24, 11)], fill=WHITE)
    d.polygon([(28, 8), (24, 5), (24, 11)], fill=WHITE)
    out.append(save(f, "traps", "platform_move.png"))
    # spike 16x16
    f = new(16, 16)
    d = ImageDraw.Draw(f)
    R(d, 0, 13, 16, 3, (90, 90, 100, 255))
    for x in (0, 8):
        d.polygon([(x, 13), (x + 4, 2), (x + 7, 13)], fill=(210, 215, 225, 255), outline=OUT)
        d.line([(x + 4, 4), (x + 4, 12)], fill=WHITE)
    d.line([(0, 15), (15, 15)], fill=OUT)
    out.append(save(f, "traps", "spike.png"))
    # invisible block: dashed outline
    f = new(32, 32)
    d = ImageDraw.Draw(f)
    R(d, 1, 1, 30, 30, (255, 255, 255, 40))
    for i in range(0, 32, 4):
        for (x, y) in ((i, 0), (i, 31), (0, i), (31, i)):
            R(d, x, y, 2, 1, (255, 255, 255, 170)) if y in (0, 31) else R(d, x, y, 1, 2, (255, 255, 255, 170))
    d.text((12, 10), "?", fill=(255, 255, 255, 110))
    out.append(save(f, "traps", "block_invisible.png"))
    # push block: metal with arrows
    f = new(32, 32)
    d = ImageDraw.Draw(f)
    R(d, 0, 0, 32, 32, (150, 155, 170, 255))
    R(d, 2, 2, 28, 3, (200, 205, 215, 255))
    R(d, 2, 27, 28, 3, (100, 105, 120, 255))
    d.rectangle([0, 0, 31, 31], outline=OUT)
    for (x, y) in ((3, 3), (27, 3), (3, 27), (27, 27)):
        R(d, x, y, 2, 2, (80, 80, 90, 255))
    d.polygon([(8, 16), (16, 9), (16, 13), (24, 13), (24, 19), (16, 19), (16, 23)], fill=(255, 200, 40, 255), outline=OUT)
    out.append(save(f, "traps", "block_push.png"))
    # falling block: angry stone (thwomp-like)
    f = new(32, 32)
    d = ImageDraw.Draw(f)
    noise_fill(d, 0, 0, 32, 32, (120, 120, 140, 255), [(95, 95, 115, 255), (145, 145, 160, 255)], 60)
    d.rectangle([0, 0, 31, 31], outline=OUT)
    for x in (7, 19):
        R(d, x, 10, 6, 6, WHITE)
        R(d, x + 2 if x == 7 else x + 1, 12, 3, 3, BLACK)
    d.line([(6, 7), (13, 10)], fill=OUT, width=2)
    d.line([(25, 7), (18, 10)], fill=OUT, width=2)
    R(d, 9, 21, 14, 4, BLACK)
    for x in range(10, 22, 3):
        R(d, x, 21, 2, 2, WHITE)
    for x in (0, 30):
        for y in (4, 14, 24):
            R(d, x if x == 0 else x, y, 2, 3, (80, 80, 95, 255))
    out.append(save(f, "traps", "falling_block.png"))
    # closing wall 32x64
    f = new(32, 64)
    d = ImageDraw.Draw(f)
    R(d, 0, 0, 32, 64, (100, 90, 110, 255))
    for row in range(8):
        off = 8 if row % 2 else 0
        for c in range(-1, 3):
            bx = c * 16 + off
            (min(bx + 15, 31) > max(bx, 0)) and d.rectangle([max(bx, 0), row * 8, min(bx + 15, 31), row * 8 + 7], outline=(60, 50, 70, 255))
    for y in range(4, 64, 10):
        d.polygon([(31, y), (31, y + 6), (28, y + 3)], fill=(220, 220, 230, 255), outline=OUT)
    d.rectangle([0, 0, 31, 63], outline=OUT)
    out.append(save(f, "traps", "wall_close.png"))
    # ceiling obstacle: hanging spiked ball/stalactite
    f = new(32, 32)
    d = ImageDraw.Draw(f)
    R(d, 0, 0, 32, 6, (90, 90, 100, 255))
    d.line([(0, 6), (31, 6)], fill=OUT)
    for x in (2, 12, 22):
        d.polygon([(x, 6), (x + 4, 30 if x == 12 else 22), (x + 8, 6)], fill=(170, 160, 150, 255), outline=OUT)
        d.line([(x + 3, 8), (x + 4, 18 if x == 12 else 14)], fill=(220, 210, 200, 255))
    out.append(save(f, "traps", "ceiling_obstacle.png"))
    return out


# =====================================================================
# UI
# =====================================================================
FONT = {
    "D": ["1110.", "1..1.", "1...1", "1...1", "1...1", "1..1.", "1110."],
    "O": [".111.", "1...1", "1...1", "1...1", "1...1", "1...1", ".111."],
    "G": [".111.", "1...1", "1....", "1.111", "1...1", "1...1", ".111."],
    "M": ["1...1", "11.11", "1.1.1", "1.1.1", "1...1", "1...1", "1...1"],
    "A": [".111.", "1...1", "1...1", "11111", "1...1", "1...1", "1...1"],
    "R": ["1111.", "1...1", "1...1", "1111.", "1.1..", "1..1.", "1...1"],
    "I": ["11111", "..1..", "..1..", "..1..", "..1..", "..1..", "11111"],
    " ": ["....."] * 7,
}


def heart(full=True):
    f = new(16, 16)
    d = ImageDraw.Draw(f)
    rows = ["..XXX...XXX..", ".XXXXX.XXXXX.", "XXXXXXXXXXXXX", "XXXXXXXXXXXXX", "XXXXXXXXXXXXX",
            ".XXXXXXXXXXX.", "..XXXXXXXXX..", "...XXXXXXX...", "....XXXXX....", ".....XXX.....", "......X......"]
    mask = new(16, 16)
    md = ImageDraw.Draw(mask)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "X":
                md.point((x + 1, y + 2), fill=(RED if full else (60, 40, 50, 255)))
    f = outline_img(mask)
    d = ImageDraw.Draw(f)
    if full:
        R(d, 3, 4, 2, 2, (255, 170, 170, 255))
        d.point((4, 6), fill=(255, 120, 120, 255))
        for x in range(5, 10):
            d.point((x, 11), fill=DRED)
    else:
        d.point((3, 4), fill=(110, 90, 100, 255))
    return f


def make_logo():
    W, H = 320, 80
    img = new(W, H)
    d = ImageDraw.Draw(img)
    text = "DOG MARIO"
    s = 5
    total = len(text) * 6 * s - s
    x0 = (W - total) // 2
    y0 = 14
    colors = [RED, (255, 140, 30, 255), GOLD, None, (80, 200, 80, 255), (60, 150, 240, 255),
              (150, 90, 230, 255), (240, 90, 170, 255), RED]
    layer = new(W, H)
    ld = ImageDraw.Draw(layer)
    shadow = new(W, H)
    sd = ImageDraw.Draw(shadow)
    for i, ch in enumerate(text):
        g = FONT[ch]
        cx = x0 + i * 6 * s
        bounce = -3 if i % 2 else 0
        for gy, row in enumerate(g):
            for gx, b in enumerate(row):
                if b == "1":
                    c = colors[i]
                    px, py = cx + gx * s, y0 + gy * s + bounce
                    R(ld, px, py, s, s, c)
                    R(ld, px, py, s, 1, tuple(min(255, v + 70) for v in c[:3]) + (255,))
                    R(sd, px + 4, py + 4, s, s, (40, 20, 60, 255))
    shadow = outline_img(outline_img(shadow, (40, 20, 60, 255)), (40, 20, 60, 255))
    layer = outline_img(outline_img(layer, WHITE), OUT)
    img.paste(shadow, (0, 0), shadow)
    img.paste(layer, (0, 0), layer)
    # paw prints decorating
    for (px, py) in ((8, 60), (296, 8)):
        E(d, px, py + 4, px + 10, py + 12, BROWN)
        for k, (ox, oy) in enumerate(((0, 0), (4, -2), (8, 0))):
            E(d, px + ox - 1, py + oy - 1, px + ox + 3, py + oy + 3, BROWN)
    for k in range(6):
        tiny_star(d, 20 + k * 55, 6 + (k % 2) * 66)
    return img


def sky_gradient(d, W, H, top, bottom):
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)) + (255,)
        # banded gradient for pixel-art look
        d.line([(0, y), (W, y)], fill=c)


def banded(c, y, H, steps=12):
    return c


def cloud(d, x, y, s, col=(255, 255, 255, 255), shade=(220, 230, 245, 255)):
    for ox, oy, r in ((0, 8, 10), (12, 2, 13), (28, 6, 11), (40, 10, 8)):
        d.ellipse([x + ox * s, y + oy * s, x + (ox + r * 2) * s, y + (oy + r * 2) * s], fill=col)
    d.rectangle([x + 4 * s, y + 22 * s, x + 52 * s, y + 28 * s], fill=shade)


def hills(d, W, H, base_y, amp, freq, phase, col, top_col=None):
    pts = [(0, H)]
    for x in range(0, W + 8, 8):
        y = base_y + amp * math.sin(x * freq + phase) + amp * 0.4 * math.sin(x * freq * 2.7 + phase)
        pts.append((x, int(y) // 4 * 4))
    pts.append((W, H))
    d.polygon(pts, fill=col)
    if top_col:
        for x, y in pts[1:-1]:
            d.rectangle([x, y, x + 7, y + 3], fill=top_col)


def pixelate(img, k=4):
    w, h = img.size
    return img.resize((w // k, h // k), Image.NEAREST).resize((w, h), Image.NEAREST)


def bg_sunny(menu=False):
    W, H = 1280, 720
    img = new(W, H)
    d = ImageDraw.Draw(img)
    sky_gradient(d, W, H, (90, 170, 255), (200, 235, 255))
    # sun
    d.ellipse([1040, 60, 1160, 180], fill=(255, 240, 150, 255))
    d.ellipse([1056, 76, 1144, 164], fill=(255, 220, 80, 255))
    for k in range(12):
        a = k * math.pi / 6
        d.line([(1100 + 75 * math.cos(a), 120 + 75 * math.sin(a)), (1100 + 100 * math.cos(a), 120 + 100 * math.sin(a))],
               fill=(255, 230, 120, 255), width=8)
    for (x, y, s) in ((80, 80, 3), (420, 140, 2), (700, 60, 3), (900, 230, 2), (250, 260, 2)):
        cloud(d, x, y, s)
    hills(d, W, H, 470, 50, 0.006, 0.5, (120, 200, 140, 255), (150, 220, 160, 255))
    hills(d, W, H, 540, 35, 0.009, 2.0, (80, 180, 80, 255), (110, 210, 90, 255))
    # trees on mid hills
    for x in range(60, W, 230):
        y = 520 + int(25 * math.sin(x * 0.01))
        d.rectangle([x + 18, y, x + 30, y + 50], fill=(110, 70, 40, 255))
        d.ellipse([x - 10, y - 50, x + 58, y + 14], fill=(50, 150, 60, 255))
        d.ellipse([x, y - 40, x + 30, y - 14], fill=(80, 190, 80, 255))
    # ground strip
    d.rectangle([0, 640, W, H], fill=(170, 110, 60, 255))
    d.rectangle([0, 624, W, 648], fill=(96, 200, 70, 255))
    for x in range(0, W, 16):
        d.rectangle([x, 616 + (x // 16 % 2) * 4, x + 7, 628], fill=(130, 220, 90, 255))
    for x in range(30, W, 140):
        d.ellipse([x, 600, x + 12, 612], fill=(255, 120, 160, 255) if x % 280 else GOLD)
    img = pixelate(img, 4)
    if menu:
        dog = draw_dog(0, eye="happy", tongue=True, tail=1).resize((192, 192), Image.NEAREST)
        img.paste(dog, (160, 440), dog)
        sl = draw_slime(2).resize((128, 128), Image.NEAREST)
        img.paste(sl, (960, 500), sl)
        bd = draw_bird(1).resize((128, 128), Image.NEAREST)
        img.paste(bd, (820, 260), bd)
    return img


def bg_forest():
    W, H = 1280, 720
    img = new(W, H)
    d = ImageDraw.Draw(img)
    sky_gradient(d, W, H, (20, 30, 50), (60, 90, 80))
    d.ellipse([980, 80, 1080, 180], fill=(230, 240, 210, 255))
    d.ellipse([1000, 90, 1070, 160], fill=(30, 40, 60, 255))  # crescent moon cut
    for _ in range(80):
        x, y = random.randrange(W), random.randrange(300)
        d.point((x, y), fill=(220, 220, 255, 255))
    layers = [((30, 60, 55, 255), 0.6, 380), ((22, 48, 40, 255), 0.8, 440), ((14, 32, 28, 255), 1.0, 500)]
    for col, sc, base in layers:
        for x in range(-40, W + 40, int(90 * sc)):
            h = int((200 + random.randint(0, 120)) * sc)
            w = int(60 * sc)
            d.polygon([(x, base + 120), (x + w // 2, base - h), (x + w, base + 120)], fill=col)
            d.rectangle([x + w // 2 - 6, base + 60, x + w // 2 + 6, H], fill=col)
        d.rectangle([0, base + 110, W, H], fill=col)
    # fireflies and fog
    for _ in range(40):
        x, y = random.randrange(W), random.randrange(350, 650)
        d.rectangle([x, y, x + 4, y + 4], fill=(200, 255, 120, 255))
    for y in range(560, 640, 8):
        d.rectangle([0, y, W, y + 3], fill=(120, 150, 140, 255) if y % 16 else (90, 120, 110, 255))
    d.rectangle([0, 640, W, H], fill=(55, 40, 35, 255))
    d.rectangle([0, 624, W, 644], fill=(40, 110, 60, 255))
    # glowing eyes in the dark
    for (x, y) in ((200, 470), (760, 500), (1150, 450)):
        d.rectangle([x, y, x + 8, y + 6], fill=(255, 220, 40, 255))
        d.rectangle([x + 20, y, x + 28, y + 6], fill=(255, 220, 40, 255))
    return pixelate(img, 4)


def bg_castle():
    W, H = 1280, 720
    img = new(W, H)
    d = ImageDraw.Draw(img)
    sky_gradient(d, W, H, (30, 10, 40), (120, 40, 70))
    d.ellipse([140, 80, 300, 240], fill=(255, 120, 120, 255))
    d.ellipse([160, 100, 280, 220], fill=(230, 80, 90, 255))
    for _ in range(60):
        d.point((random.randrange(W), random.randrange(320)), fill=(255, 200, 230, 255))
    # distant castle silhouette
    far = (55, 25, 60, 255)
    d.rectangle([380, 300, 900, 600], fill=far)
    for x in range(380, 900, 40):
        d.rectangle([x, 284, x + 20, 300], fill=far)
    for tx, th in ((360, 180), (600, 120), (880, 200)):
        d.rectangle([tx, th, tx + 70, 600], fill=far)
        d.polygon([(tx - 10, th), (tx + 35, th - 80), (tx + 80, th)], fill=(80, 30, 80, 255))
        for wy in range(th + 30, 560, 60):
            d.rectangle([tx + 28, wy, tx + 42, wy + 20], fill=(255, 200, 60, 255))
    for x in range(420, 880, 70):
        d.rectangle([x, 380, x + 14, 404], fill=(255, 200, 60, 255))
    # bats
    for (x, y) in ((500, 150), (560, 190), (1000, 120), (1080, 170), (760, 90)):
        d.polygon([(x, y), (x - 20, y - 10), (x - 12, y + 2), (x - 4, y - 2)], fill=BLACK)
        d.polygon([(x, y), (x + 20, y - 10), (x + 12, y + 2), (x + 4, y - 2)], fill=BLACK)
    # foreground stone wall with pillars
    d.rectangle([0, 560, W, H], fill=(70, 65, 85, 255))
    for row, y in enumerate(range(560, H, 24)):
        off = 32 if row % 2 else 0
        for x in range(-64 + off, W, 64):
            d.rectangle([x, y, x + 62, y + 22], outline=(45, 40, 60, 255), width=2)
    for x in range(80, W, 320):
        d.rectangle([x, 420, x + 48, 560], fill=(90, 85, 105, 255))
        d.ellipse([x + 8, 400, x + 40, 432], fill=(255, 150, 30, 255))
        d.ellipse([x + 16, 410, x + 32, 428], fill=(255, 230, 100, 255))
    # lava glow
    d.rectangle([0, 690, W, H], fill=(230, 70, 20, 255))
    for x in range(0, W, 24):
        d.rectangle([x, 682, x + 12, 690], fill=(255, 170, 40, 255))
    return pixelate(img, 4)


def make_ui():
    out = []
    out.append(save(heart(True), "ui", "heart.png"))
    out.append(save(heart(False), "ui", "heart_empty.png"))
    out.append(save(make_logo(), "ui", "logo.png"))
    f = new(16, 16)
    d = ImageDraw.Draw(f)
    star_shape(d, 7.5, 8.5, 7.4, GOLD)
    d.point((6, 6), fill=WHITE)
    d.point((7, 5), fill=(255, 250, 190, 255))
    out.append(save(f, "ui", "star.png"))
    bgs = {"bg_menu.png": bg_sunny(True), "bg_level1.png": bg_sunny(False),
           "bg_level2.png": bg_forest(), "bg_level3.png": bg_castle()}
    for name, im in bgs.items():
        out.append(save(im, "ui", name))
        im.save(os.path.join(ROOT, "backgrounds", name))
    return out


# =====================================================================
# EFFECTS (extras used by gameplay juice)
# =====================================================================
def make_effects():
    out = []
    dust = []
    for i in range(4):
        f = new(16, 16)
        d = ImageDraw.Draw(f)
        r = 2 + i * 2
        a = 255 - i * 55
        for cx, cy in ((5, 11), (11, 11), (8, 8)):
            d.ellipse([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2], fill=(230, 220, 200, a))
        dust.append(f)
    out.append(save(sheet(dust), "effects", "dust.png"))
    sp = []
    for i in range(4):
        f = new(16, 16)
        d = ImageDraw.Draw(f)
        r = [2, 5, 7, 4][i]
        d.line([(8 - r, 8), (8 + r, 8)], fill=(255, 250, 180, 255))
        d.line([(8, 8 - r), (8, 8 + r)], fill=(255, 250, 180, 255))
        if i in (1, 2):
            d.point((8 - r // 2, 8 - r // 2), fill=GOLD)
            d.point((8 + r // 2, 8 + r // 2), fill=GOLD)
            d.point((8 + r // 2, 8 - r // 2), fill=GOLD)
            d.point((8 - r // 2, 8 + r // 2), fill=GOLD)
        d.point((8, 8), fill=WHITE)
        sp.append(f)
    out.append(save(sheet(sp), "effects", "sparkle.png"))
    ex = []
    for i in range(4):
        f = new(32, 32)
        d = ImageDraw.Draw(f)
        r = 4 + i * 4
        cols = [(255, 255, 200, 255), (255, 200, 60, 255), (255, 120, 30, 220), (120, 100, 100, 140)]
        d.ellipse([16 - r, 16 - r, 16 + r, 16 + r], fill=cols[i])
        if i < 3:
            d.ellipse([16 - r // 2, 16 - r // 2, 16 + r // 2, 16 + r // 2], fill=(255, 255, 230, 255))
        ex.append(f)
    out.append(save(sheet(ex), "effects", "poof.png"))
    return out


def main():
    files = []
    for fn in (make_player, make_enemies, make_boss, make_environment, make_traps, make_ui, make_effects):
        files += fn()
    print(f"Generated {len(files)} sprite files")
    for p in files:
        with Image.open(p) as im:
            print(f"{os.path.relpath(p, SPR):42s} {im.size[0]}x{im.size[1]} {im.mode}")


if __name__ == "__main__":
    main()
