# cumulus.team (GitHub Pages)

Team Cumulus 공식 사이트. 팀 project_id: SITE.

## 배포
- main에 push하면 GitHub Pages가 바로 빌드·배포한다. push = 운영 반영이다.
- App Store의 지원 URL·개인정보 URL이 이 사이트를 가리킨다. 기존 경로(/<app>/, /<app>/support/, /<app>/privacy/, /sandtime/ 리다이렉트)를 지우거나 옮기지 않는다.

## 구조
- 앱 폴더: redday, weatherfit, lifory, onlumi, pixder. 한국어가 기본이고 en/ 하위에 영어판이 있다. sandtime은 lifory로 넘기는 리다이렉트.
- weatherfit/index.html은 weatherfit/build_landing.py로 생성한다. 직접 고치지 말고 스크립트를 고친 뒤 `python3 weatherfit/build_landing.py`를 저장소 루트에서 실행한다.
- 지우지 않는 파일: CNAME, BingSiteAuth.xml, naver*.html, 67671e*.txt(검색엔진 소유 확인용).

## 변경 시 같이 고칠 것
- 페이지를 추가·변경하면 sitemap.xml lastmod, llms.txt의 해당 앱 항목, 페이지 JSON-LD를 함께 맞춘다.
- 사이트에 나가지 않아야 할 파일(스크립트, 템플릿, 문서)은 _config.yml의 exclude에 추가한다.

## Git
- 커밋 메시지는 `<app>: 변경 내용` 형식(예: `weatherfit: App Store 출시 반영`). 공통 변경은 `site:`.
- 개인정보 처리방침·결제 관련 문구의 의미가 바뀌면 push 전에 사용자에게 확인한다.
