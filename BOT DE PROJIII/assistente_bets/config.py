"""
Configurações gerais do projeto.

Tudo que o grupo pode querer mudar sem mexer na lógica fica aqui:
nome do assistente, modelos do Gemini, tamanho das respostas, etc.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Pasta onde este arquivo está (a raiz do projeto)
PASTA_PROJETO = Path(__file__).resolve().parent

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

# Se a base inteira tiver até este número de caracteres, ela é enviada
# INTEIRA para o modelo a cada pergunta (mais preciso para bases pequenas).
# Acima disso, o app faz uma busca e envia só os trechos mais relevantes.
LIMITE_BASE_COMPLETA = 60_000

# Quantos trechos da base entram em cada resposta quando há busca
TRECHOS_POR_PERGUNTA = 6

# Quantas mensagens anteriores da conversa o modelo "lembra"
MENSAGENS_DE_HISTORICO = 10
