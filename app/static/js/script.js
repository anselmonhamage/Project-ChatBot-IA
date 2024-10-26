document.getElementById('quiz-form').addEventListener('submit', function(e) {
    var submitButton = document.getElementById('submit-button');
    submitButton.disabled = true;
    submitButton.textContent = 'Enviando...';
});