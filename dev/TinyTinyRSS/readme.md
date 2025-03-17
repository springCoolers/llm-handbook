# **Tiny Tiny RSS (TTRSS) Docker 설치 및 설정 가이드**

아래는 완전히 새로운 환경에서 Tiny Tiny RSS를 Docker를 사용하여 설치하고 설정하는 전체 과정입니다.

## **1. 필요한 Docker 이미지**

TTRSS 설치를 위해 두 개의 Docker 컨테이너가 필요합니다:

1. PostgreSQL 데이터베이스 컨테이너
2. TTRSS 애플리케이션 컨테이너
3. 1. PostgreSQL 데이터베이스 컨테이너
4. 2. TTRSS 애플리케이션 컨테이너

## **2. PostgreSQL 데이터베이스 컨테이너 설치**

먼저 PostgreSQL 데이터베이스 컨테이너를 생성합니다:

```bash
docker run -d --name ttrss-db \\
-v ttrss-db-data:/var/lib/postgresql/data \\
-e POSTGRES_PASSWORD=handbook12 \\
-p 5432:5432 \\
postgres:15-alpine
```

이 명령어는:

* **`ttrss-db`**라는 이름의 컨테이너를 생성합니다
* 데이터를 영구적으로 저장하기 위한 볼륨을 생성합니다
* PostgreSQL 관리자 비밀번호를 **`handbook12`**로 설정합니다
* PostgreSQL 기본 포트인 5432를 호스트 시스템에 노출시킵니다 (외부 접속용)
* PostgreSQL 15 Alpine 버전 이미지를 사용합니다

## **3. TTRSS 사용자 및 데이터베이스 생성**

TTRSS가 사용할 데이터베이스와 사용자를 생성합니다:

```bash
docker exec -it ttrss-db bash -c "psql -U postgres -c \\"CREATE USER ttrss WITH PASSWORD 'handbook12';\\" && psql -U postgres -c \\"CREATE DATABASE ttrss OWNER ttrss;\\""
```

이 명령어는:

* **`ttrss`** 사용자를 생성하고 비밀번호를 **`handbook12`**로 설정합니다
* **`ttrss`** 데이터베이스를 생성하고 소유자를 **`ttrss`** 사용자로 지정합니다

## **4. TTRSS 애플리케이션 컨테이너 설치**

이제 TTRSS 애플리케이션 컨테이너를 생성합니다:

```bash
docker run -d --name ttrss \\
  -p 8080:80 \\
  --link ttrss-db:db \\
  -e SELF_URL_PATH=http://localhost:8080/ \\
  -e DB_HOST=db \\
  -e DB_TYPE=pgsql \\
  -e DB_PORT=5432 \\
  -e DB_NAME=ttrss \\
  -e DB_USER=ttrss \\
  -e DB_PASS=handbook12 \\
  -e ADMIN_USER=admin \\
  -e ADMIN_PASS=handbook12 \\
  wangqiru/ttrss:latest
```

이 명령어는:

* **`ttrss`**라는 이름의 컨테이너를 생성합니다
* 웹 인터페이스를 위해 컨테이너의 80 포트를 호스트의 8080 포트에 매핑합니다
* 데이터베이스 컨테이너( **`ttrss-db`** )와 연결합니다
* 다양한 환경 변수를 설정합니다:
  * **`SELF_URL_PATH`** : TTRSS가 자신의 URL을 인식하는 데 사용하는 경로
  * 데이터베이스 연결 정보 (호스트, 타입, 포트, 이름, 사용자, 비밀번호)
  * 관리자 계정 정보 (사용자 이름, 비밀번호)
* **`wangqiru/ttrss`** 이미지의 최신 버전을 사용합니다

## **5. TTRSS 웹 인터페이스 접속**

설치가 완료되면 웹 브라우저에서 다음 URL로 접속할 수 있습니다:

* [http://localhost:8080](http://localhost:8080)

로그인 정보:

* 사용자 이름: **`admin`**
* 비밀번호: **`handbook12`**

## **6. 외부 접속 설정**

다른 기기에서 TTRSS에 접속하려면 호스트 컴퓨터의 IP 주소를 사용합니다:

* http://[호스트IP]:8080

데이터베이스에 외부에서 접속하려면:

* 호스트: [호스트IP]
* 포트: 5432
* 데이터베이스: ttrss
* 사용자: ttrss
* 비밀번호: handbook12

## **7. 컨테이너 관리**

컨테이너를 중지하려면:

```bash
docker stop ttrss ttrss-db
```

컨테이너를 다시 시작하려면:

```bash
docker start ttrss-db
docker start ttrss
```

컨테이너를 삭제하려면 (데이터는 볼륨에 유지됨):

```bash
docker rm ttrss ttrss-db
```

## **8. 문제 해결**

**데이터베이스 연결 문제**

데이터베이스 연결 문제가 발생하면 다음을 확인하세요:

```bash
docker logs ttrss
```

**로그인 문제**

로그인에 문제가 있으면 관리자 비밀번호를 재설정할 수 있습니다:

```bash
docker exec -it ttrss-db psql -U ttrss -d ttrss -c "UPDATE ttrss_users SET pwd_hash = 'SHA1:5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8' WHERE login = 'admin';"
```

이 명령어는 관리자 비밀번호를 **`password`**로 재설정합니다.

## **9. 데이터 백업**

PostgreSQL 데이터베이스를 백업하려면:

```bash
docker exec -it ttrss-db pg_dump -U ttrss ttrss > ttrss_backup.sql
```

## **10. 주의사항**

* ARM64 아키텍처(예: M1/M2 Mac)에서는 일부 이미지가 호환성 경고를 표시할 수 있지만 대부분 정상적으로 작동합니다.
* 컨테이너를 재생성할 때 데이터베이스 볼륨을 유지하면 데이터가 보존됩니다.
* 보안을 위해 초기 설정 후 관리자 비밀번호를 변경하는 것이 좋습니다.

이 가이드를 따라 설치하면 Tiny Tiny RSS가 정상적으로 작동하며, RSS 피드를 구독하고 관리할 수 있는 환경이 준비됩니다.
