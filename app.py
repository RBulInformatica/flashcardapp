from flask import Flask, jsonify, render_template, request
from sentence_transformers import SentenceTransformer, util
import csv
import random
import os

app = Flask(__name__)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# ✅ Laad flashcards uit CSV-bestand (gescheiden door ;)
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

if __name__ == '__main__':
    from waitress import serve
    port = int(os.environ.get("PORT", 5000))
    serve(app, host='0.0.0.0', port=port)
