/* Neon Sticker Studio — canvas sticker maker */

const SIZE = 800;
const HALF = SIZE / 2;

const canvas = document.getElementById("preview");
const ctx = canvas.getContext("2d");

const state = {
  template: "planet",
  mainColor: "#0d0d2b",
  accentColor: "#00f5ff",
  glowColor: "#ff006e",
  textTop: "",
  textBottom: "",
  stars: true,
  glow: true,
  seed: 42,
  pro: localStorage.getItem("nss_pro") === "1",
};

const TEMPLATES = [
  { id: "planet", label: "惑星", icon: "🪐" },
  { id: "rocket", label: "ロケット", icon: "🚀" },
  { id: "cat", label: "宇宙ネコ", icon: "🐱" },
  { id: "moon", label: "三日月", icon: "🌙" },
  { id: "burst", label: "バースト", icon: "💥" },
  { id: "badge", label: "アーケード", icon: "🕹️" },
];

const YELLOW = "#ffe600";
const WHITE = "#ffffff";

// ── Helpers ──────────────────────────────────────────────────────────────────

function seededRandom(seed) {
  let s = seed >>> 0;
  return () => {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 4294967296;
  };
}

function hexAlpha(hex, alpha) {
  const a = Math.round(alpha * 255).toString(16).padStart(2, "0");
  return hex + a;
}

function drawGlow(c, x, y, radius, color, strength = 0.5) {
  if (!state.glow) return;
  const g = c.createRadialGradient(x, y, radius * 0.2, x, y, radius * 1.6);
  g.addColorStop(0, hexAlpha(color, strength));
  g.addColorStop(1, hexAlpha(color, 0));
  c.fillStyle = g;
  c.fillRect(0, 0, SIZE, SIZE);
}

function drawStars(c, count, seed) {
  if (!state.stars) return;
  const rng = seededRandom(seed);
  const colors = [WHITE, state.accentColor, YELLOW];
  for (let i = 0; i < count; i++) {
    const x = 30 + rng() * (SIZE - 60);
    const y = 30 + rng() * (SIZE - 60);
    const r = 2 + rng() * 3;
    c.fillStyle = colors[Math.floor(rng() * colors.length)];
    c.beginPath();
    c.arc(x, y, r, 0, Math.PI * 2);
    c.fill();
  }
}

function starPath(c, cx, cy, outer, inner, points) {
  c.beginPath();
  for (let i = 0; i < points * 2; i++) {
    const angle = (Math.PI / points) * i - Math.PI / 2;
    const r = i % 2 === 0 ? outer : inner;
    const x = cx + r * Math.cos(angle);
    const y = cy + r * Math.sin(angle);
    i === 0 ? c.moveTo(x, y) : c.lineTo(x, y);
  }
  c.closePath();
}

function centeredText(c, text, y, fontSize, fill, outline) {
  if (!text) return;
  c.font = `900 ${fontSize}px "Arial Black", "Hiragino Kaku Gothic ProN", sans-serif`;
  c.textAlign = "center";
  c.textBaseline = "middle";
  if (outline) {
    c.lineWidth = fontSize / 8;
    c.strokeStyle = outline;
    c.lineJoin = "round";
    c.strokeText(text, HALF, y);
  }
  c.fillStyle = fill;
  c.fillText(text, HALF, y);
}

function overlayTexts(c) {
  centeredText(c, state.textTop, 80, 56, state.accentColor, state.mainColor);
  centeredText(c, state.textBottom, SIZE - 80, 56, YELLOW, state.mainColor);
}

// ── Templates ────────────────────────────────────────────────────────────────

function drawPlanet(c) {
  drawGlow(c, HALF, HALF, 240, state.glowColor, 0.45);
  drawStars(c, 25, 1);

  const pr = 160;
  // Body
  c.beginPath();
  c.arc(HALF, HALF, pr, 0, Math.PI * 2);
  c.fillStyle = state.mainColor;
  c.fill();
  c.lineWidth = 5;
  c.strokeStyle = state.accentColor;
  c.stroke();

  // Surface bands clipped to planet
  c.save();
  c.beginPath();
  c.arc(HALF, HALF, pr - 4, 0, Math.PI * 2);
  c.clip();
  const bands = [
    [HALF - 30, 18, hexAlpha(state.accentColor, 0.45)],
    [HALF - 5, 14, hexAlpha(state.glowColor, 0.5)],
    [HALF + 20, 18, hexAlpha(state.accentColor, 0.35)],
  ];
  for (const [y, h, col] of bands) {
    c.fillStyle = col;
    c.fillRect(HALF - pr, y, pr * 2, h);
  }
  c.restore();

  // Rings
  const rings = [
    [210, hexAlpha(state.accentColor, 0.8), 6],
    [240, hexAlpha(state.glowColor, 0.6), 4],
    [265, hexAlpha(YELLOW, 0.4), 3],
  ];
  for (const [r, col, w] of rings) {
    c.beginPath();
    c.ellipse(HALF, HALF, r, 55, 0, 0, Math.PI * 2);
    c.lineWidth = w;
    c.strokeStyle = col;
    c.stroke();
  }

  // Planet front half over rings
  c.beginPath();
  c.arc(HALF, HALF, pr - 2, 0.15 * Math.PI, 0.85 * Math.PI);
  c.fillStyle = state.mainColor;
  c.fill();

  // Glint
  c.beginPath();
  c.ellipse(HALF - 90, HALF - 95, 22, 15, -0.5, 0, Math.PI * 2);
  c.fillStyle = "rgba(180, 220, 255, 0.5)";
  c.fill();
}

function drawRocket(c) {
  drawStars(c, 30, 2);
  const cx = HALF;

  // Flame
  c.beginPath();
  c.moveTo(cx - 40, 680); c.lineTo(cx - 20, 580); c.lineTo(cx, 640);
  c.lineTo(cx + 20, 580); c.lineTo(cx + 40, 680);
  c.closePath();
  c.fillStyle = "rgba(255, 140, 0, 0.85)";
  c.fill();
  c.beginPath();
  c.moveTo(cx - 20, 660); c.lineTo(cx, 600); c.lineTo(cx + 20, 660);
  c.closePath();
  c.fillStyle = YELLOW;
  c.fill();

  drawGlow(c, cx, 640, 70, "#ff6400", 0.5);

  // Body
  c.beginPath();
  c.moveTo(cx - 50, 550); c.lineTo(cx - 55, 400); c.lineTo(cx - 35, 280);
  c.lineTo(cx, 180);
  c.lineTo(cx + 35, 280); c.lineTo(cx + 55, 400); c.lineTo(cx + 50, 550);
  c.closePath();
  c.fillStyle = state.mainColor;
  c.fill();
  c.lineWidth = 4;
  c.strokeStyle = state.accentColor;
  c.stroke();

  // Nose cone
  c.beginPath();
  c.moveTo(cx - 20, 340); c.lineTo(cx, 180); c.lineTo(cx + 20, 340);
  c.closePath();
  c.fillStyle = hexAlpha(state.glowColor, 0.8);
  c.fill();

  // Fins
  for (const dir of [-1, 1]) {
    c.beginPath();
    c.moveTo(cx + dir * 55, 520); c.lineTo(cx + dir * 55, 400); c.lineTo(cx + dir * 110, 560);
    c.closePath();
    c.fillStyle = hexAlpha("#7b2fbe", 0.9);
    c.fill();
    c.lineWidth = 3;
    c.strokeStyle = state.glowColor;
    c.stroke();
  }

  // Stripe
  c.fillStyle = hexAlpha(state.glowColor, 0.8);
  c.fillRect(cx - 54, 460, 108, 20);

  // Window
  c.beginPath();
  c.arc(cx, 428, 28, 0, Math.PI * 2);
  c.fillStyle = "#1e3264";
  c.fill();
  c.lineWidth = 4;
  c.strokeStyle = state.accentColor;
  c.stroke();
  c.beginPath();
  c.arc(cx, 428, 14, 0, Math.PI * 2);
  c.fillStyle = hexAlpha(state.accentColor, 0.7);
  c.fill();

  // Decorative stars
  for (const [sx, sy, ss] of [[150, 200, 12], [620, 150, 10], [680, 400, 8], [120, 500, 10]]) {
    starPath(c, sx, sy, ss, ss / 2, 5);
    c.fillStyle = YELLOW;
    c.fill();
  }
}

function drawCat(c) {
  const cx = HALF, cy = HALF + 30;
  drawGlow(c, cx, cy, 230, state.glowColor, 0.4);
  drawStars(c, 20, 7);

  // Ears
  const ears = [
    [[cx - 160, cy - 130], [cx - 80, cy - 260], [cx - 30, cy - 140]],
    [[cx + 160, cy - 130], [cx + 80, cy - 260], [cx + 30, cy - 140]],
  ];
  for (const ear of ears) {
    c.beginPath();
    c.moveTo(...ear[0]); c.lineTo(...ear[1]); c.lineTo(...ear[2]);
    c.closePath();
    c.fillStyle = state.mainColor;
    c.fill();
    c.lineWidth = 5;
    c.strokeStyle = state.glowColor;
    c.stroke();
    // Inner ear
    const mx = (ear[0][0] + ear[1][0] + ear[2][0]) / 3;
    const my = (ear[0][1] + ear[1][1] + ear[2][1]) / 3;
    c.beginPath();
    for (let i = 0; i < 3; i++) {
      const x = mx + (ear[i][0] - mx) * 0.55;
      const y = my + (ear[i][1] - my) * 0.55;
      i === 0 ? c.moveTo(x, y) : c.lineTo(x, y);
    }
    c.closePath();
    c.fillStyle = hexAlpha(state.glowColor, 0.8);
    c.fill();
  }

  // Head
  c.beginPath();
  c.arc(cx, cy, 170, 0, Math.PI * 2);
  c.fillStyle = state.mainColor;
  c.fill();
  c.lineWidth = 6;
  c.strokeStyle = state.glowColor;
  c.stroke();

  // Eyes
  for (const ex of [cx - 65, cx + 65]) {
    const ey = cy - 30;
    c.beginPath();
    c.arc(ex, ey, 30, 0, Math.PI * 2);
    c.fillStyle = "#14143c";
    c.fill();
    c.lineWidth = 4;
    c.strokeStyle = state.accentColor;
    c.stroke();
    c.beginPath();
    c.arc(ex, ey, 12, 0, Math.PI * 2);
    c.fillStyle = state.accentColor;
    c.fill();
    c.beginPath();
    c.arc(ex + 11, ey - 11, 5, 0, Math.PI * 2);
    c.fillStyle = WHITE;
    c.fill();
  }

  // Nose
  c.beginPath();
  c.moveTo(cx, cy + 20); c.lineTo(cx - 12, cy + 40); c.lineTo(cx + 12, cy + 40);
  c.closePath();
  c.fillStyle = state.glowColor;
  c.fill();

  // Whiskers
  c.lineWidth = 2;
  c.strokeStyle = state.accentColor;
  for (const [x1, x2, y] of [
    [cx - 170, cx - 45, cy + 35], [cx - 170, cx - 45, cy + 55],
    [cx + 45, cx + 170, cy + 35], [cx + 45, cx + 170, cy + 55],
  ]) {
    c.beginPath(); c.moveTo(x1, y); c.lineTo(x2, y); c.stroke();
  }

  // Antenna
  c.lineWidth = 4;
  c.strokeStyle = YELLOW;
  c.beginPath(); c.moveTo(cx, cy - 170); c.lineTo(cx + 30, cy - 300); c.stroke();
  c.beginPath();
  c.arc(cx + 30, cy - 304, 14, 0, Math.PI * 2);
  c.fillStyle = YELLOW;
  c.fill();
  c.lineWidth = 3;
  c.strokeStyle = WHITE;
  c.stroke();

  // Blush
  for (const bx of [cx - 100, cx + 100]) {
    c.beginPath();
    c.ellipse(bx, cy + 40, 28, 12, 0, 0, Math.PI * 2);
    c.fillStyle = hexAlpha(state.glowColor, 0.4);
    c.fill();
  }
}

function drawMoon(c) {
  drawStars(c, 35, 3);
  drawGlow(c, HALF, HALF, 240, YELLOW, 0.35);

  const mr = 200;
  // Crescent: full circle minus offset circle
  c.save();
  c.beginPath();
  c.arc(HALF, HALF, mr, 0, Math.PI * 2);
  c.arc(HALF + 80, HALF, mr, 0, Math.PI * 2, true);
  c.fillStyle = "#ffe696";
  c.fill("evenodd");
  c.restore();

  c.save();
  c.beginPath();
  c.arc(HALF, HALF, mr, 0, Math.PI * 2);
  c.arc(HALF + 80, HALF, mr, 0, Math.PI * 2, true);
  c.clip("evenodd");
  // Craters inside the crescent
  for (const [cx2, cy2, cr] of [
    [HALF - 60, HALF - 80, 22], [HALF + 20, HALF + 60, 16],
    [HALF - 140, HALF + 30, 12], [HALF - 30, HALF + 120, 18],
  ]) {
    c.beginPath();
    c.arc(cx2, cy2, cr, 0, Math.PI * 2);
    c.fillStyle = "rgba(220, 190, 100, 0.8)";
    c.fill();
    c.lineWidth = 2;
    c.strokeStyle = "rgba(180, 150, 60, 0.8)";
    c.stroke();
  }
  c.restore();

  // Outline
  c.beginPath();
  c.arc(HALF, HALF, mr, 0, Math.PI * 2);
  c.lineWidth = 5;
  c.strokeStyle = hexAlpha(YELLOW, 0.5);
  c.stroke();

  // Decorative stars
  for (const [sx, sy, sr] of [[HALF + 250, 120, 20], [100, HALF - 200, 15], [680, HALF + 100, 18]]) {
    starPath(c, sx, sy, sr, sr * 0.45, 5);
    c.fillStyle = YELLOW;
    c.fill();
  }
}

function drawBurst(c) {
  // Outer burst
  starPath(c, HALF, HALF, 360, 280, 16);
  c.fillStyle = YELLOW;
  c.fill();
  drawGlow(c, HALF, HALF, 340, YELLOW, 0.3);

  // Inner burst
  starPath(c, HALF, HALF, 240, 190, 16);
  c.fillStyle = hexAlpha(state.glowColor, 0.9);
  c.fill();

  // Center circle
  c.beginPath();
  c.arc(HALF, HALF, 150, 0, Math.PI * 2);
  c.fillStyle = state.mainColor;
  c.fill();
  c.lineWidth = 6;
  c.strokeStyle = state.accentColor;
  c.stroke();

  centeredText(c, state.textTop || "Y2K", HALF - 20, 110, state.accentColor, "#7b2fbe");
  centeredText(c, state.textBottom || "FUTURE IS NOW", HALF + 80, 30, YELLOW, state.mainColor);

  // Tip stars
  for (let i = 0; i < 16; i += 2) {
    const angle = (i * (Math.PI * 2)) / 16 - Math.PI / 2;
    const sx = HALF + 340 * Math.cos(angle);
    const sy = HALF + 340 * Math.sin(angle);
    starPath(c, sx, sy, 18, 8, 5);
    c.fillStyle = WHITE;
    c.fill();
  }
}

function drawBadge(c) {
  // Badge background
  const r = 80;
  c.beginPath();
  c.roundRect(60, 80, SIZE - 120, SIZE - 160, r);
  c.fillStyle = state.mainColor;
  c.fill();
  c.lineWidth = 8;
  c.strokeStyle = "#39ff14";
  c.stroke();

  drawGlow(c, HALF, HALF, 300, "#39ff14", 0.25);

  // Inner border
  c.beginPath();
  c.roundRect(80, 100, SIZE - 160, SIZE - 200, 65);
  c.lineWidth = 3;
  c.strokeStyle = hexAlpha(YELLOW, 0.7);
  c.stroke();

  // Coin
  c.beginPath();
  c.arc(HALF, HALF - 40, 100, 0, Math.PI * 2);
  c.fillStyle = "#c8a000";
  c.fill();
  c.lineWidth = 5;
  c.strokeStyle = YELLOW;
  c.stroke();
  c.beginPath();
  c.arc(HALF, HALF - 40, 86, 0, Math.PI * 2);
  c.fillStyle = "#e6be14";
  c.fill();

  centeredText(c, "1UP", HALF - 40, 52, state.mainColor);
  centeredText(c, state.textTop || "INSERT COIN", 150, 38, "#39ff14", state.mainColor);
  centeredText(c, state.textBottom || "PLAY AGAIN", SIZE - 160, 38, state.accentColor, state.mainColor);

  // Pixel dots
  for (let i = 0; i < 16; i++) {
    const angle = (i * Math.PI * 2) / 16;
    const px = HALF + 300 * Math.cos(angle);
    const py = HALF + 230 * Math.sin(angle);
    c.fillStyle = i % 2 === 0 ? "#39ff14" : YELLOW;
    c.fillRect(px - 5, py - 5, 10, 10);
  }
}

const DRAWERS = {
  planet: drawPlanet,
  rocket: drawRocket,
  cat: drawCat,
  moon: drawMoon,
  burst: drawBurst,
  badge: drawBadge,
};

// ── Render / export ──────────────────────────────────────────────────────────

function render() {
  ctx.clearRect(0, 0, SIZE, SIZE);
  DRAWERS[state.template](ctx);
  if (!["burst", "badge"].includes(state.template)) overlayTexts(ctx);
}

function addWatermark(c, size) {
  c.save();
  c.globalAlpha = 0.45;
  c.font = `700 ${Math.round(size / 28)}px sans-serif`;
  c.textAlign = "right";
  c.textBaseline = "bottom";
  c.fillStyle = "#ffffff";
  c.strokeStyle = "rgba(0,0,0,0.6)";
  c.lineWidth = 3;
  c.strokeText("Neon Sticker Studio", size - 14, size - 12);
  c.fillText("Neon Sticker Studio", size - 14, size - 12);
  c.restore();
}

function download() {
  const select = document.getElementById("sizeSelect");
  let size = parseInt(select.value, 10);
  const isProSize = select.selectedOptions[0].dataset.pro === "1";
  if (isProSize && !state.pro) {
    alert("このサイズはPRO限定です。512pxは無料でご利用いただけます。");
    size = 512;
  }

  const out = document.createElement("canvas");
  out.width = size;
  out.height = size;
  const octx = out.getContext("2d");
  octx.drawImage(canvas, 0, 0, size, size);
  if (!state.pro) addWatermark(octx, size);

  const link = document.createElement("a");
  link.download = `sticker_${state.template}_${size}px.png`;
  link.href = out.toDataURL("image/png");
  link.click();
}

function randomize() {
  const rng = seededRandom(Date.now() & 0xffffffff);
  const palette = ["#ff006e", "#00f5ff", "#7b2fbe", "#39ff14", "#ffe600", "#ff00ff", "#ff6400"];
  const darks = ["#0d0d2b", "#1a0a2e", "#0a1a2e", "#16213e", "#1b0f3b"];
  state.template = TEMPLATES[Math.floor(rng() * TEMPLATES.length)].id;
  state.mainColor = darks[Math.floor(rng() * darks.length)];
  state.accentColor = palette[Math.floor(rng() * palette.length)];
  state.glowColor = palette[Math.floor(rng() * palette.length)];
  syncControls();
  render();
}

// ── License (placeholder — replace with Gumroad/Stripe verification) ────────

function activateLicense() {
  const key = document.getElementById("licenseInput").value.trim();
  // Placeholder check: real implementation should call your payment
  // provider's license verification API (e.g. Gumroad License API).
  if (/^NSS-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$/.test(key)) {
    state.pro = true;
    localStorage.setItem("nss_pro", "1");
    document.getElementById("freeNote").textContent = "✦ PRO版：1024px・透かしなしで書き出せます";
    alert("PRO版が有効になりました！");
  } else {
    alert("ライセンスキーの形式が正しくありません（例: NSS-XXXX-XXXX-XXXX）");
  }
}

// ── UI wiring ────────────────────────────────────────────────────────────────

function buildTemplateGrid() {
  const grid = document.getElementById("templateGrid");
  for (const t of TEMPLATES) {
    const btn = document.createElement("button");
    btn.className = "template-btn" + (t.id === state.template ? " active" : "");
    btn.dataset.id = t.id;
    btn.innerHTML = `<span class="t-icon">${t.icon}</span>${t.label}`;
    btn.addEventListener("click", () => {
      state.template = t.id;
      grid.querySelectorAll(".template-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      render();
    });
    grid.appendChild(btn);
  }
}

function syncControls() {
  document.getElementById("mainColor").value = state.mainColor;
  document.getElementById("accentColor").value = state.accentColor;
  document.getElementById("glowColor").value = state.glowColor;
  document.querySelectorAll(".template-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.id === state.template);
  });
}

function bind(id, prop, event = "input") {
  document.getElementById(id).addEventListener(event, (e) => {
    state[prop] = e.target.type === "checkbox" ? e.target.checked : e.target.value;
    render();
  });
}

buildTemplateGrid();
bind("mainColor", "mainColor");
bind("accentColor", "accentColor");
bind("glowColor", "glowColor");
bind("textTop", "textTop");
bind("textBottom", "textBottom");
bind("starsToggle", "stars", "change");
bind("glowToggle", "glow", "change");
document.getElementById("downloadBtn").addEventListener("click", download);
document.getElementById("randomBtn").addEventListener("click", randomize);
document.getElementById("licenseBtn").addEventListener("click", activateLicense);
document.getElementById("buyBtn").addEventListener("click", (e) => {
  const url = e.currentTarget.dataset.paymentLink;
  if (!url) {
    e.preventDefault();
    alert("販売準備中です。README の手順で決済リンク（Stripe / Gumroad / BOOTH）を設定してください。");
  }
});

if (state.pro) {
  document.getElementById("freeNote").textContent = "✦ PRO版：1024px・透かしなしで書き出せます";
}

render();
