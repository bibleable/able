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
  <title>ABLE Bible Search</title>
  <style>
    :root {
      --bg: #f8fafc;
      --card: #ffffff;
      --text: #0f172a;
      --muted: #64748b;
      --primary: #7c3aed;
      --border: #e2e8f0;
    }

    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #0f172a;
        --card: #1e293b;
        --text: #f1f5f9;
        --muted: #94a3b8;
        --border: #334155;
      }
    }

    body {
      font-family: system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 20px;
    }

    .container {
      max-width: 600px;
      margin: 0 auto;
      padding-top: 5vh;
    }

    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 1.5rem;
    }

    .title {
      font-size: 1.5rem;
      font-weight: bold;
    }

    .subtitle {
      font-size: 0.9rem;
      color: var(--muted);
    }

    .search-container {
      position: relative;
      margin-bottom: 1rem;
    }

    .search-input {
      width: 100%;
      padding: 12px 12px 12px 40px;
      font-size: 1rem;
      border: 2px solid var(--border);
      border-radius: 8px;
      background: var(--card);
      color: var(--text);
    }

    .search-icon {
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--muted);
    }

    .search-button {
      display: block;
      width: 100%;
      padding: 12px;
      margin-top: 10px;
      background: var(--primary);
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 1rem;
      font-weight: bold;
      cursor: pointer;
    }

    .quick-picks {
      margin-top: 1.5rem;
    }

    .quick-label {
      color: var(--muted);
      margin-bottom: 8px;
      font-weight: 500;
    }

    .chips {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .chip {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 8px 12px;
      font-size: 0.9rem;
      text-decoration: none;
      color: var(--text);
    }
  </style>
</head>
<body>
  <div class="container">
    <header class="header">
      <div>
        <div class="title">ABLE Bible Search</div>
        <div class="subtitle">Grade-1 friendly • NIV/Berean references</div>
      </div>
    </header>

    <form method="get" action="/search">
      <div class="search-container">
        <span class="search-icon">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.3-4.3"></path></svg>
        </span>
        <input id="q" class="search-input" type="text" name="q" placeholder="Search the Bible..." />
      </div>
      
      <button class="search-button" type="submit">Search</button>
    </form>

    <div class="quick-picks">
      <div class="quick-label">Quick picks</div>
      <div class="chips">
        <a class="chip" href="/search?q=Psalm+23">Psalm 23</a>
        <a class="chip" href="/search?q=John+3:16">John 3:16</a>
        <a class="chip" href="/search?q=Genesis+1">Genesis 1</a>
        <a class="chip" href="/search?q=Romans+8">Romans 8</a>
      </div>
    </div>
  </div>
</body>
</html>
    """


@app.get("/search", response_class=HTMLResponse)
async def search(q: str = ""):
    return f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Results for {q}</title>
  <style>
    :root {{
      --bg: #f8fafc;
      --card: #ffffff;
      --text: #0f172a;
      --muted: #64748b;
      --primary: #7c3aed;
      --border: #e2e8f0;
    }}

    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #0f172a;
        --card: #1e293b;
        --text: #f1f5f9;
        --muted: #94a3b8;
        --border: #334155;
      }}
    }}

    body {{
      font-family: system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 20px;
    }}

    .container {{
      max-width: 600px;
      margin: 0 auto;
    }}

    .back-link {{
      display: inline-block;
      margin-bottom: 16px;
      color: var(--primary);
      text-decoration: none;
      font-weight: 500;
    }}

    .results {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
    }}

    h2 {{
      margin-top: 0;
    }}

    .muted {{
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <div class="container">
    <a href="/" class="back-link">← Back</a>
    
    <div class="results">
      <h2>Results for: {q}</h2>
      <p class="muted">Search results will appear here.</p>
    </div>
  </div>
</body>
</html>
    """
