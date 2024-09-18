
# Contribution Guide


이 페이지는 llm_handbook 오픈소스 프로젝트에 기여하는 방법을 알려드리기 위한 가이드 문서입니다.

이 문서를 참고하여 llm_handbook 프로젝트에 기여하는 방법과 유의사항을 알아봅시다.

  
## How to contribute

이 챕터는 문서를 기여하는 방안에 대한 것입니다.
  

1. 먼저 llm_handbook 레포를 본인의 깃허브로 포크합니다. [https://github.com/springcoolers/llm-handbook](https://github.com/springcoolers/llm-handbook)

2. 자신의 로컬 디렉토리에 해당 리포를 `git clone` 합니다.

3. 포크해온 리포에 branch를 하나 만듭니다.
   - 브랜치의 이름은 기여하고자 하는 문서의 이름 `llm_handbook : {chatper-name}_{page-name}` 으로 작성해주시기 바랍니다.

4. 해당 branch에서 문서를 작성한 후에 commit을 진행합니다. commit 메세지는 아래의 규칙을 따라야합니다.

    - 문서를 새로 작성한 경우 : `create : {chapter-name}_{page-name}`
    - 문서를 수정한 경우 : `modify : {chater-name}_{page-name}`
    - 문서를 삭제한 경우 : `delete : {chapter-name}_{page-name}`
    - 문서를 이동한 경우 : `migrate : {origin_src} to {chapter-name}_{page_name}`

5. 커밋을 완료하였다면 이제 자신의 브랜치를 push하면 됩니다.

6. 이제 자신의 깃허브 repo에서 `Before Pull Request` 사항을 확인한 후에 PR을 요청해주시면 됩니다.

## Before Pull Request

이 챕터는 pull request를 날리기 전에 기여자분들이 수행 해야할 작업입니다.

1. Check list

    - 본인이 PR을 날리기 아래의 checklist를 확인하셨다면 체크하여 주시면 됩니다.
    - 아래의 체크리스트는 나중에 PR Description 템플릿에 적용될 사항입니다.


- [ ] 본인의 로컬에서 정상적으로 빌드가 되는지 확인하였습니까?
- [ ] TOC에 문서 작성 사항을 업데이트하였습니까?
- [ ] 문서를 작성하기 전에 Contribution 가이드를 확인하셨습니까?

2. Review

    - 체크리스트의 모든 사항을 확인하였다면, 이제 이 리포의 관리자한테 리뷰를 요청하는 스텝입니다. 리포의 관리자한테 리뷰를 요청하면, 요청받은 관리자가 문서 리뷰 후에 PR을 승인할 것입니다. 리뷰 방안은 다음과 같습니다.
    - 리뷰 방안 : `@관리자이름` 으로 태그를 건 후에 리뷰를 요청하면 됩니다.

## Tutorial  

이제 실제로 위의 프로젝트에 기여를 해보기 전에 간단한 실습을 해볼겁니다. 기여자의 자기소개 페이지에 간단한 자기소개를 작성한 후에, 위의 과정에 따라 PR을 날려보면 됩니다.

  
1. 깃헙 레포를 포크합니다.
    -  이 페이지를 포크 해오세요 [`https://github.com/springcoolers/llm-handbook](https://github.com/springcoolers/llm-handbook)`  

2. 포크 해온 repo에 새 브랜치 `contribution_practice : self-introduction_{your_name}`
를 만듭니다.

3. 다음의 경로의 마크다운 파일을 작성합니다. md 파일 내용에는 자기소개를 쓰면됩니다.
   `_contents/contricution_intro/contributor_introduction/sections/{자기 이름}.md`

>**파일의 첫번째 h1을 제대로 작성했는지 확인해주세요!!!!!!** 쥬피터 북은 여러분이 작성하신 ‘파일 이름’을 읽어오지 않습니다. 여러분이 작성한 md / ipynb 파일의 ‘첫 번째 헤딩1’을 제목으로 읽어옵니다.


4. 테스트 확인: 자기가 한게 제대로 들어갔는지 열어봅니다.

    1. 여러분의 repo에 push합시다.

    2. [계정이름.github.io/tutorial-book](http://계정이름.github.io/tutorial-book) 에 들어가면 됩니다

    3. [`https://github.com/springcoolers/llm-handbook`](https://github.com/springcoolers/llm-handbook) 의 액션 탭을 보면, 빌드 중인지를 알 수 있습니다.

5. 테스트가 끝났으면, 이제 본 repo인 [`https://github.com/springcoolers/llm-handbook](https://github.com/springcoolers/llm-handbook)`  에다가 본인이 만든 pr을 날려주세요.

## Issue

만약 현재의 TOC나 목차 이외에 본인이 기여하고자 하는 문서를 새롭게 작성하시고자 한다면, 이슈란에 남겨주시기 바랍니다. 더불어