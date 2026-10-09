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
├── app.py                  # interface (chat, simulador, sobre)
├── assistente.py           # instruções do bot + chamada ao Gemini
├── busca.py                # lê a base e escolhe os trechos relevantes
├── simulador.py            # cálculos do simulador (Monte Carlo)
├── config.py               # nome, modelos, limites — mude aqui
├── estilo.css              # visual
├── imagens/betinha.png     # rosto da Betinha (troque pelo desenho de vocês)
├── base_conhecimento/      # A BASE: um arquivo .md por tema
│   ├── _MODELO.md          # modelo (arquivos com "_" são ignorados)
│   ├── 02_probabilidades_odds.md
│   └── 06_vieses_comportamentais.md
├── .streamlit/config.toml  # tema claro
├── requirements.txt
└── .env                    # sua chave (NÃO enviar para o GitHub)
```

## Formato da base de conhecimento

```markdown
# Tema: Nome do tema

## Pergunta: Como uma pessoa comum perguntaria?
**Também perguntam:** outra forma; mais outra forma
**Resposta:** 2 a 5 frases simples.
**Exemplo:** situação do dia a dia com números redondos.
**Fonte:** Autor/órgão, título, ano, link.
```

- Cada `## ` = uma pergunta. É a unidade que o sistema busca.
- Salvou um arquivo? O app recarrega a base sozinho na próxima pergunta.
- Até ~60 mil caracteres, a base inteira vai para o Gemini a cada pergunta.
  Acima disso, o app usa busca por similaridade (embeddings) e envia só os
  6 trechos mais parecidos. Os dois limites ficam em `config.py`.

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
