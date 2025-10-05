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
       MODERN THEME TOKENS
    ------------------------------------------- */
    :root {
      --bg-0: #0f0f23; --bg-1: #1a1a2e; --bg-2: #16213e;
      --card: rgba(255,255,255,0.08);
      --card-border: 255,255,255;
      --text: #ffffff; --muted: #a0a9c0; --ring: #6366f1;
      --cta-0: #6366f1; --cta-1: #8b5cf6;
      --chip-bg: rgba(255,255,255,0.05); --chip-text: #e5e7eb; --chip-border: rgba(255,255,255,0.12);
      --ok: #10b981; --warn: #f59e0b;
      --accent: #06b6d4;

      /* Kid mode overrides */
      --kid-cta-0: #22c55e; --kid-cta-1: #10b981;
      --kid-chip-bg: rgba(34,197,94,0.1);
      --kid-chip-border: rgba(34,197,94,0.2);
      --kid-ring: #22c55e;
    }

    * { box-sizing: border-box; }
    html, body { height: 100%; margin: 0; overflow-x: hidden; }

    /* Modern animated background */
    .bg { 
      position: fixed; inset: 0; 
      background: 
        radial-gradient(circle at 20% 80%, rgba(120,119,198,0.3) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(255,119,198,0.25) 0%, transparent 50%),
        radial-gradient(circle at 40% 40%, rgba(99,102,241,0.2) 0%, transparent 50%),
        linear-gradient(135deg, var(--bg-0) 0%, var(--bg-1) 50%, var(--bg-2) 100%);
    }
    
    .bg::before {
      content: '';
      position: absolute;
      inset: 0;
      background: 
        repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(255,255,255,0.01) 2px, rgba(255,255,255,0.01) 4px),
        repeating-linear-gradient(90deg, transparent, transparent 2px, rgba(255,255,255,0.01) 2px, rgba(255,255,255,0.01) 4px);
      opacity: 0.5;
    }

    @media (prefers-reduced-motion: no-preference) {
      .bg { animation: gradient-shift 20s ease-in-out infinite alternate; }
      @keyframes gradient-shift { 
        0% { filter: hue-rotate(0deg) brightness(1); }
        100% { filter: hue-rotate(10deg) brightness(1.05); }
      }
    }

    /* Modern layout */
    .shell { 
      position: relative; height: 100vh; display: flex; align-items: center; justify-content: center;
      padding: 2rem; font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, sans-serif; 
      color: var(--text); line-height: 1.6;
    }
    
    .card { 
      width: min(580px, 100%); 
      background: var(--card);
      border: 1px solid rgba(var(--card-border),0.1);
      border-radius: 32px; 
      backdrop-filter: blur(24px) saturate(180%);
      box-shadow: 
        0 32px 64px rgba(0,0,0,0.25),
        inset 0 1px 0 rgba(255,255,255,0.1);
      padding: 2.5rem; 
      position: relative;
    }

    .card::before {
      content: '';
      position: absolute;
      inset: 0;
      border-radius: 32px;
      padding: 1px;
      background: linear-gradient(135deg, rgba(255,255,255,0.2), rgba(255,255,255,0.05));
      mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
      mask-composite: xor;
      -webkit-mask-composite: xor;
    }

    .header { 
      display: flex; align-items: center; justify-content: space-between; 
      gap: 1.5rem; margin-bottom: 2rem; flex-wrap: wrap;
    }
    
    .left { display: flex; align-items: center; gap: 1rem; }
    
    .logo { 
      width: 56px; height: 56px; border-radius: 16px; display: grid; place-items: center;
      background: linear-gradient(135deg, var(--cta-0), var(--cta-1));
      box-shadow: 0 8px 32px rgba(99,102,241,0.3);
      position: relative;
    }
    
    .logo::before {
      content: '';
      position: absolute;
      inset: 2px;
      border-radius: 14px;
      background: linear-gradient(135deg, rgba(255,255,255,0.2), rgba(255,255,255,0.05));
    }
    
    .title { 
      font-weight: 800; font-size: 1.75rem; letter-spacing: -0.02em;
      background: linear-gradient(135deg, var(--text), var(--muted));
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    
    .subtitle { 
      color: var(--muted); font-size: 0.875rem; font-weight: 500;
      margin-top: 0.25rem;
    }

    .mode { display: flex; align-items: center; gap: 0.75rem; }
    
    .switch { 
      position: relative; width: 64px; height: 36px; 
      background: rgba(255,255,255,0.1); 
      border: 1px solid rgba(255,255,255,0.2);
      border-radius: 999px; transition: all .3s ease; cursor: pointer; 
    }
    
    .switch::after { 
      content: ""; position: absolute; top: 3px; left: 3px; 
      width: 28px; height: 28px; 
      background: linear-gradient(135deg, #fff, #f1f5f9); 
      border-radius: 50%; 
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      transition: all .3s cubic-bezier(0.4, 0, 0.2, 1); 
    }
    
    .switch[aria-checked="true"] { 
      background: linear-gradient(135deg, var(--kid-cta-0), var(--kid-cta-1)); 
      border-color: var(--kid-cta-0);
    }
    
    .switch[aria-checked="true"]::after { transform: translateX(28px); }
    
    .switch:focus-visible { 
      outline: none;
      box-shadow: 0 0 0 4px rgba(34,197,94,0.2); 
    }

    form { display: grid; gap: 1.5rem; }
    
    .search-row { display: grid; grid-template-columns: 1fr auto; gap: 1rem; align-items: end; }

    .input-wrap { position: relative; }
    
    .icon { 
      position: absolute; left: 1.25rem; top: 50%; transform: translateY(-50%); 
      z-index: 2; color: var(--muted);
    }
    
    .search-input { 
      width: 100%; padding: 1.25rem 1.25rem 1.25rem 3.5rem; 
      font-size: 1.125rem; font-weight: 500;
      border: 2px solid rgba(255,255,255,0.1); 
      border-radius: 20px; outline: none; 
      background: rgba(255,255,255,0.05);
      color: var(--text);
      backdrop-filter: blur(12px);
      transition: all .3s ease;
    }
    
    .search-input::placeholder { color: var(--muted); }
    
    .search-input:focus { 
      border-color: var(--ring); 
      background: rgba(255,255,255,0.08);
      box-shadow: 0 0 0 4px rgba(99,102,241,0.1), 0 8px 32px rgba(99,102,241,0.15); 
    }

    .btn { 
      border: none; cursor: pointer; white-space: nowrap; 
      border-radius: 16px; padding: 1.25rem 2rem; 
      font-weight: 700; font-size: 1rem; letter-spacing: 0.02em;
      color: white; 
      background: linear-gradient(135deg, var(--cta-0), var(--cta-1)); 
      box-shadow: 0 8px 32px rgba(99,102,241,0.3);
      transition: all .2s ease; 
      position: relative;
    }
    
    .btn::before {
      content: '';
      position: absolute;
      inset: 0;
      border-radius: 16px;
      background: linear-gradient(135deg, rgba(255,255,255,0.2), rgba(255,255,255,0.05));
      opacity: 0;
      transition: opacity .2s ease;
    }
    
    .btn:hover { 
      transform: translateY(-2px); 
      box-shadow: 0 12px 40px rgba(99,102,241,0.4); 
    }
    
    .btn:hover::before { opacity: 1; }

    /* Kid mode visual tweaks */
    body.kid .btn { background: linear-gradient(135deg, var(--kid-cta-0), var(--kid-cta-1)); }
    body.kid .search-input:focus { border-color: var(--kid-ring); box-shadow: 0 0 0 4px rgba(34,197,94,0.1); }

    .quick-label { 
      color: var(--text); font-weight: 700; font-size: 1.125rem;
      margin-bottom: 0.5rem;
    }
    
    .quick-links { 
      display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); 
      gap: 1rem; 
    }
    
    .chip { 
      display: flex; align-items: center; justify-content: center; gap: 0.5rem;
      text-decoration: none; padding: 1rem 1.25rem; 
      border-radius: 16px; font-weight: 600; font-size: 0.95rem; 
      color: var(--chip-text); 
      background: var(--chip-bg); 
      border: 1px solid var(--chip-border); 
      backdrop-filter: blur(12px);
      transition: all .2s ease; 
      text-align: center;
    }
    
    .chip:hover { 
      border-color: var(--ring); 
      background: rgba(255,255,255,0.08);
      transform: translateY(-2px); 
      box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    }

    body.kid .chip { 
      background: var(--kid-chip-bg); 
      border-color: var(--kid-chip-border); 
      font-size: 1rem;
    }

    .assist { 
      display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; 
      margin-top: 0.5rem;
    }
    
    .assist button { 
      border-radius: 12px; 
      border: 1px solid rgba(255,255,255,0.15); 
      background: rgba(255,255,255,0.05); 
      color: var(--text);
      padding: 0.75rem 1rem; font-weight: 600; cursor: pointer; 
      backdrop-filter: blur(12px);
      transition: all .2s ease;
    }
    
    .assist button:hover {
      background: rgba(255,255,255,0.1);
      transform: translateY(-1px);
    }

    .foot { 
      display: flex; justify-content: space-between; align-items: center; 
      margin-top: 1.5rem; color: var(--muted); font-size: 0.875rem; 
      flex-wrap: wrap; gap: 1rem;
    }

    /* Accessibility improvements */
    :is(a, button, .switch):focus-visible { 
      outline: 3px solid rgba(99,102,241,0.5); 
      outline-offset: 2px; 
    }
    
    body.kid :is(a, button, .switch):focus-visible { 
      outline-color: rgba(34,197,94,0.6); 
    }

    @media (max-width: 640px) {
      .shell { padding: 1rem; }
      .card { padding: 1.5rem; }
      .header { flex-direction: column; align-items: flex-start; gap: 1rem; }
      .search-row { grid-template-columns: 1fr; gap: 1rem; }
      .btn { width: 100%; }
      .quick-links { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="bg" aria-hidden="true"></div>
  <div class="shell">
    <main class="card" role="main" aria-label="ABLE Bible search">
      <header class="header">
        <div class="left">
          <div class="logo" aria-hidden="true">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M5 9h14"/></svg>
          </div>
          <div>
            <div class="title">ABLE</div>
            <div class="subtitle">Special needs Bible search</div>
          </div>
        </div>
        <div class="mode">
          <label id="kidlbl" class="subtitle" for="kid">Kid mode</label>
          <div id="kid" class="switch" role="switch" aria-checked="false" tabindex="0" aria-labelledby="kidlbl"></div>
        </div>
      </header>

      <form method="get" action="/search" role="search" aria-label="Search form">
        <div class="search-row">
          <div class="input-wrap">
            <label class="sr-only" for="q">Search Bible</label>
            <span class="icon" aria-hidden="true">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.3-4.3"></path></svg>
            </span>
            <input id="q" class="search-input" type="text" name="q" placeholder="Search the Bible..." autocomplete="off" aria-describedby="help" />
          </div>
          <button class="btn" type="submit" aria-label="Search">Search</button>
        </div>

        <div>
          <div id="help" class="quick-label">Popular passages</div>
          <nav class="quick-links" aria-label="Quick picks">
            <a class="chip" href="/search?q=Psalm+23">🐑 Psalm 23</a>
            <a class="chip" href="/search?q=John+3:16">💝 John 3:16</a>
            <a class="chip" href="/search?q=Genesis+1">🌍 Genesis 1</a>
            <a class="chip" href="/search?q=Romans+8">❤️ Romans 8</a>
            <a class="chip" href="/search?q=Isaiah+53">✨ Isaiah 53</a>
            <a class="chip" href="/search?q=Matthew+5">⛰️ Matthew 5</a>
          </nav>
        </div>

        <div class="assist" aria-label="Helpers">
          <button type="button" id="speak" aria-live="polite" title="Read the popular passages out loud">🔊 Read aloud</button>
          <button type="button" id="clear" title="Clear search">✨ Clear</button>
        </div>

        <footer class="foot">
          <div>Press <kbd>/</kbd> to search quickly</div>
          <div>Designed for accessibility</div>
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
      q.placeholder = on ? 'Type simple words here...' : 'Search the Bible...';
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
<title>Results for {q} • ABLE</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ 
    font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, sans-serif; 
    margin: 0; color: #ffffff; line-height: 1.6;
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
    min-height: 100vh;
  }}
  .wrap {{ max-width: 920px; margin: 0 auto; padding: 2rem; }}
  .crumbs {{ margin-bottom: 2rem; }}
  .crumbs a {{ 
    color: #6366f1; text-decoration: none; font-weight: 700; 
    padding: 0.75rem 1.5rem; background: rgba(255,255,255,0.05);
    border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);
    transition: all .2s ease;
  }}
  .crumbs a:hover {{ background: rgba(255,255,255,0.1); transform: translateY(-1px); }}
  .panel {{ 
    background: rgba(255,255,255,0.08); 
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 24px; padding: 2rem; 
    backdrop-filter: blur(24px);
    box-shadow: 0 32px 64px rgba(0,0,0,0.25);
  }}
  .muted {{ color: #a0a9c0; }}
  h2 {{ margin: 0 0 1rem; font-weight: 800; font-size: 1.5rem; }}
</style></head>
<body>
  <div class="wrap">
    <div class="crumbs"><a href="/">← Back to ABLE</a></div>
    <div class="panel">
      <h2>Results for: <em>{q}</em></h2>
      <p class="muted">ABLE Bible search results will appear here with special needs-friendly formatting and audio support.</p>
    </div>
  </div>
</body></html>
    """
