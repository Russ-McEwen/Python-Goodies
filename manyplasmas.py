import pygame
import math
import time
import random

# -----------------------------
#  CONFIG — ULTRA RESOLUTION
# -----------------------------
WIDTH, HEIGHT = 1020, 600   # huge window
SCALE = 12                   # tiny pixel blocks = very smooth plasma
MODE_SWITCH_TIME = 5       # seconds per hue mode

# -----------------------------
#  FAST SINE TABLE (0–255 → -127..127)
# -----------------------------
sin_table = [int(math.sin(i * 2 * math.pi / 256) * 127) for i in range(256)]

def fsin(x):
    return sin_table[x & 0xFF]

# -----------------------------
#  HUE → RGB (HSV conversion)
# -----------------------------
def hsv_to_rgb(h, s, v):
    h = float(h % 360)
    s = float(s) / 255
    v = float(v) / 255

    c = v * s
    x = c * (1 - abs(((h / 60) % 2) - 1))
    m = v - c

    if h < 60:   r, g, b = c, x, 0
    elif h < 120: r, g, b = x, c, 0
    elif h < 180: r, g, b = 0, c, x
    elif h < 240: r, g, b = 0, x, c
    elif h < 300: r, g, b = x, 0, c
    else:         r, g, b = c, 0, x

    return (
        int((r + m) * 255),
        int((g + m) * 255),
        int((b + m) * 255)
    )

# -----------------------------
#  HUE MODES (mirroring Arduino)
# -----------------------------
def hue0(i): return i * 301
def hue1(i): return i * 983
def hue2(i): return (i * i) & 0xACFF
def hue3(i): return (i * i * 3) & 0xFFFF
def hue4(i): return (i << 7) ^ (i * 23)
def hue5(i): return (i << 9) | (i * 37)
def hue6(i): return i * 126
def hue7(i): return (i * 256) + (fsin(i) * 40)
def hue8(i): return (i * 37) ^ (i * i * 13)
def hue9(i): return (i * 256) + (fsin(i * 2) * 60)
def hue10(i): return int(i * 256 * 1.6180339887)
def hue11(i): return (i * 128) + ((i * i) // 4)
def hue12(i): return (i * 256) + (fsin(i) * 30)

hue_modes = [
    hue0, hue1, hue2, hue3, hue4, hue5, hue6,
    hue7, hue8, hue9, hue10, hue11, hue12
]

# -----------------------------
#  BUILD PLASMA LUT
# -----------------------------
def build_lut(mode_index):
    f = hue_modes[mode_index]
    lut = []
    for i in range(256):
        hue = f(i) & 0xFFFF
        hue_deg = (hue / 65535) * 360
        lut.append(hsv_to_rgb(hue_deg, 255, 255))
    return lut

# -----------------------------
#  MAIN
# -----------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

current_mode = 0
lut = build_lut(current_mode)
last_switch = time.time()

t = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Auto-switch hue mode
    if time.time() - last_switch > MODE_SWITCH_TIME:
        current_mode = (current_mode + 1) % len(hue_modes)
        lut = build_lut(current_mode)
        last_switch = time.time()
        print("Switched to hue mode", current_mode)

    # Draw plasma
    for y in range(HEIGHT // SCALE):
        for x in range(WIDTH // SCALE):
            v = (
                fsin((x * 7 + t * 3)) +
                fsin((y * 11 + t * 5)) +
                fsin(((x + y) * 5 + t * 4)) +
                fsin(((x - y) * 9 + t * 6))
            )

            idx = (v + 512) >> 1

            # clamp to 0–255
            if idx < 0:
                idx = 0
            elif idx > 255:
                idx = 255

            color = lut[idx]

            pygame.draw.rect(
                screen,
                color,
                (x * SCALE, y * SCALE, SCALE, SCALE)
            )

    pygame.display.flip()
    t += 1
    clock.tick(40)

pygame.quit()
