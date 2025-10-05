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
    html, body { height: 100%; margin: 0; }

    .bg {
      position: fixed;
      inset: 0;
      background:
        radial-gradient(40% 35% at 35% 45%, rgba(255,184,150,0.70) 0%, rgba(255,184,150,0.00) 60%),
        radial-gradient(45% 40% at 78% 18%, rgba(192,173,255,0.65) 0%, rgba(192,173,255,0.00) 62%),
        radial-gradient(55% 50% at 88% 55%, rgba(140,180,255,0.55) 0%, rgba(140,180,255,0.00) 65%),
        radial-gradient(50% 45% at 8% 30%, rgba(255,150,170,0.45) 0%, rgba(255,150,170,0.00) 65%),
        radial-gradient(35% 30% at 55% 45%, rgba(255,214,153,0.55) 0%, rgba(255,214,153,0.00) 70%),
        linear-gradient(180deg, #f2f6ff 0%, #f7f2ff 40%, #f0fbff 100%);
      filter: blur(0.3px);
      overflow: hidden;
    }

    .bg::after {
      content: "";
      position: absolute;
      inset: -2vmax;
      pointer-events: none;
      background: radial-gradient(100% 100% at 50% 50%,
          rgba(0,0,0,0) 60%,
          rgba(0,0,0,0.05) 100%);
      mix-blend-mode: multiply;
    }

    @media (prefers-reduced-motion: no-preference) {
      .bg { animation: drift 16s ease-in-out infinite alternate; }
      @keyframes drift {
        0%   { filter: blur(0.3px) saturate(100%); }
        100% { filter: blur(0.6px) saturate(108%); }
      }
    }

    .center {
      position: relative;
      height: 100%;
      display: grid;
      place-items: center;
      text-align: center;
    }

    form {
      background: rgba(255,255,255,0.9);
      padding: 1.5rem 2rem;
      border-radius: 1rem;
      box-shadow: 0 4px 20px rgba(0,0,0,0.1);
      backdrop-filter: blur(6px);
      display: flex;
      flex-direction: column;
      align-items: stretch;
      gap: 0.8rem;
    }

    .search-row {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    input[type="text"] {
      flex: 1;
      width: 100%;
      padding: 0.8rem 1rem;
      font-size: 1.1rem;
      border: 1px solid #ccc;
      border-radius: 0.6rem;
      outline: none;
    }

    button {
      padding: 0.8rem 1.4rem;
      font-size: 1rem;
      border: none;
      border-radius: 0.6rem;
      background: #6c63ff;
      color: white;
      cursor: pointer;
      white-space: nowrap;
    }

    button:hover {
      background: #5850ec;
    }

    .quick-links {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      justify-content: flex-start;
      margin-top: 0.5rem;
    }

    .quick-links a {
      display: inline-block;
      padding: 0.4rem 0.9rem;
      border-radius: 0.6rem;
      background: #fbbf24;
      color: #1f2937;
      text-decoration: none;
      font-weight: 600;
      font-size: 0.9rem;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      transition: background 0.2s;
    }

    .quick-links a:hover {
      background: #f59e0b;
    }
    
    /* Search button */
button {
  padding: 0.8rem 1.4rem;
  font-size: 1rem;
  border: none;
  border-radius: 0.6rem;
  background: #6c63ff;   /* Purple CTA */
  color: white;
  cursor: pointer;
  white-space: nowrap;
}
button:hover {
  background: #5850ec;
}

/* Quick links */
.quick-links a {
  padding: 0.4rem 0.9rem;
  border-radius: 0.6rem;
  background: #fbbf24;   /* Strong gold */
  color: #1f2937;
  font-weight: 600;
  font-size: 0.9rem;
}

  </style>
</head>
<body>
  <div class="bg" aria-hidden="true"></div>
  <div class="center">
    <form method="get" action="/search">
      <div class="search-row">
        <input type="text" name="q" placeholder="Search Bible..." />
        <button type="submit">Search</button>
      </div>
      <div class="quick-links">
        <a href="/search?q=Psalm+23">Psalm 23</a>
        <a href="/search?q=John+1">John 1</a>
        <a href="/search?q=Genesis+1">Genesis 1</a>
        <a href="/search?q=Romans+8">Romans 8</a>
        <a href="/search?q=Isaiah+53">Isaiah 53</a>
      </div>
    </form>
  </div>
</body>
</html>
    """


@app.get("/search", response_class=HTMLResponse)
async def search(q: str = ""):
    return f"<h2 style='font-family:sans-serif;padding:2rem;'>You searched for: <em>{q}</em></h2>"
