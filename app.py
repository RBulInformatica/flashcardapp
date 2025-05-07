from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import csv
import os
from flask_sqlalchemy import SQLAlchemy

# Zorg dat relatieve paden vanuit de instance-folder gebruikt worden
app = Flask(__name__, instance_relative_config=True)

# Upload instellingen
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# Pad naar de database in de instance-folder
os.makedirs(app.instance_path, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'flashcards.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model voor flashcards
class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(200), nullable=False)
    definition = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"Flashcard('{self.term}', '{self.definition}')"

# Zorg dat de database wordt aangemaakt
with app.app_context():
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
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)
            process_csv(filepath)
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
    return jsonify({"term": "Geen kaarten beschikbaar", "definition": ""})

@app.route('/check_answer', methods=['POST'])
def check_answer():
    data = request.get_json()
    user_answer = data.get("user_answer", "").strip().lower()
    correct_answer = data.get("correct_answer", "").strip().lower()
    correct = user_answer in correct_answer or correct_answer in user_answer
    feedback = "Correct!" if correct else f"Onjuist. Het juiste antwoord is: {correct_answer}"
    return jsonify({"correct": correct, "feedback": feedback})

@app.route('/ontwikkelingsblog')
def ontwikkelingsblog():
    return render_template('ontwikkelingsblog.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
