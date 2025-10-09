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

# Add this function before your search endpoint
def normalize_bible_reference(reference):
    """
    Normalize Bible references to handle common variations:
    - Convert lowercase to proper case: "john 3:16" → "John 3:16"
    - Add space between book and chapter: "john3:16" → "John 3:16"
    - Handle numeric books: "1john 4:7" → "1 John 4:7"
    - Handle condensed format: "john316" → "John 3:16"
    - Detect ambiguous references: "genesis11" could be "Genesis 1:1" or "Genesis 11"
    """
    import re
    
    # Trim whitespace
    reference = reference.strip()
    
    # Extract the book and digits for possible ambiguous references
    book_digit_pattern = re.compile(r'^([a-zA-Z]+)(\d+)$')
    match = book_digit_pattern.match(reference)
    
    if match:
        book = match.group(1)
        digits = match.group(2)
        
        # Capitalize book name
        book = book.capitalize()
        
        # Check if this could be an ambiguous reference
        if len(digits) == 2:
            ambiguous_options = handle_ambiguous_reference(book, digits)
            if ambiguous_options:
                # For now, default to the chapter interpretation
                # (we'll handle the ambiguity in the search endpoint)
                reference = ambiguous_options[1]  # Default to "Genesis 11" interpretation
    
    # Continue with normal normalization
    reference = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', reference)
    reference = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', reference)
    
    # Split into components
    parts = reference.split()
    
    if len(parts) >= 1:
        # Capitalize book names
        if len(parts) >= 2 and parts[0].isdigit():
            # Handle "1 john" → "1 John"
            parts[1] = parts[1].capitalize()
        else:
            # Handle "john" → "John"
            parts[0] = parts[0].capitalize()
    
    # Recombine parts
    normalized = ' '.join(parts)
    
    # Special case for Song of Solomon/Songs
    normalized = normalized.replace('Song Of Solomon', 'Song of Solomon')
    normalized = normalized.replace('Songs', 'Song of Solomon')
    
    return normalized

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str = "", page: int = 1):
    items_per_page = 5
    ambiguous_options = None
    
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
    
    try:
        # Check for possible ambiguous references before normalization
        import re
        book_digit_pattern = re.compile(r'^([a-zA-Z]+)(\d+)$')
        match = book_digit_pattern.match(q.strip())
        
        if match:
            book = match.group(1).capitalize()
            digits = match.group(2)
            
            if len(digits) == 2:
                ambiguous_options = handle_ambiguous_reference(book, digits)
        
        # Normalize the query
        normalized_q = normalize_bible_reference(q)
        
        print(f"\n--- SEARCH QUERY: '{normalized_q}' ---")
        
        # Try to detect if the query is a reference (e.g. "John 3:16", "Philippians 4:6-7", "Genesis 1")
        import re

        ref_pattern = re.compile(r"^(.+?)\s+(\d+)(?::(\d+)(?:-(\d+))?)?$")
        m = ref_pattern.match(normalized_q.strip())

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
            params = (f'%{normalized_q}%', f'%{normalized_q}%')
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
        
        # Return the template with the added ambiguous_options parameter
        return templates.TemplateResponse(
            "search.html", 
            {
                "request": request, 
                "query": q, 
                "results": paginated_results,
                "page_num": page,
                "items_per_page": items_per_page,
                "total_items": total_items,
                "total_pages": total_pages,
                "ambiguous_options": ambiguous_options  # Pass ambiguous options to template
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
        # Use regex to handle books with numbers (like "1 John")
        # Modified to allow optional "the" before book names
        import re
        
        ref_pattern = re.compile(r"^(?:the\s+)?((?:\d+\s+)?[A-Za-z]+)\s+(\d+)(?::(\d+)(?:-(\d+))?)?$")
        m = ref_pattern.match(passage.strip())
        
        if not m:
            return templates.TemplateResponse("verses.html", {
                "request": request, 
                "passage": passage, 
                "verses": [],
                "error": "Could not parse the passage reference."
            })
            
        book = m.group(1)  # This now correctly captures "1 John" as a whole
        chapter = m.group(2)
        start_verse = m.group(3)
        end_verse = m.group(4)
        
        print(f"Parsed book: '{book}', chapter: {chapter}, verses: {start_verse}-{end_verse}")
        
        conditions = {"book": book, "chapter": chapter}
        verse_range = None
        
        if start_verse:
            if end_verse:  # verse range like 4:6-7
                verse_range = [start_verse, end_verse]
            else:  # single verse like 4:6
                conditions["verse"] = start_verse
        
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

# In your server code before sending to templates
def process_jesus_tags(text):
    return text.replace('<jesus>', '<span class="jesus-words">').replace('</jesus>', '</span>')

def handle_ambiguous_reference(book, digits):
    if len(digits) == 2 and int(digits) <= get_max_chapter(book):
        # Could be chapter or chapter:verse
        return [
            f"{book} {digits[0]}:{digits[1]}",  # Genesis 1:1
            f"{book} {digits}"                  # Genesis 11
        ]
    return None  # Not ambiguous

def get_max_chapter(book):
    """Return the maximum chapter number for a given Bible book."""
    max_chapters = {
        "Genesis": 50, "Exodus": 40, "Leviticus": 27, "Numbers": 36, "Deuteronomy": 34,
        "Joshua": 24, "Judges": 21, "Ruth": 4, "1 Samuel": 31, "2 Samuel": 24,
        "1 Kings": 22, "2 Kings": 25, "1 Chronicles": 29, "2 Chronicles": 36, "Ezra": 10,
        "Nehemiah": 13, "Esther": 10, "Job": 42, "Psalm": 150, "Psalms": 150, "Proverbs": 31,
        "Ecclesiastes": 12, "Song of Solomon": 8, "Isaiah": 66, "Jeremiah": 52,
        "Lamentations": 5, "Ezekiel": 48, "Daniel": 12, "Hosea": 14, "Joel": 3,
        "Amos": 9, "Obadiah": 1, "Jonah": 4, "Micah": 7, "Nahum": 3,
        "Habakkuk": 3, "Zephaniah": 3, "Haggai": 2, "Zechariah": 14, "Malachi": 4,
        "Matthew": 28, "Mark": 16, "Luke": 24, "John": 21, "Acts": 28,
        "Romans": 16, "1 Corinthians": 16, "2 Corinthians": 13, "Galatians": 6, "Ephesians": 6,
        "Philippians": 4, "Colossians": 4, "1 Thessalonians": 5, "2 Thessalonians": 3,
        "1 Timothy": 6, "2 Timothy": 4, "Titus": 3, "Philemon": 1, "Hebrews": 13,
        "James": 5, "1 Peter": 5, "2 Peter": 3, "1 John": 5, "2 John": 1,
        "3 John": 1, "Jude": 1, "Revelation": 22
    }
    
    normalized_book = book.strip()
    if normalized_book.lower() == "psalms":
        normalized_book = "Psalm"
    if normalized_book.lower() == "song":
        normalized_book = "Song of Solomon"
        
    return max_chapters.get(normalized_book, 150)  # Default to a large number if unknown