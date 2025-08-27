import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("OLLAMA_DEFAULT_MODEL", "gemma2:2b")
REQUEST_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "60"))

def list_models():
    """Lista todos os modelos disponíveis no Ollama"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags")
        if response.status_code == 200:
            return response.json().get('models', [])
        return []
    except requests.exceptions.RequestException as e:
        print(f"Erro ao listar modelos: {e}")
        return []

def pull_model(model_name):
    """Baixa um modelo se não estiver disponível"""
    try:
        data = {"name": model_name}
        response = requests.post(f"{OLLAMA_BASE_URL}/api/pull", json=data, stream=True)
        
        for line in response.iter_lines():
            if line:
                status = json.loads(line.decode('utf-8'))
                if status.get('status') == 'success':
                    return True
        return False
    except Exception as e:
        print(f"Erro ao baixar modelo: {e}")
        return False

def generate_response(prompt, model_name=None, system_message=None, temperature=0.7):
    """
    Gera uma resposta usando o Ollama
    
    Args:
        prompt (str): Pergunta/prompt do utilizador
        model_name (str): Nome do modelo (usa DEFAULT_MODEL se None)
        system_message (str): Mensagem de sistema
        temperature (float): Criatividade da resposta (0.0 a 1.0)
    
    Returns:
        str: Resposta gerada pelo modelo ou None em caso de erro
    """
    if model_name is None:
        model_name = DEFAULT_MODEL
    
    try:
        data = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
                "top_k": 40
            }
        }
        
        if system_message:
            data["system"] = system_message
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate", 
            json=data, 
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', '').strip()
        else:
            print(f"Erro na API: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("Timeout na requisição para o Ollama")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return None

def ensure_model_available(model_name):
    """Garante que o modelo está disponível, baixando se necessário"""
    available_models = list_models()
    model_names = [model.get('name', '') for model in available_models]
    
    if not any(model_name in name for name in model_names):
        print(f"Modelo {model_name} não encontrado. Tentando baixar...")
        if pull_model(model_name):
            print(f"Modelo {model_name} baixado com sucesso!")
            return True
        else:
            print(f"Falha ao baixar modelo {model_name}")
            return False
    return True

def get_chatbot_response(user_message):
    """
    Função principal para obter resposta do chatbot
    
    Args:
        user_message (str): Mensagem do utilizador
    
    Returns:
        str: Resposta do chatbot ou mensagem de erro
    """
    if not ensure_model_available(DEFAULT_MODEL):
        fallback_models = [
            "gemma2:2b",
            "qwen2-math:1.5b"
        ]   
        model_to_use = None
        
        for model in fallback_models:
            if ensure_model_available(model):
                model_to_use = model
                break
        
        if not model_to_use:
            return "Desculpe, nenhum modelo está disponível no momento."
    else:
        model_to_use = DEFAULT_MODEL
    
    system_message = """Você é um assistente útil e gentil, suas respostas são rápidas, resumidas e sempre em português. Responda às perguntas de forma precisa e clara."""
    
    
    prompt = f"Pergunta: {user_message}"
    
    response = generate_response(
        prompt=prompt,
        model_name=model_to_use,
        system_message=system_message,
        temperature=0.7
    )
    
    if response:
        return response
    else:
        return "Desculpe, ocorreu um erro ao processar sua solicitação."

def check_ollama_status():
    """Verifica se o Ollama está rodando"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False