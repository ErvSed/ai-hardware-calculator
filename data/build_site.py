# -*- coding: utf-8 -*-
"""Генерирует site/data.js из db.py."""
import io
import json
import os

import db

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "site")
os.makedirs(SITE, exist_ok=True)


def gpu(g):
    av = db.avito_price(g[0], g[8])
    st = db.avito_stats(g[0]) or {}
    return {
        "name": g[0], "vram": g[1], "bw": g[2], "tdp": g[3], "len": g[4], "slots": g[5],
        "comp": g[6], "shop": g[7], "avito": av, "note": g[9], "vendor": g[10],
        "price": av if av else g[7],
        "avitoN": st.get("ads_clean") or 0,
        "avitoMin": st.get("min"), "avitoMax": st.get("max"),
        "avitoUrl": db.avito_url(g[0]),
    }


def pstat(name):
    st = db.avito_stats(name) or {}
    return st.get("ads_clean") or 0


data = {
    "gpus": [gpu(g) for g in db.GPU_ROWS],
    "platforms": [
        {
            "name": p["name"],
            "title": p["title"],
            "cpus": [
                {"name": c[0], "cores": c[1], "ch": c[2], "bw": c[3], "tdp": c[4], "price": db.avito_price(c[0], c[5]), "src": c[6], "platform": p["name"], "avitoUrl": db.avito_url(c[0]), "avitoN": pstat(c[0])}
                for c in p["cpus"]
            ],
            "mbs": [
                {"name": m[0], "ram": m[1], "ramSlots": m[2], "slots": m[3], "price": db.avito_price(m[0], m[4]), "src": m[5], "platform": p["name"], "avitoUrl": db.avito_url(m[0]), "avitoN": pstat(m[0])}
                for m in p["mbs"]
            ],
            "rams": [
                {"name": r[0], "type": r[1], "mods": r[2], "gb": r[3], "price": db.avito_price(r[0], r[4]), "src": r[5], "platform": p["name"], "avitoUrl": db.avito_url(r[0]), "avitoN": pstat(r[0])}
                for r in p["rams"]
            ],
        }
        for p in db.PLATFORMS
    ],
    "psus": [{"name": p[0], "w": p[1], "price": db.avito_price(p[0], p[2]), "src": p[3], "avitoUrl": db.avito_url(p[0]), "avitoN": pstat(p[0])} for p in db.PSUS],
    "cases": [{"name": c[0], "len": c[1], "slots": c[2], "price": db.avito_price(c[0], c[3]), "src": c[4], "avitoUrl": db.avito_url(c[0]), "avitoN": pstat(c[0])} for c in db.CASES],
    "models": [
        {
            "name": m[0], "engine": m[1], "size": m[2], "active": m[3], "bpt": m[4], "dense": m[5],
            "aVram": m[6], "aBw": m[7], "aRam": m[8], "aComp": m[9], "aDec": m[10], "aPP": m[11],
            "exp": m[12], "src": m[13],
        }
        for m in db.MODELS
    ],
}

payload = json.dumps(data, ensure_ascii=False, indent=1)
with io.open(os.path.join(SITE, "data.js"), "w", encoding="utf-8") as f:
    f.write("/* Сгенерировано build_site.py из db.py — не править вручную */\n")
    f.write("const DB = " + payload + ";\n")
    f.write("if (typeof window !== 'undefined') { window.DB = DB; }\n")
    f.write("if (typeof module !== 'undefined') { module.exports = DB; }\n")

print("data.js written:", len(payload), "bytes;",
      len(data["gpus"]), "GPU,", len(data["platforms"]), "platforms")
