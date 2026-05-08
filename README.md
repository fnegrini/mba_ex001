# Desafio MBA Engenharia de Software com IA - Full Cycle

# RAG com LangChain e PostgreSQL + pgVector

## Objetivo

Implementação de um sistema de **Retrieval Augmented Generation (RAG)** capaz de:

- **Ingerir** um documento PDF, dividindo-o em chunks, gerando embeddings e armazenando os vetores em um banco PostgreSQL com extensão pgVector.
- **Responder perguntas** via linha de comando (CLI), buscando os trechos mais relevantes do documento e utilizando uma LLM para formular a resposta com base exclusivamente no conteúdo ingerido.

---

## Escopo

O documento utilizado neste projeto é o **Manual do Proprietário da Triumph Speed Twin 1200 (2020)**.

O sistema é capaz de responder perguntas sobre:

- Instrumentos e painel de controle
- Manutenção e intervalos de serviço
- Especificações técnicas (motor, pneus, fluidos, etc.)
- Procedimentos de operação e segurança
- Acessórios e equipamentos opcionais

> ⚠️ O sistema responde **somente** com base no conteúdo do manual. Perguntas fora deste escopo receberão a mensagem: _"Não tenho informações necessárias para responder sua pergunta."_

---

## Tecnologias

- **Python** com **LangChain**
- **PostgreSQL 17** com extensão **pgVector**
- **Docker & Docker Compose**
- **OpenAI** (`text-embedding-3-small` + `gpt-4o-mini`) ou **Google Gemini** (`models/embedding-001` + `gemini-2.0-flash`)

---

## Estrutura do Projeto

```
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── src/
│   ├── ingest.py       # Ingestão do PDF no banco vetorial
│   ├── search.py       # Busca semântica no banco
│   └── chat.py         # Interface CLI para perguntas e respostas
├── document.pdf        # Manual da Triumph Speed Twin 1200 2020
└── README.md
```

---

## Configuração

### 1. Clonar o repositório e criar o ambiente virtual

```bash
git clone <url-do-repositorio>
cd <nome-do-repositorio>

python3 -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

Copie o arquivo de exemplo e preencha com suas chaves:

```bash
cp .env.example .env
```

Conteúdo do `.env`:

```env
# OpenAI
OPENAI_API_KEY=sua-chave-aqui
OPENAI_MODEL=text-embedding-3-small

# Google Gemini
GOOGLE_API_KEY=sua-chave-aqui

# PostgreSQL
PGVECTOR_URL=postgresql+psycopg://postgres:postgres@localhost:5434/rag
PGVECTOR_COLLECTION=documents
```

> ℹ️ A porta padrão do container neste projeto é **5434** para evitar conflito com instalações locais do PostgreSQL.

---

## Ordem de Execução

### 1. Subir o banco de dados

```bash
docker compose up -d
```

Aguarde o container `bootstrap_vector_ext` concluir — ele instala automaticamente a extensão `pgVector` no banco.

### 2. Executar a ingestão do PDF

```bash
python src/ingest.py
```

O script irá:
- Ler o `manual-speed-twin-1200-2020.pdf`
- Dividir em chunks de **1000 caracteres** com overlap de **150**
- Gerar embeddings de cada chunk
- Armazenar os vetores no PostgreSQL

### 3. Rodar o chat

```bash
python src/chat.py
```

---

## Exemplos de Uso

### Perguntas dentro do contexto

```
PERGUNTA: Quais informações estão disponíveis no painel da Speed Twin?
RESPOSTA: No painel estão disponíveis: velocímetro, tacômetro, odômetro,
          hodômetro parcial, relógio, indicador de controle de tração (TC),
          luz de aviso de temperatura, ABS, entre outros.
```

```
PERGUNTA: Qual o intervalo recomendado para troca de óleo?
RESPOSTA: <resposta baseada no manual>
```

```
PERGUNTA: Qual a pressão recomendada dos pneus?
RESPOSTA: <resposta baseada no manual>
```

### Perguntas fora do contexto

```
PERGUNTA: Qual a capital da França?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

```
PERGUNTA: Quantos clientes temos em 2024?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

---

## Observações Técnicas

- A cada execução do `ingest.py`, a collection é **recriada** (`pre_delete_collection=True`) para evitar duplicidade de dados.
- A busca utiliza `similarity_search_with_score` com `k=10` — os 10 chunks mais semanticamente próximos da pergunta são enviados como contexto para a LLM.
- A LLM é instruída via prompt a **nunca utilizar conhecimento externo**, respondendo exclusivamente com base nos chunks recuperados.