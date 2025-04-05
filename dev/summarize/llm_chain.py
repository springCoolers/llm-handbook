import pandas as pd
# from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains.router import MultiPromptChain
from langchain.chains.router.llm_router import LLMRouterChain,RouterOutputParser
from langchain.chains import LLMChain
from templetes import prompt_info
from langchain_core.runnables import RunnablePassthrough, RunnableBranch
from langchain_core.output_parsers import JsonOutputParser
from typing import Literal, TypedDict, Dict, Any
import yaml
import os

load_dotenv()

MULTI_PROMPT_ROUTER_TEMPLATE = """
Task: Categorize the given AI-related content into one of the predefined categories.

Instructions:
The classification should be based on the primary focus of the content.
If the content fits into multiple categories, choose the most dominant one.
Assign at least two relevant tags for more granular classification.

Categories:
- New AI Model Release: Announcements of new AI models and architectures (e.g., GPT-5 release, Mistral-7B).
- New Tool Introduction: Tutorials, reviews, or walkthroughs of AI software/tools (e.g., LangChain updates, Hugging Face spaces).
- Technical Deep Dive: In-depth explanations of AI concepts, mechanisms, or architectures (e.g., "How Transformers Work").
- Benchmark & Performance: Comparisons, speed tests, and efficiency analyses of AI models (e.g., Hugging Face Leaderboard rankings).
- Industry Trend Analysis: Analysis of AI adoption across industries (e.g., "How AI is Changing Finance").
- AI Ethics & Regulation: Discussions on AI risks, bias, governance, and regulations (e.g., EU AI Act updates).
- Open-Source Project: Highlights of new AI repositories and self-hosted projects (e.g., "Self-Hosted LLM on GitHub").
- Research Paper Review: Summaries and breakdowns of academic AI research papers (e.g., "Recent Paper on RLHF in LLMs").
- Event Coverage: Recaps, live updates, and summaries of AI conferences (e.g., NeurIPS, CVPR, ICLR reviews).
- Community Discussion: Debates, Q&A, or informal AI-related conversations (e.g., "Is GPT-4-Turbo Slower Than GPT-4?").
- Meme/Humor: AI-related jokes, memes, or viral content (e.g., "ChatGPT-generated Memes on Twitter").

Input Format:
Title: {{title}}
Content: {{content}}

Output Format:
<< FORMATTING >>
```json
{{{{
    "Category": string \ The most relevant category from the list above or "DEFAULT"
    "Tags": string \ Relevant keywords based on the content
}}}}
```
"""

def init_llm():
    """LLM 모델 초기화"""
    load_dotenv()
    GPT_MODEL = "gpt-4o-mini"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    return ChatOpenAI(model=GPT_MODEL, api_key=OPENAI_API_KEY)

def create_router_chain(llm):
    """라우터 체인 생성"""
    class RouterOutput(TypedDict):
        Category: str
        Tags: str

    router_parser = JsonOutputParser(pydantic_object=RouterOutput)
    
    router_prompt = ChatPromptTemplate.from_messages([
        ("system", MULTI_PROMPT_ROUTER_TEMPLATE),
        ("user", """Title: {title}
Content: {content}""")
    ])
    
    return router_prompt | llm | router_parser

def create_destination_chains(llm, prompt_info):
    """카테고리별 체인 생성"""
    destination_chains = {}
    for p in prompt_info:
        name = p["name"]
        prompt = ChatPromptTemplate.from_template(template=p["prompt_template"])
        destination_chains[name] = prompt | llm | StrOutputParser()
    return destination_chains

def create_default_chain(llm):
    """기본 체인 생성"""
    return (
        ChatPromptTemplate.from_template(
            """아래의 내용을 보고 뉴스레터에 들어가기 쉬운 형태로 요약해줘.
            Title: {title}
            Content: {content}
            """
        )
        | llm
        | StrOutputParser()
    )

def create_branch_fn(destination_chains, default_chain):
    """브랜치 로직 함수 생성"""
    def branch_fn(data: Dict[str, Any]):
        category = data["router_output"]["Category"]
        return destination_chains.get(category, default_chain)
    return branch_fn

def create_chain(prompt_info):
    """전체 체인 생성"""
    llm = init_llm()
    router_chain = create_router_chain(llm)
    destination_chains = create_destination_chains(llm, prompt_info)
    default_chain = create_default_chain(llm)
    branch_fn = create_branch_fn(destination_chains, default_chain)

    return (
        {
            "router_output": router_chain,
            "title": lambda x: x["title"],
            "content": lambda x: x["content"],
        }
        | RunnableBranch(
            (lambda x: x["router_output"]["Category"] in destination_chains, branch_fn),
            default_chain,
        )
    )

def main():
    """메인 실행 함수"""
    csv_filename = "machine_learning_news.csv"
    df = pd.read_csv(csv_filename)
    
    chain = create_chain(prompt_info)
    
    df_1 = df.head(1)
    for index, row in df_1.iterrows():
        title = row["Sub_title"]
        content = row["Content"]
        result = chain.invoke({
                    "title": title,
                    "content": content
                })
        print(result)

if __name__ == "__main__":
    main()
