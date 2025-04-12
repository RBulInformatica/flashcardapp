document.addEventListener('DOMContentLoaded', function() {
    // Koppel de functies aan de knoppen
    window.showExamMenu = showExamMenu;
    window.showOwnFlashcards = showOwnFlashcards;
    window.showBiologyTopics = showBiologyTopics;
    window.showImmuneSystemOptions = showImmuneSystemOptions;
    window.showFlashcards = showFlashcards;
    window.startPractice = startPractice;
    window.startAIPractice = startAIPractice;
    window.goBack = goBack;
    window.flipCard = flipCard;
    window.submitAnswer = submitAnswer;
    window.submitAIAnswer = submitAIAnswer;
    window.retryIncorrect = retryIncorrect;
    window.showDevelopmentBlog = showDevelopmentBlog;

    // Laad de flashcards bij het laden van de pagina
    fetchFlashcards();
});

let flashcards = [];
let currentFlashcardIndex = 0;
let correctAnswers = [];
let incorrectAnswers = [];

function showExamMenu() {
    document.getElementById('start-menu').classList.add('hidden');
    document.getElementById('exam-menu').classList.remove('hidden');
}

function showOwnFlashcards() {
    // Voeg hier de logica toe om eigen flashcards te tonen
}

function showBiologyTopics() {
    document.getElementById('exam-menu').classList.add('hidden');
    document.getElementById('biology-topics').classList.remove('hidden');
}

function showImmuneSystemOptions() {
    document.getElementById('flashcards-container').classList.add('hidden'); // Verberg begrippenlijst
    document.getElementById('practice-container').classList.add('hidden'); // Verberg oefenmodus als die open was
    document.getElementById('ai-practice-container').classList.add('hidden'); // Verberg AI oefenmodus als die open was
    document.getElementById('immune-system-options').classList.remove('hidden');
}

function showFlashcards() {
    document.getElementById('immune-system-options').classList.add('hidden');
    document.getElementById('flashcards-container').classList.remove('hidden');
    fetchFlashcards();
}

function startPractice() {
    document.getElementById('immune-system-options').classList.add('hidden');
    document.getElementById('practice-container').classList.remove('hidden');
    fetchFlashcardsForPractice();
}

function startAIPractice() {
    document.getElementById('immune-system-options').classList.add('hidden');
    document.getElementById('ai-practice-container').classList.remove('hidden');
    fetchFlashcardsForPractice();
}

function goBack() {
    // Verberg alle secties behalve het hoofdmenu
    document.getElementById("vak-sectie").classList.add("hidden");
    document.getElementById("onderwerp-sectie").classList.add("hidden");
    document.getElementById("flashcard-sectie").classList.add("hidden");
    document.getElementById("antwoord-sectie").classList.add("hidden");
    document.getElementById("feedback").textContent = "";
    document.getElementById("gebruiker-antwoord").value = "";

    // Leeg de flashcards-tabel (anders blijven ze staan)
    document.getElementById("flashcards-body").innerHTML = "";

    // Verberg flashcards sectie
    document.getElementById("flashcards").classList.add("hidden");

    // Toon hoofdmenu opnieuw
    document.getElementById("main-menu").classList.remove("hidden");

    // Reset opgeslagen onderwerp
    geselecteerdOnderwerp = null;
}

function flipCard() {
    const flashcard = document.getElementById('flashcard');
    if (flashcard.dataset.flipped === 'true') {
        flashcard.textContent = flashcard.dataset.term;
        flashcard.dataset.flipped = 'false';
    } else {
        flashcard.textContent = flashcard.dataset.definition;
        flashcard.dataset.flipped = 'true';
    }
}

function submitAnswer(isCorrect) {
    const flashcard = flashcards[currentFlashcardIndex];
    if (isCorrect) {
        correctAnswers.push(flashcard);
    } else {
        incorrectAnswers.push(flashcard);
    }
    currentFlashcardIndex++;
    if (currentFlashcardIndex < flashcards.length) {
        showNextFlashcard();
    } else {
        showResults();
    }
}

function fetchFlashcards() {
    fetch("http://127.0.0.1:5000/flashcards")
        .then(response => response.json())
        .then(data => {
            const list = document.getElementById("flashcards-body");
            list.innerHTML = "";
            data.forEach(flashcard => {
                const row = document.createElement("tr");
                const termCell = document.createElement("td");
                const definitionCell = document.createElement("td");
                termCell.textContent = flashcard.term; // Zorg ervoor dat de JSON-velden overeenkomen met de databasevelden
                definitionCell.textContent = flashcard.definition; // Zorg ervoor dat de JSON-velden overeenkomen met de databasevelden
                row.appendChild(termCell);
                row.appendChild(definitionCell);
                list.appendChild(row);
            });
        })
        .catch(error => console.error("Error fetching flashcards:", error));
}

function fetchFlashcardsForPractice() {
    fetch("http://127.0.0.1:5000/flashcards")
        .then(response => response.json())
        .then(data => {
            flashcards = data;
            currentFlashcardIndex = 0;
            correctAnswers = [];
            incorrectAnswers = [];
            showNextFlashcard();
        })
        .catch(error => console.error("Error fetching flashcards:", error));
}

function showNextFlashcard() {
    const flashcard = flashcards[currentFlashcardIndex];
    if (!flashcard) return;
    
    const normalFlashcardElement = document.getElementById('flashcard');
    const aiFlashcardElement = document.getElementById('ai-flashcard');

    if (normalFlashcardElement) {
        normalFlashcardElement.textContent = flashcard.term;
        normalFlashcardElement.dataset.term = flashcard.term;
        normalFlashcardElement.dataset.definition = flashcard.definition;
        normalFlashcardElement.dataset.flipped = 'false';
    }

    if (aiFlashcardElement) {
        aiFlashcardElement.textContent = flashcard.term;
    }
}

function showResults() {
    const resultsContainer = document.getElementById('results-container');
    resultsContainer.innerHTML = `
        <h2>Resultaten</h2>
        <p>Goed: ${correctAnswers.length}</p>
        <p>Fout: ${incorrectAnswers.length}</p>
        <button class="button" onclick="startPractice()">Oefenen</button>
        <button class="button" onclick="startAIPractice()">Oefenen met AI</button>
        <button class="button" onclick="retryIncorrect()">Herhaal foute begrippen</button>
        <button class="button" onclick="showImmuneSystemOptions()">Terug</button>
    `;
    document.getElementById('practice-container').classList.add('hidden');
    resultsContainer.classList.remove('hidden');
}

function submitAIAnswer() {
    const userAnswer = document.getElementById("ai-answer").value;
    const flashcard = flashcards[currentFlashcardIndex];

    fetch("http://127.0.0.1:5000/check_answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_answer: userAnswer,
            correct_answer: flashcard.definition
        })
    })
    .then(response => response.json())
    .then(data => {
        const feedback = data.feedback;  // Haal de feedback op uit het antwoord
        const isCorrect = data.correct;

        // Toon de feedback aan de gebruiker
        document.getElementById("feedback").textContent = feedback;

        // Als het antwoord correct is, ga naar de volgende flashcard
        if (isCorrect) {
            currentFlashcardIndex++;
            if (currentFlashcardIndex < flashcards.length) {
                showNextFlashcard();
            } else {
                showResults();
            }
        }
    })
    .catch(error => console.error("Error checking answer:", error));
}

function retryIncorrect() {
    flashcards = incorrectAnswers;
    currentFlashcardIndex = 0;
    correctAnswers = [];
    incorrectAnswers = [];
    document.getElementById('results-container').classList.add('hidden');
    document.getElementById('practice-container').classList.remove('hidden');
    showNextFlashcard();
}

function showDevelopmentBlog() {
    const startMenu = document.getElementById('start-menu');
    startMenu.innerHTML = `
        <h2>Ontwikkelings blog</h2>
        <p>Richard Feynman zei ooit dat als je iets begrijpt, je het moet kunnen uitleggen. Met deze nieuwe manier van flashcards leren, kan je dit toepassen.</p>
        <button class="button" onclick="goBackToStart()">Terug</button>
    `;
}

function goBackToStart() {
    location.reload(); // Herlaad de pagina om terug te gaan naar het startmenu
}