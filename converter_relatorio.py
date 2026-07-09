import markdown
import os

def converter_markdown_para_html_premium(caminho_md: str, caminho_html: str) -> None:
    if not os.path.exists(caminho_md):
        raise FileNotFoundError(f"Arquivo markdown nao encontrado: {caminho_md}")
        
    with open(caminho_md, "r", encoding="utf-8") as f:
        text_md = f.read()
        
    body_html = markdown.markdown(text_md, extensions=['tables'])
    
    html_completo = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Controladoria Industrial</title>
    <style>
        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            color: #333333;
            line-height: 1.6;
            background-color: #F8F9FA;
            margin: 0;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 900px;
            background-color: #FFFFFF;
            padding: 40px;
            margin: 0 auto;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            border-top: 6px solid #1F497D;
        }}
        h1 {{
            color: #1F497D;
            border-bottom: 2px solid #E9ECEF;
            padding-bottom: 10px;
            font-size: 28px;
            margin-top: 0;
        }}
        h2 {{
            color: #2C3E50;
            margin-top: 30px;
            border-bottom: 1px solid #E9ECEF;
            padding-bottom: 6px;
            font-size: 22px;
        }}
        h3 {{
            color: #34495E;
            font-size: 18px;
        }}
        p, li {{
            font-size: 15px;
            color: #555555;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }}
        th {{
            background-color: #1F497D;
            color: #FFFFFF;
            font-weight: bold;
            padding: 10px;
            text-align: left;
            border: 1px solid #D3D3D3;
        }}
        td {{
            padding: 8px 10px;
            border: 1px solid #E9ECEF;
        }}
        tr:nth-child(even) {{
            background-color: #F8F9FA;
        }}
        .warning, blockquote {{
            background-color: #FFF3CD;
            border-left: 5px solid #FFC107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .warning p, blockquote p {{
            margin: 0;
            color: #856404;
            font-weight: 500;
        }}
        .footer {{
            margin-top: 40px;
            font-size: 12px;
            color: #999999;
            text-align: center;
            border-top: 1px solid #E9ECEF;
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        {body_html}
        <div class="footer">
            Relatório gerado automaticamente pelo Agente Especialista Custo Certo.
        </div>
    </div>
</body>
</html>
"""
    with open(caminho_html, "w", encoding="utf-8") as f:
        f.write(html_completo)
