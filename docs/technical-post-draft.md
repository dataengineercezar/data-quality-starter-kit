# Technical Post Draft: Data Quality Starter Kit

Status: local draft only. Do not publish before explicit approval. This draft is ready for final link insertion after repository creation, if public publication is approved later.

## Working Title

Como transformei uma validacao manual de CSV em um quality gate reutilizavel

## Audience

Engenheiros de dados, analistas tecnicos, gestores de dados em times pequenos e pessoas que ainda dependem de arquivos CSV para operacao, campanhas, relatorios ou auditorias simples.

## Core Message

Qualidade de dados nao precisa comecar com uma plataforma grande. Um fluxo pequeno, testavel e configuravel ja consegue reduzir risco operacional quando arquivos CSV sao usados como entrada para decisoes de negocio.

## Short Post Draft

CSV continua sendo uma das interfaces mais comuns entre sistemas, planilhas, operacoes e times de negocio.

O problema e que muitos arquivos sao usados diretamente em relatorios, campanhas ou analises sem uma verificacao repetivel. Uma coluna ausente, um email invalido, um cliente duplicado ou uma data futura pode parecer detalhe, mas esses erros entram silenciosamente em decisoes reais.

Para explorar esse problema, criei o Data Quality Starter Kit: um MVP em Python para validar arquivos CSV com regras configuraveis em JSON e gerar um relatorio simples.

O escopo foi propositalmente pequeno:

- ler um CSV local;
- carregar regras de validacao a partir de JSON;
- executar checagens como colunas obrigatorias, campos nulos, email, valores aceitos, faixa numerica, unicidade e data futura;
- retornar resultados estruturados;
- oferecer saida no terminal, JSON serializavel e relatorio HTML;
- incluir testes automatizados;
- manter o projeto sem dependencias externas.

A arquitetura ficou direta:

```text
configs/customers.json
        |
        v
examples/customers_*.csv -> read_csv -> validate_dataset -> ValidationReport
                                                    |
                                                    +-> terminal text
                                                    +-> serializable JSON
                                                    +-> HTML report
```

O caso de demonstracao usa um arquivo de clientes. A base valida passa em todas as regras. A base com erros falha em regras de campos obrigatorios, email, status, idade, unicidade e data de cadastro futura. O relatorio HTML resume o resultado executivo, mostra o status por checagem e inclui amostras de falhas com linha, coluna, valor e mensagem.

A principal decisao tecnica foi manter o MVP local-first e auditavel. Em vez de comecar com banco de dados, cloud, orquestracao ou dashboards, o projeto foca em um problema estreito: responder rapidamente se um CSV esta confiavel o bastante para ser usado.

Limites atuais:

- leitura em memoria;
- suporte apenas a CSV;
- sem conectores de banco;
- sem cloud;
- sem orquestracao;
- sem perfilamento estatistico avancado.

Mesmo com esses limites, o projeto ja mostra um padrao reutilizavel para consultoria de escopo fechado: pegar uma entrada de dados simples, transformar regras de negocio em validacoes executaveis e entregar um relatorio entendivel por pessoas tecnicas e nao tecnicas.

O projeto passou por uma revisao local de publicacao segura em 2026-06-10: 9 testes automatizados passaram, a demo valida retornou `passed`, a demo com erros retornou 6 checagens com falha e 10 falhas esperadas, e os artefatos HTML/PNG foram confirmados.

Proximo passo: decidir explicitamente se o repositorio remoto publico sera criado. Ate essa decisao, o post permanece como rascunho local.

## Optional LinkedIn Version

Construi um pequeno MVP em Python para validar arquivos CSV com regras configuraveis e gerar um relatorio HTML simples.

A ideia nasceu de um problema comum em dados: muitos times usam exports de CRM, ERP ou planilhas em relatorios e campanhas sem uma validacao repetivel.

O projeto valida:

- colunas obrigatorias;
- campos nulos;
- emails invalidos;
- valores fora de uma lista aceita;
- faixas numericas;
- chaves duplicadas;
- datas futuras.

Tudo usando apenas Python standard library, JSON de configuracao, testes com `unittest`, saida JSON e um relatorio HTML local.

O objetivo nao foi criar uma plataforma completa de data quality. Foi criar um primeiro quality gate pequeno, explicavel e reaproveitavel.

Esse tipo de ativo e util para portfolio porque mostra engenharia aplicada a um problema de negocio: transformar uma revisao manual de planilha em um processo repetivel e documentado.

## Evidence To Attach Before Publishing

- Repository link after explicit approval and remote creation.
- Screenshot: `docs/demo-output/validation_report.png`.
- Demo docs: `docs/portfolio-demo.md`.
- README sections: setup, architecture, usage, limitations and license.
- Test command result: `python -B -m unittest discover -s tests -v` returned 9 passing tests on 2026-06-10.
- CLI evidence: valid CSV returned `passed`; error CSV returned `failed` with 6 failed checks and 10 expected failures.

## Publication Notes

- Do not mention employer, client, consulting project, private data or proprietary workflows.
- Keep the story generic and portfolio-focused.
- Link to the repository only after public remote creation is explicitly authorized.
- Avoid implying production readiness beyond the documented MVP boundaries.
- Keep the current limitations visible: in-memory CSV only, no cloud, no orchestration, no database connectors and no external services.
