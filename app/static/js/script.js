document.getElementById('chat-form').addEventListener('submit', function(e) {

    e.preventDefault()

    const button = document.getElementById('button');
    const span = document.getElementById('button-text');

    function disableButton() {
        button.disabled = true;
        span.textContent = null
        button.classList.add('button-loading');
    }

    disableButton();

});