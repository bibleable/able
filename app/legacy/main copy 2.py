from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>ABLE Bible Search</title>
  <style>
    /* -------------------------------------------
       THEME TOKENS
    ------------------------------------------- */
    :root {
      --bg-0: #f2f6ff; --bg-1: #f7f2ff; --bg-2: #f0fbff;
      --card: rgba(255,255,255,0.78);
      --card-border: 255,255,255;
      --text: #0f172a; --muted: #475569; --ring: #7c3aed;
      --cta-0: #7c3aed; --cta-1: #6366f1;
      --chip-bg: #f1f5f9; --chip-text: #0f172a; --chip-border: #e2e8f0;
      --ok: #10b981; --warn: #f59e0b;

      /* Kid mode overrides (applied when body.kid) */
      --kid-cta-0: #22c55e; --kid-cta-1: #10b981; /* green gradient */
      --kid-chip-bg: #fff7ed; /* peach */
      --kid-chip-border: #fed7aa;
      --kid-ring: #22c55e;
    }
    @media (prefers-color-scheme: dark) {
      :root { --bg-0:#0b1021; --bg-1:#0d0f1a; --bg-2:#0a1320; --card:rgba(17,24,39,0.7); --card-border:148,163,184; --text:#e5e7eb; --muted:#94a3b8; --ring:#a78bfa; --cta-0:#a78bfa; --cta-1:#60a5fa; --chip-bg:rgba(148,163,184,0.12); --chip-text:#e5e7eb; --chip-border:rgba(148,163,184,0.25); }
    }

    html, body { height: 100%; margin: 0; }

    /* Background you liked */
    .bg { position: fixed; inset: 0; overflow: hidden; background:
      radial-gradient(40% 35% at 35% 45%, rgba(255,184,150,0.70) 0%, rgba(255,184,150,0.00) 60%),
      radial-gradient(45% 40% at 78% 18%, rgba(192,173,255,0.65) 0%, rgba(192,173,255,0.00) 62%),
      radial-gradient(55% 50% at 88% 55%, rgba(140,180,255,0.55) 0%, rgba(140,180,255,0.00) 65%),
      radial-gradient(50% 45% at 8% 30%, rgba(255,150,170,0.45) 0%, rgba(255,150,170,0.00) 65%),
      radial-gradient(35% 30% at 55% 45%, rgba(255,214,153,0.55) 0%, rgba(255,214,153,0.00) 70%),
      linear-gradient(180deg, var(--bg-0) 0%, var(--bg-1) 40%, var(--bg-2) 100%);
      filter: blur(0.3px);
    }
    .bg::after { content: ""; position: absolute; inset: -2vmax; pointer-events:none; background: radial-gradient(100% 100% at 50% 50%, rgba(0,0,0,0) 60%, rgba(0,0,0,0.06) 100%); mix-blend-mode: multiply; }
    @media (prefers-reduced-motion: no-preference) {
      .bg { animation: drift 16s ease-in-out infinite alternate; }
      @keyframes drift { 0% { filter: blur(0.3px) saturate(100%);} 100% { filter: blur(0.6px) saturate(108%);} }
    }

    /* Layout */
    .shell { position: relative; height: 100%; display: grid; place-items: center; padding: 4vmin; font-family: ui-rounded, system-ui, -apple-system, \"Segoe UI\", Roboto, Inter, \"Helvetica Neue\", Arial; color: var(--text); }
    .card { width: min(920px, 92vw); background: linear-gradient(180deg, rgba(var(--card-border),0.35), rgba(var(--card-border),0.12)) border-box, var(--card); border: 1px solid rgba(var(--card-border),0.35); border-radius: 24px; box-shadow: 0 10px 40px rgba(2,6,23,0.15); backdrop-filter: blur(12px); padding: 1.25rem; }

    .header { display:flex; align-items:center; justify-content:space-between; gap:1rem; margin-bottom: 0.5rem; }
    .left { display:flex; align-items:center; gap:0.75rem; }
    .logo { width: 44px; height: 44px; border-radius: 12px; display:grid; place-items:center; background: radial-gradient(80% 80% at 30% 30%, rgba(255,255,255,0.85), rgba(255,255,255,0.5)); border: 1px solid rgba(var(--card-border),0.4); box-shadow: 0 6px 24px rgba(2,6,23,0.15) inset; }
    .title { font-weight: 900; letter-spacing: 0.2px; font-size: clamp(1.1rem, 2.4vw, 1.4rem); }
    .subtitle { color: var(--muted); font-size: 0.95rem; }

    .mode { display:flex; align-items:center; gap:0.5rem; }
    .switch { position: relative; width: 56px; height: 32px; background: #e2e8f0; border-radius: 999px; transition: background .2s; cursor: pointer; outline: 2px solid transparent; }
    .switch::after { content:\"\"; position:absolute; top:3px; left:3px; width:26px; height:26px; background:white; border-radius: 50%; box-shadow: 0 1px 4px rgba(2,6,23,0.2); transition: transform .2s; }
    .switch[aria-checked=\"true\"] { background: linear-gradient(90deg, var(--ok), var(--kid-cta-1)); }
    .switch[aria-checked=\"true\"]::after { transform: translateX(24px); }
    .switch:focus-visible { box-shadow: 0 0 0 4px rgba(34,197,94,0.2); }

    form { display: grid; gap: 0.9rem; }
    .search-row { display:grid; grid-template-columns: 1fr auto; gap:0.6rem; align-items:center; }

    .input-wrap { position:relative; }
    .icon { position:absolute; left:14px; top:50%; transform: translateY(-50%); }
    .search-input { width:100%; padding: 1.1rem 1rem 1.1rem 48px; font-size: clamp(1.05rem, 2.3vw, 1.2rem); border: 2px solid rgba(148,163,184,0.35); border-radius: 16px; outline:none; background: linear-gradient(180deg, rgba(255,255,255,0.7), rgba(255,255,255,0.5)); }
    .search-input::placeholder { color:#94a3b8; }
    .search-input:focus-visible { box-shadow: 0 0 0 4px rgba(124,58,237,0.18); border-color: var(--ring); }

    .btn { border:none; cursor:pointer; white-space:nowrap; border-radius: 14px; padding: 1rem 1.25rem; font-weight:800; letter-spacing:0.2px; color:white; background: linear-gradient(135deg, var(--cta-0), var(--cta-1)); box-shadow: 0 8px 24px rgba(99,102,241,0.35); transition: transform .08s, box-shadow .2s, filter .2s; }
    .btn:hover { transform: translateY(-1px); filter:saturate(1.05); box-shadow: 0 10px 28px rgba(99,102,241,0.45); }

    /* Kid mode visual tweaks */
    body.kid .btn { background: linear-gradient(135deg, var(--kid-cta-0), var(--kid-cta-1)); }
    body.kid .search-input { border-color: var(--kid-ring); box-shadow: 0 0 0 4px rgba(34,197,94,0.18); font-weight:700; }

    .quick-label { color: var(--muted); font-weight: 700; margin-top: 0.2rem; }
    .quick-links { display:flex; flex-wrap:wrap; gap:0.6rem; }
    .chip { display:inline-flex; align-items:center; gap:8px; text-decoration:none; padding: 0.7rem 1rem; border-radius: 999px; font-weight: 800; font-size: 1rem; color: var(--chip-text); background: var(--chip-bg); border: 2px solid var(--chip-border); transition: border-color .2s, transform .06s, background .2s; }
    .chip:hover { border-color: var(--ring); transform: translateY(-1px); }

    /* Larger, friendlier chips in Kid mode + emojis */
    body.kid .chip { font-size: 1.05rem; padding: 0.8rem 1.1rem; background: var(--kid-chip-bg); border-color: var(--kid-chip-border); }

    .assist { display:flex; gap:.6rem; align-items:center; flex-wrap:wrap; }
    .assist button { border-radius: 12px; border: 2px solid #e2e8f0; background: white; padding: .7rem 1rem; font-weight: 700; cursor: pointer; }

    .foot { display:flex; justify-content:space-between; align-items:center; margin-top:.5rem; color: var(--muted); font-size: .95rem; }
    .foot .right { display:flex; gap:.75rem; align-items:center; }

    /* Accessibility: focus-visible for all interactive elements */
    :is(a, button, .switch):focus-visible { outline: 3px solid rgba(124,58,237,0.35); outline-offset: 2px; }
    body.kid :is(a, button, .switch):focus-visible { outline-color: rgba(34,197,94,0.5); }

    @media (max-width: 560px) {
      .foot { flex-direction: column; gap: .4rem; align-items: flex-start; }
    }
  </style>
</head>
<body>
  <div class=\"bg\" aria-hidden=\"true\"></div>
  <div class=\"shell\">
    <main class=\"card\" role=\"main\" aria-label=\"ABLE Bible search\">
      <header class=\"header\">
        <div class=\"left\">
          <div class=\"logo\" aria-hidden=\"true\">
            <svg width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" style=\"color: var(--ring)\"><path d=\"M12 2v20M5 9h14\"/></svg>
          </div>
          <div>
            <div class=\"title\">ABLE — Bible Search</div>
            <div class=\"subtitle\">Grade‑1 friendly • NIV/Berean references</div>
          </div>
        </div>
        <div class=\"mode\">
          <label id=\"kidlbl\" class=\"subtitle\" for=\"kid\">Kid mode</label>
          <div id=\"kid\" class=\"switch\" role=\"switch\" aria-checked=\"false\" tabindex=\"0\" aria-labelledby=\"kidlbl\"></div>
        </div>
      </header>

      <form method=\"get\" action=\"/search\" role=\"search\" aria-label=\"Search form\">
        <div class=\"search-row\">
          <div class=\"input-wrap\">
            <label class=\"sr-only\" for=\"q\">Search Bible</label>
            <span class=\"icon\" aria-hidden=\"true\">
              <svg width=\"22\" height=\"22\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"#94a3b8\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><circle cx=\"11\" cy=\"11\" r=\"8\"></circle><path d=\"m21 21-4.3-4.3\"></path></svg>
            </span>
            <input id=\"q\" class=\"search-input\" type=\"text\" name=\"q\" placeholder=\"Type words or verse (e.g., Psalm 23)\" autocomplete=\"off\" aria-describedby=\"help\" />
          </div>
          <button class=\"btn\" type=\"submit\" aria-label=\"Search\">Search</button>
        </div>

        <div id=\"help\" class=\"quick-label\">Quick picks</div>
        <nav class=\"quick-links\" aria-label=\"Quick picks\">
          <a class=\"chip\" href=\"/search?q=Psalm+23\">🧑‍🌾 Psalm 23</a>
          <a class=\"chip\" href=\"/search?q=John+1\">✨ John 1</a>
          <a class=\"chip\" href=\"/search?q=Genesis+1\">🌍 Genesis 1</a>
          <a class=\"chip\" href=\"/search?q=Romans+8\">❤️ Romans 8</a>
          <a class=\"chip\" href=\"/search?q=Isaiah+53\">🕊️ Isaiah 53</a>
        </nav>

        <div class=\"assist\" aria-label=\"Helpers\">
          <button type=\"button\" id=\"speak\" aria-live=\"polite\" title=\"Read the quick picks out loud\">🔊 Read aloud</button>
          <button type=\"button\" id=\"clear\" title=\"Clear search\">🧽 Clear</button>
        </div>

        <footer class=\"foot\">
          <div>Tip: Press <b>/</b> to focus search • Tap chips</div>
          <div class=\"right\"><span>Kid‑friendly UI • Large touch targets • WCAG AA</span></div>
        </footer>
      </form>
    </main>
  </div>

  <script>
    // Toggle kid mode (adds .kid to body)
    const kid = document.getElementById('kid');
    const q = document.getElementById('q');
    const speakBtn = document.getElementById('speak');
    const clearBtn = document.getElementById('clear');

    function setKid(on) {
      document.body.classList.toggle('kid', on);
      kid.setAttribute('aria-checked', on ? 'true' : 'false');
      localStorage.setItem('able.kidMode', on ? '1' : '0');
      q.placeholder = on ? 'Type easy words here… (e.g., God loves you)' : 'Type words or verse (e.g., Psalm 23)';
    }

    kid.addEventListener('click', () => setKid(kid.getAttribute('aria-checked') !== 'true'));
    kid.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); kid.click(); } });

    // Load saved preference
    setKid(localStorage.getItem('able.kidMode') === '1');

    // Keyboard shortcut to focus search
    window.addEventListener('keydown', (e) => { if (e.key === '/') { e.preventDefault(); q.focus(); } });

    // Read aloud using SpeechSynthesis (browser-provided)
    function speak(text) {
      try {
        const u = new SpeechSynthesisUtterance(text);
        u.rate = document.body.classList.contains('kid') ? 0.9 : 1.0;
        speechSynthesis.cancel();
        speechSynthesis.speak(u);
      } catch (e) { /* no-op if unsupported */ }
    }
    speakBtn?.addEventListener('click', () => {
      const chips = Array.from(document.querySelectorAll('.quick-links a')).map(a => a.textContent.trim()).join(', ');
      speak('Quick picks: ' + chips);
    });

    // Clear input
    clearBtn?.addEventListener('click', () => { q.value = ''; q.focus(); });
  </script>
</body>
</html>
    """


@app.get("/search", response_class=HTMLResponse)
async def search(q: str = ""):
    return f"""
<!doctype html>
<html lang=\"en\"><head>
<meta charset=\"utf-8\" /><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
<title>Results for {q}</title>
<style>
  body{{font-family: ui-rounded, system-ui, -apple-system, Segoe UI, Roboto, Inter, \"Helvetica Neue\", Arial; margin:0; color:#0f172a;}}
  .wrap{{max-width:920px;margin:6vmin auto;padding:0 4vmin;}}
  .crumbs a{{color:#6366f1;text-decoration:none;font-weight:700}}
  .panel{{margin-top:16px;background:#ffffffcc;border:1px solid #e2e8f0;border-radius:18px;padding:16px;box-shadow:0 8px 24px rgba(2,6,23,0.06);}}
  .muted{{color:#64748b}}
  @media (prefers-color-scheme: dark){{ body{{color:#e5e7eb;background:#0b1021}} .panel{{background:rgba(17,24,39,0.7);border-color:#334155}} .crumbs a{{color:#a78bfa}} .muted{{color:#94a3b8}} }}
</style></head>
<body>
  <div class=\"wrap\">
    <div class=\"crumbs\"><a href=\"/\">← Back</a></div>
    <div class=\"panel\">
      <h2 style=\"margin:0 0 6px\">You searched for: <em>{q}</em></h2>
      <p class=\"muted\">(Connect results to ABLE engine later — with NIV/Berean citations.)</p>
    </div>
  </div>
</body></html>
    """
