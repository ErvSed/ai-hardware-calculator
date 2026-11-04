# -*- coding: utf-8 -*-
"""Готовит список поисковых запросов Авито из db.py."""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import db  # noqa: E402

items = []
for g in db.GPU_ROWS:
    items.append({"kind": "gpu", "name": g[0], "query": db.avito_query(g[0]), "estimate": g[8]})
for p in db.PLATFORMS:
    for c in p["cpus"]:
        items.append({"kind": "cpu", "name": c[0], "query": db.avito_query(c[0]), "estimate": c[5]})
    for m in p["mbs"]:
        items.append({"kind": "mb", "name": m[0], "query": db.avito_query(m[0]), "estimate": m[4]})
    for r in p["rams"]:
        items.append({"kind": "ram", "name": r[0], "query": db.avito_query(r[0]), "estimate": r[4]})
for x in db.PSUS:
    items.append({"kind": "psu", "name": x[0], "query": db.avito_query(x[0]), "estimate": x[2]})
for x in db.CASES:
    items.append({"kind": "case", "name": x[0], "query": db.avito_query(x[0]), "estimate": x[3]})

with io.open(os.path.join(HERE, "avito_queries.json"), "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=1)
print("queries:", len(items))
