"""Main Flask application for Idea Factory."""

import json
import os
import uuid
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

from bender_quotes import get_random_quote
from openai_client import IdeaGenerator
from sheets import SheetsClient
from bender_audio import play_bender_audio

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Initialize clients
idea_generator = IdeaGenerator()
sheets_client = SheetsClient()

# Ensure sheet has headers
try:
    sheets_client.ensure_headers()
except Exception as e:
    print(f"Warning: Could not ensure headers: {e}")


def admin_required(f):
    """Decorator to require admin password."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_password = os.getenv('ADMIN_PASSWORD')
        if not admin_password:
            return "Admin access not configured", 403
        
        auth = request.authorization
        if not auth or auth.password != admin_password:
            return ('Admin access required', 401, {
                'WWW-Authenticate': 'Basic realm="Admin Access"'
            })
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def landing():
    """Landing page."""
    quote = get_random_quote('landing')
    play_bender_audio(quote)  # Play audio in background
    return render_template('landing.html', quote=quote)


@app.route('/brainstorm', methods=['GET', 'POST'])
@limiter.limit("20 per hour")
def brainstorm():
    """Brainstorm page - generate ideas."""
    if request.method == 'GET':
        # Show initial brainstorm form
        default_prompt = """Згенеруй 6 ідей для шкільного STEAM-хакатону як продовження теми енергоефективних міст.
У кожній ідеї: назва (до 8 слів), 1–2 речення опису, і коротко: що можна реально зробити за 1–2 дні в школі.
Додай щонайменше 2 ідеї з дроном та 2 з AI/даними. Пиши українською."""
        
        quote = get_random_quote('brainstorm')
        play_bender_audio(quote)  # Play audio in background
        return render_template('brainstorm.html', 
                             default_prompt=default_prompt,
                             quote=quote,
                             stage=1)
    
    # POST - generate ideas
    prompt = request.form.get('prompt', '').strip()
    if not prompt:
        flash('Будь ласка, введіть промпт для генерації ідей', 'error')
        return redirect(url_for('brainstorm'))
    
    try:
        # Generate session ID if not exists
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        # Store prompt in session
        session['prompt_initial'] = prompt
        
        # Generate ideas
        quote = get_random_quote('brainstorm')
        play_bender_audio(quote)  # Play audio in background
        ideas = idea_generator.generate_ideas(prompt)
        
        # Store ideas in session
        session['ideas_generated'] = ideas
        
        return render_template('brainstorm.html',
                             prompt=prompt,
                             ideas=ideas,
                             quote=quote,
                             stage=1,
                             generated=True)
    
    except Exception as e:
        flash(f'Помилка при генерації ідей. Спробуйте ще раз. ({str(e)})', 'error')
        return redirect(url_for('brainstorm'))


@app.route('/improve', methods=['POST'])
@limiter.limit("30 per hour")
def improve():
    """Improve/discuss selected idea."""
    # Get selected idea from form
    idea_index = request.form.get('idea_index')
    action = request.form.get('action', 'select')
    
    if idea_index is None:
        flash('Будь ласка, оберіть ідею', 'error')
        return redirect(url_for('brainstorm'))
    
    try:
        idea_index = int(idea_index)
        ideas = session.get('ideas_generated', [])
        
        if idea_index < 0 or idea_index >= len(ideas):
            flash('Невірний індекс ідеї', 'error')
            return redirect(url_for('brainstorm'))
        
        selected_idea = ideas[idea_index]
        session['selected_idea'] = selected_idea
        
        # If action is 'select', just show the improve page
        if action == 'select':
            quote = get_random_quote('improve')
            play_bender_audio(quote)  # Play audio in background
            return render_template('improve.html',
                                 idea=selected_idea,
                                 quote=quote,
                                 stage=2)
        
        # If action is 'improve', regenerate with instruction
        instruction = request.form.get('instruction', '').strip()
        
        if not instruction:
            flash('Будь ласка, введіть інструкцію для покращення', 'error')
            quote = get_random_quote('improve')
            return render_template('improve.html',
                                 idea=selected_idea,
                                 quote=quote,
                                 stage=2)
        
        # Store edit notes
        session['user_edit_notes'] = instruction
        
        # Improve the idea
        improved = idea_generator.improve_idea(selected_idea, instruction)
        session['selected_idea'] = improved
        
        quote = get_random_quote('improve')
        play_bender_audio(quote)  # Play audio in background
        return render_template('improve.html',
                             idea=improved,
                             quote=quote,
                             stage=2,
                             improved=True,
                             changes=improved.get('changes_summary', ''))
    
    except Exception as e:
        flash(f'Помилка при покращенні ідеї. Спробуйте ще раз. ({str(e)})', 'error')
        return redirect(url_for('brainstorm'))


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    """Submit final idea."""
    if request.method == 'GET':
        # Show submit form
        selected_idea = session.get('selected_idea')
        if not selected_idea:
            flash('Спочатку оберіть ідею', 'error')
            return redirect(url_for('brainstorm'))
        
        quote = get_random_quote('submit')
        play_bender_audio(quote)  # Play audio in background
        return render_template('submit.html',
                             idea=selected_idea,
                             quote=quote,
                             stage=3)
    
    # POST - save to Google Sheets
    final_title = request.form.get('final_title', '').strip()
    final_description = request.form.get('final_description', '').strip()
    
    if not final_title or not final_description:
        flash('Будь ласка, заповніть назву та опис', 'error')
        return redirect(url_for('submit'))
    
    try:
        # Prepare row data (10 columns)
        timestamp_utc = datetime.utcnow().isoformat()
        session_id = session.get('session_id', '')
        prompt_initial = session.get('prompt_initial', '')
        selected_idea = session.get('selected_idea', {})
        user_edit_notes = session.get('user_edit_notes', '')
        user_agent = request.headers.get('User-Agent', '')
        ip_address = request.remote_addr or ''
        
        row = [
            timestamp_utc,
            session_id,
            prompt_initial,
            selected_idea.get('title', ''),
            selected_idea.get('description', ''),
            user_edit_notes,
            final_title,
            final_description,
            user_agent,
            ip_address
        ]
        
        # Append to Google Sheets
        success = sheets_client.append_row(row)
        
        if not success:
            flash('Помилка при збереженні. Спробуйте ще раз.', 'error')
            return redirect(url_for('submit'))
        
        # Store final data for thank you page
        session['final_title'] = final_title
        session['final_description'] = final_description
        session['timestamp'] = timestamp_utc
        
        return redirect(url_for('thankyou'))
    
    except Exception as e:
        flash(f'Помилка при збереженні. Спробуйте ще раз. ({str(e)})', 'error')
        return redirect(url_for('submit'))


@app.route('/thankyou')
def thankyou():
    """Thank you page after submission."""
    final_title = session.get('final_title')
    if not final_title:
        return redirect(url_for('landing'))
    
    quote = get_random_quote('thankyou')
    play_bender_audio(quote)  # Play audio in background
    timestamp = session.get('timestamp', '')
    session_id = session.get('session_id', '')
    
    return render_template('thankyou.html',
                         quote=quote,
                         title=final_title,
                         timestamp=timestamp,
                         session_id=session_id)


@app.route('/admin')
@admin_required
def admin():
    """Admin dashboard to view recent ideas."""
    try:
        rows = sheets_client.read_recent_rows(limit=50)
        if rows is None:
            flash('Помилка при читанні даних', 'error')
            rows = []
        
        return render_template('admin.html', rows=rows)
    
    except Exception as e:
        return f"Error loading admin page: {e}", 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
