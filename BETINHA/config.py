"""
Configurações gerais do projeto.

Tudo que o grupo pode querer mudar sem mexer na lógica fica aqui:
nome do assistente, modelos do Gemini, tamanho das respostas, etc.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Pasta onde este arquivo está (a raiz do projeto)
PASTA_PROJETO = Path(__file__).parent

# Lê o arquivo .env (onde fica a GEMINI_API_KEY)
load_dotenv(PASTA_PROJETO / ".env")

# ---------------------------------------------------------------------------
# Identidade
# ---------------------------------------------------------------------------
NOME_ASSISTENTE = "Betinha"
SUBTITULO = "Tire dúvidas sobre bets e simule quanto elas custam no longo prazo."

# Rosto da Betinha: coloque o desenho de vocês na pasta "imagens" com um destes
# nomes (o primeiro que existir é usado). Formato quadrado fica melhor.
_CANDIDATOS_AVATAR = ["betinha.png", "betinha.jpg", "betinha.jpeg", "betinha.webp"]
AVATAR_ASSISTENTE = next(
    (str(PASTA_PROJETO / "imagens" / n) for n in _CANDIDATOS_AVATAR
     if (PASTA_PROJETO / "imagens" / n).exists()),
    "🙂",  # usado só se não houver nenhuma imagem
)

# ---------------------------------------------------------------------------
# Gemini
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
if not GEMINI_API_KEY:
    # No Streamlit Community Cloud a chave fica em "Secrets" (não existe .env lá)
    try:
        import streamlit as st
        GEMINI_API_KEY = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
    except Exception:
        pass

# Modelo que escreve as respostas. Dá para trocar pelo .env (GEMINI_MODEL=...)
MODELO_CHAT = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

# Modelo que transforma textos em vetores para a busca na base
MODELO_EMBEDDING = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")

# Temperatura baixa = respostas mais fiéis à base e menos "criativas"
TEMPERATURA = 0.3

# ---------------------------------------------------------------------------
# Base de conhecimento
# ---------------------------------------------------------------------------
PASTA_BASE = PASTA_PROJETO / "base_conhecimento"
PASTA_CACHE = PASTA_PROJETO / ".cache"

# Se a base inteira tiver até este número de caracteres (umas 50 páginas de texto), ela é enviada
# INTEIRA para o modelo a cada pergunta (mais preciso para bases pequenas).
# Acima disso, o app faz uma busca e envia só os trechos mais relevantes.
LIMITE_BASE_COMPLETA = 150_000

# Quantos trechos da base entram em cada resposta quando há busca
TRECHOS_POR_PERGUNTA = 6

# Quantas mensagens anteriores da conversa o modelo "lembra"
MENSAGENS_DE_HISTORICO = 10

# ---------------------------------------------------------------------------
# "Isso equivale a..." (simulador): preços de referência COM FONTE.
# Atualizem os valores quando sair um dado novo.
# ---------------------------------------------------------------------------
EQUIVALENCIAS = [
    {"icone": "shopping_cart", "singular": "cesta básica", "plural": "cestas básicas", "valor": 922.51,
     "fonte": "DIEESE, custo da cesta básica em São Paulo, setembro de 2026"},
    {"icone": "propane_tank", "singular": "botijão de gás", "plural": "botijões de gás", "valor": 114.80,
     "fonte": "ANP, preço médio nacional do botijão de 13 kg, setembro de 2026"},
    {"icone": "payments", "singular": "salário mínimo", "plural": "salários mínimos", "valor": 1621.00,
     "fonte": "Decreto nº 12.797/2025 (salário mínimo de 2026)"},
]
