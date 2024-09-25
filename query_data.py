#query_data.py

import argparse
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from embedding_function import get_embedding_function
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

API_KEY = os.getenv("OPENAI_API_KEY")

def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text)


def query_rag(query_text: str):

    client = OpenAI()

    embedding_function = get_embedding_function()

    # Load the existing database.
    db = Chroma(
        collection_name="medicine-research",
        embedding_function=embedding_function,
        persist_directory= CHROMA_PATH,  # Where to save data locally, remove if not necessary
    )

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    # Use GPT-4 model
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = response.choices[0].message.content

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    return response_text


if __name__ == "__main__":
    main()