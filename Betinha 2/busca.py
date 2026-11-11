"""
Leitura e busca na base de conhecimento.

Como funciona, em linguagem simples:
1. Cada arquivo .md da pasta base_conhecimento/ é um TEMA.
2. Dentro dele, cada bloco que começa com "## " é UMA pergunta com sua resposta.
   Esse bloco é a menor unidade de informação (chamamos de "trecho").
3. Quando o usuário pergunta algo:
   - se a base é pequena, mandamos TODOS os trechos para o Gemini;
   - se é grande, transformamos a pergunta em um vetor (embedding) e pegamos
     os trechos mais parecidos com ela.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from google.genai import types


@dataclass
class Trecho:
    tema: str
    pergunta: str
    texto: str      # bloco completo (pergunta + variações + resposta + fonte)
    fonte: str
    arquivo: str


# ---------------------------------------------------------------------------
# Leitura dos arquivos
# ---------------------------------------------------------------------------
def carregar_base(pasta: Path) -> list[Trecho]:
    """Lê todos os .md da pasta e quebra cada um em trechos (um por '## ')."""
    trechos: list[Trecho] = []
    if not pasta.exists():
        return trechos

    for arquivo in sorted(pasta.glob("*.md")):
        # Arquivos que começam com "_" são modelos/guias e não entram na base
        if arquivo.name.startswith("_"):
            continue

        conteudo = arquivo.read_text(encoding="utf-8")

        # Nome do tema = primeira linha "# ..." (ou o nome do arquivo)
        achou_tema = re.search(r"^#\s+(?:Tema:\s*)?(.+)$", conteudo, flags=re.M)
        tema = achou_tema.group(1).strip() if achou_tema else arquivo.stem

        # Quebra nos títulos de nível 2 ("## ")
        blocos = re.split(r"^##\s+", conteudo, flags=re.M)[1:]
        for bloco in blocos:
            bloco = bloco.strip()
            if not bloco:
                continue
            primeira_linha = bloco.splitlines()[0]
            pergunta = re.sub(r"^Pergunta:\s*", "", primeira_linha).strip()

            achou_fonte = re.search(r"\*\*Fontes?:\*\*\s*(.+)", bloco)
            fonte = achou_fonte.group(1).strip() if achou_fonte else ""

            trechos.append(
                Trecho(
                    tema=tema,
                    pergunta=pergunta,
                    texto=f"[Tema: {tema}]\n## {bloco}",
                    fonte=fonte,
                    arquivo=arquivo.name,
                )
            )
    return trechos


# ---------------------------------------------------------------------------
# Busca
# ---------------------------------------------------------------------------
class BuscadorBase:
    """Escolhe quais trechos da base vão junto com cada pergunta."""

    def __init__(self, cliente, trechos: list[Trecho], modelo_embedding: str,
                 pasta_cache: Path, limite_base_completa: int):
        self.cliente = cliente
        self.trechos = trechos
        self.modelo_embedding = modelo_embedding
        self.pasta_cache = pasta_cache
        self.aviso = ""
        self.matriz: np.ndarray | None = None

        tamanho_total = sum(len(t.texto) for t in trechos)
        self.usar_base_inteira = tamanho_total <= limite_base_completa

        if trechos and not self.usar_base_inteira:
            try:
                self._indexar()
            except Exception as erro:  # sem internet, cota estourada etc.
                self.usar_base_inteira = True
                self.aviso = (
                    "Não consegui criar o índice de busca; usando a base inteira. "
                    f"Detalhe técnico: {erro}"
                )

    @property
    def modo(self) -> str:
        return "base inteira" if self.usar_base_inteira else "busca por similaridade"

    # -- embeddings -----------------------------------------------------------
    def _embed(self, textos: list[str], tipo: str) -> np.ndarray:
        vetores = []
        for i in range(0, len(textos), 50):  # a API aceita lotes
            resposta = self.cliente.models.embed_content(
                model=self.modelo_embedding,
                contents=textos[i:i + 50],
                config=types.EmbedContentConfig(task_type=tipo),
            )
            vetores.extend(e.values for e in resposta.embeddings)
        matriz = np.array(vetores, dtype=np.float32)
        # Normaliza para que o produto escalar seja a similaridade de cosseno
        return matriz / np.linalg.norm(matriz, axis=1, keepdims=True)

    def _indexar(self) -> None:
        """Calcula (ou reaproveita do cache) os vetores de todos os trechos."""
        textos = [t.texto for t in self.trechos]
        impressao = hashlib.sha256(
            (self.modelo_embedding + "\n".join(textos)).encode("utf-8")
        ).hexdigest()[:16]
        arquivo_cache = self.pasta_cache / f"indice_{impressao}.npy"

        if arquivo_cache.exists():
            self.matriz = np.load(arquivo_cache)
            return

        self.matriz = self._embed(textos, "RETRIEVAL_DOCUMENT")
        self.pasta_cache.mkdir(exist_ok=True)
        np.save(arquivo_cache, self.matriz)

    def buscar(self, consulta: str, quantidade: int) -> list[Trecho]:
        if self.usar_base_inteira or self.matriz is None:
            return self.trechos
        try:
            vetor = self._embed([consulta], "RETRIEVAL_QUERY")[0]
        except Exception:
            return self.trechos
        similaridades = self.matriz @ vetor
        melhores = np.argsort(similaridades)[::-1][:quantidade]
        return [self.trechos[i] for i in melhores]
