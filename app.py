from flask import Flask, render_template, request
from fpdf import FPDF
import os
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage

PASTA_RAIZ = "D:\\HD_Loja\\Vendas\\"
EMAIL_REMETENTE = "plhosting5@gmail.com"
SENHA_EMAIL = "lqsq wdji rgys hzhv"

app = Flask(__name__)

# Função para gerar PDF
def gerar_fatura(cliente_nome, cliente_email, produtos, valor_total, pasta_cliente):
    data_emissao = datetime.now().strftime("%d/%m/%Y")
    vencimento = "05/05/2025"
    id_fatura = datetime.now().strftime("%Y%m%d%H%M%S")
    nome_arquivo = f"Fatura_{id_fatura}.pdf"
    caminho_arquivo = os.path.join(pasta_cliente, nome_arquivo)
    if not os.path.exists(pasta_cliente):
        os.makedirs(pasta_cliente)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Fatura - PL HOSTING", ln=True, align="C")
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 128, 0)
    pdf.cell(0, 10, "PAGO", ln=True, align="R")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Fatura #{id_fatura}", ln=True)
    pdf.cell(0, 10, f"Data da Fatura: {data_emissao}", ln=True)
    pdf.cell(0, 10, f"Vencimento: {vencimento}", ln=True)
    pdf.cell(0, 10, f"Cliente: {cliente_nome}", ln=True)
    pdf.cell(0, 10, f"E-mail: {cliente_email}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(95, 10, "Descrição", border=1)
    pdf.cell(95, 10, "Total", border=1, ln=True)
    pdf.set_font("Arial", '', 12)
    for produto, valor in produtos:
        pdf.cell(95, 10, produto, border=1)
        pdf.cell(95, 10, valor, border=1, ln=True)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(95, 10, "Total:", border=1)
    pdf.cell(95, 10, valor_total, border=1, ln=True)
    pdf.output(caminho_arquivo)
    return caminho_arquivo

# Função para enviar email
def enviar_email(cliente_email, cliente_nome, pdf_caminho, usuario, senha, plano, valor_inicial, valor_mensal, proximo_vencimento):
    msg = MIMEMultipart('related')
    msg['Subject'] = "Confirmação de Pagamento - PL HOSTING"
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = cliente_email
    msg_alternativo = MIMEMultipart('alternative')
    msg.attach(msg_alternativo)
    html = f"""
    <html><body>
    <p>Prezado(a) <strong>{cliente_nome}</strong>,</p>
    <p>Obrigado por sua compra! Sua conta foi configurada.</p>
    <ul>
    <li><strong>Plano:</strong> {plano}</li>
    <li><strong>Valor Inicial:</strong> {valor_inicial}</li>
    <li><strong>Valor Mensal:</strong> {valor_mensal}</li>
    <li><strong>Próximo Vencimento:</strong> {proximo_vencimento}</li>
    <li><strong>Usuário:</strong> {usuario}</li>
    <li><strong>Senha:</strong> {senha}</li>
    </ul>
    </body></html>
    """
    msg_alternativo.attach(MIMEText(html, 'html'))
    with open(pdf_caminho, "rb") as f:
        parte_pdf = MIMEApplication(f.read(), _subtype="pdf")
        parte_pdf.add_header("Content-Disposition", "attachment", filename=os.path.basename(pdf_caminho))
        msg.attach(parte_pdf)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_REMETENTE, SENHA_EMAIL)
        smtp.send_message(msg)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        cliente_nome = request.form["cliente_nome"]
        cliente_email = request.form["cliente_email"]
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        plano = request.form["plano"]
        valor_inicial = request.form["valor_inicial"]
        valor_mensal = request.form["valor_mensal"]
        proximo_vencimento = request.form["proximo_vencimento"]
        produtos = [(f"{plano} ({datetime.now().strftime('%d/%m/%Y')} - {proximo_vencimento})", valor_mensal)]
        valor_total = valor_mensal
        pasta_cliente = os.path.join(PASTA_RAIZ, cliente_nome.replace(" ", "_"))
        pdf_caminho = gerar_fatura(cliente_nome, cliente_email, produtos, valor_total, pasta_cliente)
        enviar_email(cliente_email, cliente_nome, pdf_caminho, usuario, senha, plano, valor_inicial, valor_mensal, proximo_vencimento)
        return render_template("index.html", sucesso=True, email=cliente_email)
    return render_template("index.html", sucesso=False)

if __name__ == "__main__":
    app.run(debug=True)
