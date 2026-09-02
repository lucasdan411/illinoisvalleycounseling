#!/usr/bin/env python3
"""
IVCS 15-second Whiteboard Explainer Video
Black & white stick-figure style, mobile-first
"""

import subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont

TMP = "/tmp/ivcs_video"
FRAMES = f"{TMP}/frames"
AUDIO = f"{TMP}/audio.wav"
OUTPUT = f"{TMP}/ivcs_whiteboard.mp4"

os.makedirs(FRAMES, exist_ok=True)

W, H = 720, 1280   # 9:16 vertical (mobile-first)
FPS = 30
TOTAL_FRAMES = 15 * FPS  # 15 seconds

def run(cmd):
    print("  Running:", " ".join(cmd[:4]), "...")
    subprocess.run(cmd, check=True, capture_output=True)

def draw_scene(draw_fn, frame_num, total_frames):
    """Render one frame by calling draw_fn(img_array)"""
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(img)
    draw_fn(draw, frame_num, total_frames)
    img.save(f"{FRAMES}/frame_{frame_num:04d}.png")

def circle(draw, cx, cy, r, fill="black", outline=None, width=3):
    xy = [cx-r, cy-r, cx+r, cy+r]
    if outline:
        draw.ellipse(xy, fill=fill, outline=outline, width=width)
    else:
        draw.ellipse(xy, fill=fill, outline=outline)

def line(draw, x1, y1, x2, y2, fill="black", width=3):
    draw.line([x1, y1, x2, y2], fill=fill, width=width)

def text(draw, text_str, cx, cy, size=36, fill="black"):
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text_str, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((cx - tw//2, cy - th//2), text_str, font=font, fill=fill)

def stick_figure(draw, cx, cy, scale=1.0, flip=False, hand_up=False):
    """Simple stick figure"""
    s = scale
    # head
    circle(draw, cx, cy - 80*s, int(22*s))
    # body
    line(draw, cx, cy - 58*s, cx, cy + 20*s, width=int(3*s))
    # legs
    line(draw, cx, cy + 20*s, cx - 25*s, cy + 80*s, width=int(3*s))
    line(draw, cx, cy + 20*s, cx + 25*s, cy + 80*s, width=int(3*s))
    # arms
    if hand_up:
        # right arm up (excitement)
        line(draw, cx, cy - 30*s, cx - 30*s, cy, width=int(3*s))
        line(draw, cx, cy - 30*s, cx + 30*s, cy - 60*s, width=int(3*s))
    else:
        line(draw, cx, cy - 30*s, cx - 30*s, cy, width=int(3*s))
        line(draw, cx, cy - 30*s, cx + 30*s, cy, width=int(3*s))

def phone_icon(draw, cx, cy, scale=1.0):
    """Simple phone rectangle"""
    s = scale
    w, h = int(30*s), int(55*s)
    draw.rounded_rectangle([cx-w//2, cy-h//2, cx+w//2, cy+h//2], radius=5, outline="black", width=3)
    # screen
    screen_pad = 4*s
    draw.rounded_rectangle([cx-w//2+screen_pad, cy-h//2+screen_pad, cx+w//2-screen_pad, cy+h//2-screen_pad], radius=2, fill="black")

# ─────────────────────────────────────────────────────────────────
# SCENE 0: [0-4s] SEARCH - person on phone searching
# ─────────────────────────────────────────────────────────────────
def scene_search(draw, frame, total):
    t = frame / FPS
    progress = min(1.0, t / 3.5)

    # Background
    draw.rectangle([0, 0, W, H], fill="white")

    # Phone body
    pw, ph = 160, 320
    px, py = W//2 - pw//2, 200
    draw.rounded_rectangle([px, py, px+pw, py+ph], radius=18, outline="black", width=4)
    # Screen
    sx1, sy1 = px+10, py+30
    sx2, sy2 = px+pw-10, py+ph-40
    draw.rounded_rectangle([sx1, sy1, sx2, sy2], radius=4, fill="white", outline="black", width=2)

    # Search bar in phone
    search_y = sy1 + 20
    draw.rounded_rectangle([sx1+10, search_y, sx2-10, search_y+28], radius=14, fill="white", outline="black", width=2)
    text(draw, "therapist near me", sx1+20, search_y+4, 16, "black")
    # Magnifying glass icon
    circle(draw, sx2-25, search_y+14, 8, outline="black", width=2)

    # Search results appearing
    result_y = search_y + 50
    alpha_results = int(255 * max(0, (t - 1.0) / 1.5))
    results = [
        (f"IVCS - Illinois Valley Counseling", True),
        ("TherapistName, LCSW - Nearby", False),
        ("AnotherPractice - Psychology Today", False),
    ]
    for i, (label, highlight) in enumerate(results):
        ry = result_y + i * 45
        if highlight:
            draw.rectangle([sx1+5, ry, sx2-5, ry+38], fill="black")
            text(draw, label, sx1+15, ry+6, 14, "white")
        else:
            text(draw, label, sx1+15, ry+6, 14, "black")

    # Stick figure person (holding phone)
    fig_x, fig_y = W//2, py+ph+100
    stick_figure(draw, fig_x, fig_y, scale=1.8)
    # Arm reaching to phone
    line(draw, fig_x+30, fig_y-30, fig_x+80, fig_y-10, width=3)

    # Text below
    text(draw, "You show up on Google.", W//2, py+ph+220, size=42)
    text(draw, "But patients can't book online.", W//2, py+ph+270, size=32)

# ─────────────────────────────────────────────────────────────────
# SCENE 1: [3.5-7.5s] PROBLEM - tries to book, hits wall
# ─────────────────────────────────────────────────────────────────
def scene_problem(draw, frame, total):
    t = (frame - 3.5*FPS) / FPS

    draw.rectangle([0, 0, W, H], fill="white")

    # Phone with X on booking button
    pw, ph = 160, 320
    px, py = W//2 - pw//2, 160
    draw.rounded_rectangle([px, py, px+pw, py+ph], radius=18, outline="black", width=4)
    sx1, sy1 = px+10, py+30
    sx2, sy2 = px+pw-10, py+ph-40

    # Big X over the booking area
    x_size = 60
    cx_b, cy_b = W//2, sy1+100
    draw.ellipse([cx_b-x_size, cy_b-x_size, cx_b+x_size, cy_b+x_size], fill="white", outline="black", width=4)
    line(draw, cx_b-x_size+15, cy_b-x_size+15, cx_b+x_size-15, cy_b+x_size-15, fill="black", width=5)
    line(draw, cx_b+x_size-15, cy_b-x_size+15, cx_b-x_size+15, cy_b+x_size-15, fill="black", width=5)

    # "BOOK" button label
    draw.rounded_rectangle([cx_b-40, cy_b+80, cx_b+40, cy_b+115], radius=8, fill="black")
    text(draw, "BOOK", cx_b-18, cy_b+85, 14, "white")

    # Stick figure looking frustrated
    fig_x, fig_y = W//2, py+ph+100
    # arms on head (frustrated gesture)
    line(draw, fig_x, fig_y-58, fig_x-25, fig_y-30, width=3)
    line(draw, fig_x, fig_y-58, fig_x+25, fig_y-30, width=3)
    line(draw, fig_x, fig_y-30, fig_x-30, fig_y, width=3)
    line(draw, fig_x, fig_y-30, fig_x+30, fig_y, width=3)
    circle(draw, fig_x, fig_y-80, 22)
    line(draw, fig_x, fig_y-58, fig_x, fig_y+20, width=3)
    line(draw, fig_x, fig_y+20, fig_x-25, fig_y+80, width=3)
    line(draw, fig_x, fig_y+20, fig_x+25, fig_y+80, width=3)

    text(draw, "They try to book.", W//2, py+ph+195, size=38)
    text(draw, "No online booking. They call.", W//2, py+ph+245, size=32)

# ─────────────────────────────────────────────────────────────────
# SCENE 2: [7.5-11s] SOLUTION - SimplePractice booking works
# ─────────────────────────────────────────────────────────────────
def scene_solution(draw, frame, total):
    t = (frame - 7.5*FPS) / FPS

    draw.rectangle([0, 0, W, H], fill="white")

    # Calendar/booking confirmation
    cal_x, cal_y = W//2, 300
    cal_w, cal_h = 300, 380
    draw.rounded_rectangle([cal_x-cal_w//2, cal_y-cal_h//2, cal_x+cal_w//2, cal_y+cal_h//2], radius=12, outline="black", width=4)

    # Calendar header
    draw.rectangle([cal_x-cal_w//2, cal_y-cal_h//2, cal_x+cal_w//2, cal_y-cal_h//2+50], fill="black")
    text(draw, "Sept 2026", cal_x-70, cal_y-cal_h//2+10, 18, "white")

    # Calendar grid lines
    for row in range(5):
        y = cal_y - 80 + row * 55
        for col in range(7):
            x = cal_x - cal_w//2 + 15 + col * 40
            draw.rectangle([x, y, x+32, y+45], outline="black", width=1)

    # Highlight a day
    hl_x = cal_x + 40
    hl_y = cal_y - 80 + 55
    draw.ellipse([hl_x-18, hl_y-18, hl_x+18, hl_y+18], fill="black")

    # Checkmark
    check_x, check_y = W//2, cal_y+180
    circle(draw, check_x, check_y, 40, outline="black", width=4)
    line(draw, check_x-18, check_y, check_x-5, check_y+18, fill="black", width=5)
    line(draw, check_x-5, check_y+18, check_x+20, check_y-15, fill="black", width=5)

    # Happy stick figure
    fig_x, fig_y = W//2, cal_y+340
    stick_figure(draw, fig_x, fig_y, scale=1.8, hand_up=True)

    text(draw, "Online booking.", W//2, 760, size=44)
    text(draw, "Patients book. Appointments confirm.", W//2, 820, size=32)

# ─────────────────────────────────────────────────────────────────
# SCENE 3: [11-15s] CTA - IVCS logo + tagline
# ─────────────────────────────────────────────────────────────────
def scene_cta(draw, frame, total):
    t = (frame - 11*FPS) / FPS
    fade_in = min(1.0, t * 2)

    draw.rectangle([0, 0, W, H], fill="white")

    # Logo-style text
    text(draw, "Illinois Valley", W//2, 420, size=56)
    text(draw, "Counseling", W//2, 490, size=56)

    # Divider line
    lx1, ly = W//2 - 100, 560
    draw.line([lx1, ly, lx1+200, ly], fill="black", width=3)

    # Tagline
    text(draw, "Book online. Always open.", W//2, 610, size=36)

    # Phone
    text(draw, "(815) 993-1614", W//2, 700, size=32)

    # Website
    text(draw, "illinoisvalleycounseling.com", W//2, 750, size=28)

# ─────────────────────────────────────────────────────────────────
# RENDER ALL FRAMES
# ─────────────────────────────────────────────────────────────────
SCENE_BREAKS = [
    (0,               scene_search),
    (3.5 * FPS,      scene_problem),
    (7.5 * FPS,      scene_solution),
    (11.0 * FPS,     scene_cta),
]

print("Rendering frames...")
for fn in range(TOTAL_FRAMES):
    # Find which scene
    scene_fn = SCENE_BREAKS[0][1]
    for break_frame, sf in SCENE_BREAKS:
        if fn >= break_frame:
            scene_fn = sf

    draw_scene(scene_fn, fn, TOTAL_FRAMES)
    if fn % 30 == 0:
        print(f"  Frame {fn}/{TOTAL_FRAMES} ({fn//FPS}s)")

print("Frames rendered.")

# ─────────────────────────────────────────────────────────────────
# ENCODE VIDEO
# ─────────────────────────────────────────────────────────────────
print("Encoding video...")
run([
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", f"{FRAMES}/frame_%04d.png",
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "23",
    "-pix_fmt", "yuv420p",
    "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:white",
    OUTPUT
])

print(f"\nOutput: {OUTPUT}")
print(f"Size: {os.path.getsize(OUTPUT)//1024}KB")
