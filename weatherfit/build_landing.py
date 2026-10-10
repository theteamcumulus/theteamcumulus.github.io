#!/usr/bin/env python3
"""출퇴근날씨 랜딩 페이지 생성기: 본문 FAQ와 JSON-LD FAQ를 같은 데이터에서 만들어 문장이 항상 같게 유지한다.

  python3 weatherfit/build_landing.py   # 저장소 루트에서 실행 → weatherfit/index.html

앱 기능이 바뀌면 FAQS·FEATURES와 TODAY, llms.txt의 출퇴근날씨 항목을 함께 고친다.
"""
import html
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / 'index.html'
APP = 'https://apps.apple.com/kr/app/id6819701703'
BASE = 'https://cumulus.team/weatherfit/'
TODAY = '2026-10-11'
TODAY_KO = '2026년 10월 11일'
VERSION = '1.0.0'

FAQS = [
    ("출근길 날씨와 퇴근길 날씨를 한 번에 볼 수 있는 앱이 있나요?",
     "출퇴근날씨는 출근(기본 오전 8시)·점심(12시)·퇴근(오후 6시) 세 시간대의 기온, 체감, 강수확률, 바람, 자외선을 한 화면에 보여주는 아이폰 날씨 앱입니다. 대한민국 기상청 단기예보와 초단기실황을 바탕으로 하며, 퇴근 시각이 지나면 자동으로 내일 출퇴근 날씨로 바뀝니다."),
    ("출퇴근날씨는 어떤 앱인가요?",
     "직장인이 밖에 나서는 세 순간의 날씨를 '내가 느끼는 체감'과 옷차림으로 알려주는 아이폰 앱입니다. 체감은 '출근길 사우나', '트렌치코트 시즌', '걷고 싶은 날'처럼 10단계 문구로 보여주고(비·눈 오는 날, 월요일·금요일엔 그에 어울리는 문구가 섞여요), 우산·마스크 같은 준비물도 알려줍니다. 무료이며 광고와 회원가입이 없습니다."),
    ("같은 기온이라도 나는 더 춥게 느끼는데, 내 체감에 맞출 수 있나요?",
     "네. '지금 내 체감은?'에서 실제로 느끼는 단계를 고르면 그때의 온도·습도·바람·비·자외선을 함께 기록해 나만의 기준을 학습합니다. 추위를 많이 타거나 습하면 유독 덥게 느끼는 사람도 기록이 쌓일수록 시간대별 체감과 옷차림이 내 기준으로 보정됩니다. 기록은 기기에만 저장됩니다."),
    ("일교차가 큰 날 출근 옷차림은 어떻게 추천하나요?",
     "아침에 한 번 입고 나가 하루를 보낸다는 기준으로, 출근·점심·퇴근 세 시간대의 내 체감 중 가장 쌀쌀한 때에 맞춘 하루 옷차림을 추천합니다. 일교차가 8도 이상이면 겹쳐 입기를, 비가 오는 시간대가 있으면 우산을 챙기라고 알려주고, 점심·퇴근 카드에는 '아침 겉옷은 벗어 두세요', '겉옷 다시 챙겨 입으세요'처럼 그때 할 일을 보여줍니다. 상단 현재 날씨에는 지금과 가장 가까운 시간대의 옷차림이 나옵니다."),
    ("출근 시간이 8시가 아니어도 되나요?",
     "네. '내 출퇴근 시간'에서 출근(오전 5시~10시 30분), 점심(오전 11시~오후 2시 30분), 퇴근(오후 3시~10시) 시각을 30분 단위로 바꿀 수 있습니다. 바꾼 시각은 시간대 카드와 홈 화면 위젯에 바로 반영되고, 내일 날씨로 넘어가는 시점도 퇴근 시각을 따릅니다."),
    ("집과 직장 날씨를 따로 볼 수 있나요?",
     "네. '내 장소'에서 집과 직장을 현재 위치나 주소로 정하면 출근은 집, 점심과 퇴근은 직장 위치의 기상청 예보를 보여줍니다. 주말·공휴일에는 모든 시간대가 집 기준이고, 정하지 않으면 현재 위치를 씁니다. 홈 화면 위젯에도 '집 마포구', '직장 강남구'처럼 표시됩니다."),
    ("주말이나 공휴일에는 어떻게 보이나요?",
     "토요일·일요일과 공휴일·대체공휴일에는 출근·퇴근 대신 '느긋한 아침 · 한가한 점심 · 저녁 나들이'로 바뀌고, 체감 문구도 '피크닉하기 좋은 날', '쉬는 날 날씨 최고'처럼 쉬는 날 톤으로 나옵니다. 공휴일 정보는 한국천문연구원 특일 정보(공공데이터포털) 기준으로 2026~2027년을 담고 있으며, 임시공휴일은 앱 업데이트 없이 반영할 수 있습니다."),
    ("홈 화면 위젯이 있나요?",
     "소·중·대 세 가지 크기의 홈 화면 위젯이 있습니다. 작은 위젯은 지금 날씨와 체감·옷차림을, 중간·큰 위젯은 출근·점심·퇴근 날씨를 보여줍니다. 위젯은 약 30분마다 스스로 기상청 예보를 받아 갱신되고, 새로고침 버튼(↻)을 누르면 바로 최신 날씨로 바뀝니다. 앱과 같은 출퇴근 시간, 집·직장 위치, 쉬는 날 문구, 하루 옷차림을 따릅니다. 위젯은 iOS 17 이상에서 쓸 수 있습니다."),
    ("출근 전날 밤에 내일 날씨를 알려주나요?",
     "네. '저녁 9시 출근 날씨 알림'을 켜면 출근하는 날 전날 밤 9시에 내일 출근길 기온과 체감, 하루 옷차림, 점심·퇴근길 기온, 일교차·우산 안내를 한 번에 알려줍니다. 다음날이 주말·공휴일이면 보내지 않으며, 기본값은 꺼짐입니다. 알림은 기기 안에서 예약되는 로컬 알림입니다."),
    ("지금 기온이 기상청 발표와 같은가요?",
     "상단 현재 날씨는 기상청 초단기실황(매시 정시 관측)을 쓰며, 정시 관측이 나오는 대로(보통 정시 5분쯤) 반영합니다. 아직 이번 시각 자료가 없으면 직전 관측을 보여주고, 앱을 켜 둔 채로 있어도 10분이 지나면 알아서 새로 받습니다. 햇빛이 없는 시간엔 자외선, 비 올 확률이 없으면 강수확률을 숨겨 화면을 단순하게 유지하고, 자외선이 강하면 날씨 설명에 햇볕 안내를 덧붙입니다."),
    ("무료인가요? 개인정보는 어떻게 다루나요?",
     "무료이며 광고와 회원가입이 없습니다. 위치는 날씨를 조회하는 데에만 쓰이고, 체감 기록과 집·직장 위치는 기기에만 저장됩니다. 앱 개선을 위해 익명 오류 정보와 사용 통계만 수집하며 광고 식별자(IDFA)는 쓰지 않습니다."),
    ("해외나 안드로이드에서도 쓸 수 있나요?",
     "기상청 예보는 대한민국 위치에서만 제공되므로 국내에서만 쓸 수 있습니다. 현재 iPhone 전용이며 안드로이드 버전은 없습니다."),
]

FEATURES = [
    ("세 번의 외출 날씨", "출근(8시)·점심(12시)·퇴근(18시)의 기온·체감·강수확률·바람·자외선. 퇴근 후엔 내일 날씨로 자동 전환."),
    ("내 체감 학습", "“지금 내 체감은?”에 답하면 온도·습도·바람·비·자외선별로 내 기준을 학습해 보정해요."),
    ("하루 옷차림", "가장 쌀쌀한 때 기준 하루 옷차림, 일교차 큰 날 겹쳐 입기, 비 오는 시간대 우산 안내."),
    ("내 출퇴근 시간", "출근·점심·퇴근 시각을 30분 단위로 바꾸면 카드와 위젯이 그대로 따라와요."),
    ("집·직장 위치", "출근은 집, 점심·퇴근은 직장 날씨. 주소 검색이나 현재 위치로 설정해요."),
    ("주말·공휴일 쉬는 날 모드", "“느긋한 아침 · 한가한 점심 · 저녁 나들이”와 쉬는 날 문구로 바뀌어요."),
    ("홈 화면 위젯", "작은 위젯은 지금 날씨, 중간·큰 위젯은 출근·점심·퇴근. 30분마다 스스로 갱신하고 새로고침 버튼으로 바로."),
    ("실시간 현재 날씨", "기상청 정시 관측을 바로 반영하고, 자외선이 강하면 햇볕 안내까지. 필요 없는 정보는 숨겨서 깔끔하게."),
    ("저녁 9시 출근 날씨 알림", "출근하는 날 전날 밤 9시, 내일 출근길 날씨와 하루 옷차림을 알림으로 요약해 드려요."),
    ("체감 10단계 문구", "“트렌치코트 시즌”, “걷고 싶은 날”, “빗소리 좋은 날”, “날씨까지 불금”처럼 날씨·요일에 어울리는 문구."),
]

SHOTS = [
    ("screen-01.jpg", "현재 날씨: 서울 18°, 체감 문구 '딱 좋아요', 옷차림과 '지금 내 체감은?' 선택 카드", "출근·점심·퇴근, 내가 느끼는 날씨"),
    ("screen-02.jpg", "'지금 내 체감은?'에서 '선선'을 골라 기록한 화면, 내 기준 체감 17°", "답할수록 나에게 맞춰지는 체감"),
    ("screen-03.jpg", "내일의 외출: 출근 오전 8시 15°, 점심 12시 23°, 퇴근 오후 6시 23° 카드와 체감 문구·옷차림", "세 번의 외출을 한눈에"),
    ("screen-04.jpg", "내 출퇴근 시간 설정: 출근 오전 8:00, 점심 오후 12:00, 퇴근 오후 6:00을 30분 단위로 조절", "내 출퇴근 시간에 맞춰서"),
    ("screen-05.jpg", "홈 화면 위젯: 중형은 출근길 12°·점심 21°·퇴근길 17°, 소형은 지금 11° 트렌치코트 시즌, 대형은 하루 옷차림과 일교차 안내", "홈 화면 위젯"),
    ("screen-06.jpg", "일요일 화면: '오늘은 일요일 · 출근 없는 날' 배지와 쉬는 날 문구, 저녁 9시 출근 날씨 알림 켜짐과 다음 알림 시각", "쉬는 날 버전과 저녁 9시 알림"),
]

PRIVACY_LINK = ' 자세한 내용은 <a href="/weatherfit/privacy/">개인정보 처리방침</a>을 보세요.'

ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "Organization", "@id": "https://cumulus.team/#org", "name": "Team Cumulus",
     "url": "https://cumulus.team/", "email": "theteamcumulus@gmail.com"},
    {"@type": "MobileApplication", "@id": BASE + "#app", "name": "출퇴근날씨",
     "alternateName": ["출퇴근 날씨", "WeatherFit"],
     "description": "출근·점심·퇴근 세 시간대의 기상청 예보를 내가 느끼는 체감과 하루 옷차림으로 알려주는 아이폰 날씨 앱. 기상청 실시간 현재 날씨, 내 체감 학습, 집·직장 위치, 주말·공휴일 쉬는 날 문구, 출근 전날 저녁 9시 알림, 홈 화면 위젯.",
     "url": BASE, "sameAs": [APP], "installUrl": APP, "downloadUrl": APP,
     "operatingSystem": "iOS 15.1 이상 (위젯은 iOS 17 이상)", "availableOnDevice": "iPhone",
     "applicationCategory": "WeatherApplication", "applicationSubCategory": "출퇴근 날씨",
     "inLanguage": "ko", "countriesSupported": "KR", "softwareVersion": VERSION, "contentRating": "4+",
     "image": BASE + "img/icon-512.png", "screenshot": [BASE + "img/" + f for f, _, _ in SHOTS],
     "featureList": [f"{t}: {d}" for t, d in FEATURES],
     "offers": {"@type": "Offer", "price": "0", "priceCurrency": "KRW"},
     "author": {"@id": "https://cumulus.team/#org"}, "publisher": {"@id": "https://cumulus.team/#org"}},
    {"@type": "WebPage", "@id": BASE + "#page", "url": BASE, "name": "출퇴근날씨 - 출근·점심·퇴근, 내가 느끼는 날씨",
     "inLanguage": "ko", "about": {"@id": BASE + "#app"}, "dateModified": TODAY},
    {"@type": "FAQPage", "@id": BASE + "#faq", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQS]},
]}

esc = html.escape
features_html = "\n".join(f"          <li><strong>{esc(t)}</strong>{esc(d)}</li>" for t, d in FEATURES)
faq_html = "\n".join(
    f'        <details{" open" if i == 0 else ""}><summary>{esc(q)}</summary>\n'
    f'          <p>{esc(a)}{PRIVACY_LINK if q.startswith("무료") else ""}</p></details>'
    for i, (q, a) in enumerate(FAQS))
shots_html = "\n".join(
    f'          <li><figure><img src="/weatherfit/img/{f}" width="600" height="1304" loading="lazy" alt="{esc(alt)}">'
    f'<figcaption>{esc(cap)}</figcaption></figure></li>' for f, alt, cap in SHOTS)
ld_json = json.dumps(ld, ensure_ascii=False, indent=2)

TEMPLATE = Path(__file__).resolve().parent / 'landing.template.html'
page = (TEMPLATE.read_text()
        .replace('{{APP}}', APP).replace('{{BASE}}', BASE).replace('{{TODAY}}', TODAY)
        .replace('{{TODAY_KO}}', TODAY_KO).replace('{{VERSION}}', VERSION)
        .replace('{{LD_JSON}}', ld_json).replace('{{FEATURES}}', features_html)
        .replace('{{SHOTS}}', shots_html).replace('{{FAQ}}', faq_html))
OUT.write_text(page)
print(f'{OUT.name}: {len(FAQS)} FAQ, {len(page)} chars')
