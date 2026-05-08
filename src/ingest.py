import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

def ingest_pdf(file_path):

    #1. Ler o PDF
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    print("Carga de PDF {} iniciada".format(file_path))

    #2. Quebrar em chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

    chunks = splitter.split_documents(docs)
    print("Número de chunks gerados: {}".format(len(chunks)))

    #3. Gerar embeddings de cada chunk
    embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_MODEL","text-embedding-3-small"))
    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PGVECTOR_COLLECTION"),
        connection=os.getenv("PGVECTOR_URL"),
        use_jsonb=True,
        pre_delete_collection=True
    )

    #4. Salvar no PostgreSQL via pgVector
    store.add_documents(documents=chunks, ids=[f"doc-{i}" for i in range(len(chunks))])
    print("Ingestão de PDF {} concluída".format(file_path))


if __name__ == "__main__":

    file_path = os.path.join("." , "manual-speed-twin-1200-2020.pdf")

    ingest_pdf(file_path)