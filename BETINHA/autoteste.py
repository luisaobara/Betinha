"""
Perguntas da aba "Estou apostando demais?".

As perguntas foram inspiradas nos sinais de alerta da base de conhecimento
(arquivo 06_riscos_e_sinais_de_alerta.md) e em questionários de triagem usados
por serviços de saúde. NÃO é um diagnóstico: o resultado só sugere quando vale
buscar apoio. Nada do que a pessoa responde é salvo.

Para editar: mude, apague ou acrescente perguntas na lista abaixo.
As faixas do resultado ficam em RESULTADOS (pelo número de respostas "Sim").
"""

PERGUNTAS = [
    "Você apostou mais dinheiro do que podia perder?",
    "Precisou apostar valores cada vez maiores para sentir a mesma emoção?",
    "Voltou a apostar para tentar recuperar o que tinha perdido?",
    "Pegou dinheiro emprestado ou vendeu alguma coisa para apostar?",
    "Atrasou contas ou deixou de pagar algo por causa das apostas?",
    "Escondeu de alguém quanto ou quando você apostava?",
    "Ficou ansioso, irritado ou dormiu mal por causa das apostas, ou ao tentar parar?",
    "Alguém próximo já reclamou ou se preocupou com as suas apostas?",
    "Tentou parar ou diminuir e não conseguiu?",
    "Sentiu culpa pelo jeito como aposta ou pelo que acontece quando aposta?",
]

# (mínimo de respostas "Sim", título, texto). A primeira faixa que servir é usada.
RESULTADOS = [
    (3, "Vários sinais apareceram nas suas respostas.",
     "Isso não é um diagnóstico, mas é um bom motivo para conversar com alguém e buscar apoio. "
     "Você não precisa resolver isso sozinho, e existe ajuda gratuita."),
    (1, "Alguns sinais merecem atenção.",
     "Eles não querem dizer que você tem um problema, mas mostram que as apostas já estão afetando "
     "o seu dinheiro ou o seu bem-estar. Vale colocar limites agora, antes que cresça."),
    (0, "Nenhum desses sinais apareceu nas suas respostas.",
     "Mesmo assim, vale conhecer os sinais e decidir um limite antes de apostar. "
     "Se algo mudar, você pode refazer o teste quando quiser."),
]
