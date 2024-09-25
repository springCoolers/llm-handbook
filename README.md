# LLM-Engineering Handbook 

여기로 접속하시면 핸드북의 랜딩 페이지가 나옵니다! 거기서 Readme를 확인해 주세요  
https://springcoolers.github.io/llm-handbook/_contents/intro.html 


## Local에서 빌드해보기
* 이 내용은 운영진을 위한 안내 내용으로, 일반 유저들은 실행해보실 필요가 없습니다 

로컬 환경에서 Jupyter Book을 테스트 하고 싶다면, 먼저 독립된 환경을 구축하는 것을 권장합니다. 
[이를 위한 도커 이미지](./docker/Dockerfile)를 제공하고 있습니다. 다음과 같이 먼저 해당 도커 이미지를 빌드해주세요.

```bash
docker build --tag jb ./docker
```

도커 이미지가 빌드되었다면, 다음 명령어를 통해 빌드를 시작할 수 있습니다.

```bash
docker run --rm -ti \
    -v ./:/workspace \
    -w /workspace \
     jb jb build ./
```

빌드된 HTML 페이지는 [`./_build/html/index.html`](./_build/html/index.html)을 통해 확인할 수 있습니다. 

> [!NOTE] 
> 로컬에서 빌드된 페이지에서는 댓글을 확인할 수 없습니다.


## jupyber-book build . 사용하기

1. 라이브러리 설치
```
pip install -r requirements.txt
```

2. 빌드
```
jupyber-book build .
```
