# -*- coding: utf-8 -*-
"""Карточка сборки в PNG: состав, цены, скорость, габариты и питание."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import db  # noqa: E402
import model  # noqa: E402

W, H = 1200, 1010
BG = (15, 17, 21)
PANEL = (23, 26, 33)
LINE = (38, 43, 54)
TEXT = (230, 232, 238)
MUTED = (139, 147, 167)
ACCENT = (74, 222, 128)
WARN = (248, 113, 113)

F = {
    "h1": ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 46),
    "h2": ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20),
    "big": ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 34),
    "body": ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 19),
    "small": ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15),
    "mono": ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 19),
    "monob": ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 22),
}


def money(v):
    return "{:,}".format(int(round(v))).replace(",", " ") + " ₽"


def money_s(v):
    return "{:,}".format(int(round(v))).replace(",", " ")


def make_card(b, out_path):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # рамка-подложка
    d.rounded_rectangle([28, 24, W - 28, H - 24], 22, fill=PANEL, outline=LINE, width=2)

    # шапка
    d.text((60, 50), "AI BUILD CARD", font=F["small"], fill=ACCENT)
    title = "%d× %s · %s" % (b["count"], b["gpu"]["name"], b["cpu"]["name"].split(" · ")[0])
    size = 46
    font_title = F["h1"]
    while d.textlength(title, font=font_title) > 1060 and size > 24:
        size -= 2
        font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", size)
    d.text((60, 74), title, font=font_title, fill=TEXT)
    d.text((60, 136), "%s · %s ГБ RAM · %d ГБ VRAM · контекст %dK · %d Вт" % (
        b["platform"], b["ram"]["mods"] * b["ram"]["gb"], int(b["vram"]), b["ctx"] // 1024, b["power"]),
        font=F["body"], fill=MUTED)
    d.text((W - 60, 56), "04.11.2026", font=F["small"], fill=MUTED, anchor="ra")
    d.text((W - 60, 78), "цены: Авито СПб", font=F["small"], fill=MUTED, anchor="ra")

    # ---- состав и цены (слева)
    x0, y0 = 60, 196
    d.text((x0, y0), "СОСТАВ И ЦЕНЫ", font=F["h2"], fill=ACCENT)
    rows = [
        ("Процессор", b["cpu"]["name"], b["cpu"]["price"]),
        ("Плата", b["mb"]["name"], b["mb"]["price"]),
        ("Память", b["ram"]["name"], b["ram"]["price"]),
        ("Видеокарты", "%s × %d" % (b["gpu"]["name"], b["count"]), b["gpu"]["price"] * b["count"]),
        ("Питание", b["psu"]["name"], b["psu"]["price"]),
        ("Корпус", b["case"]["name"], b["case"]["price"]),
        ("Накопитель", b["ssd"]["name"], b["ssd"]["price"]),
    ]
    y = y0 + 38
    for label, name, price in rows:
        d.text((x0, y), label, font=F["small"], fill=MUTED)
        d.text((x0 + 120, y), name[:44], font=F["body"], fill=TEXT)
        d.text((640, y + 1), money(price), font=F["mono"], fill=TEXT, anchor="ra")
        y += 30
        d.line([x0, y + 6, 640, y + 6], fill=LINE, width=1)
        y += 14

    d.text((x0, y + 6), "ИТОГО", font=F["h2"], fill=TEXT)
    d.text((640, y), money(b["price"]), font=F["big"], fill=ACCENT, anchor="ra")

    # ---- скорость (справа)
    rx = 700
    d.text((rx, y0), "СКОРОСТЬ (ток/с)", font=F["h2"], fill=ACCENT)
    d.text((rx, y0 + 34), "декод", font=F["small"], fill=MUTED)
    d.text((rx + 240, y0 + 34), "префилл", font=F["small"], fill=MUTED)
    yy = y0 + 62
    for m in b["models"]:
        name = m["name"].replace("GLM-5.3-Flash ", "GLM ").replace("Qwen3.8-Flash ", "Qwen ").replace("DeepSeek-V4.1-Flash ", "DS ")
        d.text((rx, yy), name[:30], font=F["body"], fill=TEXT)
        if m["decode"] is None:
            d.text((rx + 240, yy), "нет NVIDIA", font=F["small"], fill=WARN)
        else:
            d.text((rx + 240, yy), "%.1f" % m["decode"], font=F["mono"], fill=TEXT)
            d.text((rx + 360, yy), "%d" % round(m["prefill"]), font=F["mono"], fill=MUTED)
        yy += 32
    d.text((rx, yy + 4), "оценка ±25 % декод, ±35 % префилл", font=F["small"], fill=MUTED)

    # ---- габариты и питание (низ)
    by = 640
    d.line([60, by - 22, W - 60, by - 22], fill=LINE, width=2)
    d.text((60, by), "ГАБАРИТЫ СБОРКИ", font=F["h2"], fill=ACCENT)
    dims = b["case"]["dims"]
    if dims:
        w, h, dp, kg = dims
        cards = [
            ("Корпус Ш×В×Г", "%d×%d×%d мм" % (w, h, dp)),
            ("Объём / вес", "%.1f л · %.0f кг" % (b["case"]["volume"], kg)),
            ("Длина карты", "%d мм" % b["gpu"]["len"]),
            ("Слотов на карту", "%d" % b["gpu"]["slots"]),
        ]
    else:
        cards = [("Длина карты", "%d мм" % b["gpu"]["len"])]
    cx = 60
    for label, val in cards:
        d.rounded_rectangle([cx, by + 40, cx + 258, by + 128], 12, fill=BG, outline=LINE, width=1)
        d.text((cx + 16, by + 54), label, font=F["small"], fill=MUTED)
        d.text((cx + 16, by + 82), val, font=F["monob"], fill=TEXT)
        cx += 270

    # питание
    py = by + 148
    d.text((60, py), "ПИТАНИЕ", font=F["h2"], fill=ACCENT)
    d.text((60, py + 34), "Потребление %d Вт · рекомендуемый БП %d Вт · установлен %d Вт" % (
        b["power"], b["psu_need"], b["psu"]["w"]), font=F["body"], fill=TEXT)
    warn = []
    if b["psu"]["w"] < b["psu_need"]:
        warn.append("БП слабее расчётного (%d < %d Вт)" % (b["psu"]["w"], b["psu_need"]))
    if b["case"]["slots"] < b["count"]:
        warn.append("в корпусе %d слота под GPU, а карт %d" % (b["case"]["slots"], b["count"]))
    if warn:
        d.text((60, py + 64), "! " + " · ".join(warn), font=F["body"], fill=WARN)
    d.text((60, py + (94 if warn else 64)), "VRAM %d ГБ · полоса %s ГБ/с · RAM %s ГБ/с · compute %.2f" % (
        int(b["vram"]), "{:,}".format(int(b["bw_vram"])).replace(",", " "), b["bw_ram"], b["compute"]),
        font=F["body"], fill=MUTED)

    # подвал
    d.line([60, H - 78, W - 60, H - 78], fill=LINE, width=1)
    d.text((60, H - 60), "ervsed.github.io/ai-hardware-calculator", font=F["small"], fill=ACCENT)
    d.text((W - 60, H - 60), "цены — медианы объявлений Авито (СПб), 04.11.2026", font=F["small"], fill=MUTED, anchor="ra")

    img.save(out_path, "PNG")
    return out_path


if __name__ == "__main__":
    opts = dict(a.split("=", 1) for a in sys.argv[1:] if "=" in a)
    b = model.build(
        platform=opts.get("platform", "SP3"),
        cpu=opts.get("cpu", "AMD EPYC 7402"),
        mb=opts.get("mb", "Supermicro H12SSL-I-B"),
        ram=opts.get("ram", "8×32 ГБ DDR4-3200 ECC RDIMM"),
        gpu=opts.get("gpu", "RTX 3090 24 ГБ"),
        count=int(opts.get("count", 2)),
        psu=opts.get("psu", "Seasonic PRIME TX-1600 (ATX 3.1)"),
        case=opts.get("case", "NegoRack NR-M48 (4U, 650 мм)"),
    )
    out = opts.get("out", os.path.join(HERE, "card.png"))
    make_card(b, out)
    print("saved:", out, "| цена:", b["price"], "| габариты:", b["case"]["dims"])
