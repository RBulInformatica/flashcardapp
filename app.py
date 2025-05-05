from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sentence_transformers import SentenceTransformer, util
import csv
import random
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuratie: SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcards.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flashcard-model (voor database)
class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(200), nullable=False)
    definition = db.Column(db.String(500), nullable=False)

    def to_dict(self):
        return {
            'term': self.term,
            'definition': self.definition
        }

# Initialiseer SentenceTransformer model voor AI beoordeling
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def load_flashcards_from_csv():
    flashcards = []
    with open('flashcards.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            flashcards.append({
                "term": row["Begrip"],
                "definition": row["Betekenis"]
            })
    return flashcards

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/flashcards', methods=['GET'])
def get_flashcards():
    # Haal flashcards uit de database (SQLite)
    flashcards = Flashcard.query.all()
    return jsonify([card.to_dict() for card in flashcards])

@app.route('/random_flashcard', methods=['GET'])
def get_random_flashcard():
    # Haal een willekeurige flashcard uit de database (SQLite)
    flashcards = Flashcard.query.all()
    if flashcards:
        return jsonify(random.choice(flashcards).to_dict())
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

    # Gebruik de SentenceTransformer om semantische gelijkenis te berekenen
    embedding1 = model.encode(user_answer, convert_to_tensor=True)
    embedding2 = model.encode(correct_answer, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(embedding1, embedding2).item()

    is_correct = similarity > 0.75
    if is_correct:
        feedback = "Goed gedaan! Je antwoord is correct."
    else:
        feedback = f"Je antwoord was niet helemaal correct. De semantische gelijkenis was {similarity:.2f}. Probeer het opnieuw."

    return jsonify({"correct": is_correct, "feedback": feedback, "similarity": similarity})

# Voor het vullen van de database met flashcards (bij de eerste keer draaien)
@app.route('/populate_flashcards', methods=['GET'])
def populate_flashcards():
    flashcards = load_flashcards_from_csv()
    for flashcard in flashcards:
        existing_flashcard = Flashcard.query.filter_by(term=flashcard['term']).first()
        if not existing_flashcard:
            new_flashcard = Flashcard(term=flashcard['term'], definition=flashcard['definition'])
            db.session.add(new_flashcard)
    db.session.commit()
    return jsonify({"message": "Flashcards populated successfully!"})

if __name__ == '__main__':
    # Zet de database en de tabel aan de start van de applicatie
    db.create_all()
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))
    serve(app, host='0.0.0.0', port=port)
