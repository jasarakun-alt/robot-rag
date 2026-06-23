// Subway Surfers gameplay (no copyright) za loading počasnih modelov — zamenljiv ID.
const SUBWAY_VIDEO_ID = "i0M4ARe9v0Y";

const chat = document.getElementById("chat");
const form = document.getElementById("form");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");
const micBtn = document.getElementById("mic");
const speakerBtn = document.getElementById("speaker");
const suggestionsEl = document.getElementById("suggestions");
const modelSel = document.getElementById("model");
const langSel = document.getElementById("language");
const otherLang = document.getElementById("otherLang");
const overlay = document.getElementById("overlay");
const overlayVideo = document.getElementById("overlayVideo");
const overlayTitle = document.getElementById("overlayTitle");
const overlayCaption = document.getElementById("overlayCaption");

// Jeziki, ki jih modeli dobro podpirajo (ime za prompt + koda za govor).
const LANGS = [
  { name: "slovenščina", code: "sl-SI" },
  { name: "angleščina", code: "en-US" },
  { name: "nemščina", code: "de-DE" },
  { name: "italijanščina", code: "it-IT" },
  { name: "francoščina", code: "fr-FR" },
  { name: "španščina", code: "es-ES" },
  { name: "hrvaščina", code: "hr-HR" },
];
const OTHER = "__other__";

// Namigi (tooltipi kot tekst) med Subway Surfers čakanjem.
const TIPS = [
  "Ali si vedel? Ultrazvočni senzor 'vidi' z zvokom nad 20 kHz, ki ga človek ne sliši.",
  "Namig: motor priklopi prek gonilnika (H-most), nikoli neposredno na krmilnik.",
  "Varnost: polov baterije nikoli ne stikaj na kratko!",
  "Hitrost motorja krmilimo s PWM — hitrim vklapljanjem in izklapljanjem napajanja.",
  "Servo motor zavrti gred na natančen kot med 0 in 180 stopinj.",
  "Infrardeči senzor loči črto od podlage po količini odbite svetlobe.",
  "Pred sestavljanjem robota vedno najprej odklopi baterijo.",
  "Diferencialni pogon: robot zavije, ko se eno kolo vrti hitreje od drugega.",
];

let speakOn = false;
let modelsCache = [];
let slowThreshold = 12;

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text != null) e.textContent = text;
  return e;
}

/* ---------------- izbirnika modela in jezika ---------------- */

function fillLanguages() {
  LANGS.forEach((l) => {
    const o = el("option", null, l.name);
    o.value = l.name;
    langSel.appendChild(o);
  });
  const o = el("option", null, "Drug jezik (prevod)…");
  o.value = OTHER;
  langSel.appendChild(o);
}

langSel.addEventListener("change", () => {
  otherLang.classList.toggle("hidden", langSel.value !== OTHER);
});

function modelLabel(m) {
  const t = m.measured ? `${m.seconds}s` : `~${m.seconds}s`;
  return `${m.name} — ${t}${m.slow ? " ⚠ Subway Surfers" : ""}`;
}

async function loadModels() {
  try {
    const res = await fetch("/models");
    const data = await res.json();
    modelsCache = data.models || [];
    slowThreshold = data.slow_threshold || slowThreshold;
    modelSel.innerHTML = "";
    modelsCache.forEach((m) => {
      const o = el("option", null, modelLabel(m));
      o.value = m.name;
      modelSel.appendChild(o);
    });
    if (data.default) modelSel.value = data.default;
  } catch (e) {
    modelSel.appendChild(el("option", null, "(privzeti model)"));
  }
}

function currentModelInfo() {
  return modelsCache.find((m) => m.name === modelSel.value);
}

function currentLanguage() {
  if (langSel.value === OTHER) {
    return { name: otherLang.value.trim() || "angleščina", code: null, pivot: true };
  }
  const l = LANGS.find((x) => x.name === langSel.value) || LANGS[0];
  return { name: l.name, code: l.code, pivot: false };
}

function refreshModelTime(name, elapsedMs) {
  const s = +(elapsedMs / 1000).toFixed(1);
  const m = modelsCache.find((x) => x.name === name);
  if (m) {
    m.seconds = s;
    m.measured = true;
    m.slow = s > slowThreshold;
    [...modelSel.options].forEach((o) => {
      if (o.value === name) o.textContent = modelLabel(m);
    });
  }
}

/* ---------------- Subway Surfers overlay ---------------- */

let capTimer = null;
function showOverlay(modelName, seconds) {
  overlayTitle.textContent = `Razmišljam… (${modelName}, ~${seconds}s)`;
  overlayVideo.innerHTML =
    `<iframe src="https://www.youtube.com/embed/${SUBWAY_VIDEO_ID}` +
    `?autoplay=1&mute=1&loop=1&playlist=${SUBWAY_VIDEO_ID}&controls=0&modestbranding=1&playsinline=1" ` +
    `allow="autoplay; encrypted-media"></iframe>`;
  let i = 0;
  overlayCaption.textContent = TIPS[0];
  capTimer = setInterval(() => {
    i = (i + 1) % TIPS.length;
    overlayCaption.textContent = TIPS[i];
  }, 3000);
  overlay.classList.remove("hidden");
}
function hideOverlay() {
  overlay.classList.add("hidden");
  overlayVideo.innerHTML = ""; // ustavi video
  if (capTimer) clearInterval(capTimer);
  capTimer = null;
}

/* ---------------- glas: STT (mikrofon) + TTS (branje) ---------------- */

const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
if (!SR) micBtn.style.display = "none";

let recognition = null;
let recognizing = false;
let voiceFinal = "";

function micErrorText(err) {
  const map = {
    "not-allowed": "Dovoli dostop do mikrofona v brskalniku.",
    "service-not-allowed": "Brskalnik je zavrnil prepoznavo govora.",
    "no-speech": "Nisem slišal govora — poskusi znova.",
    "audio-capture": "Mikrofona ni mogoče najti.",
    "network": "Napaka omrežja pri prepoznavi govora.",
    "language-not-supported": "Izbrani jezik ni podprt za govor — izberi drugega.",
  };
  return map[err] || "Napaka mikrofona: " + err;
}

function micHint(msg) {
  let h = document.getElementById("micHint");
  if (!h) {
    h = el("div", "mic-hint");
    h.id = "micHint";
    form.after(h);
  }
  h.textContent = msg;
  h.classList.remove("hidden");
  clearTimeout(h._t);
  h._t = setTimeout(() => h.classList.add("hidden"), 4500);
}

micBtn.addEventListener("click", () => {
  if (!SR) {
    micHint("Brskalnik ne podpira prepoznave govora (poskusi Chrome).");
    return;
  }
  if (recognizing) {
    if (recognition) recognition.stop(); // drugi klik = ustavi
    return;
  }
  voiceFinal = input.value ? input.value.trim() + " " : "";
  recognition = new SR();
  recognition.lang = currentLanguage().code || "sl-SI";
  recognition.interimResults = true; // sproten (živ) prepis
  recognition.continuous = true; // posluša do drugega klika
  recognition.maxAlternatives = 1;
  recognition.onstart = () => {
    recognizing = true;
    micBtn.classList.add("rec");
    micBtn.textContent = "⏹";
    input.placeholder = "Poslušam… besedilo se izpisuje sproti";
  };
  recognition.onresult = (e) => {
    let interim = "";
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const t = e.results[i][0].transcript;
      if (e.results[i].isFinal) voiceFinal += t + " ";
      else interim += t;
    }
    input.value = (voiceFinal + interim).trim(); // živ izpis v polje
  };
  recognition.onerror = (e) => micHint(micErrorText(e.error));
  recognition.onend = () => {
    recognizing = false;
    micBtn.classList.remove("rec");
    micBtn.textContent = "🎤";
    input.placeholder = "Vpiši vprašanje…";
    if (input.value.trim()) micHint("Besedilo pripravljeno — pritisni ➤ za pošiljanje.");
  };
  try {
    recognition.start();
  } catch (err) {
    recognizing = false;
    micHint("Mikrofon je že aktiven.");
  }
});

function speak(text) {
  if (!("speechSynthesis" in window)) return;
  const lang = currentLanguage();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = lang.code || "sl-SI";
  const voices = window.speechSynthesis.getVoices() || [];
  const pref = (lang.code || "sl").slice(0, 2).toLowerCase();
  const v = voices.find((vc) => vc.lang && vc.lang.toLowerCase().startsWith(pref));
  if (v) u.voice = v;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(u);
}

speakerBtn.addEventListener("click", () => {
  speakOn = !speakOn;
  speakerBtn.textContent = speakOn ? "🔊 vklop" : "🔊 izklop";
  speakerBtn.classList.toggle("on", speakOn);
  if (!speakOn && "speechSynthesis" in window) window.speechSynthesis.cancel();
});

/* ---------------- pogovor ---------------- */

function addMessage(role, content) {
  const wrap = el("div", "msg " + role);
  const avatar = el("div", "avatar", role === "bot" ? "🤖" : "🧑");
  const bubble = el("div", "bubble");
  if (typeof content === "string") bubble.textContent = content;
  else bubble.appendChild(content);
  wrap.appendChild(avatar);
  wrap.appendChild(bubble);
  chat.appendChild(wrap);
  chat.scrollTop = chat.scrollHeight;
  return { wrap, bubble };
}

function typingIndicator() {
  const d = el("div", "typing");
  d.appendChild(el("span"));
  d.appendChild(el("span"));
  d.appendChild(el("span"));
  return d;
}

function renderAnswer(data) {
  const frag = document.createElement("div");
  frag.appendChild(el("div", "answer", data.answer));

  if (data.sources && data.sources.length) {
    const det = el("details", "sources");
    det.appendChild(el("summary", null, `Uporabljeni viri iz priročnika (${data.sources.length})`));
    data.sources.forEach((s, i) => {
      const item = el("div", "source");
      const score = s.score != null ? `  ·  ujemanje ${Number(s.score).toFixed(2)}` : "";
      item.appendChild(el("div", "source-title", `${i + 1}. ${s.title}${score}`));
      item.appendChild(el("div", "source-text", s.text));
      item.appendChild(el("div", "source-meta", "vir: " + (s.source || "prirocnik.md")));
      det.appendChild(item);
    });
    frag.appendChild(det);
  }

  const secs = data.elapsed_ms != null ? ` · ${(data.elapsed_ms / 1000).toFixed(1)}s` : "";
  const piv = data.translated ? " · prevod" : "";
  const esc = data.escalated ? " · samodejna nadgradnja modela" : "";
  frag.appendChild(el("div", "model-tag", `model: ${data.model || "?"}${secs}${piv}${esc}`));

  const replay = el("button", "replay", "🔊 Preberi");
  replay.type = "button";
  replay.addEventListener("click", () => speak(data.answer));
  frag.appendChild(replay);
  return frag;
}

async function ask(question) {
  input.disabled = true;
  sendBtn.disabled = true;
  const lang = currentLanguage();
  const model = modelSel.value || undefined;
  const mInfo = currentModelInfo();
  const slow = !!(mInfo && mInfo.slow);

  addMessage("user", question);
  let loading = null;
  if (slow) {
    showOverlay(model, mInfo ? mInfo.seconds : "?");
  } else {
    loading = addMessage("bot", typingIndicator());
  }

  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, model, language: lang.name, pivot: lang.pivot }),
    });
    if (!res.ok) {
      const e = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(e.detail || "Napaka " + res.status);
    }
    const data = await res.json();
    if (slow) {
      hideOverlay();
      loading = addMessage("bot", "");
    }
    loading.bubble.classList.remove("loading");
    loading.bubble.textContent = "";
    loading.bubble.appendChild(renderAnswer(data));
    if (data.model && data.elapsed_ms != null) refreshModelTime(data.model, data.elapsed_ms);
    if (speakOn) speak(data.answer);
  } catch (err) {
    if (slow) {
      hideOverlay();
      loading = addMessage("bot", "");
    }
    loading.bubble.classList.remove("loading");
    loading.bubble.classList.add("error");
    loading.bubble.textContent = "Napaka: " + err.message;
  } finally {
    input.disabled = false;
    sendBtn.disabled = false;
    input.focus();
    chat.scrollTop = chat.scrollHeight;
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const q = input.value.trim();
  if (!q) return;
  input.value = "";
  ask(q);
});

async function loadFaq() {
  try {
    const res = await fetch("/faq");
    const data = await res.json();
    (data.questions || []).forEach((q) => {
      const chip = el("button", "chip", q);
      chip.type = "button";
      chip.addEventListener("click", () => ask(q));
      suggestionsEl.appendChild(chip);
    });
  } catch (e) {
    /* tiho ignoriraj */
  }
}

fillLanguages();
loadModels();
loadFaq();
