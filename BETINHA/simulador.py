"""
Simulador financeiro de apostas (Monte Carlo) + comparação com investimento.

Hipóteses do modelo (explicar no relatório técnico):
- O usuário aposta sempre o MESMO valor, na MESMA odd média, com a frequência
  informada. Ganhos não são reapostados (não há "efeito bola de neve").
- A odd já embute a margem da casa. A chance real de ganhar é
  p = (1 / odd) × (1 − margem). Com isso, o retorno esperado de cada aposta é
  exatamente −margem × valor apostado (a casa fica, em média, com a margem).
- Cada aposta é independente (Bernoulli). Somando as apostas de um período,
  o número de vitórias segue uma Binomial(n, p).
- O cenário "investir" aplica o mesmo valor, no início de cada período, a uma
  taxa anual fixa informada pelo usuário (juros compostos, sem imposto).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

PERIODOS_POR_ANO = {"semana": 52, "mês": 12}


@dataclass
class Parametros:
    valor_aposta: float          # R$ por aposta
    quantidade: int              # quantas apostas por "frequencia"
    frequencia: str              # "dia", "semana" ou "mês"
    anos: int                    # horizonte
    odd_media: float             # ex.: 2.0
    margem_casa: float           # ex.: 0.07 para 7%
    taxa_investimento: float     # ex.: 0.10 para 10% ao ano
    simulacoes: int = 2000
    semente: int | None = 42


@dataclass
class Resultado:
    parametros: Parametros
    periodo: str                          # "semana" ou "mês"
    eixo_tempo_anos: np.ndarray           # tempo de cada ponto, em anos
    aportado: np.ndarray                  # total colocado até cada ponto
    percentis: dict[int, np.ndarray]      # 5, 25, 50, 75, 95 -> saldo com apostas
    esperado: np.ndarray                  # saldo esperado com apostas (fórmula)
    investimento: np.ndarray              # saldo investindo o mesmo valor
    resultados_finais: np.ndarray         # lucro/prejuízo final de cada simulação
    resumo: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Fórmulas simples (também úteis para o chat explicar)
# ---------------------------------------------------------------------------
def probabilidade_implicita(odd: float) -> float:
    """Chance que a odd 'mostra': 1 / odd."""
    return 1.0 / odd


def probabilidade_real(odd: float, margem: float) -> float:
    """Chance real, descontando a margem da casa."""
    return (1.0 / odd) * (1.0 - margem)


def valor_esperado_por_aposta(valor: float, margem: float) -> float:
    """Em média, cada aposta devolve −margem × valor."""
    return -margem * valor


# ---------------------------------------------------------------------------
# Simulação
# ---------------------------------------------------------------------------
def _converter_frequencia(p: Parametros) -> tuple[str, int]:
    """Converte a frequência escolhida em (período da simulação, apostas por período)."""
    if p.frequencia == "dia":
        return "semana", p.quantidade * 7
    if p.frequencia == "semana":
        return "semana", p.quantidade
    return "mês", p.quantidade


def validar(p: Parametros) -> list[str]:
    erros = []
    if p.valor_aposta <= 0:
        erros.append("O valor da aposta precisa ser maior que zero.")
    if p.quantidade < 1:
        erros.append("A quantidade de apostas precisa ser pelo menos 1.")
    if p.odd_media <= 1:
        erros.append("A odd precisa ser maior que 1,00.")
    if not 0 <= p.margem_casa < 1:
        erros.append("A margem da casa precisa estar entre 0% e 100%.")
    if p.anos < 1:
        erros.append("O horizonte precisa ser de pelo menos 1 ano.")
    return erros


def simular(p: Parametros) -> Resultado:
    periodo, apostas_por_periodo = _converter_frequencia(p)
    periodos_ano = PERIODOS_POR_ANO[periodo]
    n_periodos = p.anos * periodos_ano

    chance = probabilidade_real(p.odd_media, p.margem_casa)
    gasto_por_periodo = apostas_por_periodo * p.valor_aposta

    # Sorteio: quantas apostas ganhou em cada período de cada simulação
    gerador = np.random.default_rng(p.semente)
    vitorias = gerador.binomial(apostas_por_periodo, chance,
                                size=(p.simulacoes, n_periodos))
    lucro_periodo = vitorias * p.valor_aposta * p.odd_media - gasto_por_periodo

    # Lucro acumulado ao longo do tempo (começa em zero)
    acumulado = np.zeros((p.simulacoes, n_periodos + 1))
    acumulado[:, 1:] = np.cumsum(lucro_periodo, axis=1)

    t = np.arange(n_periodos + 1)
    aportado = gasto_por_periodo * t

    # "Saldo" = quanto dinheiro a pessoa teria: o que colocou + lucro/prejuízo
    saldo_apostas = aportado + acumulado
    percentis = {q: np.percentile(saldo_apostas, q, axis=0) for q in (5, 25, 50, 75, 95)}
    esperado = aportado * (1 - p.margem_casa)

    # Cenário alternativo: investir o mesmo valor no início de cada período
    taxa_periodo = (1 + p.taxa_investimento) ** (1 / periodos_ano) - 1
    if taxa_periodo > 0:
        investimento = gasto_por_periodo * (((1 + taxa_periodo) ** t - 1) / taxa_periodo) * (1 + taxa_periodo)
    else:
        investimento = aportado.astype(float)

    finais = acumulado[:, -1]
    total_aportado = float(aportado[-1])
    total_apostas = apostas_por_periodo * n_periodos

    resumo = {
        "total_apostado": total_aportado,
        "numero_de_apostas": int(total_apostas),
        "chance_implicita": probabilidade_implicita(p.odd_media),
        "chance_real": chance,
        "perda_esperada": float(p.margem_casa * total_aportado),
        "resultado_mediano": float(np.median(finais)),
        "resultado_medio_simulado": float(np.mean(finais)),
        "pior_cenario_5": float(np.percentile(finais, 5)),
        "melhor_cenario_95": float(np.percentile(finais, 95)),
        "chance_terminar_no_lucro": float(np.mean(finais > 0)),
        "saldo_investindo": float(investimento[-1]),
        "rendimento_investindo": float(investimento[-1] - total_aportado),
    }
    # Diferença entre investir e o resultado típico (mediano) de apostar
    resumo["diferenca_investir_vs_apostar"] = (
        resumo["saldo_investindo"] - (total_aportado + resumo["resultado_mediano"])
    )

    return Resultado(
        parametros=p,
        periodo=periodo,
        eixo_tempo_anos=t / periodos_ano,
        aportado=aportado,
        percentis=percentis,
        esperado=esperado,
        investimento=investimento,
        resultados_finais=finais,
        resumo=resumo,
    )


# ---------------------------------------------------------------------------
# Texto-resumo (vai para o chat, para o assistente poder explicar o resultado)
# ---------------------------------------------------------------------------
def brl(valor: float) -> str:
    texto = f"{abs(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"-R$ {texto}" if valor < 0 else f"R$ {texto}"


def pct(valor: float) -> str:
    return f"{valor * 100:.1f}%".replace(".", ",")


def resumo_em_texto(r: Resultado) -> str:
    p, s = r.parametros, r.resumo
    odd_txt = f"{p.odd_media:.2f}".replace(".", ",")
    return (
        f"Parâmetros: {p.quantidade} aposta(s) por {p.frequencia} de {brl(p.valor_aposta)}, "
        f"odd média {odd_txt}, margem da casa {pct(p.margem_casa)}, "
        f"horizonte de {p.anos} ano(s), taxa do investimento {pct(p.taxa_investimento)} ao ano, "
        f"{p.simulacoes} simulações.\n"
        f"Total apostado: {brl(s['total_apostado'])} em {s['numero_de_apostas']} apostas.\n"
        f"Chance que a odd mostra: {pct(s['chance_implicita'])}; chance real estimada: {pct(s['chance_real'])}.\n"
        f"Perda esperada (fórmula): {brl(-s['perda_esperada'])}.\n"
        f"Resultado mediano nas simulações: {brl(s['resultado_mediano'])}.\n"
        f"Faixa provável (5% a 95% das simulações): de {brl(s['pior_cenario_5'])} a {brl(s['melhor_cenario_95'])}.\n"
        f"Chance de terminar no lucro: {pct(s['chance_terminar_no_lucro'])}.\n"
        f"Se investisse o mesmo dinheiro: saldo de {brl(s['saldo_investindo'])} "
        f"(rendimento de {brl(s['rendimento_investindo'])}).\n"
        f"Diferença entre investir e o resultado típico de apostar: {brl(s['diferenca_investir_vs_apostar'])}."
    )
