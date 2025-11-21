# Relatório Agentes

Projeto para gerar relatórios de agentes.

## Descrição

Repositório contendo scripts e recursos para análise e geração de relatórios relacionados a agentes (projeto em desenvolvimento).

## Pré-requisitos

- Python 3.8+ recomendado
- Dependências listadas em `requirements.txt` (se houver)

## Instalação (exemplo)

1. Criar um ambiente virtual:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

2. Instalar dependências:

```bash
pip install -r ../requirements.txt
```

> Observação: o arquivo `requirements.txt` está no diretório pai do projeto; ajuste o caminho conforme sua organização.

## Uso

- Exemplos de execução:

```bash
python ../teste.py
```

## Contribuição

- Crie issues e PRs no GitHub. Siga as boas práticas ao abrir pull requests.

## Licença

Adicione uma licença apropriada (por exemplo, `MIT`) ou remova esta seção se não aplicável.

## Dados (pasta `data/`)

- O repositório agora contém um arquivo de exemplo `data/Base_DBM.xlsx` (planilha `dados`) usado pelo app.
- O arquivo `data/Base_DBM.csv` foi removido do repositório para evitar duplicação — o app dá preferência ao `Base_DBM.xlsx` quando presente.

Como fornecer seus próprios dados:

1. Substitua `data/Base_DBM.xlsx` pelo seu arquivo real (mesma estrutura de colunas; sheet `dados`).
2. Ou mantenha o arquivo localmente e use o `st.file_uploader` na interface do Streamlit para fazer upload em tempo de execução.

Importante sobre dados sensíveis:

- Se os dados forem sensíveis, não os coloque no repositório público. Use armazenamento seguro (S3, GCS) ou mantenha os arquivos fora do repo e use variáveis de ambiente ou o uploader.

Deploy no Streamlit Cloud

- O app procura automaticamente por `data/Base_DBM.xlsx` no repositório. Se presente, o Streamlit carregará o arquivo sem necessidade de upload.
- Se você preferir não versionar os dados, remova o `Base_DBM.xlsx` antes do push e use o uploader quando abrir o app no Streamlit Cloud.

