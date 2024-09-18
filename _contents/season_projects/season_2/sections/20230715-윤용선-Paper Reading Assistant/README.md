## 0. Remind

- 논문과 관련된 질문을 생성하고 나의 답변을 채점할 수 있는 시스템 개발
- method
    1. Download paper: Arxiv에서 논문 정보와 pdf 다운로드
    2. Preprocess paper: pdf에서 논문 text를 추출 후 전처리
    3. Generate questions: 논문을 읽고 관련된 질문 생성
    4. Answer questions: 질문에 대한 pseudo 정답 생성
    5. Evaluate user answer: pseudo 정답을 기준으로 사람의 답변 채점

## 1. Problems

- 중요하지 않은 텍스트가 많다. (reference, table caption 등) → PDF layout analysis
- 채점에 사용하는 BERTScore 모델의 크기가 크다. → Model Distillation

## 2. PDF layout analysis

### 2.1. Introduction

- 논문은 대체로 서론, 관련 연구, 방법론, 실험, 결론과 같은 구조로 구성되어 있다.
- 하지만 PDF로 배포된 논문에서 위와 같은 구조를 자동으로 파악하는 것은 쉽지 않다.
- 이러한 문제를 해결하기 위해 다양한 Document-Image Understanding 모델들이 제안되었다.
- 그 중 **VI**sual **LA**yout (VILA) 모델을 사용하여 논문의 구조를 추출하는 과정을 진행해보았다.

### 2.2. VILA: Visual LAyout

- VILA: Improving structured content extraction from scientific PDFs using visual layout groups
- 문서의 구조를 인식하는 Document Layout Analysis 문제는 주로 token classification (NLP-centric)이나 object detection (vision-centric) 문제로 치환하여 해결한다.
    - VILA의 경우 token classification 방식을 사용했다.
- VILA는 line 또는 block과 같은 visual group 내의 token들은 같은 라벨을 가진다는 “group uniformity assumption”을 강조한다.
- group uniformity assumption를 따르기 위해 두 가지 방법을 제안한다.
    - I-VILA: group 사이에 speical token [BLK] 입력
    - H-VILA: group 별로 self-attention 후 group representation 추출하여 group 간 self-attention 진행
- 성능은 I-VILA가 뛰어나지만, 효율성은 H-VILA가 더 좋다.

![Illustration of the H-VILA](https://www.notion.so/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2F76654d79-f65b-4a39-a45a-324c8ff684c4%2FUntitled.png?id=3094eda7-106c-40cf-86fb-7acf58839dad&table=block&spaceId=333f96cf-396d-45ff-8331-232d41bd4d55&width=2000&userId=ab2ec52b-c260-48c9-897a-d976ebe755f2&cache=v2)

Illustration of the H-VILA [1]

### 2.3. Code

- VILA를 Docbank 데이터셋으로 fine-tuning한 모델 사용 [2]
- [VILA official repository](https://github.com/allenai/vila/tree/main)에서 공개한 코드와 모델 사용

**2.3.1. Setup**

clone repsoitory

```python
!git clone https://github.com/allenai/vila.git
import sys
sys.path.append('vila/src')
```

import libraries

```python
import layoutparser as lp
from collections import defaultdict

from utils import download_paper
from vila.pdftools.pdf_extractor import PDFExtractor
from vila.predictors import HierarchicalPDFPredictor, LayoutIndicatorPDFPredictor
```

**2.3.2. Modules**

- predict: pdf를 읽은 뒤 token classification 진행
- construct_token_groups: 같은 class로 예측된 token끼리 그룹화
- join_group_text: 같은 group의 token들을 하나의 text로 묶음
    - token의 bbox를 기준으로 띄어쓰기 유무 결정
- construct_section_groups: section(서론, 본론, 결론 등)과 section에 해당하는 paragraph 추출

```python
def predict(pdf_path, pdf_extractor, vision_model, layout_model):
    page_tokens, page_images = pdf_extractor.load_tokens_and_image(pdf_path)

    pred_tokens = []
    for page_token, page_image in zip(page_tokens, page_images):
        blocks = vision_model.detect(page_image)
        page_token.annotate(blocks=blocks)
        pdf_data = page_token.to_pagedata().to_dict()
        pred_tokens += layout_model.predict(pdf_data, page_token.page_size)

    return pred_tokens
    

def construct_token_groups(pred_tokens):
    groups, group, group_type, prev_bbox = [], [], None, None
    
    for token in pred_tokens:
        if group_type is None:
            is_continued = True
            
        elif token.type == group_type:
            if group_type == 'section':
                is_continued = abs(prev_bbox[3] - token.coordinates[3]) < 1.
            else:
                is_continued = True

        else:
            is_continued = False

        
        # print(token.text, token.type, is_continued)
        group_type = token.type
        prev_bbox = token.coordinates
        if is_continued:
            group.append(token)
        
        else:
            groups.append(group)
            group = [token]
    
    if group:
        groups.append(group)

    return groups

def join_group_text(group):
    text = ''
    prev_bbox = None
    for token in group:
        if not text:
            text += token.text
    
        else:        
            if abs(prev_bbox[2] - token.coordinates[0]) > 2:
                text += ' ' + token.text
    
            else:
                text += token.text
    
        prev_bbox = token.coordinates
    return text

def construct_section_groups(token_groups):
    section_groups = defaultdict(list)

    section = None
    for group in token_groups:
        group_type = group[0].type
        group_text = join_group_text(group)
        
        if group_type == 'section':
            section = group_text
            section_groups[section]
    
        elif group_type == 'paragraph' and section is not None:
            section_groups[section].append(group_text)

    section_groups = {k: ' '.join(v) for k,v in section_groups.items()}
    return section_groups
```

**2.3.3. Run**

prepare models

```python
pdf_extractor = PDFExtractor("pdfplumber")
vision_model = lp.EfficientDetLayoutModel("lp://PubLayNet") 
layout_model = HierarchicalPDFPredictor.from_pretrained("allenai/hvila-row-layoutlm-finetuned-docbank")
```

inference

```python
pdf_path = '2307.03170v1.pdf'
pred_tokens = predict(pdf_path, pdf_extractor, vision_model, layout_model)
token_groups = construct_token_groups(pred_tokens)
section_groups = construct_section_groups(token_groups)
```

**2.3.4. Results**

section 목록

```python
sections = list(section_groups.keys())
print(sectiosn)
```

![Untitled](https://www.notion.so/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2F741b6e2f-7983-495b-affc-21582756dec1%2FUntitled.png?id=92d44902-dd14-4b8d-bc59-a1d4702e8a17&table=block&spaceId=333f96cf-396d-45ff-8331-232d41bd4d55&width=2000&userId=ab2ec52b-c260-48c9-897a-d976ebe755f2&cache=v2)

section text

```python
print(section_groups['6 Limitations and future work'])
```

![Untitled](https://www.notion.so/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2Ff491e51e-8f2a-4010-90c3-59ea6c17521e%2FUntitled.png?id=057684a4-a7c6-45bd-ae23-273b24261b24&table=block&spaceId=333f96cf-396d-45ff-8331-232d41bd4d55&width=2000&userId=ab2ec52b-c260-48c9-897a-d976ebe755f2&cache=v2)


## 3. BERTScore Distillation

### 3.1. Introduction

- BERTScore는 pretrained language model을 사용하여 두 문장의 유사도를 측정하는 방법이다. 주로 번역, 요약 등 문장 생성 모델을 평가하는 데 사용한다 [3].
- language model의 크기가 클수록 BERTScore와 Human evalution의 상관 관계가 큰 경향이 있다.
- 하지만 큰 모델은 어플리케이션에서 실시간으로 사용되기 어렵다는 단점이 있다.
- 이를 해결하고자 Knowledge distillation을 통해 작은 모델이 큰 모델의 BERTScore를 따라하도록 학습시켰다.
- 결과 모델: [yongsun-yoon/minilmv2-bertscore-distilled](https://huggingface.co/yongsun-yoon/minilmv2-bertscore-distilled)

![모델별 BERTScore와 Human evaluation과의 상관관계 [4]](https://www.notion.so/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2F88e4b751-5bfa-4057-9aba-89f25e010b33%2FUntitled.png?id=3fa5fba0-8018-4c77-b7da-d032ad700feb&table=block&spaceId=333f96cf-396d-45ff-8331-232d41bd4d55&width=2000&userId=ab2ec52b-c260-48c9-897a-d976ebe755f2&cache=v2)

모델별 BERTScore와 Human evaluation과의 상관관계 [4]

### 3.2. Setup

- student model은 경량화된 모델 [nreimers/MiniLMv2-L6-H384-distilled-from-RoBERTa-Large](https://huggingface.co/nreimers/MiniLMv2-L6-H384-distilled-from-RoBERTa-Large)를 사용
- teacher model은 3위에 랭크된 [microsoft/deberta-large-mnli](https://huggingface.co/microsoft/deberta-large-mnli) 사용

```python
import math
import wandb
import easydict
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm

import torch
import torch.nn.functional as F

import huggingface_hub
from bert_score import BERTScorer
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModel

cfg = easydict.EasyDict(
    device = 'cuda:0',
    student_name = 'nreimers/MiniLMv2-L6-H384-distilled-from-RoBERTa-Large',
    teacher_name = 'microsoft/deberta-large-mnli',
    teacher_layer_idx = 18,
    lr = 5e-5,
    batch_size = 8,
    num_epochs = 5
)
```

### 3.3. Data

- 어느정도 유사성이 있는 문장쌍을 사용하기 위해 [GLUE MNLI](https://huggingface.co/datasets/glue/viewer/mnli) 데이터셋 선택

```python
class Dataset(torch.utils.data.Dataset):
    def __init__(self, data, text1_key, text2_key):
        self.data = data
        self.text1_key = text1_key
        self.text2_key = text2_key

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        text1 = item[self.text1_key]
        text2 = item[self.text2_key]
        return text1, text2

    def collate_fn(self, batch):
        texts1, texts2 = zip(*batch)
        return texts1, texts2

    def get_dataloader(self, batch_size, shuffle):
        return torch.utils.data.DataLoader(self, batch_size=batch_size, shuffle=shuffle)

data = load_dataset('glue', 'mnli')

train_data = data['train']
train_data = train_data.train_test_split(train_size=80000)['train']
train_dataset = Dataset(train_data, 'premise', 'hypothesis')
train_loader = train_dataset.get_dataloader(cfg.batch_size, True)

test_data = data['validation_mismatched'].train_test_split(test_size=4000)['test']
test_dataset = Dataset(test_data, 'premise', 'hypothesis')
test_loader = test_dataset.get_dataloader(cfg.batch_size, False)
```

### 3.4. Model

```python
teacher_tokenizer = AutoTokenizer.from_pretrained(cfg.teacher_name)
teacher_model = AutoModel.from_pretrained(cfg.teacher_name)
_ = teacher_model.eval().requires_grad_(False).to(cfg.device)

student_tokenizer = AutoTokenizer.from_pretrained(cfg.student_name)
student_model = AutoModel.from_pretrained(cfg.student_name)
_ = student_model.train().to(cfg.device)
optimizer = torch.optim.Adam(student_model.parameters(), lr=cfg.lr)
```

### 3.5. Train

- 두 문장의 cross attention score를 계산한 뒤 teacher의 attention 분포를 student가 따라하도록 학습
- loss function으로 두 분포간의 차이를 계산하는 kl divergence를 사용
- 이때 teacher model과 student model의 tokenizer가 다를 경우 token 단위의 비교가 불가능하다. 이를 해결하기 위해 token을 word 단위로 변환했다.

```python
def get_word_embeds(model, tokenizer, texts, layer_idx=-1, max_length=384):
    inputs = tokenizer(texts, padding=True, truncation=True, max_length=max_length, return_tensors='pt').to(model.device)
    outputs = model(**inputs, output_hidden_states=True)
    
    num_texts = inputs.input_ids.size(0)
    token_embeds = outputs.hidden_states[layer_idx]

    batch_word_embeds = []
    for i in range(num_texts):
        text_word_embeds = []

        j = 0
        while True:
            token_span = inputs.word_to_tokens(i, j)
            if token_span is None: break

            word_embed = token_embeds[i][token_span.start:token_span.end].mean(dim=0)
            text_word_embeds.append(word_embed)
            j += 1

        text_word_embeds = torch.stack(text_word_embeds, dim=0).unsqueeze(0) # (1, seq_length, hidden_dim)
        batch_word_embeds.append(text_word_embeds) 

    return batch_word_embeds

def kl_div_loss(s, t, temperature):
    if len(s.size()) != 2:
        s = s.view(-1, s.size(-1))
        t = t.view(-1, t.size(-1))

    s = F.log_softmax(s / temperature, dim=-1)
    t = F.softmax(t / temperature, dim=-1)
    return F.kl_div(s, t, reduction='batchmean') * (temperature ** 2)

def transpose_for_scores(h, num_heads):
    batch_size, seq_length, dim = h.size()
    head_size = dim // num_heads
    h = h.view(batch_size, seq_length, num_heads, head_size)
    return h.permute(0, 2, 1, 3) # (batch, num_heads, seq_length, head_size)

def attention(h1, h2, num_heads, attention_mask=None):
    # assert h1.size() == h2.size()
    head_size = h1.size(-1) // num_heads
    h1 = transpose_for_scores(h1, num_heads) # (batch, num_heads, seq_length, head_size)
    h2 = transpose_for_scores(h2, num_heads) # (batch, num_heads, seq_length, head_size)

    attn = torch.matmul(h1, h2.transpose(-1, -2)) # (batch_size, num_heads, seq_length, seq_length)
    attn = attn / math.sqrt(head_size)
    if attention_mask is not None:
        attention_mask = attention_mask[:, None, None, :]
        attention_mask = (1 - attention_mask) * -10000.0
        attn = attn + attention_mask

    return attn

def train_epoch(
    teacher_model, teacher_tokenizer, 
    student_model, student_tokenizer,
    train_loader,
    teacher_layer_idx,
):
    
    student_model.train()
    pbar = tqdm(train_loader)
    for texts1, texts2 in pbar:
        teacher_embeds1 = get_word_embeds(teacher_model, teacher_tokenizer, texts1, layer_idx=teacher_layer_idx)
        teacher_embeds2 = get_word_embeds(teacher_model, teacher_tokenizer, texts2, layer_idx=teacher_layer_idx)
        
        student_embeds1 = get_word_embeds(student_model, student_tokenizer, texts1, layer_idx=-1)
        student_embeds2 = get_word_embeds(student_model, student_tokenizer, texts2, layer_idx=-1)
    
        teacher_scores1 = [attention(e1, e2, 1) for e1, e2 in zip(teacher_embeds1, teacher_embeds2)]
        student_scores1 = [attention(e1, e2, 1) for e1, e2 in zip(student_embeds1, student_embeds2)]
        loss1 = torch.stack([kl_div_loss(ts, ss, temperature=1.) for ts, ss in zip(teacher_scores1, student_scores1)]).mean()
        
        teacher_scores2 = [attention(e2, e1, 1) for e1, e2 in zip(teacher_embeds1, teacher_embeds2)]
        student_scores2 = [attention(e2, e1, 1) for e1, e2 in zip(student_embeds1, student_embeds2)]
        loss2 = torch.stack([kl_div_loss(ts, ss, temperature=1.) for ts, ss in zip(teacher_scores2, student_scores2)]).mean()
        
        loss = (loss1 + loss2) * 0.5
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        log = {'loss': loss.item(), 'loss1': loss.item(), 'loss2': loss2.item()}
        wandb.log(log)
        pbar.set_postfix(log)

def test_epoch(
    teacher_model, teacher_tokenizer, 
    student_model, student_tokenizer,
    test_loader,
    teacher_layer_idx,
):
    student_model.eval()
    test_loss, num_data = 0, 0
    for texts1, texts2 in test_loader:
        with torch.no_grad():
            teacher_embeds1 = get_word_embeds(teacher_model, teacher_tokenizer, texts1, layer_idx=teacher_layer_idx)
            teacher_embeds2 = get_word_embeds(teacher_model, teacher_tokenizer, texts2, layer_idx=teacher_layer_idx)
            
            student_embeds1 = get_word_embeds(student_model, student_tokenizer, texts1, layer_idx=-1)
            student_embeds2 = get_word_embeds(student_model, student_tokenizer, texts2, layer_idx=-1)
    
        teacher_scores1 = [attention(e1, e2, 1) for e1, e2 in zip(teacher_embeds1, teacher_embeds2)]
        student_scores1 = [attention(e1, e2, 1) for e1, e2 in zip(student_embeds1, student_embeds2)]
        loss1 = torch.stack([kl_div_loss(ts, ss, temperature=1.) for ts, ss in zip(teacher_scores1, student_scores1)]).mean()
        
        teacher_scores2 = [attention(e2, e1, 1) for e1, e2 in zip(teacher_embeds1, teacher_embeds2)]
        student_scores2 = [attention(e2, e1, 1) for e1, e2 in zip(student_embeds1, student_embeds2)]
        loss2 = torch.stack([kl_div_loss(ts, ss, temperature=1.) for ts, ss in zip(teacher_scores2, student_scores2)]).mean()
        
        loss = (loss1 + loss2) * 0.5
        batch_size = len(texts1)
        test_loss += loss.item() * batch_size
        num_data += batch_size

    test_loss /= num_data
    return test_loss

wandb.init(project='bert-score-distillation')

best_loss = 1e10
for ep in range(cfg.num_epochs):
    train_epoch(teacher_model, teacher_tokenizer, student_model, student_tokenizer, train_loader, cfg.teacher_layer_idx)
    test_loss = test_epoch(teacher_model, teacher_tokenizer, student_model, student_tokenizer, test_loader, cfg.teacher_layer_idx)

    print(f'ep {ep:02d} | loss {test_loss:.3f}')
    if test_loss < best_loss:
        student_model.save_pretrained('checkpoint')
        student_tokenizer.save_pretrained('checkpoint')
        best_loss = test_loss
        wandb.log({'test_loss': test_loss})
```

![W&B Chart 2023. 7. 5. 오전 7_25_51.png](https://www.notion.so/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2Fcb10ea09-bec7-4297-a1bd-be4ff74f993b%2FWB_Chart_2023._7._5._%25E1%2584%258B%25E1%2585%25A9%25E1%2584%258C%25E1%2585%25A5%25E1%2586%25AB_7_25_51.png?id=019f7c26-ec40-4ad1-99c4-49437602a1b5&table=block&spaceId=333f96cf-396d-45ff-8331-232d41bd4d55&width=2000&userId=ab2ec52b-c260-48c9-897a-d976ebe755f2&cache=v2)

### 3.6. Evaluate

- 학습 결과 teacher model과의 BERTScore 상관관계가 0.806에서 0.936으로 향상

```python
def calculate_score(scorer, loader):
    scores = []
    for texts1, texts2 in tqdm(loader):
        P, R, F = scorer.score(texts1, texts2)
        scores += F.tolist()
    return scores

teacher_scorer = BERTScorer(model_type=cfg.teacher_name, num_layers=cfg.teacher_layer_idx)
student_scorer = BERTScorer(model_type=cfg.student_name, num_layers=6)
distilled_student_scorer = BERTScorer(model_type='checkpoint', num_layers=6)

teacher_scores = calculate_score(teacher_scorer, test_loader)
student_scores = calculate_score(student_scorer, test_loader)
distilled_scores = calculate_score(distilled_student_scorer, test_loader)

scores = pd.DataFrame({'teacher': teacher_scores, 'student': student_scores, 'distilled': distilled_scores})
scores.corr().round(3)
```

![Untitled](https://www.notion.so/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2F60a70751-e296-4480-80dd-c609ee5a2b20%2FUntitled.png?id=42384096-ca21-4894-a8ac-45f338148820&table=block&spaceId=333f96cf-396d-45ff-8331-232d41bd4d55&width=2000&userId=ab2ec52b-c260-48c9-897a-d976ebe755f2&cache=v2)

- scatterplot 상에서도 distillation한 후에 teacher의 BERTScore를 더 잘 따라하는 것을 확인할 수 있다.

![Untitled](https://www.notion.so/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2F774fe593-5977-46cc-9a48-42504b718f36%2FUntitled.png?id=fd7d9077-5d93-484d-a7cd-fec9496bc9b7&table=block&spaceId=333f96cf-396d-45ff-8331-232d41bd4d55&width=2000&userId=ab2ec52b-c260-48c9-897a-d976ebe755f2&cache=v2)

## Reference

[1] Shen, Z., Lo, K., Wang, L. L., Kuehl, B., Weld, D. S., & Downey, D. (2022). VILA: Improving structured content extraction from scientific PDFs using visual layout groups. *Transactions of the Association for Computational Linguistics*, *10*, 376-392.ISO 690

[2] Li, M., Xu, Y., Cui, L., Huang, S., Wei, F., Li, Z., & Zhou, M. (2020). DocBank: A benchmark dataset for document layout analysis. *arXiv preprint arXiv:2006.01038*.

[3] Zhang, T., Kishore, V., Wu, F., Weinberger, K. Q., & Artzi, Y. (2019). Bertscore: Evaluating text generation with bert. *arXiv preprint arXiv:1904.09675*.

[4] https://github.com/Tiiiger/bert_score
