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
    
    text = re.sub(r'^#{1,6}\s+(.+)$', r'\1', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'*\1*', text)
    text = re.sub(r'__(.+?)__', r'*\1*', text)

    text = re.sub(r'^\* (.+)$', r'• \1\n', text, flags=re.MULTILINE)
    text = re.sub(r'^- (.+)$', r'• \1\n', text, flags=re.MULTILINE)
    text = re.sub(r'^ {2}\* (.+)$', r'  • \1\n', text, flags=re.MULTILINE)
    text = re.sub(r'^ {2}- (.+)$', r'  • \1\n', text, flags=re.MULTILINE)

    text = re.sub(r'^(\d+)\. (.+)$', r'\1. \2\n', text, flags=re.MULTILINE)

    code_blocks = []

    def extract_code_blocks(match):
        content = match.group(2)
        lines = content.split('\n')

        if len(lines) > 0 and not lines[0].startswith('    ') and re.match(r'^[a-zA-Z0-9_\-+.]+$', lines[0]):
            lines = lines[1:]

        index = len(code_blocks)
        code_blocks.append('\n'.join(lines))

        return f"_CODE_BLOCK{index}"

    text = re.sub(r'(`{3,})(.+?)\1', extract_code_blocks, text, flags=re.DOTALL)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'\1: \2', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)

    for i, block in enumerate(code_blocks):
        text = text.replace(f"_CODE_BLOCK{i}", f"\n{block.strip()}\n")

    text = re.sub(r'(\n• .+?)(?=(\n• )|(\n\d+\. )|(\n$))', r'\1\n', text, flags=re.MULTILINE)
    text = re.sub(r'(\n\d+\. .+?)(?=(\n• )|(\n\d+\. )|(\n$))', r'\1\n', text, flags=re.MULTILINE)

    return text.strip()
