"""
Serviço unificado de chatbot que suporta múltiplos modelos
(Gemini online, Ollama local configurável pelo utilizador)
"""
import os
import requests
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Dict, Any

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "gemini")
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "60"))

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class UnifiedChatbot:
    """Classe para gerenciar múltiplos modelos de chatbot"""
    
    def __init__(self, model_type: str = None, ollama_url: str = None):
        """
        Inicializa o chatbot
        
        Args:
            model_type: Tipo do modelo (gemini ou ollama_{model_name})
            ollama_url: URL do servidor Ollama (se None, não usa modelos locais)
        """
        self.model_type = model_type or DEFAULT_MODEL
        self.ollama_url = ollama_url
        self.gemini_model = None
        
        if self.model_type == "gemini" and GEMINI_API_KEY:
            self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")
    
    def get_available_models(self) -> Dict[str, Any]:
        """Retorna modelos disponíveis dinamicamente"""
        models = {}
        
        if GEMINI_API_KEY:
            models["gemini"] = {
                "name": "Gemini 2.0 Flash",
                "type": "online",
                "description": "Modelo online do Google AI"
            }
        
        if self.ollama_url and self._check_ollama_status():
            ollama_models = self._list_ollama_models()
            
            for ollama_model in ollama_models:
                model_name = ollama_model.get("name", "")
                if not model_name:
                    continue
                
                if "embed" in model_name.lower():
                    continue
                
                model_base = model_name.split(':')[0]
                model_key = f"ollama_{model_base.replace('-', '_').replace('.', '_')}"
                
                display_name = model_base.replace('-', ' ').replace('_', ' ').title()
                if ':' in model_name:
                    version = model_name.split(':')[1]
                    display_name = f"{display_name} ({version})"
                
                models[model_key] = {
                    "name": display_name,
                    "type": "local",
                    "ollama_name": model_name,
                    "description": f"Modelo local: {model_name}"
                }
        
        return models
    
    def _check_ollama_status(self) -> bool:
        """Verifica se Ollama está rodando na URL configurada"""
        if not self.ollama_url:
            return False
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _list_ollama_models(self) -> list:
        """Lista modelos Ollama disponíveis"""
        if not self.ollama_url:
            return []
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return response.json().get('models', [])
        except:
            pass
        return []
    
    def _generate_with_gemini(self, message: str, context: str = "") -> str:
        """Gera resposta com Gemini"""
        try:
            system_prompt = """Você é StudentHub, um assistente educacional inteligente.
            Suas características:
            - Responde sempre em português
            - É claro, preciso e educativo
            - Usa exemplos práticos
            - Formata respostas matemáticas em LaTeX quando apropriado
            
            REGRAS DE FORMATAÇÃO LATEX (IMPORTANTE):
            - Para expressões matemáticas INLINE use: \\(expressão\\) ou $expressão$
            - Para equações EM BLOCO use: \\[equação\\] ou $$equação$$
            - Exemplo inline: A solução é \\(x = 1\\)
            - Exemplo bloco: 
              \\[
              2x - 2 = 0
              \\]
            
            Você pode usar qualquer um desses formatos, ambos funcionam perfeitamente!
            """
            
            full_prompt = f"{system_prompt}\n\n"
            if context:
                full_prompt += f"Contexto: {context}\n\n"
            full_prompt += f"Pergunta do estudante: {message}"
            
            chat = self.gemini_model.start_chat(history=[])
            response = chat.send_message(full_prompt)
            
            return response.text if response else "Desculpe, não consegui processar sua solicitação."
            
        except Exception as e:
            print(f"Erro ao gerar resposta com Gemini: {e}")
            return "Desculpe, ocorreu um erro ao processar sua solicitação."
    
    def _generate_with_ollama(self, message: str, model_name: str, context: str = "") -> str:
        """Gera resposta com Ollama"""
        if not self.ollama_url:
            return None
            
        try:
            system_message = """Você é StudentHub, um assistente educacional inteligente.
            Suas características:
            - Responde sempre em português
            - É claro, preciso e educativo
            - Usa exemplos práticos
            - Formata respostas matemáticas em LaTeX quando apropriado
            
            REGRAS DE FORMATAÇÃO LATEX (IMPORTANTE):
            - Para expressões matemáticas INLINE use: \\(expressão\\) ou $expressão$
            - Para equações EM BLOCO use: \\[equação\\] ou $$equação$$
            - Exemplo inline: A solução é \\(x = 1\\)
            - Exemplo bloco: 
              \\[
              2x - 2 = 0
              \\]
            
            Você pode usar qualquer um desses formatos, ambos funcionam perfeitamente!
            """
            
            prompt = message
            if context:
                prompt = f"Contexto: {context}\n\nPergunta: {message}"
            
            data = {
                "model": model_name,
                "prompt": prompt,
                "system": system_message,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=data,
                timeout=OLLAMA_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                print(f"Erro na API Ollama: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("Timeout na requisição Ollama")
            return None
        except Exception as e:
            print(f"Erro ao gerar resposta com Ollama: {e}")
            return None
    
    def generate_response(self, message: str, context: str = "") -> Dict[str, Any]:
        """
        Gera resposta usando o modelo configurado (busca dinâmica)
        
        Args:
            message: Mensagem do usuário
            context: Contexto adicional
        
        Returns:
            Dict com response e metadata
        """
        if not message.strip():
            return {
                "success": False,
                "error": "Mensagem vazia",
                "response": None
            }
        
        available = self.get_available_models()
        model_config = available.get(self.model_type)
        
        if not model_config:
            return {
                "success": False,
                "error": f"Modelo '{self.model_type}' não encontrado ou indisponível",
                "response": None
            }
        
        try:
            if self.model_type == "gemini":
                response = self._generate_with_gemini(message, context)
                return {
                    "success": True,
                    "response": response,
                    "model": model_config["name"],
                    "type": "online"
                }
            
            elif model_config["type"] == "local":
                ollama_name = model_config.get("ollama_name")
                
                if not ollama_name:
                    return {
                        "success": False,
                        "error": "Nome do modelo Ollama não especificado",
                        "response": None
                    }
                
                response = self._generate_with_ollama(
                    message, 
                    ollama_name, 
                    context
                )
                
                if response:
                    return {
                        "success": True,
                        "response": response,
                        "model": model_config["name"],
                        "type": "local"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Falha ao gerar resposta com modelo {ollama_name}",
                        "response": None
                    }
            else:
                return {
                    "success": False,
                    "error": f"Tipo de modelo desconhecido: {model_config.get('type')}",
                    "response": None
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": None
            }


def get_chatbot(model_type: str = None, ollama_url: str = None) -> UnifiedChatbot:
    """Retorna instância do chatbot"""
    return UnifiedChatbot(model_type, ollama_url)

def get_available_models(ollama_url: str = None) -> Dict[str, Any]:
    """Retorna modelos disponíveis"""
    bot = UnifiedChatbot(ollama_url=ollama_url)
    return bot.get_available_models()

def generate_response(message: str, model_type: str = None, ollama_url: str = None, context: str = "") -> Dict[str, Any]:
    """
    Gera resposta de forma simplificada
    
    Args:
        message: Mensagem do usuário
        model_type: Tipo do modelo a usar
        ollama_url: URL do servidor Ollama (para modelos locais)
        context: Contexto adicional
    
    Returns:
        Dict com response e metadata
    """
    try:
        bot = UnifiedChatbot(model_type, ollama_url)
        result = bot.generate_response(message, context)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro ao processar: {str(e)}",
            "response": None,
            "model": model_type or "unknown",
            "type": "error"
        }
