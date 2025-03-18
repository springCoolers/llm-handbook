New_AI_Model_Release = """
아래의 컨텐츠를 보고 주요 내용을 템플릿에 맞게 재구성해줘.

Title: {title}
Contents: {content}

**Output Templete (Markdown):**

## **Introducing [모델 이름]: 최신 AI 모델 공개!**
**🔍 오늘의 주제: [모델 요약]**
최신 AI 모델 **[모델 이름]**이 출시되었습니다! 이번 모델은 **[핵심 개선점 또는 특징 요약]**을 통해 **[적용 분야 및 주요 기대 효과]**에 강력한 성능을 제공합니다.
🔗 **공식 발표:** [출처 링크 (OpenAI, Meta, Google AI 등)]
---

### 🏆 **[모델 이름] 주요 특징**
✅ **[기능 1]** - [설명]
✅ **[기능 2]** - [설명]
✅ **[기능 3]** - [설명]

📌 **주요 개선점 (이전 모델과 비교)**
| 기능 | 이전 모델 ([이전 모델 이름]) | 새로운 모델 ([모델 이름]) |
| --- | --- | --- |
| **정확도(%)** | XX.X% | XX.X% |
| **처리 속도(ms)** | XXXms | XXXms |
| **메모리 사용량** | XXGB | XXGB |
| **지원 언어** | [언어 목록] | [언어 목록] |

### 📌 추가 정보

🔗 [공식 블로그 링크]
📄 [논문 링크]
👨‍💻 [GitHub / Hugging Face Repository]"""

New_Tool_Introduction = """
아래의 컨텐츠를 보고 주요 내용을 템플릿에 맞게 재구성해줘.

Title: {title}
Contents: {content}

**Output Templete (Markdown):**
## 🛠️ New Tool Introduction: **[툴/라이브러리명]**

**🔍 오늘의 주제: [툴 요약]**

최신 AI 툴 **[툴 이름]**이 출시되었습니다! 이번 툴은 **[주요 기능 또는 특징 요약]**을 통해 **[적용 분야 및 주요 기대 효과]**에 강력한 성능을 제공합니다.

👨‍💻 [GitHub / Hugging Face Repository]

### 🔥 주요 기능

- **[기능 1]**: [설명]
- **[기능 2]**: [설명]
- **[기능 3]**: [설명]

### 📝 간단한 사용법

```python
# [툴명]을 사용한 간단한 코드 예제
import [툴명]

result = [툴명].run("[입력값]")
print(result)
```

### 🎯 실전 활용 사례
💡 **사례 1**: [사용 사례 예시]
💡 **사례 2**: [사용 사례 예시]

### 📌 더 알아보기
🔗 [공식 블로그 링크]
📄 [문서 링크]
"""

Technical_Deep_Dive = """
아래의 컨텐츠를 보고 주요 내용을 템플릿에 맞게 재구성해줘.

Title: {title}
Contents: {content}

**Output Templete (Markdown):**
## 🧠 Deep Dive: [기술 개념 또는 주제]
**🔍 오늘의 주제: [한줄 핵심 개념 요약]**

### 🔹 **[주제]란?**
[주제의 기본 개념 설명]
✅ **어디에 사용될까?** - [사용 사례]
✅ **왜 중요한가?** - [기술적 또는 산업적 중요성]

### **[주제]의 동작 원리**
🛠️ **핵심 알고리즘** - [기본 수식, 모델 구조, 프로세스]
🛠️ **구현 방식** - [작동 방식의 시각적 또는 코드 예제]
🛠️ **성능 최적화** - [속도, 메모리 효율성, 최신 개선 사항]

### 🏗️ **실제 적용 사례**
💡 **기업/프로젝트 적용 사례** - [실제 사례 분석]

### 📌 **한계점과 해결 방안**
**현재 한계** - [성능 문제, 윤리적 문제 등]
**미래 발전 방향** - [해결 방법, 최신 연구 동향]

### 🔗 **추가 리소스**
📖 논문: [관련 논문 링크]
📚 공식 문서: [관련 기술 문서]
🎥 강의 영상: [추천 유튜브/강의]"""

Open_Source_Project = """
아래의 컨텐츠를 보고 주요 내용을 템플릿에 맞게 재구성해줘.

Title: {title}
Contents: {content}

**Output Templete (Markdown):**
## 🚀 **오픈소스 프로젝트 소개: [프로젝트 이름]**
**🔍 오늘의 주제: [프로젝트 요약]**

새로운 오픈소스 AI 프로젝트 **[프로젝트 이름]**이 등장했습니다! 이 프로젝트는 **[핵심 기능 요약]**을 제공하며, **[특정 문제 해결 또는 용도]**에 최적화되어 있습니다.
📌 **Github 링크:** [🔗 프로젝트 URL]

### 🛠️ **[프로젝트 이름]이란?**
📌 **핵심 기능:**
- ✅ **[기능 1]** - [설명]
- ✅ **[기능 2]** - [설명]
- ✅ **[기능 3]** - [설명]

### ⚙️ **설치 및 사용법**
💻 **설치 방법:**
```bash
pip install [패키지명]
# 또는 GitHub에서 직접 클론:
git clone [프로젝트 URL]
cd [프로젝트 폴더]
pip install -r requirements.txt
```

🚀 **기본 사용법:**
```python
import [라이브러리명]
model = [라이브러리명].load_model("example")
result = model.run("Hello, world!")
print(result)
```

### 🔥 **실전 활용 사례**
💡 **사용 사례 1:** [특정 분야에서 어떻게 활용될 수 있는지]
💡 **사용 사례 2:** [실제 적용된 예제 또는 프로젝트]

### 🔗 **추가 리소스**
📄 공식 문서: [링크]
🎥 튜토리얼 영상: [링크]
🌍 관련 기사: [링크]
"""

Research_Paper_Review = """
아래의 컨텐츠를 보고 주요 내용을 템플릿에 맞게 재구성해줘.

Title: {title}
Contents: {content}

**Output Templete (Markdown):**
## 🧠 **Research Paper Review: [논문 제목]**

**🔍 오늘의 주제: [핵심 연구 요약]**
최근 **[논문 제목]** 논문이 발표되었으며, 이 연구는 **[핵심 연구 주제]**에 대한 중요한 통찰을 제공합니다. 오늘은 이 논문의 주요 내용을 분석하고, AI 및 관련 분야에서 어떤 의미가 있는지 살펴보겠습니다.

🔗 **논문 링크:** [arXiv / 공식 저널 링크]
---
### 📌 **논문** 3줄 요약
**연구 질문:**
> "[이 논문이 해결하고자 하는 주요 문제]"
> 
1.
2.
3.

---
### 🏗️ **연구 방법론**
🔹 **사용된 데이터셋:** [예: COCO, ImageNet, Hugging Face 데이터셋 등]
🔹 **모델 및 기법:** [예: Transformer, CNN, RLHF 등]
🔹 **실험 환경:** [GPU, 프레임워크, 학습 시간 등]
🔹 **평가 지표:** [예: BLEU, ROUGE, Accuracy 등]
---
### 📊 **주요 연구 결과**
📌 **결과 요약:**
🔺 **[새로운 접근 방식이 기존 대비 얼마나 개선되었는지]**
📊 **결과 그래프/표:**
| 모델 | 정확도 | 속도(ms) | 메모리 사용량 |
| --- | --- | --- | --- |
| 기존 모델 | 78.4% | 250ms | 10GB |
| 제안된 모델 | 85.6% | 180ms | 8GB |
---
### 🚨 **한계점 및 향후 연구 방향**
⚠️ **현재 연구의 한계점:**
- [예: 작은 데이터셋으로만 검증됨, 특정 도메인에만 최적화됨 등]

💡 **향후 연구 방향:**
- [예: 더 큰 데이터셋에서의 성능 평가 필요, 실제 산업 적용 실험 필요 등]
---
### 🔗 **추가 리소스**
📖 **논문 링크:** [논문 원문]
🎥 **연구 발표 영상:** [링크]
💬 **관련 커뮤니티 토론:** [Reddit, Twitter, Discord 등]"""

prompt_info = [
    {
        "name":"New AI Model Release",
        "description": "Announcements of new AI models and architectures (e.g., GPT-5 release, Mistral-7B).",
        "prompt_template": New_AI_Model_Release
    },
    {
        "name":"New Tool Introduction",
        "description": "Tutorials, reviews, or walkthroughs of AI software/tools (e.g., LangChain updates, Hugging Face spaces).",
        "prompt_template": New_Tool_Introduction
    },
    {
        "name":"Technical Deep Dive",
        "description": "In-depth explanations of AI concepts, mechanisms, or architectures (e.g., 'How Transformers Work').",
        "prompt_template": Technical_Deep_Dive
    },
    {
        "name":"Open-Source Project",
        "description": "Highlights of new AI repositories and self-hosted projects (e.g., 'Self-Hosted LLM on GitHub').",
        "prompt_template": Open_Source_Project
    },
    {
        "name":"Research Paper Review",
        "description": "Summaries and breakdowns of academic AI research papers (e.g., 'Recent Paper on RLHF in LLMs').",
        "prompt_template": Research_Paper_Review
    }
]