# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Setup

### Local Development

```bash
cd idea_factory
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
python app.py
```

The app runs on `http://localhost:5001`

### Docker Development

```bash
cd idea_factory
docker-compose build
docker-compose up -d
docker-compose logs -f  # View logs
```

Access at `http://localhost:5001`

### Environment Configuration

Required `.env` variables:
- `OPENAI_API_KEY` - OpenAI API key
- `OPENAI_MODEL` - Model name (default: `gpt-5-mini`)
- `GOOGLE_SHEETS_SPREADSHEET_ID` - Google Spreadsheet ID from URL
- `GOOGLE_SHEETS_CREDS` - Service account JSON as single-line string
- `APP_SECRET_KEY` - Flask session secret

Optional:
- `ADMIN_PASSWORD` - Admin dashboard password
- `BENDER_URL` - External Bender TTS service URL (default: `http://bender.rmn.pp.ua`)
- `GOOGLE_SHEETS_SHEET_NAME` - Sheet name (default: `Ideas`)

## Application Architecture

### Three-Stage User Flow

The application implements a linear 3-stage workflow stored in Flask sessions:

1. **Brainstorm** (`/brainstorm`) - User enters a prompt → OpenAI generates 6-8 ideas → User selects one
2. **Improve** (`/improve`) - User refines selected idea with preset or custom instructions → OpenAI regenerates improved version
3. **Submit** (`/submit`) - User finalizes title/description → Data saved to Google Sheets

Session state carries data forward through stages:
- `session_id` - UUID generated at first brainstorm
- `prompt_initial` - Original brainstorm prompt
- `ideas_generated` - List of all generated ideas
- `selected_idea` - Currently selected idea dict
- `user_edit_notes` - Improvement instructions

### Core Components

**`app.py`** - Flask application with routes for each stage
- Rate limiting: 20/hour for brainstorm, 30/hour for improve, 200/day global
- Session-based state management (no database)
- Admin dashboard at `/admin` (HTTP Basic Auth)

**`openai_client.py`** - OpenAI integration using structured JSON responses
- `IdeaGenerator.generate_ideas(prompt)` - Returns list of idea dicts
- `IdeaGenerator.improve_idea(idea, instruction)` - Returns improved idea dict
- Uses `response_format={"type": "json_object"}` for reliable JSON parsing
- Retry logic if JSON parsing fails

**`sheets.py`** - Google Sheets API client
- `SheetsClient.append_row(row_values)` - Appends submission to sheet
- `SheetsClient.read_recent_rows(limit)` - Reads recent submissions for admin view
- `ensure_headers()` - Initializes sheet headers on startup
- Uses service account credentials from env var

**`bender_quotes.py`** - Motivational quotes collection by stage

**`bender_audio.py`** - Optional external TTS integration
- Fires non-blocking POST to external service
- Silently fails if service unavailable

### Google Sheets Schema

The `Ideas` sheet has 10 columns in this order:
1. `timestamp_utc` - ISO format timestamp
2. `session_id` - UUID
3. `prompt_initial` - User's original brainstorm prompt
4. `idea_selected_title` - Title of idea from brainstorm stage
5. `idea_selected_description` - Description from brainstorm stage
6. `user_edit_notes` - User's improvement instructions
7. `final_title` - Final submitted title
8. `final_description` - Final submitted description
9. `user_agent` - Browser user agent
10. `ip` - User IP address

## Common Modifications

### Changing OpenAI Prompts

System prompts are in `openai_client.py` in the `IdeaGenerator` class:
- `generate_ideas()` - Brainstorm prompt at openai_client.py:32
- `improve_idea()` - Improvement prompt at openai_client.py:81

Both prompts are in Ukrainian and specify strict JSON response formats.

### Adjusting Rate Limits

Rate limits are in `app.py`:
- Global limits: app.py:29
- Per-route limits: `@limiter.limit()` decorators (app.py:70, app.py:121)

### Adding/Removing Google Sheets Columns

Must update in 3 places:
1. `sheets.py:101` - Headers list in `ensure_headers()`
2. `sheets.py:51` - Range in `append_row()` (currently `A:J` for 10 columns)
3. `app.py:219` - Row construction in `/submit` POST handler

### Templates and UI

Templates use Jinja2 in `templates/`:
- `base.html` - Base layout with Bootstrap 5
- `landing.html`, `brainstorm.html`, `improve.html`, `submit.html`, `thankyou.html` - Stage pages
- `admin.html` - Admin dashboard

All pages show stage progress (1/3, 2/3, 3/3) and display Bender quotes.

## Testing

No automated tests currently exist. Manual testing workflow:

1. Start app locally
2. Visit `/` → Click "Почати"
3. Enter prompt → Click "Згенерувати ідеї" → Select idea
4. Enter improvement instruction → Click improve button
5. Edit final title/description → Click "Зберегти ідею"
6. Verify row appears in Google Sheet
7. Visit `/admin` (use ADMIN_PASSWORD) to view submissions

## Known Limitations

- Session data lost on server restart (stored in memory)
- No database - all state in Flask sessions
- IP addresses stored directly in sheet (privacy consideration)
- Rate limiting resets on server restart (memory-backed)
- Bender audio integration depends on external service availability
- No retry logic for Google Sheets API failures
