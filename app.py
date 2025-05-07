from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import sqlite3
import os
import csv
from sentence_transformers import SentenceTransformer, util

# Setup
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# Maak uploads-map aan
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Pad naar SQLite database
DATABASE = os.path.join(app.root_path, 'database.db')

# Laad AI-model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# --- DATABASE HELPERS ---

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS immuunsysteem (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Begrip TEXT NOT NULL,
            Betekenis TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_flashcard', methods=['GET', 'POST'])
def add_flashcard():
    if request.method == 'POST':
        begrip = request.form.get('term')
        betekenis = request.form.get('definition')

        conn = get_db_connection()
        conn.execute('INSERT INTO immuunsysteem (Begrip, Betekenis) VALUES (?, ?)', (begrip, betekenis))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('add_flashcard.html')

@app.route('/upload_csv', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'Geen bestand geselecteerd!', 400
        file = request.files['file']
        if file.filename == '':
            return 'Geen bestand geselecteerd!', 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            process_csv(filepath)
            return redirect(url_for('index'))
    return render_template('upload_csv.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_csv(filepath):
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        conn = get_db_connection()
        for row in reader:
            begrip = row['Begrip']
            betekenis = row['Betekenis']
            conn.execute('INSERT INTO immuunsysteem (Begrip, Betekenis) VALUES (?, ?)', (begrip, betekenis))
        conn.commit()
        conn.close()

@app.route('/flashcards', methods=['GET'])
def get_flashcards():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Begrip, Betekenis FROM immuunsysteem ORDER BY RANDOM()")
    flashcards = cursor.fetchall()
    conn.close()
    return jsonify([{"term": row["Begrip"], "definition": row["Betekenis"]} for row in flashcards])

@app.route('/random_flashcard', methods=['GET'])
def get_random_flashcard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Begrip, Betekenis FROM immuunsysteem ORDER BY RANDOM() LIMIT 1")
    flashcard = cursor.fetchone()
    conn.close()

    if flashcard:
        return jsonify({"term": flashcard["Begrip"], "definition": flashcard["Betekenis"]})
    else:
        return jsonify({"error": "Geen flashcards beschikbaar"}), 404

@app.route('/evaluate_answer', methods=['POST'])
def evaluate_answer():
    data = request.json
    user_answer = data.get("user_answer")
    correct_answer = data.get("correct_answer")
    is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
    return jsonify({"correct": is_correct})

@app.route('/check_answer', methods=['POST'])
def check_answer():
    data = request.json
    user_answer = data.get("user_answer")
    correct_answer = data.get("correct_answer")

    embedding1 = model.encode(user_answer, convert_to_tensor=True)
    embedding2 = model.encode(correct_answer, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embedding1, embedding2).item()
    is_correct = similarity > 0.75

    feedback = (
        "Goed gedaan! Je antwoord is correct."
        if is_correct
        else f"Je antwoord was niet helemaal correct. De semantische gelijkenis was {similarity:.2f}. Probeer opnieuw."
    )

    return jsonify({"correct": is_correct, "feedback": feedback, "similarity": similarity})

@app.route('/ontwikkelingsblog')
def ontwikkelingsblog():
    return render_template('ontwikkelingsblog.html')

# --- SERVER ---

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
