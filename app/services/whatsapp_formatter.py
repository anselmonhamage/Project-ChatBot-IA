"""
Formatador de texto específico para WhatsApp
Converte respostas do AI para formato amigável no WhatsApp
"""

import re


def format_for_whatsapp(text: str, max_length: int = 1500) -> str:
    """
    Formata texto para WhatsApp com as seguintes regras:
    - Remove Markdown complexo
    - Converte formatação para WhatsApp nativo
    - Limita tamanho
    - Melhora legibilidade
    
    Args:
        text: Texto original do AI
        max_length: Tamanho máximo da mensagem
        
    Returns:
        Texto formatado para WhatsApp
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Converte negrito Markdown para WhatsApp (*texto*)
    text = re.sub(r'\*\*([^*]+)\*\*', r'*\1*', text)
    
    # Converte itálico Markdown para WhatsApp (_texto_)
    text = re.sub(r'\_\_([^_]+)\_\_', r'_\1_', text)
    text = re.sub(r'\*([^*]+)\*', r'_\1_', text)
    
    # Converte código inline
    text = re.sub(r'`([^`]+)`', r'"\1"', text)
    
    # Remove blocos de código mantendo conteúdo
    text = re.sub(r'```[\w]*\n?(.*?)```', r'\1', text, flags=re.DOTALL)
    
    # Converte listas numeradas
    text = re.sub(r'^\d+\.\s', '• ', text, flags=re.MULTILINE)
    
    # Converte listas com traço
    text = re.sub(r'^[-*]\s', '• ', text, flags=re.MULTILINE)
    
    # Remove links Markdown [texto](url) mas mantém o texto
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove múltiplas linhas em branco
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove espaços no início/fim de linhas
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Limita tamanho
    if len(text) > max_length:
        # Tenta cortar em uma frase completa
        cutoff = text.rfind('.', 0, max_length - 3)
        if cutoff > max_length * 0.8:  # Pelo menos 80% do texto
            text = text[:cutoff + 1]
        else:
            # Corta no espaço mais próximo
            cutoff = text.rfind(' ', 0, max_length - 3)
            text = text[:cutoff] + "..."
    
    # Remove espaços extras
    text = text.strip()
    
    return text


def split_long_message(text: str, max_length: int = 1500) -> list:
    """
    Divide mensagem longa em múltiplas partes.
    Usado quando precisar enviar mensagens muito longas.
    
    Args:
        text: Texto completo
        max_length: Tamanho máximo por mensagem
        
    Returns:
        Lista de mensagens
    """
    if len(text) <= max_length:
        return [text]
    
    messages = []
    current = ""
    
    # Divide por parágrafos
    paragraphs = text.split('\n\n')
    
    for para in paragraphs:
        if len(current) + len(para) + 2 <= max_length:
            current += para + '\n\n'
        else:
            if current:
                messages.append(current.strip())
            current = para + '\n\n'
    
    if current:
        messages.append(current.strip())
    
    # Se ainda tiver partes muito longas, divide por frases
    final_messages = []
    for msg in messages:
        if len(msg) <= max_length:
            final_messages.append(msg)
        else:
            # Divide por frases
            sentences = re.split(r'(?<=[.!?])\s+', msg)
            part = ""
            for sentence in sentences:
                if len(part) + len(sentence) + 1 <= max_length:
                    part += sentence + ' '
                else:
                    if part:
                        final_messages.append(part.strip())
                    part = sentence + ' '
            if part:
                final_messages.append(part.strip())
    
    # Adiciona numeração se houver múltiplas partes
    if len(final_messages) > 1:
        numbered = []
        for i, msg in enumerate(final_messages, 1):
            numbered.append(f"*[Parte {i}/{len(final_messages)}]*\n\n{msg}")
        return numbered
    
    return final_messages


def create_whatsapp_menu(options: list) -> str:
    """
    Cria menu de opções formatado para WhatsApp
    
    Args:
        options: Lista de opções ['Opção 1', 'Opção 2']
        
    Returns:
        Menu formatado
    """
    menu = "*Escolha uma opção:*\n\n"
    for i, option in enumerate(options, 1):
        menu += f"{i}. {option}\n"
    menu += "\n_Digite o número da opção desejada_"
    return menu


def add_whatsapp_emojis(text: str, category: str = None) -> str:
    """
    Adiciona emojis contextuais ao texto
    
    Args:
        text: Texto original
        category: Categoria do conteúdo (math, programming, general)
        
    Returns:
        Texto com emojis
    """
    emoji_map = {
        'math': '📐',
        'programming': '💻',
        'science': '🔬',
        'language': '📚',
        'help': '❓',
        'success': '✅',
        'error': '❌',
        'info': 'ℹ️',
        'warning': '⚠️'
    }
    
    if category and category in emoji_map:
        emoji = emoji_map[category]
        return f"{emoji} {text}"
    
    return text


def format_code_for_whatsapp(code: str, language: str = None) -> str:
    """
    Formata código para WhatsApp
    
    Args:
        code: Código fonte
        language: Linguagem de programação
        
    Returns:
        Código formatado
    """
    header = f"*Código {language}:*\n" if language else "*Código:*\n"
    
    # WhatsApp usa fonte monoespaçada com ```
    formatted = f"{header}```\n{code}\n```"
    
    return formatted


def create_whatsapp_table(headers: list, rows: list) -> str:
    """
    Cria tabela ASCII simples para WhatsApp
    
    Args:
        headers: Lista de cabeçalhos
        rows: Lista de listas com dados
        
    Returns:
        Tabela formatada
    """
    # Calcula largura de cada coluna
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    
    # Cria tabela
    lines = []
    
    # Cabeçalho
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    lines.append(header_line)
    lines.append("-" * len(header_line))
    
    # Linhas
    for row in rows:
        row_line = " | ".join(str(cell).ljust(w) for cell, w in zip(row, widths))
        lines.append(row_line)
    
    return "```\n" + "\n".join(lines) + "\n```"
