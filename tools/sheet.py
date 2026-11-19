# 把候選圖做成編號對照表（每張 3 種狗 × 16 張，兩排）
# 用法: python3 -I tools/sheet.py outdir
import json, sys, os, subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
UA = "DogQuizBuilder/1.0 (educational teaching page; https://mattsue1003.github.io/)"
d = sys.argv[1]; c = json.load(open(os.path.join(d, "cands.json")))
th = os.path.join(d, "th"); os.makedirs(th, exist_ok=True)
jobs = []
for k, L in c.items():
    for i, p in enumerate(L):
        u = p["thumb"].replace("/1000px-", "/330px-")
        jobs.append((os.path.join(th, f"{k}_{i}.jpg"), u))
def get(j):
    f, u = j
    for t in range(3):
        if os.path.exists(f) and os.path.getsize(f) > 2000: return
        subprocess.run(["curl", "-s", "-L", "-A", UA, "-o", f, u])
with ThreadPoolExecutor(4) as ex: list(ex.map(get, jobs))
font = ImageFont.truetype("/System/Library/Fonts/STHeiti Medium.ttc", 22)
keys = list(c); W, H = 250, 190; PER = 8
for s in range(0, len(keys), 3):
    ks = keys[s:s+3]
    im = Image.new("RGB", (PER*W + 120, len(ks)*2*(H+6) + len(ks)*10), "white"); dr = ImageDraw.Draw(im)
    for r, k in enumerate(ks):
        y0 = r*(2*(H+6)+10); dr.text((4, y0+80), k, fill="black", font=font)
        for i in range(len(c[k])):
            x = 120 + (i % PER)*W; y = y0 + (i // PER)*(H+6)
            try:
                t = Image.open(os.path.join(th, f"{k}_{i}.jpg")).convert("RGB"); t.thumbnail((W-6, H-4)); im.paste(t, (x, y))
            except Exception: pass
            dr.rectangle([x, y, x+30, y+24], fill="black"); dr.text((x+4, y-1), str(i), fill="yellow", font=font)
        dr.line([(0, y0-5), (im.width, y0-5)], fill="red", width=3)
    im.save(os.path.join(d, f"sheet{s//3}.jpg"), quality=82)
print("ok", len(keys))
