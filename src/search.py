import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_openai import ChatOpenAI

load_dotenv()

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

def search_prompt(question=None):
  
  if question is None:

    raise ValueError("A pergunta não pode ser vazia.")
  
  embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_MODEL","text-embedding-3-small"))

  store = PGVector(
      embeddings=embeddings,
      collection_name=os.getenv("PGVECTOR_COLLECTION"),
      connection=os.getenv("PGVECTOR_URL"),
      use_jsonb=True,
  )
  
  results = store.similarity_search_with_score(question, k=10)

  #for i, (doc, score) in enumerate(results, start=1):
  #    print("="*50)
  #    print(f"Resultado {i} (score: {score:.2f}):")
  #    print("="*50)
  #    print("\nTexto:\n")
  #    print(doc.page_content.strip())
  #    print("\nMetadados:\n")
  #    for k, v in doc.metadata.items():
  #        print(f"{k}: {v}")

  textos = [doc.page_content for doc, score in results]
  contexto = "\n\n".join(textos)
  prompt = PROMPT_TEMPLATE.format(contexto=contexto, pergunta=question)
  model = ChatOpenAI(model="gpt-5-mini", temperature=0.5)
  result = model.invoke(prompt)
  return result



if __name__ == "__main__":

    search_prompt(question="Qual é a velocidade máxima do Speed Twin 1200 2020?")