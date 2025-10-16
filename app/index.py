from fastapi import FastAPI, Request, Depends, Form, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import sqlite3
import sqlitecloud
from pathlib import Path
import secrets
from typing import Optional
import bcrypt

app = FastAPI()

# Set up templates directory
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

# Environment toggle - automatically detect if running on Vercel
import os
USE_CLOUD_DB = os.environ.get('VERCEL', '0') == '1'  # True on Vercel, False locally
print(f"Environment: {'Production (Vercel)' if USE_CLOUD_DB else 'Local development'}")

# Database paths and connection strings
ABLE_DB_PATH = Path(__file__).parent.parent / "able.db"
KJV_DB_PATH = Path(__file__).parent.parent / "comparison" / "kjv.db"
ASV_DB_PATH = Path(__file__).parent.parent / "comparison" / "asv.db"
BSB_DB_PATH = Path(__file__).parent.parent / "comparison" / "bsb.db"

# SQLite Cloud connection strings
CLOUD_ABLE_DB_CONN = "sqlitecloud://cgduhmoehk.g6.sqlite.cloud:8860/able.db?apikey=S2jwydw2wnTWxJsXVQUosNMuvjPs9qU0Luh8B6oHrik"
CLOUD_KJV_DB_CONN = "sqlitecloud://cgduhmoehk.g6.sqlite.cloud:8860/kjv.db?apikey=S2jwydw2wnTWxJsXVQUosNMuvjPs9qU0Luh8B6oHrik"
CLOUD_ASV_DB_CONN = "sqlitecloud://cgduhmoehk.g6.sqlite.cloud:8860/asv.db?apikey=S2jwydw2wnTWxJsXVQUosNMuvjPs9qU0Luh8B6oHrik"
CLOUD_BSB_DB_CONN = "sqlitecloud://cgduhmoehk.g6.sqlite.cloud:8860/bsb.db?apikey=S2jwydw2wnTWxJsXVQUosNMuvjPs9qU0Luh8B6oHrik"

# Debug prints for database existence (local only)
if not USE_CLOUD_DB:
    print(f"ABLE DB exists: {ABLE_DB_PATH.exists()}, path: {ABLE_DB_PATH}")
    print(f"KJV DB exists: {KJV_DB_PATH.exists()}, path: {KJV_DB_PATH}")
    print(f"ASV DB exists: {ASV_DB_PATH.exists()}, path: {ASV_DB_PATH}")
    print(f"BSB DB exists: {BSB_DB_PATH.exists()}, path: {BSB_DB_PATH}")
else:
    print("Using SQLite Cloud database connections")

# Add these variables for session management
SECRET_KEY = secrets.token_hex(16)
SESSION_COOKIE_NAME = "able_session"

# Mock user database (in a real app, you'd use a database)
users_db = {
    "admin@example.com": {
        "email": "admin@example.com",
        "hashed_password": bcrypt.hashpw("adminpassword".encode(), bcrypt.gensalt()).decode(),
        "name": "Admin User"
    },
    "user@example.com": {
        "email": "user@example.com",
        "hashed_password": bcrypt.hashpw("userpassword".encode(), bcrypt.gensalt()).decode(),
        "name": "Regular User"
    }
}

# def get_db_connection(version="able"):
#     # Database unplugged to avoid SQLite usage on Vercel.
#     raise RuntimeError("SQLite access is disabled in this deployment.")
def get_db_connection(version="able"):
    """Create a connection to the selected database (local SQLite or SQLite Cloud)"""
    if USE_CLOUD_DB:
        # Use SQLite Cloud in production
        if version.lower() == "kjv":
            conn_str = CLOUD_KJV_DB_CONN
        elif version.lower() == "asv":
            conn_str = CLOUD_ASV_DB_CONN
        elif version.lower() == "bsb":
            conn_str = CLOUD_BSB_DB_CONN
        else:
            conn_str = CLOUD_ABLE_DB_CONN
            
        print(f"Connecting to {version} cloud database")
        conn = sqlitecloud.connect(conn_str)
        
        # Create a custom row factory to mimic sqlite3.Row
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d
            
        conn.row_factory = dict_factory
        return conn
    else:
        # Use local SQLite in development
        if version.lower() == "kjv":
            db_path = KJV_DB_PATH
        elif version.lower() == "asv":
            db_path = ASV_DB_PATH
        elif version.lower() == "bsb":
            db_path = BSB_DB_PATH
        else:
            db_path = ABLE_DB_PATH
        
        print(f"Connecting to {version} local database at: {db_path}")
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

def handle_ambiguous_reference(book, digits):
    """
    Handle ambiguous references like "genesis11" which could be
    "Genesis 1:1" or "Genesis 11".
    Returns a list of possible interpretations.
    """
    # For a 2-digit number like "11", it could be:
    # 1. Chapter 1, verse 1 (Genesis 1:1)
    # 2. Chapter 11 (Genesis 11)
    if len(digits) == 2:
        option1 = f"{book} {digits[0]}:{digits[1]}"  # Genesis 1:1
        option2 = f"{book} {digits}"                 # Genesis 11
        return [option1, option2]
    
    # For a 3-digit number like "123", it could be:
    # 1. Chapter 1, verse 23 (Genesis 1:23)
    # 2. Chapter 12, verse 3 (Genesis 12:3)
    # 3. Chapter 123 (Genesis 123) - usually invalid in Bible context
    elif len(digits) == 3:
        option1 = f"{book} {digits[0]}:{digits[1:3]}"    # Genesis 1:23
        option2 = f"{book} {digits[0:2]}:{digits[2]}"    # Genesis 12:3
        option3 = f"{book} {digits}"                     # Genesis 123
        return [option1, option2, option3]
    
    return None  # Not ambiguous or couldn't determine

# Get current user from session
def get_current_user(request: Request) -> Optional[dict]:
    session_email = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_email:
        return None
    
    if session_email in users_db:
        return users_db[session_email]
    return None

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    # Check if user is already logged in
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    # For simplicity, we're treating username as email
    email = username.lower()
    
    # Check if user exists
    if email not in users_db:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Invalid email or password"}
        )
    
    user = users_db[email]
    stored_password = user["hashed_password"].encode()
    
    # Verify password
    if not bcrypt.checkpw(password.encode(), stored_password):
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Invalid email or password"}
        )
    
    # Create session
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=email,
        httponly=True,
        max_age=3600 * 24 * 7,  # 1 week
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )
    
    return response

@app.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response

# Update the home route to include user info
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str = "", page: int = 1):
    user = get_current_user(request)
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
            "total_pages": 0,
            "user": user
        })
    
    try:
        # Add detailed debugging
        print(f"\nDEBUG: Starting search for '{q}'")
        
        # Normalize the query to handle case and format variations
        normalized_q = normalize_bible_reference(q)
        print(f"DEBUG: Normalized query: '{normalized_q}'")
        
        # Check for ambiguous references
        import re
        book_digit_pattern = re.compile(r'^([a-zA-Z]+)(\d+)$')
        match = book_digit_pattern.match(q.strip())
        
        if match:
            book = match.group(1).capitalize()
            digits = match.group(2)
            
            if len(digits) == 2:
                ambiguous_options = handle_ambiguous_reference(book, digits)
        
        # Try to detect if the query is a reference
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
                cursor_able.execute(able_query, params)

            able_results = cursor_able.fetchall()
        else:
            # Text search fallback
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
                "text_kjv": "KJV translation not found",
                "text_asv": "ASV translation not found",
                "text_bsb": "BSB translation not found"
            }
        
        # Get matching verses from comparison databases
        for version in ["kjv", "asv", "bsb"]:
            try:
                conn = get_db_connection(version)
                cursor = conn.cursor()
                
                for ref, data in combined_results.items():
                    query = f"""
                        SELECT text AS text_{version}
                        FROM verses
                        WHERE book = ? AND chapter = ? AND verse = ?
                    """
                    cursor.execute(query, (data["book"], data["chapter"], data["verse"]))
                    verse = cursor.fetchone()
                    if verse:
                        combined_results[ref][f"text_{version}"] = verse[f"text_{version}"]
                
                conn.close()
            except Exception as e:
                print(f"Error fetching {version.upper()} verses: {str(e)}")
        
        # Convert dictionary back to a list for the template
        results = list(combined_results.values())
        
        # Pagination
        total_items = len(results)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        paginated_results = results[start_idx:end_idx]
        
        # At the end of processing, log the results
        print(f"DEBUG: Found {len(combined_results)} results")
        
        # Right before returning, dump the first result for inspection
        if len(results) > 0:
            print(f"DEBUG: First result: {results[0]}")
            print(f"DEBUG: Total results to return: {len(paginated_results)}")
        else:
            print("DEBUG: No results found")
        
        # Return the response as before
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
                "ambiguous_options": ambiguous_options,
                "user": user
            }
        )
    except Exception as e:
        # Enhanced error reporting
        import traceback
        error_message = f"Database error: {str(e)}"
        print(f"ERROR in search: {error_message}")
        print(traceback.format_exc())
        return templates.TemplateResponse(
            "search.html", 
            {"request": request, "query": q, "results": [], "error": error_message, "user": user}
        )

@app.get("/verses", response_class=HTMLResponse)
async def verses(request: Request, passage: str = ""):
    user = get_current_user(request)
    
    if not passage:
        return templates.TemplateResponse("verses.html", {"request": request, "passage": passage, "verses": [], "user": user})
    
    try:
        print(f"\n--- VERSES REQUEST: '{passage}' ---")
        
        # Parse the passage
        import re
        
        ref_pattern = re.compile(r"^(?:the\s+)?((?:\d+\s+)?[A-Za-z]+)\s+(\d+)(?::(\d+)(?:-(\d+))?)?$")
        m = ref_pattern.match(passage.strip())
        
        if not m:
            return templates.TemplateResponse("verses.html", {
                "request": request, 
                "passage": passage, 
                "verses": [],
                "error": "Could not parse the passage reference.",
                "user": user
            })
            
        book = m.group(1)
        chapter = m.group(2)
        start_verse = m.group(3)
        end_verse = m.group(4)
        
        print(f"Parsed book: '{book}', chapter: {chapter}, verses: {start_verse}-{end_verse}")
        
        conditions = {"book": book, "chapter": chapter}
        verse_range = None
        
        if start_verse:
            if end_verse:  # verse range
                verse_range = [start_verse, end_verse]
            else:  # single verse
                conditions["verse"] = start_verse
        
        # Get verses from ABLE database
        conn_able = get_db_connection("able")
        cursor_able = conn_able.cursor()
        
        # Build query dynamically
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
        
        # Process results for full chapter navigation
        is_full_chapter = False
        prev_chapter = None
        next_chapter = None
        
        chapter_pattern = re.compile(r'^([\w\s]+)\s+(\d+)$')
        match = chapter_pattern.match(passage)
        
        if match and not start_verse:
            book = match.group(1)
            chapter = int(match.group(2))
            is_full_chapter = True
            
            bible_books = [
                "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
                "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel", 
                "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles",
                "Ezra", "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
                "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah",
                "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
                "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah",
                "Haggai", "Zechariah", "Malachi",
                "Matthew", "Mark", "Luke", "John", "Acts", "Romans",
                "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians", "Philippians",
                "Colossians", "1 Thessalonians", "2 Thessalonians", "1 Timothy",
                "2 Timothy", "Titus", "Philemon", "Hebrews", "James", "1 Peter",
                "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation"
            ]
            
            max_chapters = {
                "Genesis": 50, "Exodus": 40, "Leviticus": 27, "Numbers": 36, "Deuteronomy": 34,
                "Joshua": 24, "Judges": 21, "Ruth": 4, "1 Samuel": 31, "2 Samuel": 24, 
                "1 Kings": 22, "2 Kings": 25, "1 Chronicles": 29, "2 Chronicles": 36,
                "Ezra": 10, "Nehemiah": 13, "Esther": 10, "Job": 42, "Psalms": 150, "Proverbs": 31,
                "Ecclesiastes": 12, "Song of Solomon": 8, "Isaiah": 66, "Jeremiah": 52,
                "Lamentations": 5, "Ezekiel": 48, "Daniel": 12, "Hosea": 14, "Joel": 3, "Amos": 9,
                "Obadiah": 1, "Jonah": 4, "Micah": 7, "Nahum": 3, "Habakkuk": 3, "Zephaniah": 3,
                "Haggai": 2, "Zechariah": 14, "Malachi": 4,
                "Matthew": 28, "Mark": 16, "Luke": 24, "John": 21, "Acts": 28, "Romans": 16,
                "1 Corinthians": 16, "2 Corinthians": 13, "Galatians": 6, "Ephesians": 6, "Philippians": 4,
                "Colossians": 4, "1 Thessalonians": 5, "2 Thessalonians": 3, "1 Timothy": 6,
                "2 Timothy": 4, "Titus": 3, "Philemon": 1, "Hebrews": 13, "James": 5, "1 Peter": 5,
                "2 Peter": 3, "1 John": 5, "2 John": 1, "3 John": 1, "Jude": 1, "Revelation": 22
            }
            
            if chapter > 1:
                prev_chapter = f"{book} {chapter - 1}"
            else:
                try:
                    book_index = bible_books.index(book)
                    if book_index > 0:
                        prev_book = bible_books[book_index - 1]
                        prev_chapter = f"{prev_book} {max_chapters[prev_book]}"
                except ValueError:
                    prev_chapter = None
            
            if book in max_chapters and chapter < max_chapters[book]:
                next_chapter = f"{book} {chapter + 1}"
            else:
                try:
                    book_index = bible_books.index(book)
                    if book_index < len(bible_books) - 1:
                        next_book = bible_books[book_index + 1]
                        next_chapter = f"{next_book} 1"
                except ValueError:
                    next_chapter = None
        
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
                "text_kjv": "KJV translation not found",
                "text_asv": "ASV translation not found",
                "text_bsb": "BSB translation not found"
            }
        
        # Get matching verses from comparison databases
        for version in ["kjv", "asv", "bsb"]:
            try:
                conn = get_db_connection(version)
                cursor = conn.cursor()
                
                for ref, data in combined_verses.items():
                    query = f"""
                        SELECT text AS text_{version}
                        FROM verses
                        WHERE book = ? AND chapter = ? AND verse = ?
                    """
                    cursor.execute(query, (data["book"], data["chapter"], data["verse"]))
                    verse = cursor.fetchone()
                    if verse:
                        combined_verses[ref][f"text_{version}"] = verse[f"text_{version}"]
                
                conn.close()
            except Exception as e:
                print(f"Error fetching {version.upper()} verses: {str(e)}")
        
        # Convert dictionary back to a list for the template
        verses = list(combined_verses.values())
        
        return templates.TemplateResponse(
            "verses.html", 
            {
                "request": request, 
                "passage": passage, 
                "verses": verses,
                "is_full_chapter": is_full_chapter,
                "prev_chapter": prev_chapter,
                "next_chapter": next_chapter,
                "user": user
            }
        )
        
    except Exception as e:
        error_message = f"Database error: {str(e)}"
        print(f"ERROR in verses: {error_message}")
        return templates.TemplateResponse(
            "verses.html", 
            {"request": request, "passage": passage, "verses": [], "error": error_message, "user": user}
        )

@app.get("/test-search")
async def test_search(q: str = "john 3:16"):
    """Debug endpoint to isolate search issues"""
    try:
        print(f"--- TEST SEARCH: '{q}' ---")
        
        # Test database connection
        conn = get_db_connection("able")
        print("Database connection successful!")
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM verses")
        count = cursor.fetchone()
        print(f"Total verses in database: {count['count']}")
        
        # Test parsing
        normalized_q = normalize_bible_reference(q)
        print(f"Normalized query: '{normalized_q}'")
        
        # Test specific query matching
        import re
        ref_pattern = re.compile(r"^(.+?)\s+(\d+)(?::(\d+)(?:-(\d+))?)?$")
        m = ref_pattern.match(normalized_q.strip())
        
        if m:
            print("Query matches reference pattern!")
            book = m.group(1).strip()
            chapter = m.group(2)
            start_verse = m.group(3)
            end_verse = m.group(4)
            print(f"Parsed: book='{book}', chapter={chapter}, verse={start_verse}-{end_verse}")
            
            # Test direct verse query
            query = """
                SELECT COUNT(*) as count
                FROM verses 
                WHERE book = ? AND chapter = ? AND verse = ?
            """
            cursor.execute(query, (book, chapter, start_verse))
            match_count = cursor.fetchone()
            print(f"Matching verses for '{book} {chapter}:{start_verse}': {match_count['count']}")
        else:
            print("Query does NOT match reference pattern")
            
            # Test text search
            query = """
                SELECT COUNT(*) as count
                FROM verses
                WHERE LOWER(text) LIKE LOWER(?)
            """
            cursor.execute(query, (f'%{normalized_q}%',))
            match_count = cursor.fetchone()
            print(f"Text search matches: {match_count['count']}")
        
        conn.close()
        return {"status": "success", "message": "See server logs for details"}
        
    except Exception as e:
        import traceback
        print(f"ERROR in test-search: {str(e)}")
        print(traceback.format_exc())
        return {"status": "error", "message": str(e)}

@app.get("/search-json")
async def search_json(q: str = ""):
    """Simple JSON endpoint to verify search functionality"""
    try:
        if not q:
            return {"success": False, "message": "No query provided"}
            
        normalized_q = normalize_bible_reference(q)
        
        conn = get_db_connection("able")
        cursor = conn.cursor()
        
        import re
        ref_pattern = re.compile(r"^(.+?)\s+(\d+)(?::(\d+)(?:-(\d+))?)?$")
        m = ref_pattern.match(normalized_q.strip())
        
        results = []
        if m:
            book = m.group(1).strip()
            chapter = m.group(2)
            verse = m.group(3)
            
            query = """
                SELECT book, chapter, verse, text 
                FROM verses
                WHERE book = ? AND chapter = ? AND verse = ?
            """
            cursor.execute(query, (book, chapter, verse))
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
        
        conn.close()
        return {"success": True, "query": q, "normalized": normalized_q, "results": results}
    except Exception as e:
        import traceback
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}
