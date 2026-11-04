# -*- coding: utf-8 -*-
"""Собирает Excel-калькулятор из ai_calc.py, подставляя данные из db.py."""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from db import GPU_ROWS, PLATFORMS  # noqa: E402

src_path = os.path.join(HERE, "ai_calc.py")
src = io.open(src_path, encoding="utf-8").read()

start = src.index("# ================================================================ данные")
end = src.index("# ================================================================ Инструкция")
patched = src[:start] + "from db import GPU_ROWS, PLATFORMS, PSUS, CASES, MODELS, SSDS, SSD_DEFAULT, avito_url, avito_price, avito_note, gpu_arch, strata_factor\n\n" + src[end:]

patched = patched.replace("6 платформ: SP3, AM5, LGA4677, LGA4189, LGA3647, TR5",
                          "%d платформ: %s" % (len(PLATFORMS), ", ".join(p["name"] for p in PLATFORMS)))
patched = patched.replace("20 карт в базе", "%d карт в базе" % len(GPU_ROWS))
patched = patched.replace("6 платформ, расширенная база железа",
                          "%d платформ, %d GPU" % (len(PLATFORMS), len(GPU_ROWS)))

code = compile(patched, "ai_calc_from_db.py", "exec")
exec(code, {"__name__": "__main__"})
