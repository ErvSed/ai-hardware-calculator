# -*- coding: utf-8 -*-
"""Расчёт сборки на Python — та же модель, что в calc.js и Excel."""
import db


def gpu_by_name(name):
    for g in db.GPU_ROWS:
        if g[0] == name:
            return {"name": g[0], "vram": g[1], "bw": g[2], "tdp": g[3], "len": g[4],
                    "slots": g[5], "comp": g[6], "shop": g[7], "avito": g[8], "vendor": g[10],
                    "arch": db.gpu_arch(g[0]),
                    "price": db.avito_price(g[0], g[8]) or g[7]}
    raise KeyError(name)


def platform_by_name(name):
    for p in db.PLATFORMS:
        if p["name"] == name:
            return p
    raise KeyError(name)


def cpu_of(p, name):
    for c in p["cpus"]:
        if c[0] == name:
            return {"name": c[0], "cores": c[1], "ch": c[2], "bw": c[3], "tdp": c[4],
                    "price": db.avito_price(c[0], c[5]), "src": c[6]}
    raise KeyError(name)


def mb_of(p, name):
    for m in p["mbs"]:
        if m[0] == name:
            return {"name": m[0], "ram": m[1], "ramSlots": m[2], "slots": m[3],
                    "price": db.avito_price(m[0], m[4]), "src": m[5]}
    raise KeyError(name)


def ram_of(p, name):
    for r in p["rams"]:
        if r[0] == name:
            return {"name": r[0], "type": r[1], "mods": r[2], "gb": r[3],
                    "price": db.avito_price(r[0], r[4]), "src": r[5]}
    raise KeyError(name)


def s_share(vram, dense, size):
    return max(0.0, min(1.0, (vram - dense - 2) / (size - dense)))


def build(platform="SP3", cpu="AMD EPYC 7402", mb="Supermicro H12SSL-I-B",
          ram="8×32 ГБ DDR4-3200 ECC RDIMM", gpu="RTX 3090 24 ГБ", count=2,
          psu="Seasonic PRIME TX-1600 (ATX 3.1)", case="NegoRack NR-M48 (4U, 650 мм)"):
    p = platform_by_name(platform)
    c = cpu_of(p, cpu)
    m = mb_of(p, mb)
    r = ram_of(p, ram)
    g = gpu_by_name(gpu)
    ps = next(x for x in db.PSUS if x[0] == psu)
    cs = next(x for x in db.CASES if x[0] == case)
    ps_price = db.avito_price(ps[0], ps[2])
    cs_price = db.avito_price(cs[0], cs[3])

    vram = g["vram"] * count
    bw_vram = g["bw"] * count
    compute = g["comp"] * count
    bw_ram = c["bw"]
    price = g["price"] * count + c["price"] + m["price"] + r["price"] + ps_price + cs_price
    power = g["tdp"] * count * 1.1 + c["tdp"] * 1.3 + 100

    models = []
    for mm in db.MODELS:
        name, engine, size, active, bpt, dense, a_vram, a_bw, a_ram, a_comp, a_dec, a_pp, exp, src = mm
        s = s_share(vram, dense, size)
        d = s * bw_vram + (1 - s) * bw_ram
        da = s_share(a_vram, dense, size) * a_bw + (1 - s_share(a_vram, dense, size)) * a_ram
        dec = a_dec * (d / da) ** exp
        pp = a_pp * (compute / a_comp) ** 0.35 * (bw_ram / a_ram) ** 0.2
        blocked = ((engine.startswith("Maya") and g["vendor"] != "NVIDIA")
                   or (engine == "Basalt" and g["arch"] != "Blackwell"))
        reason = "нужен Blackwell" if engine == "Basalt" else "нет NVIDIA"
        models.append({"name": name, "engine": engine, "s": s,
                       "decode": None if blocked else dec,
                       "prefill": None if blocked else pp,
                       "reason": reason if blocked else None,
                       "lim": "всё в VRAM" if s > 0.8 else ("VRAM + RAM-ярус" if s > 0.3 else "упирается в RAM/SSD")})

    dims = db.CASE_DIMS.get(case)
    volume = round(dims[0] * dims[1] * dims[2] / 1e6, 1) if dims else None

    return {
        "platform": platform, "cpu": c, "mb": m, "ram": r, "gpu": g, "count": count,
        "psu": {"name": ps[0], "w": ps[1], "price": ps_price},
        "case": {"name": cs[0], "len": cs[1], "slots": cs[2], "price": cs_price, "dims": dims, "volume": volume},
        "vram": vram, "bw_vram": bw_vram, "compute": compute, "bw_ram": bw_ram,
        "price": price, "power": round(power), "psu_need": int(-(-power / 0.75 // 50) * 50),
        "models": models,
    }
