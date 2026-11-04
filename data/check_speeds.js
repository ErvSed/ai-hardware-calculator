// Сверка модели с известными замерами: где расходится — видно сразу.
const DB = require("./site/data.js");
global.DB = DB;
const Calc = require("./site/calc.js");

function mk(gpuName, count, cpuName, ramName, platformName) {
  const plat = DB.platforms.find(p => p.name === (platformName || "SP3"));
  return {
    platform: plat,
    cpu: plat.cpus.find(c => c.name === (cpuName || "AMD EPYC 7402")) || plat.cpus[0],
    mb: plat.mbs[0],
    ram: plat.rams.find(r => r.name === (ramName || "8×32 ГБ DDR4-3200 ECC RDIMM")) || plat.rams[0],
    gpu: DB.gpus.find(g => g.name === gpuName),
    count: count,
    psu: DB.psus[0],
    case: DB.cases[0],
    ssd: DB.ssds[0],
    models: DB.models,
  };
}

const cases = [
  ["R9700, Strata Q4 (замер 63-64)", "Radeon AI PRO R9700 32 ГБ", 1, null, null, "Qwen3.8-Flash UD-Q4_K_XL", 63.5],
  ["2×2080 Ti, Strata IQ4_XS (замер 52-58)", "RTX 2080 Ti 22 ГБ (мод)", 2, null, null, "Qwen3.8-Flash UD-IQ4_XS", 55],
  ["1×5090, Strata Q4 (PR #1617: 109,7)", "RTX 5090 32 ГБ", 1, null, null, "Qwen3.8-Flash UD-Q4_K_XL", 109.7],
  ["5090+5060Ti, Basalt NVFP4 (274)", "RTX 5090 32 ГБ", 1, null, null, "Qwen3.8-Flash Basalt NVFP4-DQ6_K", 274],
  ["3×5090, Basalt NVFP4 (форум 406)", "RTX 5090 32 ГБ", 3, null, null, "Qwen3.8-Flash Basalt NVFP4-DQ6_K", 406],
  ["2×3090, Maya-L (замер 30,2)", "RTX 3090 24 ГБ", 2, null, null, "GLM-5.3-Flash Maya-L", 30.2],
  ["1×5090, Maya-M (замер 30+)", "RTX 5090 32 ГБ", 1, null, null, "GLM-5.3-Flash Maya-M", 30],
];

let bad = 0;
cases.forEach(([label, gpu, n, cpu, ram, model, ref]) => {
  const r = Calc.build(mk(gpu, n, cpu, ram));
  const m = r.models.find(x => x.name === model);
  const val = m ? m.decode : null;
  const dev = val ? (val - ref) / ref * 100 : null;
  const ok = dev !== null && Math.abs(dev) < 30;
  if (!ok) bad++;
  console.log((ok ? "OK  " : "MISS") + " " + label.padEnd(42) +
    " модель: " + (val == null ? "—" : val.toFixed(1)) + "  замер: " + ref +
    (dev === null ? "" : "  (" + (dev > 0 ? "+" : "") + dev.toFixed(0) + "%)"));
});
console.log("\nрасхождений >30%: " + bad + " из " + cases.length);

console.log("\nдля справки (те же карты, остальные модели):");
[["1×5090", "RTX 5090 32 ГБ", 1], ["2×3090", "RTX 3090 24 ГБ", 2], ["2×2080 Ti", "RTX 2080 Ti 22 ГБ (мод)", 2]].forEach(([l, g, n]) => {
  const r = Calc.build(mk(g, n));
  console.log("  " + l.padEnd(10) + r.models.map(m => m.name.split(" ")[0].replace("Qwen3.8-Flash", "Q") + "=" + (m.decode == null ? "—" : m.decode.toFixed(0))).join("  "));
});
