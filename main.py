
from query import retrieve_and_rerank
from llm import Inception_llm

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnableLambda,
    RunnablePassthrough
)


# Retrieve documents and prepare citation information
def prepare_context(inputs):
    question = inputs["question"]
    chat_history = inputs.get("chat_history", "")

    results = retrieve_and_rerank(question)

    context_parts = []
    sources = []

    for i, item in enumerate(results, start=1):
        doc = item["document"]
        source_id = f"S{i}"
        source_path = doc.metadata.get("source", "Unknown source")

        context_parts.append(
            f"[{source_id}]\n"
            f"Source: {source_path}\n"
            f"Content:\n{doc.page_content}"
        )

        sources.append({
            "id": source_id,
            "source": source_path
        })

    context = "\n\n".join(context_parts)

    return {
        "question": question,
        "context": context,
        "chat_history": chat_history,
        "sources": sources,
        "contexts": [
            item["document"].page_content
            for item in results
        ]
    }


# Create the prompt
prompt = ChatPromptTemplate.from_template("""
You are a helpful and conversational assistant for the CivicActions employee handbook.

Your job is to answer questions about CivicActions employee policies.

CONVERSATION RULES:
- Remember relevant details shared by the user during the conversation,
  such as their name and preferences.
- Use the user's name naturally when appropriate.
- Understand follow-up questions using the previous conversation.
- Maintain a natural, friendly conversation.
- Do not repeatedly ask the user for information they have already shared.
- Do not assume personal details that the user has not provided.

POLICY ANSWERING RULES:
- Answer policy questions using ONLY the information in the retrieved context.
- Never invent company policies, rules, benefits, or numbers.
- If the retrieved context does not contain sufficient information,
  clearly say that you could not find the information in the handbook.
- Do not use previous conversation as evidence for company policies.
- Previous conversation is only for understanding the user's identity
  and conversational context.

CITATION RULES:
- Cite supporting passages using their IDs, such as [S1] or [S2].
- Put citations next to the claims they support.
- Use only citation IDs that appear in the context.
- Do not invent citations.

Previous conversation:
{chat_history}

Retrieved handbook context:
{context}

User's question:
{question}

Provide a clear, conversational answer with inline citations:
""")


# 3. Build the LCEL chain
rag_chain = (
    RunnableLambda(prepare_context)
    | RunnablePassthrough.assign(
        answer=(
            prompt
            | Inception_llm
            | StrOutputParser()
        )
    )
)


# 4. Ask a question and display the answer and sources
if __name__ == "__main__":
    question = input("Ask a question: ")

    result = rag_chain.invoke({
    "question": question,
    "chat_history": ""
})

    contexts = result["contexts"]
    response = result["answer"]

    print("\n--- Final Answer ---")
    print(result["answer"])

    print("\n--- Sources Used ---")

    for source in result["sources"]:
        print(f"[{source['id']}] {source['source']}")
