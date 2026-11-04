# -*- coding: utf-8 -*-
"""Единая база данных железа для калькулятора (Excel + сайт)."""
import json
import os
import urllib.parse

AVITO_CITY = "sankt-peterburg"
HERE = os.path.dirname(os.path.abspath(__file__))

# запросы, где Авито смешивает комплекты разной ёмкости — доверять нельзя
AVITO_BLOCK = {
    "2×48 ГБ DDR5-6000": "неоднозначный запрос: в заголовках разная ёмкость комплектов",
    "2×32 ГБ DDR5-6000": "неоднозначный запрос: в заголовках разная ёмкость комплектов",
}

# реальные цены, собранные avito_harvest.js (Opera + CDP)
_AVITO = {}
_prices_path = os.path.join(HERE, "avito_prices.json")
if os.path.exists(_prices_path):
    try:
        with open(_prices_path, encoding="utf-8") as f:
            for _k, _v in json.load(f).items():
                if isinstance(_v, dict) and _v.get("median"):
                    _AVITO[_k] = _v
    except Exception:
        _AVITO = {}


def avito_stats(name):
    """Данные Авито, если им можно доверять (иначе None).

    Отсекаем: меньше 8 живых объявлений и медиану, которая расходится
    с прежней оценкой сильнее допустимого (Авито часто ищет «похожее»
    и подмешивает целые серверы и другие модели).
    """
    if name in AVITO_BLOCK:
        return None
    v = _AVITO.get(name)
    if not v or not v.get("median"):
        return None
    n = v.get("ads_clean") or 0
    if n < 8:
        return None
    est = v.get("estimate") or 0
    if est:
        lo, hi = (0.4, 2.5) if v.get("kind") == "gpu" else (0.2, 3.5)
        r = float(v["median"]) / est
        if r < lo or r > hi:
            return None
    return v


def avito_reject_reason(name):
    """Почему данные Авито не использованы (для листа «Авито»)."""
    if name in AVITO_BLOCK:
        return AVITO_BLOCK[name]
    v = _AVITO.get(name)
    if not v or not v.get("median"):
        return "нет данных"
    n = v.get("ads_clean") or 0
    if n < 8:
        return "мало объявлений (%d)" % n
    est = v.get("estimate") or 0
    if est:
        r = float(v["median"]) / est
        lo, hi = (0.4, 2.5) if v.get("kind") == "gpu" else (0.2, 3.5)
        if r < lo or r > hi:
            return "выброс (%.2f× от оценки)" % r
    return ""


def avito_price(name, estimate):
    """Медиана реальных объявлений Авито, иначе — прежняя оценка."""
    v = avito_stats(name)
    return v["median"] if v else estimate


def avito_note(name):
    v = avito_stats(name)
    if not v:
        return ""
    return "Авито: %d объявл., медиана %s ₽ (%s–%s)" % (
        v.get("ads_clean") or 0, "{:,}".format(v["median"]).replace(",", " "),
        "{:,}".format(v["min"]).replace(",", " ") if v.get("min") else "?",
        "{:,}".format(v["max"]).replace(",", " ") if v.get("max") else "?")


def avito_query(name):
    """Поисковый запрос по конкретной модели (без города)."""
    return (name.replace(" (мод)", "").replace(" ГБ", "GB")
            .replace("×", "x").replace("ё", "е").strip())


def avito_url(name):
    """Ссылка на поиск Авито (СПб) по конкретной модели."""
    return "https://www.avito.ru/%s?q=%s" % (AVITO_CITY, urllib.parse.quote(avito_query(name)))


# архитектура GPU: нужна для Basalt (только Blackwell, sm_120)
GPU_ARCH = {
    "RTX 2080 Ti 22 ГБ (мод)": "Turing", "RTX 3060 12 ГБ": "Ampere", "RTX 3070 8 ГБ": "Ampere",
    "RTX 3080 10 ГБ": "Ampere", "RTX 3080 Ti 12 ГБ": "Ampere", "RTX 3090 24 ГБ": "Ampere",
    "RTX 3090 Ti 24 ГБ": "Ampere", "RTX 4060 Ti 16 ГБ": "Ada", "RTX 4070 12 ГБ": "Ada",
    "RTX 4070 Ti Super 16 ГБ": "Ada", "RTX 4080 Super 16 ГБ": "Ada", "RTX 4090 24 ГБ": "Ada",
    "RTX 5070 Ti 16 ГБ": "Blackwell", "RTX 5080 16 ГБ": "Blackwell", "RTX 5090 32 ГБ": "Blackwell",
    "RTX A4000 16 ГБ": "Ampere", "RTX A4500 20 ГБ": "Ampere", "RTX A5000 24 ГБ": "Ampere",
    "RTX A6000 48 ГБ": "Ampere", "RTX 6000 Ada 48 ГБ": "Ada", "RTX 5880 Ada 45 ГБ": "Ada",
    "RTX PRO 6000 Blackwell 96 ГБ": "Blackwell", "Radeon AI PRO R9700 32 ГБ": "RDNA4",
    "Radeon RX 7900 XTX 24 ГБ": "RDNA3", "Radeon RX 7900 XT 20 ГБ": "RDNA3",
    "Radeon RX 9070 XT 16 ГБ": "RDNA4", "Arc A770 16 ГБ": "Alchemist", "Arc B580 12 ГБ": "Battlemage",
    "Tesla V100 32 ГБ": "Volta", "Tesla P100 16 ГБ": "Pascal", "Tesla P40 24 ГБ": "Pascal",
    "Tesla T4 16 ГБ": "Turing",
}


def gpu_arch(name):
    return GPU_ARCH.get(name, "?")


# имя, VRAM, полоса ГБ/с, TDP, длина мм, слотов, compute, цена магазин, цена Авито, статус, вендор
GPU_ROWS = [
    ("RTX 2080 Ti 22 ГБ (мод)", 22, 616, 260, 267, 2, 0.72, 0, 55000, "Авито 45–65 тыс (ориентир); карта модифицированная", "NVIDIA"),
    ("RTX 3060 12 ГБ", 12, 360, 170, 242, 2, 0.45, 0, 24000, "Авито 20–28 тыс (ориентир)", "NVIDIA"),
    ("RTX 3070 8 ГБ", 8, 448, 220, 242, 2, 0.70, 0, 30000, "Авито 28–35 тыс (ориентир)", "NVIDIA"),
    ("RTX 3080 10 ГБ", 10, 760, 320, 285, 2, 0.95, 0, 40000, "Авито 35–45 тыс (ориентир)", "NVIDIA"),
    ("RTX 3080 Ti 12 ГБ", 12, 912, 350, 300, 2, 1.05, 0, 50000, "Авито 45–55 тыс (ориентир)", "NVIDIA"),
    ("RTX 3090 24 ГБ", 24, 936, 350, 320, 2, 1.00, 146793, 70000, "g-race 146 793 ₽ (нал.); Авито 55–90 тыс", "NVIDIA"),
    ("RTX 3090 Ti 24 ГБ", 24, 1008, 450, 320, 3, 1.15, 0, 90000, "Авито 80–100 тыс (ориентир)", "NVIDIA"),
    ("RTX 4060 Ti 16 ГБ", 16, 288, 165, 245, 2, 0.55, 0, 45000, "Авито 40–50 тыс (ориентир)", "NVIDIA"),
    ("RTX 4070 12 ГБ", 12, 504, 200, 244, 2, 0.95, 0, 65000, "Авито 60–70 тыс (ориентир)", "NVIDIA"),
    ("RTX 4070 Ti Super 16 ГБ", 16, 672, 285, 305, 3, 1.20, 0, 80000, "Авито 75–85 тыс (ориентир)", "NVIDIA"),
    ("RTX 4080 Super 16 ГБ", 16, 736, 320, 310, 3, 1.35, 0, 100000, "Авито 90–110 тыс (ориентир)", "NVIDIA"),
    ("RTX 4090 24 ГБ", 24, 1008, 450, 336, 3, 1.60, 403630, 185000, "g-race 403 630 ₽; Авито 150–220 тыс", "NVIDIA"),
    ("RTX 5070 Ti 16 ГБ", 16, 896, 300, 304, 3, 1.45, 0, 110000, "Авито 100–120 тыс (ориентир)", "NVIDIA"),
    ("RTX 5080 16 ГБ", 16, 960, 360, 304, 3, 1.65, 0, 140000, "Авито 130–150 тыс (ориентир)", "NVIDIA"),
    ("RTX 5090 32 ГБ", 32, 1792, 575, 330, 3, 2.20, 935000, 780000, "RoyalPC СПб 935 000 ₽; Авито 700–850 тыс", "NVIDIA"),
    ("RTX A4000 16 ГБ", 16, 448, 140, 241, 1, 0.85, 0, 90000, "Авито 80–100 тыс (ориентир)", "NVIDIA"),
    ("RTX A4500 20 ГБ", 20, 640, 200, 267, 2, 1.10, 0, 120000, "Авито 110–130 тыс (ориентир)", "NVIDIA"),
    ("RTX A5000 24 ГБ", 24, 768, 230, 267, 2, 1.30, 0, 165000, "Авито 150–180 тыс (ориентир)", "NVIDIA"),
    ("RTX A6000 48 ГБ", 48, 768, 300, 267, 2, 1.55, 558408, 400000, "g-race 558 408 ₽ (б/у); Авито 350–450 тыс", "NVIDIA"),
    ("RTX 6000 Ada 48 ГБ", 48, 960, 300, 267, 2, 1.90, 0, 600000, "Авито 550–650 тыс (ориентир)", "NVIDIA"),
    ("RTX 5880 Ada 45 ГБ", 45, 960, 285, 304, 2, 1.85, 0, 450000, "Авито 400–500 тыс (ориентир)", "NVIDIA"),
    ("RTX PRO 6000 Blackwell 96 ГБ", 96, 1792, 600, 304, 2, 3.00, 2575000, 0, "gpumall от 2 575 000 ₽", "NVIDIA"),
    ("Radeon AI PRO R9700 32 ГБ", 32, 640, 300, 267, 2, 1.25, 313480, 0, "PriceTool от 313 480 ₽; в СПб polus.ru", "AMD"),
    ("Radeon RX 7900 XTX 24 ГБ", 24, 960, 355, 320, 3, 1.35, 0, 90000, "Авито 85–95 тыс (ориентир)", "AMD"),
    ("Radeon RX 7900 XT 20 ГБ", 20, 800, 315, 300, 3, 1.15, 0, 70000, "Авито 65–75 тыс (ориентир)", "AMD"),
    ("Radeon RX 9070 XT 16 ГБ", 16, 645, 304, 305, 3, 1.30, 0, 85000, "Авито 80–90 тыс (ориентир)", "AMD"),
    ("Arc A770 16 ГБ", 16, 560, 225, 280, 2, 0.50, 0, 30000, "Авито 28–35 тыс (ориентир)", "Intel"),
    ("Arc B580 12 ГБ", 12, 456, 190, 272, 2, 0.55, 0, 35000, "Авито 32–38 тыс (ориентир)", "Intel"),
    ("Tesla V100 32 ГБ", 32, 900, 250, 267, 2, 0.60, 64593, 48000, "g-race 64 593 ₽; Авито 40–55 тыс", "NVIDIA"),
    ("Tesla P100 16 ГБ", 16, 732, 250, 267, 2, 0.40, 0, 25000, "Авито 20–30 тыс (ориентир)", "NVIDIA"),
    ("Tesla P40 24 ГБ", 24, 346, 250, 267, 2, 0.30, 0, 30000, "Авито 25–35 тыс (ориентир)", "NVIDIA"),
    ("Tesla T4 16 ГБ", 16, 320, 70, 168, 1, 0.25, 0, 40000, "Авито 35–45 тыс (ориентир)", "NVIDIA"),
]

PLATFORMS = [
    {
        "name": "SP3",
        "title": "SP3 — EPYC 7002/7003: 8 каналов DDR4, 128 линий PCIe 4.0, до 7 GPU",
        "cpus": [
            ("AMD EPYC 7402", 24, 8, 139, 180, 30000, "sale-server, б/у"),
            ("AMD EPYC 7443", 24, 8, 139, 200, 98937, "srv-trade"),
            ("AMD EPYC 7502P", 32, 8, 139, 180, 46238, "srv-trade"),
            ("AMD EPYC 7543", 32, 8, 139, 225, 86853, "srv-trade"),
            ("AMD EPYC 7702P", 64, 8, 139, 200, 45000, "Авито (ориентир)"),
        ],
        "mbs": [
            ("Supermicro H12SSL-I-B", "DDR4", 8, 7, 108100, "chipdip; 5×x16 + 2×x8"),
            ("Supermicro H12SSL-NT", "DDR4", 8, 7, 135188, "srv-trade; 2×10GbE"),
            ("Gigabyte MZ31-AR0", "DDR4", 8, 7, 51273, "srv-trade"),
        ],
        "rams": [
            ("8×32 ГБ DDR4-3200 ECC RDIMM", "DDR4", 8, 32, 184616, "srv-trade, 23 077 ₽/шт"),
            ("8×32 ГБ DDR4-2666 ECC RDIMM", "DDR4", 8, 32, 255200, "sale-server, 31 900 ₽/шт"),
            ("8×16 ГБ DDR4-3200 ECC RDIMM", "DDR4", 8, 16, 95000, "Авито (ориентир)"),
        ],
    },
    {
        "name": "AM5",
        "title": "AM5 — Ryzen 7000/9000: 2 канала DDR5, 24 линии PCIe 5.0, максимум 2 GPU",
        "cpus": [
            ("AMD Ryzen 9 9950X3D", 16, 2, 90, 170, 78860, "chipdip"),
            ("AMD Ryzen 9 9950X", 16, 2, 90, 170, 65070, "chipdip"),
            ("AMD Ryzen 9 7950X", 16, 2, 88, 170, 42000, "Авито (ориентир)"),
            ("AMD Ryzen 9 7900X", 12, 2, 88, 170, 32000, "Авито (ориентир)"),
        ],
        "mbs": [
            ("ASUS ProArt X870E-Creator", "DDR5", 4, 3, 65390, "chipdip; 2 GPU в x8/x8"),
            ("Gigabyte X870E Aorus Master", "DDR5", 4, 2, 62140, "chipdip"),
            ("ASUS TUF B650-PLUS", "DDR5", 4, 2, 20000, "Авито (ориентир)"),
        ],
        "rams": [
            ("2×48 ГБ DDR5-6000", "DDR5", 2, 48, 255100, "chipdip, комплект"),
            ("2×32 ГБ DDR5-6000", "DDR5", 2, 32, 156900, "chipdip, комплект"),
        ],
    },
    {
        "name": "LGA1851",
        "title": "LGA1851 — Intel Core Ultra 200S (Arrow Lake): 2 канала DDR5, 24 линии PCIe 5.0",
        "cpus": [
            ("Intel Core Ultra 9 285K", 24, 2, 90, 250, 70000, "Авито (ориентир)"),
            ("Intel Core Ultra 7 265K", 20, 2, 90, 250, 45000, "Авито (ориентир)"),
            ("Intel Core Ultra 5 245K", 14, 2, 90, 160, 30000, "Авито (ориентир)"),
        ],
        "mbs": [
            ("ASUS ProArt Z890-Creator", "DDR5", 4, 3, 60000, "Авито (ориентир)"),
            ("Gigabyte Z890 Aorus Master", "DDR5", 4, 3, 55000, "Авито (ориентир)"),
            ("ASUS TUF Z890-PLUS", "DDR5", 4, 3, 30000, "Авито (ориентир)"),
        ],
        "rams": [
            ("2×48 ГБ DDR5-6000", "DDR5", 2, 48, 255100, "chipdip, комплект"),
            ("2×32 ГБ DDR5-6000", "DDR5", 2, 32, 156900, "chipdip, комплект"),
        ],
    },
    {
        "name": "LGA1700",
        "title": "LGA1700 — Intel 12/13/14-е поколение: 2 канала DDR4/DDR5, 20 линий PCIe",
        "cpus": [
            ("Intel Core i9-14900K", 24, 2, 85, 253, 45000, "Авито (ориентир)"),
            ("Intel Core i7-14700K", 20, 2, 85, 253, 32000, "Авито (ориентир)"),
            ("Intel Core i5-14600K", 14, 2, 80, 181, 22000, "Авито (ориентир)"),
        ],
        "mbs": [
            ("ASUS ProArt Z790-Creator", "DDR5", 4, 3, 40000, "Авито (ориентир)"),
            ("MSI MAG Z790 Tomahawk DDR4", "DDR4", 4, 3, 25000, "Авито (ориентир)"),
        ],
        "rams": [
            ("2×48 ГБ DDR5-6000", "DDR5", 2, 48, 255100, "chipdip, комплект"),
            ("4×32 ГБ DDR4-3200", "DDR4", 4, 32, 140000, "Авито (ориентир)"),
        ],
    },
    {
        "name": "LGA4677",
        "title": "LGA4677 — Xeon Sapphire/Emerald Rapids: 8 каналов DDR5, до 240 ГБ/с",
        "cpus": [
            ("Intel Xeon Gold 6430", 32, 8, 240, 270, 180000, "Авито (ориентир)"),
            ("Intel Xeon Gold 5418Y", 24, 8, 240, 185, 140000, "Авито (ориентир)"),
            ("Intel Xeon Silver 4510", 12, 8, 240, 150, 90000, "Авито (ориентир)"),
        ],
        "mbs": [
            ("Supermicro X13SEI-F", "DDR5", 8, 6, 120000, "Авито (ориентир)"),
            ("Supermicro X13SRA-TF", "DDR5", 8, 6, 140000, "Авито (ориентир)"),
        ],
        "rams": [
            ("8×32 ГБ DDR5-4800 ECC RDIMM", "DDR5", 8, 32, 420000, "Авито (ориентир)"),
            ("8×16 ГБ DDR5-4800 ECC RDIMM", "DDR5", 8, 16, 220000, "Авито (ориентир)"),
        ],
    },
    {
        "name": "LGA4189",
        "title": "LGA4189 — Xeon Ice Lake: 8 каналов DDR4, до 150 ГБ/с",
        "cpus": [
            ("Intel Xeon Gold 6338", 32, 8, 150, 205, 70000, "Авито (ориентир)"),
            ("Intel Xeon Silver 4314", 16, 8, 150, 135, 35000, "Авито (ориентир)"),
        ],
        "mbs": [
            ("Supermicro X12SPI-TF", "DDR4", 8, 6, 80000, "Авито (ориентир)"),
            ("Supermicro X12SPL-F", "DDR4", 8, 4, 60000, "Авито (ориентир)"),
        ],
        "rams": [
            ("8×32 ГБ DDR4-3200 ECC RDIMM", "DDR4", 8, 32, 184616, "srv-trade"),
            ("8×16 ГБ DDR4-3200 ECC RDIMM", "DDR4", 8, 16, 95000, "Авито (ориентир)"),
        ],
    },
    {
        "name": "LGA3647",
        "title": "LGA3647 — Xeon Scalable 1/2-го поколения: 6 каналов DDR4 на сокет, AVX-512",
        "cpus": [
            ("Intel Xeon Gold 6252", 24, 6, 110, 150, 26900, "sale-server"),
            ("Intel Xeon Platinum 8163", 24, 6, 110, 165, 20000, "Авито (ориентир)"),
            ("Intel Xeon Gold 6230", 20, 6, 110, 125, 12500, "sale-server"),
        ],
        "mbs": [
            ("Supermicro X11SPI-TF", "DDR4", 6, 4, 45000, "Авито (ориентир), 1 сокет"),
            ("Supermicro X11DPi-NT", "DDR4", 12, 6, 55000, "Авито (ориентир), 2 сокета"),
        ],
        "rams": [
            ("6×32 ГБ DDR4-2666 ECC RDIMM", "DDR4", 6, 32, 150000, "Авито (ориентир)"),
            ("6×16 ГБ DDR4-2666 ECC RDIMM", "DDR4", 6, 16, 78000, "Авито (ориентир)"),
            ("12×32 ГБ DDR4-2666 ECC RDIMM", "DDR4", 12, 32, 300000, "Авито (ориентир), 2 сокета"),
        ],
    },
    {
        "name": "TR5",
        "title": "sTR5 — Threadripper 7000: 4 канала DDR5, 48–80 линий PCIe 5.0",
        "cpus": [
            ("AMD Threadripper 7960X", 24, 4, 170, 350, 150000, "Авито (ориентир)"),
            ("AMD Threadripper 7970X", 32, 4, 170, 350, 220000, "Авито (ориентир)"),
        ],
        "mbs": [
            ("ASUS Pro WS TRX50-SAGE", "DDR5", 4, 4, 110000, "Авито (ориентир)"),
            ("Gigabyte TRX50 AERO D", "DDR5", 4, 4, 95000, "Авито (ориентир)"),
        ],
        "rams": [
            ("4×32 ГБ DDR5-5600 ECC RDIMM", "DDR5", 4, 32, 180000, "Авито (ориентир)"),
            ("4×64 ГБ DDR5-5600 ECC RDIMM", "DDR5", 4, 64, 360000, "Авито (ориентир)"),
        ],
    },
    {
        "name": "AM4",
        "title": "AM4 — Ryzen 5000: 2 канала DDR4, 20 линий PCIe 4.0, самый дешёвый вход",
        "cpus": [
            ("AMD Ryzen 9 5950X", 16, 2, 51, 105, 22000, "Авито (ориентир)"),
            ("AMD Ryzen 9 5900X", 12, 2, 51, 105, 15000, "Авито (ориентир)"),
        ],
        "mbs": [
            ("Gigabyte B550 Aorus Pro", "DDR4", 4, 3, 12000, "Авито (ориентир)"),
            ("Gigabyte X570 Aorus Elite", "DDR4", 4, 3, 15000, "Авито (ориентир)"),
        ],
        "rams": [
            ("2×32 ГБ DDR4-3200", "DDR4", 2, 32, 70000, "Авито (ориентир)"),
            ("2×16 ГБ DDR4-3200", "DDR4", 2, 16, 35000, "Авито (ориентир)"),
        ],
    },
]

PSUS = [
    ("Seasonic PRIME TX-1600 (ATX 3.1)", 1600, 57550, "chipdip"),
    ("БП 2000 Вт (серверный, в корпусе YCC)", 2000, 52407, "NIX, корпус 4U с БП 2000 Вт"),
    ("БП 1200 Вт (SuperFlower)", 1200, 25000, "Авито (ориентир)"),
    ("БП 1000 Вт (Corsair RM1000x)", 1000, 18000, "Авито (ориентир)"),
    ("БП 850 Вт (be quiet! Straight Power)", 850, 12000, "Авито (ориентир)"),
]

CASES = [
    ("NegoRack NR-M48 (4U, 650 мм)", 350, 8, 29623, "srv-trade"),
    ("Корпус 4U PROCASE (430 мм)", 300, 4, 22238, "srv-trade"),
    ("Открытый стенд", 400, 6, 8000, "Авито (ориентир)"),
    ("Fractal Define 7 XL", 460, 3, 33000, "снят с продажи, ориентир"),
    ("Lian Li PC-O11 Dynamic", 420, 2, 18000, "Авито (ориентир)"),
    ("Корпус ATX с 3 слотами (ориентир)", 340, 3, 6000, "Авито (ориентир)"),
]

# имя, объём ГБ, чтение ГБ/с, цена, источник
SSDS = [
    ("NVMe 4 ТБ Gen5 Crucial T705", 4000, 13.6, 85370, "chipdip"),
    ("NVMe 4 ТБ Gen4 WD Black SN850X", 4000, 7.3, 88360, "chipdip"),
    ("NVMe 4 ТБ Gen4 Kingston KC3000", 4000, 7.0, 89520, "chipdip"),
    ("NVMe 2 ТБ Gen4 WD Black SN850X", 2000, 7.3, 43500, "Авито (ориентир)"),
    ("NVMe 8 ТБ Gen4 WD Black SN850X", 8000, 7.3, 168000, "Авито (ориентир)"),
]
SSD_DEFAULT = "NVMe 4 ТБ Gen4 WD Black SN850X"

# габариты корпусов: ширина × высота × глубина, мм; вес, кг (ориентир)
CASE_DIMS = {
    "NegoRack NR-M48 (4U, 650 мм)": (430, 176, 650, 14.0),
    "Корпус 4U PROCASE (430 мм)": (430, 176, 430, 9.0),
    "Открытый стенд": (400, 350, 420, 4.0),
    "Fractal Define 7 XL": (240, 604, 566, 16.0),
    "Lian Li PC-O11 Dynamic": (285, 465, 459, 13.0),
    "Корпус ATX с 3 слотами (ориентир)": (210, 470, 420, 8.0),
}

# имя, движок, размер, активных, байт/токен, dense, anchor VRAM, anchor BW VRAM, anchor BW RAM,
# anchor compute, anchor decode, anchor prefill, степень, источник
MODELS = [
    ("GLM-5.3-Flash Maya-L", "Maya", 156.3, 18, 8.8, 6.9, 48, 1872, 139, 2.0, 30.2, 801, 0.30, "2×3090 + EPYC 7452, Maya #165"),
    ("GLM-5.3-Flash Maya-M", "Maya", 116.0, 18, 6.5, 6.9, 24, 936, 139, 1.0, 27.0, 1069, 0.30, "1×3090 + EPYC 7702P, Maya #157"),
    ("Qwen3.8-Flash UD-Q4_K_XL", "Strata", 111.3, 6, 3.77, 4.8, 32, 644, 106, 1.25, 63.5, 1110, 0.12, "1×R9700 + EPYC 7452, Strata QUANTS.md"),
    ("Qwen3.8-Flash UD-IQ4_XS", "Strata", 93.7, 6, 3.12, 4.8, 44, 1232, 150, 1.44, 55.0, 869, 0.12, "2×2080 Ti 22 ГБ, Strata PR #2665"),
    ("DeepSeek-V4.1-Flash Maya-S", "Maya-ds4", 340.0, 40, 3.0, 20.0, 32, 1792, 90, 2.2, 24.9, 1842, 0.30, "1×RTX 5090 + 128 ГБ, dev.to 10.2026"),
    ("Qwen3.8-Flash Basalt NVFP4-DQ6_K", "Basalt", 131.7, 6, 4.39, 4.8, 96, 5376, 139, 6.6, 406, 7957, 1.0, "3× Blackwell: 406 ток/с и pp 7957 (замер); экстраполяция линейна по полосе"),
    ("Qwen3.8-Flash Basalt IQ3_S", "Basalt", 87.6, 6, 2.92, 4.8, 96, 5376, 139, 6.6, 540, 8500, 1.0, "оценка от замера NVFP4: меньше байт на токен"),
]
