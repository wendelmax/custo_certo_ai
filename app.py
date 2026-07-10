import os
import sys
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from crew import montar_equipe_analise
from tools import (
    calcular_margem_contribuicao,
    calcular_custeio_absorcao,
    analisar_desperdicios_eficiencia,
    calcular_ponto_equilibrio
)
from exportador import exportar_analise_excel
from converter_relatorio import converter_markdown_para_html_premium

load_dotenv()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204


@app.route('/analisar', methods=['POST'])
def analisar():
    try:
        custos_fixos = float(request.form.get('custos_fixos', 30000.00))
    except (ValueError, TypeError):
        return jsonify({'error': 'custos_fixos deve ser um número válido'}), 400

    file_fin = request.files.get('file_financeiro')
    file_op = request.files.get('file_operacional')

    if not file_fin or not file_op:
        return jsonify({'error': 'Arquivos obrigatórios ausentes'}), 400

    filename_fin = secure_filename(file_fin.filename)
    filename_op = secure_filename(file_op.filename)
    if not filename_fin:
        return jsonify({'error': 'Nome de arquivo financeiro inválido'}), 400
    if not filename_op:
        return jsonify({'error': 'Nome de arquivo operacional inválido'}), 400
    caminho_fin = os.path.join(app.config['UPLOAD_FOLDER'], filename_fin)
    caminho_op = os.path.join(app.config['UPLOAD_FOLDER'], filename_op)
    file_fin.save(caminho_fin)
    file_op.save(caminho_op)

    try:
        caminhos_opcionais = {}
        for key in ['bom', 'budget', 'observacoes']:
            f = request.files.get(key)
            if f and f.filename:
                path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename))
                f.save(path)
                caminhos_opcionais[key] = path

        equipe = montar_equipe_analise(caminho_fin, caminho_op, custos_fixos, caminhos_opcionais)
        resultado = equipe.kickoff()

        with open("relatorio_controladoria.md", "w", encoding="utf-8") as f:
            f.write(resultado)

        import pandas as pd
        margens_df = calcular_margem_contribuicao(caminho_fin)
        pe_dict = calcular_ponto_equilibrio(caminho_fin, custos_fixos)
        abs_vol = calcular_custeio_absorcao(caminho_fin, caminho_op, custos_fixos, "volume")
        abs_horas = calcular_custeio_absorcao(caminho_fin, caminho_op, custos_fixos, "horas_maquina")
        abs_custo_direto = calcular_custeio_absorcao(caminho_fin, caminho_op, custos_fixos, "custo_direto")
        desperdicios_df = analisar_desperdicios_eficiencia(caminho_op, caminho_fin)

        exportar_analise_excel(
            "analise_de_custos.xlsx",
            margens_df, abs_vol, abs_horas, abs_custo_direto, desperdicios_df,
            pe_dict, custos_fixos
        )

        converter_markdown_para_html_premium("relatorio_controladoria.md", "relatorio_controladoria.html")

        import markdown
        html_resultado = markdown.markdown(resultado, extensions=['tables'])

        top_produtos = margens_df.nlargest(5, 'margem_contribuição_total')[
            ['produto_id', 'margem_contribuição_total']
        ].to_dict(orient='records')

        custo_variavel_total = float(margens_df['custo_variavel_unitario'].sum())
        custo_refugo_total = float(desperdicios_df['custo_refugo'].sum()) if not desperdicios_df.empty else 0.0

        kpis = {
            'ponto_equilibrio': pe_dict.get('faturamento_equilibrio_geral', 0.0),
            'margem_media': float(margens_df['margem_contribuição_unitaria'].mean()),
            'custo_refugo': custo_refugo_total,
            'top_produtos': top_produtos,
            'custo_variavel_total': custo_variavel_total,
            'custos_fixos': custos_fixos
        }

        return jsonify({
            'success': True,
            'kpis': kpis,
            'relatorio_html': html_resultado
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<arquivo>')
def download(arquivo):
    if arquivo == 'excel':
        return send_from_directory('.', 'analise_de_custos.xlsx', as_attachment=True)
    elif arquivo == 'html':
        return send_from_directory('.', 'relatorio_controladoria.html')
    return jsonify({'error': 'Arquivo inválido'}), 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)
