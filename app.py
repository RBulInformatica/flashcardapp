from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import csv
import os
from flask_sqlalchemy import SQLAlchemy

# Zorg dat deze folder overeenkomt met je Render disk mount path
DATABASE_PATH = '/var/data/flashcards.db'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model voor flashcards
class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(200), nullable=False)
    definition = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"Flashcard('{self.term}', '{self.definition}')"

# Database aanmaken als die nog niet bestaat
with app.app_context():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_flashcard', methods=['GET', 'POST'])
def add_flashcard():
    if request.method == 'POST':
        term = request.form['term']
        definition = request.form['definition']
        new_flashcard = Flashcard(term=term, definition=definition)
        db.session.add(new_flashcard)
        db.session.commit()
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
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(upload_path)
            process_csv(upload_path)
            return redirect(url_for('index'))
    return render_template('upload_csv.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def process_csv(filepath):
    with open(filepath, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            term = row['Begrip']
            definition = row['Betekenis']
            new_flashcard = Flashcard(term=term, definition=definition)
            db.session.add(new_flashcard)
        db.session.commit()

@app.route('/flashcards')
def flashcards():
    all_flashcards = Flashcard.query.all()
    return jsonify([{"term": f.term, "definition": f.definition} for f in all_flashcards])

@app.route('/random_flashcard')
def random_flashcard():
    flashcard = Flashcard.query.order_by(db.func.random()).first()
    if flashcard:
        return jsonify({"term": flashcard.term, "definition": flashcard.definition})
    else:
        return jsonify({"term": "Geen kaarten", "definition": "Je moet eerst kaarten toevoegen."})

@app.route('/check_answer', methods=['POST'])
def check_answer():
    data = request.get_json()
    user_answer = data.get('user_answer', '').strip().lower()
    correct_answer = data.get('correct_answer', '').strip().lower()

    is_correct = user_answer == correct_answer
    feedback = "Juist!" if is_correct else f"Onjuist. Het correcte antwoord is: {correct_answer}"

    return jsonify({"correct": is_correct, "feedback": feedback})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
