#!/usr/bin/env python3
"""Build IVC 30-second cartoon animation — pain points to solution"""

from PIL import Image, ImageDraw, ImageFont
import os, math

W, H = 1280, 720
FPS = 30
SECS = 6  # per scene
FRAMES = SECS * FPS
OUT = "/home/storyclaw/.openclaw/workspace-github-repo-executor-pro/illinoisvalleycounseling/ivc-preview.mp4"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# ── Palette ──────────────────────────────────────────────────────────────────
TEAL   = (26,  95,  90)
TEAL_L = (45, 138, 132)
AMBER  = (232, 168,  74)
CREAM  = (250, 247, 242)
WHITE  = (255, 253, 249)
CHARCO = (44,  44,  44)
GRAY   = (107, 107, 107)
RED    = (210,  80,  70)
GREEN  = (60,  180, 120)

# ── Helpers ───────────────────────────────────────────────────────────────────
def ease(t): return t * t * (3 - 2 * t)   # smoothstep

def fade_alpha(t, duration=0.5):
    """Return alpha 0..255 for a fade over duration (in seconds) at time t"""
    if t < 0: return 0
    if t > duration: return 255
    return int(255 * (t / duration))

def lerp(a, b, t): return a + (b - a) * t
def lerp_color(c1, c2, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))

def circle(draw, cx, cy, r, fill, outline=None, width=1):
    xy = [cx-r, cy-r, cx+r, cy+r]
    draw.ellipse(xy, fill=fill, outline=outline, width=width)

def rounded_rect(draw, xy, r, fill, outline=None, width=1):
    x0,y0,x1,y1 = xy
    draw.rounded_rectangle([x0,y0,x1,y1], radius=r, fill=fill, outline=outline, width=width)

def text_center(draw, text, cx, cy, font, color, max_w=None):
    import textwrap
    if max_w:
        lines = []
        for line in text.split('\n'):
            wrapped = textwrap.wrap(line, width=int(max_w / (font.size * 0.55)))
            lines.extend(wrapped if wrapped else [''])
        text = '\n'.join(lines)
    bbox = draw.textbbox((0,0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cx - tw/2, cy - th/2), text, font=font, fill=color)

def load_font(size):
    for path in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                 "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

FONT_TITLE = load_font(72)
FONT_SUB   = load_font(40)
FONT_BODY  = load_font(30)
FONT_SMALL = load_font(24)
FONT_NUM   = load_font(64)

# ── Scene drawing functions ───────────────────────────────────────────────────

def draw_bg(draw, color=None, gradient=None):
    if gradient:
        for y in range(H):
            t = y / H
            c = lerp_color(gradient[0], gradient[1], t)
            draw.line([(0,y),(W,y)], fill=c)
    elif color:
        draw.rectangle([0,0,W,H], fill=color)

def draw_person(draw, cx, cy, color=TEAL, scale=1.0, expression='happy'):
    """Simple flat cartoon person"""
    r = int(28 * scale)
    # body
    circle(draw, cx, cy + int(70*scale), int(45*scale), color)
    # head
    circle(draw, cx, cy, r, color)
    # eyes
    ex = int(9*scale)
    ey = cy - int(4*scale)
    circle(draw, cx-ex, ey, int(4*scale), WHITE)
    circle(draw, cx+ex, ey, int(4*scale), WHITE)
    eye_pupil_r = int(2.5*scale)
    if expression == 'sad':
        circle(draw, cx-ex+1, ey+1, eye_pupil_r, CHARCO)
        circle(draw, cx+ex+1, ey+1, eye_pupil_r, CHARCO)
        # frown
        draw.arc([cx-10, cy+int(8*scale), cx+10, cy+int(20*scale)],
                 start=0, end=180, fill=WHITE, width=2)
    elif expression == 'neutral':
        circle(draw, cx-ex, ey, eye_pupil_r, CHARCO)
        circle(draw, cx+ex, ey, eye_pupil_r, CHARCO)
    else:
        circle(draw, cx-ex, ey, eye_pupil_r, CHARCO)
        circle(draw, cx+ex, ey, eye_pupil_r, CHARCO)
    # smile
    draw.arc([cx-12, cy+int(5*scale), cx+12, cy+int(20*scale)],
             start=0, end=180, fill=WHITE, width=2)

def draw_phone(draw, cx, cy, scale=1.0, screen_content=None):
    """Phone flat icon"""
    bw = int(60*scale)
    bh = int(110*scale)
    # body
    rounded_rect(draw, [cx-bw//2, cy-bh//2, cx+bw//2, cy+bh//2], int(10*scale), CHARCO)
    # screen
    rounded_rect(draw, [cx-bw//2+4, cy-bh//2+8, cx+bw//2-4, cy+bh//2-14], int(6*scale), WHITE)
    if screen_content:
        screen_content(draw, cx, cy)

def draw_search_bar(draw, cx, cy, query, scale=1.0, results=None):
    """Google search bar"""
    bw = int(700*scale)
    bh = int(60*scale)
    rounded_rect(draw, [cx-bw//2, cy-bh//2, cx+bw//2, cy+bh//2], int(30*scale), WHITE, outline=GRAY, width=2)
    # search icon
    circle(draw, cx-bw//2+30, cy, 12, None, outline=GRAY, width=2)
    draw.line([(cx-bw//2+38, cy+8), (cx-bw//2+46, cy+16)], fill=GRAY, width=2)
    # query text
    draw.text((cx-bw//2+60, cy-12), query, font=FONT_BODY, fill=CHARCO)
    if results:
        results(draw, cx, cy, scale)

def draw_google_results(draw, cx, start_y, scale=1.0, highlight=None):
    """Draw 3 Google result cards"""
    colors = [GREEN if highlight==0 else TEAL,
              GREEN if highlight==1 else TEAL_L,
              GREEN if highlight==2 else GRAY]
    labels = [
        "North Central Behavioral Health",
        "Starved Rock Counseling",
        "Illinois Valley Counseling ✗",
    ]
    y = start_y
    for i, (label, col) in enumerate(zip(labels, colors)):
        r = 12 * scale
        rounded_rect(draw, [cx-320, y, cx+320, y+72], int(r), WHITE, outline=col, width=2)
        draw.text((cx-300, y+10), label, font=FONT_BODY, fill=CHARCO)
        draw.text((cx-300, y+40), "https://example.com", font=FONT_SMALL, fill=GRAY)
        y += 84

def draw_x(draw, cx, cy, color=RED, scale=1.0):
    r = int(16*scale)
    draw.line([cx-r, cy-r, cx+r, cy+r], fill=color, width=3)
    draw.line([cx-r, cy+r, cx+r, cy-r], fill=color, width=3)

# ── Scene 1: Lost on Google ────────────────────────────────────────────────────
def scene_lost(frame_i, progress):
    t = progress
    img = Image.new('RGBA', (W, H), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw_bg(draw, gradient=[CREAM, WHITE])

    # Title fade-in
    alpha_title = fade_alpha(t, 0.5)
    alpha_content = fade_alpha(max(0, t-0.3), 0.5)

    # Scene number
    draw.text((80, 55), "01", font=FONT_NUM, fill=(*TEAL, int(200*alpha_title/255)))

    # Main text
    if alpha_title > 10:
        c = (*CHARCO, alpha_title)
        draw.text((W//2, 130), "Can They Even Find You?", font=FONT_TITLE, fill=c)

    if alpha_content > 10:
        c = (*GRAY, alpha_content)
        draw.text((W//2, 220), "When someone searches 'therapist near me'...", font=FONT_SUB, fill=c)

    # Phone + search
    pcy = 440
    # person looking confused at phone
    person_cx = W//2 - 180
    draw_person(draw, person_cx, pcy, color=TEAL, expression='sad', scale=1.1)

    # Phone showing search results
    ph_cx = W//2 + 80
    ph_cy = pcy

    def screen(drw, cx, cy):
        sc = 1.2
        bw = int(60*sc)
        # show search bar
        rounded_rect(drw, [cx-bw//2, cy-80, cx+bw//2, cy-50], 8, (230,235,240))
        drw.text((cx-bw//2+8, cy-76), "therapy near me", font=load_font(14), fill=GRAY)
        # results
        labels_rs = ["North Central...", "Starved Rock...", "Illinois Valley  ✗"]
        ry = cy - 40
        for i, lbl in enumerate(labels_rs):
            rdy = ry + i*30
            rounded_rect(drw, [cx-bw//2+4, rdy, cx+bw//2-4, rdy+24], 4, (240,245,248))
            drw.text((cx-bw//2+8, rdy+3), lbl[:18], font=load_font(12), fill=CHARCO if i < 2 else RED)

    draw_phone(draw, ph_cx, ph_cy, scale=1.2, screen_content=screen)

    # Arrow from person to phone
    draw.line([(person_cx + 60, pcy - 20), (ph_cx - 50, pcy - 40)], fill=TEAL_L, width=3)

    # Label
    c = (*CHARCO, int(alpha_content))
    draw.text((W//2, 610), '"I searched but couldn\'t find them..."', font=FONT_BODY, fill=c)

    # X mark on their result
    mx = ph_cx + 20
    my = ph_cy + 20
    draw_x(draw, mx, my, scale=0.9)
    alpha_x = int(alpha_content * 0.8)
    draw.text((mx+20, my-12), "Not visible", font=FONT_SMALL, fill=(*RED, alpha_x))

    return img

# ── Scene 2: Phone-only intake ─────────────────────────────────────────────────
def scene_phone(frame_i, progress):
    t = progress
    alpha = fade_alpha(t, 0.5)

    img = Image.new('RGBA', (W, H), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw_bg(draw, gradient=[CREAM, WHITE])

    draw.text((80, 55), "02", font=FONT_NUM, fill=(*TEAL, int(200*alpha/255)))

    c = (*CHARCO, alpha)
    draw.text((W//2, 100), "The Intake Gap", font=FONT_TITLE, fill=c)
    draw.text((W//2, 195), "Someone calls... you don't answer... they move on.", font=FONT_SUB, fill=(*GRAY, alpha))

    # Phone ringing
    pcy = 430
    draw_phone(draw, W//2, pcy, scale=1.5)

    # Ringing waves
    progress_loop = (t * 1.5) % 1.0
    for i in range(3):
        p2 = min(1.0, progress_loop + i*0.15)
        r = int(80 + p2 * 60)
        alpha_ring = int(200 * (1 - p2))
        circle(draw, W//2, pcy, r, None, outline=(*AMBER, alpha_ring), width=2)

    # Caller ID
    draw.text((W//2-60, pcy-30), "Unknown", font=FONT_BODY, fill=WHITE)
    draw.text((W//2-60, pcy+5), "Missed Call", font=FONT_SMALL, fill=(*AMBER, 200))

    # Person putting phone down (frustrated)
    draw_person(draw, W//2-200, pcy, expression='sad', scale=1.0)
    # thought bubble
    draw.arc([W//2-280, pcy-180, W//2-140, pcy-130], 0, 360, fill=(*GRAY, alpha), width=2)
    draw.arc([W//2-260, pcy-210, W//2-155, pcy-145], 0, 360, fill=(*GRAY, alpha), width=2)
    draw.text((W//2-340, pcy-200), "They hung up...", font=FONT_BODY, fill=(*RED, alpha))

    # Another person (calm) with calendar
    draw_person(draw, W//2+220, pcy, expression='neutral', scale=1.0)
    # calendar
    bx = W//2+280
    by = pcy-80
    rounded_rect(draw, [bx-40, by-35, bx+40, by+35], 8, WHITE, outline=TEAL, width=2)
    draw.rectangle([bx-40, by-10, bx+40, by-5], fill=TEAL)
    draw.text((bx-15, by-35), "MON", font=FONT_SMALL, fill=TEAL)
    draw.text((bx-8, by-5), "15", font=FONT_BODY, fill=WHITE)

    # Big stat
    stat_alpha = fade_alpha(max(0, t-0.8), 0.5)
    c2 = (*AMBER, int(255*stat_alpha/255))
    draw.text((W//2, 610), "70% of people who call don't book", font=FONT_SUB, fill=c2)

    return img

# ── Scene 3: Directory invisibility ───────────────────────────────────────────
def scene_directory(frame_i, progress):
    t = progress
    alpha = fade_alpha(t, 0.5)

    img = Image.new('RGBA', (W, H), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw_bg(draw, gradient=[CREAM, WHITE])

    draw.text((80, 55), "03", font=FONT_NUM, fill=(*TEAL, int(200*alpha/255)))

    draw.text((W//2, 100), "Competitors Are Listed.", font=FONT_TITLE, fill=(*CHARCO, alpha))
    draw.text((W//2, 195), "You're not. Here's who is...", font=FONT_SUB, fill=(*GRAY, alpha))

    # Directory logos
    dirs = [
        ("Psychology Today", TEAL),
        ("BetterHelp", TEAL_L),
        ("GoodTherapy", GRAY),
        ("Zencare", GRAY),
    ]
    dx = W//2 - 260
    dy = 300
    for name, col in dirs:
        rounded_rect(draw, [dx, dy, dx+220, dy+70], 12, WHITE, outline=col, width=2)
        draw.text((dx+20, dy+18), name, font=FONT_BODY, fill=col)
        # checkmark
        circle(draw, dx+195, dy+35, 14, GREEN)
        draw.line([(dx+188, dy+35), (dx+194, dy+42), (dx+205, dy+28)], fill=WHITE, width=2)
        dx += 240

    # "You" section
    iy = 430
    rounded_rect(draw, [W//2-120, iy-35, W//2+120, iy+35], 12, (*RED, 30), outline=RED, width=2)
    draw.text((W//2, iy-10), "Illinois Valley?", font=FONT_BODY, fill=RED)
    draw_x(draw, W//2+80, iy, color=RED, scale=1.2)

    # Stat
    stat_alpha = fade_alpha(max(0, t-0.5), 0.5)
    draw.text((W//2, 520), "Psychology Today has 10M+ visits/month", font=FONT_SUB, fill=(*AMBER, int(255*stat_alpha/255)))
    draw.text((W//2, 580), "That's where new clients are searching.", font=FONT_BODY, fill=(*GRAY, int(200*stat_alpha/255)))

    return img

# ── Scene 4: Transition — THE PATH ─────────────────────────────────────────────
def scene_path(frame_i, progress):
    t = progress
    # Quick flash/zoom
    t2 = min(1.0, t * 2)
    alpha = int(255 * ease(t2))

    img = Image.new('RGBA', (W, H), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw_bg(draw, TEAL_DARK := (15, 60, 58))

    # Rays
    for i in range(8):
        angle = math.radians(i * 45 + t * 30)
        r1, r2 = 100, 400
        x1 = W//2 + int(r1 * math.cos(angle))
        y1 = H//2 + int(r1 * math.sin(angle))
        x2 = W//2 + int(r2 * math.cos(angle))
        y2 = H//2 + int(r2 * math.sin(angle))
        draw.line([(x1,y1),(x2,y2)], fill=(*AMBER, int(20 * t2)), width=1)

    c = (*WHITE, alpha)
    draw.text((W//2, H//2 - 80), "There's a Better Way.", font=FONT_TITLE, fill=c)
    draw.text((W//2, H//2), "Get Found. Get Booked. Grow.", font=FONT_SUB, fill=(*AMBER, alpha))

    # Animated arrow
    ay = H//2 + 80
    ax = W//2
    arr_t = (t * 2) % 1.0
    offset = int(20 * math.sin(arr_t * math.pi * 2))
    draw.polygon([(ax, ay+offset-15), (ax-20, ay+offset+10), (ax, ay+offset+2),
                  (ax+20, ay+offset+10)], fill=(*AMBER, alpha))

    return img

# ── Scene 5: Get Set Up ───────────────────────────────────────────────────────
def scene_set(frame_i, progress):
    t = progress
    alpha = fade_alpha(t, 0.5)
    items = [
        ("Google Business", "Verified & Optimized", GREEN),
        ("Psychology Today", "Profile Created", GREEN),
        ("SimplePractice", "Online Booking Ready", GREEN),
        ("Google Ads", "Campaign Live", AMBER),
        ("Reviews", "Automated Requests", TEAL_L),
    ]

    img = Image.new('RGBA', (W, H), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw_bg(draw, gradient=[WHITE, CREAM])

    draw.text((80, 55), "04", font=FONT_NUM, fill=(*TEAL, int(200*alpha/255)))
    draw.text((W//2, 100), "You Get Set Up Right.", font=FONT_TITLE, fill=(*CHARCO, alpha))

    cy = 250
    for i, (title, sub, col) in enumerate(items):
        ia = fade_alpha(max(0, t - i*0.12), 0.4)
        x = W//2
        # icon circle
        circle(draw, W//2 - 200, cy, 22, col)
        draw.line([(W//2-215, cy), (W//2-188, cy)], fill=WHITE, width=2)
        draw.line([(W//2-202, cy-13), (W//2-202, cy+13)], fill=WHITE, width=2)
        # text
        draw.text((W//2 - 160, cy-14), title, font=FONT_BODY, fill=(*CHARCO, ia))
        draw.text((W//2 - 160, cy+10), sub, font=FONT_SMALL, fill=(*GRAY, ia))
        cy += 80

    return img

# ── Scene 6: Phone Ringing ────────────────────────────────────────────────────
def scene_phones_ringing(frame_i, progress):
    t = progress
    alpha = fade_alpha(t, 0.5)
    pulse = (math.sin(t * math.pi * 2) + 1) / 2  # 0..1 pulse

    img = Image.new('RGBA', (W, H), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    draw_bg(draw, gradient=[(15,60,58), TEAL])

    # Ringing circles
    for i in range(4):
        p = (t * 1.2 + i * 0.2) % 1.0
        r = int(40 + p * 80)
        alpha_ring = int(180 * (1 - p))
        circle(draw, W//2, 300, r, None, outline=(*AMBER, alpha_ring), width=3)

    # Phone
    draw_phone(draw, W//2, 300, scale=2.0)
    draw.text((W//2-50, 290), "📞", font=load_font(50))

    c = (*WHITE, alpha)
    draw.text((W//2, 470), "New Clients.", font=FONT_TITLE, fill=c)
    draw.text((W//2, 555), "Booking Online.", font=FONT_TITLE, fill=(*AMBER, alpha))

    c2 = (*WHITE, int(200*fade_alpha(max(0,t-0.6), 0.4)/255))
    draw.text((W//2, 620), "Illinois Valley Counseling Services", font=FONT_BODY, fill=c2)

    return img

# ── Render loop ───────────────────────────────────────────────────────────────
SCENES = [scene_lost, scene_phone, scene_directory, scene_path, scene_set, scene_phones_ringing]
SCENE_FRAMES = FRAMES  # all same length

import subprocess, os

FRAME_DIR = "/home/storyclaw/.openclaw/workspace-github-repo-executor-pro/illinoisvalleycounseling/frames"
os.makedirs(FRAME_DIR, exist_ok=True)
print(f"Rendering {len(SCENES) * SCENE_FRAMES} frames to {FRAME_DIR} ...")

for si, scene_fn in enumerate(SCENES):
    print(f"  Scene {si+1}/{len(SCENES)}: {scene_fn.__name__}")
    for fi in range(SCENE_FRAMES):
        progress = fi / SCENE_FRAMES
        frame = scene_fn(fi, progress)
        frame_rgb = frame.convert('RGB')
        frame_path = os.path.join(FRAME_DIR, f"scene{si:02d}_frame{fi:04d}.png")
        frame_rgb.save(frame_path)
        if fi % 60 == 0:
            print(f"    frame {fi}/{SCENE_FRAMES}")

print("Compiling with ffmpeg...")
cmd = [
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", os.path.join(FRAME_DIR, "scene%02d_frame%04d.png"),
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "23",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",
    OUT
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print("FFMPEG ERROR:", result.stderr[-2000:])
else:
    print(f"✓ Video saved to {OUT}")
    # Clean up frames
    shutil.rmtree(FRAME_DIR)
    print("Frames cleaned up.")

import os
size = os.path.getsize(OUT) if os.path.exists(OUT) else 0
print(f"File size: {size/1024/1024:.2f} MB")
