from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import csv
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcards.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model voor flashcards
class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(200), nullable=False)
    definition = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"Flashcard('{self.term}', '{self.definition}')"

# Zorg ervoor dat de database wordt aangemaakt als deze nog niet bestaat
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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # CSV-bestand verwerken en flashcards toevoegen aan de database
            process_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))
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

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

