# Pendências e correções da base (para o grupo revisar)

> Arquivo de controle. Começa com "_", então a Betinha NÃO lê.

## A. Erros encontrados nas entregas e já corrigidos nas fichas

1. **Imposto de Renda (Conteúdo III, Pergunta 12).** A entrega dizia que se desconta o que foi perdido "na mesma plataforma" e que os 15% valem sobre o ganho. Pelo art. 31 da Lei 14.790/2023, o prêmio líquido é o resultado positivo **do ano**, descontadas as perdas com apostas **da mesma natureza** (não "da mesma plataforma"), e o imposto só incide sobre o que **passar da primeira faixa da tabela anual do IR**. A ficha foi corrigida.
2. **Escolha de casa de apostas (Conteúdo III, Pergunta 11).** A resposta sugeria comparar odds entre sites e escolher um "favorito". Isso ajuda a apostar melhor e vai contra a regra do workbook de não incentivar. A ficha nova não recomenda casas: só ensina a conferir se o site é autorizado (.bet.br).
3. **Herding e representatividade (Conteúdo II, itens 17 e 22).** O texto dizia que o bot mostraria se uma aposta tem "valor esperado positivo". Isso vira dica de aposta. As fichas novas explicam o viés sem avaliar apostas específicas.
4. **Ancoragem (Conteúdo II, item 18).** A definição copiada era a de enquadramento. Corrigido.
5. **Falácia do jogador (Conteúdo II, segundo item 21).** A definição copiada era a de custos irrecuperáveis (e a numeração "21" aparece duas vezes). Corrigido.
6. **Simulador (Conteúdo IV, Hipóteses).** O texto dizia "p = 1 ÷ odd". Com essa conta, o valor esperado dá **zero**, o que contradiz a hipótese seguinte (margem constante). O código usa p = (1 ÷ odd) × (1 − margem). Ajustem o texto do relatório técnico.
7. **Overround (Conteúdo III, Pergunta 3).** Uma soma de 103,6% quer dizer que a casa fica com cerca de 3,5% do que foi apostado (1 − 1/1,036), e não exatamente 3,6%. A ficha explica isso.
8. **Odd e enquadramento (Conteúdo III, Pergunta 1).** O exemplo "x2,50 vs. 50% de chance de perder" não bate: odd 2,50 equivale a cerca de 60% de chance de perder. A ficha nova usa outro exemplo.

## B. Números que não batem entre si (escolher um e citar a fonte)

- **Número de empresas autorizadas:** "cerca de 90 a partir de 2024" (Conteúdo III, P9) × "78 empresas no 1º semestre de 2025" (Conteúdo I). A ficha usa 78. Confiram na lista atual do gov.br.
- **Tamanho do mercado:** US$ 4,139 bi (receita líquida 2025) × US$ 4,12 bi (tamanho do mercado esportivo 2025) × R$ 17,4 bi (faturamento 1º sem. 2025). A ficha usa "cerca de US$ 4,1 bi" e explica que receita ≠ total apostado.
- **Idade (DataSenado × Quaest):** DataSenado diz que 56% têm 16–39 anos, e a Quaest mostra distribuição equilibrada entre as faixas. As perguntas são diferentes (apostou no mês × costuma apostar). A ficha usa o DataSenado.

## C. Pontos que dependem de decisão do grupo

- **Margem padrão do Simulador.** O app começa em 7%, mas nenhuma entrega traz uma faixa de margem com fonte. Pesquisem a margem típica de mercados de futebol (1X2) e, se possível, de múltiplas, e ajustem o valor inicial em `app.py`. O feedback de ancoragem do Conteúdo II também pede valores iniciais "neutros".
- **Taxa do investimento alternativo.** Começa em 10% ao ano só como exemplo. Usem a taxa atual de um título público e citem a fonte.
- **Dados da Quaest por religião e posição política** (Conteúdo I) foram deixados de fora da base: não ajudam a responder dúvidas do público e poderiam soar como julgamento de grupos.
- **Entrevistas com apostadores** (feedback do Conteúdo I): se não forem feitas, o relatório deve justificar o uso de estatísticas agregadas (DataSenado, Locomotiva, Clarice/Ideia).

## D. Informações acrescentadas por mim que não estavam nas entregas (conferir)

- Critério de Kelly aplicado a apostas com margem (resultado negativo → apostar zero): conta feita com os números do próprio simulador.
- Exemplo do Monte Carlo de 1913 (roleta deu preto 26 vezes), citado no Conteúdo II como ideia de módulo.
- Cash-out: o valor oferecido embute a margem da casa (consenso de mercado; buscar uma fonte para citar).
- Sinais de alerta extras (pensar em apostas o tempo todo, pegar dinheiro emprestado): critérios comuns de rastreio; citar o Ministério da Saúde ou a CID-11.
- Renegociação de dívidas nos Procons (Lei do Superendividamento, Lei nº 14.181/2021).
- Ficha "Como posso ajudar um amigo ou familiar": orientação geral; validar com a fonte de saúde escolhida.
- Fichas novas pedidas pelos feedbacks: "Quem fiscaliza as bets?" (aplicação e monitoramento da regulamentação), "Você pode me dar um palpite?" e "Existe estratégia garantida?" (perguntas de otimização).

## E. Revisão das fontes (16/10)

- Retiradas as fontes de 9 fichas que não precisam (sobre a Betinha, o simulador e contas simples).
- Retiradas todas as autocitações ("Grupo A2, Conteúdo X").
- Trocadas fontes que não sustentavam a ficha: "O que significa odd?" (Prospect Theory → Estadão);
  quase-perda (Prospect Theory → Clark et al., 2009); tigrinho (Portarias/PL → estudo sobre
  imediatez da recompensa em caça-níqueis); cartão de crédito (Portaria 722 → Portaria 615/2024).
- Conferir ainda: a origem do dado "89% gastam todo mês / 39% entre R$ 50 e R$ 200 / 8,6% mais de
  R$ 500" (Conteúdo I não diz de onde veio) e o veículo da notícia "R$ 3 bilhões em tributos via LAI".
