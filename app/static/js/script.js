document.getElementById('chat-form').addEventListener('submit', function(e) {

    e.preventDefault()

    const button = document.getElementById('button');
    const span = document.getElementById('button-text');

    // Desabilita o botão e adiciona o efeito de loading
    function disableButton() {
        button.disabled = true;
        span.innerText = ""
        button.classList.add('button-loading');
    }

    disableButton();

});