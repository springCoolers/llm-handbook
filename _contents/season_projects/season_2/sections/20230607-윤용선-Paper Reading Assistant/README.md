# Paper Reading Assistant [윤용선]

## 1. Introduction

- 논문을 제대로 읽기 위한 도구 필요
- 논문과 관련된 질문을 생성하고 나의 답변을 채점할 수 있는 시스템 개발

## 2. Method

1. Download paper: Arxiv에서 논문 정보와 pdf 다운로드
2. Preprocess paper: pdf에서 논문 text를 추출 후 전처리
3. Generate questions: 논문을 읽고 관련된 질문 생성
4. Answer questions: 질문에 대한 pseudo 정답 생성
5. Evaluate user answer: pseudo 정답을 기준으로 사람의 답변 채점

### 2.1. Download paper

- 사용자가 입력한 arxiv id에 해당하는 논문 정보와 pdf 파일 다운로드
- `arxiv` 라이브러리 사용

```python
def download_paper(arxiv_id):
    search = arxiv.Search(id_list = [arxiv_id])
    result = next(search.results())

    file_path = f'pdfs/{arxiv_id}.pdf'
    if not os.path.exists(file_path):
        result.download_pdf(dirpath='pdfs', filename=f'{arxiv_id}.pdf')
    
    authors = ', '.join([a.name for a in result.authors])
    paper = {'title': result.title, 'arxiv_id': arxiv_id, 'authors': authors, 'abstract': result.summary, 'file_path': file_path}
    return paper

def print_paper(paper):
    print('title: ' + paper['title'] + '\n')
    print('url: ' + 'https://arxiv.org/abs/' + paper['arxiv_id'] + '\n')
    print('authors: ' + paper['authors'] + '\n')
    print('abstract: ' + paper['abstract'])

arxiv_id = '2305.13298'
paper = download_paper(arxiv_id)
print(paper)
```

![Untitled](https://www.notion.so/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2Fe37a94d5-d37b-4c35-99fc-0a6f3a289763%2FUntitled.png?id=2552128b-ebe9-454c-946a-27a727e43059&table=block&spaceId=333f96cf-396d-45ff-8331-232d41bd4d55&width=2000&userId=ab2ec52b-c260-48c9-897a-d976ebe755f2&cache=v2)

### 2.2. Preprocess paper

- `fitz` 라이브러리를 사용하여 pdf 파일에서 텍스트 추출
- 일정 길이를 기준으로 텍스트를 분리하여 chunk 구성
- chunk별로 embedding 추출 후 index에 저장
- `langchain` 라이브러리 사용
    - `RecursiveCharacterTextSplitter`: 텍스트를 특정 길이로 분리
    - `HuggingFaceEmbeddings`: Text embedding wrapper
    - `FAISS`: Faiss vector index wrapper

```python
def clean_text(text):
    text = text.replace('\n', ' ')
    text = re.sub('\s+', ' ', text)
    return text

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    num_pages = doc.page_count

    text = []
    for p in range(num_pages):
        page = doc[p]
        page_text = page.get_text('text')
        page_text = clean_text(page_text)
        text.append(page_text)

    doc.close()
    text = '\n'.join(text)
    return text

def split_text(text, chunk_size=1024):
    text_splitter =  RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=100)
    chunks = text_splitter.split_text(text)
    chunks = [c for c in chunks if len(c) > chunk_size * 0.9]
    return chunks

text = extract_text(paper['file_path'])
chunks = split_text(text)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
db = FAISS.from_texts(chunks, embeddings)
```

### 2.3. Generate questions

- chunk를 보고 답변 가능한 질문 생성
- chunk 선택
    - reference, acknowledgement와 같이 논문 내용과 관련 없는 chunk 존재
    - 이를 해결하기 위해 논문 abstract과 유사도가 높은 5개의 chunk만 선택
- 질문 생성
    - 한 chunk당 3개 질문 생성
    - `langchain`의 `ChatOpenAI`모듈 사용
- 질문 선택
    - 유사한 질문들이 많이 생성되기 때문에 다른 질문들을 선택하는 과정 필요
    - extractive summarization에서 사용하는 Maximal marginal relevance를 사용하여 질문 선택

```python
def clean_questions(questions):
    return [q.replace(f'{i+1}.', '').strip() for i, q in enumerate(questions.split('\n'))]

def generate_questions(chat, context):
    system_content = (
        'Generate three questions based on the paragraph. '
        'All questions should be answerable using the information provided in the paragraph.'
    )

    messages = [
        SystemMessage(content=system_content),
        HumanMessage(content=context)
    ]

    questions = run_chat(chat, messages)
    return clean_questions(questions)

class MMR(object):
    def __init__(self, k, _lambda):
        self.k = k
        self._lambda = _lambda
    
    def get_similarity(self, s1, s2):
        """ Get cosine similarity between vectors

        Params:
        s1 (np.array): 1d sentence embedding (512,)
        s2 (np.array): 1d sentence embedding (512,)
        
        Returns:
        sim (float): cosine similarity 
        """

        cossim = np.dot(s1, s2) / (np.linalg.norm(s1) * np.linalg.norm(s2))
        sim = 1 - np.arccos(cossim) / np.pi
        return sim
    
    def get_similarity_with_matrix(self, s, m):
        """Get cosine similarity between vector and matrix

        Params:
        s (np.array): 1d sentence embedding (512,)
        m (np.array): 2d sentences' embedding (n, 512)

        Returns:
        sim (np.array): similarity (n,)
        """

        cossim = np.dot(m, s) / (np.linalg.norm(s) * np.linalg.norm(m, axis=1))
        sim = 1 - np.arccos(cossim) / np.pi
        return sim
    
    def get_mmr_score(self, s, q, selected):
        """Get MMR (Maximal Marginal Relevance) score of a sentence

        Params:
        s (np.array): sentence embedding (512,)
        q (np.array): query embedding (512,)
        selected (np.array): embedding of selected sentences (m, 512)

        Returns:
        mmr_score (float)
        """

        relevance = self._lambda * self.get_similarity(s, q)
        if selected.shape[0] > 0:
            negative_diversity = (1 - self._lambda) * np.max(self.get_similarity_with_matrix(s, selected))
        else:
            negative_diversity = 0
        return relevance - negative_diversity

    def summarize(self, embedding):
        selected = [False] * len(embedding)

        query = np.mean(embedding, axis=0) # (512,)
        while np.sum(selected) < self.k:
            selected_embedding = embedding[selected]
            remaining_idx = [idx for idx, i in enumerate(selected) if not i]
            mmr_score = [self.get_mmr_score(embedding[i], query, selected_embedding) for i in remaining_idx]
            best_idx = remaining_idx[np.argsort(mmr_score)[-1]]
            selected[best_idx] = True

        selected = np.where(selected)[0].tolist()
        return selected

contexts = db.similarity_search(paper['abstract'], k=5)
contexts = [c.page_content for c in contexts]

chat = ChatOpenAI(openai_api_key=OPENAI_API_KEY)
questions = []
for ctx in contexts:
    questions += generate_questions(chat, ctx)

question_embeds = embeddings.embed_documents(questions)
question_embeds = np.array(question_embeds)

mmr = MMR(k=3, _lambda=0.5)
question_idxs = mmr.summarize(question_embeds)
selected_questions = [questions[i] for i in question_idxs]
selected_questions
```

생성 질문 예시

```
What is DIFFUSIONNER and how does it formulate named entity recognition?
How does the model generate entity boundaries during inference?
What are the advantages of DIFFUSIONNER over previous models?
```

### 2.4. Answer questions

- 생성한 질문에 대한 답변을 생성
- 질문과 유사한 chunk를 검색 후 chatgpt에 함께 입력

```python
def answer_question(chat, context, question):
    system_content = (
        "Answer the question as truthfully as possible using the provided context. "
        "The answer should be one line."
    )

    user_content = f'Context:\n{context}\nQuestion:\n{question}'

    messages = [
        SystemMessage(content=system_content),
        HumanMessage(content=user_content)
    ]

    return run_chat(chat, messages)

qnas = []
for q in selected_questions:
    ctx = db.similarity_search(q, k=1)[0].page_content
    ans = answer_question(chat, ctx, q)
    qnas.append((q, ans))
```

답변 예시

```
Q: What is DIFFUSIONNER and how does it formulate named entity recognition?
A: DIFFUSIONNER formulates named entity recognition task as a boundary-denoising diffusion process and generates named entities from noisy spans.
evidence: we propose DIFFUSIONNER, which formulates the named entity recognition task as a boundary-denoising diffusion process and thus generates named entities from noisy spans.

Q: How does the model generate entity boundaries during inference?
A: The model predicts entity boundaries at the word level using max-pooling to aggregate subwords into word representations.
evidence: Entity boundaries are predicted at the word level, and we use max-pooling to aggregate subwords into word representations

Q: What are the advantages of DIFFUSIONNER over previous models?
A: DIFFUSIONNER can achieve better performance while maintaining a faster inference speed with minimal parameter scale compared to previous generation-based models.
evidence: we ﬁnd that DIFFUSIONNER could achieve better perfor- mance while maintaining a faster inference speed with minimal parameter scale.
```

### 2.5. Evaluate user answer

- syntactic evaluation: 영어 문법과 표현에 대한 평가
    - ChatGPT 사용하여 수정된 문장 생성
- semantic evaluation: pseudo 정답과 예측 정답의 의미적 유사도 평가
    - BERTScore 사용

```python
def edit_english(chat, text):
    system_content = (
        'You are a English spelling corrector and improver. '
        'User will give you an English text and you will answer the corrected and improved version of the text. ' 
        'Reply only the corrected and improved text, do not write explanations. ' 
        'If the text is perfect write "The text is perfect."'
        f'The text is "{text}"'
    )

    messages = [SystemMessage(content=system_content)]
    return run_chat(chat, messages)

bert_scorer = BERTScorer(model_type='microsoft/deberta-base-mnli')
question, answer, _ = qnas[0]
print('Question:', question)

user_answer = 'DiffusionNER is a named entity recognition model which formulates the NER task as a boundary denoising diffusion process.'

syntactic_evaluation = edit_english(chat, user_answer)
semantic_evaluation = bert_scorer.score([user_answer], [answer])[2][0].item() # P, R, F1
semantic_evaluation = round(semantic_evaluation * 100, 2)
```

결과 예시

![Untitled](https://www.notion.so/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2Fe6403240-fb22-41a1-8994-22c59a589900%2FUntitled.png?id=11d68ba6-ae76-4248-a138-84e2cc71afa5&table=block&spaceId=333f96cf-396d-45ff-8331-232d41bd4d55&width=2000&userId=ab2ec52b-c260-48c9-897a-d976ebe755f2&cache=v2)

## 3. Future works

- Component 개선
    - 공통 질문
    - prompt engineering
    - evaluation algorithm
    - distillation to open-source llm
- UI 개발
