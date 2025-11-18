#!/usr/bin/env python3
"""
Script to generate several investment portfolio PDFs with varied assets
"""

import random
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfgen import canvas

# Sample data for variations
FIRST_NAMES = [
    "BURIDAN", "JOÃO", "MARIA", "PEDRO", "ANA", "CARLOS", "JULIANA", 
    "FERNANDO", "PATRICIA", "ROBERTO", "LUCIA", "MARCOS", "BEATRIZ",
    "RAFAEL", "CAMILA", "GUSTAVO", "AMANDA", "RICARDO", "FERNANDA", "DIEGO",
    "MARIANA", "THIAGO", "GABRIELA", "BRUNO", "LARISSA", "FELIPE", "NATALIA",
    "DANIEL", "VANESSA", "LEONARDO", "CAROLINA", "ANDRE", "JESSICA", "PAULO",
    "RENATA", "EDUARDO", "BIANCA", "LUCAS", "ALINE", "SERGIO", "PRISCILA",
    "RODRIGO", "SIMONE", "MARCELO", "CRISTINA", "FABIO", "ADRIANA", "VITOR",
    "DENISE", "ALEXANDRE", "TATIANA"
]

MIDDLE_NAMES = [
    "GENEROSO", "SILVA", "SANTOS", "OLIVEIRA", "SOUZA", "COSTA", "FERREIRA",
    "RODRIGUES", "ALMEIDA", "NASCIMENTO", "CARVALHO", "PEREIRA", "RIBEIRO",
    "MARTINS", "ARAUJO", "ROCHA", "DIAS", "TEIXEIRA", "GOMES", "BARBOSA"
]

LAST_NAMES = [
    "LIMA", "DOS SANTOS", "DE OLIVEIRA", "DA SILVA", "DE SOUZA",
    "DA COSTA", "DE ALMEIDA", "DO NASCIMENTO", "DE CARVALHO", "PEREIRA",
    "MARTINS", "RIBEIRO", "GOMES", "FERNANDES", "ROCHA", "CARDOSO",
    "MENDES", "MOREIRA", "NUNES", "BARROS"
]

# Asset pools
BDR_ASSETS = [
    ("BIXN39", "ISHARES GLOBAL TECH ETF", "ETF"),
    ("AAPL34", "APPLE INC", "BDR"),
    ("MSFT34", "MICROSOFT CORPORATION", "BDR"),
    ("GOGL34", "ALPHABET INC CLASS A", "BDR"),
    ("AMZO34", "AMAZON.COM INC", "BDR"),
    ("TSLA34", "TESLA INC", "BDR"),
    ("META34", "META PLATFORMS INC", "BDR"),
    ("NVDC34", "NVIDIA CORPORATION", "BDR"),
]

DEBENTURES = [
    ("DEB - USINA TERMELETRICA PAMPA SUL S.A.", "2036-10-15"),
    ("DEB - ENERGISA S.A.", "2035-07-20"),
    ("DEB - LIGHT S.A.", "2037-03-15"),
    ("DEB - CEMIG DISTRIBUIÇÃO S.A.", "2034-11-10"),
    ("DEB - CELESC DISTRIBUIÇÃO S.A.", "2036-06-25"),
    ("DEB - COPEL DISTRIBUIÇÃO S.A.", "2035-09-18"),
]

ETF_ASSETS = [
    ("NASD11", "TREND ETF NASDAQ 100 FDO. ÍNDICE. INV. EXT. - IE", "Internacional"),
    ("TECK11", "IT NOW NYSE FANG+TM FUNDO DE ÍNDICE", "Internacional"),
    ("IVVB11", "ISHARES S&P 500 FUNDO DE ÍNDICE", "Internacional"),
    ("BOVA11", "ISHARES IBOVESPA FUNDO DE ÍNDICE", "Nacional"),
    ("SMAL11", "ISHARES SMALL CAP FUNDO DE ÍNDICE", "Nacional"),
    ("DIVO11", "ISHARES DIVIDENDOS FUNDO DE ÍNDICE", "Nacional"),
]

FII_ASSETS = [
    ("KNSC11", "KINEA SECURITIES FII RESP LIMITADA", "Cotas"),
    ("HGLG11", "CSHG LOGISTICA FII", "Cotas"),
    ("MXRF11", "MAXI RENDA FII", "Cotas"),
    ("XPML11", "XP MALLS FII", "Cotas"),
    ("VISC11", "VINCI SHOPPING CENTERS FII", "Cotas"),
    ("BTLG11", "BTG PACTUAL LOGÍSTICA FII", "Cotas"),
]

TESOURO_OPTIONS = [
    ("Tesouro IPCA+ 2026", "2026-08-15"),
    ("Tesouro IPCA+ 2029", "2029-05-15"),
    ("Tesouro IPCA+ 2035", "2035-05-15"),
    ("Tesouro IPCA+ com Juros Semestrais 2030", "2030-08-15"),
    ("Tesouro IPCA+ com Juros Semestrais 2032", "2032-08-15"),
    ("Tesouro Prefixado 2026", "2026-01-01"),
    ("Tesouro Prefixado 2029", "2029-01-01"),
    ("Tesouro Selic 2027", "2027-03-01"),
]

def generate_cpf():
    """Generate a random CPF number"""
    cpf = ''.join([str(random.randint(0, 9)) for _ in range(11)])
    return cpf

def generate_random_name():
    """Generate a random Brazilian name"""
    first = random.choice(FIRST_NAMES)
    middle = random.choice(MIDDLE_NAMES)
    last = random.choice(LAST_NAMES)
    return f"{first} {middle} {last}"

def format_currency(value):
    """Format value as Brazilian currency"""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def create_header_footer(canvas, doc):
    """Add header and footer to pages"""
    canvas.saveState()
    
    # Header with B3 logo placeholder
    canvas.setFont('Helvetica-Bold', 14)
    canvas.drawString(30*mm, 280*mm, "Extrato de Posição")
    canvas.drawRightString(180*mm, 280*mm, "[B]³")
    
    # Footer disclaimer
    canvas.setFont('Helvetica', 6)
    disclaimer = ("A valorização dos ativos tem fins meramente informacionais, representando uma estimativa, é calculada utilizando-se o preço de fechamento do último dia em que o ativo foi negociado ou o "
                  "último preço de referência divulgado pela B3 e Entidades de Mercado de Balcão Organizado, quando da data do saldo. O investidor não deve considerar essa estimativa como a real valorização "
                  "dos ativos. Dessa forma, a B3 está isenta de quaisquer responsabilidades relativas à real valorização dos ativos e por quaisquer ônus ou prejuízos que venham a ser suportados direta ou "
                  "indiretamente pelo investidor em decorrência dos valores ou preços por ela divulgados de acordo com os critérios utilizados, bem como a aceitação, pelo investidor, desta valorização estimada pela B3.")
    
    text = canvas.beginText(20*mm, 15*mm)
    text.setFont('Helvetica', 6)
    
    # Word wrap for disclaimer
    words = disclaimer.split()
    line = ""
    for word in words:
        if canvas.stringWidth(line + " " + word, 'Helvetica', 6) < 170*mm:
            line += " " + word if line else word
        else:
            text.textLine(line)
            line = word
    if line:
        text.textLine(line)
    
    canvas.drawText(text)
    
    # Footer link
    canvas.setFont('Helvetica-Bold', 7)
    canvas.drawString(20*mm, 10*mm, "acesse investidor.B3.com.br")
    
    # Page number
    canvas.drawRightString(180*mm, 10*mm, f"{doc.page}/2")
    
    canvas.restoreState()

def generate_portfolio_pdf(filename, person_name, cpf, portfolio_date):
    """Generate a single portfolio PDF"""
    
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=50*mm,
        bottomMargin=30*mm
    )
    
    # Container for elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading1'],
        fontSize=11,
        textColor=colors.HexColor('#003366'),
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=8,
        fontName='Helvetica'
    )
    
    # Person info
    elements.append(Paragraph(f"{person_name} | CPF/CNPJ: {cpf}", normal_style))
    elements.append(Spacer(1, 12))
    
    # Filters
    elements.append(Paragraph("<b>Filtros aplicados</b>", normal_style))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(f"<b>Data:</b> {portfolio_date}", normal_style))
    elements.append(Paragraph("<b>Tipo de Investimento:</b> Todos", normal_style))
    elements.append(Paragraph("<b>Instituição:</b> Todos", normal_style))
    elements.append(Paragraph("<b>Marcações:</b> Todos", normal_style))
    elements.append(Spacer(1, 20))
    
    # BDR Section
    num_bdr = random.randint(0, 3)
    if num_bdr > 0:
        elements.append(Paragraph("BDR - Brazilian Depositary Receipts", header_style))
        elements.append(Spacer(1, 6))
        
        bdr_data = [["Produto", "Tipo", "Instituição", "Quantidade", "Preço de\nfechamento", "Valor\nAtualizado"]]
        total_bdr = 0
        
        selected_bdrs = random.sample(BDR_ASSETS, num_bdr)
        for code, name, tipo in selected_bdrs:
            qty = random.randint(10, 200)
            price = random.uniform(10, 150)
            value = qty * price
            total_bdr += value
            
            bdr_data.append([
                f"{code} - {name}",
                tipo,
                "NU INVEST CORRETORA DE\nVALORES S.A.",
                str(qty),
                format_currency(price),
                format_currency(value)
            ])
        
        bdr_table = Table(bdr_data, colWidths=[65*mm, 20*mm, 40*mm, 20*mm, 22*mm, 22*mm])
        bdr_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),
            ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(bdr_table)
        elements.append(Spacer(1, 6))
        
        # Total
        total_table = Table([["", "", "", "", "Total", format_currency(total_bdr)]], 
                          colWidths=[65*mm, 20*mm, 40*mm, 20*mm, 22*mm, 22*mm])
        total_table.setStyle(TableStyle([
            ('ALIGN', (4, 0), (-1, 0), 'RIGHT'),
            ('FONTNAME', (4, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (4, 0), (-1, 0), 8),
        ]))
        elements.append(total_table)
        elements.append(Spacer(1, 20))
    
    # Debentures Section
    num_deb = random.randint(0, 2)
    if num_deb > 0:
        elements.append(Paragraph("DEB - Debêntures", header_style))
        elements.append(Spacer(1, 6))
        
        deb_data = [["Produto", "Instituição", "Vencimento", "Quantidade", "Preço unitário\natualizado", "Valor\natualizado"]]
        total_deb = 0
        
        selected_debs = random.sample(DEBENTURES, num_deb)
        for name, maturity in selected_debs:
            qty = random.randint(1, 5)
            price = random.uniform(1000, 2000)
            value = qty * price
            total_deb += value
            
            deb_data.append([
                name,
                "NU INVEST CORRETORA DE\nVALORES S.A.",
                maturity.replace("-", "/")[:7] + "/" + maturity[:4],
                str(qty),
                format_currency(price),
                format_currency(value)
            ])
        
        deb_table = Table(deb_data, colWidths=[55*mm, 40*mm, 22*mm, 20*mm, 25*mm, 25*mm])
        deb_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),
            ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(deb_table)
        elements.append(Spacer(1, 6))
        
        # Total
        total_table = Table([["", "", "", "", "Total", format_currency(total_deb)]], 
                          colWidths=[55*mm, 40*mm, 22*mm, 20*mm, 25*mm, 25*mm])
        total_table.setStyle(TableStyle([
            ('ALIGN', (4, 0), (-1, 0), 'RIGHT'),
            ('FONTNAME', (4, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (4, 0), (-1, 0), 8),
        ]))
        elements.append(total_table)
        elements.append(Spacer(1, 20))
    
    # ETF Section - Page 1
    num_etf = random.randint(1, 3)
    etf_page1 = min(num_etf, 1)
    
    if etf_page1 > 0:
        elements.append(Paragraph("ETF - Exchange Traded Fund", header_style))
        elements.append(Spacer(1, 6))
        
        etf_data = [["Produto", "Tipo", "Instituição", "Quantidade", "Preço de\nfechamento", "Valor\nAtualizado"]]
        total_etf_p1 = 0
        
        selected_etfs = random.sample(ETF_ASSETS, etf_page1)
        for code, name, tipo in selected_etfs:
            qty = random.randint(10, 150)
            price = random.uniform(10, 120)
            value = qty * price
            total_etf_p1 += value
            
            etf_data.append([
                f"{code} - {name}",
                tipo,
                "NU INVEST CORRETORA DE\nVALORES S.A.",
                str(qty),
                format_currency(price),
                format_currency(value)
            ])
        
        etf_table = Table(etf_data, colWidths=[65*mm, 25*mm, 40*mm, 20*mm, 22*mm, 22*mm])
        etf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),
            ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(etf_table)
    
    # Page break
    elements.append(PageBreak())
    
    # Page 2
    # ETF continuation if needed
    remaining_etf = num_etf - etf_page1
    if remaining_etf > 0:
        elements.append(Paragraph("ETF - Exchange Traded Fund", header_style))
        elements.append(Spacer(1, 6))
        
        etf_data2 = [["Produto", "Tipo", "Instituição", "Quantidade", "Preço de\nfechamento", "Valor\nAtualizado"]]
        total_etf_p2 = 0
        
        remaining_etfs = [e for e in ETF_ASSETS if e not in selected_etfs]
        selected_etfs2 = random.sample(remaining_etfs, min(remaining_etf, len(remaining_etfs)))
        
        for code, name, tipo in selected_etfs2:
            qty = random.randint(10, 150)
            price = random.uniform(10, 120)
            value = qty * price
            total_etf_p2 += value
            
            etf_data2.append([
                f"{code} - {name}",
                tipo,
                "NU INVEST CORRETORA DE\nVALORES S.A.",
                str(qty),
                format_currency(price),
                format_currency(value)
            ])
        
        etf_table2 = Table(etf_data2, colWidths=[65*mm, 25*mm, 40*mm, 20*mm, 22*mm, 22*mm])
        etf_table2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),
            ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(etf_table2)
        elements.append(Spacer(1, 6))
        
        # ETF Total
        total_etf = total_etf_p1 + total_etf_p2
        total_table = Table([["", "", "", "", "Total", format_currency(total_etf)]], 
                          colWidths=[65*mm, 25*mm, 40*mm, 20*mm, 22*mm, 22*mm])
        total_table.setStyle(TableStyle([
            ('ALIGN', (4, 0), (-1, 0), 'RIGHT'),
            ('FONTNAME', (4, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (4, 0), (-1, 0), 8),
        ]))
        elements.append(total_table)
        elements.append(Spacer(1, 20))
    
    # FII Section
    num_fii = random.randint(0, 2)
    if num_fii > 0:
        elements.append(Paragraph("FII - Fundo de Investimento Imobiliário", header_style))
        elements.append(Spacer(1, 6))
        
        fii_data = [["Produto", "Tipo", "Instituição", "Quantidade", "Preço de\nfechamento", "Valor\nAtualizado"]]
        total_fii = 0
        
        selected_fiis = random.sample(FII_ASSETS, num_fii)
        for code, name, tipo in selected_fiis:
            qty = random.randint(50, 200)
            price = random.uniform(5, 15)
            value = qty * price
            total_fii += value
            
            fii_data.append([
                f"{code} - {name}",
                tipo,
                "NU INVEST CORRETORA DE\nVALORES S.A.",
                str(qty),
                format_currency(price),
                format_currency(value)
            ])
        
        fii_table = Table(fii_data, colWidths=[65*mm, 20*mm, 40*mm, 20*mm, 22*mm, 22*mm])
        fii_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),
            ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(fii_table)
        elements.append(Spacer(1, 6))
        
        # Total
        total_table = Table([["", "", "", "", "Total", format_currency(total_fii)]], 
                          colWidths=[65*mm, 20*mm, 40*mm, 20*mm, 22*mm, 22*mm])
        total_table.setStyle(TableStyle([
            ('ALIGN', (4, 0), (-1, 0), 'RIGHT'),
            ('FONTNAME', (4, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (4, 0), (-1, 0), 8),
        ]))
        elements.append(total_table)
        elements.append(Spacer(1, 20))
    
    # Tesouro Direto Section
    num_tesouro = random.randint(2, 4)
    elements.append(Paragraph("Tesouro Direto", header_style))
    elements.append(Spacer(1, 6))
    
    tesouro_data = [["Produto", "Instituição", "Vencimento", "Quantidade", "Valor aplicado", "Valor atualizado"]]
    total_tesouro = 0
    
    selected_tesouros = random.sample(TESOURO_OPTIONS, num_tesouro)
    for name, maturity in selected_tesouros:
        qty = round(random.uniform(0.1, 3.0), 2)
        invested = random.uniform(1500, 5000)
        current = invested * random.uniform(1.05, 1.35)
        total_tesouro += current
        
        tesouro_data.append([
            name,
            "NU INVEST CORRETORA DE\nVALORES S.A.",
            maturity.replace("-", "/")[:7] + "/" + maturity[:4],
            str(qty),
            format_currency(invested),
            format_currency(current)
        ])
    
    tesouro_table = Table(tesouro_data, colWidths=[48*mm, 40*mm, 22*mm, 20*mm, 25*mm, 25*mm])
    tesouro_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
        ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(tesouro_table)
    elements.append(Spacer(1, 6))
    
    # Total
    total_table = Table([["", "", "", "", "Total", format_currency(total_tesouro)]], 
                      colWidths=[48*mm, 40*mm, 22*mm, 20*mm, 25*mm, 25*mm])
    total_table.setStyle(TableStyle([
        ('ALIGN', (4, 0), (-1, 0), 'RIGHT'),
        ('FONTNAME', (4, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (4, 0), (-1, 0), 8),
    ]))
    elements.append(total_table)
    
    # Build PDF
    doc.build(elements, onFirstPage=create_header_footer, onLaterPages=create_header_footer)
    print(f"Generated: {filename}")

def main():
    """Generate 50 portfolio PDFs"""
    print("Generating 50 investment portfolio PDFs...")
    
    # Generate random date range
    base_date = datetime(2025, 10, 3)
    
    for i in range(1, 51):
        # Generate random person data
        name = generate_random_name()
        cpf = generate_cpf()
        
        # Vary the date slightly
        date_offset = random.randint(-30, 7)
        portfolio_date = base_date + timedelta(days=date_offset)
        date_str = portfolio_date.strftime("%d/%m/%Y")
        
        # Generate filename
        filename = f"./aux/pdfs/posicao_{i:03d}_{portfolio_date.strftime('%Y-%m-%d')}.pdf"
        
        # Generate PDF
        generate_portfolio_pdf(filename, name, cpf, date_str)
    
    print(f"\nSuccessfully generated 50 PDFs in /aux/pdfs/")

if __name__ == "__main__":
    main()