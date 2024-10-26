document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chat-form');
    const messagesDiv = document.getElementById('messages');
    const inputField = document.getElementById('message');

    chatForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const userMessage = inputField.value.trim();
        if (userMessage === "") return;

        // Exibir a mensagem do usuário
        const userDiv = document.createElement('div');
        userDiv.classList.add('user-message');
        userDiv.innerHTML = `<strong>Você:</strong> ${userMessage}`;
        messagesDiv.appendChild(userDiv);

        // Limpar o campo de entrada
        inputField.value = '';

        // Enviar a mensagem para o servidor via AJAX
        fetch(CHATBOT_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRF_TOKEN
            },
            body: JSON.stringify({ message: userMessage })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na resposta do servidor');
            }
            return response.json();
        })
        .then(data => {
            if (data.answer) {
                const botDiv = document.createElement('div');
                botDiv.classList.add('bot-message');
                botDiv.innerHTML = `<strong>StudentHub:</strong> ${data.answer}`;
                messagesDiv.appendChild(botDiv);
            } else {
                const errorDiv = document.createElement('div');
                errorDiv.classList.add('bot-message');
                errorDiv.innerHTML = `<strong>StudentHub:</strong> Desculpe, não entendi sua mensagem.`;
                messagesDiv.appendChild(errorDiv);
            }

            // Rolar para a última mensagem
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        })
        .catch(error => {
            console.error('Erro:', error);
            const errorDiv = document.createElement('div');
            errorDiv.classList.add('bot-message');
            errorDiv.innerHTML = `<strong>Bot:</strong> Ocorreu um erro ao processar sua mensagem.`;
            messagesDiv.appendChild(errorDiv);
        });
    });
});
