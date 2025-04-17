from flask import Flask, jsonify, render_template, request
 import sqlite3
 import random
 import os  # <-- Dit was vergeten
 import os
 if not os.path.exists("database.db"):
     raise FileNotFoundError("Database ontbreekt in de deployment-omgeving!")
 
 app = Flask(__name__)
 DATABASE = "database.db"
 
 model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
 
 def get_db_connection():
     conn = sqlite3.connect(DATABASE)
     conn.row_factory = sqlite3.Row
     return conn
 
 @app.route('/')
 def index():
     return render_template('index.html')
 
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
 
     # Bereken de semantische gelijkenis
     embedding1 = model.encode(user_answer, convert_to_tensor=True)
     embedding2 = model.encode(correct_answer, convert_to_tensor=True)
     similarity = util.pytorch_cos_sim(embedding1, embedding2).item()
 
     # Stel een drempelwaarde in (bijv. 0.75 = redelijk correct)
     is_correct = similarity > 0.75
 
     # Geef feedback op basis van de semantische gelijkenis
     if is_correct:
         feedback = "Goed gedaan! Je antwoord is correct."
     else:
         feedback = f"Je antwoord was niet helemaal correct. De semantische gelijkenis was {similarity:.2f}. Probeer het opnieuw."
 
     return jsonify({"correct": is_correct, "feedback": feedback, "similarity": similarity})
 
 if __name__ == '__main__':
     from waitress import serve
     port = int(os.environ.get("PORT", 5000))
     serve(app, host='0.0.0.0', port=port)
