import os
import asyncio
from dotenv import load_dotenv

from langchain.schema.runnable import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")

system_message = """You are an agent who reads the given text and specializes in active summerization and keyword extraction. Read the following text, summarize the main content, and extract important keywords.

1. summary: Briefly abstractive summarize the main content of the text in 1024 tokens.
2. keywords: Please extract 5 of the most important keywords from the text (RAG, LLM, MoE, CoT, etc.)
3. category: Please classification category of the text (paper, model, tool, update & trend)
"""

user_message = """### Context
{context}

### Answer:
Please answer in Korean but category should be in English.
**Let's think about it step-by-step!**

summary:
keywords:
category:"""

prompt = ChatPromptTemplate.from_messages(
    [
        ('system', system_message),
        ('user', user_message)
    ]
)


llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0.,
    max_tokens=1024,
    streaming=True
)

parser = StrOutputParser()

chain = (
    {
        'context': RunnablePassthrough(),
    }
    | prompt
    | llm
    | parser
)

async def process(context):
    async for chunk in chain.astream({"context": context}):
        print(chunk, end="", flush=True)

async def main():
    url = input("Enter the URL of the article you want to summarize: ")

    loader = WebBaseLoader(url)
    context = loader.load()

    await process(context)


if __name__ == "__main__":
    asyncio.run(main())
