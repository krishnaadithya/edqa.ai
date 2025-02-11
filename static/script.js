let player;
let questions = [];
let currentQuestionIndex = -1;
let timeCheckInterval = null; // Store interval ID

function onYouTubeIframeAPIReady() {
    // This function will be called when the YouTube API is ready
}

function processVideo() {
    const videoUrl = document.getElementById('videoUrl').value;
    const gradeLevel = document.getElementById('gradeLevel').value;
    const numQuestions = document.getElementById('numQuestions').value;
    
    // Clear any existing interval
    if (timeCheckInterval) {
        clearInterval(timeCheckInterval);
        timeCheckInterval = null;
    }
    
    fetch('/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            video_url: videoUrl,
            grade_level: parseInt(gradeLevel),
            num_questions: parseInt(numQuestions)
        })
    })
    .then(response => response.json())
    .then(data => {
        questions = data.questions;
        console.log("Loaded questions:", questions); // Debug log
        initializePlayer(data.video_id);
        document.getElementById('videoSection').classList.remove('hidden');
        renderQuestions();
        currentQuestionIndex = -1; // Reset question index
    });
}

function initializePlayer(videoId) {
    player = new YT.Player('player', {
        height: '360',
        width: '640',
        videoId: videoId,
        events: {
            'onStateChange': onPlayerStateChange,
            'onReady': onPlayerReady
        }
    });
}

function onPlayerReady(event) {
    console.log("Player is ready");
}

function onPlayerStateChange(event) {
    console.log("Player state changed:", event.data);
    
    if (event.data == YT.PlayerState.PLAYING) {
        // Clear any existing interval before starting a new one
        if (timeCheckInterval) {
            clearInterval(timeCheckInterval);
        }
        checkQuestionTiming();
    } else if (event.data == YT.PlayerState.PAUSED || event.data == YT.PlayerState.ENDED) {
        // Clear interval when video is paused or ended
        if (timeCheckInterval) {
            clearInterval(timeCheckInterval);
            timeCheckInterval = null;
        }
    }
}

function checkQuestionTiming() {
    timeCheckInterval = setInterval(() => {
        if (player && player.getCurrentTime) {
            const currentTime = player.getCurrentTime();
            console.log("Current time:", currentTime); // Debug log
            
            questions.forEach((question, index) => {
                // Wider time window for matching (2 seconds)
                if (Math.abs(currentTime - question.timestamp) < 2 && currentQuestionIndex !== index) {
                    console.log(`Triggering question ${index} at time ${currentTime}`); // Debug log
                    currentQuestionIndex = index;
                    player.pauseVideo();
                    showQuestion(index);
                }
            });
        }
    }, 500); // Check more frequently (every 500ms)
}

function showQuestion(index) {
    // Highlight the question
    highlightQuestion(index);
    
    // Show a notification or visual indicator
    const questionCard = document.getElementById(`question-${index}`);
    questionCard.classList.add('question-active', 'animate-pulse');
    
    // Add a "Continue" button if it doesn't exist
    if (!document.getElementById(`continue-${index}`)) {
        const continueButton = document.createElement('button');
        continueButton.id = `continue-${index}`;
        continueButton.className = 'mt-2 ml-2 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600';
        continueButton.textContent = 'Continue Video';
        continueButton.onclick = () => {
            player.playVideo();
            questionCard.classList.remove('animate-pulse');
        };
        questionCard.appendChild(continueButton);
    }
}

function renderQuestions() {
    const container = document.getElementById('questionsContainer');
    container.innerHTML = '';
    
    questions.forEach((question, index) => {
        const questionCard = document.createElement('div');
        questionCard.className = 'question-card';
        questionCard.id = `question-${index}`;
        
        questionCard.innerHTML = `
            <p class="font-semibold">${question.question}</p>
            <div class="answer-hidden" id="answer-${index}">
                ${question.answer}
            </div>
            <button onclick="toggleAnswer(${index})" 
                    class="mt-2 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                Show Answer
            </button>
        `;
        
        container.appendChild(questionCard);
    });
}

function toggleAnswer(index) {
    const answerElement = document.getElementById(`answer-${index}`);
    if (answerElement.classList.contains('answer-hidden')) {
        answerElement.classList.remove('answer-hidden');
        answerElement.classList.add('answer-visible');
    } else {
        answerElement.classList.remove('answer-visible');
        answerElement.classList.add('answer-hidden');
    }
}

function highlightQuestion(index) {
    // Remove highlight from all questions
    document.querySelectorAll('.question-card').forEach(card => {
        card.classList.remove('question-active');
    });
    
    // Add highlight to current question
    const questionCard = document.getElementById(`question-${index}`);
    questionCard.classList.add('question-active');
    questionCard.scrollIntoView({ behavior: 'smooth' });
} 