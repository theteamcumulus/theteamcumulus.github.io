#!/usr/bin/env python3
"""sitemap.xml의 페이지 주소를 IndexNow(Bing·Naver·Yandex 등 공용)로 제출해 새로 수집해 달라고 알린다.

  python3 tools/indexnow.py            # 저장소 루트에서, push 후 GitHub Pages 배포가 끝난 다음 실행
  python3 tools/indexnow.py --dry-run  # 보낼 주소만 출력

- 키는 공개용이다. 사이트 루트의 <KEY>.txt가 소유 확인 파일이며 지우지 않는다(AGENTS.md).
- ChatGPT 검색은 Bing 색인을 많이 쓰므로, 페이지·아이콘을 바꾼 뒤 실행하면 반영이 빨라진다.
- 사이트 빌드에서 제외된다(_config.yml exclude: tools/).
"""
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOST = 'cumulus.team'
KEY = 'fb31c6d11c670e1c946929476738568d'
ENDPOINT = 'https://api.indexnow.org/indexnow'


def urls():
    text = (ROOT / 'sitemap.xml').read_text()
    return re.findall(r'<url><loc>([^<]+)</loc>', text)


def main():
    if not (ROOT / f'{KEY}.txt').exists():
        print(f'키 파일 {KEY}.txt 없음', file=sys.stderr)
        return 1
    url_list = urls()
    if '--dry-run' in sys.argv:
        print('\n'.join(url_list))
        return 0
    body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': f'https://{HOST}/{KEY}.txt',
                       'urlList': url_list}).encode()
    req = urllib.request.Request(ENDPOINT, data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f'IndexNow {r.status}: {len(url_list)}개 주소 제출')
    except urllib.error.HTTPError as e:
        print(f'IndexNow 실패 {e.code}: {e.read().decode(errors="ignore")[:300]}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
