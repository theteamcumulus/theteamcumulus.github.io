# App Store 캠페인 링크 (App Analytics)

사이트의 App Store 링크에는 App Analytics 캠페인 파라미터를 붙여, 앱 분석(획득 › 캠페인)에서 어느 페이지·위치에서 받았는지 본다. 시작 2026-10-13.

형식: `<App Store 주소>?pt=129567498&ct=<캠페인>&mt=8` (HTML 속성 안에서는 `&amp;`)

- `pt=129567498`: Team Cumulus provider token. 모든 앱 공통.
- 주소는 앱 판매 국가에 맞춘다. 한국 전용 앱은 반드시 `/kr/app/id…` (국가 없는 주소는 웹에서 미국 스토어로 열려 404). 여러 나라에 파는 앱(Lifestamp)의 영어 페이지는 `/app/id…`.
- JSON-LD(`sameAs`·`installUrl`·`downloadUrl`)에는 캠페인 없는 정식 주소를 쓴다.
- 캠페인 데이터는 앱별로 나뉘므로 ct에 앱 이름을 넣지 않는다.
- 캠페인 귀속은 링크를 누르고 24시간 안의 다운로드, 기기 분석 공유에 동의한 사용자만.

## 캠페인 토큰 (ct)

| ct | 위치 | 적용 페이지 |
|---|---|---|
| `web-landing-hero` | 랜딩 상단 버튼 | weatherfit, redday, onlumi, lifory |
| `web-landing-howto` | 랜딩 "설치/사용 방법"의 앱 이름 링크 | weatherfit, redday, lifory |
| `web-landing-bottom` | 랜딩 하단 버튼 | weatherfit, redday, onlumi, lifory |
| `web-landing-en-hero` / `-howto` / `-bottom` | 영어 랜딩(`/<app>/en/`) 같은 위치 | onlumi(hero·bottom), lifory |
| `web-support` / `web-support-en` | 지원 페이지 상단 App Store 링크 | weatherfit, redday, onlumi(+en) |
| `web-llms` | /llms.txt 앱 항목 (AI 검색·에이전트 경유) | 전 앱 |
| `web-hub` | 허브(/) 앱 카드의 "App Store에서 보기" | 출시된 앱 |

예약(사이트 밖에서 쓸 때): `sns-instagram`, `sns-threads`, `sns-x`, `community-<이름>`, `qr-offline`.

## 고칠 때

- weatherfit 랜딩은 `weatherfit/build_landing.py`의 `PT`·`app_link(ct)`로 만든다(index.html 직접 수정 금지).
- 랜딩 상단 배지(hero)·하단 버튼(bottom)·허브·llms.txt 링크는 `tools/appstore/appstore_lib.py`·`render.py`가 만든다(`store_link`, apps.json의 pages[].storeUrl·ct). 본문 안 링크(howto)는 HTML의 `href`를 직접 고친다. 새 버튼을 추가하면 위 표에 ct를 먼저 적는다.
- 링크를 바꾸면 `curl -s -o /dev/null -w "%{http_code}" -L "<주소>"`로 200인지 확인한다(출시 전 앱은 404).
- 분석: 출퇴근날씨는 weather-fit 저장소 `scripts/app-analytics.mjs`(Analytics Reports API). 다른 앱은 App Store Connect 앱 분석 콘솔, 또는 같은 스크립트를 앱 ID·리포트 요청 ID만 바꿔 쓴다.

## Google Play (Android)

형식: `https://play.google.com/store/apps/details?id=<패키지>&referrer=<URL 인코딩한 UTM>`
예: `…?id=com.cumulus.weatherfit&referrer=utm_source%3Dcumulus.team%26utm_medium%3Dweb%26utm_campaign%3Dweb-landing-hero`

- `utm_source=cumulus.team`, `utm_medium=web`, `utm_campaign=<위 ct 표와 같은 값>` — iOS와 같은 위치는 같은 이름을 써서 플랫폼끼리 비교한다. 사이트 밖은 `utm_source=<instagram 등>&utm_medium=social|community|qr`.
- referrer 값 전체를 한 번 URL 인코딩한다(`=`→`%3D`, `&`→`%26`). HTML 속성 안에서 `id=…&referrer=` 사이의 `&`는 `&amp;`.
- 보는 곳: Play Console › 통계 › 스토어 등록정보 획득(UTM 캠페인별 방문·설치) / Firebase Analytics 첫 사용자 소스·캠페인(앱 SDK가 Play Install Referrer로 읽음).
- 출시 전에는 링크를 내보내지 않는다. weatherfit은 `build_landing.py`의 `PLAY_LIVE`(False)·`play_link(ct)`로 준비돼 있다. 출시하면 True로 바꾸고 FAQ·meta·JSON-LD·llms.txt의 "iPhone 전용" 문구를 같이 고친다.
