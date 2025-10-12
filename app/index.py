from fastapi import FastAPI, Request, Depends, Form, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import sqlite3
from pathlib import Path
import secrets
from typing import Optional
import bcrypt

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

def get_db_connection(version="able"):
    # Database unplugged to avoid SQLite usage on Vercel.
    raise RuntimeError("SQLite access is disabled in this deployment.")

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
            "total_pages": 0
        })
    
    # Database lookups disabled for Vercel deployment to prevent SQLite access.
    import re
    book_digit_pattern = re.compile(r'^([a-zA-Z]+)(\d+)$')
    match = book_digit_pattern.match(q.strip())
    
    if match:
        book = match.group(1).capitalize()
        digits = match.group(2)
        
        if len(digits) == 2:
            ambiguous_options = handle_ambiguous_reference(book, digits)
    
    normalized_q = normalize_bible_reference(q)
    print(f"\n--- SEARCH QUERY: '{normalized_q}' ---")
    
    results = []
    total_items = 0
    total_pages = 0
    paginated_results = results
    
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
            "user": user,
            "error": "Database access is disabled for this deployment."
        }
    )

@app.get("/verses", response_class=HTMLResponse)
async def verses(request: Request, passage: str = ""):
    user = get_current_user(request)
    
    print(f"\n--- VERSES REQUEST: '{passage}' ---")
    
    import re
    
    ref_pattern = re.compile(r"^(?:the\s+)?((?:\d+\s+)?[A-ZaZ]+)\s+(\d+)(?::(\d+)(?:-(\d+))?)?$")
    m = ref_pattern.match(passage.strip())
    
    if not m:
        return templates.TemplateResponse("verses.html", {
            "request": request, 
            "passage": passage, 
            "verses": [],
            "error": "Could not parse the passage reference."
        })
        
    book = m.group(1)
    chapter = m.group(2)
    start_verse = m.group(3)
    end_verse = m.group(4)
    
    print(f"Parsed book: '{book}', chapter: {chapter}, verses: {start_verse}-{end_verse}")
    
    # Database lookups disabled for Vercel deployment to prevent SQLite access.
    verses = []
    
    is_full_chapter = False
    prev_chapter = None
    next_chapter = None
    
    chapter_pattern = re.compile(r'^([\w\s]+)\s+(\d+)$')
    match = chapter_pattern.match(passage)
    
    if match:
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
   