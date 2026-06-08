# Demo Case: Customer CSV Quality Check

## Business Scenario

Uma pequena empresa usa um arquivo CSV de clientes exportado de um CRM simples antes de preparar relatorios, campanhas de email e analises comerciais. O arquivo e usado por pessoas de operacoes, marketing e gestao, mas hoje a validacao e manual: alguem abre a planilha, confere algumas linhas e assume que os dados estao bons.

O objetivo deste caso de demonstracao e validar um arquivo `customers.csv` antes que ele seja usado em decisoes ou automacoes.

## Data Context

O arquivo de clientes planejado para o MVP contem as seguintes colunas:

- `customer_id`: identificador unico do cliente;
- `full_name`: nome completo;
- `email`: email principal para contato e campanhas;
- `status`: situacao comercial do cliente;
- `age`: idade do cliente;
- `signup_date`: data de cadastro.

## Why Bad Data Is Risky

Dados ruins em uma base de clientes podem gerar problemas praticos:

- clientes duplicados distorcem metricas de aquisicao e retencao;
- emails invalidos reduzem entrega de campanhas e prejudicam reputacao;
- status incorretos incluem clientes errados em campanhas ou relatorios;
- idades fora do esperado quebram segmentacoes e analises;
- datas futuras de cadastro indicam erro de carga, timezone ou digitacao;
- campos vazios impedem analises confiaveis e aumentam retrabalho manual.

Esses problemas parecem pequenos em uma planilha, mas afetam diretamente decisoes de receita, comunicacao e operacao.

## Validation Value

A validacao proposta transforma a revisao manual em um processo repetivel. Antes de usar o CSV, a empresa podera responder perguntas como:

- o arquivo tem todas as colunas esperadas?
- os campos criticos estao preenchidos?
- cada cliente aparece apenas uma vez?
- os emails parecem validos?
- os status seguem uma lista conhecida?
- as idades estao dentro de uma faixa aceitavel?
- existe algum cadastro com data futura?

O valor do kit esta em tornar essas respostas visiveis rapidamente, com um relatorio simples que pode ser entendido por usuarios tecnicos e nao tecnicos.

## Planned Demo Files

- `examples/customers_valid.csv`: arquivo com dados bons para demonstrar um caso aprovado;
- `examples/customers_with_errors.csv`: arquivo com erros realistas para demonstrar falhas;
- `configs/customers.json`: regras planejadas para validar o arquivo de clientes.
- `docs/demo-output/validation_report.html`: relatorio HTML gerado a partir do arquivo com erros.
- `docs/demo-output/validation_report.png`: screenshot do relatorio HTML.
- `docs/portfolio-demo.md`: narrativa curta da demo para portfolio.

## MVP Boundary

O MVP atual cobre um fluxo local de validacao de CSV com regras JSON configuraveis, saida no terminal, saida JSON, relatorio HTML simples e testes automatizados basicos.

Ainda estao fora do escopo:

- conexoes com bancos de dados;
- armazenamento em nuvem;
- orquestracao;
- dashboards;
- servicos pagos;
- publicacao sem autorizacao explicita.
