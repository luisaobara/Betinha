"""
Betinha — assistente de IA sobre apostas esportivas + simulador.

Como rodar (no terminal do VS Code, dentro da pasta do projeto):
    streamlit run app.py
"""

from __future__ import annotations

import base64
import html
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st

import config
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

PAGINAS = ["💬  Conversar", "📊  Simulador", "ℹ️  Sobre"]

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
st.markdown(
    f"<style>{(config.PASTA_PROJETO / 'estilo.css').read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True,
)

# Estado da sessão (o que o app "lembra" enquanto a aba está aberta)
st.session_state.setdefault("mensagens", [])
st.session_state.setdefault("pergunta_pendente", None)
st.session_state.setdefault("resultado_simulacao", None)
st.session_state.setdefault("pagina", PAGINAS[0])


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
    st.session_state.pagina = PAGINAS[0]


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
# Barra de navegação no topo (sempre visível, não dá para fechar sem querer)
# ---------------------------------------------------------------------------
with st.container(key="barra_topo"):
    col_marca, col_nav = st.columns([1, 2], vertical_alignment="center")
    col_marca.markdown(
        f'<div class="marca">{imagem_html(30, "rosto-marca")}'
        f"{html.escape(config.NOME_ASSISTENTE)}</div>",
        unsafe_allow_html=True,
    )
    col_nav.radio("Navegação", PAGINAS, key="pagina", horizontal=True,
                  label_visibility="collapsed")

# Sem chave da API não dá para conversar
if not config.GEMINI_API_KEY:
    st.error(
        "Não encontrei a **GEMINI_API_KEY**. Crie um arquivo `.env` na pasta do projeto "
        "com a linha `GEMINI_API_KEY=sua_chave_aqui` e reinicie o app."
    )
    st.stop()

cliente = obter_cliente(config.GEMINI_API_KEY)
buscador = obter_buscador(config.GEMINI_API_KEY, assinatura_da_base())


# ===========================================================================
# PÁGINA 1 — CHAT
# ===========================================================================
def mostrar_mensagem(papel: str, texto: str) -> None:
    """Pessoa: só o balão (sem ícone). Betinha: com o rostinho dela."""
    if papel == "user":
        seguro = html.escape(texto).replace("$", "&#36;").replace("\n", "<br>")
        st.markdown(f'<div class="linha-usuario"><div class="balao-usuario">{seguro}</div></div>',
                    unsafe_allow_html=True)
    else:
        with st.chat_message("assistant", avatar=config.AVATAR_ASSISTENTE):
            st.markdown(sem_formula(texto))


def pagina_chat():
    if not buscador.trechos:
        st.warning(
            "A base de conhecimento está vazia. Coloque arquivos `.md` na pasta "
            "`base_conhecimento/` (veja o modelo `_MODELO.md`)."
        )
    if buscador.aviso:
        st.info(buscador.aviso)

    # Lê a caixa de digitação ANTES de desenhar a tela, para a tela de
    # boas-vindas sumir logo na primeira pergunta
    digitada = st.chat_input("Pergunte algo sobre apostas…")

    # Tela de boas-vindas (só quando a conversa está vazia)
    if not st.session_state.mensagens and not st.session_state.pergunta_pendente and not digitada:
        st.markdown(
            f'<div class="boas-vindas">{imagem_html(96, "rosto-grande")}'
            f"<h1>Oi! Eu sou a {html.escape(config.NOME_ASSISTENTE)}.</h1>"
            f"<p>{html.escape(config.SUBTITULO)}</p></div>",
            unsafe_allow_html=True,
        )
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
    for m in st.session_state.mensagens:
        mostrar_mensagem(m["role"], m["content"])

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
        with st.spinner("Pensando…"):
            fluxo = responder(cliente, config.MODELO_CHAT, instrucoes, historico, config.TEMPERATURA)
            primeiro = next(fluxo, "")

        texto_original = []  # guarda a resposta sem os escapes de "$"

        def continuar():
            for pedaco in [primeiro, *fluxo]:
                texto_original.append(pedaco)
                yield sem_formula(pedaco)

        st.write_stream(continuar())

    st.session_state.mensagens.append({"role": "assistant", "content": "".join(texto_original)})


# ===========================================================================
# PÁGINA 2 — SIMULADOR
# ===========================================================================
def cartao(rotulo: str, valor: str, nota: str = "", destaque: bool = False) -> str:
    classe = "cartao destaque" if destaque else "cartao"
    nota_html = f'<div class="nota">{nota}</div>' if nota else ""
    return (f'<div class="{classe}"><div class="rotulo">{rotulo}</div>'
            f'<div class="valor">{valor}</div>{nota_html}</div>')


def grafico_trajetorias(r) -> go.Figure:
    x = r.eixo_tempo_anos
    fig = go.Figure()

    def faixa(baixo, alto, opacidade, nome):
        fig.add_trace(go.Scatter(x=x, y=alto, mode="lines", line=dict(width=0),
                                 showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=x, y=baixo, mode="lines", line=dict(width=0),
                                 fill="tonexty", fillcolor=f"rgba(208,87,47,{opacidade})",
                                 name=nome, hoverinfo="skip"))

    faixa(r.percentis[5], r.percentis[95], 0.12, "Apostando: 90% dos casos")
    faixa(r.percentis[25], r.percentis[75], 0.25, "Apostando: 50% dos casos")
    fig.add_trace(go.Scatter(x=x, y=r.percentis[50], mode="lines", name="Apostando: caso típico",
                             line=dict(color=COR_APOSTAS, width=2),
                             hovertemplate="%{y:,.0f}<extra>Apostando (típico)</extra>"))
    fig.add_trace(go.Scatter(x=x, y=r.investimento, mode="lines", name="Investindo o mesmo valor",
                             line=dict(color=COR_INVESTIMENTO, width=2),
                             hovertemplate="%{y:,.0f}<extra>Investindo</extra>"))
    fig.add_trace(go.Scatter(x=x, y=r.aportado, mode="lines", name="Dinheiro que você colocou",
                             line=dict(color=COR_NEUTRA, width=1.5, dash="dash"),
                             hovertemplate="%{y:,.0f}<extra>Você colocou</extra>"))

    fig.update_layout(
        height=420, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font=dict(family="Inter, sans-serif", color="#22201C", size=13),
        hovermode="x unified", separators=",.",
        legend=dict(orientation="h", yanchor="top", y=-0.15, x=0),
        xaxis=dict(title="Anos", showgrid=False, linecolor="#E2DDD2"),
        yaxis=dict(title="Quanto você teria (R$)", gridcolor="#EFECE4", zeroline=False,
                   tickprefix="R$ ", tickformat=",.0f"),
    )
    return fig


def grafico_distribuicao(r) -> go.Figure:
    finais = r.resultados_finais
    fig = go.Figure(go.Histogram(
        x=finais, nbinsx=40, marker=dict(color=COR_APOSTAS, line=dict(color="#FFFFFF", width=1)),
        hovertemplate="Resultado entre %{x}<br>%{y} simulações<extra></extra>",
    ))
    fig.add_vline(x=0, line=dict(color="#22201C", width=1.5, dash="dot"),
                  annotation_text="empatar", annotation_position="top")
    fig.update_layout(
        height=300, margin=dict(l=10, r=10, t=30, b=10), bargap=0.02,
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF", separators=",.",
        font=dict(family="Inter, sans-serif", color="#22201C", size=13),
        xaxis=dict(title="Lucro ou prejuízo no fim do período (R$)", tickprefix="R$ ",
                   tickformat=",.0f", showgrid=False),
        yaxis=dict(title="Nº de simulações", gridcolor="#EFECE4"),
    )
    return fig


def pagina_simulador():
    st.markdown("## Simulador de apostas")
    st.write(
        "Informe como você aposta (ou imagina apostar). O simulador repete esse padrão "
        "milhares de vezes no computador e mostra o que costuma acontecer com o seu dinheiro, "
        "comparando com investir o mesmo valor."
    )

    with st.form("form_simulador"):
        c1, c2 = st.columns(2)
        valor = c1.number_input("Valor de cada aposta (R$)", min_value=1.0, value=20.0, step=5.0)
        quantidade = c2.number_input("Quantas apostas", min_value=1, max_value=200, value=3, step=1)
        frequencia = c1.selectbox("Com que frequência", ["semana", "dia", "mês"],
                                  format_func=lambda f: f"por {f}")
        anos = c2.slider("Por quantos anos", min_value=1, max_value=10, value=3)
        odd = c1.number_input("Odd média das apostas", min_value=1.01, value=2.00, step=0.10,
                              help="O número que a casa mostra. Odd 2,00 paga o dobro do que você apostou.")
        margem = c2.slider("Margem da casa (%)", min_value=0.0, max_value=30.0, value=7.0, step=0.5,
                           help="Quanto a casa fica, em média, de cada aposta. "
                                "Use o valor definido na base de conhecimento do grupo.") / 100
        taxa = st.slider("Rendimento do investimento alternativo (% ao ano)", min_value=0.0,
                         max_value=20.0, value=10.0, step=0.5,
                         help="Taxa usada para comparar. Ajuste para a taxa de referência atual "
                              "(por exemplo, a de um título público).") / 100
        enviar = st.form_submit_button("Simular", type="primary", width="stretch")

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

    st.markdown("#### Como o seu dinheiro evolui")
    st.plotly_chart(grafico_trajetorias(r), width="stretch", config={"displayModeBar": False})

    st.markdown(
        f'<div class="caixa-explicacao">'
        "A odd " + f'{r.parametros.odd_media:.2f}'.replace('.', ',') + f' dá a impressão de uma chance de '
        f'<b>{pct(s["chance_implicita"])}</b>, mas, descontando a margem da casa, a chance real fica em '
        f'<b>{pct(s["chance_real"])}</b>. Parece pouco, mas se repete em cada aposta: em média, você perde '
        f'<b>{brl(s["perda_esperada"])}</b> ao longo do período. Em 90% das simulações o resultado ficou '
        f'entre <b>{brl(s["pior_cenario_5"])}</b> e <b>{brl(s["melhor_cenario_95"])}</b>.'
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("#### Onde as simulações terminaram")
    st.plotly_chart(grafico_distribuicao(r), width="stretch", config={"displayModeBar": False})

    with st.expander("Ver tabela com os números"):
        passo = max(1, len(r.eixo_tempo_anos) // 10)
        indices = np.arange(0, len(r.eixo_tempo_anos), passo)
        st.dataframe(
            {
                "Ano": [f"{a:.1f}".replace(".", ",") for a in r.eixo_tempo_anos[indices]],
                "Você colocou": [brl(v) for v in r.aportado[indices]],
                "Apostando (típico)": [brl(v) for v in r.percentis[50][indices]],
                "Apostando (pior 5%)": [brl(v) for v in r.percentis[5][indices]],
                "Apostando (melhor 5%)": [brl(v) for v in r.percentis[95][indices]],
                "Investindo": [brl(v) for v in r.investimento[indices]],
            },
            hide_index=True, width="stretch",
        )

    with st.expander("Hipóteses e limitações do simulador"):
        st.markdown(
            "- Você aposta sempre o mesmo valor, na mesma odd média, com a frequência escolhida.\n"
            "- Ganhos não são reapostados; cada aposta é independente das outras.\n"
            "- A chance real de ganhar é (1 ÷ odd) × (1 − margem da casa).\n"
            "- O investimento rende uma taxa fixa, sem impostos e sem taxas.\n"
            "- É um modelo educativo: mostra tendências, não prevê o seu futuro."
        )

    st.button(f"💬  Pedir para a {config.NOME_ASSISTENTE} explicar meu resultado", type="primary",
              on_click=explicar_simulacao_no_chat, width="stretch")


# ===========================================================================
# PÁGINA 3 — SOBRE
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
    st.caption(
        f"Base carregada: {len(buscador.trechos)} perguntas · modo: {buscador.modo} · "
        f"modelo: {config.MODELO_CHAT}"
    )


# ---------------------------------------------------------------------------
if st.session_state.pagina == PAGINAS[0]:
    pagina_chat()
elif st.session_state.pagina == PAGINAS[1]:
    pagina_simulador()
else:
    pagina_sobre()
