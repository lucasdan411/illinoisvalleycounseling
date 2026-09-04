#!/usr/bin/env python3
"""IVC Stickman Whiteboard Explainer - with edge-tts narration"""

import asyncio, edge_tts, os, subprocess
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
FPS = 30

# Palette
WHITE  = (255, 255, 255)
BLACK  = (30, 30, 30)
GRAY   = (120, 120, 120)
TEAL   = (26, 95, 90)
AMBER  = (200, 140, 40)
GREEN  = (60, 160, 90)
RED    = (200, 60, 50)

def load_font(size):
    for path in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

FONT_TITLE = load_font(52)
FONT_SUB   = load_font(36)
FONT_BODY  = load_font(24)
FONT_SMALL = load_font(20)

# ── Drawing helpers ──────────────────────────────────────────────────────────
def circle(draw, cx, cy, r, fill):
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill)

def rounded_rect(draw, xy, r, fill, outline=None, width=1):
    x0,y0,x1,y1 = xy
    draw.rounded_rectangle([x0,y0,x1,y1], radius=r, fill=fill, outline=outline, width=width)

def text_center(draw, text, cx, cy, font, color):
    bbox = draw.textbbox((0,0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    draw.text((cx-tw//2, cy-th//2), text, font=font, fill=color)

# ── Scene 1: Phone search frustration ─────────────────────────────────────────
def scene1(draw, t):
    draw.rectangle([0, 0, W, H], fill=WHITE)
    
    # Table
    rounded_rect(draw, [W//2-320, 490, W//2+320, 510], 4, GRAY)
    
    # Person
    cx, cy = W//2-100, 370
    circle(draw, cx, cy-80, 22, TEAL)     # head
    draw.ellipse([cx-22, cy-30, cx+22, cy+50], fill=TEAL)  # body
    
    # Eyes looking down
    draw.ellipse([cx-10, cy-75, cx-3, cy-69], fill=WHITE)
    draw.ellipse([cx+3, cy-75, cx+10, cy-69], fill=WHITE)
    # Frown
    draw.arc([cx-12, cy-62, cx+12, cy-48], 0, 180, fill=TEAL, width=2)
    
    # Arm reaching right
    draw.line([cx+20, cy, cx+100, cy+30], fill=TEAL, width=4)
    draw.line([cx+100, cy+30, cx+180, cy+30], fill=TEAL, width=4)
    
    # Phone
    px, py = W//2+180, 350
    rounded_rect(draw, [px-30, py-55, px+30, py+55], 8, BLACK)
    rounded_rect(draw, [px-24, py-46, px+24, py+44], 4, (210,225,245))
    draw.text((px-22, py-35), "No therapists", font=FONT_SMALL, fill=RED)
    draw.text((px-22, py-15), "nearby...", font=FONT_SMALL, fill=RED)
    
    # Confusion marks
    for i, q in enumerate(["?", "?", "!"]):
        qx = cx + 35 + i*25
        qy = cy - 110 - i*10 + int(5 * abs((t*2+i*0.5)%1 - 0.5))
        draw.text((qx, qy), q, font=FONT_SUB, fill=RED)
    
    # Label
    text_center(draw, "When someone searches 'therapist near me'...", W//2, 560, FONT_SUB, GRAY)
    text_center(draw, "they can't find your practice.", W//2, 600, FONT_BODY, GRAY)

# ── Scene 2: Missed call ────────────────────────────────────────────────────────
def scene2(draw, t):
    draw.rectangle([0, 0, W, H], fill=WHITE)
    
    # Ringing phone center
    px, py = W//2, 280
    
    # Animated ring waves
    for i in range(3):
        phase = (t * 2.5 + i * 0.25) % 1.0
        r = 60 + phase * 60
        alpha = int(180 * (1 - phase))
        # Draw ring as ellipse outline (no alpha in RGB)
        draw.ellipse([px-r, py-r, px+r, py+r], outline=AMBER, width=3)
    
    # Phone body
    rounded_rect(draw, [px-42, py-75, px+42, py+75], 12, BLACK)
    rounded_rect(draw, [px-34, py-64, px+34, py+58], 6, (220,230,240))
    draw.text((px-30, py-25), "Missed Call", font=FONT_SMALL, fill=RED)
    draw.text((px-30, py-5), "No answer...", font=FONT_SMALL, fill=GRAY)
    
    # Sad person left
    cx, cy = W//2-280, 360
    circle(draw, cx, cy-80, 22, TEAL)
    draw.ellipse([cx-22, cy-30, cx+22, cy+50], fill=TEAL)
    draw.ellipse([cx-10, cy-75, cx-3, cy-69], fill=WHITE)
    draw.ellipse([cx+3, cy-75, cx+10, cy-69], fill=WHITE)
    draw.arc([cx-12, cy-62, cx+12, cy-48], 0, 180, fill=TEAL, width=2)
    # Arms down (gave up)
    draw.line([cx-22, cy, cx-70, cy+60], fill=TEAL, width=4)
    draw.line([cx+22, cy, cx+70, cy+60], fill=TEAL, width=4)
    
    # Stat
    text_center(draw, "70% of people who call don't book online.", W//2, 490, FONT_SUB, AMBER)
    text_center(draw, "They move on. That lead is gone.", W//2, 535, FONT_BODY, GRAY)

# ── Scene 3: Not listed ────────────────────────────────────────────────────────
def scene3(draw, t):
    draw.rectangle([0, 0, W, H], fill=WHITE)
    
    text_center(draw, "Where are new clients searching?", W//2, 70, FONT_TITLE, BLACK)
    
    competitors = [
        ("Psychology Today", True),
        ("BetterHelp", True),
        ("Zencare", True),
        ("Your practice?", False),
    ]
    
    cy = 160
    for name, listed in competitors:
        col = GREEN if listed else RED
        rounded_rect(draw, [W//2-280, cy, W//2+280, cy+65], 8, WHITE, outline=col, width=3)
        if listed:
            # Checkmark
            cx = W//2-240
            circle(draw, cx, cy+32, 14, GREEN)
            draw.line([cx-8, cy+32, cx-3, cy+39], fill=WHITE, width=3)
            draw.line([cx-3, cy+39, cx+9, cy+23], fill=WHITE, width=3)
        else:
            cx = W//2-240
            draw.line([cx-12, cy+20, cx+12, cy+48], fill=RED, width=4)
            draw.line([cx+12, cy+20, cx-12, cy+48], fill=RED, width=4)
        draw.text((W//2-200, cy+18), name, font=FONT_BODY, fill=col)
        cy += 85
    
    text_center(draw, "Psychology Today has 10 million visits a month.", W//2, cy+20, FONT_BODY, GRAY)
    text_center(draw, "Are you showing up there?", W//2, cy+55, FONT_SUB, BLACK)

# ── Scene 4: Solution ──────────────────────────────────────────────────────────
def scene4(draw, t):
    draw.rectangle([0, 0, W, H], fill=WHITE)
    
    text_center(draw, "Here's the fix.", W//2, 70, FONT_TITLE, TEAL)
    
    items = [
        ("Google Business Profile", "Verified and visible in search results", GREEN),
        ("Psychology Today", "Listed where new clients are actively searching", GREEN),
        ("Online Booking", "Patients book 24/7, no phone tag, no missed calls", GREEN),
        ("Google Ads", "Appearing at the exact moment someone is looking", AMBER),
    ]
    
    cy = 170
    for title, sub, col in items:
        cx_chk = W//2-280
        circle(draw, cx_chk, cy+30, 16, col)
        draw.line([cx_chk-8, cy+30, cx_chk-3, cy+38], fill=WHITE, width=3)
        draw.line([cx_chk-3, cy+38, cx_chk+9, cy+22], fill=WHITE, width=3)
        draw.text((W//2-240, cy+14), title, font=FONT_BODY, fill=BLACK)
        draw.text((W//2-240, cy+38), sub, font=FONT_SMALL, fill=GRAY)
        cy += 78
    
    text_center(draw, "One platform. Full visibility. More bookings.", W//2, cy+20, FONT_SUB, TEAL)

# ── Scene 5: CTA ───────────────────────────────────────────────────────────────
def scene5(draw, t):
    draw.rectangle([0, 0, W, H], fill=WHITE)
    
    # Phone center
    px, py = W//2, 270
    rounded_rect(draw, [px-90, py-160, px+90, py+140], 16, BLACK)
    rounded_rect(draw, [px-76, py-140, px+76, py+120], 10, (235,242,250))
    
    # Profile text
    text_center(draw, "Illinois Valley Counseling", px, py-110, load_font(20), TEAL)
    text_center(draw, "Services", px, py-85, load_font(20), TEAL)
    
    # Book Now button
    rounded_rect(draw, [px-60, py-60, px+60, py-22], 8, GREEN)
    text_center(draw, "Book Now", px, py-46, load_font(22), WHITE)
    
    # Calendar slots
    text_center(draw, "Available Slots:", px, py+5, FONT_SMALL, GRAY)
    slots = [("Mon 9am", True), ("Tue 2pm", True), ("Wed 10am", True), ("Thu 3pm", True)]
    for i, (slot, avail) in enumerate(slots):
        sx = px - 70 + (i % 2) * 80
        sy = py + 30 + (i // 2) * 35
        col = GREEN if avail else GRAY
        rounded_rect(draw, [sx, sy, sx+68, sy+28], 4, (220,245,220), outline=col, width=1)
        text_center(draw, slot, sx+34, sy+14, load_font(14), col)
    
    # Tagline
    text_center(draw, "Get Found. Get Booked. Grow.", W//2, 490, FONT_TITLE, TEAL)
    text_center(draw, "Your practice. Online. Booking itself.", W//2, 555, FONT_SUB, GRAY)
    text_center(draw, "Book your strategy call today.", W//2, 610, FONT_BODY, BLACK)

# ── Title card ─────────────────────────────────────────────────────────────────
def make_title():
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    # Teal band
    draw.rectangle([0, H//2-90, W, H//2+90], fill=TEAL)
    text_center(draw, "Illinois Valley Counseling Services", W//2, H//2-20, load_font(52), WHITE)
    text_center(draw, "Get Found. Get Booked. Grow.", W//2, H//2+40, load_font(32), (200,220,255))
    return img

# ── Render frames ──────────────────────────────────────────────────────────────
def render_scene(scene_fn, duration, fps=FPS, out_dir=None):
    n = scene_fn.__name__
    out_dir = out_dir or f"/tmp/ivc_scenes/{n}"
    os.makedirs(out_dir, exist_ok=True)
    n_frames = duration * fps
    for i in range(n_frames):
        t = i / fps
        img = Image.new("RGB", (W, H), WHITE)
        draw = ImageDraw.Draw(img)
        scene_fn(draw, t)
        img.save(f"{out_dir}/frame_{i:04d}.png")
        if i % 60 == 0:
            print(f"  {n}: {i}/{n_frames}")
    print(f"  {n}: done {n_frames} frames")
    return out_dir

def frames_to_mp4(frame_dir, output_mp4, fps=FPS):
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", f"{frame_dir}/frame_%04d.png",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        output_mp4
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  FFMPEG ERROR: {r.stderr[-300:]}")
        return False
    return True

# ── Concatenate videos ──────────────────────────────────────────────────────────
def concat_videos(mp4_list, output):
    list_file = "/tmp/ivc_concat.txt"
    with open(list_file, "w") as f:
        for mp4 in mp4_list:
            f.write(f"file '{mp4}'\n")
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", list_file,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        output
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  CONCAT ERROR: {r.stderr[-300:]}")
        return False
    return True

# ── Main ──────────────────────────────────────────────────────────────────────
async def gen_narrations():
    print("Generating narrations...")
    os.makedirs("/tmp/ivc_narration", exist_ok=True)
    
    narrations = [
        ("title",  "Illinois Valley Counseling Services. Get Found. Get Booked. Grow."),
        ("scene1", "When someone searches 'therapist near me'... they can't find your practice. You're invisible. They move on to a competitor."),
        ("scene2", "They try to call. No answer. They leave a voicemail. They never hear back. That potential client is gone forever."),
        ("scene3", "Meanwhile, your competitors are listed on Psychology Today, BetterHelp, and Zencare. New clients are finding them. Not you."),
        ("scene4", "Here's the fix. We get you listed on Psychology Today, set up your Google Business Profile, and add online booking so patients can book any time, day or night."),
        ("scene5", "Now when someone searches for a therapist near you... you're right there. They book an appointment online. Your calendar fills up. Your practice grows."),
    ]
    
    for name, text in narrations:
        out = f"/tmp/ivc_narration/{name}.mp3"
        await edge_tts.Communicate(text, "en-US-AndrewNeural").save(out)
        sz = os.path.getsize(out)
        print(f"  {name}: {sz//1024}KB")
    
    return narrations

def main():
    print("=== IVC Stickman Explainer Builder ===\n")
    
    # 1. Narrations
    narrations = asyncio.run(gen_narrations())
    
    # 2. Render scenes
    print("\nRendering frames...")
    os.makedirs("/tmp/ivc_scenes", exist_ok=True)
    
    # Title card
    print("  Title card...")
    title_img = make_title()
    title_dir = "/tmp/ivc_scenes/title"
    os.makedirs(title_dir, exist_ok=True)
    for i in range(3 * FPS):
        title_img.save(f"{title_dir}/frame_{i:04d}.png")
    
    scene_defs = [
        (scene1, 12),
        (scene2, 12),
        (scene3, 12),
        (scene4, 12),
        (scene5, 14),
    ]
    
    for fn, dur in scene_defs:
        render_scene(fn, dur)
    
    # 3. Compile to MP4
    print("\nCompiling scenes...")
    os.makedirs("/tmp/ivc_scene_mp4s", exist_ok=True)
    scene_mp4s = {}
    
    # Title
    mp4 = "/tmp/ivc_scene_mp4s/title.mp4"
    frames_to_mp4("/tmp/ivc_scenes/title", mp4, fps=30)
    scene_mp4s["title"] = mp4
    
    for fn, dur in scene_defs:
        mp4 = f"/tmp/ivc_scene_mp4s/{fn.__name__}.mp4"
        frames_to_mp4(f"/tmp/ivc_scenes/{fn.__name__}", mp4)
        sz = os.path.getsize(mp4)
        scene_mp4s[fn.__name__] = mp4
        print(f"  {fn.__name__}: {sz//1024}KB")
    
    # 4. Concat all scenes
    print("\nConcatenating...")
    order = ["title", "scene1", "scene2", "scene3", "scene4", "scene5"]
    mp4s = [scene_mp4s[n] for n in order]
    
    concat_mp4 = "/tmp/ivc_stickman_no_audio.mp4"
    concat_videos(mp4s, concat_mp4)
    sz = os.path.getsize(concat_mp4)
    dur = float(subprocess.check_output([
        "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
        "-of", "csv=p=0", concat_mp4
    ], text=True).strip())
    print(f"  Raw concat: {sz//1024}KB, {dur:.1f}s")
    
    print("\nDone!")

if __name__ == "__main__":
    main()
