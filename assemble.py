#!/usr/bin/env python3
"""Assemble IVC sketch video from Kling clips + edge-tts narration"""
import subprocess, os, json

TMP = "/tmp/ivc"
OUT = "/tmp/ivc/ivc_sketch_final.mp4"
os.makedirs(f"{TMP}/scene_mp4s", exist_ok=True)

SCENES = [
    # (clip_file, audio_file, start_time_in_audio)
    ("clip_title.mp4", "narration_title.mp3",  0.0),
    ("clip1.mp4",      "narration_scene1.mp3", 0.0),
    ("clip2.mp4",      "narration_scene2.mp3", 0.0),
    ("clip3.mp4",      "narration_scene3.mp3", 0.0),
    ("clip4.mp4",      "narration_scene4.mp3", 0.0),
    ("clip5.mp4",      "narration_scene5.mp3", 0.0),
]

AUDIO_ORDER = [
    "narration_title.mp3",
    "narration_scene1.mp3",
    "narration_scene2.mp3",
    "narration_scene3.mp3",
    "narration_scene4.mp3",
    "narration_scene5.mp3",
]

def run(cmd, desc=""):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"ERROR {desc}: {r.stderr[-400:]}")
    else:
        print(f"  OK: {desc}")
    return r.returncode == 0

# Step 1: Trim each audio to 5s and make video+audio clips
print("Making scene clips with audio...")
for clip, audio, offset in SCENES:
    clip_path = f"{TMP}/videos/{clip}"
    audio_path = f"{TMP}/narration_{audio.replace('narration_','')}"
    out = f"{TMP}/scene_mp4s/{clip.replace('.mp4','_a.mp4')}"
    # Trim audio to 5s starting from offset
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(offset), "-t", "5", "-i", audio_path,
        "-i", clip_path,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-vf", "scale=1280:720",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        "-movflags", "+faststart",
        out
    ]
    run(cmd, f"{clip} + audio")

# Step 2: Concat all scene clips
print("Concatenating all scenes...")
concat_list = f"{TMP}/concat.txt"
with open(concat_list, "w") as f:
    for clip, _, _ in SCENES:
        f.write(f"file '{TMP}/scene_mp4s/{clip.replace('.mp4','_a.mp4')}'\n")

concat_out = f"{TMP}/ivc_concat.mp4"
cmd = [
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0", "-i", concat_list,
    "-c:v", "libx264", "-preset", "fast", "-crf", "20",
    "-c:a", "aac", "-b:a", "128k",
    "-movflags", "+faststart",
    concat_out
]
run(cmd, "concat all scenes")
sz = os.path.getsize(concat_out) if os.path.exists(concat_out) else 0
print(f"  Output: {sz//1024//1024}MB")

# Step 3: Copy to workspace
dest = "/home/storyclaw/.openclaw/workspace-github-repo-executor-pro/illinoisvalleycounseling/ivc_sketch_final.mp4"
subprocess.run(["cp", concat_out, dest])
print(f"  Copied to workspace")
