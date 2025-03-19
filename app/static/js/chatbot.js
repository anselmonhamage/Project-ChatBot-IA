document.addEventListener('DOMContentLoaded', function () {
    
    const chatForm = document.getElementById('chat-form');
    const messagesDiv = document.getElementById('messages');
    const inputField = document.getElementById('message');
    const button = document.getElementById('button');
    const span = document.getElementById('button-text');
    const faqItens = document.querySelectorAll('.faq-questions');

    function enableButton() {
        button.disabled = false;
        button.classList.remove('button-loading');
        span.innerText = "➤";
    }

    function addMessage(text, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
        const sender = isUser ? 'Você' : 'StudentHub';
        messageDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    async function sendMessageToBot(message) {
        try {
            const response = await fetch(CHATBOT_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': CSRF_TOKEN
                },
                body: JSON.stringify({ message })
            });

            if (!response.ok) {
                throw new Error('Erro na resposta do servidor');
            }

            const data = await response.json();
            addMessage(data.answer || 'Desculpe, não entendi sua mensagem.');
        } catch (error) {
            console.error('Erro:', error);
            addMessage('Ocorreu um erro ao processar sua mensagem.');
        } finally {
            enableButton();
        }
    }

    chatForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const userMessage = inputField.value.trim();
        if (!userMessage) return;

        addMessage(userMessage, true);
        inputField.value = '';
        sendMessageToBot(userMessage);
    });

    faqItens.forEach(button => {
        button.addEventListener('click', function (event) {
            event.stopPropagation();
            const clickedQuestion = event.target.textContent.trim();
            
            sendMessageToBot(clickedQuestion);

            this.classList.add('clicked');
            setTimeout(() => this.classList.remove('clicked'), 300);
        });
    });
});