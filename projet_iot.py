import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama

PDF_DIR = "datasheet"



def load_all_pdfs(pdf_dir):
    documents = []
    for file in os.listdir(pdf_dir):
        if file.lower().endswith(".pdf"):
            path = os.path.join(pdf_dir, file)
            loader = PyMuPDFLoader(path)
            documents.extend(loader.load())
    return documents


def main():
    print("Loading PDF document")
    documents = load_all_pdfs(PDF_DIR)

    print("Text chunking")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    docs = splitter.split_documents(documents)

    print("Build a vector database(OpenAI Embedding)")
    embeddings = HuggingFaceEmbeddings(
        model_name="nomic-ai/nomic-embed-text-v1",
        model_kwargs={"trust_remote_code": True}
    )


    vectorstore = FAISS.from_documents(docs, embeddings)

    print("Launch LLM")
    llm = Ollama(
        model="llama3",
        temperature=0
    )

    print("\nRAG system ready, enter your question (type 'exit' to quit)\n")

    while True:
        query = input("Question:")
        if query.lower() == "exit":
            break

        retrieved_docs = vectorstore.similarity_search(query, k=3)
        context = "\n".join([doc.page_content for doc in retrieved_docs])

        prompt = f"""
You are a document-based Q&A system.
Please answer questions strictly based on the provided document content; do not make things up.


Document content:
{context}

Question: {query}
"""

        response = llm.invoke(prompt)
        print("\n Response: ")
        print(response)

        print("-" * 60)


if __name__ == "__main__":
    main()
