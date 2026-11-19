# 依人工挑選結果下載額外照片（key-2.jpg / key-3.jpg），寫入 data/media.js 的 more 欄位
# 用法: python3 -I tools/addmore.py cands.json
import json, sys, os, subprocess
from PIL import Image
UA = "DogQuizBuilder/1.0 (educational teaching page; https://mattsue1003.github.io/)"
PICK = dict(taiwan=[1,2], mutt=[1,5], shiba=[1,2], akita=[8,15], golden=[12,13], lab=[3,13], corgi=[1,2],
            husky=[3,4], poodle=[11,13], pom=[11,2], chihuahua=[3,12], dachshund=[7,12], frenchie=[6,4],
            pug=[1,4], bichon=[11,13], schnauzer=[10,6], border=[8,4], gsd=[9,13], beagle=[6,7],
            dalmatian=[1,4], basenji=[11,5])
c = json.load(open(sys.argv[1]))
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = open(os.path.join(root, "data/media.js"), encoding="utf-8").read()
head, body = src.split("window.MEDIA=", 1)
mjson, rest = body.split("\n};", 1)
M = json.loads(mjson + "\n}")
for k, idx in PICK.items():
    more = []
    for n, i in enumerate(idx, start=2):
        p = c[k][i]; f = os.path.join(root, f"assets/img/{k}-{n}.jpg")
        for t in range(4):
            if os.path.exists(f) and os.path.getsize(f) > 8000: break
            subprocess.run(["curl", "-s", "-L", "-A", UA, "-o", f, p["thumb"]])
        im = Image.open(f).convert("RGB")
        if max(im.size) > 1000: im.thumbnail((1000, 1000))
        im.save(f, quality=84, optimize=True)
        more.append(dict(file=p["file"], author=p["author"], lic=p["lic"], licurl=p["licurl"], page=p["page"]))
    M[k]["more"] = more
open(os.path.join(root, "data/media.js"), "w", encoding="utf-8").write(head + "window.MEDIA=" + json.dumps(M, ensure_ascii=False, indent=1) + ";" + rest)
print("done", len(PICK))
