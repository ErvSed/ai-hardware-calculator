/* Экспорт расчёта в настоящий .xlsx без внешних библиотек.
   Собираем OOXML (workbook, styles, worksheets) и упаковываем в ZIP (без сжатия). */
(function (root) {
  "use strict";

  // ---------- ZIP ----------
  var CRC = (function () {
    var t = new Int32Array(256);
    for (var n = 0; n < 256; n++) {
      var c = n;
      for (var k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
      t[n] = c;
    }
    return t;
  })();

  function crc32(buf) {
    var c = -1;
    for (var i = 0; i < buf.length; i++) c = CRC[(c ^ buf[i]) & 0xFF] ^ (c >>> 8);
    return (c ^ -1) >>> 0;
  }

  function utf8(str) {
    if (typeof TextEncoder !== "undefined") return new TextEncoder().encode(str);
    var out = [], i, c;
    for (i = 0; i < str.length; i++) {
      c = str.charCodeAt(i);
      if (c < 0x80) out.push(c);
      else if (c < 0x800) out.push(0xC0 | (c >> 6), 0x80 | (c & 63));
      else out.push(0xE0 | (c >> 12), 0x80 | ((c >> 6) & 63), 0x80 | (c & 63));
    }
    return new Uint8Array(out);
  }

  function zipStore(files) {
    var parts = [], central = [], offset = 0, i;
    files.forEach(function (f) {
      var name = utf8(f.name);
      var data = typeof f.data === "string" ? utf8(f.data) : f.data;
      var crc = crc32(data);
      var lh = new Uint8Array(30 + name.length);
      var dv = new DataView(lh.buffer);
      dv.setUint32(0, 0x04034b50, true);
      dv.setUint16(4, 20, true);
      dv.setUint16(6, 0x0800, true); // UTF-8 имена
      dv.setUint16(8, 0, true);      // метод: store
      dv.setUint16(10, 0, true);
      dv.setUint16(12, 0, true);
      dv.setUint32(14, crc, true);
      dv.setUint32(18, data.length, true);
      dv.setUint32(22, data.length, true);
      dv.setUint16(26, name.length, true);
      dv.setUint16(28, 0, true);
      lh.set(name, 30);
      parts.push(lh, data);

      var ch = new Uint8Array(46 + name.length);
      var cv = new DataView(ch.buffer);
      cv.setUint32(0, 0x02014b50, true);
      cv.setUint16(4, 20, true);
      cv.setUint16(6, 20, true);
      cv.setUint16(8, 0x0800, true);
      cv.setUint16(10, 0, true);
      cv.setUint16(12, 0, true);
      cv.setUint16(14, 0, true);
      cv.setUint32(16, crc, true);
      cv.setUint32(20, data.length, true);
      cv.setUint32(24, data.length, true);
      cv.setUint16(28, name.length, true);
      cv.setUint16(30, 0, true);
      cv.setUint16(32, 0, true);
      cv.setUint16(34, 0, true);
      cv.setUint16(36, 0, true);
      cv.setUint32(38, 0, true);
      cv.setUint32(42, offset, true);
      ch.set(name, 46);
      central.push(ch);
      offset += lh.length + data.length;
    });

    var cdSize = central.reduce(function (s, x) { return s + x.length; }, 0);
    var eocd = new Uint8Array(22);
    var ev = new DataView(eocd.buffer);
    ev.setUint32(0, 0x06054b50, true);
    ev.setUint16(8, files.length, true);
    ev.setUint16(10, files.length, true);
    ev.setUint32(12, cdSize, true);
    ev.setUint32(16, offset, true);
    var all = parts.concat(central, [eocd]);

    var total = all.reduce(function (s, x) { return s + x.length; }, 0);
    var out = new Uint8Array(total), pos = 0;
    all.forEach(function (x) { out.set(x, pos); pos += x.length; });
    return out;
  }

  // ---------- OOXML ----------
  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/\u0000-\u0008|\u000B|\u000C|\u000E-\u001F/g, "");
  }

  function colName(n) {
    var s = "";
    while (n > 0) { var m = (n - 1) % 26; s = String.fromCharCode(65 + m) + s; n = Math.floor((n - 1) / 26); }
    return s;
  }

  var STYLES = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' +
    '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">' +
    '<numFmts count="2"><numFmt numFmtId="164" formatCode="#,##0&quot; \u20bd&quot;"/>' +
    '<numFmt numFmtId="165" formatCode="#,##0.0"/></numFmts>' +
    '<fonts count="3">' +
    '<font><sz val="11"/><name val="Calibri"/></font>' +
    '<font><b/><sz val="11"/><name val="Calibri"/></font>' +
    '<font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>' +
    '</fonts>' +
    '<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>' +
    '<fill><patternFill patternType="solid"><fgColor rgb="FF1B5E20"/><bgColor indexed="64"/></patternFill></fill></fills>' +
    '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>' +
    '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>' +
    '<cellXfs count="7">' +
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>' +                                    // 0 обычный
    '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>' +                      // 1 жирный
    '<xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>' +            // 2 деньги
    '<xf numFmtId="165" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1"/>' +            // 3 число .0
    '<xf numFmtId="0" fontId="2" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/>' +        // 4 шапка
    '<xf numFmtId="164" fontId="1" fillId="0" borderId="0" xfId="0" applyNumberFormat="1" applyFont="1"/>' + // 5 итог
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>' + // 6 перенос
    '</cellXfs>' +
    '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>' +
    '</styleSheet>';

  // лист: {name, cols:[width], rows:[[{v,s,t}]]}
  function sheetXml(sheet) {
    var xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' +
      '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">';
    if (sheet.cols && sheet.cols.length) {
      xml += "<cols>";
      sheet.cols.forEach(function (w, i) {
        xml += '<col min="' + (i + 1) + '" max="' + (i + 1) + '" width="' + w + '" customWidth="1"/>';
      });
      xml += "</cols>";
    }
    xml += "<sheetData>";
    sheet.rows.forEach(function (row, ri) {
      xml += '<row r="' + (ri + 1) + '">';
      row.forEach(function (cell, ci) {
        if (cell === null || cell === undefined || cell === "") return;
        var v = typeof cell === "object" ? cell.v : cell;
        var s = typeof cell === "object" ? (cell.s || 0) : 0;
        if (v === null || v === undefined || v === "") return;
        var ref = colName(ci + 1) + (ri + 1);
        if (typeof v === "number" && isFinite(v)) {
          xml += '<c r="' + ref + '"' + (s ? ' s="' + s + '"' : "") + "><v>" + v + "</v></c>";
        } else {
          xml += '<c r="' + ref + '" t="inlineStr"' + (s ? ' s="' + s + '"' : "") +
            "><is><t>" + esc(v) + "</t></is></c>";
        }
      });
      xml += "</row>";
    });
    xml += "</sheetData></worksheet>";
    return xml;
  }

  function build(sheets) {
    var files = [
      { name: "[Content_Types].xml", data: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' +
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">' +
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>' +
        '<Default Extension="xml" ContentType="application/xml"/>' +
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>' +
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>' +
        sheets.map(function (s, i) {
          return '<Override PartName="/xl/worksheets/sheet' + (i + 1) + '.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>';
        }).join("") +
        "</Types>" },
      { name: "_rels/.rels", data: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' +
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' +
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>' +
        "</Relationships>" },
      { name: "xl/workbook.xml", data: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' +
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" ' +
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>' +
        sheets.map(function (s, i) {
          return '<sheet name="' + esc(s.name) + '" sheetId="' + (i + 1) + '" r:id="rId' + (i + 1) + '"/>';
        }).join("") + "</sheets></workbook>" },
      { name: "xl/_rels/workbook.xml.rels", data: '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' +
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' +
        sheets.map(function (s, i) {
          return '<Relationship Id="rId' + (i + 1) + '" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet' + (i + 1) + '.xml"/>';
        }).join("") +
        '<Relationship Id="rId' + (sheets.length + 1) + '" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>' +
        "</Relationships>" },
      { name: "xl/styles.xml", data: STYLES }
    ];
    sheets.forEach(function (s, i) { files.push({ name: "xl/worksheets/sheet" + (i + 1) + ".xml", data: sheetXml(s) }); });
    return zipStore(files);
  }

  // ---------- данные расчёта ----------
  function money(v) { return Math.round(v); }
  function dateStr() {
    var d = new Date();
    return ("0" + d.getDate()).slice(-2) + "." + ("0" + (d.getMonth() + 1)).slice(-2) + "." + d.getFullYear();
  }

  function buildSheets(sel, r) {
    var H = 4, B = 1, M = 2, N = 3, T = 5, W = 6;
    var smeta = [];
    smeta.push([{ v: "Смета сборки", s: 1 }, null, null, { v: dateStr(), s: 0 }]);
    smeta.push([{ v: "Платформа: " + sel.platform.title, s: 0 }]);
    smeta.push([]);
    smeta.push([{ v: "Позиция", s: H }, { v: "Модель", s: H }, { v: "Цена, ₽", s: H }, { v: "Авито", s: H }]);
    var rows = [
      ["CPU", sel.cpu.name, sel.cpu.price, sel.cpu.avitoUrl],
      ["Материнская плата", sel.mb.name, sel.mb.price, sel.mb.avitoUrl],
      ["Память", sel.ram.name, sel.ram.price, sel.ram.avitoUrl],
      ["Видеокарты", sel.gpu.name + " × " + r.count, sel.gpu.price * r.count, sel.gpu.avitoUrl],
      ["Блок питания", sel.psu.name, sel.psu.price, sel.psu.avitoUrl],
      ["Корпус", sel["case"].name, sel["case"].price, sel["case"].avitoUrl]
    ];
    if (sel.ssd) rows.push(["Накопитель", sel.ssd.name, sel.ssd.price, sel.ssd.avitoUrl]);
    rows.forEach(function (x) {
      smeta.push([{ v: x[0] }, { v: x[1], s: W }, { v: money(x[2]), s: M }, { v: x[3] || "" }]);
    });
    smeta.push([{ v: "ИТОГО", s: 1 }, null, { v: money(r.price), s: T }, null]);
    smeta.push([]);

    smeta.push([{ v: "Параметры сборки", s: 1 }]);
    smeta.push([{ v: "VRAM, ГБ" }, { v: r.vram }]);
    smeta.push([{ v: "Полоса VRAM, ГБ/с" }, { v: Math.round(r.bwVram) }]);
    smeta.push([{ v: "Полоса RAM, ГБ/с" }, { v: r.bwRam }]);
    smeta.push([{ v: "Compute (отн. 3090)" }, { v: Math.round(r.compute * 100) / 100, s: N }]);
    smeta.push([{ v: "Потребление, Вт" }, { v: Math.round(r.power) }]);
    smeta.push([{ v: "Рекомендуемый БП, Вт" }, { v: r.psuNeed }]);
    smeta.push([{ v: "Контекст, токенов" }, { v: r.ctx }]);
    smeta.push([{ v: "KV-кэш контекста, ГБ" }, { v: Math.round((sel.models[0].kvRate || 0.1) * r.ctx / 1000 * 10) / 10, s: N }]);
    smeta.push([]);

    var d = sel["case"].dims || [];
    smeta.push([{ v: "Габариты", s: 1 }]);
    if (d.length) {
      smeta.push([{ v: "Корпус Ш×В×Г, мм" }, { v: d[0] + "×" + d[1] + "×" + d[2] }]);
      smeta.push([{ v: "Объём, л" }, { v: Math.round(d[0] * d[1] * d[2] / 1e6 * 10) / 10, s: N }]);
      smeta.push([{ v: "Вес, кг" }, { v: d[3], s: N }]);
    }
    smeta.push([{ v: "Длина карты, мм" }, { v: sel.gpu.len }]);
    smeta.push([{ v: "Слотов на карту" }, { v: sel.gpu.slots }]);
    smeta.push([]);

    smeta.push([{ v: "Совместимость", s: 1 }]);
    r.checks.forEach(function (c) { smeta.push([{ v: c.name }, { v: c.ok ? "OK" : c.msg }]); });
    smeta.push([{ v: "Поддержка моделей" }, { v: r.vendorOk }]);

    var speed = [];
    speed.push([{ v: "Скорость по моделям", s: 1 }, null, null, { v: dateStr(), s: 0 }]);
    speed.push([{ v: "Сборка: " + r.count + "× " + sel.gpu.name + " + " + sel.cpu.name, s: 0 }]);
    speed.push([]);
    speed.push([{ v: "Модель", s: H }, { v: "Движок", s: H }, { v: "Доля в VRAM", s: H },
      { v: "Декод, ток/с", s: H }, { v: "Префилл, ток/с", s: H }, { v: "Ограничитель", s: H }]);
    r.models.forEach(function (m) {
      speed.push([
        { v: m.name }, { v: m.engine },
        { v: Math.round(m.s * 100) / 100, s: N },
        m.blocked ? { v: m.reason || "недоступно" } : { v: Math.round(m.decode * 10) / 10, s: N },
        m.blocked ? { v: "—" } : { v: Math.round(m.prefill) },
        { v: m.lim }
      ]);
    });
    speed.push([]);
    speed.push([{ v: "Оценка: ±25 % декод, ±35 % префилл. Цены — медианы объявлений Авито (СПб) и магазины, ноябрь 2026.", s: W }]);

    return [
      { name: "Смета", cols: [26, 46, 16, 52], rows: smeta },
      { name: "Скорость", cols: [38, 14, 14, 16, 16, 24], rows: speed }
    ];
  }

  function fileName(sel, r) {
    var clean = function (s) { return String(s).replace(/[\\/:*?"<>|]/g, "").replace(/\s+/g, "-"); };
    return "raschet-" + clean(sel.gpu.name) + "x" + r.count + "-" + clean(sel.cpu.name) + ".xlsx";
  }

  function download(sel, r) {
    var data = build(buildSheets(sel, r));
    var blob = new Blob([data], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = fileName(sel, r);
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 2000);
    return data.length;
  }

  var api = { build: build, buildSheets: buildSheets, download: download, zipStore: zipStore, fileName: fileName };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.Xlsx = api;
})(typeof window !== "undefined" ? window : globalThis);
