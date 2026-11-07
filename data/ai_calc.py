# -*- coding: utf-8 -*-
"""Калькулятор максимума LLM: 6 платформ, расширенная база железа, зависимые списки."""
import os

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.utils import get_column_letter

OUT = os.environ.get("XLSX_OUT") or r"U:\Documents\deepseek-harness\Trash\AI_Calculator_Hardware_Avito.xlsx"
MONEY = '#,##0" ₽"'
NUM1 = '#,##0.0'
NUM2 = '#,##0.00'

H_FONT = Font(bold=True, color="FFFFFF", size=11)
H_FILL = PatternFill("solid", fgColor="1B5E20")
SUB_FONT = Font(bold=True, size=12, color="1B5E20")
SUB_FILL = PatternFill("solid", fgColor="C8E6C9")
IN_FILL = PatternFill("solid", fgColor="FFF9C4")
OUT_FILL = PatternFill("solid", fgColor="E3F2FD")
NOTE_FILL = PatternFill("solid", fgColor="FFFDE7")
LINK = Font(color="0563C1", underline="single")
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="center")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

WB = Workbook()

def head(ws, row, values):
    for i, v in enumerate(values, start=1):
        c = ws.cell(row=row, column=i, value=v)
        c.font = H_FONT
        c.fill = H_FILL
        c.alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[row].height = 32

def note(ws, row, text, ncols):
    c = ws.cell(row=row, column=1, value=text)
    c.alignment = WRAP
    c.fill = NOTE_FILL
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)
    ws.row_dimensions[row].height = 44

def widths(ws, ws_widths):
    for i, w in enumerate(ws_widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

# ================================================================ данные
GPU_ROWS = [
    # имя, VRAM, полоса, TDP, длина, слотов, compute, магазин, авито, статус
    ("RTX 2080 Ti 22 ГБ (мод)", 22, 616, 260, 267, 2, 0.72, 0, 55000, "Авито 45–65 тыс (ориентир); карта модифицированная"),
    ("RTX 3060 12 ГБ", 12, 360, 170, 242, 2, 0.45, 0, 24000, "Авито 20–28 тыс (ориентир)"),
    ("RTX 3080 Ti 12 ГБ", 12, 912, 350, 300, 2, 1.05, 0, 50000, "Авито 45–55 тыс (ориентир)"),
    ("RTX 3090 24 ГБ", 24, 936, 350, 320, 2, 1.00, 146793, 70000, "g-race 146 793 ₽ (нал.); Авито 55–90 тыс"),
    ("RTX 4070 Ti Super 16 ГБ", 16, 672, 285, 305, 3, 1.20, 0, 80000, "Авито 75–85 тыс (ориентир)"),
    ("RTX 4080 Super 16 ГБ", 16, 736, 320, 310, 3, 1.35, 0, 100000, "Авито 90–110 тыс (ориентир)"),
    ("RTX 4090 24 ГБ", 24, 1008, 450, 336, 3, 1.60, 403630, 185000, "g-race 403 630 ₽; Авито 150–220 тыс"),
    ("RTX 5070 Ti 16 ГБ", 16, 896, 300, 304, 3, 1.45, 0, 110000, "Авито 100–120 тыс (ориентир)"),
    ("RTX 5080 16 ГБ", 16, 960, 360, 304, 3, 1.65, 0, 140000, "Авито 130–150 тыс (ориентир)"),
    ("RTX 5090 32 ГБ", 32, 1792, 575, 330, 3, 2.20, 935000, 780000, "RoyalPC СПб 935 000 ₽; Авито 700–850 тыс"),
    ("RTX A5000 24 ГБ", 24, 768, 230, 267, 2, 1.30, 0, 165000, "Авито 150–180 тыс (ориентир)"),
    ("RTX A6000 48 ГБ", 48, 768, 300, 267, 2, 1.55, 558408, 400000, "g-race 558 408 ₽ (б/у); Авито 350–450 тыс"),
    ("RTX 6000 Ada 48 ГБ", 48, 960, 300, 267, 2, 1.90, 0, 600000, "Авито 550–650 тыс (ориентир)"),
    ("RTX 5880 Ada 45 ГБ", 45, 960, 285, 304, 2, 1.85, 0, 450000, "Авито 400–500 тыс (ориентир)"),
    ("RTX PRO 6000 Blackwell 96 ГБ", 96, 1792, 600, 304, 2, 3.00, 2575000, 0, "gpumall от 2 575 000 ₽"),
    ("Radeon AI PRO R9700 32 ГБ", 32, 640, 300, 267, 2, 1.25, 313480, 0, "PriceTool от 313 480 ₽; в СПб polus.ru"),
    ("Tesla V100 32 ГБ", 32, 900, 250, 267, 2, 0.60, 64593, 48000, "g-race 64 593 ₽; Авито 40–55 тыс"),
    ("Tesla P100 16 ГБ", 16, 732, 250, 267, 2, 0.40, 0, 25000, "Авито 20–30 тыс (ориентир)"),
    ("Tesla P40 24 ГБ", 24, 346, 250, 267, 2, 0.30, 0, 30000, "Авито 25–35 тыс (ориентир)"),
    ("Tesla T4 16 ГБ", 16, 320, 70, 168, 1, 0.25, 0, 40000, "Авито 35–45 тыс (ориентир)"),
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
            ("12×32 ГБ DDR4-2666 ECC RDIMM", "DDR4", 12, 32, 300000, "Авито (ориентир), для 2 сокетов"),
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
]

PSUS = [
    ("Seasonic PRIME TX-1600 (ATX 3.1)", 1600, 57550, "chipdip"),
    ("БП 2000 Вт (серверный, в корпусе YCC)", 2000, 52407, "NIX, корпус 4U с БП 2000 Вт"),
    ("БП 1200 Вт (SuperFlower)", 1200, 25000, "Авито (ориентир)"),
    ("БП 1000 Вт (Corsair RM1000x)", 1000, 18000, "Авито (ориентир)"),
]
CASES = [
    ("NegoRack NR-M48 (4U, 650 мм)", 350, 8, 29623, "srv-trade"),
    ("Корпус 4U PROCASE (430 мм)", 300, 4, 22238, "srv-trade"),
    ("Открытый стенд", 400, 6, 8000, "Авито (ориентир)"),
    ("Fractal Define 7 XL", 460, 3, 33000, "снят с продажи, ориентир"),
    ("Lian Li PC-O11 Dynamic", 420, 2, 18000, "Авито (ориентир)"),
]

MODELS = [
    ("GLM-5.3-Flash Maya-L", "Maya", 156.3, 18, 8.8, 6.9, 48, 1872, 139, 2.0, 30.2, 801, 0.30, "2×3090 + EPYC 7452, #165"),
    ("GLM-5.3-Flash Maya-M", "Maya", 116.0, 18, 6.5, 6.9, 24, 936, 139, 1.0, 27.0, 1069, 0.30, "1×3090 + EPYC 7702P, #157"),
    ("Qwen3.8-Flash UD-Q4_K_XL", "Strata", 111.3, 6, 3.77, 4.8, 32, 644, 106, 1.25, 63.5, 1110, 0.12, "1×R9700 + EPYC 7452"),
    ("Qwen3.8-Flash UD-IQ4_XS", "Strata", 93.7, 6, 3.12, 4.8, 44, 1232, 150, 1.44, 55.0, 869, 0.12, "2×2080 Ti 22 ГБ, PR #2665"),
    ("DeepSeek-V4.1-Flash Maya-S", "Maya-ds4", 340.0, 40, 3.0, 20.0, 32, 1792, 90, 2.2, 24.9, 1842, 0.30, "1×RTX 5090 + 128 ГБ, dev.to"),
]

# ================================================================ Инструкция
s = WB.active
s.title = "Инструкция"
widths(s, [30, 118])
tex = [
    ("Калькулятор максимума LLM на выбранном железе", None),
    ("Что считает", "Декод (ток/с) и префилл (ток/с) для GLM-5.3-Flash (2 кванта), Qwen3.8-Flash-Next (2 кванта, Strata) и DeepSeek-V4.1-Flash-1017 (Maya-ds4), плюс цену сборки, требуемый БП и проверки совместимости"),
    ("Как пользоваться", "Лист «Калькулятор», сверху вниз: платформа → CPU → плата → память → GPU → количество → БП → корпус. Списки CPU, плат и памяти фильтруются сами: показываются только варианты под выбранную платформу"),
    ("Движки и модели", "Project Maya (GLM-5.3-Flash Maya-L и Maya-M, DeepSeek-V4.1-Flash) · Strata (Qwen3.8-Flash UD-Q4_K_XL и UD-IQ4_XS) · Basalt (Qwen3.8-Flash NVFP4-DQ6_K и GSQ-RCO-IQ3_S — форк Strata под Blackwell, работает только на sm_120: RTX 50 и RTX PRO 6000)"),
    ("Платформы", "SP3 (EPYC, 8×DDR4, 128 линий PCIe) · AM5 (Ryzen, 2×DDR5, 24 линии, максимум 2 GPU) · LGA4677 (Xeon SPR, 8×DDR5, до 240 ГБ/с) · LGA4189 (Xeon Ice Lake, 8×DDR4) · LGA3647 (Xeon Scalable, 6×DDR4 на сокет, AVX-512) · sTR5 (Threadripper 7000, 4×DDR5, до 80 линий PCIe)"),
    ("После смены платформы", "Перевыберите CPU, плату и память: старые значения останутся в ячейках и подсветятся в проверках как несовместимые"),
    ("Модель расчёта", "От измеренных опорных точек (лист «Модели»): декод масштабируется по доле экспертов в VRAM и полосе памяти, префилл — по compute и полосе RAM. Погрешность ±25 % по декоду и ±35 % по префиллу"),
    ("Максимум", "Лист «Максимум»: все карты базы × 1–4 штуки с расчётом каждой модели и рейтингом ТОП-5 по декоду и по цене за 1 ток/с"),
    ("Цены", "Авито блокирует автоматические запросы (HTTP 429). В базе два столбца: «Магазин» — проверенная цена открытой страницы, «Авито» — ориентир по объявлениям. Пометка «(ориентир)» в источнике означает непроверенную цену"),
    ("Совместимость", "Сокет, тип памяти, число GPU против слотов PCIe, длина карты против корпуса, мощность БП против расчётной. Итог — строка «ИТОГ ПРОВЕРОК»"),
    ("Не учтено", "Шум, температура, толщина карт (2–3 слота), райзеры, наличие на складе. 22-ГБ 2080 Ti — модифицированные карты"),
    ("Дата", "25 октября — 1 ноября 2026"),
]
for i, (a, b) in enumerate(tex, start=1):
    s.cell(row=i, column=1, value=a).font = Font(bold=(i == 1), size=(14 if i == 1 else 11))
    s.cell(row=i, column=2, value=b).alignment = WRAP
s.sheet_view.showGridLines = False

# ================================================================ GPU
g = WB.create_sheet("GPU")
head(g, 1, ["Модель", "VRAM, ГБ", "Полоса, ГБ/с", "TDP, Вт", "Длина, мм", "Слотов", "Compute", "Цена магазин, ₽", "Цена Авито, ₽", "Цена для расчёта, ₽", "Источник / статус", "Вендор", "Авито", "Арх.", "k Strata"])
r = 2
for name, vram, bw, tdp, ln, slots, comp, shop, avito, src, vendor in GPU_ROWS:
    g.cell(row=r, column=1, value=name)
    g.cell(row=r, column=2, value=vram)
    g.cell(row=r, column=3, value=bw)
    g.cell(row=r, column=4, value=tdp)
    g.cell(row=r, column=5, value=ln)
    g.cell(row=r, column=6, value=slots)
    g.cell(row=r, column=7, value=comp).number_format = NUM2
    _av = avito_price(name, avito)
    _note = avito_note(name)
    g.cell(row=r, column=8, value=shop if shop else None).number_format = MONEY
    g.cell(row=r, column=9, value=_av if _av else None).number_format = MONEY
    g.cell(row=r, column=10, value=f"=IF(I{r}>0,I{r},H{r})").number_format = MONEY
    g.cell(row=r, column=11, value=(src + (" · " + _note if _note else ""))).alignment = WRAP
    g.cell(row=r, column=12, value=vendor).alignment = CENTER
    g.cell(row=r, column=14, value=gpu_arch(name)).alignment = CENTER
    g.cell(row=r, column=15, value=strata_factor(name)).number_format = NUM2
    lc = g.cell(row=r, column=13, value="Авито")
    lc.hyperlink = avito_url(name)
    lc.font = LINK
    lc.alignment = CENTER
    r += 1
gpu_last = r - 1
note(g, r, "Compute — относительная матричная производительность (RTX 3090 = 1,00) для префилла, с учётом анлока FP16/BF16 у RTX 20/30/40. «Цена для расчёта» = Авито, если есть, иначе магазин.", 11)
widths(g, [30, 10, 13, 9, 10, 8, 10, 17, 15, 18, 52])
g.freeze_panes = "A2"

# ================================================================ CPU / Платы / Память
c = WB.create_sheet("CPU")
head(c, 1, ["Модель", "Сокет", "Ядра", "Каналов RAM", "Полоса RAM, ГБ/с", "TDP, Вт", "Цена, ₽", "Источник", "Авито"])
m = WB.create_sheet("Платы")
head(m, 1, ["Модель", "Сокет", "Тип RAM", "Слотов RAM", "Слотов PCIe x16", "Цена, ₽", "Источник", "Авито"])
p = WB.create_sheet("Память")
head(p, 1, ["Комплект", "Тип", "Модулей", "ГБ/модуль", "Итого ГБ", "Цена, ₽", "Источник", "Авито"])

ranges = {}
rc = rm = rp = 2
for plat in PLATFORMS:
    for ws, row, text in ((c, rc, plat["title"]), (m, rm, plat["title"]), (p, rp, plat["title"] + " — память")):
        cell = ws.cell(row=row, column=1, value=text)
        cell.font = SUB_FONT
        cell.fill = SUB_FILL
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=8)
        ws.row_dimensions[row].height = 20
    rc += 1; rm += 1; rp += 1
    c_start = rc
    for name, cores, ch, bw, tdp, price, src in plat["cpus"]:
        c.cell(row=rc, column=1, value=name)
        c.cell(row=rc, column=2, value=plat["name"])
        c.cell(row=rc, column=3, value=cores)
        c.cell(row=rc, column=4, value=ch)
        c.cell(row=rc, column=5, value=bw)
        c.cell(row=rc, column=6, value=tdp)
        c.cell(row=rc, column=7, value=avito_price(name, price)).number_format = MONEY
        c.cell(row=rc, column=8, value=(src + (" · " + avito_note(name) if avito_note(name) else ""))).alignment = WRAP
        lc = c.cell(row=rc, column=9, value="Авито")
        lc.hyperlink = avito_url(name)
        lc.font = LINK
        lc.alignment = CENTER
        rc += 1
    m_start = rm
    for name, ram, rs, ps, price, src in plat["mbs"]:
        m.cell(row=rm, column=1, value=name)
        m.cell(row=rm, column=2, value=plat["name"])
        m.cell(row=rm, column=3, value=ram)
        m.cell(row=rm, column=4, value=rs)
        m.cell(row=rm, column=5, value=ps)
        m.cell(row=rm, column=6, value=avito_price(name, price)).number_format = MONEY
        m.cell(row=rm, column=7, value=(src + (" · " + avito_note(name) if avito_note(name) else ""))).alignment = WRAP
        lc = m.cell(row=rm, column=8, value="Авито")
        lc.hyperlink = avito_url(name)
        lc.font = LINK
        lc.alignment = CENTER
        rm += 1
    p_start = rp
    for name, typ, mods, gb, price, src in plat["rams"]:
        p.cell(row=rp, column=1, value=name)
        p.cell(row=rp, column=2, value=typ)
        p.cell(row=rp, column=3, value=mods)
        p.cell(row=rp, column=4, value=gb)
        p.cell(row=rp, column=5, value=mods * gb)
        p.cell(row=rp, column=6, value=avito_price(name, price)).number_format = MONEY
        p.cell(row=rp, column=7, value=(src + (" · " + avito_note(name) if avito_note(name) else ""))).alignment = WRAP
        lc = p.cell(row=rp, column=8, value="Авито")
        lc.hyperlink = avito_url(name)
        lc.font = LINK
        lc.alignment = CENTER
        rp += 1
    ranges[plat["name"]] = {
        "cpu": f"'CPU'!$A${c_start}:$A${rc-1}",
        "mb": f"'Платы'!$A${m_start}:$A${rm-1}",
        "ram": f"'Память'!$A${p_start}:$A${rp-1}",
    }
    rc += 1; rm += 1; rp += 1

note(c, rc, "Полоса RAM: EPYC 8×DDR4-3200 ≈ 139 ГБ/с (STREAM), Ryzen 2×DDR5-6000 ≈ 90, Xeon SPR 8×DDR5-4800 ≈ 240, Ice Lake 8×DDR4 ≈ 150, Scalable 6×DDR4-2666 ≈ 110, Threadripper 4×DDR5-5600 ≈ 170 ГБ/с. Это скорость RAM-яруса для экспертов, не влезших в VRAM.", 8)
widths(c, [28, 12, 8, 14, 18, 9, 14, 28])
note(m, rm, "SP3/TR5/LGA4677: 4–7 слотов x16 — 4 карты без райзеров. AM5: 24 линии, максимум 2 карты в x8. X11DPi-NT — два сокета, 12 слотов RAM и 6 слотов x16.", 7)
widths(m, [30, 10, 10, 12, 16, 14, 30])
note(p, rp, "Комплекты сгруппированы по платформам: в списке памяти видны только те, что подходят к выбранной плате. Для моделей 96–200 ГБ нужно 128–256 ГБ RAM.", 7)
widths(p, [32, 8, 9, 12, 10, 14, 30])

# ================================================================ БП и корпус
b = WB.create_sheet("БП_Корпус")
head(b, 1, ["Компонент", "Тип", "Мощность, Вт", "Макс. длина GPU, мм", "Слотов GPU", "Цена, ₽", "Источник", "Авито"])
r = 2
b.cell(row=r, column=1, value="Блоки питания").font = SUB_FONT
b.cell(row=r, column=1).fill = SUB_FILL
b.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
r += 1
psu_start = r
for name, w, price, src in PSUS:
    b.cell(row=r, column=1, value=name)
    b.cell(row=r, column=2, value="БП")
    b.cell(row=r, column=3, value=w)
    b.cell(row=r, column=6, value=avito_price(name, price)).number_format = MONEY
    b.cell(row=r, column=7, value=(src + (" · " + avito_note(name) if avito_note(name) else ""))).alignment = WRAP
    lc = b.cell(row=r, column=8, value="Авито")
    lc.hyperlink = avito_url(name)
    lc.font = LINK
    lc.alignment = CENTER
    r += 1
psu_end = r - 1
r += 1
b.cell(row=r, column=1, value="Корпуса").font = SUB_FONT
b.cell(row=r, column=1).fill = SUB_FILL
b.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
r += 1
case_start = r
for name, ln, slots, price, src in CASES:
    b.cell(row=r, column=1, value=name)
    b.cell(row=r, column=2, value="Корпус")
    b.cell(row=r, column=4, value=ln)
    b.cell(row=r, column=5, value=slots)
    b.cell(row=r, column=6, value=avito_price(name, price)).number_format = MONEY
    b.cell(row=r, column=7, value=(src + (" · " + avito_note(name) if avito_note(name) else ""))).alignment = WRAP
    lc = b.cell(row=r, column=8, value="Авито")
    lc.hyperlink = avito_url(name)
    lc.font = LINK
    lc.alignment = CENTER
    r += 1
case_end = r - 1
widths(b, [34, 10, 14, 18, 12, 14, 34])

# ================================================================ SSD
sd = WB.create_sheet("SSD")
head(sd, 1, ["Модель", "Объём, ГБ", "Чтение, ГБ/с", "Цена, ₽", "Источник", "Авито"])
r = 2
for name, gb, gbs, price, src in SSDS:
    sd.cell(row=r, column=1, value=name)
    sd.cell(row=r, column=2, value=gb)
    sd.cell(row=r, column=3, value=gbs).number_format = NUM1
    sd.cell(row=r, column=4, value=avito_price(name, price)).number_format = MONEY
    sd.cell(row=r, column=5, value=(src + (" · " + avito_note(name) if avito_note(name) else ""))).alignment = WRAP
    lc = sd.cell(row=r, column=6, value="Авито")
    lc.hyperlink = avito_url(name)
    lc.font = LINK
    lc.alignment = CENTER
    r += 1
ssd_end = r - 1
widths(sd, [42, 12, 14, 14, 34, 10])

# ================================================================ Модели
md = WB.create_sheet("Модели")
head(md, 1, ["Модель", "Движок", "Размер, ГБ", "Активных, млрд", "Байт/токен, ГБ", "Dense, ГБ",
             "Anchor VRAM", "Anchor полоса VRAM", "Anchor полоса RAM", "Anchor compute",
             "Anchor декод", "Anchor префилл", "s опорная", "Степень", "Источник опоры", "KV ГБ/1К"])
r = 2
for name, eng, size, act, bt, dense, avram, abwv, abwr, acomp, adec, app, ex, src in MODELS:
    md.cell(row=r, column=1, value=name)
    md.cell(row=r, column=2, value=eng)
    md.cell(row=r, column=3, value=size)
    md.cell(row=r, column=4, value=act)
    md.cell(row=r, column=5, value=bt).number_format = NUM2
    md.cell(row=r, column=6, value=dense)
    md.cell(row=r, column=7, value=avram)
    md.cell(row=r, column=8, value=abwv)
    md.cell(row=r, column=9, value=abwr)
    md.cell(row=r, column=10, value=acomp)
    md.cell(row=r, column=11, value=adec).number_format = NUM1
    md.cell(row=r, column=12, value=app)
    md.cell(row=r, column=13, value=f"=MIN(1,MAX(0,(G{r}-F{r}-2)/(C{r}-F{r})))").number_format = NUM2
    md.cell(row=r, column=14, value=ex).number_format = NUM2
    md.cell(row=r, column=15, value=src).alignment = WRAP
    md.cell(row=r, column=16, value=kv_rate(name)).number_format = NUM2
    r += 1
md_last = r - 1
note(md, r, "Байт/токен = активные параметры × (размер кванта ÷ общее число параметров). «Степень» подобрана по второму замеру той же модели. Dense — плотные веса, всегда в VRAM.", 15)
widths(md, [28, 11, 11, 12, 14, 9, 11, 15, 15, 13, 11, 12, 10, 9, 34])

# ================================================================ Калькулятор
k = WB.create_sheet("Калькулятор")
widths(k, [34, 34, 18, 20, 52])
k.cell(row=1, column=1, value="ВЫБОР ЖЕЛЕЗА").font = SUB_FONT
k.cell(row=1, column=1).fill = SUB_FILL
k.merge_cells(start_row=1, start_column=1, end_row=1, end_column=5)
inputs = [
    ("Платформа", "SP3", "6 платформ: SP3, AM5, LGA4677, LGA4189, LGA3647, TR5"),
    ("CPU", "AMD EPYC 7402", "фильтруется по платформе"),
    ("Материнская плата", "Supermicro H12SSL-I-B", "фильтруется по платформе"),
    ("Память", "8×32 ГБ DDR4-3200 ECC RDIMM", "только комплекты выбранной платформы"),
    ("Видеокарта", "RTX 3090 24 ГБ", "20 карт в базе"),
    ("Количество GPU", 2, "1–4, проверяется по слотам"),
    ("Блок питания", "Seasonic PRIME TX-1600 (ATX 3.1)", "проверяется по мощности"),
    ("Корпус", "NegoRack NR-M48 (4U, 650 мм)", "проверяется по длине карты"),
]
r = 2
for name, val, hint in inputs:
    k.cell(row=r, column=1, value=name).font = Font(bold=True)
    cell = k.cell(row=r, column=2, value=val)
    cell.fill = IN_FILL
    cell.alignment = CENTER
    k.cell(row=r, column=3, value=hint).alignment = WRAP
    r += 1

# контекст: отдельный ввод справа, чтобы не сдвигать блоки ниже
k.cell(row=2, column=4, value="Контекст, токенов").font = Font(bold=True)
_ctxi = k.cell(row=2, column=5, value=CTX_DEFAULT)
_ctxi.fill = IN_FILL
_ctxi.alignment = CENTER
_ctxi.number_format = '#,##0'
k.cell(row=3, column=4, value="KV-кэш (ГБ):").font = Font(bold=True)
k.cell(row=3, column=5, value='=Модели!P2*$E$2/1000').number_format = NUM1
k.cell(row=4, column=4, value="Множитель Basalt (CPU):").font = Font(bold=True)
k.cell(row=4, column=5, value='=IF($B$2="SP3",0.5,IF($B$2="AM4",0.62,IF($B$2="LGA3647",0.38,1)))').number_format = NUM2
note(k, 5, "Basalt считает экспертов на CPU: без AVX-512/VBMI2 и AVX-VNNI (SP3, AM4, LGA3647) движок падает на AVX2 и упирается в процессор. Множитель в E4 — из замера Xeon 6252 + RTX 5070 Ti (73 tok/s прозы).", 5)

for row, label, formula, fmt in [
    (10, "Вендор GPU", '=IFERROR(VLOOKUP(B6,GPU!$A:$L,12,0),"?")', None),
    (11, "Тип памяти платы", '=IFERROR(VLOOKUP(B4,Платы!$A:$G,3,0),"?")', None),
    (12, "Слотов PCIe x16 у платы", '=IFERROR(VLOOKUP(B4,Платы!$A:$G,5,0),0)', None),
    (13, "Тип памяти комплекта", '=IFERROR(VLOOKUP(B5,Память!$A:$G,2,0),"?")', None),
    (14, "Полоса RAM, ГБ/с", '=IFERROR(VLOOKUP(B3,CPU!$A:$H,5,0),0)', NUM1),
    (15, "Сокет CPU", '=IFERROR(VLOOKUP(B3,CPU!$A:$H,2,0),"?")', None),
    (16, "Сокет платы", '=IFERROR(VLOOKUP(B4,Платы!$A:$G,2,0),"?")', None),
]:
    k.cell(row=row, column=1, value=label).font = Font(bold=True)
    cell = k.cell(row=row, column=2, value=formula)
    cell.alignment = CENTER
    if fmt:
        cell.number_format = fmt

k.cell(row=17, column=1, value="РЕЗУЛЬТАТ ПО СБОРКЕ").font = SUB_FONT
k.cell(row=17, column=1).fill = SUB_FILL
k.merge_cells(start_row=17, start_column=1, end_row=17, end_column=5)
res = [
    ("Суммарный VRAM, ГБ", '=IFERROR(VLOOKUP(B6,GPU!$A:$K,2,0)*B7,0)', NUM1),
    ("Суммарная полоса VRAM, ГБ/с", '=IFERROR(VLOOKUP(B6,GPU!$A:$K,3,0)*B7,0)', NUM1),
    ("Суммарный compute", '=IFERROR(VLOOKUP(B6,GPU!$A:$K,7,0)*B7,0)', NUM2),
    ("Цена GPU", '=IFERROR(VLOOKUP(B6,GPU!$A:$K,10,0)*B7,0)', MONEY),
    ("Цена CPU + плата + память", '=IFERROR(VLOOKUP(B3,CPU!$A:$H,7,0),0)+IFERROR(VLOOKUP(B4,Платы!$A:$G,6,0),0)+IFERROR(VLOOKUP(B5,Память!$A:$G,6,0),0)', MONEY),
    ("Цена БП + корпус", '=IFERROR(VLOOKUP(B8,БП_Корпус!$A:$G,6,0),0)+IFERROR(VLOOKUP(B9,БП_Корпус!$A:$G,6,0),0)', MONEY),
    ("ИТОГО цена сборки, ₽", "=SUM(B21:B23)+IFERROR(VLOOKUP(B57,SSD!$A:$D,4,0),0)", MONEY),
    ("Требуемая мощность, Вт", '=IFERROR(VLOOKUP(B6,GPU!$A:$K,4,0)*B7*1.1 + VLOOKUP(B3,CPU!$A:$H,6,0)*1.3 + 100,0)', NUM1),
    ("Рекомендуемый БП, Вт", "=ROUNDUP(B25/0.75/50,0)*50", NUM1),
    ("Мощность выбранного БП, Вт", '=IFERROR(VLOOKUP(B8,БП_Корпус!$A:$G,3,0),0)', NUM1),
]
r = 18
for name, formula, fmt in res:
    k.cell(row=r, column=1, value=name).font = Font(bold=True)
    cell = k.cell(row=r, column=2, value=formula)
    cell.fill = OUT_FILL
    cell.number_format = fmt
    r += 1

k.cell(row=28, column=1, value="ПРОВЕРКИ СОВМЕСТИМОСТИ").font = SUB_FONT
k.cell(row=28, column=1).fill = SUB_FILL
k.merge_cells(start_row=28, start_column=1, end_row=28, end_column=5)
checks = [
    ("Сокет CPU = сокет платы", '=IF(B15=B16,"OK","РАЗНЫЕ СОКЕТЫ")'),
    ("Тип памяти совпадает с платой", '=IF(B11=B13,"OK","НЕ СОВПАДАЕТ")'),
    ("Число GPU ≤ слотов PCIe", '=IF(B7<=B12,"OK","НЕ ХВАТИТ СЛОТОВ")'),
    ("Длина карты ≤ корпуса", '=IF(IFERROR(VLOOKUP(B6,GPU!$A:$K,5,0),0)<=IFERROR(VLOOKUP(B9,БП_Корпус!$A:$G,4,0),0),"OK","НЕ ВЛЕЗЕТ")'),
    ("Мощности БП хватает", '=IF(B27>=B26,"OK","БП СЛАБЫЙ")'),
    ("Слотов GPU у корпуса хватает", '=IF(B7<=IFERROR(VLOOKUP(B9,БП_Корпус!$A:$G,5,0),0),"OK","МАЛО СЛОТОВ")'),
]
r = 29
for name, formula in checks:
    k.cell(row=r, column=1, value=name).font = Font(bold=True)
    cell = k.cell(row=r, column=2, value=formula)
    cell.alignment = CENTER
    r += 1
k.cell(row=36, column=1, value="ИТОГ ПРОВЕРОК").font = Font(bold=True)
k.cell(row=36, column=2, value='=IF(COUNTIF(B29:B34,"OK")=6,"ВСЁ СОВМЕСТИМО","ЕСТЬ ПРОБЛЕМЫ")').font = Font(bold=True)
k.cell(row=37, column=1, value="Поддержка моделей (вендор и Basalt)").font = Font(bold=True)
k.cell(row=37, column=2, value='=IF(B10="NVIDIA","NVIDIA: Maya + Strata","Вендор "&B10&": только Strata")&" · Basalt: "&IF(IFERROR(VLOOKUP(B6,GPU!$A:$N,14,0),"")="Blackwell","доступен","нужен Blackwell (sm_120)")').font = Font(bold=True)

k.cell(row=38, column=1, value="СКОРОСТЬ ПО МОДЕЛЯМ (оценка ±25 %)").font = SUB_FONT
k.cell(row=38, column=1).fill = SUB_FILL
k.merge_cells(start_row=38, start_column=1, end_row=38, end_column=5)
head(k, 39, ["Модель", "s (доля в VRAM)", "Декод, ток/с", "Префилл, ток/с", "Что ограничивает"])
r = 40
for i in range(len(MODELS)):
    md_row = 2 + i
    engine = MODELS[i][1]
    dec_f = (f"Модели!K{md_row}*(((B{r}*$B$19+(1-B{r})*$B$14)"
             f"/(Модели!M{md_row}*Модели!H{md_row}+(1-Модели!M{md_row})*Модели!I{md_row}))^Модели!N{md_row})")
    pp_f = f"Модели!L{md_row}*(($B$20/Модели!J{md_row})^0.35)*(($B$14/Модели!I{md_row})^0.2)"
    if engine == "Basalt":
        guard = f'AND(Модели!B{md_row}="Basalt",IFERROR(VLOOKUP($B$6,GPU!$A:$N,14,0),"")<>"Blackwell"),"—",'
        dec_f = "IF(" + guard + dec_f + "*$E$4)"
        pp_f = "IF(" + guard + pp_f + "*SQRT($E$4))"
    elif engine == "Strata":
        dec_f = dec_f + "*IFERROR(VLOOKUP($B$6,GPU!$A:$O,15,0),1)"
    k.cell(row=r, column=1, value=f"=Модели!A{md_row}")
    k.cell(row=r, column=2, value=f"=MIN(1,MAX(0,($B$18-Модели!F{md_row}-Модели!P{md_row}*$E$2/1000)/(Модели!C{md_row}-Модели!F{md_row})))").number_format = NUM2
    k.cell(row=r, column=3, value="=" + dec_f).number_format = NUM1
    k.cell(row=r, column=4, value="=" + pp_f).number_format = NUM1
    k.cell(row=r, column=5, value=f'=IF(B{r}>0.8,"всё в VRAM",IF(B{r}>0.3,"VRAM + RAM-ярус","упирается в RAM/SSD"))')
    r += 1
note(k, r + 1, "s — доля весов экспертов в VRAM (после вычета плотных весов и 2 ГБ контекста). Декод масштабируется по эффективной полосе со степенью из «Моделей», префилл — по compute и полосе RAM.", 5)

k.cell(row=49, column=1, value="СТОИМОСТЬ ПОЗИЦИЙ И ССЫЛКИ НА АВИТО").font = SUB_FONT
k.cell(row=49, column=1).fill = SUB_FILL
k.merge_cells(start_row=49, start_column=1, end_row=49, end_column=4)
head(k, 50, ["Позиция", "Выбранная модель", "Цена, ₽", "Авито"])
breakdown = [
    ("CPU", "=B3", '=IFERROR(VLOOKUP(B3,CPU!$A:$H,7,0),0)', '=HYPERLINK(IFERROR(VLOOKUP(B3,CPU!$A:$I,9,0),""),"Авито")'),
    ("Материнская плата", "=B4", '=IFERROR(VLOOKUP(B4,Платы!$A:$G,6,0),0)', '=HYPERLINK(IFERROR(VLOOKUP(B4,Платы!$A:$H,8,0),""),"Авито")'),
    ("Память", "=B5", '=IFERROR(VLOOKUP(B5,Память!$A:$G,6,0),0)', '=HYPERLINK(IFERROR(VLOOKUP(B5,Память!$A:$H,8,0),""),"Авито")'),
    ("Видеокарта", '=B6&" × "&B7', '=IFERROR(VLOOKUP(B6,GPU!$A:$K,10,0)*B7,0)', '=HYPERLINK(IFERROR(VLOOKUP(B6,GPU!$A:$M,13,0),""),"Авито")'),
    ("Блок питания", "=B8", '=IFERROR(VLOOKUP(B8,БП_Корпус!$A:$G,6,0),0)', '=HYPERLINK(IFERROR(VLOOKUP(B8,БП_Корпус!$A:$H,8,0),""),"Авито")'),
    ("Корпус", "=B9", '=IFERROR(VLOOKUP(B9,БП_Корпус!$A:$G,6,0),0)', '=HYPERLINK(IFERROR(VLOOKUP(B9,БП_Корпус!$A:$H,8,0),""),"Авито")'),
]
rr = 51
for label, name_f, price_f, link_f in breakdown:
    k.cell(row=rr, column=1, value=label).font = Font(bold=True)
    k.cell(row=rr, column=2, value=name_f).alignment = WRAP
    k.cell(row=rr, column=3, value=price_f).number_format = MONEY
    lc = k.cell(row=rr, column=4, value=link_f)
    lc.alignment = CENTER
    rr += 1
# накопитель — выбирается тут же
k.cell(row=57, column=1, value="Накопитель (SSD)").font = Font(bold=True)
ssd_cell = k.cell(row=57, column=2, value=SSD_DEFAULT)
ssd_cell.fill = IN_FILL
ssd_cell.alignment = CENTER
k.cell(row=57, column=3, value='=IFERROR(VLOOKUP(B57,SSD!$A:$D,4,0),0)').number_format = MONEY
lc = k.cell(row=57, column=4, value='=HYPERLINK(IFERROR(VLOOKUP(B57,SSD!$A:$F,6,0),""),"Авито")')
lc.alignment = CENTER
k.cell(row=58, column=1, value="ИТОГО по позициям").font = Font(bold=True)
c = k.cell(row=58, column=3, value="=SUM(C51:C57)")
c.number_format = MONEY
c.font = Font(bold=True)
k.cell(row=58, column=4, value='=IF(ROUND(C58-B24,0)=0,"сходится с итогом","расхождение с B24")')

def dv(formula, cell):
    v = DataValidation(type="list", formula1=formula, allow_blank=False)
    k.add_data_validation(v)
    v.add(k[cell])

dv('"' + ",".join(p["name"] for p in PLATFORMS) + '"', "B2")
dv('INDIRECT("CPU_"&$B$2)', "B3")
dv('INDIRECT("MB_"&$B$2)', "B4")
dv('INDIRECT("RAM_"&$B$2)', "B5")
dv("GPU_ALL", "B6")
dv('"1,2,3,4"', "B7")
dv("PSU_ALL", "B8")
dv("CASE_ALL", "B9")
dv("SSD_ALL", "B57")
dv('"8192,32768,65536,131072,262144"', "E2")

# ================================================================ Максимум
mx = WB.create_sheet("Максимум")
head(mx, 1, ["№", "Видеокарта", "Кол-во", "VRAM, ГБ", "Полоса VRAM", "Compute", "Цена GPU, ₽", "Цена сборки, ₽",
             "GLM-L декод", "GLM-L префилл", "Qwen Q4 декод", "Qwen Q4 префилл", "DS4 декод", "DS4 префилл",
             "₽/ток/с GLM-L", "₽/ток/с Qwen Q4", "Совместимо"])
K = "Калькулятор!"
plat = (f"IFERROR(VLOOKUP({K}$B$3,CPU!$A:$H,7,0),0)+IFERROR(VLOOKUP({K}$B$4,Платы!$A:$G,6,0),0)"
        f"+IFERROR(VLOOKUP({K}$B$5,Память!$A:$G,6,0),0)+IFERROR(VLOOKUP({K}$B$8,БП_Корпус!$A:$G,6,0),0)"
        f"+IFERROR(VLOOKUP({K}$B$9,БП_Корпус!$A:$G,6,0),0)")
r = 2
n = 0
for gi in range(2, gpu_last + 1):
    for cnt in (1, 2, 3, 4):
        n += 1
        mx.cell(row=r, column=1, value=n)
        mx.cell(row=r, column=2, value=f"=GPU!A{gi}")
        mx.cell(row=r, column=3, value=cnt)
        mx.cell(row=r, column=4, value=f"=GPU!B{gi}*C{r}")
        mx.cell(row=r, column=5, value=f"=GPU!C{gi}*C{r}")
        mx.cell(row=r, column=6, value=f"=GPU!G{gi}*C{r}").number_format = NUM2
        mx.cell(row=r, column=7, value=f"=GPU!J{gi}*C{r}").number_format = MONEY
        mx.cell(row=r, column=8, value=f"=G{r}+{plat}").number_format = MONEY
        for col, mrow in ((9, 2), (11, 4), (13, 6)):
            s_expr = f"MIN(1,MAX(0,(D{r}-Модели!F{mrow}-Модели!P{mrow}*{K}$E$2/1000)/(Модели!C{mrow}-Модели!F{mrow})))"
            mx.cell(row=r, column=col, value=(
                f"=Модели!K{mrow}*((({s_expr}*E{r}+(1-{s_expr})*{K}$B$14)"
                f"/(Модели!M{mrow}*Модели!H{mrow}+(1-Модели!M{mrow})*Модели!I{mrow}))^Модели!N{mrow})"
            )).number_format = NUM1
            mx.cell(row=r, column=col + 1, value=(
                f"=Модели!L{mrow}*((F{r}/Модели!J{mrow})^0.35)*(({K}$B$14/Модели!I{mrow})^0.2)"
            )).number_format = NUM1
        mx.cell(row=r, column=15, value=f'=IFERROR(H{r}/I{r},"")').number_format = MONEY
        mx.cell(row=r, column=16, value=f'=IFERROR(H{r}/K{r},"")').number_format = MONEY
        mx.cell(row=r, column=17, value=f'=IF(C{r}<={K}$B$12,"да","нет")').alignment = CENTER
        mx.cell(row=r, column=18, value=f"=I{r}-ROW()/1000000").number_format = NUM2
        mx.cell(row=r, column=19, value=f"=O{r}-ROW()/1000000").number_format = NUM2
        r += 1
mx_last = r - 1
note(mx, r, "Каждая строка — «карта × количество» на платформе из «Калькулятора» (CPU, плата, память, БП, корпус оттуда же). «нет» в последнем столбце — карт больше, чем слотов PCIe.", 17)

top1 = r + 2
mx.cell(row=top1, column=1, value="ТОП-5 по декоду GLM-L").font = SUB_FONT
mx.cell(row=top1, column=1).fill = SUB_FILL
mx.merge_cells(start_row=top1, start_column=1, end_row=top1, end_column=4)
head(mx, top1 + 1, ["Место", "Конфигурация", "Декод, ток/с", "Цена сборки, ₽"])
for i in range(5):
    rr = top1 + 2 + i
    mx.cell(row=rr, column=1, value=i + 1)
    mx.cell(row=rr, column=2, value=f'=IFERROR(INDEX($B$2:$B${mx_last},MATCH(LARGE($R$2:$R${mx_last},A{rr}),$R$2:$R${mx_last},0))&" × "&INDEX($C$2:$C${mx_last},MATCH(LARGE($R$2:$R${mx_last},A{rr}),$R$2:$R${mx_last},0)),"")')
    mx.cell(row=rr, column=3, value=f'=IFERROR(LARGE($R$2:$R${mx_last},A{rr}),"")').number_format = NUM1
    mx.cell(row=rr, column=4, value=f'=IFERROR(INDEX($H$2:$H${mx_last},MATCH(LARGE($R$2:$R${mx_last},A{rr}),$R$2:$R${mx_last},0)),"")').number_format = MONEY

top2 = top1 + 9
mx.cell(row=top2, column=1, value="ТОП-5 по цене за 1 ток/с (GLM-L)").font = SUB_FONT
mx.cell(row=top2, column=1).fill = SUB_FILL
mx.merge_cells(start_row=top2, start_column=1, end_row=top2, end_column=4)
head(mx, top2 + 1, ["Место", "Конфигурация", "₽ за 1 ток/с", "Декод, ток/с"])
for i in range(5):
    rr = top2 + 2 + i
    mx.cell(row=rr, column=1, value=i + 1)
    mx.cell(row=rr, column=2, value=f'=IFERROR(INDEX($B$2:$B${mx_last},MATCH(SMALL($S$2:$S${mx_last},A{rr}),$S$2:$S${mx_last},0))&" × "&INDEX($C$2:$C${mx_last},MATCH(SMALL($S$2:$S${mx_last},A{rr}),$S$2:$S${mx_last},0)),"")')
    mx.cell(row=rr, column=3, value=f'=IFERROR(SMALL($S$2:$S${mx_last},A{rr}),"")').number_format = MONEY
    mx.cell(row=rr, column=4, value=f'=IFERROR(INDEX($I$2:$I${mx_last},MATCH(SMALL($S$2:$S${mx_last},A{rr}),$S$2:$S${mx_last},0)),"")').number_format = NUM1
widths(mx, [5, 30, 8, 10, 13, 9, 15, 16, 12, 13, 12, 13, 11, 12, 16, 16, 12])

# ================================================================ Замеры
zz = WB.create_sheet("Замеры")
head(zz, 1, ["Модель / движок", "Железо", "Декод, ток/с", "Префилл, ток/с", "Источник"])
r = 2
for a, bb, cc, dd, ee in [
    ("GLM-5.3-Flash Maya-L (Maya)", "2× RTX 3090, EPYC 7452, 256 ГБ", 30.2, "801 (8K)", "Maya #165"),
    ("GLM-5.3-Flash Maya-M (Maya)", "1× RTX 3090, EPYC 7702P", 27.0, "1069 (8K)", "Maya #157"),
    ("GLM-5.3-Flash Maya-M (Maya)", "1× RTX 5090, 96 ГБ DDR5", "30+", "~2000", "Maya #43"),
    ("GLM-5.3-Flash Maya-L (Maya)", "2× RTX 5880 Ada 45 ГБ", 54.5, "1401 (8K)", "Maya #149"),
    ("GLM-5.3-Flash Maya-L (Maya)", "4× RTX 3090, TR PRO, 256 ГБ", 38.0, "600–700", "Maya #142"),
    ("Qwen3.8 UD-Q4_K_XL (Strata)", "1× R9700, EPYC 7452", "63–64", "1110–1320", "Strata QUANTS.md"),
    ("Qwen3.8 UD-Q4_K_XL (Strata)", "2× R9700", 64, "1275", "Strata QUANTS.md"),
    ("Qwen3.8 UD-Q4_K_XL (Strata)", "4× R9700", 52, "2381", "Strata QUANTS.md"),
    ("Qwen3.8 UD-Q4_K_XL (Strata)", "1× RTX 5090, 9950X3D", 109.7, "—", "Strata PR #1617"),
    ("Qwen3.8 UD-IQ4_XS (Strata)", "2× RTX 2080 Ti 22 ГБ", "52,4–57,9", "—", "Strata PR #2665"),
    ("DeepSeek-V4.1-Flash (Maya-ds4)", "1× RTX 5090, 128 ГБ DDR5", "24,9", "1842 (31K) / 2570 (126K)", "dev.to, 10.2026"),
]:
    zz.cell(row=r, column=1, value=a).alignment = WRAP
    zz.cell(row=r, column=2, value=bb).alignment = WRAP
    zz.cell(row=r, column=3, value=cc).alignment = CENTER
    zz.cell(row=r, column=4, value=dd).alignment = CENTER
    zz.cell(row=r, column=5, value=ee).alignment = WRAP
    r += 1
note(zz, r, "Опорные точки калькулятора. Остальное — оценка: зависит от кванта, контекста, профиля маршрутизации и версии движка.", 5)
widths(zz, [36, 42, 20, 26, 26])

# ================================================================ имена
for plat in PLATFORMS:
    nm = plat["name"]
    for key, prefix in (("cpu", "CPU_"), ("mb", "MB_"), ("ram", "RAM_")):
        WB.defined_names[prefix + nm] = DefinedName(prefix + nm, attr_text=ranges[nm][key])
WB.defined_names["GPU_ALL"] = DefinedName("GPU_ALL", attr_text=f"'GPU'!$A$2:$A${gpu_last}")
WB.defined_names["PSU_ALL"] = DefinedName("PSU_ALL", attr_text=f"'БП_Корпус'!$A${psu_start}:$A${psu_end}")
WB.defined_names["CASE_ALL"] = DefinedName("CASE_ALL", attr_text=f"'БП_Корпус'!$A${case_start}:$A${case_end}")
WB.defined_names["SSD_ALL"] = DefinedName("SSD_ALL", attr_text=f"'SSD'!$A$2:$A${ssd_end}")

# рамки
for nm in ("GPU", "CPU", "Платы", "Память", "БП_Корпус", "Модели", "Замеры", "Максимум"):
    ws = WB[nm]
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=ws.max_column):
        for cell in row:
            if cell.value is not None:
                cell.border = BORDER
for row in k.iter_rows(min_row=1, max_row=k.max_row, max_col=5):
    for cell in row:
        if cell.value is not None:
            cell.border = BORDER

WB.save(OUT)
print("saved:", OUT)
print("platforms:", [p["name"] for p in PLATFORMS])
print("gpus:", gpu_last - 1, "models:", md_last - 1, "max rows:", mx_last - 1)
