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

# Database paths
ABLE_DB_PATH = Path(__file__).parent.parent / "able.db"
KJV_DB_PATH = Path(__file__).parent.parent / "comparison" / "kjv.db"
ASV_DB_PATH = Path(__file__).parent.parent / "comparison" / "asv.db"
BSB_DB_PATH = Path(__file__).parent.parent / "comparison" / "bsb.db"

# Debug prints for database existence
print(f"ABLE DB exists: {ABLE_DB_PATH.exists()}, path: {ABLE_DB_PATH}")
print(f"KJV DB exists: {KJV_DB_PATH.exists()}, path: {KJV_DB_PATH}")
print(f"ASV DB exists: {ASV_DB_PATH.exists()}, path: {ASV_DB_PATH}")
print(f"BSB DB exists: {BSB_DB_PATH.exists()}, path: {BSB_DB_PATH}")

def get_db_connection(version="able"):
    """Create a connection to the selected SQLite database"""
    if version.lower() == "kjv":
        db_path = KJV_DB_PATH
    elif version.lower() == "asv":
        db_path = ASV_DB_PATH
    elif version.lower() == "bsb":
        db_path = BSB_DB_PATH
    else:
        db_path = ABLE_DB_PATH
    
    print(f"Connecting to {version} database at: {db_path}")
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str = "", page: int = 1):
    items_per_page = 5  # Number of verses per page
    
    # If no search query, return empty results
    if not q:
        return templates.TemplateResponse("search.html", {
            "request": request, 
            "query": q, 
            "results": [],
            "page_num": page,
            "items_per_page": items_per_page,
            "total_items": 0,
            "total_pages": 0
        })
    
    # Connect to the database and search
    try:
        print(f"\n--- SEARCH QUERY: '{q}' ---")
        
        # Try to detect if the query is a reference (e.g. "John 3:16", "Philippians 4:6-7", "Genesis 1")
        import re

        ref_pattern = re.compile(r"^(.+?)\s+(\d+)(?::(\d+)(?:-(\d+))?)?$")
        m = ref_pattern.match(q.strip())

        conn_able = get_db_connection("able")
        cursor_able = conn_able.cursor()

        if m:
            # Parsed a book/chapter(:start[-end]?) reference
            book = m.group(1).strip()
            chapter = m.group(2)
            start_verse = m.group(3)
            end_verse = m.group(4)

            if start_verse and end_verse:
                # range like 4:6-7
                able_query = """
                    SELECT book || ' ' || chapter || ':' || verse AS reference,
                           book, chapter, verse, text AS text_able
                    FROM verses
                    WHERE LOWER(book) = LOWER(?) AND chapter = ? AND CAST(verse AS INTEGER) BETWEEN ? AND ?
                    ORDER BY CAST(chapter AS INTEGER), CAST(verse AS INTEGER)
                """
                params = (book, chapter, start_verse, end_verse)
                cursor_able.execute(able_query, params)
            elif start_verse and not end_verse:
                # single verse like 3:16
                able_query = """
                    SELECT book || ' ' || chapter || ':' || verse AS reference,
                           book, chapter, verse, text AS text_able
                    FROM verses
                    WHERE LOWER(book) = LOWER(?) AND chapter = ? AND verse = ?
                    ORDER BY CAST(chapter AS INTEGER), CAST(verse AS INTEGER)
                    LIMIT 1
                """
                params = (book, chapter, start_verse)
                cursor_able.execute(able_query, params)
            else:
                # whole chapter like "Genesis 1"
                able_query = """
                    SELECT book || ' ' || chapter || ':' || verse AS reference,
                           book, chapter, verse, text AS text_able
                    FROM verses
                    WHERE LOWER(book) = LOWER(?) AND chapter = ?
                    ORDER BY CAST(chapter AS INTEGER), CAST(verse AS INTEGER)
                """
                params = (book, chapter)

                # execute the chapter query
                cursor_able.execute(able_query, params)

            able_results = cursor_able.fetchall()
            conn_able.close()
        else:
            # Text search fallback (search in reference string or verse text)
            query = """
                SELECT book || ' ' || chapter || ':' || verse AS reference, 
                    book, chapter, verse, text AS text_able
                FROM verses
                WHERE LOWER(book || ' ' || chapter || ':' || verse) LIKE LOWER(?) 
                OR LOWER(text) LIKE LOWER(?)
                LIMIT 10
            """
            params = (f'%{q}%', f'%{q}%')
            cursor_able.execute(query, params)
            able_results = cursor_able.fetchall()
            conn_able.close()
        
        # Create a dictionary to hold combined results
        combined_results = {}
        for row in able_results:
            ref = row["reference"]
            combined_results[ref] = {
                "reference": ref,
                "book": row["book"],
                "chapter": row["chapter"],
                "verse": row["verse"],
                "text_able": row["text_able"],
                "text_kjv": "KJV translation not found",  # Default value
                "text_asv": "ASV translation not found",  # Default value
                "text_bsb": "BSB translation not found"   # Default value
            }
        
        # Get matching verses from KJV database
        try:
            conn_kjv = get_db_connection("kjv")
            cursor_kjv = conn_kjv.cursor()
            
            # For each reference found in ABLE, get corresponding KJV verse
            for ref, data in combined_results.items():
                kjv_query = """
                    SELECT text AS text_kjv
                    FROM verses
                    WHERE book = ? AND chapter = ? AND verse = ?
                """
                cursor_kjv.execute(kjv_query, (data["book"], data["chapter"], data["verse"]))
                kjv_verse = cursor_kjv.fetchone()
                if kjv_verse:
                    combined_results[ref]["text_kjv"] = kjv_verse["text_kjv"]
            
            conn_kjv.close()
        except Exception as e:
            print(f"Error fetching KJV verses: {str(e)}")
        
        # Get matching verses from ASV database
        try:
            conn_asv = get_db_connection("asv")
            cursor_asv = conn_asv.cursor()
            
            # For each reference found in ABLE, get corresponding ASV verse
            for ref, data in combined_results.items():
                asv_query = """
                    SELECT text AS text_asv
                    FROM verses
                    WHERE book = ? AND chapter = ? AND verse = ?
                """
                cursor_asv.execute(asv_query, (data["book"], data["chapter"], data["verse"]))
                asv_verse = cursor_asv.fetchone()
                if asv_verse:
                    combined_results[ref]["text_asv"] = asv_verse["text_asv"]
            
            conn_asv.close()
        except Exception as e:
            print(f"Error fetching ASV verses: {str(e)}")
        
        # Get matching verses from BSB database
        try:
            conn_bsb = get_db_connection("bsb")
            cursor_bsb = conn_bsb.cursor()
            
            # For each reference found in ABLE, get corresponding BSB verse
            for ref, data in combined_results.items():
                bsb_query = """
                    SELECT text AS text_bsb
                    FROM verses
                    WHERE book = ? AND chapter = ? AND verse = ?
                """
                cursor_bsb.execute(bsb_query, (data["book"], data["chapter"], data["verse"]))
                bsb_verse = cursor_bsb.fetchone()
                if bsb_verse:
                    combined_results[ref]["text_bsb"] = bsb_verse["text_bsb"]
            
            conn_bsb.close()
        except Exception as e:
            print(f"Error fetching BSB verses: {str(e)}")
        
        # Convert dictionary back to a list for the template
        results = list(combined_results.values())
        print(f"Combined results found: {len(results)}")
        
        # After you fetch all results, implement pagination:
        total_items = len(results)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        # Paginate results
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        paginated_results = results[start_idx:end_idx]
        
        return templates.TemplateResponse(
            "search.html", 
            {
                "request": request, 
                "query": q, 
                "results": paginated_results,
                "page_num": page,
                "items_per_page": items_per_page,
                "total_items": total_items,
                "total_pages": total_pages
            }
        )
    except Exception as e:
        # Handle error (database not found, etc.)
        error_message = f"Database error: {str(e)}"
        print(f"ERROR in search: {error_message}")
        return templates.TemplateResponse(
            "search.html", 
            {"request": request, "query": q, "results": [], "error": error_message}
        )

@app.get("/verses", response_class=HTMLResponse)
async def verses(request: Request, passage: str = ""):
    if not passage:
        return templates.TemplateResponse("verses.html", {"request": request, "passage": passage, "verses": []})
    
    try:
        print(f"\n--- VERSES REQUEST: '{passage}' ---")
        
        # Parse the passage (support: Book Chapter, Book Chapter:Verse, Book Chapter:Start-End)
        import re

        parts = passage.split()
        if not parts:
            return templates.TemplateResponse("verses.html", {"request": request, "passage": passage, "verses": []})

        book = parts[0]
        print(f"Parsed book: '{book}'")

        conditions = {}
        verse_range = None

        if len(parts) > 1:
            chapter_verse = parts[1]
            # match patterns like 3, 3:16, 4:6-7
            m = re.match(r"^(\d+)(?::(\d+)(?:-(\d+))?)?$", chapter_verse)
            # Note: fallback simple parsing if regex fails
            if m:
                chapter = m.group(1)
                start_verse = m.group(2)
                end_verse = m.group(3)
                conditions = {"book": book, "chapter": chapter}
                if start_verse and end_verse:
                    verse_range = (start_verse, end_verse)
                elif start_verse:
                    verse_range = (start_verse, start_verse)
            else:
                # fallback: treat as chapter if it's numeric
                if chapter_verse.isdigit():
                    conditions = {"book": book, "chapter": chapter_verse}
                else:
                    # unknown format: try to match book only
                    conditions = {"book": book}
        else:
            conditions = {"book": book}
        
        # Get verses from ABLE database
        conn_able = get_db_connection("able")
        cursor_able = conn_able.cursor()
        
        # Build query dynamically based on conditions and optional verse_range
        able_query = "SELECT book || ' ' || chapter || ':' || verse AS reference, book, chapter, verse, text AS text_able FROM verses WHERE "
        query_parts = []
        params = []

        for key, value in conditions.items():
            query_parts.append(f"{key} = ?")
            params.append(value)

        able_query += " AND ".join(query_parts)

        if verse_range:
            able_query += " AND CAST(verse AS INTEGER) BETWEEN ? AND ?"
            params.extend([verse_range[0], verse_range[1]])

        able_query += " ORDER BY CAST(chapter AS INTEGER), CAST(verse AS INTEGER)"

        cursor_able.execute(able_query, params)
        able_results = cursor_able.fetchall()
        conn_able.close()
        
        # Create combined results dictionary
        combined_verses = {}
        for row in able_results:
            ref = row["reference"]
            combined_verses[ref] = {
                "reference": ref,
                "book": row["book"],
                "chapter": row["chapter"],
                "verse": row["verse"],
                "verse_number": row["verse"],
                "text_able": row["text_able"],
                "text_kjv": "KJV translation not found",  # Default value
                "text_asv": "ASV translation not found",  # Default value
                "text_bsb": "BSB translation not found"   # Default value
            }
        
        # Get matching verses from KJV database
        try:
            conn_kjv = get_db_connection("kjv")
            cursor_kjv = conn_kjv.cursor()
            
            # For each reference found in ABLE, get corresponding KJV verse
            for ref, data in combined_verses.items():
                kjv_query = """
                    SELECT text AS text_kjv
                    FROM verses
                    WHERE book = ? AND chapter = ? AND verse = ?
                """
                cursor_kjv.execute(kjv_query, (data["book"], data["chapter"], data["verse"]))
                kjv_verse = cursor_kjv.fetchone()
                if kjv_verse:
                    combined_verses[ref]["text_kjv"] = kjv_verse["text_kjv"]
            
            conn_kjv.close()
        except Exception as e:
            print(f"Error fetching KJV verses: {str(e)}")
        
        # Get matching verses from ASV database
        try:
            conn_asv = get_db_connection("asv")
            cursor_asv = conn_asv.cursor()
            
            # For each reference found in ABLE, get corresponding ASV verse
            for ref, data in combined_verses.items():
                asv_query = """
                    SELECT text AS text_asv
                    FROM verses
                    WHERE book = ? AND chapter = ? AND verse = ?
                """
                cursor_asv.execute(asv_query, (data["book"], data["chapter"], data["verse"]))
                asv_verse = cursor_asv.fetchone()
                if asv_verse:
                    combined_verses[ref]["text_asv"] = asv_verse["text_asv"]
            
            conn_asv.close()
        except Exception as e:
            print(f"Error fetching ASV verses: {str(e)}")
        
        # Get matching verses from BSB database
        try:
            conn_bsb = get_db_connection("bsb")
            cursor_bsb = conn_bsb.cursor()
            
            # For each reference found in ABLE, get corresponding BSB verse
            for ref, data in combined_verses.items():
                bsb_query = """
                    SELECT text AS text_bsb
                    FROM verses
                    WHERE book = ? AND chapter = ? AND verse = ?
                """
                cursor_bsb.execute(bsb_query, (data["book"], data["chapter"], data["verse"]))
                bsb_verse = cursor_bsb.fetchone()
                if bsb_verse:
                    combined_verses[ref]["text_bsb"] = bsb_verse["text_bsb"]
            
            conn_bsb.close()
        except Exception as e:
            print(f"Error fetching BSB verses: {str(e)}")
        
        # Convert dictionary back to a list for the template
        verses = list(combined_verses.values())
        print(f"Combined verses found: {len(verses)}")
        
        return templates.TemplateResponse(
            "verses.html", 
            {"request": request, "passage": passage, "verses": verses}
        )
        
    except Exception as e:
        error_message = f"Database error: {str(e)}"
        print(f"ERROR in verses: {error_message}")
        return templates.TemplateResponse(
            "verses.html", 
            {"request": request, "passage": passage, "verses": [], "error": error_message}
        )