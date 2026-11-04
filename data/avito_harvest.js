// Сбор реальных цен с Авито через запущенную Opera (CDP, порт 9222).
// Запуск: node avito_harvest.js [--kind gpu] [--limit 10]
const fs = require("fs");
const http = require("http");
const path = require("path");

const HERE = __dirname;
const OUT = path.join(HERE, "avito_prices.json");
const MANIFEST = path.join(HERE, "avito_queries.json");

const args = process.argv.slice(2);
const getArg = (name) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : null; };
const KIND = getArg("--kind");
const ONLY = getArg("--only");
const LIMIT = parseInt(getArg("--limit") || "0", 10);

const JUNK = /скупк|обмен|нерабоч|не\s*работ|битая|битый|битую|на\s*запчаст|донор|ремонт|только\s*корпус|без\s*чипа|не\s*включается|неисправ|неработоспособ|под\s*восстановлен|восстановлен|запчаст|аренда|прокат|в\s*рассрочку|только\s*плата|выкуп/i;

// целые машины вместо запчасти — только для комплектующих, не для БП/корпусов
const WHOLE = /рабочая\s*станция|системный\s*блок|моноблок|ноутбук|компьютер\s*в\s*сборе|сервер\b/i;

// модель, которую ищем: число модели + значимые слова (Ada, Blackwell, Ti, Super, XT...)
function modelFilter(query) {
  const pure = (query.match(/\b\d{3,4}\b/g) || []);
  const digits = (query.match(/\d{3,5}/g) || []);
  const token = pure.length ? pure[0] : (digits.length ? digits.sort((a, b) => b.length - a.length)[0] : null);
  const quals = (query.match(/\b(Ada|Blackwell|Ti|Super|PRO|XTX|XT|Max-Q|R9700|A6000|A5000|A4000|A4500|V100|P40|P100|T4)\b/gi) || [])
    .map((s) => s.toLowerCase());
  return { token, quals: [...new Set(quals)] };
}
function matchesModel(title, f) {
  const t = title.toLowerCase();
  if (f.token && !t.includes(String(f.token).toLowerCase())) return false;
  for (const q of f.quals) {
    if (["pro", "ti", "super", "xt", "xtx"].includes(q)) continue; // слишком общие — не требуем
    if (!t.includes(q)) return false;
  }
  return true;
}

const EXTRACT = `
(() => {
  const items = [...document.querySelectorAll('[data-marker="item"]')];
  const out = items.slice(0, 50).map(e => {
    const a = e.querySelector('a[data-marker="item-title"]') || e.querySelector('a');
    const meta = e.querySelector('meta[itemprop="price"]');
    const priceEl = e.querySelector('[data-marker="item-price"]') || e.querySelector('[itemprop="price"]');
    const priceRaw = (meta && meta.getAttribute('content')) || (priceEl ? priceEl.textContent : '');
    const titleEl = e.querySelector('[itemprop="name"]') || e.querySelector('[data-marker="item-title"]');
    const dateEl = e.querySelector('[data-marker="item-date"]');
    return {
      title: titleEl ? titleEl.textContent.trim().slice(0, 120) : '',
      priceRaw: String(priceRaw || ''),
      date: dateEl ? dateEl.textContent.trim() : '',
      url: a ? a.href.split('?')[0] : ''
    };
  });
  return JSON.stringify({url: location.href, title: document.title, count: items.length,
                         body: document.body.innerText.slice(0, 400), items: out});
})()`;

function getJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (r) => {
      let d = "";
      r.on("data", (c) => (d += c));
      r.on("end", () => { try { resolve(JSON.parse(d)); } catch (e) { reject(e); } });
    }).on("error", reject);
  });
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function parsePrice(s) {
  const m = String(s).replace(/\u00a0|\u2009|\s/g, "").match(/(\d{4,9})/);
  return m ? parseInt(m[1], 10) : null;
}
function quantile(arr, q) {
  if (!arr.length) return null;
  const a = [...arr].sort((x, y) => x - y);
  const pos = (a.length - 1) * q;
  const lo = Math.floor(pos), hi = Math.ceil(pos);
  return Math.round(a[lo] + (a[hi] - a[lo]) * (pos - lo));
}

(async () => {
  const manifest = JSON.parse(fs.readFileSync(MANIFEST, "utf8"));
  const results = fs.existsSync(OUT) ? JSON.parse(fs.readFileSync(OUT, "utf8")) : {};
  const onlySet = ONLY ? new Set(ONLY.split("|")) : null;
  const todo = manifest.filter((m) => (!KIND || m.kind === KIND) &&
    (onlySet ? onlySet.has(m.name) : !results[m.name]));
  const list = LIMIT > 0 ? todo.slice(0, LIMIT) : todo;
  if (onlySet) onlySet.forEach((n) => { delete results[n]; });
  console.log("к обработке:", list.length, "из", manifest.length);

  const targets = await getJson("http://127.0.0.1:9222/json/list");
  const page = targets.find((t) => t.type === "page");
  if (!page) { console.log("нет страницы в Opera"); process.exit(1); }

  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let id = 0;
  const pending = new Map();
  ws.onmessage = (ev) => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  };
  const send = (method, params) => new Promise((res) => {
    const myId = ++id;
    pending.set(myId, res);
    ws.send(JSON.stringify({ id: myId, method, params: params || {} }));
  });
  await new Promise((r) => (ws.onopen = r));
  const evaluate = async (expr) => {
    const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true });
    return r.result && r.result.result ? r.result.result.value : null;
  };

  for (let i = 0; i < list.length; i++) {
    const item = list[i];
    const url = "https://www.avito.ru/sankt-peterburg?q=" + encodeURIComponent(item.query);
    await send("Page.navigate", { url });
    let data = null;
    for (let t = 0; t < 10; t++) {
      await sleep(1500);
      const raw = await evaluate(EXTRACT);
      if (typeof raw === "string") { try { data = JSON.parse(raw); } catch (e) {} }
      if (data && data.count > 0) break;
      if (data && /проверка безопасности|доступ ограничен|робот/i.test(data.title + data.body)) { data = null; break; }
    }
    if (!data || data.count === 0) {
      // возможная проверка — пауза и один повтор
      await sleep(25000);
      await send("Page.navigate", { url });
      await sleep(6000);
      const raw = await evaluate(EXTRACT);
      if (typeof raw === "string") { try { data = JSON.parse(raw); } catch (e) {} }
    }
    if (!data || !data.count) {
      results[item.name] = { kind: item.kind, query: item.query, status: "blocked_or_empty", ts: new Date().toISOString() };
      fs.writeFileSync(OUT, JSON.stringify(results, null, 1), "utf8");
      console.log(`[${i + 1}/${list.length}] ${item.name}: нет данных`);
      await sleep(15000);
      continue;
    }
    const prices = [];
    const samples = [];
    const mf = modelFilter(item.query);
    (data.items || []).forEach((it) => {
      const p = parsePrice(it.priceRaw);
      if (!p) return;
      if (JUNK.test(it.title)) return;
      if (item.kind !== "psu" && item.kind !== "case" && WHOLE.test(it.title)) return;
      if (!matchesModel(it.title, mf)) return;
      if (p < 1000 || p > 6000000) return;
      prices.push(p);
      samples.push({ price: p, title: it.title, date: it.date, url: it.url });
    });
    const med = quantile(prices, 0.5);
    const clean = prices.filter((p) => med ? p >= med * 0.4 && p <= med * 2.5 : true);
    results[item.name] = {
      kind: item.kind, query: item.query, status: "ok",
      ads_total: data.count, ads_used: prices.length, ads_clean: clean.length,
      min: clean.length ? Math.min(...clean) : null,
      p25: quantile(clean, 0.25),
      median: quantile(clean, 0.5),
      p75: quantile(clean, 0.75),
      max: clean.length ? Math.max(...clean) : null,
      estimate: item.estimate,
      samples: samples.slice(0, 5),
      url: data.url,
      ts: new Date().toISOString()
    };
    fs.writeFileSync(OUT, JSON.stringify(results, null, 1), "utf8");
    console.log(`[${i + 1}/${list.length}] ${item.name}: n=${clean.length} медиана ${results[item.name].median} ₽ (${results[item.name].min}–${results[item.name].max})`);
    await sleep(2500);
  }
  console.log("готово, файл:", OUT);
  ws.close();
  process.exit(0);
})().catch((e) => { console.log("ERR", e.message); process.exit(1); });
