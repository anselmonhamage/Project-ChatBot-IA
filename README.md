# StudentHub - Assistente Educacional Inteligente

Este é um projeto de chatbot educacional inteligente desenvolvido com Flask, integrando múltiplas tecnologias de IA para fornecer assistência personalizada em contextos educacionais.

## 🚀 Funcionalidades

- **Assistente Educacional Inteligente**: Múltiplos modelos de IA (Gemini online, Ollama local)
- **Modelos Dinâmicos**: Descobre automaticamente todos os modelos disponíveis
- **Ollama Configurável**: Cada utilizador pode configurar sua própria URL Ollama local
- **Contextos Especializados**: Programação, Matemática e Tradução(línguas locais)
- **Processamento de Imagens**: Pix2Latex para fórmulas matemáticas + OCR
- **Sistema de Autenticação**: Login e registro de usuários com perfis personalizados
- **Interface Web Moderna**: Design responsivo e intuitivo
- **Upload de Imagens**: Suporte para análise de fórmulas e textos
- **Integração WhatsApp**: Suporte via Twilio
- **Base de Dados**: SQLite/PostgreSQL com SQLAlchemy

## 🛠️ Tecnologias Utilizadas

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **IA**: Google Gemini AI, Ollama
- **Processamento de Imagens**: Pix2Latex, Tesseract OCR
- **Frontend**: HTML5, CSS3, JavaScript
- **Base de Dados**: SQLite/PostgreSQL
- **Comunicação**: Twilio (WhatsApp)

## 📍 Pré-requisitos

- Python 3.8+
- SQLite (incluído) ou PostgreSQL
- Ollama (opcional - cada utilizador configura o seu)
- Tesseract OCR (para processamento de imagens)
- Google Gemini API Key (para modelos online)
- Conta Twilio (opcional - para integração WhatsApp)

## 🔧 Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/anselmonhamage/Project-ChatBot-IA.git
cd Project-ChatBot-IA
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Instale Tesseract OCR**
- **Windows**: Baixe de https://github.com/UB-Mannheim/tesseract/wiki
- **Linux**: `sudo apt-get install tesseract-ocr`
- **Mac**: `brew install tesseract`

5. **Configure as variáveis de ambiente**
```bash
cp env.example .env
# Edite o arquivo .env com suas configurações
```

6. **Configure o banco de dados**
```bash
flask db init
flask db migrate
flask db upgrade
```

7. **Execute a aplicação**
```bash
python run.py
```

A aplicação estará disponível em `http://localhost:8000`

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```env
# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_DEVELOPMENT_PORT=8000
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# Database Configuration (SQLite)
SQLALCHEMY_DATABASE_URI=sqlite:///chatbot.db

# AI Services Configuration (Online)
GEMINI_API_KEY=your-google-gemini-api-key

# Default Model (gemini para online)
DEFAULT_MODEL=gemini

# Ollama Configuration
# NOTA: Modelos locais Ollama são configurados por utilizador
# Cada utilizador pode definir sua própria URL local (ex: http://localhost:11434)
OLLAMA_TIMEOUT=60

# Upload Configuration
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# Twilio Configuration (WhatsApp Integration - Optional)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_WHATSAPP_NUMBER=your-twilio-whatsapp-number
MY_WHATSAPP_NUMBER=your-personal-whatsapp-number
```

## 🎯 Uso

### Interface Web
1. Acesse `http://localhost:8000`
2. Registre-se ou faça login
3. **(Opcional)** Configure URL Ollama local em **Secção do modelo**
4. Alterne entre modelos **Online** (Gemini) e **Local** (Ollama)
5. Faça perguntas ou envie imagens para análise

### Configurando Ollama Local
1. Instale Ollama: https://ollama.ai
2. Baixe modelos: `ollama pull llama3.1` ou `ollama pull qwen2.5`
3. No seu perfil, configure: `http://localhost:11434`
4. No chatbot, alterne para "Local" e selecione o modelo
5. Todos os seus modelos Ollama aparecerão automaticamente!

### Contextos Educacionais

#### 🔧 Programação
- Debug de código
- Explicação de algoritmos
- Boas práticas de desenvolvimento
- Conceitos de programação

#### 🧮 Matemática
- Resolução de problemas matemáticos
- Explicação de fórmulas
- Métodos de cálculo
- Análise de fórmulas em imagens

#### 🌐 Tradução
- Traduções entre idiomas
- Explicações gramaticais
- Vocabulário
- Compreensão de textos

### Upload de Imagens
- Clique no botão "+" para enviar imagens
- O sistema processará automaticamente:
  - Fórmulas matemáticas (LaTeX)
  - Texto (OCR)
  - Análise contextual

### 📱 Integração WhatsApp (via Twilio)

O StudentHub oferece integração completa com WhatsApp através do Twilio, permitindo que usuários conversem com o assistente educacional diretamente pelo WhatsApp.

#### Configuração WhatsApp

1. **Criar conta Twilio**
   - Acesse [Twilio Console](https://console.twilio.com/)
   - Ative o WhatsApp Sandbox para testes

2. **Configurar variáveis de ambiente**
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_WHATSAPP_NUMBER=+14155238886  # Número Twilio Sandbox
MY_WHATSAPP_NUMBER=+258841234567     # Seu número
```

3. **Configurar Webhook no Twilio**
   - No Console Twilio: **Messaging** > **Try it out** > **WhatsApp**
   - Configure "WHEN A MESSAGE COMES IN":
     - URL: `https://seu-dominio.com/whatsapp`
     - Method: `POST`

4. **Teste com ngrok (desenvolvimento local)**
```bash
# Terminal 1: Execute o app
python run.py

# Terminal 2: Exponha com ngrok
ngrok http 8000

# Configure webhook com URL ngrok
https://abc123.ngrok.io/whatsapp
```

#### Funcionalidades WhatsApp

✅ **Mesmas capacidades do chatbot web**
- Usa Gemini AI para respostas inteligentes
- Mantém contexto das últimas 5 mensagens
- Formatação otimizada para WhatsApp
- Histórico salvo no banco de dados

✅ **Formatação Automática**
- Converte Markdown para formato WhatsApp
- Remove HTML e tags complexas
- Limita respostas a 1500 caracteres
- Preserva listas, negrito e código

✅ **Exemplo de Conversa**
```
👤 Usuário: Como resolver x² - 5x + 6 = 0?

🤖 Bot:
Para resolver essa equação do segundo grau, use a fórmula de Bhaskara:

*Passo a passo:*
1. Identifique os coeficientes
   a = 1, b = -5, c = 6

2. Calcule o delta
   Δ = b² - 4ac = 1

3. Aplique a fórmula
   x = (5 ± 1) / 2

*Soluções:*
• x₁ = 3
• x₂ = 2
```

#### Recursos Técnicos

- **Session ID**: Cada número de telefone tem sessão única
- **Contexto**: Histórico mantido por número
- **Error Handling**: Mensagens de erro amigáveis
- **CSRF Exempt**: Webhook configurado para aceitar POST externo
- **Logs**: Sistema completo de logging

#### Limitações WhatsApp

- Respostas limitadas a 1500 caracteres
- Sem suporte a imagens no momento
- Requer HTTPS em produção (use ngrok para testes)
- Rate limits do Twilio aplicam-se

## 📁 Estrutura do Projeto

```
Project-ChatBot-IA/
├── app/
│   ├── __init__.py
│   ├── auth/                         # Decorators de autenticação
│   ├── controllers/
│   │   └── routes.py                 # Rotas principais da aplicação
│   ├── models/
│   │   ├── tables.py                 # Modelos SQLAlchemy (User, ChatHistory)
│   │   └── forms.py                  # Formulários Flask-WTF
│   ├── services/
│   │   ├── unified_chatbot.py        # Serviço unificado (Gemini + Ollama)
│   │   ├── twilio_service.py         # Integração WhatsApp
│   │   ├── whatsapp_formatter.py     # Formatação para WhatsApp
│   │   ├── pix2latex_service.py      # Processa imagens
│   │   └── chat_history_service.py   # Histórico de conversas
│   ├── static/
│   │   ├── css/                      # Estilos CSS
│   │   ├── js/                       # JavaScript (chatbot.js, edit_profile.js)
│   │   ├── images/                   # Imagens estáticas
│   │   └── uploads/                  # Uploads de usuários
│   └── templates/
│       ├── base.html                 # Template base
│       ├── chatbot.html              # Interface do chatbot
│       ├── edit.html                 # Edição de perfil
│       ├── login.html                # Login
│       ├── signup.html               # Registro
│       └── index.html                # Página inicial
├── migrations/                       # Migrações de banco de dados
├── instance/                         # Banco SQLite
├── config.py                         # Configurações Flask
├── run.py                            # Ponto de entrada
├── requirements.txt                  # Dependências Python
├── .env.example                      # Exemplo de configuração
└── README.md                
```


## 🔄 Funcionalidades do Chatbot

### Arquitetura Híbrida
- **Modelos Online** (providos pelo servidor):
  - Gemini 2.0 Flash (Google AI)
  - Requer apenas GEMINI_API_KEY no servidor

- **Modelos Locais** (configurados pelo utilizador):
  - Qualquer modelo Ollama disponível
  - Cada utilizador configura sua própria URL
  - Descoberta dinâmica de modelos
  - Privacidade total - roda na máquina do utilizador

### Fluxo de Processamento
1. Utilizador seleciona modelo (online ou local)
2. Sistema busca modelos disponíveis dinamicamente
3. Envia pergunta ou imagem com contexto educacional
4. Retorna resposta personalizada com formatação LaTeX
5. Histórico de conversa mantido por sessão

### Processamento de Imagens
- **Pix2Latex**: Extração de fórmulas matemáticas
- **Tesseract OCR**: Extração de texto de imagens
- **Crop e Ajuste**: Editor integrado de imagens
- **Múltiplos formatos**: JPG, PNG, PDF

## 🚀 Deploy

### Docker
```bash
docker build -t studenthub .
docker run -p 5000:5000 studenthub
```

### Produção
1. Configure um servidor web (Nginx/Apache)
2. Use um WSGI server (Gunicorn/uWSGI)
3. Configure SSL/HTTPS
4. Configure variáveis de ambiente de produção

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Suporte

Para suporte, entre em contato através de:
- Email: [nhamageanselmo@gmail.com]

## 🔮 Roadmap

- [x] Integração com múltiplos modelos de IA (Gemini, Ollama)
- [x] URL Ollama configurável por usuário
- [x] Descoberta dinâmica de modelos
- [x] Chat em tempo real com histórico
- [x] Processamento de imagens (Pix2Latex + OCR)
- [x] Sistema de autenticação e perfis
- [x] Integração WhatsApp via Twilio
- [ ] Suporte a múltiplos idiomas
- [ ] API REST completa
- [ ] Dashboard administrativo
- [ ] MCP (Model Context Protocol)
