# TTRSS-Notion 동기화 도구 사용 가이드

이 문서는 TTRSS-Notion 동기화 도구의 각 모듈과 메서드의 상세 사용법을 제공합니다.

## 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [설치 및 설정](#설치-및-설정)
   - [요구 사항](#요구-사항)
   - [TTRSS Docker 설치](#ttrss-docker-설치)
   - [애플리케이션 설치](#애플리케이션-설치)
   - [환경 변수 설정](#환경-변수-설정)
3. [모듈 별 기능 설명](#모듈-별-기능-설명)
   - [config.py (설정 모듈)](#configpy-설정-모듈)
   - [db_manager.py (데이터베이스 관리 모듈)](#db_managerpy-데이터베이스-관리-모듈)
   - [notion_manager.py (Notion API 관리 모듈)](#notion_managerpy-notion-api-관리-모듈)
   - [sync_manager.py (동기화 관리 모듈)](#sync_managerpy-동기화-관리-모듈)
   - [main.py (메인 실행 모듈)](#mainpy-메인-실행-모듈)
   - [run_sync.py (간편 실행 스크립트)](#run_syncpy-간편-실행-스크립트)
4. [일반적인 사용 시나리오](#일반적인-사용-시나리오)
   - [최초 설정 및 동기화](#최초-설정-및-동기화)
   - [정기적인 동기화 작업](#정기적인-동기화-작업)
   - [데이터 비교 및 확인](#데이터-비교-및-확인)
5. [문제 해결](#문제-해결)
   - [데이터베이스 연결 문제](#데이터베이스-연결-문제)
   - [Notion API 오류](#notion-api-오류)
   - [동기화 충돌 해결](#동기화-충돌-해결)
   - [일반적인 오류 메시지](#일반적인-오류-메시지)
6. [Notion 데이터베이스 설정 가이드](#notion-데이터베이스-설정-가이드)

## 프로젝트 개요

TTRSS-Notion 동기화 도구는 Tiny Tiny RSS(TTRSS) 데이터베이스의 항목을 Notion 데이터베이스와 동기화하기 위한 Python 애플리케이션입니다. 이 도구는 다음과 같은 주요 기능을 제공합니다:

- TTRSS 데이터베이스에서 새 항목 검색
- Notion 데이터베이스 항목 관리
- 중간 동기화 테이블을 통한 두 시스템 간 데이터 동기화
- 양방향 동기화 지원 (TTRSS → Notion, Notion → 동기화 테이블)

### 동기화 흐름도

```
+--------+       +------------+       +---------+
| TTRSS  | ----> | 동기화 테이블 | ----> | Notion |
+--------+       +------------+       +---------+
                      ^                    |
                      |                    |
                      +--------------------+
```

## 설치 및 설정

### 요구 사항

- Python 3.6 이상
- PostgreSQL 데이터베이스가 있는 TTRSS 인스턴스
- Notion 계정 및 API 키

### TTRSS Docker 설치

기존 TTRSS 설치가 없는 경우, Docker를 사용하여 쉽게 설정할 수 있습니다:

1. PostgreSQL 데이터베이스 컨테이너 실행:

```bash
docker run -d --name ttrss-db \
  -e POSTGRES_PASSWORD=handbook12 \
  -e POSTGRES_USER=ttrss \
  -e POSTGRES_DB=ttrss \
  -p 5432:5432 \
  postgres:13
```

2. TTRSS 애플리케이션 컨테이너 실행:

```bash
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

설치 후 브라우저에서 http://localhost:8080/ 에 접속하여 TTRSS에 로그인할 수 있습니다. (기본 로그인: admin/handbook12)

3. TTRSS 설정 및 피드 추가:
   - TTRSS에 로그인한 후 "Feed" 아이콘을 클릭하여 새 피드를 구독하세요.
   - 원하는 RSS 피드 URL을 추가하고 업데이트하세요.
   - 피드를 업데이트하여 항목을 가져오세요.

### 애플리케이션 설치

1. 필요한 패키지 설치:

```bash
pip install -r requirements.txt
```

또는 개별 패키지 설치:

```bash
pip install psycopg2-binary notion-client tqdm python-dotenv
```

### 환경 변수 설정

`.env` 파일을 프로젝트 루트 디렉토리에 생성하고 다음 정보를 입력합니다:

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

Docker로 TTRSS를 설정한 경우 다음과 같이 설정합니다:

```
# Database configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ttrss
DB_USER=ttrss
DB_PASSWORD=handbook12

# Notion configuration
NOTION_DATABASE_ID=your_notion_database_id
NOTION_API_KEY=your_notion_api_key
```

## 모듈 별 기능 설명

### config.py (설정 모듈)

설정 정보와 환경 변수를 관리하는 모듈입니다.

#### 주요 변수

- **DB_CONFIG**: 데이터베이스 연결 설정을 포함하는 딕셔너리
- **NOTION_DATABASE_ID**: Notion 데이터베이스 ID
- **NOTION_API_KEY**: Notion API 키
- **TTRSS_ENTRIES_TABLE**: TTRSS 항목 테이블 이름 (기본값: "ttrss_entries")
- **SYNC_TABLE**: 동기화 테이블 이름 (기본값: "ttrss_notion_sync")
- **logger**: 애플리케이션 전반에서 사용하는 로깅 객체

#### 사용 예시

```python
from config import DB_CONFIG, NOTION_DATABASE_ID, logger

# 로깅 사용
logger.info("정보 메시지")
logger.error("오류 메시지")

# 설정 값 접근
db_host = DB_CONFIG["host"]
```

### db_manager.py (데이터베이스 관리 모듈)

TTRSS 데이터베이스 연결 및 동기화 테이블 관리를 담당하는 모듈입니다.

#### DatabaseManager 클래스

이 클래스는 데이터베이스 연결과 조작을 담당합니다.

##### 초기화 및 연결 메서드

- **`__init__()`**: 데이터베이스 관리자 객체 초기화
  ```python
  db_manager = DatabaseManager()
  ```

- **`connect()`**: TTRSS 데이터베이스에 연결
  ```python
  conn = db_manager.connect()
  ```

- **`close()`**: 데이터베이스 연결 종료
  ```python
  db_manager.close()
  ```

##### 테이블 관리 메서드

- **`table_exists(table_name)`**: 지정된 테이블이 데이터베이스에 존재하는지 확인
  
  ```python
  exists = db_manager.table_exists("ttrss_notion_sync")
  if exists:
      print("테이블이 이미 존재합니다.")
  ```

- **`create_sync_table()`**: 동기화 테이블이 존재하지 않는 경우에만 생성
  
  ```python
  was_created = db_manager.create_sync_table()
  if was_created:
      print("동기화 테이블이 생성되었습니다.")
  else:
      print("동기화 테이블이 이미 존재합니다.")
  ```
  
  이 메서드는 테이블이 이미 존재하는 경우 그대로 유지하고, 존재하지 않는 경우에만 새롭게 생성합니다. 반환값은 테이블이 새로 생성되었는지 여부를 나타냅니다(True: 생성됨, False: 이미 존재하여 생성되지 않음). 테이블 스키마는 다음을 포함합니다:
  - id: 기본 키
  - ttrss_entry_id: TTRSS 항목 ID (외래 키)
  - notion_page_id: Notion 페이지 ID
  - title: 제목
  - content: 내용
  - link: 링크
  - published: 발행 시간
  - updated: 업데이트 시간
  - source: 소스 ('ttrss' 또는 'notion')
  - synced_to_notion: Notion 동기화 상태
  - last_sync: 마지막 동기화 시간

##### 데이터 조회 메서드

- **`get_ttrss_entries_schema()`**: TTRSS 항목 테이블의 스키마 조회
  
  ```python
  schema = db_manager.get_ttrss_entries_schema()
  print(f"컬럼: {schema}")
  ```

- **`get_ttrss_entries()`**: TTRSS 항목 테이블의 모든 항목 조회
  
  ```python
  entries = db_manager.get_ttrss_entries()
  for entry in entries[:5]:  # 처음 5개 항목 출력
      print(f"제목: {entry['title']}")
  ```

- **`get_sync_entries()`**: 동기화 테이블의 모든 항목 조회
  
  ```python
  sync_entries = db_manager.get_sync_entries()
  print(f"동기화 테이블 항목 수: {len(sync_entries)}")
  ```

##### 데이터 변경 메서드

- **`add_ttrss_entry_to_sync(entry)`**: TTRSS 항목을 동기화 테이블에 추가
  
  ```python
  entry = {
      'id': 123,
      'title': '제목',
      'content': '내용',
      'link': 'https://example.com',
      'date_entered': datetime.now(),
      'date_updated': datetime.now()
  }
  sync_id = db_manager.add_ttrss_entry_to_sync(entry)
  print(f"새 항목 ID: {sync_id}")
  ```

- **`add_notion_entry_to_sync(entry)`**: Notion 항목을 동기화 테이블에 추가
  
  ```python
  entry = {
      'notion_page_id': 'page_id',
      'title': '제목',
      'content': '내용',
      'link': 'https://example.com',
      'published': datetime.now(),
      'updated': datetime.now()
  }
  sync_id = db_manager.add_notion_entry_to_sync(entry)
  ```

- **`update_sync_status(sync_id, notion_page_id)`**: 동기화 항목의 Notion 동기화 상태 업데이트
  
  ```python
  db_manager.update_sync_status(sync_id, "notion_page_id_here")
  ```

- **`delete_sync_entry(sync_id)`**: 동기화 테이블에서 항목 삭제
  
  ```python
  db_manager.delete_sync_entry(123)
  ```

- **`get_ttrss_entries()`**: TTRSS 데이터베이스에서 항목 검색
  
  ```python
  ttrss_entries = db_manager.get_ttrss_entries()
  ```

- **`add_ttrss_entry_to_sync(entry)`**: TTRSS 항목을 동기화 테이블에 추가
  
  ```python
  db_manager.add_ttrss_entry_to_sync(entry)
  ```

- **`add_notion_entry_to_sync(entry)`**: Notion 항목을 동기화 테이블에 추가 (synced_to_notion=TRUE로 설정)
  
  ```python
  db_manager.add_notion_entry_to_sync(entry)
  ```

- **`find_matching_entries_by_title(title)`**: 제목이 일치하는 항목 검색
  
  ```python
  matches = db_manager.find_matching_entries_by_title("항목 제목")
  ```

- **`update_duplicate_entries_sync_status()`**: 제목이 일치하는 항목들의 동기화 상태 업데이트
  
  ```python
  db_manager.update_duplicate_entries_sync_status()
  ```

### notion_manager.py (Notion API 관리 모듈)

Notion API 연결 및 데이터베이스 항목 관리를 담당하는 모듈입니다.

#### NotionManager 클래스

이 클래스는 Notion API 호출과 데이터 처리를 담당합니다.

##### 초기화 메서드

- **`__init__()`**: Notion 관리자 객체 초기화
  
  ```python
  notion_manager = NotionManager()
  ```

##### Notion 데이터베이스 메서드

- **`get_database_pages()`**: Notion 데이터베이스의 모든 페이지 조회
  
  ```python
  pages = notion_manager.get_database_pages()
  for page in pages[:5]:  # 처음 5개 페이지 출력
      print(f"페이지 ID: {page['id']}, 제목: {page['properties']['Name']['title'][0]['text']['content']}")
  ```

- **`create_database_page(entry)`**: Notion 데이터베이스에 새 페이지 생성
  
  ```python
  entry = {
      'title': '제목',
      'content': '내용',
      'link': 'https://example.com',
      'published': datetime.now()
  }
  page_id = notion_manager.create_database_page(entry)
  print(f"생성된 페이지 ID: {page_id}")
  ```

### sync_manager.py (동기화 관리 모듈)

TTRSS와 Notion 간의 동기화 로직을 담당하는 모듈입니다.

#### SyncManager 클래스

이 클래스는 두 시스템 간의 데이터 동기화 프로세스를 관리합니다.

##### 초기화 메서드

- **`__init__()`**: 동기화 관리자 객체 초기화
  
  ```python
  sync_manager = SyncManager()
  ```

##### 동기화 메서드

- **`sync_notion_to_db()`**: Notion 데이터베이스의 항목을 동기화 테이블에 동기화
  
  ```python
  sync_manager.sync_notion_to_db()
  ```

- **`sync_ttrss_to_db()`**: TTRSS 항목을 동기화 테이블에 동기화
  
  ```python
  sync_manager.sync_ttrss_to_db()
  ```

- **`sync_to_notion()`**: 동기화 테이블의 항목을 Notion 데이터베이스에 동기화
  
  ```python
  sync_manager.sync_to_notion()
  ```

- **`full_sync()`**: 전체 동기화 프로세스 실행
  
  ```python
  sync_manager.full_sync()
  ```

- **`perform_full_sync()`**: 전체 동기화 수행 (4단계 과정)
  
  ```python
  summary = sync_manager.perform_full_sync()
  print(f"Added from Notion: {summary['added_notion']}")
  print(f"Added from TTRSS: {summary['added_ttrss']}")
  print(f"Updated matches by title: {summary['updated_matches']}")
  print(f"Synced to Notion: {summary['synced_notion']}")
  ```
  
  이 메서드는 다음 4단계로 진행됩니다:
  1. Notion 데이터베이스와 동기화 테이블 동기화 (Notion을 기준으로)
  2. TTRSS 항목과 동기화 테이블 동기화 (새 항목만 추가)
  3. 제목이 일치하는 항목들의 동기화 상태 업데이트
  4. 동기화 테이블의 새 항목을 Notion에 동기화

### main.py (메인 실행 모듈)

명령줄 인터페이스를 제공하여 다양한 동기화 작업을 실행할 수 있게 하는 모듈입니다.

#### 사용 방법

```bash
python -m ttrss_notion_sync_app.main [command] [options]
```

#### 지원하는 명령

- **`full-sync`**: 전체 동기화 프로세스 실행
  
  ```bash
  python -m ttrss_notion_sync_app.main full-sync
  ```

- **`check-notion`**: Notion 데이터베이스 항목 확인
  
  ```bash
  python -m ttrss_notion_sync_app.main check-notion
  ```

- **`check-ttrss`**: TTRSS 항목 확인
  
  ```bash
  python -m ttrss_notion_sync_app.main check-ttrss
  ```

- **`compare`**: 소스와 동기화 테이블 간 항목 비교
  
  ```bash
  python -m ttrss_notion_sync_app.main compare --source notion
  python -m ttrss_notion_sync_app.main compare --source ttrss
  ```

- **`sync-notion`**: Notion 데이터베이스를 동기화 테이블에 동기화
  
  ```bash
  python -m ttrss_notion_sync_app.main sync-notion
  ```

- **`sync-ttrss`**: TTRSS 항목을 동기화 테이블에 동기화
  
  ```bash
  python -m ttrss_notion_sync_app.main sync-ttrss
  ```

- **`sync-to-notion`**: 동기화 테이블의 항목을 Notion에 동기화
  
  ```bash
  python -m ttrss_notion_sync_app.main sync-to-notion
  ```

### run_sync.py (간편 실행 스크립트)

복잡한 명령줄 옵션 없이 전체 동기화 프로세스를 간단히 실행할 수 있는 스크립트입니다.

#### 사용 방법

```bash
python run_sync.py
```

이 스크립트는 SyncManager의 full_sync() 메서드를 호출하여 전체 동기화 프로세스를 실행합니다.

## 일반적인 사용 시나리오

### 최초 설정 및 동기화

초기 설정 후 첫 번째 동기화를 수행하는 방법:

1. TTRSS 설치 및 피드 구독 확인
2. Notion 데이터베이스 생성 및 API 키 획득
3. `.env` 파일 설정
4. 전체 동기화 실행:

```bash
python main.py full-sync
```

이 명령은 다음 단계를 수행합니다:
- Notion 데이터베이스의 모든 항목을 동기화 테이블에 추가 (synced_to_notion=TRUE로 설정)
- TTRSS의 새 항목을 동기화 테이블에 추가
- 제목이 일치하는 항목들의 동기화 상태를 업데이트 (TTRSS 항목 중 Notion에 이미 있는 항목의 synced_to_notion을 TRUE로 설정)
- 아직 동기화되지 않은 항목을 Notion에 추가

### 정기적인 동기화 작업

주기적으로 새 항목을 동기화하려면 다음 명령을 실행합니다:

```bash
python run_sync.py
```

또는 cron 작업으로 설정하여 자동화할 수 있습니다:

```bash
# 매시간 동기화 실행
0 * * * * cd /path/to/your/app && python run_sync.py >> /path/to/logfile.log 2>&1
```

### 데이터 비교 및 확인

동기화 상태를 확인하려면 다음 명령을 사용합니다:

```bash
# Notion 데이터베이스와 동기화 테이블 비교
python -m ttrss_notion_sync_app.main compare --source notion

# TTRSS 항목과 동기화 테이블 비교
python -m ttrss_notion_sync_app.main compare --source ttrss
```

## 문제 해결

### 데이터베이스 연결 문제

**문제**: 데이터베이스 연결 오류

**해결 방법**:
1. DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD 환경 변수가 올바르게 설정되었는지 확인
2. PostgreSQL 서버가 실행 중인지 확인
3. Docker 컨테이너를 사용하는 경우, 컨테이너가 실행 중인지 확인:
   ```bash
   docker ps | grep ttrss-db
   ```
4. 방화벽 설정이 데이터베이스 포트 연결을 허용하는지 확인

### Notion API 오류

**문제**: Notion API 호출 실패

**해결 방법**:
1. NOTION_API_KEY가 올바르게 설정되었는지 확인
2. NOTION_DATABASE_ID가 올바른지 확인
3. API 키가 해당 데이터베이스에 대한 권한을 가지고 있는지 확인
4. Notion API 서비스 상태 확인: https://status.notion.so/

### 동기화 충돌 해결

**문제**: 동기화 과정에서 중복 항목 발생

**해결 방법**:
1. 동기화 테이블 초기화:
   ```bash
   python reset_sync_table.py
   ```
2. 전체 동기화 다시 실행:
   ```bash
   python run_sync.py
   ```

### 일반적인 오류 메시지

- **"Unable to connect to database"**: 데이터베이스 연결 설정 확인
- **"Notion API Error: 401 Unauthorized"**: API 키 확인
- **"Notion API Error: 404 Not Found"**: 데이터베이스 ID 확인
- **"Sync conflict detected"**: 동기화 충돌 해결 방법 참조

## Notion 데이터베이스 설정 가이드

### 필수 속성

Notion 데이터베이스에는 다음과 같은 속성이 필요합니다:

1. **Name** (제목): 제목 유형 (title)
2. **Link** (링크): URL 유형 (url)
3. **Published** (발행일): 날짜 유형 (date)
4. **Source** (소스): 선택 유형 (select)

### 데이터베이스 설정 단계

1. Notion에서 새 데이터베이스 생성
2. 필요한 속성 추가
3. Notion 통합 설정:
   - https://www.notion.so/my-integrations 에서 새 통합 생성
   - 생성된 통합에서 API 키 복사
   - 데이터베이스 페이지에서 '...' 메뉴 클릭 > '연결' > 생성한 통합 선택
4. 데이터베이스 ID 복사:
   - 데이터베이스 URL에서 ID 부분 복사 (https://www.notion.so/{workspace_name}/{DATABASE_ID}?...)
   - 또는 브라우저에서 'Share' 버튼을 클릭하고 '복사' 버튼을 눌러 URL을 복사한 후 ID 부분 추출
