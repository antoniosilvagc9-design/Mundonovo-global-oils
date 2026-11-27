"""Geração de PowerPoint editável a partir de dados demonstrativos."""
from io import BytesIO
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

DARK = RGBColor(10, 14, 17)
LIME = RGBColor(183, 255, 0)
WHITE = RGBColor(255, 255, 255)
MUTED = RGBColor(185, 192, 190)

def textbox(slide, text, x, y, w, h, size=18, color=WHITE, bold=False):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = shape.text_frame
    frame.word_wrap = True
    p = frame.paragraphs[0]
    p.text = text
    p.font.name = "Aptos"
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = color
    return shape

def add_slide(prs, title, lines, subtitle=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.background.fill
    bg.solid()
    bg.fore_color.rgb = DARK
    textbox(slide, "MUNDO NOVO  /  INTELIGÊNCIA EXECUTIVA", .6, .35, 11, .4, 13, LIME, True)
    textbox(slide, title, .6, 1.1, 11.5, .85, 30, WHITE, True)
    if subtitle:
        textbox(slide, subtitle, .6, 2.0, 11.4, .5, 14, MUTED)
    for i, line in enumerate(lines):
        textbox(slide, line, .85, 2.75 + i * .66, 11.5, .57, 19, WHITE)
    textbox(slide, "DEMONSTRAÇÃO • DADOS FICTÍCIOS • NÃO USAR PARA DECISÕES", .6, 6.95, 11.8, .3, 10, LIME, True)

def generate_presentation(data):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    items = data["commodities"]
    add_slide(prs, "Inteligência de Mercado", ["Relatório executivo automatizado", "Protótipo sem integração com o ERP"], data["periodo"])
    add_slide(prs, "Resumo executivo", [
        f'Contratos simulados: {data["contratos"]}',
        f'Margem média simulada: {data["margem_media_pct"]:.1f}%',
        f'Estoque simulado: {data["estoque_ton"]:,} toneladas',
        f'Câmbio hipotético USD/BRL: R$ {data["usd_brl"]:.2f}',
    ])
    add_slide(prs, "Mercado de commodities", [
        f'{item["nome"]}: índice {item["indice"]:.1f} | variação {item["variacao_pct"]:+.1f}%'
        for item in items
    ], "Índice-base hipotético 100; não são preços de mercado")
    add_slide(prs, "Riscos e oportunidades", [
        "Simulação: avaliar sensibilidade de margem ao câmbio.",
        "Simulação: monitorar desvios entre custo e preço de referência.",
        "Próximo passo: validar fontes e regras com a equipe comercial.",
    ])
    add_slide(prs, "Plano de ação", [
        "1. Validar indicadores prioritários com a diretoria.",
        "2. Homologar fonte de preços e periodicidade.",
        "3. Solicitar à TI acesso de leitura autorizado ao Maxys Web.",
        "4. Substituir dados fictícios após testes e aprovação.",
    ])
    buffer = BytesIO()
    prs.save(buffer)
    return buffer.getvalue()
