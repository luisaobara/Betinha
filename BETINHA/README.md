# Betinha — assistente de IA sobre bets + simulador

Projeto de Projetos III (FGV EESP, 2º sem. 2026). Chat com o Gemini que responde
**só com base na base de conhecimento do grupo** e um simulador Monte Carlo que
compara apostar com investir o mesmo dinheiro.

## Como rodar (VS Code)

1. Abra a pasta `assistente_bets` no VS Code e abra o terminal (Ctrl + ').
2. Crie e ative um ambiente virtual:
   - Windows: `python -m venv .venv` e depois `.venv\Scripts\activate`
   - Mac/Linux: `python3 -m venv .venv` e depois `source .venv/bin/activate`
3. Instale as bibliotecas: `pip install -r requirements.txt`
4. Copie `.env.example` para `.env` e cole a sua chave:
   `GEMINI_API_KEY=sua_chave`
5. Rode: `streamlit run app.py` (abre no navegador em http://localhost:8501)

## Estrutura

```
assistente_bets/
├── app.py                  # interface (chat, simulador, mito ou verdade, sobre)
├── assistente.py           # instruções do bot + chamada ao Gemini
├── busca.py                # lê a base e escolhe os trechos relevantes
├── simulador.py            # cálculos do simulador (Monte Carlo)
├── quiz.py                 # frases da aba "Mito ou verdade" (editem aqui)
├── config.py               # nome, modelos, limites — mude aqui
├── testar_betinha.py       # bateria de perguntas de teste
├── gerar_planilha_verificacao.py  # cria a planilha que confere os cálculos
├── estilo.css              # visual
├── imagens/betinha.png     # rosto da Betinha (troque pelo desenho de vocês)
├── base_conhecimento/      # A BASE: um arquivo .md por tema
│   ├── _MODELO.md, _REGISTRO_DE_FONTES.md, _PENDENCIAS_E_CORRECOES.md
│   └── 00_... a 09_...md   # 67 fichas em 10 temas
├── .streamlit/config.toml  # tema claro
├── requirements.txt
└── .env                    # sua chave (NÃO enviar para o GitHub)
```

## Base de conhecimento

67 fichas em 10 temas, construídas a partir das entregas Conteúdo I a IV e dos
feedbacks dos professores:

| Arquivo | Tema (requisito do workbook) |
|---|---|
| 00_sobre_a_betinha.md | O que a Betinha faz e seus limites (palpites, casas, conselhos) |
| 01_como_funcionam_as_apostas.md | Funcionamento das apostas esportivas |
| 02_probabilidades_e_margem_da_casa.md | Probabilidades, chances de ganho e vantagem da casa |
| 03_ganhos_e_perdas_no_longo_prazo.md | Expectativa de retorno, perdas no longo prazo, simulador, "estratégias" |
| 04_custo_de_oportunidade.md | Custo de oportunidade |
| 05_vieses_comportamentais.md | Vieses comportamentais |
| 06_riscos_e_sinais_de_alerta.md | Riscos da aposta excessiva |
| 07_participacao_consciente_e_ajuda.md | Participação consciente e onde buscar ajuda |
| 08_regras_no_brasil.md | Regulamentação, aplicação e fiscalização |
| 09_mercado_e_quem_aposta.md | Mercado brasileiro e perfil dos apostadores |

Arquivos que começam com `_` são do grupo e a Betinha não lê:
`_MODELO.md` (molde + checklist), `_REGISTRO_DE_FONTES.md` (fonte → pontos
extraídos → onde entra) e `_PENDENCIAS_E_CORRECOES.md` (o que revisar).

Formato de cada ficha:

```markdown
## Pergunta: Como uma pessoa comum perguntaria?
**Também perguntam:** outras formas; gírias; erros comuns
**Resposta curta:** UMA frase que já responde.
**Explicação:** 2 a 4 frases simples.
**Exemplo:** situação de aposta esportiva com números redondos.
**Simulador:** (opcional) o que testar no simulador.
**Quer saber mais?** Nome técnico: X. Pergunta relacionada: "..."
**Fonte:** Autor/órgão, título, ano, link.
```

- Cada `## ` = uma ficha. Salvou um arquivo? O app recarrega sozinho.
- Até 150 mil caracteres, a base inteira vai para o Gemini a cada pergunta
  (hoje ela tem ~80 mil). Acima disso, o app usa busca por similaridade.

## Testes

`python testar_betinha.py` manda 22 perguntas para a Betinha (dúvidas comuns,
pedidos de estratégia para lucrar, situações de risco e perguntas fora do
escopo) e salva as respostas, com checagens automáticas, em
`resultados_testes.md`. Usem como ponto de partida para o relatório de testes.

## Recursos para o usuário

- **☰ Menu:** botão no canto superior esquerdo que abre um retângulo rosa na esquerda com as abas uma embaixo da outra
  (Conversar, Simulador, Mito ou verdade, Sobre). Depois de
  escolher uma aba, ele continua aberto (para fechar sozinho, mude `FECHAR_MENU_AO_ESCOLHER` para `True`). As cores do menu ficam em `MENU_FUNDO`, `MENU_TEXTO` etc., e os símbolos das abas em `ICONES`, no início do `app.py`.
- **Perguntas clicáveis:** as perguntas do "Quer saber mais?" aparecem como botões abaixo da resposta.
- **🆘 Preciso de ajuda:** botão no topo com UBS/CAPS, autoexclusão do gov.br e Jogadores Anônimos.
- **🔎 Letra maior:** aumenta o texto do app inteiro.
- **Simulador em forma de frase:** a pessoa completa "Eu aposto R$ __ por vez, __ vezes por __, durante __ anos."
- **Calculadora da margem:** abaixo do botão Simular. A pessoa copia as odds de todos os resultados de uma
  aposta (2 a 6: sim/não, mais/menos gols, vitória/empate/derrota, placar...), vê a soma passar de 100% e
  pode usar a margem calculada (margem = 1 − 1 ÷ soma das chances) no simulador.
- **O que esse dinheiro compraria:** o simulador mostra a perda média em cestas básicas, botijões de gás e
  salários mínimos. Os preços (com fonte) ficam em `EQUIVALENCIAS`, no `config.py`.
- **Mito ou verdade:** quiz com 10 frases; cada uma leva à Betinha. As frases ficam em `quiz.py`.

## Verificação do simulador no Excel

`python gerar_planilha_verificacao.py` cria `verificacao_simulador.xlsx`, que refaz
com fórmulas do Excel todas as contas do simulador, a simulação nº 1 período por
período (com os mesmos sorteios do Python), o investimento e as estatísticas das
2.000 simulações. A aba "Resumo" mostra OK/VERIFICAR para cada parte. Para outro
cenário, mude `PARAMETROS` no início do arquivo e rode de novo.

## Hipóteses do simulador

- Mesmo valor, mesma odd média, mesma frequência; ganhos não são reapostados.
- Chance real = (1 ÷ odd) × (1 − margem da casa) ⇒ perda média = margem × total apostado.
- Vitórias por período ~ Binomial(apostas no período, chance real); 2.000 simulações.
- Investimento: mesmo valor aplicado no início de cada período a uma taxa anual fixa, sem impostos.

## Rosto da Betinha

Salvem o desenho na pasta `imagens/` com o nome `betinha.png` (também vale
`.jpg` ou `.webp`), substituindo o provisório. De preferência quadrado, com pelo
menos 256×256 pixels. Ele aparece no ícone das respostas, na tela inicial, na
barra do topo e na aba do navegador.
