// Проверка ядра расчёта: сравниваем с числами Excel для дефолтной сборки.
const DB = require("./data.js");
global.DB = DB;
const Calc = require("./calc.js");

const plat = DB.platforms.find(p => p.name === "SP3");
const sel = {
  platform: plat,
  cpu: plat.cpus.find(c => c.name === "AMD EPYC 7402"),
  mb: plat.mbs.find(m => m.name === "Supermicro H12SSL-I-B"),
  ram: plat.rams.find(r => r.name.indexOf("DDR4-3200 ECC") > 0),
  gpu: DB.gpus.find(g => g.name === "RTX 3090 24 ГБ"),
  count: 2,
  psu: DB.psus[0],
  case: DB.cases[0],
  models: DB.models,
};

const r = Calc.build(sel);
console.log("vendor:", r.vendorOk);
console.log("vram", r.vram, "bw", r.bwVram, "ram", r.bwRam, "compute", r.compute);
console.log("price", r.price, "power", Math.round(r.power), "psuNeed", r.psuNeed);
console.log("checks:", r.checks.map(c => (c.ok ? "OK" : c.msg)).join(" | "));
console.log("--- models ---");
r.models.forEach(m => console.log(m.name.padEnd(30), "s=" + m.s.toFixed(3),
  "decode=" + (m.decode == null ? "—" : m.decode.toFixed(2)),
  "prefill=" + (m.prefill == null ? "—" : m.prefill.toFixed(0))));

const expect = { "GLM-5.3-Flash Maya-L": [30.2, 801], "GLM-5.3-Flash Maya-M": [37.72, 1362.5],
  "Qwen3.8-Flash UD-Q4_K_XL": [73.72, 1381.36], "Qwen3.8-Flash UD-IQ4_XS": [58.03, 960.15],
  "DeepSeek-V4.1-Flash Maya-S": [30.44, 1943.38] };
let bad = 0;
r.models.forEach(m => {
  const e = expect[m.name];
  if (!e) return;
  const dd = Math.abs(m.decode - e[0]) / e[0];
  const dp = Math.abs(m.prefill - e[1]) / e[1];
  const ok = dd < 0.01 && dp < 0.01;
  if (!ok) bad++;
  console.log((ok ? "OK  " : "FAIL") + " " + m.name, "decode", m.decode.toFixed(2), "vs", e[0], "| prefill", m.prefill.toFixed(0), "vs", e[1]);
});
console.log("mismatches:", bad);

const rows = Calc.maxTable(sel);
console.log("max rows:", rows.length, "| fits:", rows.filter(x => x.fits).length);
rows.sort((a, b) => (b.glmDec || 0) - (a.glmDec || 0));
console.log("top decode:", rows.slice(0, 3).map(x => x.gpu + " ×" + x.n + " = " + x.glmDec.toFixed(1)));
rows.sort((a, b) => (a.perGlm || 1e12) - (b.perGlm || 1e12));
console.log("top per-tok/s:", rows.slice(0, 3).map(x => x.gpu + " ×" + x.n + " = " + Math.round(x.perGlm)));
