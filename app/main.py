# from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# import os

# app = FastAPI()

# # Set up templates directory
# templates_dir = os.path.join(os.path.dirname(__file__), "templates")
# templates = Jinja2Templates(directory=templates_dir)


# @app.get("/", response_class=HTMLResponse)
# async def home(request: Request):
#     return templates.TemplateResponse("home.html", {"request": request})


# @app.get("/search", response_class=HTMLResponse)
# async def search(request: Request, q: str = ""):
#     return templates.TemplateResponse("search.html", {"request": request, "query": q})


# @app.get("/verses", response_class=HTMLResponse)
# async def verses(request: Request, passage: str = ""):
#     # In a real application, you would fetch the actual verses for the requested passage
#     # For now, we'll just pass the passage reference to the template
#     return templates.TemplateResponse("verses.html", {"request": request, "passage": passage})

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import sqlite3
from pathlib import Path

app = FastAPI()

# Set up templates directory
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

# Database path
DB_PATH = Path(__file__).parent.parent / "able.db"

def get_db_connection():
    """Create a connection to the SQLite database"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str = ""):
    # If no search query, return empty results
    if not q:
        return templates.TemplateResponse("search.html", {"request": request, "query": q, "results": []})
    
    # Connect to the database and search
    try:
        conn = get_db_connection()
        print(conn)
        cursor = conn.cursor()
        
        # Debug code - add to your route
        cursor.execute("SELECT * FROM verses LIMIT 5")
        debug_results = cursor.fetchall()
        print("Debug results:", debug_results)
        # Search in both references and text content
        # Adjust the SQL query based on your actual database schema
        
        # cursor.execute("""
        #     SELECT book || ' ' || chapter || ':' || verse AS reference, 
        #            text AS text_able,
        #            NULL AS text_kjv,
        #            NULL AS text_bsb
        #     FROM verses
        #     WHERE book = ? AND chapter = ? AND verse >= ? AND verse <= ?
        # """, (book, chapter, start_verse, end_verse))
        
        query = """
            SELECT book || ' ' || chapter || ':' || verse AS reference, 
                text AS text_able,
                NULL AS text_kjv,
                NULL AS text_bsb
            FROM verses
            WHERE LOWER(book || ' ' || chapter || ':' || verse) LIKE LOWER(?) 
            OR LOWER(text) LIKE LOWER(?)
            LIMIT 10
        """
        params = (f'%{q}%', f'%{q}%')
        print(f"Executing query: {query} with params: {params}")
        cursor.execute(query, params)

        results = cursor.fetchall()
        conn.close()
        
        return templates.TemplateResponse(
            "search.html", 
            {"request": request, "query": q, "results": results}
        )
    except Exception as e:
        # Handle error (database not found, etc.)
        error_message = f"Database error: {str(e)}"
        return templates.TemplateResponse(
            "search.html", 
            {"request": request, "query": q, "results": [], "error": error_message}
        )


@app.get("/verses", response_class=HTMLResponse)
async def verses(request: Request, passage: str = ""):
    if not passage:
        return templates.TemplateResponse("verses.html", {"request": request, "passage": passage, "verses": []})
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Parse the passage to get book, chapter, and verse range
        # This is simplified - you might need more robust parsing
        parts = passage.split()
        book = parts[0]
        chapter_verse = parts[1] if len(parts) > 1 else ""
        
        # Query for the specific passage
        cursor.execute("""
            SELECT reference, verse_number, text_able 
            FROM verses
            WHERE reference LIKE ?
            ORDER BY verse_number
        """, (f'{passage}%',))
        
        verses = cursor.fetchall()
        conn.close()
        
        return templates.TemplateResponse(
            "verses.html", 
            {"request": request, "passage": passage, "verses": verses}
        )
    except Exception as e:
        error_message = f"Database error: {str(e)}"
        return templates.TemplateResponse(
            "verses.html", 
            {"request": request, "passage": passage, "verses": [], "error": error_message}
        )