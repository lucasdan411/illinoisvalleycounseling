#!/usr/bin/env python3
"""Assemble B&W-to-color sketch video with voiceover"""
import subprocess, os

WORK  = "/tmp/ivc_kling_v2"
OUT   = "/home/storyclaw/.openclaw/workspace-github-repo-executor-pro/illinoisvalleycounseling"

# 6 clips x 5s = 30s
clips = [
    ("s1_bw_heavy.mp4",    "scene1.mp4"),
    ("s2_bw_alone.mp4",    "scene2.mp4"),
    ("s3_bw_not_found.mp4", "scene3.mp4"),
    ("s4_color_burst.mp4", "scene4.mp4"),
    ("s5_full_color.mp4",  "scene5.mp4"),
    ("s6_title_card.mp4",  "scene6.mp4"),
]

audio = {
    "scene1": f"{WORK}/vo_scene1.mp3",
    "scene2": f"{WORK}/vo_scene2.mp3",
    "scene3": f"{WORK}/vo_scene3.mp3",
    "scene4": f"{WORK}/vo_scene4.mp3",
    "scene5": f"{WORK}/vo_scene5.mp3",
    "scene6": f"{WORK}/vo_title.mp3",
}

CLIP_DUR = 5.0   # seconds per clip
N_CLIPS  = 6
TOTAL_DUR = CLIP_DUR * N_CLIPS  # 30s

# Total audio duration
total_audio = sum(
    float(subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", af], capture_output=True, text=True
    ).stdout.strip())
    for af in audio.values()
)
SPEEDUP = total_audio / TOTAL_DUR  # e.g. 51/30 = 1.67x
print(f"Total audio: {total_audio:.1f}s, Total video: {TOTAL_DUR}s")
print(f"Speed up audio by {SPEEDUP:.2f}x")

# Step 1: Trim + speed-up each audio to exactly CLIP_DUR
print("\nPreparing audio clips...")
for name, afile in audio.items():
    out = f"{WORK}/audio_{name}.wav"
    subprocess.run([
        "ffmpeg", "-y", "-i", afile,
        "-filter:a", f"atempo={SPEEDUP}",
        "-t", str(CLIP_DUR),
        out
    ], capture_output=True)
    print(f"  audio_{name}.wav: {CLIP_DUR}s")

# Step 2: Make each video clip with audio
print("\nMaking scene clips...")
for (clip_file, scene_out), name in zip(clips, audio.keys()):
    subprocess.run([
        "ffmpeg", "-y", "-i", f"{WORK}/{clip_file}",
        "-i", f"{WORK}/audio_{name}.wav",
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-shortest",
        f"{WORK}/{scene_out}"
    ], capture_output=True)
    print(f"  {scene_out} + audio")

# Step 3: Concat all clips
concat_list = "\n".join([f"file '{WORK}/scene{i}.mp4'" for i in range(1, N_CLIPS+1)])
with open(f"{WORK}/concat.txt", "w") as f:
    f.write(concat_list)

final_raw = f"{WORK}/concat_raw.mp4"
subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{WORK}/concat.txt",
    "-c:v", "copy",
    final_raw
], capture_output=True)
print(f"\nConcatenated: {final_raw}")

# Step 4: Combine with audio track (already embedded, just verify)
result = f"{OUT}/ivc_bw_to_color.mp4"
subprocess.run([
    "ffmpeg", "-y", "-i", final_raw,
    "-c:v", "copy", "-c:a", "aac",
    result
], capture_output=True)

dur = float(subprocess.run(
    ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
     "-of", "csv=p=0", result], capture_output=True, text=True
).stdout.strip())
sz = os.path.getsize(result) // (1024*1024)
print(f"\n✅ Done: {result}")
print(f"   Duration: {dur:.1f}s, Size: {sz}MB")
