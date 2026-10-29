# Tema: Expectativa de retorno e perdas no longo prazo


## Pergunta: O que é valor esperado? Quanto eu ganho ou perco em média apostando?
**Também perguntam:** valor esperado; esperança matemática; EV; quanto se perde em média; a aposta vale a pena na média
**Resposta curta:** Valor esperado é quanto você ganharia ou perderia, em média, se repetisse a mesma aposta muitas vezes, e nas bets ele é sempre negativo.
**Explicação:** A conta junta todos os resultados possíveis, pesando cada um pela chance de acontecer. Como a casa cobra margem, o resultado médio de cada aposta é uma pequena perda. Na prática, a perda média é a margem vezes o valor apostado.
**Exemplo:** Com margem de 5%, cada R$ 100 apostados devolvem, em média, R$ 95. Apostando R$ 100 por semana durante 1 ano, você coloca R$ 5.200 e perde, em média, R$ 260.
**Simulador:** O cartão "Total apostado" e a linha "perde, em média" do Simulador mostram exatamente essa conta para o seu caso.
**Quer saber mais?** Nome técnico: valor esperado (ou esperança matemática). Pergunta relacionada: "Se eu ganhei semana passada, por que dizem que vou perder no longo prazo?"
**Fonte:** Bussab, W. O.; Morettin, P. A. Estatística Básica. Saraiva.


## Pergunta: Se eu ganhei semana passada, por que dizem que vou perder no longo prazo?
**Também perguntam:** eu já ganhei dinheiro apostando; tô no lucro; conheço gente que ganha; sorte de principiante; variância
**Resposta curta:** Porque em poucas apostas a sorte pesa muito, mas com muitas apostas ela perde peso e o que sobra é a margem da casa.
**Explicação:** Os resultados de apostas "balançam" bastante: dá para ganhar várias seguidas e perder várias seguidas. Esse balanço esconde a tendência no curto prazo. Mas, quanto mais você aposta, mais o seu resultado médio se aproxima do valor esperado, e ele é negativo. A sorte não "devolve" o que você perdeu; ela só vai ficando pequena perto da margem que se acumula.
**Exemplo:** Em 5 apostas de R$ 20, é bem possível estar no lucro. Em 500 apostas de R$ 20 (R$ 10.000 no total) com margem de 5%, o resultado tende a ficar perto de uma perda de R$ 500.
**Simulador:** No gráfico "Onde as simulações terminaram", repare que algumas simulações acabam no lucro, mas a maioria fica no prejuízo. Aumente os anos e veja a parte do lucro encolher.
**Quer saber mais?** Nome técnico: variância e Lei dos Grandes Números. Pergunta relacionada: "O que é a Lei dos Grandes Números?"
**Fonte:** Bussab, W. O.; Morettin, P. A. Estatística Básica. Saraiva; Meyer, P. L. Probabilidade: aplicações à estatística. LTC.


## Pergunta: O que é a Lei dos Grandes Números e o que ela tem a ver com apostas?
**Também perguntam:** lei dos grandes números; a sorte se equilibra; no longo prazo eu recupero; a média compensa
**Resposta curta:** Ela diz que, quanto mais vezes você repete uma aposta, mais o seu resultado médio se aproxima do valor esperado, que nas bets é uma perda.
**Explicação:** A lei não diz que a sorte "se equilibra" nem que perdas passadas serão recuperadas: cada aposta é independente da anterior. O que acontece é que as variações por acaso ficam cada vez menores em relação ao total apostado, enquanto a margem cobrada em cada aposta vai se somando. É por isso que a casa, que recebe milhões de apostas, tem lucro estável.
**Exemplo:** Jogando uma moeda 10 vezes, pode dar 7 caras. Jogando 10.000 vezes, a proporção vai ficar muito perto de 50%. Nas apostas, a "moeda" é levemente viciada a favor da casa, e com muitas apostas isso aparece.
**Simulador:** Rode o Simulador com 1 ano e depois com 10 anos: a faixa de resultados fica mais concentrada no prejuízo.
**Quer saber mais?** Nome técnico: Lei dos Grandes Números; Teorema Central do Limite (explica por que o gráfico dos resultados finais tem formato de sino). Pergunta relacionada: "Como funciona o Simulador?"
**Fonte:** Bussab, W. O.; Morettin, P. A. Estatística Básica. Saraiva; Meyer, P. L. Probabilidade: aplicações à estatística. LTC.


## Pergunta: Como funciona o Simulador? O que é simulação de Monte Carlo?
**Também perguntam:** como o simulador calcula; de onde vêm os números do simulador; monte carlo; o que é o caso típico; o que é a faixa
**Resposta curta:** O Simulador "finge" que você apostou do mesmo jeito milhares de vezes e mostra o que costuma acontecer com o seu dinheiro.
**Explicação:** Você informa o valor, a frequência, a odd, a margem e o prazo. O computador sorteia o resultado de cada aposta, respeitando a chance real, e repete isso 2.000 vezes. O "caso típico" é o resultado do meio, e a faixa sombreada mostra onde caiu a maioria das simulações. Ao lado, ele calcula quanto você teria se investisse o mesmo dinheiro.
**Exemplo:** 3 apostas de R$ 20 por semana, odd 2,00 e margem de 7%, durante 3 anos: você coloca R$ 9.360 e o caso típico termina com cerca de R$ 640 de prejuízo. Investindo o mesmo valor a 10% ao ano, teria cerca de R$ 1.480 de rendimento.
**Quer saber mais?** Nome técnico: simulação de Monte Carlo; distribuição binomial (conta quantas apostas você ganha). Pergunta relacionada: "Quais são as limitações do Simulador?"
**Fonte:** Ross, S. M. Simulation. Academic Press; Bussab, W. O.; Morettin, P. A. Estatística Básica. Saraiva.


## Pergunta: Quais são as limitações do Simulador?
**Também perguntam:** o simulador é exato; o simulador prevê meu futuro; hipóteses do simulador
**Resposta curta:** O Simulador é um modelo educativo: mostra tendências, não prevê exatamente o que vai acontecer com você.
**Explicação:** Ele supõe que você aposta sempre o mesmo valor, na mesma odd média e com a mesma frequência, e que cada aposta é independente das outras. Os ganhos não são reapostados. O investimento comparado rende uma taxa fixa, sem impostos nem taxas. Na vida real, as odds mudam e as pessoas costumam aumentar o valor depois de ganhar ou de perder, o que tende a piorar o resultado.
**Exemplo:** Se você aposta R$ 10 num dia e R$ 100 no outro, use no Simulador o valor médio por aposta, sabendo que é uma aproximação.
**Quer saber mais?** Pergunta relacionada: "O que é perseguição de perdas?"
**Fonte:** Ross, S. M. Simulation. Academic Press; Lesieur, H. R. The Chase: Career of the Compulsive Gambler. Anchor Press/Doubleday, 1977.


## Pergunta: Existe alguma estratégia ou fórmula que garanta ganhar nas apostas?
**Também perguntam:** estratégia infalível; método para ganhar sempre; como lucrar com bets; como ganhar dinheiro com apostas; robô de apostas; curso de apostas; tip garantida; green garantido; como aumentar meu retorno
**Resposta curta:** Não. Não existe estratégia que garanta lucro nas apostas.
**Explicação:** As odds já são calculadas para a casa ter vantagem em qualquer resultado, e nenhum método, planilha ou robô elimina essa margem no longo prazo. O jogo também tem coisas imprevisíveis, como lesões, arbitragem e sorte. Quem vende curso ou "método" prometendo lucro certo está dando um sinal de alerta. A própria lei proíbe publicidade que apresente a aposta como forma de ganhar dinheiro ou resolver problemas financeiros.
**Exemplo:** Um método que "acerta 70%" das apostas em odds 1,30 ainda perde dinheiro: a cada 10 apostas de R$ 10, você ganha 7 × R$ 3 = R$ 21 e perde 3 × R$ 10 = R$ 30.
**Simulador:** Se quiser, eu te mostro no Simulador como isso funciona: qualquer combinação de odd e margem positiva termina com o caso típico no prejuízo.
**Quer saber mais?** Nome técnico: valor esperado negativo. Pergunta relacionada: "Dobrar a aposta depois de perder funciona?"
**Fonte:** Lei nº 14.790/2023; Portaria SPA/MF nº 1.231/2024; Portaria Interministerial MF/SECOM/MJSP nº 73/2026.


## Pergunta: Dobrar a aposta depois de perder funciona? (Martingale)
**Também perguntam:** martingale; dobrar até ganhar; aumentar a aposta para recuperar; estratégia de dobrar; gale
**Resposta curta:** Não. Dobrar depois de cada derrota parece recuperar tudo, mas uma sequência de derrotas faz o valor explodir e pode zerar o seu dinheiro.
**Explicação:** A ideia é que uma vitória cobre todas as perdas anteriores. O problema é que sequências de derrotas são mais comuns do que parecem, e o valor cresce muito rápido. Ou o seu dinheiro acaba, ou você bate no limite da casa antes da vitória chegar. E a margem da casa continua sendo cobrada em todas essas apostas.
**Exemplo:** Começando com R$ 10, com 6 derrotas seguidas você já perdeu R$ 630 e a próxima aposta teria que ser de R$ 640, só para ganhar os R$ 10 do começo. Numa aposta com 50% de chance, perder 6 seguidas acontece mais ou menos 1 vez a cada 64 tentativas.
**Quer saber mais?** Nome técnico: Martingale e risco de ruína. Pergunta relacionada: "O que é perseguição de perdas?"
**Fonte:** Meyer, P. L. Probabilidade: aplicações à estatística. LTC; Ross, S. M. Probabilidade: um curso moderno com aplicações. Bookman (problema da ruína do jogador).


## Pergunta: O que é o critério de Kelly? Ele ajuda a ganhar nas apostas?
**Também perguntam:** critério de kelly; quanto apostar da banca; tamanho ideal da aposta; fórmula de kelly
**Resposta curta:** O critério de Kelly é uma fórmula que diz quanto apostar quando a aposta é vantajosa, e, nas bets, como a margem da casa torna a aposta desvantajosa, a fórmula diz para apostar zero.
**Explicação:** A fórmula é f = (b × p − q) ÷ b, onde b é a odd menos 1, p é a chance real de ganhar e q é a chance de perder. Ela só dá um valor positivo quando a sua chance real é maior do que a odd sugere. Como a casa cobra margem, isso não acontece na média, e achar que você estima as chances melhor que a casa é exatamente o excesso de confiança.
**Exemplo:** Odd 2,00 com chance real de 46,5%: b = 1, p = 0,465, q = 0,535. A conta dá 0,465 − 0,535 = −0,07. Resultado negativo: a fórmula recomenda não apostar.
**Quer saber mais?** Nome técnico: critério de Kelly. Pergunta relacionada: "Entender muito de futebol me faz ganhar nas apostas?"
**Fonte:** Kelly, J. L. A New Interpretation of Information Rate. Bell System Technical Journal, v. 35, n. 4, p. 917–926, 1956.


## Pergunta: Dá para viver de apostas ou usar como renda extra?
**Também perguntam:** apostador profissional; renda extra com bets; ganhar a vida apostando; trocar o trabalho pelas apostas; aposta é investimento
**Resposta curta:** Não é uma forma confiável de renda: na média, quem aposta perde dinheiro, e aposta não é investimento.
**Explicação:** Um investimento tem retorno esperado positivo, e a aposta tem retorno esperado negativo por causa da margem da casa. Desde julho de 2026, toda propaganda de bets no Brasil precisa exibir avisos como "Apostar faz você perder dinheiro" e "Aposta não é investimento". Contar com apostas para pagar contas aumenta muito o risco de dívidas.
**Exemplo:** R$ 300 por mês apostados com margem de 5% perdem, em média, R$ 15 por mês. Os mesmos R$ 300 guardados todo mês rendem juros, em vez de encolher.
**Quer saber mais?** Pergunta relacionada: "Quanto eu deixo de ganhar apostando em vez de investir?"
**Fonte:** Portaria SPA/MF nº 1.964/2026; Portaria Interministerial MF/SECOM/MJSP nº 73/2026.