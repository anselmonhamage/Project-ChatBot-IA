const messageInput = document.getElementById('message-input');
const chatForm = document.getElementById('chat-form');
const chatMessages = document.getElementById('chat-messages');
const chatMessagesContainer = document.getElementById('chatMessagesContainer');
const fileInput = document.getElementById('fileInput');
const modelSelect = document.getElementById('modelSelect');
const serviceToggle = document.getElementById('serviceToggle');
const ollamaUrlGroup = document.getElementById('ollamaUrlGroup');
const ollamaUrlInput = document.getElementById('ollamaUrlInput');
const connectOllamaBtn = document.getElementById('connectOllamaBtn');

let firstMessage = true;
let currentSessionId = null;
let currentExtractionMode = 'text';
let cropper = null;
let croppedImageBlob = null;
let originalFileName = '';
let currentOllamaUrl = null;

if (!window.APP_URLS) {
    console.error('ERRO: window.APP_URLS não foi definido! Verifique se o template HTML está correto.');
}

loadUserProfile();

checkModelsStatus();

setupServiceSelector();

checkModelSelectorScroll();

async function loadUserProfile() {
    try {
        const response = await fetch(window.APP_URLS.userProfile);
        
        if (!response.ok) {
            console.error('Erro ao carregar perfil:', response.status);
            return;
        }
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            console.error('Resposta de perfil não é JSON');
            return;
        }
        
        const data = await response.json();
        
        const userAvatar = document.getElementById('userAvatar');
        if (data.profile_image && userAvatar) {
            userAvatar.innerHTML = `<img src="data:image/jpeg;base64,${data.profile_image}" alt="${data.name}">`;
        }
    } catch (error) {
        console.error('Erro ao carregar perfil:', error);
    }
}

async function checkModelsStatus() {
    try {
        const response = await fetch('/api/models/available');
        
        if (!response.ok) {
            console.error(`❌ Erro ao verificar modelos: HTTP ${response.status}`);
            return;
        }
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            console.error('❌ Resposta de modelos não é JSON');
            return;
        }
        
        const data = await response.json();
        
        if (!data.config.gemini_configured) {
            console.warn('⚠️ Gemini não configurado. Configure GEMINI_API_KEY no servidor.');
        } else {
            console.log('✅ Gemini (online) disponível');
        }
        
        console.log('💡 Para usar modelos locais, mude para "Local" e conecte ao Ollama.');
    } catch (error) {
        console.error('❌ Erro ao verificar modelos:', error);
    }
}

function setupServiceSelector() {
    serviceToggle.addEventListener('change', function() {
        const isLocal = this.checked;
        
        // Mostrar/ocultar campo URL Ollama
        if (isLocal) {
            ollamaUrlGroup.style.display = '';
            // Se já tiver uma URL e nenhum modelo local, tentar conectar automaticamente
            const url = ollamaUrlInput.value.trim();
            const hasLocalModels = Array.from(modelSelect.options).some(opt => opt.dataset.type === 'local');
            if (url && !hasLocalModels) {
                showNotification('💡 Pressione Enter ou clique em conectar para carregar modelos', 'info');
            }
        } else {
            ollamaUrlGroup.style.display = 'none';
        }
        
        updateModelOptions(isLocal);
    });
    
    // Conectar ao Ollama ao pressionar Enter no input
    ollamaUrlInput.addEventListener('keypress', async function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            connectOllamaBtn.click();
        }
    });
    
    // Conectar ao Ollama
    connectOllamaBtn.addEventListener('click', async function() {
        const url = ollamaUrlInput.value.trim();
        if (!url) {
            showNotification('⚠️ Por favor, insira a URL do servidor Ollama (ex: http://localhost:11434)', 'warning');
            ollamaUrlInput.focus();
            return;
        }
        
        connectOllamaBtn.disabled = true;
        connectOllamaBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        
        await loadOllamaModels(url);
        
        connectOllamaBtn.disabled = false;
        connectOllamaBtn.innerHTML = '<i class="fas fa-plug"></i>';
    });
    
    serviceToggle.checked = false;
    updateModelOptions(false);
}

async function loadOllamaModels(url) {
    try {
        console.log(`🔌 Tentando conectar ao Ollama em: ${url}`);
        
        const response = await fetch('/api/models/available', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.CSRF_TOKEN
            },
            body: JSON.stringify({ ollama_url: url })
        });
        
        if (!response.ok) {
            throw new Error(`Servidor retornou erro: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        const localModels = Object.entries(data.models || {}).filter(([k, m]) => m.type === 'local');
        
        if (localModels.length > 0) {
            // Limpar opções locais existentes
            const options = Array.from(modelSelect.options);
            options.forEach(opt => {
                if (opt.dataset.type === 'local') {
                    opt.remove();
                }
            });
            
            // Adicionar novos modelos
            localModels.forEach(([key, model]) => {
                const option = document.createElement('option');
                option.value = key;
                option.textContent = model.name;
                option.dataset.type = 'local';
                modelSelect.appendChild(option);
            });
            
            currentOllamaUrl = url;
            serviceToggle.checked = true;
            updateModelOptions(true);
            
            console.log(`✅ ${localModels.length} modelo(s) local(is) carregado(s)`);
            showNotification(`✅ Conectado! ${localModels.length} modelo(s) encontrado(s)`, 'success');
        } else {
            showNotification('⚠️ Nenhum modelo encontrado. Verifique se o Ollama está rodando e tem modelos instalados.', 'warning');
        }
    } catch (error) {
        console.error('❌ Erro ao carregar modelos Ollama:', error);
        showNotification(`❌ Erro: ${error.message}. Verifique a URL e se o Ollama está rodando.`, 'error');
    }
}

function updateModelOptions(showLocal) {
    const options = modelSelect.querySelectorAll('option');
    let firstValidOption = null;
    let visibleCount = 0;
    
    options.forEach(option => {
        const type = option.dataset.type;
        
        if (showLocal) {
            option.style.display = type === 'local' ? '' : 'none';
            if (type === 'local') {
                visibleCount++;
                if (!firstValidOption) firstValidOption = option;
            }
        } else {
            option.style.display = type === 'online' ? '' : 'none';
            if (type === 'online') {
                visibleCount++;
                if (!firstValidOption) firstValidOption = option;
            }
        }
    });
    
    if (firstValidOption) {
        modelSelect.value = firstValidOption.value;
    }
    
    // Aviso se não houver modelos disponíveis
    if (visibleCount === 0) {
        if (showLocal) {
            showNotification('⚠️ Nenhum modelo local disponível. Conecte ao Ollama primeiro.', 'warning');
        } else {
            showNotification('⚠️ Nenhum modelo online disponível.', 'warning');
        }
    }
    
    console.log(`📊 ${visibleCount} modelo(s) ${showLocal ? 'local(is)' : 'online'} disponível(is)`);
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const message = messageInput.value.trim();
    const hasFile = fileInput.files.length > 0 || croppedImageBlob !== null;
    
    if (!message && !hasFile) return;

    if (firstMessage) {
        chatMessagesContainer.style.display = 'block';
        document.querySelector('.chat-main').classList.add('has-messages');
        firstMessage = false;
    }

    if (message) {
        addMessage(message, 'user');
    } else if (hasFile) {
        addMessage('📷 Processando imagem...', 'user');
    }
    
    messageInput.value = '';
    
    const typingId = showTypingIndicator();
    
    try {
        const selectedModel = modelSelect.value;
        const isLocal = serviceToggle.checked;
        
        // Sempre usar FormData (padrão web)
        const formData = new FormData();
        
        if (hasFile) {
            // Usar blob cortado se disponível, senão usar arquivo original
            if (croppedImageBlob) {
                formData.append('image', croppedImageBlob, originalFileName || 'image.jpg');
            } else if (fileInput.files.length > 0) {
                formData.append('image', fileInput.files[0]);
            }
            formData.append('mode', currentExtractionMode);
            if (message) {
                formData.append('additional_message', message);
            }
        } else {
            formData.append('message', message);
        }
        
        formData.append('model', selectedModel);
        formData.append('session_id', currentSessionId || '');
        
        // Adicionar URL do Ollama se estiver usando modelo local
        if (isLocal && currentOllamaUrl) {
            formData.append('ollama_url', currentOllamaUrl);
        }
        
        const response = await fetch(window.APP_URLS.chatbot, {
            method: 'POST',
            headers: {
                'X-CSRFToken': window.CSRF_TOKEN
            },
            body: formData
        });
        
        removeTypingIndicator(typingId);
        
        // Verificar se a resposta é JSON válido
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const textResponse = await response.text();
            console.error('Resposta não é JSON:', textResponse.substring(0, 200));
            addMessage(`❌ Erro: O servidor retornou uma resposta inválida (${response.status})`, 'bot error');
            return;
        }
        
        let data;
        try {
            data = await response.json();
        } catch (parseError) {
            console.error('Erro ao parsear JSON:', parseError);
            addMessage('❌ Erro: Não foi possível processar a resposta do servidor', 'bot error');
            return;
        }
        
        // Verificar se há erro no response
        if (!response.ok || data.error) {
            const errorMsg = data.error || `Erro ${response.status}: ${response.statusText}`;
            console.error('Erro do servidor:', errorMsg);
            addMessage('❌ ' + errorMsg, 'bot error');
            return;
        }
        
        if (data.response) {
            currentSessionId = data.session_id;
            addMessage(data.response, 'bot', {
                model: data.model,
                type: data.type
            });
        } else {
            addMessage('❌ Resposta inválida do servidor', 'bot error');
        }
    } catch (error) {
        removeTypingIndicator(typingId);
        console.error('Erro ao enviar mensagem:', error);
        addMessage('❌ Erro: ' + error.message, 'bot error');
    } finally {
        // Limpar após envio
        fileInput.value = '';
        croppedImageBlob = null;
        originalFileName = '';
        messageInput.placeholder = 'Digite sua mensagem...';
    }
});

function addMessage(text, type, metadata = {}) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (type === 'bot') {
        // Protege LaTeX antes do Marked processar
        const latexBlocks = [];
        let protectedText = text;
        
        // Protege display math \[...\]
        protectedText = protectedText.replace(/\\\[([\s\S]*?)\\\]/g, (match) => {
            const index = latexBlocks.length;
            latexBlocks.push(match);
            return `LATEX_DISPLAY_${index}`;
        });
        
        // Protege inline math \(...\)
        protectedText = protectedText.replace(/\\\(([\s\S]*?)\\\)/g, (match) => {
            const index = latexBlocks.length;
            latexBlocks.push(match);
            return `LATEX_INLINE_${index}`;
        });
        
        // Processa Markdown
        contentDiv.innerHTML = marked.parse(protectedText);
        
        // Restaura blocos LaTeX
        let html = contentDiv.innerHTML;
        latexBlocks.forEach((latex, index) => {
            html = html.replace(`LATEX_DISPLAY_${index}`, latex);
            html = html.replace(`LATEX_INLINE_${index}`, latex);
        });
        
        // Decodifica entidades HTML que podem ter sido criadas pelo Marked
        html = html.replace(/&lt;/g, '<')
                   .replace(/&gt;/g, '>')
                   .replace(/&amp;/g, '&')
                   .replace(/&quot;/g, '"')
                   .replace(/&#39;/g, "'");
        
        contentDiv.innerHTML = html;
        
        // Renderiza LaTeX
        try {
            renderMathInElement(contentDiv, {
                delimiters: [
                    {left: '$$', right: '$$', display: true},
                    {left: '$', right: '$', display: false},
                    {left: '\\[', right: '\\]', display: true},
                    {left: '\\(', right: '\\)', display: false}
                ],
                throwOnError: false,
                errorColor: '#ff6b6b'
            });
        } catch (e) {
            console.error('Erro ao renderizar LaTeX:', e);
        }
        
        contentDiv.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightElement(block);
        });
        
        if (metadata.model) {
            const badge = document.createElement('div');
            badge.className = 'model-badge';
            const icon = metadata.type === 'local' ? '🏠' : '☁️';
            badge.innerHTML = `${icon} ${metadata.model}`;
            messageDiv.appendChild(badge);
        }
    } else {
        contentDiv.textContent = text;
    }
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

let typingCounter = 0;
function showTypingIndicator() {
    const id = ++typingCounter;
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot typing-indicator';
    typingDiv.id = `typing-${id}`;
    typingDiv.innerHTML = `
        <div class="message-content">
            <div class="typing-dots">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
        </div>
    `;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const typingDiv = document.getElementById(`typing-${id}`);
    if (typingDiv) typingDiv.remove();
}

function insertMathTemplate() {
    currentExtractionMode = 'math';
    updateExtractionModeUI();
    messageInput.value = 'Resolva a equação: ';
    messageInput.focus();
}

function insertCodeTemplate() {
    currentExtractionMode = 'text';
    updateExtractionModeUI();
    messageInput.value = 'Explique o código: ';
    messageInput.focus();
}

function updateExtractionModeUI() {
    const mathBtn = document.querySelector('[onclick="insertMathTemplate()"]');
    const codeBtn = document.querySelector('[onclick="insertCodeTemplate()"]');
    
    if (mathBtn && codeBtn) {
        mathBtn.classList.remove('active');
        codeBtn.classList.remove('active');
        
        if (currentExtractionMode === 'math') {
            mathBtn.classList.add('active');
        } else {
            codeBtn.classList.add('active');
        }
    }
}

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        const file = e.target.files[0];
        originalFileName = file.name;
        
        // Verificar se é uma imagem
        if (file.type.startsWith('image/')) {
            openImagePreview(file);
        } else {
            messageInput.placeholder = `📎 Arquivo: ${file.name}`;
        }
    } else {
        // Se não houver arquivo, restaurar placeholder
        if (!croppedImageBlob) {
            messageInput.placeholder = 'Digite sua mensagem...';
            originalFileName = '';
        }
    }
});

// Funções de Preview e Crop de Imagem
function openImagePreview(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        const modal = document.getElementById('imagePreviewModal');
        const previewImage = document.getElementById('previewImage');
        
        previewImage.src = e.target.result;
        modal.style.display = 'flex';
        
        // Inicializar Cropper.js
        if (cropper) {
            cropper.destroy();
        }
        
        cropper = new Cropper(previewImage, {
            aspectRatio: NaN,
            viewMode: 1,
            autoCropArea: 1,
            responsive: true,
            background: false,
            zoomable: true,
            scalable: true,
            rotatable: true,
            cropBoxResizable: true,
            cropBoxMovable: true,
        });
    };
    reader.readAsDataURL(file);
}

function closeImagePreview() {
    const modal = document.getElementById('imagePreviewModal');
    modal.style.display = 'none';
    
    if (cropper) {
        cropper.destroy();
        cropper = null;
    }
    
    // Só limpar se não houver blob cortado (cancelamento)
    if (!croppedImageBlob) {
        fileInput.value = '';
        originalFileName = '';
        messageInput.placeholder = 'Digite sua mensagem...';
    }
}

function rotateImage(degrees) {
    if (cropper) {
        cropper.rotate(degrees);
    }
}

function confirmCroppedImage() {
    if (!cropper) {
        showNotification('❌ Erro: Editor de imagem não inicializado', 'error');
        return;
    }
    
    try {
        cropper.getCroppedCanvas({
            maxWidth: 4096,
            maxHeight: 4096,
            fillColor: '#fff',
            imageSmoothingEnabled: true,
            imageSmoothingQuality: 'high',
        }).toBlob((blob) => {
            if (!blob) {
                showNotification('❌ Erro ao processar imagem', 'error');
                return;
            }
            
            // Armazenar o blob para envio posterior
            croppedImageBlob = blob;
            
            // Atualizar UI para indicar que a imagem está pronta
            const sizeKB = (blob.size / 1024).toFixed(1);
            messageInput.placeholder = `✅ Imagem ajustada (${sizeKB} KB) - ${originalFileName}`;
            
            console.log(`✅ Imagem processada: ${sizeKB} KB`);
            showNotification('✅ Imagem ajustada com sucesso!', 'success');
            
            // Fechar modal
            closeImagePreview();
        }, 'image/jpeg', 0.95);
    } catch (error) {
        console.error('❌ Erro ao processar imagem:', error);
        showNotification('❌ Erro ao processar imagem: ' + error.message, 'error');
    }
}

// Fechar modal ao clicar fora ou pressionar ESC
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('imagePreviewModal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeImagePreview();
            }
        });
    }
    
    // Fechar modal com ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal && modal.style.display === 'flex') {
            closeImagePreview();
        }
    });
});

// Fix para dispositivos móveis - mantém o botão de enviar fixo quando o teclado aparece/desaparece
function handleMobileKeyboard() {
    const inputSection = document.querySelector('.input-section');
    const sendBtn = document.querySelector('.send-btn');
    
    if (window.innerWidth <= 768) {
        // Força o reflow quando o teclado é aberto/fechado
        let lastHeight = window.innerHeight;
        
        window.addEventListener('resize', () => {
            const currentHeight = window.innerHeight;
            
            // Detecta mudança significativa de altura (teclado abrindo/fechando)
            if (Math.abs(currentHeight - lastHeight) > 100) {
                if (inputSection) {
                    // Força recalculo do layout
                    inputSection.style.transform = 'translateZ(0)';
                    
                    // Remove e readiciona para forçar reposicionamento
                    setTimeout(() => {
                        inputSection.style.transform = '';
                    }, 10);
                }
            }
            
            lastHeight = currentHeight;
        });
        
        // Previne scroll ao focar no input
        messageInput.addEventListener('focus', (e) => {
            setTimeout(() => {
                if (inputSection) {
                    inputSection.scrollIntoView({ behavior: 'smooth', block: 'end' });
                }
            }, 300);
        });
        
        // Garante que o botão mantenha sua posição ao blur
        messageInput.addEventListener('blur', () => {
            setTimeout(() => {
                if (sendBtn) {
                    sendBtn.style.transform = 'translateY(-50%)';
                }
            }, 100);
        });
    }
}

// Sistema de notificações
function showNotification(message, type = 'info') {
    // Remove notificação anterior se existir
    const existingNotification = document.querySelector('.toast-notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `toast-notification toast-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Remover após 4 segundos
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// Verifica se o model selector tem scroll horizontal
function checkModelSelectorScroll() {
    const container = document.querySelector('.model-selector-container');
    if (!container) return;
    
    function updateScrollIndicator() {
        const hasScroll = container.scrollWidth > container.clientWidth;
        if (hasScroll) {
            container.classList.add('has-scroll');
        } else {
            container.classList.remove('has-scroll');
        }
    }
    
    // Verifica inicialmente
    updateScrollIndicator();
    
    // Verifica quando redimensionar
    window.addEventListener('resize', updateScrollIndicator);
    
    // Verifica quando modelos mudarem
    const observer = new MutationObserver(updateScrollIndicator);
    observer.observe(container, { childList: true, subtree: true });
}

// Controla o botão de scroll to bottom
function setupScrollToBottomButton() {
    const scrollBtn = document.getElementById('scrollToBottomBtn');
    const chatMessages = document.getElementById('chat-messages');
    const chatMessagesContainer = document.getElementById('chatMessagesContainer');
    
    if (!scrollBtn || !chatMessages || !chatMessagesContainer) return;
    
    // Função para verificar se está no final
    function isAtBottom() {
        const threshold = 100; // pixels de tolerância
        const scrollTop = chatMessages.scrollTop;
        const scrollHeight = chatMessages.scrollHeight;
        const clientHeight = chatMessages.clientHeight;
        return scrollHeight - scrollTop - clientHeight < threshold;
    }
    
    // Mostra/esconde botão baseado na posição do scroll
    function updateButtonVisibility() {
        if (isAtBottom()) {
            scrollBtn.classList.remove('show');
        } else {
            scrollBtn.classList.add('show');
        }
    }
    
    // Scroll suave para o final
    function scrollToBottom() {
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }
    
    // Event listeners
    chatMessages.addEventListener('scroll', updateButtonVisibility);
    scrollBtn.addEventListener('click', scrollToBottom);
    
    // Observer para detectar novas mensagens
    const observer = new MutationObserver(() => {
        // Se estava no final, mantém no final
        if (isAtBottom()) {
            setTimeout(() => {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }, 10);
        } else {
            // Mostra botão se não estava no final
            updateButtonVisibility();
        }
    });
    
    observer.observe(chatMessages, { childList: true, subtree: true });
}

// Executa quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        handleMobileKeyboard();
        setupScrollToBottomButton();
    });
} else {
    handleMobileKeyboard();
    setupScrollToBottomButton();
}