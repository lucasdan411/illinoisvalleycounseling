#!/usr/bin/env python3
"""Generate IVC stickman whiteboard explainer clips via Giggle kling25"""

import httpx, json, time, os, sys

KEY = "sk_prod_IJJ31k9zA1fPbWhPySyDFDbqTtintzs5M4iJ4TH6zVc="
BASE = "https://giggle.pro"
HEADERS = {"x-auth": KEY, "Content-Type": "application/json"}

SCENES = [
    {
        "id": "clip1",
        "prompt": (
            "Whiteboard animation style. Simple hand-drawn stick figure sitting alone at a desk at night, "
            "frustrated, scrolling on a smartphone. Phone screen shows 'No therapists found nearby'. "
            "White background, black stroke stick figure drawings, animated like a whiteboard explainer video. "
            "Empathetic humor, relatable frustration. No text, no logos."
        ),
        "duration": 5,
    },
    {
        "id": "clip2",
        "prompt": (
            "Whiteboard animation style. Stick figure at a desk looking at a ringing phone that keeps ringing. "
            "They look sad, put the phone down. Phone shows a missed call icon. "
            "Simple black stroke drawings on white background, marker-style animation. "
            "Emotional, relatable moment of missed opportunity. No text, no logos."
        ),
        "duration": 5,
    },
    {
        "id": "clip3",
        "prompt": (
            "Whiteboard animation style. A stick figure looking at a computer monitor showing a list of competitor therapy practices. "
            "Monitor displays logos like Psychology Today and BetterHelp with checkmarks. "
            "The stick figure looks confused and left out, like they're not on the list. "
            "Simple hand-drawn whiteboard style, black strokes on white, animated drawings. No text, no logos."
        ),
        "duration": 5,
    },
    {
        "id": "clip4",
        "prompt": (
            "Whiteboard animation style. A happy stick figure therapist shaking hands warmly with a smiling client stick figure. "
            "A laptop screen between them shows a calendar with many time slots booked and a green 'Confirm' button. "
            "Simple black stroke drawings on white background, whiteboard explainer animation style. "
            "Warm, hopeful feeling. No text, no logos."
        ),
        "duration": 5,
    },
    {
        "id": "clip5",
        "prompt": (
            "Whiteboard animation style. A stick figure holding a smartphone showing Psychology Today profile for Illinois Valley Counseling. "
            "They tap the green 'Book Now' button and a calendar appears with open appointment slots. "
            "They smile and tap to confirm. Simple hand-drawn whiteboard animation, black strokes on white. "
            "Satisfying, empowering moment. No text, no logos."
        ),
        "duration": 5,
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
    resp = httpx.get(
        f"{BASE}/api/v1/generation/task/query?task_id={task_id}",
        headers={"x-auth": KEY},
        timeout=15,
    )
    return resp.json()["data"]

def poll_until_done(task_id, timeout=300):
    start = time.time()
    while time.time() - start < timeout:
        result = query(task_id)
        status = result.get("status", "")
        print(f"  [{int(time.time()-start)}s] {status}", flush=True)
        if status == "success" or status == "failed":
            return result
        time.sleep(15)
    raise Exception("Timeout waiting for task")

OUT_DIR = "/tmp/ivc_kling"
os.makedirs(OUT_DIR, exist_ok=True)

# Submit all clips first
print("Submitting all clips...")
task_ids = {}
for scene in SCENES:
    tid = submit(scene["prompt"], scene["duration"])
    task_ids[scene["id"]] = tid
    print(f"  {scene['id']}: {tid}")
    time.sleep(2)  # Brief delay between submits

print(f"\nAll submitted. Polling {len(task_ids)} clips...")

for scene in SCENES:
    tid = task_ids[scene["id"]]
    print(f"\n  Waiting for {scene['id']}...")
    try:
        result = poll_until_done(tid)
        urls = result.get("urls", [])
        if urls:
            print(f"  DONE: {urls[0]}")
            # Download
            out_path = f"{OUT_DIR}/{scene['id']}.mp4"
            r = httpx.get(urls[0], timeout=120, follow_redirects=True)
            with open(out_path, "wb") as f:
                f.write(r.content)
            print(f"  Saved: {out_path} ({os.path.getsize(out_path)//1024}KB)")
        else:
            print(f"  FAILED: {result.get('err_msg', 'no URL')}")
    except Exception as e:
        print(f"  ERROR: {e}")

print("\nAll done!")
for f in sorted(os.listdir(OUT_DIR)):
    print(f"  {f}: {os.path.getsize(os.path.join(OUT_DIR, f))//1024}KB")
