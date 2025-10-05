from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Bible Search</title>
  <style>
    :root {
      --bg-0: #f2f6ff;
      --bg-1: #f7f2ff;
      --bg-2: #f0fbff;
      --card: rgba(255,255,255,0.78);
      --card-border: 255,255,255;
      --text: #0f172a;          /* slate-900 */
      --muted: #475569;         /* slate-600 */
      --ring: #7c3aed;          /* violet-600 */
      --cta-0: #7c3aed;         /* violet-600 */
      --cta-1: #6366f1;         /* indigo-500 */
      --chip-bg: #f1f5f9;       /* slate-100 */
      --chip-text: #0f172a;     /* slate-900 */
      --chip-border: #e2e8f0;   /* slate-200 */
    }

    @media (prefers-color-scheme: dark) {
      :root {
        --bg-0: #0b1021;
        --bg-1: #0d0f1a;
        --bg-2: #0a1320;
        --card: rgba(17, 24, 39, 0.7);
        --card-border: 148,163,184; /* slate-400 */
        --text: #e5e7eb;        /* slate-200 */
        --muted: #94a3b8;       /* slate-400 */
        --ring: #a78bfa;        /* violet-400 */
        --cta-0: #a78bfa;
        --cta-1: #60a5fa;       /* blue-400 */
        --chip-bg: rgba(148,163,184,0.12);
        --chip-text: #e5e7eb;
        --chip-border: rgba(148,163,184,0.25);
      }
    }

    html, body { height: 100%; margin: 0; }

    /* Pastel blob background you liked */
    .bg {
      position: fixed; inset: 0; overflow: hidden;
      background:
        radial-gradient(40% 35% at 35% 45%, rgba(255,184,150,0.70) 0%, rgba(255,184,150,0.00) 60%),
        radial-gradient(45% 40% at 78% 18%, rgba(192,173,255,0.65) 0%, rgba(192,173,255,0.00) 62%),
        radial-gradient(55% 50% at 88% 55%, rgba(140,180,255,0.55) 0%, rgba(140,180,255,0.00) 65%),
        radial-gradient(50% 45% at 8% 30%, rgba(255,150,170,0.45) 0%, rgba(255,150,170,0.00) 65%),
        radial-gradient(35% 30% at 55% 45%, rgba(255,214,153,0.55) 0%, rgba(255,214,153,0.00) 70%),
        linear-gradient(180deg, var(--bg-0) 0%, var(--bg-1) 40%, var(--bg-2) 100%);
      filter: blur(0.3px);
    }
    .bg::after {
      content: ""; position: absolute; inset: -2vmax; pointer-events: none;
      background: radial-gradient(100% 100% at 50% 50%, rgba(0,0,0,0) 60%, rgba(0,0,0,0.06) 100%);
      mix-blend-mode: multiply;
    }
    @media (prefers-reduced-motion: no-preference) {
      .bg { animation: drift 16s ease-in-out infinite alternate; }
      @keyframes drift { 0% { filter: blur(0.3px) saturate(100%);} 100% { filter: blur(0.6px) saturate(108%);} }
    }

    .shell {
      position: relative; height: 100%; display: grid; place-items: center; padding: 4vmin;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Inter, "Helvetica Neue", Arial, "Apple Color Emoji", "Segoe UI Emoji";
      color: var(--text);
    }

    .card {
      width: min(900px, 92vw);
      background: linear-gradient(180deg, rgba(var(--card-border),0.35), rgba(var(--card-border),0.12)) border-box,
                  var(--card);
      border: 1px solid rgba(var(--card-border),0.35);
      border-radius: 20px;
      box-shadow: 0 10px 40px rgba(2,6,23,0.15);
      -webkit-backdrop-filter: blur(10px);
      backdrop-filter: blur(10px);
      padding: 1.25rem;
    }

    .header {
      display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;
    }
    .logo {
      width: 36px; height: 36px; border-radius: 10px; display: grid; place-items: center;
      background: radial-gradient(80% 80% at 30% 30%, rgba(255,255,255,0.8), rgba(255,255,255,0.4));
      border: 1px solid rgba(var(--card-border),0.4);
      box-shadow: 0 6px 24px rgba(2,6,23,0.15) inset;
    }
    .title { font-weight: 800; letter-spacing: 0.2px; font-size: clamp(1.1rem, 2.2vw, 1.35rem); }
    .subtitle { color: var(--muted); font-size: 0.95rem; }

    form { display: grid; gap: 0.9rem; }

    .search-row { position: relative; display: grid; grid-template-columns: 1fr auto; gap: 0.6rem; align-items: center; }

    .input-wrap { position: relative; }
    .icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); display: grid; place-items: center; }
    .search-input {
      width: 100%; padding: 1rem 1rem 1rem 44px; font-size: clamp(1rem, 2.2vw, 1.1rem);
      border: 1px solid rgba(148,163,184,0.35);
      border-radius: 14px; outline: none; color: var(--text);
      background: linear-gradient(180deg, rgba(255,255,255,0.65), rgba(255,255,255,0.45));
    }
    .search-input::placeholder { color: #94a3b8; }
    .search-input:focus-visible { box-shadow: 0 0 0 4px rgba(124,58,237,0.15); border-color: var(--ring); }

    .kbd { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 0.78rem; color: var(--muted); }

    .btn {
      border: none; cursor: pointer; white-space: nowrap; border-radius: 12px; padding: 0.9rem 1.2rem;
      font-weight: 700; letter-spacing: 0.2px; color: white;
      background: linear-gradient(135deg, var(--cta-0), var(--cta-1));
      box-shadow: 0 8px 24px rgba(99,102,241,0.35);
      transition: transform 0.08s ease, box-shadow 0.2s ease, filter 0.2s ease;
    }
    .btn:hover { transform: translateY(-1px); filter: saturate(1.05); box-shadow: 0 10px 28px rgba(99,102,241,0.45); }
    .btn:active { transform: translateY(0); }

    .quick-label { color: var(--muted); font-weight: 600; margin-top: 0.4rem; }

    .quick-links { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.25rem; }
    .chip {
      display: inline-flex; align-items: center; gap: 8px; text-decoration: none;
      padding: 0.55rem 0.8rem; border-radius: 999px; font-weight: 600; font-size: 0.92rem;
      color: var(--chip-text); background: var(--chip-bg); border: 1px solid var(--chip-border);
      transition: border-color 0.2s ease, transform 0.06s ease, background 0.2s ease;
    }
    .chip:hover { border-color: var(--ring); transform: translateY(-1px); }

    .sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }

    .foot { display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem; color: var(--muted); font-size: 0.9rem; }
    .foot .right { display: flex; gap: 0.75rem; align-items: center; }

    @media (max-width: 520px) {
      .btn { padding-inline: 1rem; }
      .foot { flex-direction: column; gap: 0.4rem; align-items: flex-start; }
    }
  </style>
</head>
<body>
  <div class="bg" aria-hidden="true"></div>
  <div class="shell">
    <main class="card" role="main" aria-label="Bible search">
      <header class="header">
        <div class="logo" aria-hidden="true">
          <!-- simple cross mark -->
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--ring)"><path d="M12 2v20M5 9h14"/></svg>
        </div>
        <div>
          <div class="title">Bible Search</div>
          <div class="subtitle">Find verses fast — NIV / Berean friendly</div>
        </div>
      </header>

      <form method="get" action="/search" role="search" aria-label="Search form">
        <div class="search-row">
          <div class="input-wrap">
            <label class="sr-only" for="q">Search Bible</label>
            <span class="icon" aria-hidden="true">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.3-4.3"></path></svg>
            </span>
            <input id="q" class="search-input" type="text" name="q" placeholder="e.g., Psalm 23, \"love your enemies\", Romans 8:28" autocomplete="off" />
          </div>
          <button class="btn" type="submit">Search</button>
        </div>

        <div class="quick-label">Quick picks</div>
        <nav class="quick-links" aria-label="Quick picks">
          <a class="chip" href="/search?q=Psalm+23">Psalm 23</a>
          <a class="chip" href="/search?q=John+1">John 1</a>
          <a class="chip" href="/search?q=Genesis+1">Genesis 1</a>
          <a class="chip" href="/search?q=Romans+8">Romans 8</a>
          <a class="chip" href="/search?q=Isaiah+53">Isaiah 53</a>
        </nav>

        <footer class="foot">
          <div>Tip: Press <span class="kbd">/</span> to focus search</div>
          <div class="right"><span>Modern UI • Glass • Dark‑mode aware</span></div>
        </footer>
      </form>
    </main>
  </div>

  <script>
    // Keyboard shortcut to focus the search field
    const q = document.getElementById('q');
    window.addEventListener('keydown', (e) => {
      if (e.key === '/') {
        e.preventDefault(); q.focus();
      }
    });
  </script>
</body>
</html>
    """


@app.get("/search", response_class=HTMLResponse)
async def search(q: str = ""):
    # Simple placeholder results container (kept minimal)
    return f"""
<!doctype html>
<html lang=\"en\"><head>
<meta charset=\"utf-8\" /><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
<title>Results for {q}</title>
<style>
  body{{font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Inter, \"Helvetica Neue\", Arial; margin:0; color:#0f172a;}}
  .wrap{{max-width:900px;margin:6vmin auto;padding:0 4vmin;}}
  .crumbs a{{color:#6366f1;text-decoration:none;font-weight:600}}
  .panel{{margin-top:16px;background:#ffffffcc;border:1px solid #e2e8f0;border-radius:16px;padding:16px;box-shadow:0 8px 24px rgba(2,6,23,0.06);}}
  .muted{{color:#64748b}}
  @media (prefers-color-scheme: dark){{
    body{{color:#e5e7eb;background:#0b1021}}
    .panel{{background:rgba(17,24,39,0.7);border-color:#334155}}
    .crumbs a{{color:#a78bfa}}
    .muted{{color:#94a3b8}}
  }}
</style></head>
<body>
  <div class=\"wrap\">
    <div class=\"crumbs\"><a href=\"/\">← Back</a></div>
    <div class=\"panel\">
      <h2 style=\"margin:0 0 6px\">You searched for: <em>{q}</em></h2>
      <p class=\"muted\">(Hook up to your search endpoint next.)</p>
    </div>
  </div>
</body></html>
    """
