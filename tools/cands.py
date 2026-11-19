# 找每種狗的額外照片候選：先抓 Commons 品種分類，不夠再用搜尋；篩授權、尺寸、檔名
# 用法: python3 -I tools/cands.py outdir
import json, sys, re, subprocess, html, os, time
UA = "DogQuizBuilder/1.0 (educational teaching page; https://mattsue1003.github.io/)"
OK = re.compile(r"^(CC BY(-SA)? [0-9.]+( [a-z]+)?|CC0|Public domain|PD.*)$", re.I)
BAD = re.compile(r"drawing|illustr|painting|stamp|logo|map|statue|sculpt|figur|toy_|plush|skull|skeleton|\.svg|\.tif|postcard|poster|sketch|art_|fresco|coin|badge", re.I)
CATS = dict(
 taiwan=["Taiwan Dog"], mutt=["Mixed-breed dogs", "Mongrels"], shiba=["Shiba Inu"], akita=["Akita Inu"],
 golden=["Golden Retrievers", "Golden Retriever"], lab=["Labrador Retrievers", "Labrador Retriever"],
 corgi=["Pembroke Welsh Corgis", "Pembroke Welsh Corgi"], husky=["Siberian Huskies", "Siberian Husky"],
 poodle=["Toy Poodles", "Toy Poodle", "Poodles"], pom=["Pomeranians (dogs)", "Pomeranian (dog)"],
 chihuahua=["Chihuahua (dog)", "Chihuahuas (dogs)"], dachshund=["Dachshunds", "Dachshund"],
 frenchie=["French Bulldogs", "French Bulldog"], pug=["Pugs", "Pug"], bichon=["Bichon Frisé"],
 schnauzer=["Miniature Schnauzers", "Miniature Schnauzer"], border=["Border Collies", "Border Collie"],
 gsd=["German Shepherds", "German Shepherd Dog"], beagle=["Beagles", "Beagle"],
 dalmatian=["Dalmatians (dog)", "Dalmatian (dog)"], basenji=["Basenjis", "Basenji"])
SEARCH = dict(taiwan="Taiwan Dog", mutt="mixed-breed dog", shiba="Shiba Inu", akita="Akita Inu", golden="Golden Retriever",
 lab="Labrador Retriever", corgi="Pembroke Welsh Corgi", husky="Siberian Husky", poodle="Toy Poodle", pom="Pomeranian dog",
 chihuahua="Chihuahua dog", dachshund="Dachshund", frenchie="French Bulldog", pug="Pug dog", bichon="Bichon Frise",
 schnauzer="Miniature Schnauzer", border="Border Collie", gsd="German Shepherd dog", beagle="Beagle dog",
 dalmatian="Dalmatian dog", basenji="Basenji")
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
cur = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}

def api(params):
    args = ["curl", "-s", "-A", UA, "-G", "https://commons.wikimedia.org/w/api.php"]
    for k, v in params.items(): args += ["--data-urlencode", f"{k}={v}"]
    for t in range(5):
        r = subprocess.run(args, capture_output=True, text=True).stdout
        try: return json.loads(r)
        except Exception: time.sleep(6 + 4*t)
    return {}

COMMON = dict(action="query", prop="imageinfo", iiprop="url|extmetadata|size", iiurlwidth="1000", format="json")
res = {}
for key in CATS:
    seen = {cur.get(key, "").replace(" ", "_")}
    picks = []
    def take(d):
        for p in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
            if "imageinfo" not in p: continue
            ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
            g = lambda k: re.sub("<[^>]+>", "", html.unescape(m.get(k, {}).get("value", ""))).strip()
            fn = p["title"].replace(" ", "_")
            if fn in seen or BAD.search(fn): continue
            if not fn.lower().endswith((".jpg", ".jpeg")): continue
            if ii["width"] < 800 or ii["height"] < 600: continue
            lic = g("LicenseShortName")
            if not OK.match(lic): continue
            seen.add(fn)
            picks.append(dict(file=p["title"], thumb=ii.get("thumburl", ii["url"]), w=ii["width"], h=ii["height"],
                              author=(g("Artist") or "Unknown")[:60], lic=lic,
                              licurl=m.get("LicenseUrl", {}).get("value", ""), page=ii["descriptionurl"]))
    for cat in CATS[key]:
        take(api(dict(COMMON, generator="categorymembers", gcmtitle="Category:" + cat, gcmtype="file", gcmlimit="60")))
        time.sleep(1.5)
        if len(picks) >= 16: break
    if len(picks) < 16:
        take(api(dict(COMMON, generator="search", gsrsearch=SEARCH[key] + " filetype:bitmap", gsrnamespace="6", gsrlimit="40")))
        time.sleep(1.5)
    res[key] = picks[:16]
    print(key, len(res[key]), flush=True)
json.dump(res, open(os.path.join(out, "cands.json"), "w"), ensure_ascii=False, indent=1)
