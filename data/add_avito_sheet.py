# -*- coding: utf-8 -*-
"""Добавляет в Excel лист «Авито» с реальными ценами, собранными из объявлений."""
import json
import os
import sys

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(HERE, "AI_Calculator_Hardware_Avito.xlsx")
PRICES = os.path.join(HERE, "avito_prices.json")
sys.path.insert(0, HERE)
import db  # noqa: E402

MONEY = '#,##0" ₽"'
H_FONT = Font(bold=True, color="FFFFFF", size=11)
H_FILL = PatternFill("solid", fgColor="4A148C")
LINK = Font(color="0563C1", underline="single")
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="center")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

KIND_RU = {"gpu": "Видеокарта", "cpu": "Процессор", "mb": "Плата", "ram": "Память", "psu": "БП", "case": "Корпус"}

data = json.load(open(PRICES, encoding="utf-8"))
wb = load_workbook(XLSX)
if "Авито" in wb.sheetnames:
    del wb["Авито"]
ws = wb.create_sheet("Авито", 1)

head = ["Позиция", "Тип", "Запрос", "Объявлений", "Мин, ₽", "p25, ₽", "Медиана, ₽", "p75, ₽", "Макс, ₽",
        "Было (оценка), ₽", "Отклонение", "В расчёте", "Причина", "Ссылка"]
for i, h in enumerate(head, start=1):
    c = ws.cell(row=1, column=i, value=h)
    c.font = H_FONT
    c.fill = H_FILL
    c.alignment = Alignment(wrap_text=True, vertical="center")
ws.row_dimensions[1].height = 30

rows = [(n, v) for n, v in data.items() if isinstance(v, dict) and v.get("median")]
rows.sort(key=lambda x: (x[1].get("kind", ""), x[0]))

r = 2
for name, v in rows:
    ws.cell(row=r, column=1, value=name).alignment = WRAP
    ws.cell(row=r, column=2, value=KIND_RU.get(v.get("kind"), v.get("kind"))).alignment = CENTER
    ws.cell(row=r, column=3, value=v.get("query", "")).alignment = WRAP
    ws.cell(row=r, column=4, value=v.get("ads_clean")).alignment = CENTER
    for col, key in ((5, "min"), (6, "p25"), (7, "median"), (8, "p75"), (9, "max")):
        cell = ws.cell(row=r, column=col, value=v.get(key))
        cell.number_format = MONEY
    est = v.get("estimate")
    ws.cell(row=r, column=10, value=est).number_format = MONEY
    if est:
        cell = ws.cell(row=r, column=11, value=(v["median"] / est) - 1)
        cell.number_format = "+0 %;-0 %;0 %"
    used = db.avito_stats(name) is not None
    ws.cell(row=r, column=12, value="да" if used else "нет").alignment = CENTER
    ws.cell(row=r, column=13, value=db.avito_reject_reason(name)).alignment = WRAP
    lc = ws.cell(row=r, column=14, value="Авито")
    lc.hyperlink = db.avito_url(name)
    lc.font = LINK
    lc.alignment = CENTER
    r += 1

total_row = r + 1
ws.cell(row=total_row, column=1, value="Всего позиций с реальными ценами").font = Font(bold=True)
ws.cell(row=total_row, column=4, value=len(rows)).font = Font(bold=True)
ws.cell(row=total_row + 1, column=1,
        value="Медиана по объявлениям Авито (Санкт-Петербург), мусорные лоты (скупка, нерабочие, на запчасти) отфильтрованы. "
              "Собрано автоматически через Opera + CDP 04.11.2026.").alignment = WRAP
ws.merge_cells(start_row=total_row + 1, start_column=1, end_row=total_row + 1, end_column=12)

widths = [34, 13, 30, 12, 12, 12, 14, 12, 12, 16, 12, 11, 26, 10]
for i, w in enumerate(widths, start=1):
    ws.column_dimensions[get_column_letter(i)].width = w
for row in ws.iter_rows(min_row=1, max_row=r - 1, max_col=14):
    for cell in row:
        cell.border = BORDER
ws.freeze_panes = "A2"

wb.save(XLSX)
print("лист «Авито» добавлен:", len(rows), "позиций")

# ---- карточка сборки картинкой
try:
    import card as card_mod
    import model as model_mod
    from openpyxl.drawing.image import Image as XLImage

    png = os.path.join(HERE, "card.png")
    b = model_mod.build()
    card_mod.make_card(b, png)
    if "Карточка" in wb.sheetnames:
        del wb["Карточка"]
    ws2 = wb.create_sheet("Карточка", 1)
    ws2.cell(row=1, column=1, value="Карточка сборки (по умолчанию): %d× %s, %s" % (
        b["count"], b["gpu"]["name"], b["cpu"]["name"])).font = Font(bold=True, size=12)
    ws2.cell(row=2, column=1, value="На сайте карточка генерируется под выбранную конфигурацию кнопкой «Скачать карточку PNG».").alignment = WRAP
    img = XLImage(png)
    ws2.add_image(img, "A4")
    ws2.column_dimensions["A"].width = 12
    wb.save(XLSX)
    print("лист «Карточка» добавлен:", png)
except Exception as e:
    print("карточка не добавлена:", e)
