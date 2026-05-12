with open('build_90_page_pdf.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = content.replace('—', '-').replace('’', "'").replace('“', '"').replace('”', '"')
with open('build_90_page_pdf.py', 'w', encoding='utf-8') as f:
    f.write(content)
