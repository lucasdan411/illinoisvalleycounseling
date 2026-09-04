#!/usr/bin/env python3
"""Assemble IVC sketch video — 30s version with sped-up voiceover"""
import subprocess, os

TMP = "/tmp/ivc"
OUT_DIR = "/home/storyclaw/.openclaw/workspace-github-repo-executor-pro/illinoisvalleycounseling"
final_dest = f"{OUT_DIR}/ivc_sketch_final.mp4"

# Clips in order (5s each = 30s total)
CLIPS = [
    "clip_title.mp4",
    "clip1.mp4",
    "clip2.mp4",
    "clip3.mp4",
    "clip4.mp4",
    "clip5.mp4",
]

os.makedirs(f"{TMP}/scene_mp4s", exist_ok=True)

def run(cmd, desc=""):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ERROR {desc}: {r.stderr[-300:]}")
        return False
    print(f"  OK: {desc}")
    return True

# Step 1: Concatenate all video clips (no audio yet)
print("Concatenating video clips...")
concat_list = f"{TMP}/concat_video.txt"
with open(concat_list, "w") as f:
    for clip in CLIPS:
        f.write(f"file '{TMP}/videos/{clip}'\n")

video_only = f"{TMP}/video_only.mp4"
run([
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0", "-i", concat_list,
    "-c:v", "libx264", "-preset", "fast", "-crf", "20",
    "-pix_fmt", "yuv420p", "-vf", "scale=1280:720",
    "-an",
    video_only
], "video concat")

# Step 2: Speed up voiceover 1.5x so 45s → 30s
print("Speeding up voiceover 1.5x...")
vo_fast = f"{TMP}/vo_fast.mp3"
run([
    "ffmpeg", "-y",
    "-i", f"{TMP}/vo_full.mp3",
    "-filter:a", "atempo=1.5",
    "-q:a", "0", vo_fast
], "voiceover speed up")

vo_dur = float(subprocess.check_output([
    "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
    "-of", "csv=p=0", vo_fast
], text=True).strip())
print(f"  Voiceover duration: {vo_dur:.2f}s")

# Step 3: Combine video + sped-up audio
print("Combining video + audio...")
run([
    "ffmpeg", "-y",
    "-i", video_only,
    "-i", vo_fast,
    "-c:v", "libx264", "-preset", "fast", "-crf", "20",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k",
    "-shortest",
    "-movflags", "+faststart",
    final_dest
], "final combine")

sz = os.path.getsize(final_dest) if os.path.exists(final_dest) else 0
dur = float(subprocess.check_output([
    "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
    "-of", "csv=p=0", final_dest
], text=True).strip())
print(f"\nDone! {sz//1024//1024}MB, {dur:.1f}s")
print(f"Output: {final_dest}")
