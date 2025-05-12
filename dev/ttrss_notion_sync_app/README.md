# TTRSS-Notion 동기화 도구

이 도구는 Tiny Tiny RSS(TTRSS)의 항목을 Notion의 "읽을거리" 데이터베이스와 동기화하는 모듈화된 Python 애플리케이션입니다.

## 주요 기능

- TTRSS 피드 항목을 자동으로 Notion 데이터베이스에 동기화
- Notion 데이터베이스 변경사항 추적 및 동기화 테이블 업데이트
- 중복 항목 감지 및 처리
- 제목 기반 항목 매칭을 통한 효율적인 동기화 상태 관리
- RSS 피드의 HTML 내용을 텍스트로 변환하여 Notion에 저장
- 비어있는 Notion 항목 내용 자동 채우기
- 로깅 기능을 통한 동기화 과정 모니터링

## 📚 시스템 개요

이 시스템은 TTRSS에서 구독하는 RSS 피드 항목들을 Notion 데이터베이스로 자동 동기화해줍니다. 이를 통해 RSS 피드의 내용을 Notion에서 체계적으로 관리하고 참조할 수 있습니다.

## 🔄 동기화 원리

동기화 과정은 세 개의 주요 요소로 이루어집니다:

1. **TTRSS 데이터베이스**: RSS 피드 항목이 저장되는 곳
2. **Notion 데이터베이스**: 최종적으로 보고 관리하려는 곳
3. **동기화 테이블(ttrss_notion_sync)**: TTRSS와 Notion 사이의 중계자 역할

## 아키텍처

이 애플리케이션은 다음과 같은 모듈식 구조로 설계되었습니다:

```
ttrss_notion_sync_app/
├── config.py          # 설정 정보 (DB 연결, Notion API 키 등)
├── db_manager.py      # TTRSS DB 및 동기화 테이블 관리
├── notion_manager.py  # Notion API 연결 및 관리
├── sync_manager.py    # 동기화 로직 구현
├── main.py            # 명령줄 인터페이스
├── run_sync.py        # 사용하기 쉬운 동기화 스크립트
└── .env               # 환경 변수 (DB 인증정보, API 키 등)
```

## 설치 요구사항

### 1. Python 패키지 설치

```bash
pip install psycopg2-binary notion-client tqdm python-dotenv beautifulsoup4
```

또는 제공된 requirements.txt 파일을 사용:

```bash
pip install -r requirements.txt
```

### 2. Docker를 사용한 TTRSS 설치 (선택사항)

TTRSS가 아직 설치되지 않은 경우, Docker를 사용하여 쉽게 설정할 수 있습니다:

```bash
# PostgreSQL 데이터베이스 컨테이너 생성
docker run -d --name ttrss-db \
  -e POSTGRES_PASSWORD=handbook12 \
  -e POSTGRES_USER=ttrss \
  -e POSTGRES_DB=ttrss \
  -p 5432:5432 \
  postgres:13

# TTRSS 애플리케이션 컨테이너 생성
docker run -d --name ttrss \
  -p 8080:80 \
  -e SELF_URL_PATH=http://localhost:8080/ \
  -e DB_HOST=host.docker.internal \
  -e DB_PORT=5432 \
  -e DB_NAME=ttrss \
  -e DB_USER=ttrss \
  -e DB_PASS=handbook12 \
  -e ADMIN_USER=admin \
  -e ADMIN_PASS=handbook12 \
  cthulhoo/ttrss:latest
```

TTRSS 설치 후, http://localhost:8080/ 에서 접근할 수 있습니다. (기본 로그인: admin/handbook12)

## 환경 변수 설정

애플리케이션을 실행하기 전에 `.env` 파일을 만들고 다음 환경 변수를 설정해야 합니다:

```
# Database configuration
DB_HOST=your_db_host
DB_PORT=your_db_port
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# Notion configuration
NOTION_DATABASE_ID=your_notion_database_id
NOTION_API_KEY=your_notion_api_key
```

## 🚶‍♂️ 동기화 흐름 설명

### 1단계: Notion에서 동기화 테이블로
- Notion에 있는 모든 항목은 동기화 테이블에 복사됩니다
- Notion은 "진실의 원천(source of truth)"으로 취급됩니다
- Notion에서 항목이 삭제되면 동기화 테이블에서도 삭제됩니다
- Notion 항목은 `synced_to_notion = TRUE`로 설정됩니다(이미 Notion에 있으므로)

### 2단계: TTRSS에서 동기화 테이블로
- TTRSS의 새로운 항목들이 동기화 테이블에 추가됩니다
- 이때 기본적으로 `synced_to_notion = FALSE`로 설정됩니다(아직 Notion에 동기화되지 않았으므로)
- TTRSS에서 항목이 삭제되어도 동기화 테이블에서는 유지됩니다
- 동기화는 일방향으로만 이루어집니다(TTRSS → 동기화 테이블)

### 3단계: 제목 기반 항목 매칭
- 동기화 테이블 내에서 동일한 제목을 가진 항목들을 찾습니다
- Notion 항목과 동일한 제목의 TTRSS 항목을 발견하면:
  - TTRSS 항목의 `synced_to_notion` 값을 `TRUE`로 설정합니다
  - 이를 통해 중복 동기화를 방지합니다
- Notion 항목의 content가 비어있고 TTRSS 항목에 content가 있으면:
  - TTRSS의 content를 Notion 항목에 복사합니다
  - HTML 내용을 텍스트로 변환하여 저장합니다
  - 출처를 'ttrss'로 변경합니다

### 4단계: 동기화 테이블에서 Notion으로
- `synced_to_notion = FALSE`인 항목들만 Notion으로 동기화됩니다
- 이전 단계에서 이미 동일 제목이 있는 항목들은 `TRUE`로 설정되었으므로 제외됩니다
- 새로운 항목들만 Notion에 추가됩니다

## 💡 주요 기능 설명

### 제목 기반 매칭
- 동일한 제목을 가진 항목들은 자동으로 매칭됩니다
- 이를 통해 같은 내용을 중복으로 Notion에 올리지 않습니다

### 내용(Content) 자동 채우기
- Notion 항목에 내용이 비어있는 경우:
  1. 동일 제목의 TTRSS 항목이 동기화 테이블에 있으면 그 내용을 사용합니다
  2. 동기화 테이블에 없거나 내용이 비어있으면 원본 TTRSS 데이터베이스에서 찾습니다
  3. HTML 내용은 읽기 쉽게 텍스트로 변환됩니다

### HTML → 텍스트 변환
- RSS 피드의 HTML 내용을 깔끔한 텍스트로 변환합니다
- Notion에서 읽기 쉬운 형태로 표시됩니다

## 사용 방법

### 전체 동기화 실행 (권장)

```bash
python -m ttrss_notion_sync_app.main full-sync
```

또는 간편 스크립트 사용:

```bash
python run_sync.py
```

이 명령은 위에서 설명한 모든 단계(1~4)를 자동으로 수행합니다.

### Notion 데이터베이스 확인

```bash
python -m ttrss_notion_sync_app.main check-notion
```

### TTRSS 항목 확인

```bash
python -m ttrss_notion_sync_app.main check-ttrss
```

### Notion 데이터베이스와 동기화 테이블 비교

```bash
python -m ttrss_notion_sync_app.main compare --source notion
```

### TTRSS 항목과 동기화 테이블 비교

```bash
python -m ttrss_notion_sync_app.main compare --source ttrss
```

### Notion 데이터베이스와 동기화 테이블 동기화

```bash
python -m ttrss_notion_sync_app.main sync-notion
```

### TTRSS 항목과 동기화 테이블 동기화

```bash
python -m ttrss_notion_sync_app.main sync-ttrss
```

### 동기화 테이블에서 Notion으로 동기화

```bash
python -m ttrss_notion_sync_app.main sync-to-notion
```

## 🏁 이상적인 사용 시나리오

1. TTRSS에서 새로운 RSS 항목들이 수신됩니다
2. `full-sync` 명령어를 실행합니다
3. 새 항목들이 자동으로 Notion에 추가됩니다
4. 이미 제목이 같은 항목은 중복 추가되지 않습니다
5. Notion의 비어있는 내용(Why it matters) 필드는 TTRSS의 내용으로 자동 채워집니다
6. 모든 내용이 HTML이 아닌 읽기 쉬운 텍스트로 변환됩니다

## 동기화 처리 원칙

1. **Notion 기준 동기화**:
   - Notion에 있는 항목은 반드시 동기화 테이블에도 유지됨
   - Notion에서 삭제된 항목은 동기화 테이블에서도 삭제됨
   - Notion 항목은 동기화 테이블에 추가될 때 `synced_to_notion = TRUE`로 설정됨

2. **TTRSS에서 동기화 테이블로 단방향 동기화**:
   - TTRSS의 새 항목은 동기화 테이블에 추가됨
   - TTRSS에서 항목이 삭제되더라도 동기화 테이블에서는 유지됨
   - Notion을 기준으로 데이터 일관성 유지

3. **동기화 테이블에서 Notion으로 단방향 동기화**:
   - 동기화 테이블의 새 항목(아직 Notion에 동기화되지 않은)은 Notion에 추가됨
   - 이미 동기화된 항목은 다시 동기화되지 않음

4. **제목 기반 항목 매칭**:
   - 동일한 제목을 가진 TTRSS 항목과 Notion 항목은 자동으로 매칭됨
   - 제목이 일치하는 항목이 발견되면 TTRSS 항목의 `synced_to_notion` 상태가 `TRUE`로 업데이트됨
   - Notion 항목의 내용이 비어있으면 TTRSS 항목의 내용으로 자동 채워짐
   - 이를 통해 중복 동기화를 방지하고 효율적인 동기화 관리 가능

## 보안 참고사항

- 절대로 `.env` 파일을 버전 관리 시스템(예: git)에 커밋하지 마세요.
- 프로덕션 환경에서는 `.env.example` 파일을 만들어 어떤 환경 변수가 필요한지 설명하되, 실제 값은 포함하지 마세요.

## 문제 해결

- **데이터베이스 연결 오류**: 데이터베이스 호스트, 포트, 인증 정보가 올바른지 확인하세요.
- **Notion API 오류**: API 키가 올바르고 만료되지 않았는지 확인하세요.
- **동기화 실패**: 로그 파일을 확인하여 구체적인 오류 메시지를 확인하세요.
- **내용이 비어있는 Notion 항목**: 전체 동기화(full-sync)를 실행하여 TTRSS 내용으로 자동 채우기를 시도하세요.

자세한 사용법과 고급 설정은 `USAGE_GUIDE.md`를 참조하세요.
