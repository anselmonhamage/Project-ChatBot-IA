import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")

def get_chatbot_response(user_message):
    """
    Função principal para obter resposta do chatbot usando Google Gemini
    
    Args:
        user_message (str): Mensagem do utilizador
    
    Returns:
        str: Resposta do chatbot ou mensagem de erro
    """
    try:
        system_message = """Você é um assistente útil e gentil, suas respostas são rápidas, 
        resumidas e sempre em português. Responda às perguntas de forma precisa e clara."""
        
        chat = model.start_chat(history=[])
        response = chat.send_message(
            f"{system_message}\n\nPergunta: {user_message}"
        )
        
        if response:
            return response.text
        else:
            return "Desculpe, não consegui processar sua solicitação."
    except Exception as e:
        return "Desculpe, ocorreu um erro ao processar sua solicitação."

def check_gemini_status():
    """Verifica se a API do Gemini está funcionando"""
    try:
        response = model.generate_content("Teste de conexão com gemini")
        return True
    except Exception as e:
        return False