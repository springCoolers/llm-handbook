import os
import re
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from youtube_transcript_api import YouTubeTranscriptApi

from langchain.schema.runnable import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

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

### Format: 
{format_instruction}"""

class summarize(BaseModel):
    summary: str = Field(description="Briefly abstractive summarize the main content of the text in 1024 tokens.")
    keywords: list = Field(description="Please extract 5 of the most important keywords from the text (RAG, LLM, MoE, CoT, etc.)")
    category: str = Field(description="Please classification category of the text (paper, model, tool, update & trend)")

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

parser = JsonOutputParser(pydantic_object=summarize)

chain = (
    {
        'context': RunnablePassthrough(),
    }
    | prompt.partial(format_instruction=parser.get_format_instructions())
    | llm
    | parser
)

def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
        r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}(?:\.\d{1,3}){3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return re.match(regex, url) is not None

def is_youtube_url(url):
    regex = re.compile(
        r'^(?:https?://)?'
        r'(?:www\.)?'
        r'(?:m\.)?'
        r'(?:youtube\.com/watch\?v=|youtu\.be/)'
        r'[\w-]+', re.IGNORECASE
    )
    return re.match(regex, url) is not None

def generate_summary(source: str) -> str:
    if is_valid_url(source):
        if is_youtube_url(source):
            match = re.search(r'(?:v=|youtu\.be/)([\w-]+)', source)
            if match:
                video_id = match.group(1)
            else:
                return "잘못된 YouTube URL입니다."
            srt = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            context = "\n".join(item["text"] for item in srt)
        else:
            loader = WebBaseLoader(source)
            documents = loader.load()
            if isinstance(documents, list):
                context = "\n".join(doc.page_content for doc in documents)
            else:
                context = documents
    else:
        context = source

    result = chain.invoke({"context": context})

    return result

if __name__ == "__main__":
    source = input("Enter URL or text: ")
    print(generate_summary(source))
