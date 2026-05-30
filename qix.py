#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
****************************|
|  Written by Russ McEwen   |
|       12/10/2025          |
|     Just playin!          |
|---------------------------|
|   Python / pygame port    |
|    with modular splash    |
|****************************
"""

import math
import random
import sys

import pygame

# ==========================================================
#  ***** DISPLAY / SETUP CONSTANTS *****
# ==========================================================

xmax = 1100
xmin = 0
ymax = 700
ymin = 0

SCREEN_WIDTH = xmax
SCREEN_HEIGHT = ymax

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("              CLICK TO CHANGE PALETTE  ")
clock = pygame.time.Clock()
font_small = pygame.font.SysFont("consolas", 12)
font_medium = pygame.font.SysFont("consolas", 16)
font_large = pygame.font.SysFont("consolas", 24)
font_huge = pygame.font.SysFont("consolas", 72)

# ==========================================================
#  ***** COLOR HELPERS *****
# ==========================================================

def RGB(r, g, b):
    return (int(r), int(g), int(b))

COLOR_BLACK   = RGB(0, 0, 0)
COLOR_BLUE    = RGB(0, 0, 255)
COLOR_RED     = RGB(255, 0, 0)
COLOR_GREEN   = RGB(0, 255, 0)
COLOR_CYAN    = RGB(0, 255, 255)
COLOR_MAGENTA = RGB(255, 0, 255)
COLOR_YELLOW  = RGB(255, 255, 0)
COLOR_WHITE   = RGB(255, 255, 255)
COLOR_ORANGE  = RGB(255, 165, 0)
COLOR_PURPLE  = RGB(128, 0, 128)
COLOR_PINK    = RGB(255, 192, 203)
COLOR_GRAY    = RGB(132, 132, 132)

LTGREY   = RGB(180, 180, 180)
GREY     = RGB(127, 127, 127)
DARKGREY = RGB(64, 64, 64)
TURQUOISE = RGB(0, 128, 120)
PINK      = RGB(255, 128, 192)
OLIVE     = RGB(128, 128, 0)
PURPLE    = RGB(128, 0, 128)
AZURE     = RGB(0, 128, 255)
ORANGE    = RGB(255, 128, 64)
WHITE      = RGB(255, 255, 255)
DKGREEN   = RGB(0, 70, 0)
DKBLUE    = RGB(0, 0, 70)
DKRED     = RGB(70, 0, 0)
BROWN     = RGB(130, 80, 40)

def invert_color(c):
    r, g, b = c
    return (255 - r, 255 - g, 255 - b)

# ==========================================================
#  ***** STATE VARIABLES *****
# ==========================================================

count = 1

x  = 0
y  = 0
x1 = 0
y1 = 0
x2 = 0
y2 = 0
u  = 0
v  = 0

umax = xmax
umin = xmin
vmax = ymax
vmin = ymin

xlin = 0
ylin = 0

stepx  = 0
stepy  = 0
stepx1 = 0
stepy1 = 0
stepx2 = 0
stepy2 = 0
stepu  = 0
stepv  = 0
steps  = 0

bkg_color = COLOR_BLACK

buf = ""

# ==========================================================
#  ***** PALETTES *****
# ==========================================================

def rainbow(i):
    i = i % 192
    if i < 32:
        return RGB(i * 8, 255, 0)
    if i < 64:
        return RGB(255, 255 - (i - 32) * 8, 0)
    if i < 96:
        return RGB(255, 0, (i - 64) * 8)
    if i < 128:
        return RGB(255 - (i - 96) * 8, 0, 255)
    if i < 160:
        return RGB(0, (i - 128) * 8, 255)
    return RGB(0, 255, 255 - (i - 160) * 8)

def firePalette(i):
    i = i % 192
    if i < 48:
        return RGB(128 + i * 2, 0, 0)
    if i < 96:
        return RGB(255, (i - 48) * 5, 0)
    if i < 144:
        return RGB(255, 240, (i - 96) * 5)
    return RGB(255, 255, 128 + (i - 144) * 2)

def pastelPalette(i):
    i = i % 192
    r = 128 + 127 * math.sin(i * 0.033)
    g = 128 + 127 * math.sin(i * 0.033 + 2.09)
    b = 128 + 127 * math.sin(i * 0.033 + 4.18)
    return RGB(r, g, b)

def icePalette(i):
    i = i % 192
    if i < 64:
        return RGB(0, i * 4, 255)
    if i < 128:
        return RGB(0, 255, 255 - (i - 64) * 4)
    return RGB(0, 255 - (i - 128) * 2, 128)

def sunsetPalette(i):
    i = i % 192
    if i < 48:
        return RGB(64 + i * 4, 0, 128 + i * 2)
    if i < 96:
        return RGB(255, 0, 255 - (i - 48) * 5)
    if i < 144:
        return RGB(255, (i - 96) * 5, 0)
    return RGB(255, 240, (i - 144) * 3)

def toxicPalette(i):
    i = i % 192
    return RGB(
        (i * 2) & 255,
        255,
        (128 + i) & 255
    )

def synthPalette(i):
    i = i % 192
    return RGB(
        (i * 3) & 255,
        (i // 2) & 255,
        255
    )

def royalPalette(i):
    i = i % 192
    return RGB(
        128 + (i % 64),
        (i % 32),
        200 + (i % 32)
    )

NUM_PALETTES = 8
currentPalette = 0

paletteNames = [
    "Rainbow",
    "Fire",
    "Pastel",
    "Ice",
    "Sunset",
    "Toxic",
    "Synthwave",
    "Royal"
]

palette_funcs = [
    rainbow,
    firePalette,
    pastelPalette,
    icePalette,
    sunsetPalette,
    toxicPalette,
    synthPalette,
    royalPalette
]

def getColor(i):
    if 0 <= currentPalette < NUM_PALETTES:
        return palette_funcs[currentPalette](i)
    return rainbow(i)

# ==========================================================
#  ***** INPUT HANDLING (TAP -> MOUSE CLICK) *****
# ==========================================================

TS_MINPRESS = 1  # placeholder, not used here

def screenTapped(events):
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return True
    return False

# ==========================================================
#  ***** TEXT HELPERS *****
# ==========================================================

def draw_text(text, x, y, color, bg=None, size="small"):
    if size == "small":
        fnt = font_small
    elif size == "medium":
        fnt = font_medium
    elif size == "large":
        fnt = font_large
    elif size == "huge":
        fnt = font_huge
    else:
        fnt = font_small
    surf = fnt.render(text, True, color, bg)
    screen.blit(surf, (x, y))

# ==========================================================
#  ***** PALETTE NAME DISPLAY *****
# ==========================================================

_palette_hue = 0

def drawPaletteName():
    global _palette_hue
    fg = getColor(_palette_hue); _palette_hue += 1
    bg = invert_color(getColor(_palette_hue)); _palette_hue += 1
    name = paletteNames[currentPalette]
    padded = f"{name:<9}"
    draw_text(padded, int(xmax * 0.64), int(ymin + 10), fg, bg, size="medium")

# ==========================================================
#  ***** SPLASH SCREEN MODULES (MODULAR / SCALING) *****
# ==========================================================

outer_rect = pygame.Rect(0, 0, 0, 0)
inner_rect = pygame.Rect(0, 0, 0, 0)

def drawSplashFrames():
    """Draw the centered outer and inner frames."""
    global outer_rect, inner_rect

    outer_w, outer_h = int(xmax * 0.75), int(ymax * 0.58)
    inner_w, inner_h = int(xmax * 0.62), int(ymax * 0.42)

    outer_x = (xmax - outer_w) // 2
    outer_y = (ymax - outer_h) // 2

    inner_x = (xmax - inner_w) // 2
    inner_y = (ymax - inner_h) // 2

    outer_rect = pygame.Rect(outer_x, outer_y, outer_w, outer_h)
    inner_rect = pygame.Rect(inner_x, inner_y, inner_w, inner_h)

    pygame.draw.rect(screen, COLOR_PURPLE, outer_rect, border_radius=20)
    pygame.draw.rect(screen, bkg_color, inner_rect, border_radius=10)
    pygame.draw.rect(screen, COLOR_YELLOW, inner_rect, 1, border_radius=10)
    pygame.draw.rect(screen, COLOR_YELLOW, outer_rect, 1, border_radius=20)

def drawSplashText():
    """Draw the 'by RM' and 'Loading...' text."""
    global _palette_hue

    draw_text("by ", 10, 10, COLOR_BLUE, None, size="small")

    rm_fg = getColor(_palette_hue); _palette_hue += 1
    rm_bg = invert_color(getColor(_palette_hue)); _palette_hue += 1
    draw_text("RM", 40, 5, rm_fg, rm_bg, size="large")

    draw_text("Loading ...", 10, ymax - 20, COLOR_WHITE, None, size="small")

def animateSplashBorders():
    """Animate the four nested border rectangles."""
    global _palette_hue

    pygame.draw.rect(
        screen, getColor(_palette_hue),
        outer_rect.inflate(-4, -4), 1, border_radius=17
    ); _palette_hue += 1

    pygame.draw.rect(
        screen, getColor(_palette_hue),
        outer_rect.inflate(-8, -8), 1, border_radius=16
    ); _palette_hue += 1

    pygame.draw.rect(
        screen, invert_color(getColor(_palette_hue)),
        outer_rect.inflate(-12, -12), 1, border_radius=15
    ); _palette_hue += 1

    pygame.draw.rect(
        screen, invert_color(getColor(_palette_hue)),
        outer_rect.inflate(-16, -16), 1, border_radius=14
    ); _palette_hue += 1

    pygame.display.flip()
    pygame.time.delay(100)

    pygame.draw.rect(
        screen, RGB(10, 10, 10),
        outer_rect.inflate(-4, -4), 1, border_radius=17
    )

    pygame.draw.rect(
        screen, getColor(_palette_hue),
        outer_rect.inflate(-8, -8), 1, border_radius=16
    ); _palette_hue += 1

    pygame.draw.rect(
        screen, getColor(_palette_hue),
        outer_rect.inflate(-12, -12), 1, border_radius=15
    ); _palette_hue += 1

    pygame.draw.rect(
        screen, invert_color(getColor(_palette_hue)),
        outer_rect.inflate(-16, -16), 1, border_radius=14
    ); _palette_hue += 1

    pygame.display.flip()
    pygame.time.delay(100)

def flashInvert():
    """Flash the screen invert effect."""
    for _ in range(30):
        screen.fill(invert_color(bkg_color))
        pygame.display.flip()
        pygame.time.delay(40)

        screen.fill(bkg_color)
        pygame.display.flip()
        pygame.time.delay(40)

# ==========================================================
#  ***** SPLASH ORCHESTRATOR *****
# ==========================================================

def splash():
    """Full splash sequence using modular components."""
    global _palette_hue
    _palette_hue = 0

    screen.fill(bkg_color)
    drawSplashFrames()

    for _ in range(20):
        drawSplashText()
        animateSplashBorders()

        qix_x = xmax // 2 - 60
        qix_y = ymax // 2 - 40
        draw_text("QIX", qix_x, qix_y, getColor(_palette_hue), None, size="huge")
        _palette_hue += 1

        pygame.display.flip()

    flashInvert()
    pygame.time.delay(500)

# ==========================================================
#  ***** BOUNCE BOUNDARIES *****
# ==========================================================

def bounceVar(pos, min_val, max_val, step):
    if pos <= min_val or pos >= max_val:
        pos = max(min(pos, max_val), min_val)
        if step > 0:
            step = -random.randint(5, 19)
        else:
            step = random.randint(5, 19)
    return pos, step

def checkbounds():
    global x, y, x1, y1, x2, y2, u, v
    global stepx, stepy, stepx1, stepy1, stepx2, stepy2, stepu, stepv

    x,  stepx  = bounceVar(x,  xmin, xmax, stepx)
    y,  stepy  = bounceVar(y,  ymin, ymax, stepy)
    x1, stepx1 = bounceVar(x1, xmin, xmax, stepx1)
    y1, stepy1 = bounceVar(y1, ymin, ymax, stepy1)
    x2, stepx2 = bounceVar(x2, xmin, xmax, stepx2)
    y2, stepy2 = bounceVar(y2, ymin, ymax, stepy2)
    u,  stepu  = bounceVar(u,  umin, umax, stepu)
    v,  stepv  = bounceVar(v,  vmin, vmax, stepv)

# ==========================================================
#  ***** DRAWING PRIMITIVES (QIX STUFF) *****
# ==========================================================

_draw_hue = 0

def drawstuff():
    global _draw_hue
    c1 = getColor(_draw_hue); _draw_hue += 1
    c2 = invert_color(getColor(_draw_hue)); _draw_hue += 1

    # --- Filled circle ---
    # pygame.draw.circle(screen, c1, (int(x), int(y)), int(u * 0.1))

    # --- Filled triangle ---
    # pygame.draw.polygon(screen, c1, [(x, y), (u, v), (x2, y2)])

    # --- Filled rectangle ---
    # pygame.draw.rect(
       # screen, c1,
       # pygame.Rect(int(x2), int(y2), int(u * 0.5), int(v * 0.5))
    # )

    # --- Line ---
    # pygame.draw.polygon(screen, c1, [(int(u), int(v)), (int(x2), int(y2))], width=1)

    # --- Circle outline ---
    # pygame.draw.circle(screen, c2, (int(x), int(y)), int(u * 0.1), width = 3)
    # pygame.draw.circle(screen, c2, (int(x2), int(y2)), int(v * 0.1), width = 3)
    # pygame.draw.circle(screen, c2, (int(u), int(v)), int(y * 0.1), width = 3)

    #--- Ellipse ---
    #pygame.draw.ellipse(
    #    screen,
    #    c1,
    #    pygame.Rect(
    #        int(x - x2 * 0.1),
    #        int(y - y2 * 0.1),
    #        int(x2 * 0.2),
    #        int(y2 * 0.2)
    #    ),
    #    width=1
    #)

    # --- Rectangle outline ---
    #pygame.draw.rect(
    #    screen,
    #    c1,
    #    pygame.Rect(int(x2), int(y2), int(u * 0.5), int(v * 0.5)),
    #    width=1
    #)

    # --- Triangle outline ---
    pygame.draw.polygon(screen, c1, [(x, y), (u, v), (x2, y2)], width=3)

def erasestuff():
    pygame.draw.circle(screen, bkg_color, (int(x), int(y)), int(u * 0.1))
    pygame.draw.polygon(screen, bkg_color, [(x, y), (u, v), (x2, y2)])
    pygame.draw.polygon(screen, bkg_color, [(x, y), (u, v), (x2, y2)], width=2)    # --- Line ---
    pygame.draw.line(screen, bkg_color, (int(u), int(v)), (int(x2), int(y2)))
    pygame.draw.rect(
       screen, bkg_color,
       pygame.Rect(int(x2), int(y2), int(u * 0.5), int(v * 0.5))
    )



def rndmredraw():
    global count, steps, x, y, x2, y2, u, v, xlin, ylin
    if count >= steps:
        steps = random.randint(100, 299)
        screen.fill(bkg_color)
        count = 1

        x = random.randint(xmin, xmax - 1)
        y = random.randint(ymin, ymax - 1)
        xlin = random.randint(xmin, xmax - 1)
        ylin = random.randint(ymin, ymax - 1)
        x2 = random.randint(xmin, xmax - 1)
        y2 = random.randint(ymin, ymax - 1)
        u = random.randint(xmin, xmax - 1)
        v = random.randint(ymin, ymax - 1)
		#pygame.time.delay(250)
		
    count += 1

def updatevars():
    global x, y, x1, y1, x2, y2, u, v
    global stepx, stepy, stepx1, stepy1, stepx2, stepy2, stepu, stepv

    x  += stepx
    y  += stepy
    x1 += stepx1
    y1 += stepy1
    x2 += stepx2
    y2 += stepy2
    u  += stepu
    v  += stepv

_horiz_hue = 0
_vert_hue = 0
_horiz_ylin = 0
_vert_xlin = 0

def horizLines():
    global _horiz_hue, _horiz_ylin
    if _horiz_ylin >= ymax:
        _horiz_ylin = 0
    color = getColor(_horiz_hue); _horiz_hue += 1
    pygame.draw.line(screen, color, (0, _horiz_ylin), (xmax, _horiz_ylin))
    _horiz_ylin += 2

def vertLines():
    global _vert_hue, _vert_xlin
    if _vert_xlin >= xmax:
        _vert_xlin = 0
    color = getColor(_vert_hue); _vert_hue += 1
    pygame.draw.line(screen, color, (_vert_xlin, 0), (_vert_xlin, ymax))
    _vert_xlin += 2

# ==========================================================
#  ***** DRAW COORDINATES *****
# ==========================================================

def drawtext():
    pygame.draw.rect(screen, COLOR_GRAY, pygame.Rect(5, 5, 200, 40), 1)

    draw_text("X = ", 10, 10, COLOR_YELLOW, bkg_color, "small")
    draw_text(f"{int(x):3d}", 40, 10, COLOR_YELLOW, bkg_color, "small")

    draw_text("Y = ", 10, 25, COLOR_YELLOW, bkg_color, "small")
    draw_text(f"{int(y):3d}", 40, 25, COLOR_YELLOW, bkg_color, "small")

    draw_text("X2 = ", 80, 10, invert_color(COLOR_GRAY), bkg_color, "small")
    draw_text(f"{int(x2):3d}", 115, 10, invert_color(COLOR_GRAY), bkg_color, "small")

    draw_text("Y2 = ", 80, 25, invert_color(COLOR_GRAY), bkg_color, "small")
    draw_text(f"{int(y2):3d}", 115, 25, invert_color(COLOR_GRAY), bkg_color, "small")

    draw_text("U = ", 150, 10, COLOR_GREEN, bkg_color, "small")
    draw_text(f"{int(u):3d}", 175, 10, COLOR_GREEN, bkg_color, "small")

    draw_text("V = ", 150, 25, COLOR_GREEN, bkg_color, "small")
    draw_text(f"{int(v):3d}", 175, 25, COLOR_GREEN, bkg_color, "small")

# ==========================================================
#  ***** DRAW COUNTER DISPLAY *****
# ==========================================================

def doCounter():
    pygame.draw.rect(screen, COLOR_GRAY, pygame.Rect(5, 50, 200, 50), 1)

    draw_text("Count = ", 10, 55, LTGREY, bkg_color, "medium")
    draw_text(f"{count:2d}", 80, 55, COLOR_WHITE, bkg_color, "medium")

    draw_text("of ", 10, 80, COLOR_BLUE, bkg_color, "small")
    draw_text(str(steps), 40, 75, COLOR_WHITE, bkg_color, "medium")

# ==========================================================
#  ***** SETUP *****
# ==========================================================

def setup():
    global x, y, x1, y1, x2, y2, u, v
    global stepx, stepy, stepx1, stepy1, stepx2, stepy2, stepu, stepv
    global steps, count

    random.seed()

    screen.fill(bkg_color)
    # splash()
    screen.fill(bkg_color)
    drawPaletteName()

    x = random.randint(xmin, xmax - 1)
    y = random.randint(ymin, ymax - 1)
    x1 = random.randint(xmin, xmax - 1)
    y1 = random.randint(ymin, ymax - 1)
    x2 = random.randint(xmin, xmax - 1)
    y2 = random.randint(ymin, ymax - 1)
    u = random.randint(xmin, xmax - 1)
    v = random.randint(ymin, ymax - 1)

    stepx  = random.randint(1, 9)
    stepy  = random.randint(1, 9)
    stepx1 = random.randint(1, 9)
    stepy1 = random.randint(1, 9)
    stepx2 = random.randint(1, 9)
    stepy2 = random.randint(1, 9)
    stepu  = random.randint(1, 9)
    stepv  = random.randint(1, 9)

    steps = random.randint(20, 99)
    count = 1

# ==========================================================
#  ***** LOOP *****
# ==========================================================

def loop():
    global currentPalette, count

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        if screenTapped(events):
            currentPalette = (currentPalette + 1) % NUM_PALETTES
            pygame.time.delay(250)

        # erasestuff()
        rndmredraw()
        updatevars()
        checkbounds()
        drawstuff()
        # horizLines()
        # vertLines()
        drawtext()
        doCounter()
        drawPaletteName()

        #count += 1

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

# ==========================================================
#  ***** MAIN ENTRY *****
# ==========================================================

if __name__ == "__main__":
    setup()
    loop()
