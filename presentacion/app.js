(() => {
  'use strict';

  const C = { black: '#0B0B12', white: '#FFFFFF', soft: '#D9D9E3', orange: '#FF9F1C' };
  const VERDICTS = {
    confirmado: { label: 'CONFIRMADO', en: 'CONFIRMED', fate: 'su creencia se sostiene' },
    plausible: { label: 'PLAUSIBLE', en: 'PLAUSIBLE', fate: 'su creencia queda a medias' },
    desmentido: { label: 'DESMENTIDO', en: 'BUSTED', fate: 'su creencia cae' },
  };
  const ORDER = ['confirmado', 'plausible', 'desmentido'];

  const TEAMS = [
    { name: 'Los Yunques Tecnológicos', short: 'Yunques', focus: 'Adopción y experiencia' },
    { name: 'Los Correcaminos Analíticos', short: 'Correcaminos', focus: 'Innovación y escalamiento' },
    { name: 'Los Cazadores de Mitos', short: 'Cazadores', focus: 'Eficiencia y transformación' },
  ];

  const fmt = (v, d = 2) => v.toFixed(d).replace('.', ',');
  const pad2 = (n) => String(n).padStart(2, '0');

  /* ================= Gráficos SVG ================= */
  const NS = 'http://www.w3.org/2000/svg';
  function E(tag, attrs, parent, text) {
    const e = document.createElementNS(NS, tag);
    if (attrs) for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    if (parent) parent.appendChild(e);
    return e;
  }
  function svg(host, w, h, label) {
    host.innerHTML = '';
    return E('svg', { viewBox: `0 0 ${w} ${h}`, class: 'chart', role: 'img', 'aria-label': label }, host);
  }
  function multiline(parent, x, y, arr, cls, lh, anchor = 'middle') {
    const t = E('text', { x, y, class: cls, 'text-anchor': anchor }, parent);
    arr.forEach((s, i) => E('tspan', { x, dy: i ? lh : 0 }, t, s));
    return t;
  }
  const delay = (ms) => `animation-delay:${ms}ms`;

  function refLine(s, x1, y1, x2, y2) {
    E('line', { x1, y1, x2, y2, class: 'ref-line' }, s);
  }

  function hbar(host, o) {
    const w = 1040, h = 540, lw = o.labelW || 260, right = 100;
    const top = o.avg != null ? 66 : 24;
    const bottom = o.ticks ? 78 : 54;
    const [d0, d1] = o.domain;
    const pw = w - lw - right, ph = h - top - bottom;
    const x = (v) => lw + (v - d0) / (d1 - d0) * pw;
    const s = svg(host, w, h, o.aria);
    (o.ticks || []).forEach((t) => {
      E('line', { x1: x(t), x2: x(t), y1: top, y2: top + ph, class: 'grid' }, s);
      E('text', { x: x(t), y: top + ph + 38, class: 'tick', 'text-anchor': 'middle' }, s, fmt(t, o.tickDec ?? 0));
    });
    if (o.axisTitle) E('text', { x: lw + pw / 2, y: h - 6, class: o.callout ? 'callout' : 'axis-title', 'text-anchor': 'middle' }, s, o.axisTitle);
    const band = ph / o.rows.length, bh = Math.min(66, band * 0.64);
    const ys = o.rows.map((r, i) => top + i * band + (band - bh) / 2);
    o.rows.forEach((r, i) => {
      E('rect', {
        x: x(d0), y: ys[i], width: Math.max(0, x(r.v) - x(d0)), height: bh, rx: 4,
        fill: r.c || C.soft, class: 'grow-x', style: delay(i * 90),
        'data-tip': `${r.tip || r.label}\n${o.metric}: ${fmt(r.v)}${r.n ? `\nn = ${r.n}` : ''}`,
      }, s);
    });
    E('line', { x1: x(d0), x2: x(d0), y1: top - 6, y2: top + ph, class: 'base' }, s);
    if (o.avg != null) {
      refLine(s, x(o.avg), top - 10, x(o.avg), top + ph);
      E('text', { x: x(o.avg), y: top - 22, class: 'ref-label', 'text-anchor': 'middle' }, s, `Promedio ACME ${fmt(o.avg)}`);
    }
    o.rows.forEach((r, i) => {
      E('text', { x: lw - 18, y: ys[i] + bh / 2, class: 'cat', 'text-anchor': 'end', 'dominant-baseline': 'central' }, s, r.label);
      E('text', { x: x(r.v) + 14, y: ys[i] + bh / 2, class: 'val fade', 'dominant-baseline': 'central', style: delay(500 + i * 90) }, s, fmt(r.v, o.dec ?? 2));
    });
  }

  function vbar(host, o) {
    const w = 1040, h = 540, left = 30, right = 170, top = 60, bottom = 110;
    const [d0, d1] = o.domain;
    const pw = w - left - right, ph = h - top - bottom;
    const y = (v) => top + ph - (v - d0) / (d1 - d0) * ph;
    const s = svg(host, w, h, o.aria);
    const band = pw / o.rows.length, bw = Math.min(190, band * 0.58);
    o.rows.forEach((r, i) => {
      const cx = left + i * band + band / 2;
      E('rect', {
        x: cx - bw / 2, y: y(r.v), width: bw, height: y(d0) - y(r.v), rx: 4,
        fill: r.c || C.soft, class: 'grow-y', style: delay(i * 120),
        'data-tip': `${r.label.join(' ')}\n${o.metric}: ${fmt(r.v)}\nn = ${r.n}`,
      }, s);
      multiline(s, cx, top + ph + 40, r.label, 'cat', 34);
    });
    E('line', { x1: left, x2: left + pw, y1: y(d0), y2: y(d0), class: 'base' }, s);
    if (o.avg != null) {
      refLine(s, left, y(o.avg), left + pw + 12, y(o.avg));
      multiline(s, left + pw + 22, y(o.avg) - 6, ['Promedio', `ACME ${fmt(o.avg)}`], 'ref-label', 30, 'start');
    }
    o.rows.forEach((r, i) => {
      const cx = left + i * band + band / 2;
      E('text', { x: cx, y: y(r.v) - 18, class: 'val fade', 'text-anchor': 'middle', style: delay(600 + i * 120) }, s, fmt(r.v));
    });
  }

  function lineChart(host, o) {
    const w = 1040, h = 540, left = 30, right = 30, top = 60, bottom = 110;
    const [d0, d1] = o.domain;
    const pw = w - left - right, ph = h - top - bottom;
    const band = pw / o.rows.length;
    const x = (i) => left + i * band + band / 2;
    const y = (v) => top + ph - (v - d0) / (d1 - d0) * ph;
    const s = svg(host, w, h, o.aria);
    E('line', { x1: left, x2: left + pw, y1: y(d0), y2: y(d0), class: 'base' }, s);
    const d = o.rows.map((r, i) => `${i ? 'L' : 'M'}${x(i)},${y(r.v)}`).join(' ');
    E('path', { d, class: 'line draw', pathLength: 1 }, s);
    o.rows.forEach((r, i) => {
      E('circle', {
        cx: x(i), cy: y(r.v), r: 13, fill: r.c || C.soft, stroke: C.black, 'stroke-width': 4, class: 'pop', style: delay(250 + i * 170),
        'data-tip': `${r.label.join(' ')}\n${o.metric}: ${fmt(r.v)}\nn = ${r.n}`,
      }, s);
      E('text', { x: x(i), y: y(r.v) - 30, class: 'val fade', 'text-anchor': 'middle', style: delay(400 + i * 170) }, s, fmt(r.v, 1));
      multiline(s, x(i), top + ph + 40, r.label, 'cat', 32);
    });
  }

  function diverging(host, o) {
    const w = 1040, h = 540, left = 210, right = 210, top = 96, bottom = 20;
    const [d0, d1] = o.domain;
    const pw = w - left - right, ph = h - top - bottom;
    const x = (v) => left + (v - d0) / (d1 - d0) * pw;
    const s = svg(host, w, h, o.aria);
    E('rect', { x: left, y: 12, width: 26, height: 26, fill: C.orange }, s);
    E('text', { x: left + 36, y: 34, class: 'cat' }, s, o.label);
    E('text', { x: left + pw, y: 34, class: 'axis-title', 'text-anchor': 'end' }, s, o.ref);
    E('text', { x: x(4), y: top - 18, class: 'ref-label', 'text-anchor': 'middle' }, s, '4 = neutral');
    const band = ph / o.rows.length, bh = 44;
    o.rows.forEach((r, i) => {
      const by = top + i * band + (band - bh) / 2 + 12;
      const v = r.v, neg = v < 4;
      const x1 = x(Math.min(v, 4)), x2 = x(Math.max(v, 4));
      E('text', { x: left - 18, y: by - 8, class: 'panel-title', 'text-anchor': 'end' }, s, r.name);
      E('text', { x: left - 18, y: by + bh / 2 + 14, class: 'cat-sub', 'text-anchor': 'end', style: 'font-size:28px;fill:#fff' }, s, r.lp);
      E('text', { x: left + pw + 18, y: by + bh / 2 + 14, class: 'cat-sub', style: 'font-size:28px;fill:#fff' }, s, r.rp);
      E('rect', {
        x: x1, y: by, width: x2 - x1, height: bh, rx: 4, fill: C.orange,
        class: neg ? 'grow-x-r' : 'grow-x', style: delay(i * 110),
        'data-tip': `${r.name}
Promedio: ${fmt(v)} (4 = neutral)`,
      }, s);
      E('text', {
        x: neg ? x1 - 12 : x2 + 12, y: by + bh / 2, class: 'val fade', 'dominant-baseline': 'central',
        'text-anchor': neg ? 'end' : 'start', style: delay(500 + i * 110),
      }, s, fmt(v));
    });
    E('line', { x1: x(4), x2: x(4), y1: top - 6, y2: top + ph, stroke: C.white, 'stroke-width': 4 }, s);
  }

  function stacked(host, o) {
    const w = 1040, h = 540, left = 10, right = 10, gap = 4;
    const pw = w - left - right;
    const s = svg(host, w, h, o.aria);
    const rowH = h / o.rows.length;
    o.rows.forEach((row, ri) => {
      const y0 = ri * rowH;
      E('text', { x: left, y: y0 + 40, class: 'cat' }, s, row.title);
      const by = y0 + 62, bh = 104;
      let acc = 0;
      row.parts.forEach((p, pi) => {
        const x0 = left + acc / 100 * pw + (pi ? gap / 2 : 0);
        const ww = p.v / 100 * pw - (pi ? gap / 2 : 0) - (pi < row.parts.length - 1 ? gap / 2 : 0);
        acc += p.v;
        E('rect', {
          x: x0, y: by, width: ww, height: bh, rx: 4, fill: p.c, class: 'grow-x', style: delay(ri * 350 + pi * 120),
          'data-tip': `${row.title}\n${p.label}: ${fmt(p.v, 1)} %`,
        }, s);
        E('text', { x: x0 + ww / 2, y: by + bh / 2, class: 'val-in fade', 'text-anchor': 'middle', 'dominant-baseline': 'central', style: delay(500 + ri * 350 + pi * 120) }, s, `${fmt(p.v, 1)} %`);
        E('text', { x: x0 + ww / 2, y: by + bh + 38, class: 'cat-sub', 'text-anchor': 'middle', style: 'font-size:28px;fill:#fff' }, s, p.label);
      });
    });
  }

  /* ================= Mitos (cifras del tablero, verificadas en el dataset) ================= */
  const GRAY = '#8A8A9A';
  const SENS_ITEMS = [
    { name: 'Densidad', lp: 'Simple', rp: 'Detallada' },
    { name: 'Colores', lp: 'Sobrios', rp: 'Vivos' },
    { name: 'Animación', lp: 'Estática', rp: 'Animada' },
    { name: 'Sonido', lp: 'Sin sonido', rp: 'Con sonido' },
  ];

  const MYTHS = [
    {
      code: 'M1', id: 'edad', section: 'Pulso digital de ACME', verdict: 'desmentido',
      claim: 'Los mayores se resisten a lo digital',
      q: 'Q3 · ¿Qué edad tienes?',
      kicker: 'Utilidad percibida por edad',
      big: '4,40', msg: 'Los de 18 a 29 años son quienes menos valoran lo digital. Los mayores, igual o más.',
      note: 'Diferencias pequeñas: la edad no predice resistencia. Tampoco significa que los mayores adopten «más».',
      draw: (host) => hbar(host, {
        aria: 'Índice de Utilidad Percibida por grupo de edad', metric: 'Utilidad percibida',
        domain: [0, 7], avg: 4.66, labelW: 230,
        axisTitle: 'Utilidad percibida · escala 1 a 7',
        rows: [
          { label: '18 a 29 años', v: 4.40, n: 103, c: C.orange },
          { label: '30 a 39 años', v: 4.75, n: 146 },
          { label: '40 a 49 años', v: 4.70, n: 128 },
          { label: '50 a 59 años', v: 4.73, n: 79 },
          { label: '60 o más', v: 4.69, n: 27 },
        ],
      }),
    },
    {
      code: 'M2', id: 'cursos', section: 'Los verdaderos motores de la adopción', verdict: 'plausible',
      claim: 'Más cursos = más utilidad percibida',
      q: 'Q12 · ¿Con qué frecuencia participas en capacitaciones?',
      kicker: 'Utilidad percibida según frecuencia de cursos',
      big: '0,19', msg: 'de correlación (ρ): más cursos suben un poco la utilidad, pero la relación es débil.',
      note: 'Los extremos son grupos pequeños («Nunca»: 14 personas; «Varias por semana»: 30). En R2 veremos qué pesa más que los cursos.',
      draw: (host) => lineChart(host, {
        aria: 'Utilidad percibida según frecuencia de capacitación', metric: 'Utilidad percibida',
        domain: [0, 7],
        rows: [
          { label: ['Nunca'], v: 4.46, n: 14 },
          { label: ['< 1 vez', 'al año'], v: 4.39, n: 63 },
          { label: ['Varias', 'al año'], v: 4.37, n: 131 },
          { label: ['Mensual'], v: 4.82, n: 157 },
          { label: ['Semanal'], v: 4.80, n: 105 },
          { label: ['Varias', 'por semana'], v: 5.30, n: 30, c: C.orange },
        ],
      }),
    },
    {
      code: 'M3', id: 'utilidad', section: 'Los verdaderos motores de la adopción', verdict: 'confirmado',
      claim: 'Si la herramienta es útil, la gente la adopta',
      q: 'Q15_1, Q15_2 · Utilidad · Q21_1, Q21_3, Q21_4 · Adopción',
      kicker: 'Índice de Adopción según utilidad percibida',
      big: '+1,04', msg: 'puntos más de adopción cuando la herramienta se percibe útil.',
      note: 'Relación más fuerte del estudio (ρ = 0,31). Correlación no implica causalidad, pero TAM / UTAUT respaldan la dirección utilidad → adopción.',
      draw: (host) => vbar(host, {
        aria: 'Índice de Adopción según nivel de utilidad percibida', metric: 'Índice de Adopción',
        domain: [0, 7], avg: 4.74,
        rows: [
          { label: ['Utilidad baja', '(< 3,5)'], v: 4.11, n: 68 },
          { label: ['Utilidad media', '(3,5 – 5,5)'], v: 4.65, n: 264 },
          { label: ['Utilidad alta', '(≥ 5,5)'], v: 5.15, n: 168, c: C.orange },
        ],
      }),
    },
    {
      code: 'M4', id: 'modalidad', section: 'Rutas de aprendizaje', verdict: 'desmentido',
      claim: 'Lo presencial enseña mejor que lo virtual',
      q: 'Q14 · ¿Cuál fue la modalidad principal de tu aprendizaje?',
      kicker: 'Utilidad percibida por modalidad',
      big: '0,25', msg: 'puntos entre la mejor y la peor modalidad: ninguna gana con claridad.',
      note: 'Ojo con el eje: empieza en 4,4, así que 0,25 puntos parecen una goleada. Así se fabrica un mito.',
      draw: (host, card) => {
        card.classList.add('trap');
        hbar(host, {
          aria: 'Utilidad percibida por modalidad de aprendizaje', metric: 'Utilidad percibida',
          domain: [4.4, 4.8], ticks: [4.4, 4.5, 4.6, 4.7, 4.8], tickDec: 1, labelW: 290,
          axisTitle: 'Eje recortado: empieza en 4,4',
          rows: [
            { label: 'Híbrida', v: 4.75, n: 106 },
            { label: 'Presencial', v: 4.70, n: 81, c: C.orange },
            { label: 'Virtual asincrónica', v: 4.70, n: 87 },
            { label: 'Virtual sincrónica', v: 4.62, n: 82 },
            { label: 'Acompañamiento', v: 4.61, n: 62, tip: 'Acompañamiento en el puesto' },
            { label: 'Autoaprendizaje', v: 4.50, n: 67 },
          ],
        });
      },
    },
    {
      code: 'M5', id: 'jefes', section: 'La importancia del mando medio', verdict: 'desmentido',
      claim: 'Los jefes son los más digitales',
      q: 'Q7 · Cargo actual · Q10 · Experiencia digital',
      kicker: 'Utilidad percibida por cargo',
      big: '4,38', msg: 'Jefatura/Gerencia es la que menos valora las herramientas. Líderes y coordinadores, la que más.',
      note: 'En experiencia digital (escala 1 a 5) pasa lo mismo: Líder/Coordinador 3,12 es el más alto y Jefatura 2,94 está en el promedio.',
      draw: (host) => hbar(host, {
        aria: 'Utilidad percibida por cargo', metric: 'Utilidad percibida',
        domain: [0, 7], labelW: 300,
        axisTitle: 'Utilidad percibida · escala 1 a 7',
        rows: [
          { label: 'Líder/Coordinador', v: 4.93, n: 91 },
          { label: 'Técnico/Operativo', v: 4.77, n: 100 },
          { label: 'Aprendiz', v: 4.64, n: 125 },
          { label: 'Profesional', v: 4.55, n: 113 },
          { label: 'Jefatura/Gerencia', v: 4.38, n: 71, c: C.orange },
        ],
      }),
    },
    {
      code: 'M6', id: 'sensorial', section: 'Diseño sensorial', verdict: 'desmentido',
      claim: 'A todos les gustan las interfaces llamativas y animadas',
      q: 'Q30 · Sensibilidad sensorial · Q31 a Q34 · Preferencias de diseño',
      kicker: 'Preferencias de diseño (4 = neutral)',
      big: '45 %', msg: 'del equipo tiene alta sensibilidad y prefiere interfaces sobrias y sin sonido.',
      note: 'La sensibilidad no frena la adopción: pide otro diseño. Modo simple, sonido opcional y ritmo propio.',
      draw: (host) => diverging(host, {
        aria: 'Preferencias de diseño de las personas con alta sensibilidad',
        domain: [3, 5], label: 'Alta sensibilidad (227)', ref: 'Todos (500): ≈ 4',
        rows: SENS_ITEMS.map((it, i) => ({ ...it, v: [3.58, 3.62, 3.74, 3.57][i] })),
      }),
    },
    {
      code: 'R1', id: 'genero', section: 'Ronda express', verdict: 'desmentido', express: true,
      claim: 'Hombres y mujeres valoran la tecnología de forma distinta',
      q: 'Q4 · ¿Con cuál género te identificas?',
      kicker: 'Utilidad percibida por género',
      big: '0,20', msg: 'puntos de diferencia entre mujeres y hombres: no es significativa.',
      note: 'Intervalos de confianza del 95 %: Femenino 4,61–4,95 y Masculino 4,44–4,72; se superponen. «Otro / No responde» (20 personas) no se muestra.',
      draw: (host) => hbar(host, {
        aria: 'Utilidad percibida por género', metric: 'Utilidad percibida',
        domain: [0, 7], labelW: 230, callout: true,
        axisTitle: 'Diferencia no significativa',
        rows: [
          { label: 'Femenino', v: 4.78, n: 178 },
          { label: 'Masculino', v: 4.58, n: 302 },
        ],
      }),
    },
    {
      code: 'R2', id: 'recursos', section: 'Ronda express', verdict: 'confirmado', express: true,
      claim: 'Si la empresa da licencias y tiempo, la gente valora más la herramienta',
      q: 'Q18_1 · Licencias y permisos · Q18_3 · Tiempo para aprender',
      kicker: 'Utilidad percibida según soporte organizacional',
      big: '+0,88', msg: 'puntos de utilidad cuando hay licencias y tiempo (recursos altos frente a bajos).',
      note: 'Pesa más que la frecuencia de cursos (ρ = 0,26 frente a 0,19). Correlación no es causalidad.',
      draw: (host) => vbar(host, {
        aria: 'Utilidad percibida por nivel de soporte organizacional', metric: 'Utilidad percibida',
        domain: [0, 7], avg: 4.66,
        rows: [
          { label: ['Recursos bajos', '(< 3,5)'], v: 4.11, n: 53 },
          { label: ['Recursos medios', '(3,5 – 5,0)'], v: 4.54, n: 263 },
          { label: ['Recursos altos', '(> 5,0)'], v: 4.99, n: 184, c: C.orange },
        ],
      }),
    },
    {
      code: 'R3', id: 'ruta', section: 'Ronda express', verdict: 'desmentido', express: true,
      claim: 'Todos prefieren que los guíen paso a paso',
      q: 'Q35 · Guiada o autónoma · Q36 · Demostración o experimentar',
      kicker: 'Preferencia de aprendizaje (% de personas)',
      big: '36 · 28 · 35', msg: '% prefiere guía · neutral · autonomía: no hay una ruta favorita.',
      note: 'Diseña rutas flexibles: guía paso a paso para quien la pida y libertad para quien quiera explorar.',
      draw: (host) => stacked(host, {
        aria: 'Distribución de preferencias de ruta de aprendizaje',
        rows: [
          {
            title: 'Q35 · Prefiero una experiencia de aprendizaje…', parts: [
              { label: 'Guiada paso a paso', v: 36.2, c: C.white },
              { label: 'Neutral', v: 28.4, c: GRAY },
              { label: 'Autónoma, a mi ritmo', v: 35.4, c: C.orange },
            ],
          },
          {
            title: 'Q36 · Prefiero aprender…', parts: [
              { label: 'Viendo una demostración', v: 32.4, c: C.white },
              { label: 'Neutral', v: 29.6, c: GRAY },
              { label: 'Experimentando', v: 38.0, c: C.orange },
            ],
          },
        ],
      }),
    },
  ];

  /* ================= Estado ================= */
  const state = { picks: {}, revealed: {} };
  const pickOf = (m, t) => (state.picks[m.id] || [])[t];
  const score = (t) => MYTHS.filter((m) => state.revealed[m.id] && pickOf(m, t) === m.verdict).length;

  /* ================= Construcción de diapositivas ================= */
  const stage = document.getElementById('stage');
  const scoreSlide = document.getElementById('slide-score');

  const voteSlides = [];
  const revealSlides = [];

  MYTHS.forEach((m, i) => {
    const tape = `<div class="tape"><span>${m.code} · ${i + 1} / ${MYTHS.length}</span></div>`;
    const vbtns = (t) => ORDER.map((v) => `<button class="vbtn" data-team="${t}" data-v="${v}">${VERDICTS[v].label}</button>`).join('');
    const team = (t) => `
      <div class="team">
        <div class="team-row"><span class="badge">${t + 1}</span><span class="tname">${TEAMS[t].name}</span></div>
        <div class="vbtns">${vbtns(t)}</div>
      </div>`;
    const size = m.claim.length > 48 ? 'long' : m.claim.length > 34 ? 'mid' : '';

    const vote = document.createElement('section');
    vote.className = 'slide dark myth';
    vote.dataset.myth = i;
    vote.dataset.phase = 'vote';
    vote.dataset.title = `Mito ${m.code}`;
    vote.innerHTML = `${tape}
      <div class="vote-phase">
        <div class="crate">
          <div class="crate-label">
            <div>
              <div class="label-head">
                <div class="acme">ACME</div>
              </div>
              <p class="claim ${size}">«${m.claim}»</p>
            </div>
          </div>
        </div>
        <div class="vote-panel">
          <h3>Veredicto de cada mesa</h3>
          ${team(0)}
          ${team(1)}
          ${team(2)}
        </div>
      </div>`;

    const reveal = document.createElement('section');
    reveal.className = 'slide dark myth revealed';
    reveal.dataset.myth = i;
    reveal.dataset.phase = 'reveal';
    reveal.dataset.title = `Mito ${m.code} · evidencia`;
    reveal.innerHTML = `${tape}
      <div class="reveal-phase">
        <h2 class="claim-small"><span>${m.code}</span>«${m.claim}»</h2>
        <div class="reveal-grid">
          <div class="chart-card">
            <div class="trap-banner">⚠ EJE RECORTADO · EMPIEZA EN 4,4</div>
            <div class="chart-head"><h3>${m.kicker}</h3></div>
            <div class="chart-host"></div>
            <p class="lab-note"><b>NOTA DEL LABORATORIO</b>${m.note}</p>
          </div>
          <aside class="verdict-panel">
            <div class="stamp-wrap"><div class="stamp ${m.verdict}">${VERDICTS[m.verdict].label}<small>${VERDICTS[m.verdict].en}</small></div></div>
            <div class="fact"><span class="fact-big">${m.big}</span><span class="fact-label">${m.msg}</span></div>
            <div class="team-results"></div>
          </aside>
        </div>
      </div>`;

    stage.insertBefore(vote, scoreSlide);
    stage.insertBefore(reveal, scoreSlide);
    voteSlides.push(vote);
    revealSlides.push(reveal);
  });

  const slides = Array.from(stage.querySelectorAll('.slide'));

  /* ================= Sincronización de UI ================= */
  function syncTeams() {
    const hs = document.getElementById('hud-score');
    hs.innerHTML = '';
    TEAMS.forEach((t, i) => {
      const sp = document.createElement('span');
      sp.textContent = t.short;
      const b = document.createElement('b');
      b.textContent = score(i);
      sp.appendChild(b);
      hs.appendChild(sp);
    });
  }

  function syncVotes(i) {
    const m = MYTHS[i];
    voteSlides[i].querySelectorAll('.vbtn').forEach((b) => {
      b.classList.toggle('on', pickOf(m, +b.dataset.team) === b.dataset.v);
    });
  }

  function renderResults(i) {
    const m = MYTHS[i], box = revealSlides[i].querySelector('.team-results');
    box.innerHTML = '';
    TEAMS.forEach((t, ti) => {
      const p = pickOf(m, ti), ok = p === m.verdict;
      const row = document.createElement('div');
      row.className = `tr ${ok ? 'ok' : 'ko'}`;
      const n = document.createElement('span'); n.className = 'n'; n.textContent = t.name;
      const mk = document.createElement('span'); mk.className = 'm'; mk.textContent = ok ? '✔ +1' : '✖';
      row.append(n, mk);
      box.appendChild(row);
    });
  }

  function drawChart(i) {
    const m = MYTHS[i], sec = revealSlides[i];
    m.draw(sec.querySelector('.chart-host'), sec.querySelector('.chart-card'));
  }

  function enterReveal(i) {
    const m = MYTHS[i], sec = revealSlides[i];
    state.revealed[m.id] = true;
    drawChart(i);
    renderResults(i);
    const st = sec.querySelector('.stamp');
    st.classList.remove('slam'); void st.offsetWidth; st.classList.add('slam');
    const vp = sec.querySelector('.verdict-panel');
    vp.classList.remove('shake'); void vp.offsetWidth; vp.classList.add('shake');
  }

  function pick(i, t, v) {
    const m = MYTHS[i];
    const arr = state.picks[m.id] || [null, null, null];
    arr[t] = arr[t] === v ? null : v;
    state.picks[m.id] = arr;
    syncVotes(i);
    if (state.revealed[m.id]) renderResults(i);
    syncTeams();
  }

  function renderScore() {
    const box = document.getElementById('score-board');
    const s = TEAMS.map((t, i) => score(i));
    const best = Math.max(...s);
    const tied = s.filter((v) => v === best).length > 1;
    const played = MYTHS.filter((m) => state.revealed[m.id]).length;
    box.innerHTML = '';
    const cards = document.createElement('div');
    cards.className = 'score-cards';
    TEAMS.forEach((t, ti) => {
      const c = document.createElement('div');
      const win = played > 0 && best > 0 && s[ti] === best;
      c.className = `score-card${win ? ' win' : ''}`;
      const name = document.createElement('div');
      name.className = 'sc-name';
      name.textContent = t.name;
      const sm = document.createElement('small');
      sm.textContent = 'aciertos';
      name.appendChild(sm);
      const num = document.createElement('div');
      num.className = 'sc-num';
      num.textContent = s[ti];
      c.append(name, num);
      if (win) {
        const st = document.createElement('div');
        st.className = 'stamp confirmado slam';
        st.textContent = tied ? 'EMPATE' : '¡GANADOR!';
        c.appendChild(st);
      }
      cards.appendChild(c);
    });
    box.appendChild(cards);

    const foot = document.createElement('div');
    foot.className = 'score-foot';
    const reset = document.createElement('button');
    reset.className = 'btn ghost';
    reset.textContent = 'Reiniciar juego';
    reset.addEventListener('click', () => {
      if (!confirm('¿Borrar todos los votos y veredictos revelados?')) return;
      state.picks = {}; state.revealed = {};
        MYTHS.forEach((m, i) => syncVotes(i));
      syncTeams(); renderScore(); updateHud();
    });
    foot.append(reset);
    box.appendChild(foot);
  }

  /* ================= Navegación ================= */
  let cur = 0;
  const nextBtn = document.getElementById('next');
  const prevBtn = document.getElementById('prev');
  const fill = document.querySelector('#progress .fill');
  const count = document.querySelector('#progress .count');

  const curMyth = () => (slides[cur].dataset.myth != null ? +slides[cur].dataset.myth : -1);
  const curPhase = () => slides[cur].dataset.phase;

  function updateHud() {
    fill.style.width = `${(cur / (slides.length - 1)) * 100}%`;
    count.textContent = `${pad2(cur + 1)} / ${slides.length}`;
    nextBtn.textContent = curPhase() === 'vote' ? 'Revelar ▶' : 'Siguiente ▶';
    nextBtn.disabled = cur === slides.length - 1;
    prevBtn.disabled = cur === 0;
  }

  function show(i, dir = 1) {
    i = Math.max(0, Math.min(slides.length - 1, i));
    slides[cur].classList.remove('active', 'back');
    cur = i;
    const s = slides[cur];
    s.classList.toggle('back', dir < 0);
    s.classList.add('active');
    const mi = curMyth();
    if (mi >= 0) {
      if (curPhase() === 'vote') syncVotes(mi);
      else enterReveal(mi);
    }
    if (s === scoreSlide) renderScore();
    syncTeams();
    updateHud();
    try { history.replaceState(null, '', `#${cur + 1}`); } catch (e) { /* file:// sin historial */ }
  }

  const next = () => { if (cur < slides.length - 1) show(cur + 1, 1); };
  const prev = () => { if (cur > 0) show(cur - 1, -1); };

  /* ================= Eventos ================= */
  const help = document.getElementById('help');
  const toggleHelp = (force) => help.classList.toggle('open', force);

  stage.addEventListener('click', (e) => {
    const b = e.target.closest('button');
    if (!b) return;
    const mi = curMyth();
    if (b.classList.contains('vbtn') && mi >= 0) pick(mi, +b.dataset.team, b.dataset.v);
    else if (b === nextBtn) next();
    else if (b === prevBtn) prev();
    setTimeout(() => b.blur(), 0);
  });


  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    const k = e.key;
    const mi = curMyth();
    const handled = () => e.preventDefault();
    if (help.classList.contains('open') && !['h', 'H', '?', 'Escape'].includes(k)) toggleHelp(false);
    if (/^[1-9]$/.test(k)) {
      if (mi >= 0) pick(mi, Math.floor((+k - 1) / 3), ORDER[(+k - 1) % 3]);
      return;
    }
    switch (k) {
      case 'ArrowRight': case 'PageDown': case ' ': case 'Enter': handled(); next(); break;
      case 'ArrowLeft': case 'PageUp': handled(); prev(); break;
      case 'Home': handled(); show(0, -1); break;
      case 'End': handled(); show(slides.length - 1, 1); break;
      case 'r': case 'R': if (curPhase() === 'vote') next(); break;
      case 'n': case 'N': document.body.classList.toggle('show-notes'); break;
      case 'f': case 'F':
        if (document.fullscreenElement) document.exitFullscreen();
        else if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen().catch(() => {});
        break;
      case 'h': case 'H': case '?': toggleHelp(); break;
      case 'Escape': toggleHelp(false); break;
      default: break;
    }
  });

  let touchX = null;
  stage.addEventListener('pointerdown', (e) => {
    if (e.pointerType === 'touch' && !e.target.closest('button, a')) touchX = e.clientX;
  });
  stage.addEventListener('pointerup', (e) => {
    if (touchX == null) return;
    const dx = e.clientX - touchX;
    touchX = null;
    if (Math.abs(dx) > 60) (dx < 0 ? next : prev)();
  });

  const tip = document.getElementById('tip');
  document.addEventListener('pointermove', (e) => {
    const t = e.target.closest && e.target.closest('[data-tip]');
    if (!t) { tip.style.display = 'none'; return; }
    tip.textContent = t.getAttribute('data-tip');
    tip.style.display = 'block';
    const r = tip.getBoundingClientRect();
    tip.style.left = `${Math.min(e.clientX + 18, innerWidth - r.width - 8)}px`;
    tip.style.top = `${Math.min(e.clientY + 18, innerHeight - r.height - 8)}px`;
  });

  function fit() {
    stage.style.setProperty('--s', Math.min(innerWidth / 1920, innerHeight / 1080));
  }
  addEventListener('resize', fit);
  fit();

  /* ================= Inicio ================= */
  MYTHS.forEach((m, i) => syncVotes(i));
  slides[0].classList.add('active');
  const fromHash = parseInt((location.hash || '').slice(1), 10);
  if (fromHash > 1) show(fromHash - 1, 1); else { syncTeams(); updateHud(); }
})();
