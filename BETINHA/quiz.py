"""
Perguntas da aba "Mito ou verdade".

Para editar: mude, apague ou acrescente itens na lista abaixo.
- "frase": a afirmação que aparece para a pessoa.
- "verdade": True se a frase é VERDADE, False se é MITO.
- "explicacao": 1 ou 2 frases simples (aparece depois que a pessoa responde).
- "pergunta_betinha": pergunta enviada ao chat no botão "Perguntar à Betinha".
  Use o título de uma ficha da base de conhecimento, para a Betinha saber responder.
"""

QUIZ = [
    {
        "frase": "Depois de perder várias apostas seguidas, a chance de ganhar a próxima aumenta.",
        "verdade": False,
        "explicacao": "Cada aposta é independente: o jogo não \"lembra\" das derrotas anteriores. "
                      "Achar que a vitória \"está para chegar\" é um erro comum, chamado falácia do jogador.",
        "pergunta_betinha": "Depois de perder várias vezes seguidas, a chance de ganhar aumenta?",
    },
    {
        "frase": "A casa de apostas ganha dinheiro mesmo sem acertar quem vai vencer o jogo.",
        "verdade": True,
        "explicacao": "A casa paga um pouco menos do que seria justo em todos os resultados. "
                      "Como um pedágio, essa diferença fica com ela, qualquer que seja o placar.",
        "pergunta_betinha": "Por que a casa de apostas sempre ganha no longo prazo?",
    },
    {
        "frase": "Quem entende muito de futebol consegue lucrar sempre nas apostas.",
        "verdade": False,
        "explicacao": "As odds já são calculadas com muita informação, e a margem da casa continua lá. "
                      "Saber analisar um jogo não é o mesmo que conseguir prever o resultado.",
        "pergunta_betinha": "Entender muito de futebol me faz ganhar nas apostas?",
    },
    {
        "frase": "Uma odd 2,00 quer dizer que a chance de ganhar é exatamente 50%.",
        "verdade": False,
        "explicacao": "1 dividido por 2 dá 50%, mas essa é a chance que a casa \"mostra\". "
                      "Descontando a margem da casa, a chance real fica um pouco abaixo disso.",
        "pergunta_betinha": "Como transformar uma odd em chance de ganhar?",
    },
    {
        "frase": "Quanto mais jogos você junta numa aposta múltipla, mais difícil fica acertar o bilhete.",
        "verdade": True,
        "explicacao": "É preciso acertar todos. Com 3 jogos de 50% cada, a chance de acertar tudo "
                      "cai para 12,5%: você erra em 7 de cada 8 bilhetes.",
        "pergunta_betinha": "O que é uma aposta múltipla? Ela compensa por pagar mais?",
    },
    {
        "frase": "O dinheiro que ganhei numa aposta vale menos que o dinheiro do meu salário.",
        "verdade": False,
        "explicacao": "R$ 100 são R$ 100, venham de onde vierem. Tratar o prêmio como \"dinheiro da casa\" "
                      "faz muita gente arriscar mais e perder dinheiro que já era seu.",
        "pergunta_betinha": "Posso apostar sem problema o dinheiro que ganhei na aposta passada, "
                            "já que não é dinheiro que eu tinha antes?",
    },
    {
        "frase": "Existe um método ou robô que garante lucro nas apostas.",
        "verdade": False,
        "explicacao": "Nenhum método elimina a margem da casa. Quem vende \"lucro garantido\" "
                      "está dando um sinal de alerta.",
        "pergunta_betinha": "Existe alguma estratégia ou fórmula que garanta ganhar nas apostas?",
    },
    {
        "frase": "No Brasil, os sites de apostas autorizados terminam em \".bet.br\".",
        "verdade": True,
        "explicacao": "Só empresas autorizadas pelo Ministério da Fazenda podem funcionar, "
                      "e o endereço delas termina obrigatoriamente em \".bet.br\".",
        "pergunta_betinha": "Apostar em bets é legal no Brasil?",
    },
    {
        "frase": "Um adolescente pode apostar se usar a conta de um adulto.",
        "verdade": False,
        "explicacao": "Menores de 18 anos são proibidos de apostar. As casas precisam conferir a identidade, "
                      "inclusive com reconhecimento facial.",
        "pergunta_betinha": "Um adolescente pode criar conta e apostar?",
    },
    {
        "frase": "Apostar R$ 10 por dia, durante um ano, soma mais de R$ 3.600.",
        "verdade": True,
        "explicacao": "R$ 10 × 365 dias = R$ 3.650. Valores pequenos e frequentes viram uma quantia grande, "
                      "e a margem da casa é cobrada em cada aposta.",
        "pergunta_betinha": "Apostar pouquinho todo dia faz diferença?",
    },
]
