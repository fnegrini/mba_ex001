from langchain.prompts import ChatPromptTemplate

from search import search_prompt

def main():

    question = input("PERGUNTA: ")

    chain = search_prompt(question=question)

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return
    
    else:
        
        print(chain.content)

if __name__ == "__main__":
    main()