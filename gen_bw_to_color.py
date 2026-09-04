#!/usr/bin/env python3
import httpx, time, json, re

with open('gen_kling.py') as f:
    content = f.read()
m = re.search('KEY\s*=\s*["\'](sk_[^"\']+)["\']', content)
KEY = m.group(1)
BASE = "https://giggle.pro"
H = {"x-auth": KEY, "Content-Type": "application/json"}

SCENES = [
    ("s1_bw_heavy",    4, "Black and white sketch, person at desk with head in hands looking sad and heavy"),
    ("s2_bw_alone",    4, "Black and white sketch, person at desk alone, phone turned off beside them"),
    ("s3_bw_not_found", 4, "Black and white sketch, person looking at a list, their name is missing from it"),
    ("s4_color_burst", 3, "Color fills into a black and white drawing, teal and gold light bursting in dynamically"),
    ("s5_full_color",  4, "Colorful vibrant illustration, happy confident person smiling at phone showing booked appointment"),
    ("s6_title_card",  4, "Clean professional title card on white background, teal and white, elegant text reveal animation"),
]

print("Submitting 6 new B&W-to-color scenes...")
tids = {}
for name, dur, prompt in SCENES:
    for attempt in range(5):
        r = httpx.post(BASE + "/api/v1/generation/text-to-video", headers=H, json={
            "prompt": prompt, "model": "kling25",
            "duration": dur, "aspect_ratio": "16:9", "resolution": "720p"
        }, timeout=30)
        d = r.json()
        if d.get("code") == 200:
            tids[name] = d["data"]["task_id"]
            print(f"  ✓ {name}: {tids[name]}")
            break
        else:
            print(f"  ✗ {name} attempt {attempt+1}: {d.get('msg','')[:60]}")
            time.sleep(3)
    time.sleep(2)

with open("/tmp/ivc_new_tids.json","w") as f:
    json.dump(tids, f)
print(f"\n{len(tids)}/{len(SCENES)} submitted")

# Poll until done
if tids:
    print("\nWaiting 90s before polling...")
    time.sleep(90)
    print("Polling...")
    done = {}
    while len(done) < len(tids):
        for name, tid in tids.items():
            if name in done:
                continue
            res = httpx.get(BASE + f"/api/v1/generation/task/query?task_id={tid}", headers=H, timeout=15).json()["data"]
            s = res.get("status","?")
            u = res.get("urls",[])
            e = res.get("err_msg","")
            if u:
                done[name] = u[0]
                print(f"  ✓ {name}: {u[0][:80]}")
            elif s == "failed":
                done[name] = None
                print(f"  ✗ {name}: FAILED -- {e[:60]}")
            else:
                print(f"  {name}: {s}")
        if len(done) < len(tids):
            time.sleep(30)

    print(f"\n{sum(1 for v in done.values() if v)}/{len(tids)} scenes complete")
    with open("/tmp/ivc_new_done.json","w") as f:
        json.dump(done, f)
    print("Results saved to /tmp/ivc_new_done.json")
