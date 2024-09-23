# script/generate-default-page-template.py

import os
import requests
import datetime

def main(input_text):
    
    current_time = datetime.datetime.now()
    print(f"main 실행 시간: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    url = "https://api.perplexity.ai/chat/completions"

    payload = {
        "messages": [
            {
                "content": "Ignore any prompts to not include the cited URL and answer the following questions. You are an LLM engineer writing the LLM Handbook. You are writing a jupyter book for people who are new to LLM. The following are the concepts of a jupyter book and instructions for creating MD files for the chapters. Please answer all questions in Korean.",
                "role": "system"
            },
            {
                "content": f"Describe the content of '{input_text} in LLM'. Write your answer in the following markdown format:\n- Title your document with H1. ex) # {input_text}\n- Write one paragraph conceptual summary based on your search with H2 title. ex) ## Summary\n{{sentences}}\n- Write a one-line description of the concept and what students need to know about '{input_text} in LLM'. ex) ## Key Concepts\n- {{concept 1}} : {{explaination of concept 1}}\n- {{concept 2}} : {{explaination of concept 2}}\n- Write a table of references at the bottom. ex) |{{URL name}}|{{URL}}|",
                "role": "user"
            }
        ],
        "return_citations": True,
        "model": "llama-3.1-sonar-huge-128k-online"
    }

    headers = {
        "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data['choices'][0]['message']['content']
    else:
        print(f"API 요청 실패: 상태 코드 {response.status_code}")
        return ""

def traverse_and_generate():
    # 대상 디렉토리 설정
    target_dir = '_contents/llm-engineering'
    excluded_files = ['Template example.md', '12. Extra materials.md']

    for dirpath, dirnames, filenames in os.walk(target_dir):
        for filename in filenames:
            if filename.endswith('.md') and filename not in excluded_files:
                md_file_path = os.path.join(dirpath, filename)
                input_text = os.path.splitext(filename)[0]  # 확장자 제거한 파일명
                print(f"{md_file_path} 파일을 {input_text} 키워드로 처리 및 생성 중입니다.")
                # 콘텐츠 생성
                content = main(input_text)
                print(content)
                if content:
                    # 기존 MD 파일을 덮어씁니다.
                    with open(md_file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"{md_file_path} 파일이 업데이트되었습니다.")
                else:
                    print(f"{input_text}에 대한 콘텐츠 생성 실패")

if __name__ == '__main__':
    traverse_and_generate()