#!/usr/bin/env python3
"""Re-submit IVC sketch clips with proper durations matching narration"""
import httpx, time, re, os

with open('/home/storyclaw/.openclaw/workspace-github-repo-executor-pro/illinoisvalleycounseling/gen_kling.py') as f:
    content = f.read()
KEY = re.search(r'KEY\s*=\s*[\"\'](sk_[^\"\']+)[\"\']', content).group(1)

BASE = "https://giggle.pro"
HEADERS = {"x-auth": KEY}

# Audio durations (from earlier measurement)
AUDIO_DUR = {
    "title":  7.8,
    "scene1": 9.9,
    "scene2": 11.0,
    "scene3": 10.2,
    "scene4": 11.7,
    "scene5": 11.6,
}

SCENES = [
    {
        "id": "clip_title",
        "audio_id": "title",
        "prompt": (
            "Hand-drawn black ink sketch on pure white background. "
            "Clean elegant title card. Bold text appears letter by letter: "
            "'Illinois Valley Counseling Services'. Below it, smaller text: "
            "'Get Found. Get Booked. Grow.' Minimalist cartoon line art style. "
            "No characters, just clean lettering on white. Slow, calm reveal."
        ),
        "duration": 8,
    },
    {
        "id": "clip1",
        "audio_id": "scene1",
        "prompt": (
            "Hand-drawn black ink sketch on pure white background. "
            "A solitary figure standing alone, shoulders slumped, head tilted down, "
            "looking tired and weighed down. Simple expressive line art face. "
            "The figure barely moves, just slightly sways. Heavy, somber mood. "
            "Pure black linework on white. No color."
        ),
        "duration": 10,
    },
    {
        "id": "clip2",
        "audio_id": "scene2",
        "prompt": (
            "Hand-drawn black ink sketch on pure white background. "
            "The same solitary figure now with one hand reaching out tentatively, "
            "mouth slightly open, taking a first tentative step. Simple expressive line art. "
            "Pure black ink on white. Slow, tentative movement. Transition moment."
        ),
        "duration": 11,
    },
    {
        "id": "clip3",
        "audio_id": "scene3",
        "prompt": (
            "Hand-drawn black ink sketch on pure white background. "
            "The same figure now standing with shoulders back, head held higher, "
            "mouth curved in a slight warm half-smile. Confident but understated. "
            "Simple expressive line art. Pure black on white. Gentle hopeful energy."
        ),
        "duration": 11,
    },
    {
        "id": "clip4",
        "audio_id": "scene4",
        "prompt": (
            "Hand-drawn black ink sketch on pure white background. "
            "The same figure now fully upright and confident, standing tall with open posture, "
            "looking calm and settled. A subtle sense of peace. "
            "Simple expressive line art. Pure black on white. Warm, quiet resolution."
        ),
        "duration": 12,
    },
    {
        "id": "clip5",
        "audio_id": "scene5",
        "prompt": (
            "Hand-drawn black ink sketch on pure white background. "
            "The same confident figure standing peacefully. Text fades in: "
            "'Book your free consult' in clean simple lettering. "
            "The figure looks calm and complete. Simple minimal cartoon line art. "
            "Pure black on white. Clean warm finish."
        ),
        "duration": 12,
    },
]

def submit(prompt, duration):
    resp = httpx.post(
        f"{BASE}/api/v1/generation/text-to-video",
        headers=HEADERS,
        json={
            "prompt": prompt,
            "model": "kling25",
            "duration": duration,
            "aspect_ratio": "16:9",
            "resolution": "720p",
        },
        timeout=30,
    )
    data = resp.json()
    if data.get("code") != 200:
        raise Exception(f"Submit failed: {data}")
    return data["data"]["task_id"]

def query(task_id):
    resp = httpx.get(f"{BASE}/api/v1/generation/task/query?task_id={task_id}", headers=HEADERS, timeout=15)
    return resp.json()["data"]

print("Submitting all clips with proper durations...")
task_ids = {}
for scene in SCENES:
    dur = scene["duration"]
    tid = submit(scene["prompt"], dur)
    task_ids[scene["id"]] = {"task_id": tid, "audio_id": scene["audio_id"], "duration": dur}
    print(f"  {scene['id']} ({dur}s): {tid}")
    time.sleep(1)

print(f"\nAll submitted. Will poll after 60s...")

# Wait 60s before first poll
time.sleep(60)

print("Polling...")
done = {}
while len(done) < len(task_ids):
    for name, info in list(task_ids.items()):
        if name in done:
            continue
        result = query(info["task_id"])
        status = result.get("status", "")
        urls = result.get("urls", [])
        err = result.get("err_msg", "")
        if status == "success" and urls:
            done[name] = urls[0]
            print(f"  ✓ {name}: DONE")
        elif status == "failed":
            done[name] = None
            print(f"  ✗ {name}: FAILED — {err[:60]}")
        else:
            print(f"  {name}: {status}")
    if len(done) < len(task_ids):
        time.sleep(30)

print(f"\nResults: {len([v for v in done.values() if v])}/{len(task_ids)} successful")
for name, url in done.items():
    if url:
        print(f"  {name}: {url[:80]}...")
