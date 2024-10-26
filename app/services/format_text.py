import re


def format_text(texto, option='html'):
    
    if option == 'html':
        # Substitui os asteriscos por tags <strong> para o HTML
        formatted_text = re.sub(r'\*([^\*]+)\*', r'<strong>\1</strong>', texto)
    elif option == 'plain':
        # Remove os asteriscos para o texto plano
        formatted_text = texto.replace('*', '')
    else:
        raise ValueError("A opção deve ser 'html' ou 'plain'")
    
    return formatted_text
