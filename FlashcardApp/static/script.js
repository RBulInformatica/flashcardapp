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
    window.goBackToStart = goBackToStart;

    fetchFlashcards();  // Optioneel: laad op startpagina
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
    // Voeg logica toe voor eigen flashcards
}

function showBiologyTopics() {
    document.getElementById('exam-menu').classList.add('hidden');
    document.getElementById('biology-topics').classList.remove('hidden');
}

function showImmuneSystemOptions() {
    document.getElementById('flashcards-container').classList.add('hidden');
    document.getElementById('practice-container').classList.add('hidden');
    document.getElementById('ai-practice-container').classList.add('hidden');
    document.getElementById('results-container').classList.add('hidden');
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
    document.getElementById("start-menu").classList.remove("hidden");
    document.getElementById("exam-menu").classList.add("hidden");
    document.getElementById("biology-topics").classList.add("hidden");
    document.getElementById("immune-system-options").classList.add("hidden");
    document.getElementById("flashcards-container").classList.add("hidden");
    document.getElementById("practice-container").classList.add("hidden");
    document.getElementById("ai-practice-container").classList.add("hidden");
    document.getElementById("results-container").classList.add("hidden");

    // Leeg flashcard-tabel
    const list = document.getElementById("flashcards-body");
    if (list) list.innerHTML = "";
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
    fetch("/flashcards")
        .then(response => {
            if (!response.ok) throw new Error("Geen geldige respons");
            return response.json();
        })
        .then(data => {
            console.log("Ontvangen flashcards:", data);
            const list = document.getElementById("flashcards-body");
            if (!list) return;
            list.innerHTML = "";

            if (data.length === 0) {
                const row = document.createElement("tr");
                const cell = document.createElement("td");
                cell.colSpan = 2;
                cell.textContent = "Geen begrippen gevonden.";
                row.appendChild(cell);
                list.appendChild(row);
                return;
            }

            data.forEach(flashcard => {
                const row = document.createElement("tr");
                const termCell = document.createElement("td");
                const definitionCell = document.createElement("td");
                termCell.textContent = flashcard.term;
                definitionCell.textContent = flashcard.definition;
                row.appendChild(termCell);
                row.appendChild(definitionCell);
                list.appendChild(row);
            });
        })
        .catch(error => {
            console.error("Fout bij ophalen flashcards:", error);
        });
}

function fetchFlashcardsForPractice() {
    fetch("/flashcards")
        .then(response => response.json())
        .then(data => {
            flashcards = data;
            currentFlashcardIndex = 0;
            correctAnswers = [];
            incorrectAnswers = [];
            showNextFlashcard();
        })
        .catch(error => console.error("Error fetching flashcards for practice:", error));
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

    fetch("/check_answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_answer: userAnswer,
            correct_answer: flashcard.definition
        })
    })
    .then(response => response.json())
    .then(data => {
        const feedback = data.feedback;
        const isCorrect = data.correct;
        document.getElementById("feedback").textContent = feedback;

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
    location.reload();
}
