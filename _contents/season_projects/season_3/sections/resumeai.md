# 장영준 - 썰로 만드는 자소서: RESUMAI (깃잔심 시즌3 마무리)

## 설명

생성 AI 기반 자기소개서 어시스턴트 플랫폼

## 목표 기능

1. 유저가 지원 시 마주하는 몇 가지 질문들에 대해 키워드 또는 짧은 문장으로 대답하면
2. 답변과 유사한 양질의 자기소개서 레퍼런스를 바탕으로 새로운 자기소개서 생성

## 기술

RAG, vectorDB (Pinecone)

---

# 2. 진행사항 및 공부한 것

RAG와 Langchain에 대해 학습하고 싶어, 아래 강의를 수강하였습니다.

[【한글자막】 랭체인 - LangChain 으로 LLM 기반 애플리케이션 개발하기](https://www.udemy.com/course/langchain-korean/)

## 미니프로젝트

강의를 통해 아래 3가지 미니 토이 프로젝트를 완성하며, RAG와 Langchain을 학습했습니다.

1. langchain agent를 통해 유명인의 이름 입력하면 그 사람의 linkedin 정보를 가져오고, 해당 정보를 세줄 요약하는 페이지
2. pdf 파일 (실습에서는 ReAct 논문)을 pinecone, faiss에 저장하고 해당 pdf 관련한 QA하는 챗봇
3. [데모] langchain 공식 문서 (html 파일, 약 650페이지)를 pinecone에 저장하여 langchain과 streamlit으로 특정 주제에 관해 대화하는 챗봇 페이지

---

# 3. 프로젝트 프로세스 기획

1. 자기소개서 크롤링
    - Few-shot 프롬프트를 위해 잡코리아, 사람인 등의 취업 사이트에서 자기소개서 크롤링하여 sqlite와  pinecone 에 저장합니다.
2. 프롬프트 구축 및 실험
    - 크롤링한 데이터를 기반으로 프롬프트를 구축하고 실험합니다.
    - 단계별 실험
        1. zero-shot으로 (문항만 제시)
        2. few-shot으로 (문항 + 룰 + 예시) 
        3. few-shot + 나의 경험
    
    [**결과**](https://yjoonjang.tistory.com/29)
    
3. RAG
    - 내가 작성한 항목과 pinecone에 저장된 데이터들과의 유사도를 비교하여 topk를 가져옵니다.
    - 해당 예시들을 프롬프트에 넣습니다.
4. Streamlit
    - streamlit을 활용하여 웹 페이지를 구성합니다.
    - Streamlit share로 페이지를 배포합니다.

---

# 4. 과정

## TODOs

1. 데이터 크롤링
2. DB 결정 후 저장
3. RAG 과정 구현
4. 프롬프팅
5. streamlit으로 웹 구성

### 1. 크롤링

[GitHub - resum-ai/resume-crawler: Resumai의 크롤러 코드를 작성한 레포지토리입니다.](https://github.com/resum-ai/resume-crawler)

- 개별적인 자기소개서 링크 크롤링 (과정생략)

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/333f96cf-396d-45ff-8331-232d41bd4d55/66f357a9-9df6-4cf2-9705-650f74094544/Untitled.png)

- 처음에는 주어진 데이터 (=지원하려는 회사, 시기+직무, 스펙, 질문 리스트, 질문) 모두 크롤링 하려고 했으나, 굳이 필요 없다고 생각하여 질문과 질문에 대한 답만 크롤링하고, pinecone에 저장하기로 했습니다.
    
    ```python
    # jobkorea.py
    
    # 질문과 질문에 대한 답 크롤링
    def self_introduction_crawl(driver: webdriver.Chrome, file_url):
        question_list = []
        answer_list = []
    
        driver.get(file_url)
    
        paper = driver.find_element(By.CLASS_NAME, "qnaLists")
        questions = paper.find_elements(By.TAG_NAME, "dt")
        # print("회사 질문")
        for index in questions:
            question = index.find_element(By.CLASS_NAME, "tx")
            if question.text == "":
                index.find_element(By.TAG_NAME, "button").click()
                question = index.find_element(By.CLASS_NAME, "tx")
                question_list.append(question.text)
            else:
                question_list.append(question.text)
        # print(question_list)
        driver.implicitly_wait(3)
    
        answers = paper.find_elements(By.TAG_NAME, "dd")
        driver.implicitly_wait(3)
        # print("답변")
        for index in range(len(answers)):
            answer = answers[index].find_element(By.CLASS_NAME, "tx")
            if answer.text == "":
                questions[index].find_element(By.TAG_NAME, "button").click()
                answer = answers[index].find_element(By.CLASS_NAME, "tx")
            answer_list.append(answer.text)
        # print(answer_list)
    
        return {
            "question_list": question_list,
            "answer_list": answer_list
        }
    ```
    
- 크롤링 중간에 크롤러 잘못돼서 끊기는 상황이 무서워서, 
`크롤링 데이터 → sqlite3 저장 → pinecone 저장`하기로 결정
- 크롤링 데이터 Sqlite3 저장
    
    ```python
    # jobkorea_protocal.py -> sqlite에 저장
    qa_data = []
    
    while True:
        file_url = file.readline()
        print(read_count, "번째 줄")
    
        if file_url == "":
            break
    
        try:
            qa_result = jobkorea.self_introduction_crawl(driver=driver, file_url=file_url)
            question_list = qa_result["question_list"]
            answer_list = qa_result["answer_list"]
    
            for index in range(len(question_list)):
                question = question_list[index]
                answer = answer_list[index]
    
                # sqlite에 저장
                save_to_db(question, answer)
    
                qa_data.append({
                    "Question": question,
                    "Answer": answer
                })
    
        except Exception as e:
            print(f"{read_count}번째에서 다음 에러가 발생했습니다: {e}")
    
        read_count += 1
    ```
    
- 총 데이터
    
    ![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/333f96cf-396d-45ff-8331-232d41bd4d55/bc325ddd-4ea3-4130-9d78-1b725a56aacf/Untitled.png)
    

### 2. Pinecone 저장

pinecone을 처음 사용해보기에, 공식문서를 최대한 참고했습니다.

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/333f96cf-396d-45ff-8331-232d41bd4d55/3db0a7a5-1b50-4e89-96c7-f4e9ad92b3ca/Untitled.png)

- 먼저 pinecone api key를 발급받아 init 시키고, 연결하여 upsert() 함수를 통해 데이터를 넣는 방식입니다.
(물론 upsert 전에 벡터로 바꾸어야 합니다.)
- 메타데이터
    
    ![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/333f96cf-396d-45ff-8331-232d41bd4d55/f4b3d14e-3c7b-4fcf-b9c1-eba6c5f34dbd/Untitled.png)
    
- Query로 조회 시 결과는 다음과 같았습니다.
    
    ![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/333f96cf-396d-45ff-8331-232d41bd4d55/19a96aa9-4fa7-4622-93ed-c64b092398a3/Untitled.png)
    
- 위를 참고하여 코드로 작성해보았습니다.
    
    ```python
    with open("secrets.json", "r") as file:
       secrets = json.load(file) # key 가져오기
    
    pinecone.init(api_key=secrets["PINECONE_API_KEY"], environment="gcp-starter")
    
    index = pinecone.Index('resumai-self-introduction-index')
    
    #데이터 로드
    conn = sqlite3.connect('crawling_data.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM data")
    datas = cursor.fetchall()
    
    conn.close()
    
    print(len(data)# 3800개
    ```
    
    - 3800개의 데이터를 for문으로 하나하나 upsert 해야하나?? 라는 의문.
- 효율적인 insert 방식
    - batch 이용
    - 비동기 요청
    
    ```python
    def chunks(iterable, batch_size=100):
        it = iter(iterable)
        chunk = tuple(itertools.islice(it, batch_size))
        while chunk:
            yield chunk
            chunk = tuple(itertools.islice(it, batch_size))
    
    def generate_data(datas):
        for index, data in enumerate(datas):
            question = data[0]
            answer = data[1]
            qa = question + "\n\n" + answer
            qa_embedding = get_embedding(qa)
            qa_index = index + 1
            print(qa_index)
            yield (
                str(qa_index),
                qa_embedding,
                {
                    "question": question,
                    "answer": answer,
                    "qa_index": qa_index
                }
            )
    ```
    
    ```python
    with pinecone.Index('resumai-self-introduction-index', pool_threads=30) as pinecone_index:
        async_results = [
            pinecone_index.upsert(vectors=ids_vectors_chunk, async_req=True)
            for ids_vectors_chunk in chunks(generate_data(datas), batch_size=100)
        ]
        [async_result.get() for async_result in async_results]
    ```
    
- 최종적으로 업로드한 이후의 pinecone
    
    ![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/333f96cf-396d-45ff-8331-232d41bd4d55/c162d18f-c4bd-44fc-8e9e-9bbc551101e2/Untitled.png)
    
    - Postman과 유사하게 Query 날리는 기능도 있었습니다!

---

### 3. RAG 구현

![image 66.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/333f96cf-396d-45ff-8331-232d41bd4d55/3a36df01-4e9f-4f0f-8ba4-289b20af9992/image_66.png)

1. Retrieve
    
    ```python
    if st.button("생성하기!"):
        pinecone.init(api_key=st.secrets["PINECONE_API_KEY"], environment="gcp-starter")
        index = pinecone.Index("resumai-self-introduction-index")
    
        query_embedding = get_embedding(user_answer) # 유저가 질문에 답변한 것을 임베딩
    
        retrieved_data = index.query(vector=query_embedding, top_k=3, include_metadata=True) # 유사한 top 3개의 답변
    
        data = retrieved_data["matches"]
    
        data_1_question = data[0]["metadata"]["question"]
        data_1_answer = data[0]["metadata"]["answer"]
    
        data_2_question = data[1]["metadata"]["question"]
        data_2_answer = data[1]["metadata"]["answer"]
    
        data_3_question = data[2]["metadata"]["question"]
        data_3_answer = data[2]["metadata"]["answer"]
    ```
    
2. Augment - 프롬프팅
    
    ```python
    GENERATE_SELF_INTRODUCTION_PROMPT = f"""
    자기소개서를 작성하는데, 다음 질문에 답하려고 합니다.
    Question: {{question}} \n
    
    질문에 대한 저의 대답은 다움과 같습니다.
    Context: {{context}} \n
    
    아래는 몇 가지 예시입니다.
    examples: \n {{examples}} 
    
    예시들과 저의 답변을 참고하여 질문에 대한 대답을 해 주세요.
    """
    ```
    
    ```python
    examples = (
            f"Question: {data_1_question}, \n Answer: {data_1_answer}, \n\n "
            f"Question: {data_2_question}, \n Answer: {data_2_answer}, \n\n "
            f"Question: {data_3_question}, \n Answer: {data_3_answer}"
        )
    
    prompt = GENERATE_SELF_INTRODUCTION_PROMPT.format(
        examples=examples, question=question, context=user_answer
    )
    
    print(prompt)
    ```
    
    - 생성된 프롬프트
        
        ```python
        자기소개서를 작성하는데, 다음 질문에 답하려고 합니다.
        Question: 문제 해결 경험 
        
        질문에 대한 저의 대답은 다움과 같습니다.
        Context: 이번 여름 방학 때, 쇼핑몰 솔루션 개발 업체에서 2달 동안 인턴으로 근무했습니다. 인턴을 처음 시작할 당시, 쇼핑몰의 가장 기본이 되는 회원 시스템과 관리자 시스템이 서버와 클라이언트, 그리고 웹상에서 어떠한 방식으로 작동하는지 원리를 이해하기 위한 과제를 수행했습니다.
        
        과제는 가상의 쇼핑몰을 만들고 쇼핑몰의 회원가입 시스템과 관리자 시스템을 구축하는 것이었습니다. 쇼핑몰을 구성하기 위해서는 서버, HTML, 호스팅, 데이터베이스 등 다양한 분야의. 당시 저는 데이터베이스에 관한 지식만 있던 상태여서 진행을 위한 큰 그림조차 그려지지 않을 정도로 막막한 상태였습니다.
        
        이를 해결하기 위해 가장 기본적으로 웹의 표준인 HTML부터 서버 측 언어인 PHP 등 과제 수행에 필요한 지식을 하나 둘씩 습득했습니다. 시간이 지난 뒤 HTML과 PHP 각각에 대한 지식은 인터넷을 통해 각종 강의를 듣고, 책을 읽어보았지만 이 둘의 관계를 명확히 설명해 놓은 곳은 없고, 결국 무작정 과제 해결에 돌입했습니다.
        
        직접 시행착오를 겪으며 개발을 하다 보니 점점 HTML과 PHP 사이의 관계를 파악하게 되었고 후에는 완전히 이해하게 되어 성공적으로 간단한 쇼핑몰 구축에 성공하였습니다. 
        
        아래는 몇 가지 예시입니다.
        examples: 
        Question: 최근 5년 이내에 했던 경험 중 가장 많은 정보나 의견을 수집, 종합하고 이를 바탕으로 문제를 해결했던 경험에 대해 구체적으로 서술하십시오. (700자 10 단락 이내), 
        Answer: 이번 여름 방학 때, 쇼핑몰 솔루션 개발 업체에서 2달 동안 인턴으로 근무했습니다. 인턴을 처음 시작할 당시, 쇼핑몰의 가장 기본이 되는 회원 시스템과 관리자 시스템이 서버와 클라이언트, 그리고 웹상에서 어떠한 방식으로 작동하는지 원리를 이해하기 위한 과제를 수행했습니다.
        
        과제는 가상의 쇼핑몰을 만들고 쇼핑몰의 회원가입 시스템과 관리자 시스템을 구축하는 것이었습니다. 쇼핑몰을 구성하기 위해서는 서버, HTML, 호스팅, 데이터베이스 등 다양한 분야의식만 있던 상태여서 진행을 위한 큰 그림조차 그려지지 않을 정도로 막막한 상태였습니다.
        
        이를 해결하기 위해 가장 기본적으로 웹의 표준인 HTML부터 서버 측 언어인 PHP 등 과제 수행에 필요한 지식을 하나 둘씩 습득했습니다. 시간이 지난 뒤 HTML과 PHP 각각에 대한 지식은 인터넷을 통해 각종 강의를 듣고, 책을 읽어보았지만 이 둘의 관계를 명확히 설명해 놓은 곳은 없고, 결국 무작정 과제 해결에 돌입했습니다.
        
        직접 시행착오를 겪으며 개발을 하다 보니 점점 HTML과 PHP 사이의 관계를 파악하게 되었고 후에는 완전히 이해하게 되어 성공적으로 간단한 쇼핑몰 구축에 성공하였습니다.
        글자수 692자
        1,168Byte, 
        
        Question: 다양한 의견이나 정보를 자신의 기준으로 분석 / 판단하고, 이를 바탕으로 문제를 해결했던 경험에 대해서 서술하시오. - 최근 5년 이내의 경험으로 작성할 것 - 분석한 의견 것 (700 자 10 단락 이내), 
        Answer: 이번 여름 방학 때, 쇼핑몰 솔루션 개발 업체에서 2달 동안 인턴으로 근무했습니다. 과제는 가상의 쇼핑몰을 만들고 쇼핑몰의 회원가입 시스템과 관리자 시스템을 구축하는 것이었습니다.
        
        쇼핑몰을 구성하기 위해서는 서버, HTML, 호스팅, 데이터베이스 등 다양한 분야의 지식이 필요했습니다. 당시 저는 데이터베이스에 관한 지식만 있던 상태여서 쇼핑몰 설계의 큰 그림조차 그려지지 않을 정도로 막막한 상태였습니다.
        
        이를 해결하기 위해 가장 기본적으로 웹사이트 제작의 큰 틀을 분석하였습니다. 웹사이트 제작에는 서버 측, 클라이언트 측에서 사용하는 언어와 이로 이루어진 페이지, 그리고 각종 데이터를 저장할 데이터베이스가 필요했습니다.
        
        각종 서적을 참고하여 웹의 표준인 HTML부터 서버 측 언어인 PHP 등 과제 수행에 필요한 언어는 익혔지만, 프론트엔드 페이지와 백엔드 페이지 간의 상호작용을 이해하지 못해 어려움을 겪었습니다.
        
        이를 해결하기 위해 인터넷 강좌와 다양한 시행착오를 통해 HTML과 PHP 사이의 관계를 파악했습니다. 여러 번의 시행착오를 겪은 후에는 웹사이트의 작동 원리를 완전히 이해하게 되었고 성공적으로 쇼핑몰 시스템을 구축하는 데 성공하였습니다.
        글자수 610자
        1,036Byte, 
        
        Question: 지원분야와 관련된 학습내용(학창시절 이수과목포함)이나 활동사항(업무수행경험은 좌측 회사경력탭 프로젝트 경력기술서란에 기재), 
        Answer: 컴퓨터공학을 전공하며 웹 프로그래밍 분야에 관심을 갖고 있었습니다. 그러나 학과 내 수업이 개설되지 않아 정식으로 배운 경험이 없어 독학으로 HTML과 자바스크립트 초급 기술만을 익히고 있던 상황이었습니다.
        
        그러던 중 한국데이터베이스진흥원에서 진행하는 Database 개발자 양성과정에 참여하여 웹 프로그래밍 분야를 체계적으로 학습하고 프로젝트를 진행하며 개발 경험을 쌓을 수 있었습니다.
        
        팀 프로젝트의 주제는 자취생들의 윤택한 생활을 돕는 커뮤니티로 선정하였고, 자취하는 티를 감춘다는 의미로 제목은 ‘자취를 감추다’로 하였습니다. 동호회, 공동구매 등 자취생들에게있는 ‘나의 냉장고’ 기능을 고안하였습니다.
        
        또한 자취생이 간편하게 만들 수 있는 요리 레시피를 소개하고, 레시피 별 재료를 등록하여 가진 재료로 만들 수 있는 요리를 검색할 수 있도록 기획하였습니다.
        
        프로젝트는 스프링 프레임웍을 활용하여 MVC 패턴으로 구성하였습니다. 데이터베이스는 오라클로 구축하였고 mybatis를 사용하였습니다. 클라이언트는 JSP로 작성하였으며 AJAX를 활용하 개발하였습니다.
        
        일반 글을 업로드하는 게시판을 만들고 글 작성 화면에 에디터를 적용하여 내용을 다양하게 편집할 수 있도록 하였습니다. 또한 벼룩시장, 레시피 등의 게시판에는 사진을 필수적으로 첨니다. 레시피를 업로드할 때에는 필요한 재료를 전체 재료 DB에서 검색하여 등록하도록 하였습니다.
        
        모든 게시판에 페이징을 구현하였고, 회원별 마이페이지에서 내가 쓴 글/댓글을 볼 수 있게 하였습니다. 또한 ‘가진 재료로 만들 수 있는 레시피 검색’을 위하여 마이페이지의 ‘내 재료비스를 상용화하진 못하였지만, 완성된 프로젝트는 발표 후 투표에서 1등 팀으로 선발되었고, 현재 교육 후속으로 진행되는 멘토링에 참여하여 어플리케이션으로 개발을 진행하고 있습니다.
        글자수 1,174자
        2,017Byte 
        
        예시들과 저의 답변을 참고하여 질문에 대한 대답을 해 주세요.
        ```
        
3. Generate
    
    ```python
    answer = get_chat_openai(prompt)
    
    with st.spinner("답변을 생성중입니다. 잠시만 기다려주세요."):
        if answer:
            st.success("답변이 생성되었습니다!")
        else:
            st.error("답변 생성에 실패했습니다..")
    
    print(answer)
    
    st.write(answer)
    ```
    

---

# 5. 결과

[](https://resume-ai-demo.streamlit.app/)

https://github.com/yjoonjang/resume-ai-demo

---

# 6. 아쉬운 점 및 추가하고 싶은 기능

## 아쉬운 점

아쉬운 점은….생각보다는 결과가 잘 나오질 않는다는 것이었습니다. 
정성들여 쓰지 않고, 대충 키워드만 쓰거나 아무말이나 쓰면 드라마틱하게 잘 작성해주지만,

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/333f96cf-396d-45ff-8331-232d41bd4d55/3690ce9c-6533-4329-a656-3e6bc7a46ada/Untitled.png)

조금이라도 성의있게 작성한 답변에 대해서는 변화가 크게 없었습니다.

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/333f96cf-396d-45ff-8331-232d41bd4d55/106cc8e6-3661-4135-b685-b6fcb85f89a7/Untitled.png)

처음에는 제가 작성한 것에 좀 드라마틱한 변화가 있었으면 했는데,,,생각보다 잘 안나오더군요.. 

이런 성능 문제를 해결하기 위해 다음 방법을 생각해 보았습니다.

- 선택한 질문에 대해, 답변의 어느 부분을 강조해야 하는지를 프롬프팅.
    - 이전에 8가지의 프롬프트를 놓고 실험해보았을 때, **가점요소**를 프롬프트에 제시했을 때 더 높은 퀄리티의 답변을 생성했음
        - 예시: 지원동기
            
            자기소개서 지원동기는 ‘내가 신중하게 골라서 지원한 회사’라는 느낌을 주는 것이 중요하다. 그러기 위해서는 자기분석(직업관, 성향 등)과 회사분석을 통해 지원 이유의 연결고리를 찾아야 한다. 회사 홈페이지를 통해 회사의 비전과 주력사업 현황, 향후 경쟁력 등을 파악하고, 본인의 직업관과 연결시켜 회사에 대한 애정을 보여주는 것이 좋다. - 회사의 비전과 문화, 사업 방향성 등과 본인의 직업관 등을 엮어 접점을 제시했다면, 지원한 직무의 핵심역량과 자신의 강점/경험을 연결시켜 지원 이유를 더욱 보강하는 것이 필요하다. - 지원동기와 입사 후 포부를 한 문항에 함께 물어보는 경우도 종종 있다. 회사와 직무에 적합한 본인의 강점과 더불어 입사하기 위해 지금까지 해 온 노력들을 근거로, 입사 후 조직의 구성원으로서 무슨 일을 하고 어떤 목표를 달성하고 싶은지 말해 주면 좋다. 달성 목표의 경우 현실성 있는 기간과 목표치를 제시한다면 더욱 긍정적인 인상을 남길 수 있다.
            
    - 보편적인 질문들에 대해, 각 질문별로 어떤 가점요소가 있을지 리서치하여, 어떤 질문을 선택하면 그 질문에 해당하는 가점요소가 프롬프팅되도록 하면 좋을듯.
        - https://www.saramin.co.kr/zf_user/highschool/job-info/view?sub_category_cd=10&searchfield=&searchword=&page=1&doc_idx=9539
    - 나중에는 보편적인 질문들이 아닌, 사용자가 직접 마주한 질문을 작성하게 할 예정인데, 이 경우에는 LLM에게 어떤 부분을 강조해야 할지에 대해서 물어보는 것도 좋을듯..!

## 추가하고 싶은 기능

1. 자기소개서 가이드라인 제시
    - 선택한 질문에 대해서 LLM에게 가이드라인을 만들어달라고 하고, 입력란에 생성된 가이드라인을 보여주는 방식
2. 실시간 기업 정보 프롬프팅
    - 현재 기업이 어떤 방향으로 집중하고 있는지 등에 대한 정보를 제공
    - 이런 경우에는, 자신이 지원할 기업을 작성해서, 실시간으로 해당 기업에 대한 기사를 크롤링해오는 것은 말이 안됨.
    - 따라서, 10개 내외의 실시간 기업 정보를 크롤링 해오는 것을 자동화하여 DB에 저장해놓고, 사용자들이 해당 기업을 고르게 하는 수밖에 없을 것 같음.
3. 사용자 피드백 수용
    
    ![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/333f96cf-396d-45ff-8331-232d41bd4d55/d6a0906d-b902-4461-97b7-0e95fb84c9b4/Untitled.png)
    
    - 이렇게 생성된 답변 옆에, 사용자들이 ‘어떠어떠한 방식으로 고쳐줬으면 좋겠다~’ 라고 적을 수 있는 input 란을 만들고, 그걸 다시 LLM과 주고받는 형식..!

---

# 피드백

- RAG가 굳이 필요한가?
- 처음 ui를 마주했을 때 어떤걸 써야할지 잘 모르겠음 -- 이거 가이드라인 제시하면 좋을 것 같음
- langchain으로 프롬프트에 내 자소서 중 어떤 부분을 강조해야할지에 관한 가이드라인 넣어서 실험해보면 좋을 것 같음
- 메타데이터로 필터링해서 retrieve하는 것도 좋겠다.
- 환각 현상이 심함!