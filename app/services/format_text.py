import re


def format_text(texto, option='html'):
    
    if option == 'html':
        formatted_text = re.sub(r'\*([^\*]+)\*', r'<strong>\1</strong>', texto)
    elif option == 'plain':
        formatted_text = texto.replace('*', '')
    else:
        raise ValueError("A opção deve ser 'html' ou 'plain'")
    
    return formatted_text
