# 💡 Idea Factory

QR-based web application for generating STEAM hackathon ideas through a 3-stage process: Brainstorm → Discussion → Selection.

Built with Flask, OpenAI (gpt-5-mini), and Google Sheets.

## Features

- 🧠 **Brainstorm**: Generate 6-8 ideas using AI based on custom prompts
- 💬 **Discussion**: Improve and refine selected ideas with preset or custom instructions
- ✅ **Selection**: Finalize and save ideas to Google Sheets
- 🤖 **Bender Quotes**: Motivational Ukrainian quotes at each stage
- 📊 **Admin Dashboard**: View recent submissions (password protected)
- 📱 **Mobile-First**: Responsive design with Bootstrap 5
- 🎯 **Stage Navigation**: Clear breadcrumb-style progress indicator

## Quick Start

### 1. Install Dependencies

```bash
cd idea_factory
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: Model to use (default: `gpt-5-mini`)
- `GOOGLE_SHEETS_SPREADSHEET_ID`: Your Google Spreadsheet ID
- `GOOGLE_SHEETS_CREDS`: Service account credentials as JSON string
- `APP_SECRET_KEY`: Random secret key for Flask sessions

Optional:
- `ADMIN_PASSWORD`: Password for admin dashboard
- `IP_HASH_SALT`: Salt for IP hashing

### 3. Set Up Google Sheets

#### Create a Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google Sheets API**
4. Create a **Service Account**:
   - Go to "IAM & Admin" → "Service Accounts"
   - Click "Create Service Account"
   - Give it a name (e.g., "idea-factory-bot")
   - Grant it "Editor" role
   - Click "Done"
5. Create a **JSON key**:
   - Click on the service account
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key" → "JSON"
   - Download the JSON file

#### Configure the Spreadsheet

1. Create a new Google Spreadsheet
2. Copy the Spreadsheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
   ```
3. Share the spreadsheet with your service account email:
   - Click "Share" button
   - Add the service account email (found in the JSON file as `client_email`)
   - Give it "Editor" permissions

#### Add Credentials to .env

Copy the entire JSON content and paste it as a single line in your `.env` file:

```bash
GOOGLE_SHEETS_CREDS={"type":"service_account","project_id":"...","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...@....iam.gserviceaccount.com",...}
```

### 4. Run the Application

```bash
python app.py
```

The app will run on `http://localhost:5000`

## Generating a QR Code

Use any QR code generator to create a QR code pointing to your deployed URL:

- Online: [qr-code-generator.com](https://www.qr-code-generator.com/)
- Python:
  ```bash
  pip install qrcode[pil]
  python -c "import qrcode; qrcode.make('https://your-app-url.com').save('qr.png')"
  ```

## Deployment

### Render.com

1. Create a new **Web Service**
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn app:app`
5. Add environment variables in Render dashboard
6. Deploy!

Add to `requirements.txt`:
```
gunicorn==21.2.0
```

### Fly.io

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Login: `fly auth login`
3. Launch: `fly launch`
4. Set secrets:
   ```bash
   fly secrets set OPENAI_API_KEY=your_key
   fly secrets set GOOGLE_SHEETS_CREDS='{"type":"service_account",...}'
   ```
5. Deploy: `fly deploy`

### Heroku

1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Set environment variables:
   ```bash
   heroku config:set OPENAI_API_KEY=your_key
   heroku config:set GOOGLE_SHEETS_CREDS='{"type":"service_account",...}'
   ```
5. Deploy:
   ```bash
   git push heroku main
   ```

Create a `Procfile`:
```
web: gunicorn app:app
```

## Project Structure

```
idea_factory/
├── app.py                 # Main Flask application
├── openai_client.py       # OpenAI integration
├── sheets.py              # Google Sheets integration
├── bender_quotes.py       # Bender quotes collection
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── templates/            # Jinja2 templates
│   ├── base.html
│   ├── landing.html
│   ├── brainstorm.html
│   ├── improve.html
│   ├── submit.html
│   ├── thankyou.html
│   └── admin.html
└── README.md
```

## Google Sheets Schema

The app creates/uses a sheet named "Ideas" with these columns:

| Column | Description |
|--------|-------------|
| timestamp_utc | Submission timestamp (UTC) |
| session_id | Unique session identifier |
| stage | Always "final" for completed submissions |
| prompt_initial | User's initial brainstorm prompt |
| ideas_generated_json | JSON array of all generated ideas |
| idea_selected_title | Title of selected idea |
| idea_selected_description | Description of selected idea |
| user_edit_notes | User's improvement instructions |
| final_title | Final submitted title |
| final_description | Final submitted description |
| likes_or_tag | Reserved for future use |
| user_agent | Browser user agent |
| ip_hash | SHA256 hash of IP address |

## Rate Limiting

- **Brainstorm**: 20 requests per hour per IP
- **Improve**: 30 requests per hour per IP
- **Global**: 200 requests per day, 50 per hour per IP

## Security Features

- IP address hashing (SHA256 with salt)
- Rate limiting per IP
- HTML sanitization for LLM outputs
- Admin password protection
- Session-based state management
- No raw IP logging

## Troubleshooting

### "GOOGLE_SHEETS_CREDS environment variable not set"
Make sure your `.env` file exists and contains the `GOOGLE_SHEETS_CREDS` variable with valid JSON.

### "Invalid JSON in GOOGLE_SHEETS_CREDS"
Ensure the JSON is properly formatted as a single line with escaped quotes if needed.

### "Permission denied" when writing to Google Sheets
Make sure you've shared the spreadsheet with the service account email.

### OpenAI API errors
- Check your API key is valid
- Ensure you have credits in your OpenAI account
- Verify the model name is correct (`gpt-5-mini`)

## License

MIT License - feel free to use for your hackathon or educational purposes!
