from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
import csv
import random
import os

app = Flask(__name__)
CORS(app)

# Configuratie voor SQLite (Render ondersteunt dit standaard)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashcards.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Laden van het semantische model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Model voor uitbreiding in de toekomst (momenteel niet in gebruik)
class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(255), nullable=False)
    definition = db.Column(db.String(255), nullable=False)

# Flashcards laden vanuit CSV
def load_flashcards_from_csv():
    flashcards = []
    try:
        with open('flashcards.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                flashcards.append({
                    "term": row["Begrip"],
                    "definition": row["Betekenis"]
                })
    except FileNotFoundError:
        print("⚠️  flashcards.csv niet gevonden.")
    return flashcards

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/flashcards', methods=['GET'])
def get_flashcards():
    flashcards = load_flashcards_from_csv()
    random.shuffle(flashcards)
    return jsonify(flashcards)

@app.route('/random_flashcard', methods=['GET'])
def get_random_flashcard():
    flashcards = load_flashcards_from_csv()
    if flashcards:
        return jsonify(random.choice(flashcards))
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
    if is_correct:
        feedback = "Goed gedaan! Je antwoord is correct."
    else:
        feedback = f"Je antwoord was niet helemaal correct. De semantische gelijkenis was {similarity:.2f}. Probeer het opnieuw."

    return jsonify({"correct": is_correct, "feedback": feedback, "similarity": similarity})

# Start de app via waitress, met database creatie in juiste context
if __name__ == '__main__':
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))

    with app.app_context():
        db.create_all()

    serve(app, host='0.0.0.0', port=port)
