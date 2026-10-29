"""
Betinha — assistente de IA sobre apostas esportivas + simulador.

Como rodar (no terminal do VS Code, dentro da pasta do projeto):
    streamlit run app.py
"""

from __future__ import annotations

import base64
import html
import re
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st

import config
from quiz import QUIZ
from glossario import GLOSSARIO, TEMAS
from assistente import criar_cliente, montar_historico, montar_instrucoes, responder
from busca import BuscadorBase, carregar_base
from simulador import Parametros, brl, pct, resumo_em_texto, simular, validar

# Cores dos gráficos (validadas para daltonismo)
COR_APOSTAS = "#D0572F"
COR_INVESTIMENTO = "#2F6FD0"
COR_NEUTRA = "#8A857B"

SUGESTOES = [
    "O que é uma odd e como ela vira probabilidade?",
    "Por que a casa de apostas sempre ganha no longo prazo?",
    "Depois de perder várias vezes, a chance de ganhar aumenta?",
    "Quanto eu deixo de ganhar apostando em vez de investir?",
]

# Abas do menu (a ordem da lista é a ordem no menu)
CONVERSAR = "Conversar"
SIMULADOR = "Simulador"
QUIZ_PAG = "Mito ou verdade"
GLOSSARIO_PAG = "Glossário"
SOBRE = "Sobre a Betinha"
PAGINAS = [CONVERSAR, SIMULADOR, QUIZ_PAG, GLOSSARIO_PAG, SOBRE]
# Símbolos das abas (lista completa em https://fonts.google.com/icons — use o nome em inglês)
ICONES = {
    CONVERSAR: ":material/chat_bubble_outline:",
    SIMULADOR: ":material/bar_chart:",
    QUIZ_PAG: ":material/quiz:",
    GLOSSARIO_PAG: ":material/menu_book:",
    SOBRE: ":material/info:",
}
DESCRICOES = {
    CONVERSAR: "Tire suas dúvidas sobre apostas",
    SIMULADOR: "Veja quanto as apostas custam no longo prazo",
    QUIZ_PAG: "Teste o que você sabe",
    GLOSSARIO_PAG: "Os termos das apostas, explicados",
    SOBRE: "O que a Betinha faz e não faz",
}
FECHAR_MENU_AO_ESCOLHER = False  # True = o menu fecha sozinho depois de escolher uma aba

# Cores do menu lateral (troque aqui)
MENU_LARGURA = "270px"
MENU_FUNDO = "#F9DDD8"        # rosa do retângulo
MENU_TEXTO = "#4A2219"        # cor das letras
MENU_PASSAR_MOUSE = "#F3C9C1" # quando passa o mouse
MENU_ATIVA = "#EBB3A8"        # aba em que a pessoa está

# ---------------------------------------------------------------------------
# Configuração da página e estilo
# ---------------------------------------------------------------------------
st.set_page_config(page_title=config.NOME_ASSISTENTE, page_icon=config.AVATAR_ASSISTENTE,
                   layout="centered")

# Versões antigas do Streamlit não desenham a barra do topo direito.
# Em vez de a tela ficar "vazia" sem explicação, avisamos o que fazer.
_versao = tuple(int(x) for x in st.__version__.split(".")[:2] if x.isdigit())
if _versao < (1, 50):
    st.error(
        f"Seu Streamlit está na versão {st.__version__}, e este app precisa da 1.50 ou mais nova. "
        "No terminal do VS Code, rode `pip install -U streamlit`, feche o app (Ctrl+C) "
        "e rode `streamlit run app.py` de novo."
    )
    st.stop()
# st.html com só <style> não ocupa espaço na página (st.markdown deixava um vão no topo)
st.html(f"<style>{(config.PASTA_PROJETO / 'estilo.css').read_text(encoding='utf-8')}</style>")

# Estilo das funções novas (fica aqui para não mexer no estilo.css do grupo)
st.html("""<style>
/* tira o aviso "Press Enter to submit form" das caixas de número */
[data-testid="InputInstructions"] { display: none !important; }
/* símbolos (mesma família de ícones dos botões) dentro de textos em HTML */
.icone-ms { font-family: 'Material Symbols Rounded'; font-weight: normal; font-style: normal; font-size: 1.15em;
  line-height: 1; vertical-align: -.2em; display: inline-block; letter-spacing: normal; text-transform: none;
  white-space: nowrap; -webkit-font-feature-settings: 'liga'; font-feature-settings: 'liga'; }
.equivale .emoji .icone-ms { font-size: 2rem; color: #C4572F; }
/* a caixa de escrever fica presa no rodapé sozinha; não precisa de tanto espaço embaixo */
.block-container, [data-testid="stMainBlockContainer"] { padding-bottom: 2rem !important; }
.st-key-entrada_inicial_caixa { max-width: 720px; margin: .9rem auto 0; width: 100%; }
/* simulador mais compacto */
.intro-sim { color: #5C5850; margin: -.4rem 0 .2rem; }
.rotulo-secao { font-weight: 700; font-size: .95rem; color: #3A342C; margin: 0 0 .1rem; }
.st-key-frase_sim { row-gap: .4rem; }
.st-key-frase_sim [data-testid="stMarkdownContainer"] p { margin: 0 !important; font-size: 1.08rem; white-space: nowrap; }
.st-key-frase_sim .stMarkdown { margin: 0 .35rem; }
.st-key-frase_sim [data-testid="stMarkdownContainer"] p { line-height: 1.2 !important; padding: 0 !important; }
.st-key-frase_sim [data-testid="stMarkdownContainer"] { margin: 0 !important; }
.st-key-frase_sim > div { margin-bottom: 0 !important; }
.st-key-calc_margem_res { margin-top: .2rem; }
/* glossário */
.glos-tema { font-weight: 700; font-size: 1.05rem; color: #3A342C; margin: 1rem 0 .1rem; }
.glos-exemplo { background: #F7F3EC; border-radius: 10px; padding: .5rem .8rem; margin: .2rem 0 .3rem; font-size: .95rem; }
/* menos espaço no alto de todas as abas */
.block-container, [data-testid="stMainBlockContainer"] { padding-top: .9rem !important; }
.st-key-barra_topo { margin-bottom: .3rem !important; }
.stMarkdown h1 { padding-top: .4rem !important; }
/* tira o símbolo de link que aparece ao lado dos títulos */
[data-testid="stHeaderActionElements"], .stMarkdown h1 > a, .stMarkdown h2 > a, .stMarkdown h3 > a,
.stMarkdown h4 > a, .stMarkdown h5 > a, .stMarkdown h6 > a { display: none !important; }
/* tela inicial do chat mais compacta: tudo aparece sem rolar */
.boas-vindas { margin: 1.2rem 0 .4rem !important; }
.boas-vindas .rosto-grande { width: 72px !important; height: 72px !important; margin-bottom: .35rem !important; }
.boas-vindas h1 { font-size: 2rem !important; margin-bottom: .1rem !important; padding: 0 !important; }
.boas-vindas p { margin-bottom: 0 !important; }
/* botão "Menu" preso no canto superior esquerdo da tela (em telas largas, onde há espaço) */
/* em telas largas ele fica no canto da tela; em telas estreitas, ao lado do nome da Betinha */
@media (min-width: 1140px) {
  .st-key-botao_menu { position: fixed; top: 14px; left: 16px; z-index: 1000002; width: auto !important; }
}
.st-key-botao_menu button { font-weight: 600; border-radius: 10px; }
/* o conteúdo desliza junto quando o menu abre/fecha */
.block-container, [data-testid="stMainBlockContainer"] { transition: margin-left .25s ease, max-width .25s ease; }
[data-testid="stBottom"] > div { transition: padding-left .25s ease; }
/* barra do topo */
.st-key-barra_topo { margin-bottom: 1rem; }
/* convite para escrever a própria pergunta */
.convite-escrever { text-align: center; color: #5C5850; margin: .9rem 0 .1rem; font-size: 1rem; }
/* legenda dos gráficos em palavras */
.legenda-simples { display: flex; flex-direction: column; gap: .35rem; margin: .2rem 0 .8rem; font-size: .95rem; }
.legenda-simples .pt { display: inline-block; width: 14px; height: 14px; border-radius: 50%; margin-right: .5rem; vertical-align: -2px; }
.legenda-simples .tracejado { display: inline-block; width: 18px; border-top: 3px dashed #8A857B; margin-right: .5rem; vertical-align: 3px; }
/* 100 pessoas */
.cem { display: grid; grid-template-columns: repeat(20, 1fr); gap: 5px; max-width: 520px; margin: .6rem auto .8rem; }
.cem span { aspect-ratio: 1; border-radius: 50%; display: block; }
.cem-legenda { display: flex; flex-wrap: wrap; gap: .4rem 1.4rem; justify-content: center; font-size: 1rem; margin-bottom: .6rem; }
.cem-legenda .pt { display: inline-block; width: 14px; height: 14px; border-radius: 50%; margin-right: .4rem; vertical-align: -2px; }
/* perguntas sugeridas clicáveis */
.st-key-seguir .stButton > button {
  text-align: left; justify-content: flex-start; background: #FFFFFF;
  border: 1px solid #E2DDD2; border-radius: 999px; padding: .35rem .9rem; font-weight: 400;
}
.st-key-seguir .stButton > button p { white-space: normal; text-align: left; }
.rotulo-seguir { font-size: .82rem; color: #8A857B; margin: .2rem 0 .3rem 0; }
/* "isso equivale a" */
.equivale { display: grid; grid-template-columns: repeat(3, 1fr); gap: .7rem; margin: .6rem 0 .3rem; }
@media (max-width: 640px) { .equivale { grid-template-columns: 1fr; } }
.equivale .item { background: #FFFFFF; border: 1px solid #E2DDD2; border-radius: 14px; padding: .8rem 1rem; text-align: center; }
.equivale .emoji { font-size: 1.8rem; line-height: 1.2; }
.equivale .num { font-size: 1.5rem; font-weight: 600; }
.equivale .txt { font-size: .85rem; color: #5C5850; }
.fontes-equivale { font-size: .72rem; color: #8A857B; margin-bottom: 1rem; }
/* quiz */
.quiz-card { background: #FFFFFF; border: 1px solid #E2DDD2; border-radius: 16px; padding: 1.4rem 1.5rem; margin: .8rem 0; }
.quiz-card .num { font-size: .8rem; color: #8A857B; margin-bottom: .4rem; }
.quiz-card .frase { font-size: 1.3rem; font-weight: 600; line-height: 1.45; }
.quiz-feedback { border-radius: 14px; padding: 1rem 1.2rem; margin: .6rem 0 1rem; line-height: 1.6; }
.quiz-feedback.certo { background: #E8F3EC; border: 1px solid #9CCBAE; }
.quiz-feedback.errado { background: #FBEAE5; border: 1px solid #E8A894; }
</style>""")

# Estado da sessão (o que o app "lembra" enquanto a aba está aberta)
st.session_state.setdefault("mensagens", [])
st.session_state.setdefault("pergunta_pendente", None)
st.session_state.setdefault("resultado_simulacao", None)
st.session_state.setdefault("pagina", CONVERSAR)
st.session_state.setdefault("letra_grande", False)
st.session_state.setdefault("menu_aberto", False)
st.session_state.setdefault("quiz_idx", 0)
st.session_state.setdefault("quiz_acertos", 0)
st.session_state.setdefault("quiz_resposta", None)


# ---------------------------------------------------------------------------
# Recursos carregados uma vez só (cache)
# ---------------------------------------------------------------------------
def assinatura_da_base() -> str:
    """Muda sempre que algum arquivo da base é editado -> recarrega sozinho."""
    arquivos = sorted(config.PASTA_BASE.glob("*.md"))
    return "|".join(f"{a.name}:{a.stat().st_mtime_ns}" for a in arquivos)


@st.cache_resource(show_spinner=False)
def obter_cliente(api_key: str):
    return criar_cliente(api_key)


@st.cache_resource(show_spinner="Carregando a base de conhecimento…")
def obter_buscador(api_key: str, _assinatura: str) -> BuscadorBase:
    trechos = carregar_base(config.PASTA_BASE)
    return BuscadorBase(
        cliente=obter_cliente(api_key),
        trechos=trechos,
        modelo_embedding=config.MODELO_EMBEDDING,
        pasta_cache=config.PASTA_CACHE,
        limite_base_completa=config.LIMITE_BASE_COMPLETA,
    )


# ---------------------------------------------------------------------------
# Funções de navegação (callbacks rodam antes da página ser redesenhada)
# ---------------------------------------------------------------------------
def usar_sugestao(texto: str):
    st.session_state.pergunta_pendente = texto


def explicar_simulacao_no_chat():
    st.session_state.pergunta_pendente = (
        "Acabei de usar o simulador. Pode me explicar o meu resultado de forma simples?"
    )
    st.session_state.pagina = CONVERSAR


# ---------------------------------------------------------------------------
# Auxiliares de texto e imagem
# ---------------------------------------------------------------------------
def sem_formula(texto: str) -> str:
    """Impede que "R$ 10 ... R$ 25" vire fórmula matemática (texto verde).

    O Streamlit entende o que está entre dois "$" como fórmula. Colocar uma
    barra antes ("\\$") faz o cifrão aparecer normal.
    """
    return texto.replace("\\$", "$").replace("$", "\\$")


def imagem_html(tamanho: int, classe: str) -> str:
    """Rosto da Betinha como <img> (ou o emoji reserva, se não houver imagem)."""
    caminho = Path(config.AVATAR_ASSISTENTE)
    if not caminho.exists():
        return f'<span class="{classe}">{config.AVATAR_ASSISTENTE}</span>'
    tipo = "jpeg" if caminho.suffix.lower() in (".jpg", ".jpeg") else caminho.suffix[1:].lower()
    dados = base64.b64encode(caminho.read_bytes()).decode()
    return (f'<img class="{classe}" width="{tamanho}" height="{tamanho}" '
            f'src="data:image/{tipo};base64,{dados}" alt="">')


# ---------------------------------------------------------------------------
# Barra do topo: ☰ Menu + nome | Letra maior + Preciso de ajuda
# ---------------------------------------------------------------------------
CSS_MENU = f"""<style>
/* ---------- Menu lateral: retângulo rosa preso na esquerda ---------- */
.st-key-menu_lateral {{
  position: fixed; top: 0; left: 0; bottom: 0; width: {MENU_LARGURA};
  background: {MENU_FUNDO}; z-index: 1000001; overflow-y: auto;
  padding: 1rem .9rem 1.5rem; gap: .45rem; box-shadow: 2px 0 14px rgba(0,0,0,.07);
}}
.st-key-menu_cabecalho {{
  padding: 0 .1rem .8rem .5rem; margin-bottom: .5rem; border-bottom: 1px solid rgba(74,34,25,.15);
}}
.st-key-menu_lateral .titulo-menu {{ color: {MENU_TEXTO}; font-weight: 700; font-size: 1.15rem; margin: 0; }}
/* cada aba = um bloquinho com nome + frase curta */
.st-key-menu_lateral [class*="st-key-item_menu_"] {{
  border-radius: 12px; padding: .6rem .7rem 1.15rem; gap: .15rem; transition: background .15s;
}}
.st-key-menu_lateral [class*="st-key-item_menu_"]:hover {{ background: {MENU_PASSAR_MOUSE}; }}
.st-key-menu_lateral [class*="st-key-item_menu_"]:has(button[kind="primary"]) {{ background: {MENU_ATIVA}; }}
.st-key-menu_lateral [class*="st-key-item_menu_"] .stButton > button {{
  background: transparent !important; border: none !important; box-shadow: none !important;
  color: {MENU_TEXTO} !important; justify-content: flex-start; text-align: left;
  padding: 0 !important; min-height: 0 !important; width: 100%;
}}
.st-key-menu_lateral .stButton > button > div,
.st-key-menu_lateral .stButton > button [data-testid="stMarkdownContainer"] {{ justify-content: flex-start; text-align: left; }}
.st-key-menu_lateral .stButton > button p {{ color: inherit !important; font-weight: 600; font-size: 1rem !important; text-align: left; }}
.st-key-menu_lateral [class*="st-key-item_menu_"] .stButton > button span[data-testid="stIconMaterial"] {{ font-size: 1.25rem; margin-right: .35rem; }}
.st-key-menu_lateral .desc-menu {{ color: {MENU_TEXTO}; opacity: .72; font-size: .82rem !important;
  line-height: 1.35; margin: 0 0 0 1.75rem; }}
.st-key-fechar_menu button {{
  background: transparent !important; border: none !important; box-shadow: none !important;
  color: {MENU_TEXTO} !important; padding: .25rem .4rem !important; min-height: 0 !important;
}}
.st-key-fechar_menu button:hover {{ background: {MENU_PASSAR_MOUSE} !important; }}
.st-key-fechar_menu span[data-testid="stIconMaterial"], .st-key-fechar_menu p {{ font-size: 1.45rem !important; }}
/* empurra o conteúdo do meio para a direita, junto com o menu (tela de computador) */
@media (min-width: 860px) {{
  .block-container, [data-testid="stMainBlockContainer"] {{
    margin-left: max(calc({MENU_LARGURA} + 2rem), calc({MENU_LARGURA} + (100vw - {MENU_LARGURA} - 880px) / 2)) !important;
    margin-right: auto !important;
    max-width: min(880px, calc(100vw - {MENU_LARGURA} - 4rem)) !important;
  }}
  [data-testid="stBottom"] > div {{ padding-left: {MENU_LARGURA}; }}
}}
/* no celular o menu aparece no topo da página, sem cobrir o conteúdo */
@media (max-width: 859px) {{
  .st-key-menu_lateral {{ position: static; width: auto; border-radius: 16px; margin-bottom: 1rem; }}
}}
</style>"""


def alternar_menu():
    st.session_state.menu_aberto = not st.session_state.menu_aberto


def ir_para(pagina: str):
    st.session_state.pagina = pagina
    if FECHAR_MENU_AO_ESCOLHER:
        st.session_state.menu_aberto = False


with st.container(key="barra_topo", horizontal=True, horizontal_alignment="distribute",
                  vertical_alignment="center"):
    with st.container(horizontal=True, vertical_alignment="center", width="content"):
        # Botão do menu: preso no canto superior esquerdo da tela (some quando o menu está aberto)
        if not st.session_state.menu_aberto:
            st.button("Menu", icon=":material/menu:", key="botao_menu", on_click=alternar_menu)
        st.markdown(f'<div class="marca">{imagem_html(30, "rosto-marca")}'
                    f"{html.escape(config.NOME_ASSISTENTE)}</div>", unsafe_allow_html=True)
    with st.container(horizontal=True, vertical_alignment="center", width="content", key="barra_acoes"):
        st.toggle(":material/text_increase: Letra maior", key="letra_grande")
        with st.popover("Preciso de ajuda", icon=":material/support:"):
            st.markdown(
                "**Se apostar está trazendo prejuízo ou sofrimento, você não está sozinho.**\n\n"
                ":material/local_hospital: **SUS**: procure uma **UBS** (posto de saúde) ou um **CAPS** perto de você.\n\n"
                ":material/block: **Bloquear as bets**: a [autoexclusão do gov.br]"
                "(https://www.gov.br/pt-br/servicos/plataforma-centralizada-de-autoexclusao-apostas) "
                "bloqueia todas as casas autorizadas de uma vez, de graça.\n\n"
                ":material/groups: **Jogadores Anônimos**: grupos de apoio gratuitos."
            )


def desenhar_menu():
    """Retângulo rosa na esquerda, com as abas uma embaixo da outra (como no Claude)."""
    st.html(CSS_MENU)
    with st.container(key="menu_lateral"):
        with st.container(key="menu_cabecalho", horizontal=True, horizontal_alignment="distribute",
                          vertical_alignment="center"):
            st.markdown('<div class="titulo-menu">Menu</div>', unsafe_allow_html=True)
            st.button(":material/left_panel_close:", key="fechar_menu", on_click=alternar_menu,
                      help="Fechar o menu")
        for n, pag in enumerate(PAGINAS):
            with st.container(key=f"item_menu_{n}"):
                st.button(pag, icon=ICONES[pag], key=f"menu_{n}", on_click=ir_para, args=(pag,),
                          width="stretch", type="primary" if st.session_state.pagina == pag else "secondary")
                st.markdown(f'<div class="desc-menu">{DESCRICOES[pag]}</div>', unsafe_allow_html=True)


if st.session_state.letra_grande:
    st.html("""<style>
    .stApp p, .stApp li, .stApp label, .stApp td, .balao-usuario, .caixa-explicacao, .quiz-feedback,
    .stApp .stButton > button p { font-size: 1.22rem !important; line-height: 1.7 !important; }
    /* os controles do topo continuam do tamanho normal, para não cortar o texto */
    .st-key-barra_acoes p, .st-key-barra_acoes label, .st-key-botao_menu p { font-size: .95rem !important; line-height: 1.4 !important; }
    .st-key-menu_lateral .desc-menu { font-size: .95rem !important; }
    .legenda-simples, .cem-legenda, .convite-escrever { font-size: 1.2rem !important; }
    .stApp h1 { font-size: 2.7rem !important; } .stApp h2 { font-size: 2.2rem !important; }
    .stApp h4 { font-size: 1.5rem !important; }
    .cartao .valor, .equivale .num { font-size: 1.8rem !important; }
    .cartao .rotulo, .cartao .nota, .equivale .txt, .rotulo-seguir { font-size: 1rem !important; }
    .quiz-card .frase { font-size: 1.6rem !important; }
    div[data-testid="stChatInput"] textarea { font-size: 1.2rem !important; }
    </style>""")

# Sem chave da API não dá para conversar
if not config.GEMINI_API_KEY:
    # As outras abas (simulador, quiz, sobre) continuam funcionando; só o chat avisa.
    cliente = buscador = None
else:
    cliente = obter_cliente(config.GEMINI_API_KEY)
    buscador = obter_buscador(config.GEMINI_API_KEY, assinatura_da_base())


# ===========================================================================
# PÁGINA 1 — CHAT
# ===========================================================================
def formatar_resposta(texto: str, ocultar_pergunta_repetida: bool = False) -> str:
    """Separa 'Fonte:' e 'Quer saber mais?' em um rodapé visual organizado."""
    linhas = texto.strip().splitlines()
    corpo = []
    fonte = None
    termo_tecnico = None
    pergunta_extra = None

    for linha in linhas:
        l_limpa = linha.strip()
        # 1. Identifica a linha de Fonte
        if re.match(r"^\*?fontes?\s*:", l_limpa, flags=re.I):
            fonte = re.sub(r"^\*?fontes?\s*:\s*", "", l_limpa, flags=re.I).strip(" *.")
            continue

        # 2. Identifica a linha "Quer saber mais?"
        if "quer saber mais" in l_limpa.lower() or "pode me perguntar" in l_limpa.lower():
            resto = re.sub(r"^.*?quer\s+saber\s+mais\?\s*", "", l_limpa, flags=re.I)
            partes = re.split(r"voc[eê]\s+pode\s+me\s+perguntar\s*:?", resto, flags=re.I)

            parte_termo = partes[0].strip(" ·|-–—.*_\"'“”")
            parte_termo = re.sub(r"^nome\s+t[eé]cnico\s*:\s*", "", parte_termo, flags=re.I).strip(" ·|-–—.*_\"'“”")
            if parte_termo:
                termo_tecnico = parte_termo

            if len(partes) > 1:
                pergunta_extra = partes[1].strip(" ·|-–—*_\"'“”")
            continue

        corpo.append(linha)

    texto_principal = sem_formula("\n".join(corpo).strip())

    # Monta o cartão de rodapé se houver informações extras
    itens_rodape = []
    if termo_tecnico:
        itens_rodape.append(
            f'<div class="meta-linha"><span class="meta-badge">Nome técnico</span> '
            f'<span class="meta-valor">{html.escape(termo_tecnico)}</span></div>'
        )
    if fonte:
        itens_rodape.append(
            f'<div class="meta-linha"><span class="meta-rotulo">Fonte:</span> '
            f'<span class="meta-fonte">{html.escape(fonte)}</span></div>'
        )
    if pergunta_extra and not ocultar_pergunta_repetida:
        itens_rodape.append(
            f'<div class="meta-linha"><span class="meta-rotulo">Para aprofundar:</span> '
            f'<span class="meta-fonte">“{html.escape(pergunta_extra)}”</span></div>'
        )

    if itens_rodape:
        rodape_html = f'<div class="rodape-betinha">{"".join(itens_rodape)}</div>'
        return f"{texto_principal}\n\n{rodape_html}"

    return texto_principal


def mostrar_mensagem(papel: str, texto: str, eh_ultima: bool = False) -> None:
    """Pessoa: só o balão (sem ícone). Betinha: com o rostinho dela."""
    if papel == "user":
        seguro = html.escape(texto).replace("$", "&#36;").replace("\n", "<br>")
        st.markdown(f'<div class="linha-usuario"><div class="balao-usuario">{seguro}</div></div>',
                    unsafe_allow_html=True)
    else:
        with st.chat_message("assistant", avatar=config.AVATAR_ASSISTENTE):
            st.markdown(formatar_resposta(texto, ocultar_pergunta_repetida=eh_ultima),
                        unsafe_allow_html=True)


def perguntas_sugeridas(texto: str) -> list[str]:
    """Pega as perguntas da linha 'Quer saber mais? ... Você pode me perguntar: ...'."""
    linhas = [l for l in texto.splitlines() if "saber mais" in l.lower() or "pode me perguntar" in l.lower()]
    if not linhas:
        return []
    achou = re.search(r"pode me perguntar\s*:?\s*(.+)", linhas[-1], flags=re.I)
    if not achou:
        return []
    partes = re.split(r"[;|]|\s+ou\s+(?=[\"“'])", achou.group(1))
    perguntas = []
    for parte in partes:
        q = parte.strip().strip('*_ "“”\'.').strip()
        if len(q) > 8:
            perguntas.append(q if q.endswith("?") else q + "?")
    return perguntas[:2]


def usar_pergunta_sugerida(texto: str):
    st.session_state.pergunta_pendente = texto


def botoes_seguir():
    """Botões com as perguntas sugeridas na última resposta da Betinha."""
    msgs = st.session_state.mensagens
    if not msgs or msgs[-1]["role"] != "assistant":
        return
    perguntas = perguntas_sugeridas(msgs[-1]["content"])
    if not perguntas:
        return
    st.markdown('<div class="rotulo-seguir">Toque para perguntar:</div>', unsafe_allow_html=True)
    with st.container(key="seguir"):
        for i, q in enumerate(perguntas):
            st.button(q, key=f"seguir_{len(msgs)}_{i}", on_click=usar_pergunta_sugerida, args=(q,))


def enviar_pergunta_inicial():
    texto = (st.session_state.get("entrada_inicial") or "").strip()
    if texto:
        st.session_state.pergunta_pendente = texto


def pagina_chat(digitada: str | None):
    if buscador is None:
        st.error(
            "Não encontrei a **GEMINI_API_KEY**. Coloque o arquivo `.env` na pasta do projeto "
            "(a mesma pasta do `app.py`) com a linha `GEMINI_API_KEY=sua_chave_aqui` e reinicie o app. "
            "As outras abas do menu funcionam mesmo sem a chave."
        )
        return
    if not buscador.trechos:
        st.warning(
            "A base de conhecimento está vazia. Coloque arquivos `.md` na pasta "
            "`base_conhecimento/` (veja o modelo `_MODELO.md`)."
        )
    if buscador.aviso:
        st.info(buscador.aviso)

    # Tela de boas-vindas (só quando a conversa está vazia). Fica num st.empty para sumir
    # na hora em que a conversa começa (sem ficar "apagada" na tela enquanto a resposta chega).
    espaco_inicial = st.empty()
    if not st.session_state.mensagens and not st.session_state.pergunta_pendente and not digitada:
        with espaco_inicial.container():
            st.markdown(
                f'<div class="boas-vindas">{imagem_html(96, "rosto-grande")}'
                f"<h1>Oi! Eu sou a {html.escape(config.NOME_ASSISTENTE)}.</h1>"
                f"<p>{html.escape(config.SUBTITULO)}</p></div>",
                unsafe_allow_html=True,
            )
            # Na tela inicial a caixa de escrever fica no meio (como no Claude). Assim a página
            # não "rola para baixo" sozinha ao abrir. Depois da 1ª pergunta ela vai para o rodapé.
            with st.container(key="entrada_inicial_caixa"):
                st.chat_input("Escreva aqui a sua pergunta sobre apostas…", key="entrada_inicial",
                              on_submit=enviar_pergunta_inicial)
            st.markdown('<div class="convite-escrever"><span class="icone-ms">edit</span> <b>Escreva a sua pergunta</b> '
                        'na caixa acima, do seu jeito. Ou, se preferir, toque em uma destas:</div>',
                        unsafe_allow_html=True)
            with st.container(key="sugestoes"):
                colunas = st.columns(2)
                for i, sugestao in enumerate(SUGESTOES):
                    colunas[i % 2].button(
                        sugestao, key=f"sug_{i}", on_click=usar_sugestao, args=(sugestao,),
                        width="stretch",
                    )
            st.markdown(
                '<div class="aviso-chat">As respostas vêm da base do projeto, mas a IA pode errar. '
                "Confira as fontes.</div>",
                unsafe_allow_html=True,
            )

    # Histórico
    tem_nova_pergunta = bool(digitada or st.session_state.pergunta_pendente)
    for idx, m in enumerate(st.session_state.mensagens):
        eh_ultima = (idx == len(st.session_state.mensagens) - 1) and not tem_nova_pergunta
        mostrar_mensagem(m["role"], m["content"], eh_ultima=eh_ultima)
    if not tem_nova_pergunta:
        botoes_seguir()

    # Pergunta nova: digitada ou vinda de um botão
    pergunta = digitada or st.session_state.pergunta_pendente
    st.session_state.pergunta_pendente = None
    if not pergunta:
        return

    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    mostrar_mensagem("user", pergunta)

    # Busca: usa as duas últimas perguntas (ajuda em perguntas de continuação,
    # como "e no cassino online também?")
    perguntas_usuario = [m["content"] for m in st.session_state.mensagens if m["role"] == "user"]
    consulta = "\n".join(perguntas_usuario[-2:])
    trechos = buscador.buscar(consulta, config.TRECHOS_POR_PERGUNTA)

    resultado = st.session_state.resultado_simulacao
    instrucoes = montar_instrucoes(
        config.NOME_ASSISTENTE,
        trechos,
        resumo_em_texto(resultado) if resultado else None,
    )
    historico = montar_historico(st.session_state.mensagens, config.MENSAGENS_DE_HISTORICO)

    with st.chat_message("assistant", avatar=config.AVATAR_ASSISTENTE):
        espaco_resposta = st.empty()
        with st.spinner("Pensando…"):
            fluxo = responder(cliente, config.MODELO_CHAT, instrucoes, historico, config.TEMPERATURA)
            primeiro = next(fluxo, "")

        texto_original = []  # guarda a resposta sem os escapes de "$"

        def continuar():
            for pedaco in [primeiro, *fluxo]:
                texto_original.append(pedaco)
                yield sem_formula(pedaco)

        with espaco_resposta.container():
            st.write_stream(continuar())

        resposta_completa = "".join(texto_original)
        espaco_resposta.markdown(
            formatar_resposta(resposta_completa, ocultar_pergunta_repetida=True),
            unsafe_allow_html=True,
        )

    st.session_state.mensagens.append({"role": "assistant", "content": resposta_completa})
    botoes_seguir()


# ===========================================================================
# PÁGINA 2 — SIMULADOR
# ===========================================================================
def cartao(rotulo: str, valor: str, nota: str = "", destaque: bool = False) -> str:
    classe = "cartao destaque" if destaque else "cartao"
    nota_html = f'<div class="nota">{nota}</div>' if nota else ""
    return (f'<div class="{classe}"><div class="rotulo">{rotulo}</div>'
            f'<div class="valor">{valor}</div>{nota_html}</div>')


def grafico_trajetorias(r) -> go.Figure:
    """Três linhas simples, com o valor final escrito na ponta de cada uma."""
    x = r.eixo_tempo_anos
    linhas = [
        ("Se você guardasse e investisse", r.investimento, COR_INVESTIMENTO, "solid", 3),
        ("Dinheiro que saiu do seu bolso", r.aportado, COR_NEUTRA, "dash", 2),
        ("Se você apostasse (o mais comum)", r.percentis[50], COR_APOSTAS, "solid", 3),
    ]
    fig = go.Figure()
    for nome, y, cor, traco, largura in linhas:
        fig.add_trace(go.Scatter(
            x=x, y=y, mode="lines", name=nome, line=dict(color=cor, width=largura, dash=traco),
            hovertemplate="%{y:,.0f}<extra>" + nome + "</extra>"))
        fig.add_trace(go.Scatter(
            x=[x[-1]], y=[y[-1]], mode="markers", showlegend=False, hoverinfo="skip",
            marker=dict(color=cor, size=11, line=dict(color="#FFFFFF", width=2))))
    fig.update_layout(
        height=400, margin=dict(l=10, r=20, t=10, b=10),
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", showlegend=False,
        font=dict(family="Inter, sans-serif", color="#22201C", size=13),
        hovermode="x unified", separators=",.",
        xaxis=dict(title="Anos", showgrid=False, linecolor="#E2DDD2", dtick=1),
        yaxis=dict(title="Quanto você teria (R$)", gridcolor="#EFECE4", zeroline=False,
                   tickprefix="R$ ", tickformat=",.0f", rangemode="tozero"),
    )
    return fig


def legenda_trajetorias(r):
    """Legenda em palavras, já com o valor no fim do período."""
    anos = r.parametros.anos
    fim = f"depois de {anos} ano{'s' if anos > 1 else ''}"
    st.markdown(
        '<div class="legenda-simples">'
        f'<div><span class="pt" style="background:{COR_INVESTIMENTO}"></span>'
        f'<b>Azul – se você guardasse e investisse:</b> teria <b>{brl(float(r.investimento[-1]))}</b> {fim}.</div>'
        f'<div><span class="tracejado"></span><b>Cinza tracejado – o que saiu do seu bolso:</b> '
        f'<b>{brl(float(r.aportado[-1]))}</b> no total.</div>'
        f'<div><span class="pt" style="background:{COR_APOSTAS}"></span>'
        f'<b>Laranja – se você apostasse:</b> sobrariam <b>{brl(float(r.percentis[50][-1]))}</b> '
        f'{fim}, no resultado mais comum.</div>'
        '</div>'.replace("$", "&#36;"), unsafe_allow_html=True)


def cem_pessoas(r):
    """'Se 100 pessoas apostassem assim': 100 bolinhas coloridas."""
    finais = r.resultados_finais
    fracoes = {"prejuizo": float(np.mean(finais < 0)), "empate": float(np.mean(finais == 0)),
               "lucro": float(np.mean(finais > 0))}
    # arredonda para somar exatamente 100 (método do maior resto)
    base = {k: int(v * 100) for k, v in fracoes.items()}
    sobra = 100 - sum(base.values())
    for k in sorted(fracoes, key=lambda k: fracoes[k] * 100 - base[k], reverse=True)[:sobra]:
        base[k] += 1
    cores = {"prejuizo": COR_APOSTAS, "empate": "#C9C2B4", "lucro": COR_INVESTIMENTO}
    bolinhas = "".join(f'<span style="background:{cores[k]}"></span>'
                       for k in ("prejuizo", "empate", "lucro") for _ in range(base[k]))

    st.markdown("#### Se 100 pessoas apostassem desse jeito")
    def verbo(n):
        return "terminaria" if n == 1 else "terminariam"
    partes = [f'<span><span class="pt" style="background:{COR_APOSTAS}"></span>'
              f'<b>{base["prejuizo"]}</b> {verbo(base["prejuizo"])} com prejuízo</span>']
    if base["empate"]:
        empat = "empatada" if base["empate"] == 1 else "empatadas"
        partes.append(f'<span><span class="pt" style="background:#C9C2B4"></span>'
                      f'<b>{base["empate"]}</b> {verbo(base["empate"])} {empat}</span>')
    partes.append(f'<span><span class="pt" style="background:{COR_INVESTIMENTO}"></span>'
                  f'<b>{base["lucro"]}</b> {verbo(base["lucro"])} com lucro, por sorte</span>')
    st.markdown(f'<div class="cem-legenda">{"".join(partes)}</div><div class="cem">{bolinhas}</div>',
                unsafe_allow_html=True)

    ganhos, perdas = finais[finais > 0], finais[finais < 0]
    frase = []
    if len(perdas):
        frase.append(f"Quem terminou no prejuízo perdeu, em média, **{brl(float(-perdas.mean()))}**.")
    if len(ganhos):
        frase.append(f"Quem teve sorte e terminou no lucro ganhou, em média, **{brl(float(ganhos.mean()))}**.")
    st.markdown(sem_formula(" ".join(frase)))


def numero_br(x: float) -> str:
    """1 casa decimal no padrão brasileiro, sem ',0' quando é inteiro."""
    texto = f"{x:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return texto[:-2] if texto.endswith(",0") else texto


def equivalencias(perda_media: float, total_apostado: float):
    """Mostra a perda média em coisas do dia a dia (preços com fonte no config.py)."""
    itens = []
    for e in config.EQUIVALENCIAS:
        qtd = perda_media / e["valor"]
        nome = e["singular"] if round(qtd, 1) == 1 else e["plural"]
        itens.append(f'<div class="item"><div class="emoji"><span class="icone-ms">{e["icone"]}</span></div>'
                     f'<div class="num">{numero_br(qtd)}</div><div class="txt">{nome}</div></div>')
    cesta = config.EQUIVALENCIAS[0]
    st.markdown("#### O que esse dinheiro compraria")
    st.markdown(
        sem_formula(f"Em média, você perderia **{brl(perda_media)}** nesse período. "
                    "Com esse dinheiro, daria para pagar:"))
    st.markdown(f'<div class="equivale">{"".join(itens)}</div>', unsafe_allow_html=True)
    st.markdown(sem_formula(
        f"E todo o dinheiro que passaria pelas apostas (**{brl(total_apostado)}**) equivale a "
        f"**{numero_br(total_apostado / cesta['valor'])} {cesta['plural']}**."))
    fontes = " · ".join(f'{e["singular"].capitalize()}: {brl(e["valor"])} ({e["fonte"]})' for e in config.EQUIVALENCIAS)
    st.markdown(f'<div class="fontes-equivale">Preços de referência: {html.escape(fontes)}.</div>',
                unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Calculadora da margem da casa a partir das odds de uma aposta de verdade
# ---------------------------------------------------------------------------
# Odds de exemplo para cada número de resultados (a pessoa troca pelas do site)
ODDS_EXEMPLO = {
    2: [1.90, 1.90],
    3: [2.10, 3.20, 3.60],
    4: [2.50, 3.40, 5.00, 6.00],
    5: [3.00, 4.00, 5.00, 6.00, 7.00],
    6: [4.00, 4.50, 5.00, 6.00, 7.00, 8.00],
}


def usar_margem_calculada(valor_pct: float):
    st.session_state.margem_pct = valor_pct


def calculadora_margem():
    with st.expander("Não sabe a margem da casa? Descubra com as odds de uma aposta de verdade",
                     icon=":material/calculate:"):
        st.markdown(
            "Toda aposta tem uma lista de resultados possíveis, e só um deles acontece. "
            "Abra a aposta no site e copie a odd de **todos** os resultados da lista."
        )
        n = st.segmented_control(
            "Quantos resultados possíveis essa aposta tem?", options=[2, 3, 4, 5, 6], default=3,
            key="calc_n", format_func=lambda x: f"{x}" if x < 6 else "6 ou mais",
        ) or 3
        st.caption(
            "Exemplos — **2:** sim ou não (\"as duas equipes marcam?\"), mais ou menos de 2,5 gols, "
            "quem vence no tênis ou no vôlei · **3:** vitória, empate ou derrota · "
            "**4 ou mais:** quem faz o primeiro gol, placar exato, corrida, campeão do torneio "
            "(com mais de 6, use os 6 mais prováveis: a margem vai ficar um pouco menor que a real)."
        )
        with st.container(horizontal=True, gap="small"):
            odds = [
                st.number_input(f"Resultado {k + 1}", min_value=1.01, step=0.05, format="%.2f",
                                value=ODDS_EXEMPLO[n][k], key=f"calc_odd_{n}_{k}", width=110)
                for k in range(n)
            ]
        chances = [1 / o for o in odds]
        soma = sum(chances)
        partes = " + ".join(pct(c).replace("%", "") for c in chances)
        with st.container(key="calc_margem_res"):
            if soma <= 1:
                st.warning(
                    f"A soma das chances deu {pct(soma)}, que é 100% ou menos. Confira se você copiou "
                    "a odd de **todos** os resultados da mesma aposta."
                )
                return
            margem = 1 - 1 / soma
            st.markdown(sem_formula(
                f"Transformando cada odd em chance (1 dividido pela odd): {partes} = **{pct(soma)}**. "
                f"Se as odds fossem justas, a soma daria exatamente 100%. A sobra de {pct(soma - 1)} é o "
                f"\"pedágio\" da casa: ela fica com cerca de **{pct(margem)}** de tudo o que é apostado."
            ))
            valor_pct = round(min(max(margem * 100, 0.0), 30.0), 1)
            st.button(f"Usar {valor_pct:.1f}% no simulador".replace(".", ","),
                      icon=":material/arrow_upward:", on_click=usar_margem_calculada, args=(valor_pct,))


def pagina_simulador():
    st.markdown("## Simulador de apostas")
    st.markdown(
        '<p class="intro-sim">Conte como você aposta (ou imagina apostar). O simulador repete esse jeito '
        "de apostar 2.000 vezes e compara com guardar e investir o mesmo dinheiro.</p>",
        unsafe_allow_html=True,
    )
    st.session_state.setdefault("margem_pct", 7.0)

    with st.form("form_simulador"):
        st.markdown('<div class="rotulo-secao">Como você aposta</div>', unsafe_allow_html=True)
        # A pessoa completa uma frase: "Eu aposto R$ 20, 3 vezes por semana, durante 3 anos."
        with st.container(key="frase_sim", horizontal=True, vertical_alignment="center", gap=None):
            st.markdown("Eu aposto R$", width="content")
            valor = st.number_input("Valor de cada aposta (R$)", label_visibility="collapsed",
                                    min_value=1.0, value=20.0, step=5.0, format="%.2f", width=115)
            st.markdown("por vez,", width="content")
            quantidade = st.number_input("Quantas vezes", label_visibility="collapsed",
                                         min_value=1, max_value=200, value=3, step=1, width=80)
            st.markdown("vezes por", width="content")
            frequencia = st.selectbox("Frequência", ["semana", "dia", "mês"], label_visibility="collapsed",
                                      width=112)
            st.markdown(", durante", width="content")
            anos = st.number_input("Anos", label_visibility="collapsed", min_value=1, max_value=30,
                                   value=3, step=1, width=80)
            st.markdown("anos.", width="content")

        st.markdown('<div class="rotulo-secao" style="margin-top:.4rem">Sobre as apostas</div>',
                    unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        odd = c1.number_input("Odd média das apostas", min_value=1.01, value=2.00, step=0.10, format="%.2f",
                              help="É o número que o site mostra ao lado de cada resultado. Por exemplo: "
                                   "com odd 2,00, se você aposta R$ 10 e acerta, recebe R$ 20 "
                                   "(seus R$ 10 de volta + R$ 10 de lucro).")
        margem = c2.slider("Margem da casa (%)", min_value=0.0, max_value=30.0, step=0.1, key="margem_pct",
                           help="É a parte de cada aposta que fica com a casa. Por exemplo: num cara ou coroa, "
                                "o justo seria pagar odd 2,00 para cada lado. Se a casa paga 1,90, ela fica "
                                "com cerca de 5% de tudo o que é apostado. Não sabe? Use a calculadora "
                                "logo abaixo do botão Simular.") / 100
        taxa = c3.slider("Rendimento se investisse (% ao ano)", min_value=0.0,
                         max_value=20.0, value=10.0, step=0.5,
                         help="Quanto o dinheiro renderia por ano se você o guardasse em vez de apostar. "
                              "Por exemplo: com 10% ao ano, R$ 100 viram R$ 110 depois de um ano.") / 100
        enviar = st.form_submit_button("Simular", type="primary", width="stretch")

    calculadora_margem()

    if enviar:
        parametros = Parametros(
            valor_aposta=float(valor), quantidade=int(quantidade), frequencia=frequencia,
            anos=int(anos), odd_media=float(odd), margem_casa=float(margem),
            taxa_investimento=float(taxa),
        )
        erros = validar(parametros)
        if erros:
            for e in erros:
                st.error(e)
            return
        with st.spinner("Rodando 2.000 simulações…"):
            st.session_state.resultado_simulacao = simular(parametros)

    r = st.session_state.resultado_simulacao
    if r is None:
        return

    s = r.resumo
    st.markdown(
        '<div class="cartoes">'
        + cartao("Total apostado", brl(s["total_apostado"]), f'{s["numero_de_apostas"]:,} apostas'.replace(",", "."))
        + cartao("Resultado típico", brl(s["resultado_mediano"]), "metade das simulações ficou abaixo", destaque=True)
        + cartao("Chance de sair no lucro", pct(s["chance_terminar_no_lucro"]), "ao fim do período")
        + cartao("Se tivesse investido", brl(s["saldo_investindo"]), f'rendimento de {brl(s["rendimento_investindo"])}')
        + "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("#### Quanto dinheiro você teria ao longo do tempo")
    legenda_trajetorias(r)
    st.plotly_chart(grafico_trajetorias(r), width="stretch", config={"displayModeBar": False})

    st.markdown(
        f'<div class="caixa-explicacao">'
        "A odd " + f'{r.parametros.odd_media:.2f}'.replace('.', ',') + f' dá a impressão de uma chance de '
        f'<b>{pct(s["chance_implicita"])}</b>, mas, descontando a margem da casa, a chance real fica em '
        f'<b>{pct(s["chance_real"])}</b>. Parece pouco, mas se repete em cada aposta: em média, você perde '
        f'<b>{brl(s["perda_esperada"])}</b> ao longo do período.'
        f"</div>",
        unsafe_allow_html=True,
    )

    equivalencias(s["perda_esperada"], s["total_apostado"])

    cem_pessoas(r)

    with st.expander("Como o simulador faz as contas"):
        st.markdown(
            "- Ele imagina que você aposta sempre o mesmo valor, na mesma odd e com a mesma frequência.\n"
            "- Cada aposta é sorteada no computador, respeitando a chance real de ganhar. "
            "Isso é repetido 2.000 vezes, como se 2.000 pessoas apostassem do mesmo jeito.\n"
            "- O dinheiro ganho não é apostado de novo.\n"
            "- No investimento, o dinheiro rende sempre a mesma taxa, sem impostos.\n"
            "- É uma ferramenta para aprender: mostra o que costuma acontecer, mas não adivinha o seu futuro."
        )

    st.button(f"Pedir para a {config.NOME_ASSISTENTE} explicar meu resultado", icon=":material/chat_bubble_outline:", type="primary",
              on_click=explicar_simulacao_no_chat, width="stretch")


# ===========================================================================
# PÁGINA 3 — MITO OU VERDADE
# ===========================================================================
def responder_quiz(escolha_verdade: bool):
    item = QUIZ[st.session_state.quiz_idx]
    acertou = escolha_verdade == item["verdade"]
    st.session_state.quiz_resposta = acertou
    if acertou:
        st.session_state.quiz_acertos += 1


def proxima_quiz():
    st.session_state.quiz_idx += 1
    st.session_state.quiz_resposta = None


def recomecar_quiz():
    st.session_state.quiz_idx = 0
    st.session_state.quiz_acertos = 0
    st.session_state.quiz_resposta = None


def perguntar_do_quiz(pergunta: str):
    st.session_state.pergunta_pendente = pergunta
    st.session_state.pagina = CONVERSAR


def pagina_quiz():
    st.markdown("## Mito ou verdade?")
    st.write("Teste o que você sabe sobre apostas. Leia a frase e escolha se é **mito** ou **verdade**.")

    total = len(QUIZ)
    i = st.session_state.quiz_idx

    # Fim do quiz
    if i >= total:
        acertos = st.session_state.quiz_acertos
        if acertos == total:
            msg = "Você acertou tudo! Parabéns!"
        elif acertos >= total * 0.7:
            msg = "Muito bem! Você já conhece bastante sobre o assunto."
        elif acertos >= total * 0.4:
            msg = "Bom começo! Algumas dessas ideias enganam muita gente."
        else:
            msg = "Essas ideias enganam muita gente. Que tal conversar com a Betinha para entender melhor?"
        st.markdown(f'<div class="quiz-card"><div class="num">Resultado</div>'
                    f'<div class="frase">Você acertou {acertos} de {total}.</div>'
                    f'<p style="margin:.6rem 0 0">{html.escape(msg)}</p></div>', unsafe_allow_html=True)
        st.button("Jogar de novo", icon=":material/replay:", on_click=recomecar_quiz, type="primary", width="stretch")
        return

    item = QUIZ[i]
    st.progress(i / total, text=f"Pergunta {i + 1} de {total}  ·  acertos: {st.session_state.quiz_acertos}")
    st.markdown(f'<div class="quiz-card"><div class="num">Pergunta {i + 1}</div>'
                f'<div class="frase">“{html.escape(item["frase"])}”</div></div>', unsafe_allow_html=True)

    resposta = st.session_state.quiz_resposta
    if resposta is None:
        c1, c2 = st.columns(2)
        c1.button("Mito", icon=":material/close:", on_click=responder_quiz, args=(False,), width="stretch", key=f"mito_{i}")
        c2.button("Verdade", icon=":material/check:", on_click=responder_quiz, args=(True,), width="stretch", key=f"verdade_{i}")
        return

    certo = "É verdade." if item["verdade"] else "É mito."
    titulo = f"Você acertou! {certo}" if resposta else f"Não foi dessa vez. {certo}"
    classe = "certo" if resposta else "errado"
    st.markdown(f'<div class="quiz-feedback {classe}"><b>{titulo}</b><br>{html.escape(item["explicacao"])}</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.button("Perguntar mais à Betinha", icon=":material/chat_bubble_outline:", on_click=perguntar_do_quiz, args=(item["pergunta_betinha"],),
              width="stretch", key=f"perg_{i}")
    rotulo = "Próxima" if i + 1 < total else "Ver meu resultado"
    c2.button(rotulo, icon=":material/arrow_forward:", on_click=proxima_quiz, type="primary", width="stretch", key=f"prox_{i}")


# ===========================================================================
# PÁGINA 4 — SOBRE
# ===========================================================================
def pagina_sobre():
    st.markdown(f"## Sobre a {config.NOME_ASSISTENTE}")
    st.markdown(
        f"A {config.NOME_ASSISTENTE} explica, em linguagem simples, como funcionam as apostas esportivas, "
        "seus riscos e o custo delas no longo prazo. Ela responde **apenas com base em uma base "
        "de conhecimento** pesquisada e revisada pelo grupo, a partir de fontes como órgãos "
        "públicos, estudos acadêmicos e organismos internacionais.\n\n"
        "**O que ela não faz:** não recomenda apostas, não dá palpites nem estratégias para ganhar, "
        "e não substitui orientação financeira, jurídica ou psicológica. É uma ferramenta "
        "educativa feita por estudantes de Economia da FGV EESP.\n\n"
        "**Precisa de ajuda?** Se apostar está trazendo prejuízo ou sofrimento, pergunte à "
        f"{config.NOME_ASSISTENTE} onde buscar apoio."
    )



# ===========================================================================
# PÁGINA — GLOSSÁRIO
# ===========================================================================
def _sem_acento(t: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(c) != "Mn")


def pagina_glossario():
    st.markdown("## Glossário")
    st.markdown(
        '<p class="intro-sim">Os termos que aparecem nos sites de apostas e nas conversas com a Betinha, '
        "explicados em uma frase. Toque em um termo para abrir.</p>",
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([2, 1.2])
    busca = c1.text_input("Procurar um termo", placeholder="Procurar um termo, por exemplo: odd",
                          label_visibility="collapsed", icon=":material/search:", key="glos_busca")
    tema = c2.selectbox("Tema", ["Todos os temas"] + TEMAS, label_visibility="collapsed", key="glos_tema")
    alvo = _sem_acento(busca.strip())
    achados = [(i, g) for i, g in enumerate(GLOSSARIO)
               if (tema == "Todos os temas" or g["tema"] == tema)
               and (not alvo or alvo in _sem_acento(g["termo"] + " " + g["definicao"]))]
    if not achados:
        st.info("Não encontrei esse termo aqui. Você pode perguntar direto para a Betinha.")
        if busca.strip():
            st.button(f"Perguntar à Betinha: o que é \"{busca.strip()}\"?", icon=":material/chat_bubble_outline:",
                      on_click=perguntar_do_quiz, args=(f"O que é {busca.strip()} nas apostas?",))
        return
    for t in TEMAS:
        do_tema = [(i, g) for i, g in achados if g["tema"] == t]
        if not do_tema:
            continue
        st.markdown(f'<div class="glos-tema">{html.escape(t)}</div>', unsafe_allow_html=True)
        for i, g in do_tema:
            with st.expander(g["termo"], expanded=bool(alvo)):
                st.markdown(sem_formula(g["definicao"]))
                if g["exemplo"]:
                    st.markdown(f'<div class="glos-exemplo"><b>Exemplo:</b> '
                                f'{html.escape(g["exemplo"]).replace("$", "&#36;")}</div>', unsafe_allow_html=True)
                st.button("Perguntar mais à Betinha", icon=":material/chat_bubble_outline:", key=f"glos_{i}",
                          type="tertiary", on_click=perguntar_do_quiz, args=(g["pergunta_betinha"],))


# ---------------------------------------------------------------------------
# Monta a tela: menu lateral (se aberto) + página escolhida
# ---------------------------------------------------------------------------
if st.session_state.menu_aberto:
    desenhar_menu()
area = st.container()

# Depois que a conversa começa, a caixa de digitação fica presa no rodapé
digitada = None
conversa_comecou = bool(st.session_state.mensagens or st.session_state.pergunta_pendente)
if st.session_state.pagina == CONVERSAR and conversa_comecou and buscador is not None:
    digitada = st.chat_input("Escreva aqui a sua pergunta sobre apostas…")

with area:
    {
        CONVERSAR: lambda: pagina_chat(digitada),
        SIMULADOR: pagina_simulador,
        QUIZ_PAG: pagina_quiz,
        GLOSSARIO_PAG: pagina_glossario,
    }.get(st.session_state.pagina, pagina_sobre)()
