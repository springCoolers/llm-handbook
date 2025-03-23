# TTRSS-Notion 동기화 도구

이 도구는 Tiny Tiny RSS(TTRSS)의 항목을 Notion의 "읽을거리" 데이터베이스와 동기화하는 모듈화된 Python 애플리케이션입니다.

## 파일 구조

- **config.py**: 설정 정보 (데이터베이스 연결 정보, Notion API 키 등)
- **db_manager.py**: TTRSS 데이터베이스 연결 및 관리 기능
- **notion_manager.py**: Notion API 연결 및 관리 기능
- **sync_manager.py**: 동기화 로직 구현
- **main.py**: 메인 실행 모듈, 명령줄 인터페이스 제공
- **.env**: 민감한 환경 변수 저장 (데이터베이스 인증 정보, API 키 등)

## 설치 요구사항

```bash
pip install psycopg2-binary notion-client tqdm python-dotenv
```

또는 제공된 requirements.txt 파일을 사용하여 설치하세요:

```bash
pip install -r requirements.txt
```

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

## 사용 방법

### 전체 동기화 실행

```bash
python -m ttrss_notion_sync_app.main full-sync
```

이 명령은 다음 단계를 수행합니다:
1. Notion 데이터베이스와 동기화 테이블 간 동기화 (Notion을 기준으로)
2. TTRSS 항목과 동기화 테이블 간 동기화 (새 항목만 추가)
3. 동기화 테이블의 새 항목을 Notion에 동기화

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

## 동기화 처리 원칙

1. **Notion 기준 동기화**:
   - Notion에 있는 항목은 반드시 동기화 테이블에도 유지됨
   - Notion에서 삭제된 항목은 동기화 테이블에서도 삭제됨

2. **TTRSS에서 동기화 테이블로 단방향 동기화**:
   - TTRSS의 새 항목은 동기화 테이블에 추가됨
   - TTRSS에서 항목이 삭제되더라도 동기화 테이블에서는 유지됨
   - Notion을 기준으로 데이터 일관성 유지

3. **동기화 테이블에서 Notion으로 단방향 동기화**:
   - 동기화 테이블의 새 항목(아직 Notion에 동기화되지 않은)은 Notion에 추가됨
   - 이미 동기화된 항목은 다시 동기화되지 않음

## 보안 참고사항

- 절대로 `.env` 파일을 버전 관리 시스템(예: git)에 커밋하지 마세요.
- 프로덕션 환경에서는 `.env.example` 파일을 만들어 어떤 환경 변수가 필요한지 설명하되, 실제 값은 포함하지 마세요.
