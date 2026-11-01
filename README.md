# Калькулятор AI-железа: GLM-5.3-Flash, Qwen3.8-Flash-Next, DeepSeek-V4.1-Flash

Считает **скорость инференса** (декод и префилл, ток/с) для выбранной сборки ПК и **цену** этой сборки
по российским ценам (магазины + ориентиры по Авито). Есть две версии с одинаковой моделью расчёта:

- **Сайт** (этот репозиторий, GitHub Pages) — выпадающие списки с фильтрацией по совместимости.
- **Excel** — `AI_Calculator_Hardware_Avito.xlsx`: те же данные, зависимые списки через именованные диапазоны,
  лист «Максимум» с рейтингом всех конфигураций.

## Что в базе

| | Количество |
|---|---|
| Платформ | 9: SP3, AM5, LGA1851 (Core Ultra 200S), LGA1700, LGA4677, LGA4189, LGA3647, sTR5, AM4 |
| Процессоров | 28 |
| Материнских плат | 24 |
| Комплектов памяти | 24 |
| Видеокарт | 32 (NVIDIA RTX 20/30/40/50, Ada/Quadro, Tesla; AMD RX 7000/9000 и R9700; Intel Arc) |
| Моделей | 5: GLM-5.3-Flash Maya-L и Maya-M, Qwen3.8-Flash UD-Q4_K_XL и UD-IQ4_XS, DeepSeek-V4.1-Flash Maya-S |

## Как считается

Для каждой модели хранится измеренная опорная точка (железо → декод → префилл). Дальше:

- **Доля экспертов в VRAM**: `s = (VRAM − плотные веса − 2 ГБ) / (размер кванта − плотные веса)`.
- **Декод**: масштабируется от опоры по эффективной полосе `s × полоса VRAM + (1−s) × полоса RAM`
  со степенью 0,12–0,30 (своя для каждой модели, подобрана по второму замеру).
- **Префилл**: от опоры по `compute^0.35` и полосе RAM `^0.2`.
- **Проверки**: сокет CPU = сокет платы, тип памяти, число GPU ≤ слотов PCIe, длина карты ≤ корпуса,
  мощность БП ≥ расчётной, вендор (Maya требует NVIDIA — для AMD/Intel считаются только Strata-модели).

Погрешность: **±25 % по декоду, ±35 % по префиллу**. Это оценка, а не замер.

## Опорные замеры

| Модель | Железо | Декод | Префилл | Источник |
|---|---|---:|---:|---|
| GLM-5.3-Flash Maya-L | 2× RTX 3090 + EPYC 7452 | 30,2 | 801 (8K) | [Maya #165](https://github.com/mw00/project-maya/issues/165) |
| GLM-5.3-Flash Maya-M | 1× RTX 3090 + EPYC 7702P | 27,0 | 1069 (8K) | [Maya #157](https://github.com/mw00/project-maya/issues/157) |
| GLM-5.3-Flash Maya-M | 1× RTX 5090 + 96 ГБ | 30+ | ~2000 | [Maya #43](https://github.com/mw00/project-maya/issues/43) |
| GLM-5.3-Flash Maya-L | 2× RTX 5880 Ada 45 ГБ | 54,5 | 1401 (8K) | [Maya #149](https://github.com/mw00/project-maya/issues/149) |
| Qwen3.8 UD-Q4_K_XL | 1× R9700 + EPYC 7452 | 63–64 | 1110–1320 | [Strata QUANTS.md](https://github.com/Niko1221/Strata/blob/main/docs/QUANTS.md) |
| Qwen3.8 UD-IQ4_XS | 2× RTX 2080 Ti 22 ГБ | 52,4–57,9 | — | [Strata PR #2665](https://github.com/Niko1221/Strata/pull/2665) |
| DeepSeek-V4.1-Flash Maya-S | 1× RTX 5090 + 128 ГБ | 24,9 | 1842 (31K) | [dev.to, 10.2026](https://dev.to/seppegadeyne/run-deepseek-v41-flash-748b-locally-with-project-maya-on-one-rtx-5090-4i4a) |

## Цены

Авито блокирует автоматические запросы (HTTP 429), поэтому в базе два поля: **цена магазина** (проверенная
страница) и **цена Авито** (ориентир по объявлениям). В расчёт идёт Авито, если оно заполнено.
Пометка «(ориентир)» в источнике означает непроверенную цену. Проверяйте перед покупкой.

## Обновить данные

```bash
# 1. правим data/db.py (единая база: GPU, платформы, БП, корпуса, модели)
python data/build_site.py     # → data.js
python data/gen_xlsx.py       # → Excel-калькулятор из ai_calc.py + db.py
```

`calc.js` — модель расчёта, работает и в браузере, и в Node:

```bash
node data/test_calc.js   # сверяет расчёт с числами Excel
```

## Файлы

```
index.html        — интерфейс (корень = GitHub Pages)
calc.js           — модель расчёта
data.js           — данные (генерируется из data/db.py)
styles.css        — оформление
data/db.py        — единая база данных
data/ai_calc.py   — сборка Excel (рендер листов)
data/gen_xlsx.py  — подставляет db.py в сборку и запускает её
data/build_site.py — генерирует data.js
data/test_calc.js — тест модели против чисел Excel
AI_Calculator_Hardware_Avito.xlsx — Excel-версия
```

Код — MIT. Данные моделей — из публичных репозиториев Strata и Project Maya.
