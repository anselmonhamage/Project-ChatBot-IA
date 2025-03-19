import re

def format_text(text, option='html'):
    if option == 'html':
        text = format_html(text)
    elif option == 'plain':
        text = format_plain(text)
    else:
        raise ValueError("A opção deve ser 'html' ou 'plain'")
    return text

def format_html(text):
    code_blocks = {}
    text = preserve_code_blocks(text, code_blocks)
    text = apply_replacements(text)
    text = process_lists(text)
    text = restore_code_blocks(text, code_blocks)
    text = format_paragraphs(text)
    text = re.sub(r'\n{2,}', '\n', text)
    return text.strip()

def preserve_code_blocks(text, code_blocks):
    def preserve_code_block(match):
        placeholder = f"CODE_BLOCK_{len(code_blocks)}"
        code_blocks[placeholder] = match.group(0)
        return placeholder
    return re.sub(r'```(\w*)\n(.*?)```', lambda m: preserve_code_block(m), text, flags=re.DOTALL)

def apply_replacements(text):
    replacements = [
        (r'^# (.*?)$', r'<h1>\1</h1>', re.MULTILINE),
        (r'^## (.*?)$', r'<h2>\1</h2>', re.MULTILINE),
        (r'^### (.*?)$', r'<h3>\1</h3>', re.MULTILINE),
        (r'\*\*(.*?)\*\*', r'<strong>\1</strong>', 0),
        (r'\*(.*?)\*', r'<em>\1</em>', 0),
        (r'`(.*?)`', r'<code>\1</code>', 0),
        (r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', 0),
        (r'!\[([^\]]*)\]\(([^\)]+)\)', r'<img src="\2" alt="\1">', 0),
        (r'^> (.*?)$', r'<blockquote>\1</blockquote>', re.MULTILINE),
    ]
    for pattern, replacement, flags in replacements:
        text = re.sub(pattern, replacement, text, flags=flags)
    return text

def process_lists(text):
    list_blocks = re.findall(r'(^- [^\n]*\n|^\d+\. [^\n]*\n)+', text, re.MULTILINE)
    for block in list_blocks:
        if re.match(r'^\d+\.', block.strip()):
            items = re.findall(r'^\d+\. (.*?)$', block, re.MULTILINE)
            list_html = '<ol>\n' + '\n'.join(f'<li>{item}</li>' for item in items) + '\n</ol>'
        else:
            items = re.findall(r'^- (.*?)$', block, re.MULTILINE)
            list_html = '<ul>\n' + '\n'.join(f'<li>{item}</li>' for item in items) + '\n</ul>'
        text = text.replace(block, list_html + '\n')
    return text

def restore_code_blocks(text, code_blocks):
    for placeholder, code_block in code_blocks.items():
        language = re.search(r'```(\w*)\n', code_block)
        language = language.group(1) if language else ''
        code = re.search(r'```\w*\n(.*?)```', code_block, flags=re.DOTALL)
        code = code.group(1) if code else ''
        formatted_code = f'<pre><code class="language-{language}">{code}</code></pre>'
        text = text.replace(placeholder, formatted_code)
    return text

def format_paragraphs(text):
    
    def process_paragraph_content(content):
        # Verifica se o conteúdo contém itens de lista
        if re.search(r'^\* .+$', content, re.MULTILINE):
            items = re.findall(r'^\* (.+?)$', content, re.MULTILINE)
            return '<ul>\n' + '\n'.join(f'<li>{item.strip()}</li>' for item in items) + '\n</ul>'
        return '<p>' + content + '</p>'

    lines = text.split('\n')
    formatted_lines = []
    paragraph = []
    
    for line in lines:
        if not re.match(r'^\s*$', line) and not re.match(r'^<(h[1-6]|ul|ol|blockquote|pre)', line):
            paragraph.append(line)
        else:
            if paragraph:
                content = '\n'.join(paragraph)
                formatted_lines.append(process_paragraph_content(content))
                paragraph = []
            formatted_lines.append(line)
    
    if paragraph:
        content = '\n'.join(paragraph)
        formatted_lines.append(process_paragraph_content(content))
    
    return '\n'.join(formatted_lines)

def format_plain(text):
    
    def format_list_item(text):
        text = re.sub(r'\*\*(.*?)\*\*:', r'*\1*:', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', text)
        
        if ':' in text:
            title, content = text.split(': ', 1)
            return f"{title}: {content.strip()}"
        return text

    code_blocks = {}
    def preserve_code(match):
        placeholder = f"CODE_{len(code_blocks)}"
        code_blocks[placeholder] = match.group(2)
        return placeholder
    
    text = re.sub(r'```(\w*)\n(.*?)```', preserve_code, text, flags=re.DOTALL)
    
    replacements = [
        (r'^([^•\n].*?)(?=\n•|\Z)', r'\1\n', re.MULTILINE),
        
        (r'^-\s*(.*?)$', r'• \1\n', re.MULTILINE),
        (r'^\*\s*(.*?)$', r'• \1\n', re.MULTILINE),
        (r'^\d+\.\s*(.*?)$', r'• \1\n', re.MULTILINE),
    ]
    
    for pattern, replacement, flags in replacements:
        text = re.sub(pattern, replacement, text, flags=flags)
    
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        if line.strip():
            if line.startswith('• '):
                line = format_list_item(line.strip())
                formatted_lines.extend([line, ''])
            else:
                formatted_lines.append(line)
    
    text = '\n'.join(formatted_lines)
    
    text = re.sub(r'\*\*(.*?)\*\*', r'*\1*', text)
    text = re.sub(r'\s+\*', '*', text)
    text = re.sub(r'\*\s+', '*', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()
