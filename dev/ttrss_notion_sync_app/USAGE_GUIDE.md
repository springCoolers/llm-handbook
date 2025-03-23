# TTRSS-Notion 동기화 도구 사용 가이드

이 문서는 TTRSS-Notion 동기화 도구의 각 모듈과 메서드의 상세 사용법을 제공합니다.

## 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [설치 및 설정](#설치-및-설정)
3. [모듈 별 기능 설명](#모듈-별-기능-설명)
   - [config.py (설정 모듈)](#configpy-설정-모듈)
   - [db_manager.py (데이터베이스 관리 모듈)](#db_managerpy-데이터베이스-관리-모듈)
   - [notion_manager.py (Notion API 관리 모듈)](#notion_managerpy-notion-api-관리-모듈)
   - [sync_manager.py (동기화 관리 모듈)](#sync_managerpy-동기화-관리-모듈)
   - [main.py (메인 실행 모듈)](#mainpy-메인-실행-모듈)
4. [일반적인 사용 시나리오](#일반적인-사용-시나리오)
5. [문제 해결](#문제-해결)

## 프로젝트 개요

TTRSS-Notion 동기화 도구는 Tiny Tiny RSS(TTRSS) 데이터베이스의 항목을 Notion 데이터베이스와 동기화하기 위한 Python 애플리케이션입니다. 이 도구는 다음과 같은 주요 기능을 제공합니다:

- TTRSS 데이터베이스에서 새 항목 검색
- Notion 데이터베이스 항목 관리
- 중간 동기화 테이블을 통한 두 시스템 간 데이터 동기화
- 양방향 동기화 지원 (TTRSS → Notion, Notion → 동기화 테이블)

## 설치 및 설정

### 요구 사항

- Python 3.6 이상
- PostgreSQL 데이터베이스가 있는 TTRSS 인스턴스
- Notion 계정 및 API 키

### 설치 단계

1. 필요한 패키지 설치:

```bash
pip install -r requirements.txt
```

2. 환경 변수 설정:

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
  db_manager.update_sync_status(sync_id, 'notion_page_id')
  ```

- **`delete_sync_entry(sync_id)`**: 동기화 테이블에서 항목 삭제
  
  ```python
  db_manager.delete_sync_entry(sync_id)
  ```

##### 비교 및 조회 메서드

- **`compare_ttrss_with_sync()`**: TTRSS 항목과 동기화 테이블 비교
  
  ```python
  new_entries = db_manager.compare_ttrss_with_sync()
  print(f"동기화되지 않은 TTRSS 항목 수: {len(new_entries)}")
  ```

- **`find_entries_to_sync_to_notion()`**: Notion에 동기화할 항목 찾기
  
  ```python
  entries_to_sync = db_manager.find_entries_to_sync_to_notion()
  print(f"Notion에 동기화할 항목 수: {len(entries_to_sync)}")
  ```

- **`get_sync_entries_by_notion_ids(notion_ids)`**: Notion ID로 동기화 항목 조회
  
  ```python
  notion_ids = ['page_id1', 'page_id2']
  entries = db_manager.get_sync_entries_by_notion_ids(notion_ids)
  ```

### notion_manager.py (Notion API 관리 모듈)

Notion API 연결 및 데이터베이스 조작을 담당하는 모듈입니다.

#### NotionManager 클래스

이 클래스는 Notion API 연결과 조작을 담당합니다.

##### 초기화 및 연결 메서드

- **`__init__(api_key=None)`**: Notion 관리자 객체 초기화
  
  ```python
  notion_manager = NotionManager()  # 기본 API 키 사용
  notion_manager = NotionManager(api_key="your_api_key")  # 직접 API 키 지정
  ```

- **`connect()`**: Notion API에 연결
  
  ```python
  notion_client = notion_manager.connect()
  ```

##### 데이터베이스 조작 메서드

- **`get_database_structure()`**: Notion 데이터베이스 구조 조회
  
  ```python
  properties = notion_manager.get_database_structure()
  print(f"데이터베이스 속성: {properties.keys()}")
  ```

- **`get_database_pages()`**: Notion 데이터베이스의 모든 페이지 조회
  
  ```python
  pages = notion_manager.get_database_pages()
  print(f"데이터베이스 페이지 수: {len(pages)}")
  ```

- **`extract_page_data(page)`**: Notion 페이지에서 관련 데이터 추출
  
  ```python
  page = notion_manager.get_database_pages()[0]  # 첫 번째 페이지
  page_data = notion_manager.extract_page_data(page)
  print(f"페이지 제목: {page_data['title']}")
  ```

- **`create_page(entry)`**: Notion 데이터베이스에 새 페이지 생성
  
  ```python
  entry = {
      'title': '제목',
      'content': '내용',
      'link': 'https://example.com'
  }
  page_id = notion_manager.create_page(entry)
  print(f"생성된 페이지 ID: {page_id}")
  ```

- **`delete_page(page_id)`**: Notion 페이지 보관 처리 (삭제)
  
  ```python
  success = notion_manager.delete_page('page_id')
  ```

### sync_manager.py (동기화 관리 모듈)

TTRSS와 Notion 간의 동기화 로직을 담당하는 모듈입니다.

#### SyncManager 클래스

이 클래스는 TTRSS와 Notion 간의 동기화를 담당합니다.

##### 초기화 및 연결 메서드

- **`__init__()`**: 동기화 관리자 객체 초기화
  
  ```python
  sync_manager = SyncManager()
  ```

- **`initialize()`**: 데이터베이스 및 Notion 연결 초기화
  
  ```python
  sync_manager.initialize()
  ```

- **`close()`**: 연결 종료
  
  ```python
  sync_manager.close()
  ```

##### Notion 관련 메서드

- **`check_notion_database()`**: Notion 데이터베이스 내용 확인
  
  ```python
  notion_pages = sync_manager.check_notion_database()
  print(f"Notion 페이지 수: {len(notion_pages)}")
  ```

- **`compare_notion_with_sync(notion_pages=None)`**: Notion 데이터베이스와 동기화 테이블 비교
  
  ```python
  new_in_notion, missing_from_notion = sync_manager.compare_notion_with_sync()
  print(f"Notion에 새로 추가된 항목: {len(new_in_notion)}")
  print(f"Notion에서 삭제된 항목: {len(missing_from_notion)}")
  ```

- **`sync_notion_to_sync_table(notion_pages=None)`**: Notion 데이터베이스에서 동기화 테이블로 동기화
  
  ```python
  added, removed = sync_manager.sync_notion_to_sync_table()
  print(f"추가된 항목: {added}, 제거된 항목: {removed}")
  ```

##### TTRSS 관련 메서드

- **`check_ttrss_entries()`**: TTRSS 항목 확인
  
  ```python
  ttrss_entries = sync_manager.check_ttrss_entries()
  print(f"TTRSS 항목 수: {len(ttrss_entries)}")
  ```

- **`compare_ttrss_with_sync(ttrss_entries=None)`**: TTRSS 항목과 동기화 테이블 비교
  
  ```python
  new_entries = sync_manager.compare_ttrss_with_sync()
  print(f"TTRSS에 새로 추가된 항목: {len(new_entries)}")
  ```

- **`sync_ttrss_to_sync_table(ttrss_entries=None)`**: TTRSS 항목을 동기화 테이블로 동기화
  
  ```python
  added = sync_manager.sync_ttrss_to_sync_table()
  print(f"동기화 테이블에 추가된 TTRSS 항목: {added}")
  ```

##### 동기화 관련 메서드

- **`sync_to_notion()`**: 동기화 테이블의 항목을 Notion으로 동기화
  
  ```python
  synced_count = sync_manager.sync_to_notion()
  print(f"Notion에 동기화된 항목 수: {synced_count}")
  ```

- **`perform_full_sync()`**: 전체 동기화 수행
  
  ```python
  results = sync_manager.perform_full_sync()
  print(f"동기화 결과: {results}")
  ```
  
  이 메서드는 다음 단계를 수행합니다:
  1. Notion 데이터베이스를 동기화 테이블과 동기화 (Notion이 소스)
  2. TTRSS 항목을 동기화 테이블과 동기화 (추가만 수행)
  3. 동기화 테이블의 새 항목을 Notion에 동기화

### main.py (메인 실행 모듈)

명령줄 인터페이스를 제공하는 메인 모듈입니다.

#### 명령줄 인터페이스

다음 명령어를 사용하여 다양한 기능을 실행할 수 있습니다:

1. **전체 동기화 수행**: 모든 동기화 단계를 순차적으로 실행
   ```bash
   python -m ttrss_notion_sync_app.main full-sync
   ```

2. **Notion 데이터베이스 확인**: Notion 데이터베이스의 내용을 확인
   ```bash
   python -m ttrss_notion_sync_app.main check-notion
   ```

3. **TTRSS 항목 확인**: TTRSS 데이터베이스의 항목을 확인
   ```bash
   python -m ttrss_notion_sync_app.main check-ttrss
   ```

4. **비교 작업 수행**: 소스(notion 또는 ttrss)와 동기화 테이블 비교
   ```bash
   python -m ttrss_notion_sync_app.main compare --source notion
   python -m ttrss_notion_sync_app.main compare --source ttrss
   ```

5. **Notion 동기화**: Notion 데이터베이스를 동기화 테이블과 동기화
   ```bash
   python -m ttrss_notion_sync_app.main sync-notion
   ```

6. **TTRSS 동기화**: TTRSS 항목을 동기화 테이블과 동기화
   ```bash
   python -m ttrss_notion_sync_app.main sync-ttrss
   ```

7. **Notion으로 동기화**: 동기화 테이블의 항목을 Notion으로 동기화
   ```bash
   python -m ttrss_notion_sync_app.main sync-to-notion
   ```

## 일반적인 사용 시나리오

### 1. 처음 설정하기

처음 실행할 때는 다음과 같은 단계를 따릅니다:

1. 환경 변수를 설정합니다 (`.env` 파일).
2. 패키지를 설치합니다 (`pip install -r requirements.txt`).
3. 전체 동기화를 실행합니다:
   ```bash
   python -m ttrss_notion_sync_app.main full-sync
   ```

### 2. 정기적인 동기화 수행

정기적으로 동기화할 때는 다음과 같이 실행합니다:

```bash
python -m ttrss_notion_sync_app.main full-sync
```

### 3. 특정 부분만 동기화하기

특정 시스템만 동기화할 때는 다음과 같이 실행합니다:

- TTRSS에서 새 항목을 가져와 동기화 테이블에 추가:
  ```bash
  python -m ttrss_notion_sync_app.main sync-ttrss
  ```

- 동기화 테이블의 항목을 Notion에 추가:
  ```bash
  python -m ttrss_notion_sync_app.main sync-to-notion
  ```

### 4. 상태 확인하기

현재 상태를 확인할 때는 다음과 같이 실행합니다:

- Notion 데이터베이스 확인:
  ```bash
  python -m ttrss_notion_sync_app.main check-notion
  ```

- TTRSS 항목 확인:
  ```bash
  python -m ttrss_notion_sync_app.main check-ttrss
  ```

- 동기화 상태 비교:
  ```bash
  python -m ttrss_notion_sync_app.main compare --source notion
  python -m ttrss_notion_sync_app.main compare --source ttrss
  ```

## 문제 해결

### 데이터베이스 연결 오류

- `.env` 파일의 데이터베이스 연결 정보가 올바른지 확인합니다.
- TTRSS 데이터베이스에 원격으로 접속할 수 있는지 확인합니다.
- 방화벽 설정을 확인합니다.

### Notion API 오류

- Notion API 키가 올바른지 확인합니다.
- Notion 통합이 해당 데이터베이스에 접근 권한이 있는지 확인합니다.
- Notion 데이터베이스 ID가 올바른지 확인합니다.

### 동기화 문제

- 동기화 테이블이 올바르게 생성되었는지 확인합니다.
- 로그를 검토하여 오류가 있는지 확인합니다.
- `--source notion` 또는 `--source ttrss`로 비교 작업을 수행하여 차이점을 확인합니다.

### 실행 권한 문제

- Python 스크립트에 실행 권한이 있는지 확인합니다.
- Python 경로가 올바르게 설정되어 있는지 확인합니다.

---

이 문서는 TTRSS-Notion 동기화 도구의 각 모듈과 메서드에 대한 사용법을 제공합니다. 추가 질문이 있으면 README.md 파일을 참조하거나 개발자에게 문의하세요.
