/* Модель расчёта: декод и префилл по опорным точкам (см. лист «Модели» в Excel).
   Работает и в браузере, и в Node (для тестов). */
(function (root) {
  "use strict";

  function clamp(x, a, b) { return Math.max(a, Math.min(b, x)); }

  // доля весов экспертов, поместившаяся в VRAM (минус плотные веса и KV-кэш контекста)
  function sShare(vram, dense, kv, size) {
    return clamp((vram - dense - kv) / (size - dense), 0, 1);
  }

  function denom(s, bwVram, bwRam) { return s * bwVram + (1 - s) * bwRam; }

  // опорная точка замерена при своём контексте (~2 ГБ KV) — её доля фиксирована
  function anchorDenom(m) { return denom(sShare(m.aVram, m.dense, 2, m.size), m.aBw, m.aRam); }

  function decode(m, vram, bwVram, bwRam, kv) {
    var s = sShare(vram, m.dense, kv, m.size);
    var d = denom(s, bwVram, bwRam);
    return m.aDec * Math.pow(d / anchorDenom(m), m.exp);
  }

  function prefill(m, compute, bwRam) {
    return m.aPP * Math.pow(compute / m.aComp, 0.35) * Math.pow(bwRam / m.aRam, 0.2);
  }

  function requiresNvidia(m) { return m.engine === "Maya" || m.engine === "Maya-ds4"; }
  function requiresBlackwell(m) { return m.engine === "Basalt"; }

  // полный расчёт сборки
  function build(sel) {
    var gpu = sel.gpu, n = sel.count, cpu = sel.cpu, mb = sel.mb, ram = sel.ram;
    var ctx = sel.ctx || 32768;
    var vram = gpu.vram * n, bwVram = gpu.bw * n, compute = gpu.comp * n;
    var bwRam = cpu.bw;
    var price = gpu.price * n + cpu.price + mb.price + ram.price + sel.psu.price + sel.case.price +
      ((sel.ssd && sel.ssd.price) || 0);
    var power = gpu.tdp * n * 1.1 + cpu.tdp * 1.3 + 100;
    var psuNeed = Math.ceil(power / 0.75 / 50) * 50;

    var models = sel.models.map(function (m) {
      var maya = requiresNvidia(m);
      var blackwell = requiresBlackwell(m);
      var blk = (maya && gpu.vendor !== "NVIDIA") || (blackwell && gpu.arch !== "Blackwell");
      var kv = (m.kvRate || 0.1) * ctx / 1000;
      var dec = blk ? null : decode(m, vram, bwVram, bwRam, kv);
      var pp = blk ? null : prefill(m, compute, bwRam);
      if (!blk && m.engine === "Strata") dec *= (gpu.kStrata || 1);
      var s = sShare(vram, m.dense, kv, m.size);
      return {
        name: m.name, engine: m.engine, s: s, decode: dec, prefill: pp, blocked: blk,
        reason: blk ? (maya ? "нет NVIDIA" : "нужен Blackwell") : null,
        lim: s > 0.8 ? "всё в VRAM" : (s > 0.3 ? "VRAM + RAM-ярус" : "упирается в RAM/SSD"),
      };
    });

    var checks = [
      { name: "Сокет CPU = сокет платы", ok: !!(sel.platform && mb.platform === sel.platform.name && cpu.platform === sel.platform.name), msg: "разные сокеты" },
      { name: "Тип памяти совпадает с платой", ok: mb.ram === ram.type, msg: "не совпадает" },
      { name: "Число GPU ≤ слотов PCIe", ok: n <= mb.slots, msg: "не хватит слотов" },
      { name: "Длина карты ≤ корпуса", ok: gpu.len <= sel.case.len, msg: "не влезет" },
      { name: "Мощности БП хватает", ok: sel.psu.w >= psuNeed, msg: "БП слабый" },
      { name: "Слотов GPU у корпуса хватает", ok: n <= sel.case.slots, msg: "мало слотов" },
    ];

    return {
      vram: vram, bwVram: bwVram, compute: compute, bwRam: bwRam,
      price: price, power: power, psuNeed: psuNeed,
      models: models, checks: checks, count: n, ctx: ctx,
      vendorOk: gpu.vendor === "NVIDIA" ? "NVIDIA — все модели" : gpu.vendor + " — только Strata (Qwen)",
    };
  }

  // таблица «максимум»: все карты × 1..4 на текущей платформе
  function maxTable(sel) {
    var DBx = root.DB;
    var rows = [];
    DBx.gpus.forEach(function (g) {
      [1, 2, 3, 4].forEach(function (n) {
        var s2 = Object.assign({}, sel, { gpu: g, count: n });
        var r = build(s2);
        var glm = r.models[0], qwen = r.models[2];
        rows.push({
          gpu: g.name, n: n, vram: r.vram, bwVram: r.bwVram, compute: r.compute,
          price: r.price, glmDec: glm.decode, glmPP: glm.prefill,
          qwenDec: qwen.decode, qwenPP: qwen.prefill,
          perGlm: glm.decode ? r.price / glm.decode : null,
          perQwen: qwen.decode ? r.price / qwen.decode : null,
          fits: n <= sel.mb.slots,
        });
      });
    });
    return rows;
  }

  var api = { build: build, maxTable: maxTable, sShare: sShare, decode: decode, prefill: prefill, requiresNvidia: requiresNvidia, requiresBlackwell: requiresBlackwell };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.Calc = api;
})(typeof window !== "undefined" ? window : globalThis);
