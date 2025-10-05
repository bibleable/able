from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()

# Set up templates directory
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str = ""):
    return templates.TemplateResponse("search.html", {"request": request, "query": q})


@app.get("/verses", response_class=HTMLResponse)
async def verses(request: Request, passage: str = ""):
    # In a real application, you would fetch the actual verses for the requested passage
    # For now, we'll just pass the passage reference to the template
    return templates.TemplateResponse("verses.html", {"request": request, "passage": passage})
