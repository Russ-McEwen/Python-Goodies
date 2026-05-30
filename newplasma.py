"""
*****************************|
|   Written by Russ McEwen   |
|         2/20/2026          |
|----------------------------|
|    Python / pygame port    |
|Fragment shader (GPU plasma)|
|****************************|
"""

import pygame
import moderngl
import time
import struct

# -----------------------------
# Config
# -----------------------------
WIDTH, HEIGHT = 1020, 740
MODE_SWITCH_TIME = 10.0  # seconds per hue mode

# -----------------------------
# Fragment shader (GPU plasma)
# -----------------------------
FRAGMENT_SHADER = """
#version 330

uniform float iTime;
uniform vec2  iResolution;
uniform int   iMode;

out vec4 fragColor;

// ---------------------------------------------
//  fast sine approximation (0..255 → -127..127)
// ---------------------------------------------
float fsin8(float x) {
    return sin(x * 0.0245436926) * 127.0;   // 2π/256
}

// ---------------------------------------------
//  Your exact hue personalities + Monty modes
// ---------------------------------------------
float hueMode(int i, int mode) {
    float fi = float(i);

    if (mode == 0)  return fi * 301.0;
    if (mode == 1)  return fi * 983.0;
    if (mode == 2)  return float(int(fi * fi) & 0xACFF);
    if (mode == 3)  return float(int(fi * fi * 3.0) & 0xABCF);
    if (mode == 4)  return float((int(fi) << 7) ^ int(fi * 23.0));
    if (mode == 5)  return float((int(fi) << 9) | int(fi * 37.0));
    if (mode == 6)  return fi * 126.0;
    if (mode == 7)  return (fi * 256.0) + (fsin8(fi) * 40.0);
    if (mode == 8)  return float(int(fi * 37.0) ^ int(fi * fi * 13.0));
    if (mode == 9)  return (fi * 256.0) + (fsin8(fi * 2.0) * 60.0);
    if (mode == 10) return fi * 256.0 * 1.6180339887;
    if (mode == 11) return (fi * 128.0) + ((fi * fi) * 0.25);
    if (mode == 12) return (fi * 256.0) + (fsin8(fi) * 30.0);

    // 13: SPAM SPAM SPAM – four chunky bands
    if (mode == 13) {
        float spam = floor(mod(fi * 0.1 + iTime * 4.0, 4.0));
        return spam * 16000.0;
    }

    // 14: And Now for Something Completely Different – chaos
    if (mode == 14) {
        float chaos = sin(fi * 12.345 + iTime * 7.89);
        chaos = abs(chaos) * 65535.0;
        return chaos;
    }

    // 15: Ministry of Silly Walks – wobbly stepped hue
    if (mode == 15) {
        float walk = mod(fi * 37.0 + iTime * 200.0, 65535.0);
        walk += sin(iTime * 10.0 + fi) * 5000.0;
        return walk;
    }

    return fi;
}

// ---------------------------------------------
//  HSV → RGB
// ---------------------------------------------
vec3 hsv2rgb(vec3 c) {
    vec3 rgb = clamp(
        abs(mod(c.x * 6.0 + vec3(0.0,4.0,2.0), 6.0) - 3.0) - 1.0,
        0.0,
        1.0
    );
    rgb = rgb * rgb * (3.0 - 2.0 * rgb);
    return c.z * mix(vec3(1.0), rgb, c.y);
}

// ---------------------------------------------
//  MAIN
// ---------------------------------------------
void main() {
    vec2 uv = gl_FragCoord.xy / iResolution.xy;
    vec2 p = (uv - 0.5) * vec2(iResolution.x / iResolution.y, 1.0);

    float t = iTime * 0.6;

    float v =
        sin(p.x * 7.0 + t * 3.0) +
        sin(p.y * 11.0 + t * 5.0) +
        sin((p.x + p.y) * 5.0 + t * 4.0) +
        sin((p.x - p.y) * 9.0 + t * 6.0);

    v = v * 0.25 + 0.5;   // normalize to 0..1

    // convert plasma value to 0..255 index
    int idx = int(v * 255.0);

    // your hue engine
    float rawHue = hueMode(idx, iMode);

    // convert 16‑bit hue to 0..1
    float h = fract(rawHue / 65535.0);

    vec3 col = hsv2rgb(vec3(h, 1.0, 1.0));

    fragColor = vec4(col, 1.0);
}
"""

# -----------------------------
# Vertex shader (full-screen quad)
# -----------------------------
VERTEX_SHADER = """
#version 330

in vec2 in_pos;
out vec2 v_uv;

void main() {
    v_uv = (in_pos + 1.0) * 0.5;
    gl_Position = vec4(in_pos, 0.0, 1.0);
}
"""

def main():
    pygame.init()
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(
        pygame.GL_CONTEXT_PROFILE_MASK,
        pygame.GL_CONTEXT_PROFILE_CORE
    )

    pygame.display.set_mode((WIDTH, HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("GPU Plasma (ModernGL)")

    ctx = moderngl.create_context()
    ctx.viewport = (0, 0, WIDTH, HEIGHT)

    prog = ctx.program(
        vertex_shader=VERTEX_SHADER,
        fragment_shader=FRAGMENT_SHADER,
    )

    # -----------------------------
    # Full-screen quad (correct float32 data)
    # -----------------------------
    quad = struct.pack(
        "8f",
        -1.0, -1.0,
         1.0, -1.0,
        -1.0,  1.0,
         1.0,  1.0
    )

    vertices = ctx.buffer(quad)
    vao = ctx.simple_vertex_array(prog, vertices, "in_pos")

    # Uniforms
    iTime = prog["iTime"]
    iResolution = prog["iResolution"]
    iMode = prog["iMode"]

    iResolution.value = (float(WIDTH), float(HEIGHT))

    clock = pygame.time.Clock()
    start_time = time.time()
    current_mode = 0
    last_switch = start_time

    print("Initial mode = ", current_mode)
    running = True
    while running:
        for event in pygame.event.get():
            if (event.type == pygame.QUIT or
                (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                current_mode = (current_mode + 1) % 16
                last_switch = now
                print(" Manual switch to mode", current_mode)

        now = time.time()
        t = now - start_time

        if now - last_switch > MODE_SWITCH_TIME:
            current_mode = (current_mode + 1) % 16
            last_switch = now
            print(" Auto switch to mode", current_mode)

        iTime.value = float(t)
        iMode.value = current_mode

        ctx.clear(0.0, 0.0, 0.0, 1.0)
        vao.render(moderngl.TRIANGLE_STRIP)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
    