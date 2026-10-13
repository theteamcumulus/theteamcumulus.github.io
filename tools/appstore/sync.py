#!/usr/bin/env python3
"""iTunes Lookup으로 App Store 등록정보를 받아 tools/appstore/apps.json의 store 객체와 status를 갱신한다.

  python3 tools/appstore/sync.py && python3 tools/appstore/render.py   # 저장소 루트에서

- 앱마다 storeCountries의 나라별로 https://itunes.apple.com/lookup?id=<trackId>&country=<cc>&lang=<ko_kr|en_us> 조회.
- 결과가 1건이면 status=live, 0건이면 status=coming_soon(출시 전·판매 중지). trackId가 없으면(Pixder) 건너뛴다.
- 네트워크 오류나 이상한 응답이면 apps.json을 건드리지 않고 종료 코드 1로 끝난다(출시 상태를 잘못 바꾸지 않기 위해).
- 사이트 빌드에서 제외된다(_config.yml exclude: tools/).
"""
import json
import sys
import urllib.request
from datetime import datetime

from appstore_lib import DATA, KST

LOOKUP = 'https://itunes.apple.com/lookup?id={id}&country={cc}&lang={lang}'
LANG = {'kr': 'ko_kr'}
FIELDS = ['trackId', 'trackName', 'bundleId', 'version',
          'currentVersionReleaseDate', 'releaseDate', 'releaseNotes', 'genres', 'genreIds', 'primaryGenreName',
          'trackContentRating', 'averageUserRating', 'userRatingCount', 'fileSizeBytes', 'minimumOsVersion',
          'languageCodesISO2A', 'formattedPrice', 'price', 'currency', 'artworkUrl512', 'trackViewUrl']
REQUIRED = ['trackName', 'version', 'currentVersionReleaseDate', 'releaseDate', 'genres', 'trackContentRating',
            'fileSizeBytes', 'minimumOsVersion', 'languageCodesISO2A', 'formattedPrice']


def lookup(track_id, cc):
    url = LOOKUP.format(id=track_id, cc=cc, lang=LANG.get(cc, 'en_us'))
    with urllib.request.urlopen(url, timeout=30) as r:
        body = json.loads(r.read().decode('utf-8'))
    if 'resultCount' not in body:
        raise ValueError(f'unexpected response for {track_id}/{cc}')
    return body['results'][0] if body['resultCount'] else None


def pick(result, today):
    missing = [k for k in REQUIRED if result.get(k) in (None, '', [])]
    if missing:
        raise ValueError(f'{result.get("trackId")}: missing {missing}')
    out = {k: result.get(k) for k in FIELDS}
    out['trackViewUrl'] = (out['trackViewUrl'] or '').split('?')[0]
    out['averageUserRating'] = round(float(out['averageUserRating'] or 0), 2)
    out['userRatingCount'] = int(out['userRatingCount'] or 0)
    out['checked'] = today
    return out


def main():
    data = json.loads(DATA.read_text())
    today = datetime.now(KST).date().isoformat()
    try:
        for app in data['apps']:
            if not app.get('trackId'):
                print(f'{app["slug"]}: trackId 없음 → {app["status"]} 유지')
                continue
            store = {cc: lookup(app['trackId'], cc) for cc in app['storeCountries']}
            primary = store[app['storeCountries'][0]]
            if primary is None:
                app['status'], app['store'] = 'coming_soon', {}
                print(f'{app["slug"]}: lookup 0건 → coming_soon')
                continue
            app['status'] = 'live'
            app['store'] = {cc: pick(r, today) for cc, r in store.items() if r is not None}
            print(f'{app["slug"]}: live {primary["version"]} ({", ".join(app["store"])})')
    except Exception as e:  # 실패하면 기존 apps.json을 그대로 둔다
        print(f'sync 실패, apps.json 변경 없음: {e}', file=sys.stderr)
        return 1
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
