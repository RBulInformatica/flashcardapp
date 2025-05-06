function showExamMenu() {
    hideAll();
    document.getElementById("exam-menu").classList.remove("hidden");
}

function showOwnFlashcards() {
    hideAll();
    document.getElementById("own-flashcards-container").classList.remove("hidden");
}

function showDevelopmentBlog() {
    alert("De ontwikkelingsblog is nog in aanbouw.");
}

function showBiologyTopics() {
    hideAll();
    document.getElementById("biology-topics").classList.remove("hidden");
}

function showImmuneSystemOptions() {
    hideAll();
    document.getElementById("immune-system-options").classList.remove("hidden");
}

function showFlashcards() {
    hideAll();
    document.getElementById("flashcards-container").classList.remove("hidden");

    fetch("/flashcards")
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById("flashcards-body");
            tbody.innerHTML = "";
            data.forEach(item => {
                const row = document.createElement("tr");
                row.innerHTML = `<td>${item.term}</td><td>${item.definition}</td>`;
                tbody.appendChild(row);
            });
        });
}

let currentFlashcard = null;
let showingDefinition = false;

function startPractice() {
    hideAll();
    document.getElementById("practice-container").classList.remove("hidden");
    loadNewFlashcard();
}

function loadNewFlashcard() {
    fetch("/random_flashcard")
        .then(res => res.json())
        .then(data => {
            currentFlashcard = data;
            showingDefinition = false;
            document.getElementById("flashcard").textContent = currentFlashcard.term;
        });
}

function flipCard() {
    if (currentFlashcard) {
        if (showingDefinition) {
            document.getElementById("flashcard").textContent = currentFlashcard.term;
        } else {
            document.getElementById("flashcard").textContent = currentFlashcard.definition;
        }
        showingDefinition = !showingDefinition;
    }
}

function submitAnswer(correct) {
    // Dit is placeholderlogica voor handmatige evaluatie
    alert(correct ? "Juist gekozen!" : "Onjuist gekozen!");
    loadNewFlashcard();
}

function startAIPractice() {
    hideAll();
    document.getElementById("ai-practice-container").classList.remove("hidden");
    loadNewAIFlashcard();
}

let currentAIFlashcard = null;

function loadNewAIFlashcard() {
    fetch("/random_flashcard")
        .then(res => res.json())
        .then(data => {
            currentAIFlashcard = data;
            document.getElementById("ai-flashcard").textContent = currentAIFlashcard.term;
            document.getElementById("ai-answer").value = "";
            document.getElementById("feedback").textContent = "";
        });
}

function submitAIAnswer() {
    const userAnswer = document.getElementById("ai-answer").value;

    fetch("/check_answer", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            user_answer: userAnswer,
            correct_answer: currentAIFlashcard.definition
        })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("feedback").textContent = data.feedback;
        if (data.correct) {
            setTimeout(loadNewAIFlashcard, 2000);
        }
    });
}

function goBack() {
    hideAll();
    document.getElementById("start-menu").classList.remove("hidden");
}

function hideAll() {
    document.querySelectorAll(".menu-container").forEach(el => el.classList.add("hidden"));
}

// Functionaliteit voor het toevoegen van eigen flashcards via het formulier
document.getElementById("flashcard-form")?.addEventListener("submit", function (event) {
    event.preventDefault();
    const term = document.getElementById("term").value;
    const definition = document.getElementById("definition").value;

    fetch("/add_flashcard", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            term: term,
            definition: definition
        })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        if (data.success) {
            document.getElementById("term").value = "";
            document.getElementById("definition").value = "";
        }
    });
});

// Functionaliteit voor het uploaden van een CSV-bestand
document.getElementById("csv-upload-form")?.addEventListener("submit", function (event) {
    event.preventDefault();
    const formData = new FormData();
    formData.append("csvfile", document.querySelector("input[type=file]").files[0]);

    fetch("/upload_csv", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
    });
});
