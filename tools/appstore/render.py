#!/usr/bin/env python3
"""apps.json → 랜딩 페이지·허브·llms.txt·/apps.json·sitemap.xml 갱신. 몇 번 실행해도 결과가 같다.

  python3 tools/appstore/sync.py && python3 tools/appstore/render.py   # 저장소 루트에서

- 각 랜딩의 <!-- appstore:<이름>:start --> … <!-- appstore:<이름>:end --> 사이만 다시 쓴다. 마커 밖은 사람이 고친다.
- FAQPage JSON-LD는 본문 FAQ(<section id="faq">의 details)를 읽어 만든다. 본문 FAQ를 고치면 render만 다시 돌리면 된다.
- 출퇴근날씨는 weatherfit/build_landing.py를 실행한다(그 스크립트도 이 모듈의 블록을 쓴다).
- 마커가 없거나 FAQ를 못 찾으면 아무 파일도 쓰지 않고 종료 코드 1.
"""
import json
import re
import subprocess
import sys

import appstore_lib as AS

ROOT = AS.ROOT
INLINE = {'updated'}
MARK = re.compile(r'(?P<indent>[ \t]*)<!-- appstore:(?P<name>[a-z-]+):start -->.*?<!-- appstore:(?P=name):end -->', re.S)


def fill(text, content, path):
    seen = set()

    def rep(m):
        name, indent = m.group('name'), m.group('indent')
        if name not in content:
            raise KeyError(f'{path}: 알 수 없는 마커 {name}')
        seen.add(name)
        start, end = f'<!-- appstore:{name}:start -->', f'<!-- appstore:{name}:end -->'
        if name in INLINE:
            return f'{indent}{start}{content[name]}{end}'
        body = content[name]
        return f'{indent}{start}\n{body}\n{indent}{end}' if body else f'{indent}{start}\n{indent}{end}'

    out = MARK.sub(rep, text)
    missing = set(content) - seen
    if missing:
        raise KeyError(f'{path}: 마커 없음 {sorted(missing)}')
    return out


def render_page(data, app, page):
    path = ROOT / page['file']
    text = path.read_text()
    shots = page['shots']
    faqs = AS.faqs_from_html(text)
    content = AS.blocks(app, page, data, shots)
    content['head'] = AS.block_head(app, page, AS.ld_graph(app, page, data, shots, faqs))
    return path, fill(text, content, page['file'])


# ---------- 허브 ----------

def hub_card(data, app):
    page = app['pages'][0]
    store = AS.store_for(app, page)
    links = app['links']
    name = AS.page_name(app, page)
    if store:
        meta = f'{AS.esc(store["genres"][0])} · {AS.esc(store["formattedPrice"])}'
        if AS.has_rating(store):
            meta += f' · ★ {AS.rating_text(store)} (평가 {store["userRatingCount"]}개)'
    else:
        meta = 'App Store 출시 예정'
    parts = []
    if store:
        parts.append(f'<a href="{page["storeUrl"]}?pt={data["site"]["pt"]}&amp;ct=web-hub&amp;mt=8">App Store에서 보기</a>')
    parts += [f'<a href="{links["support"]["ko"]}">지원</a>', f'<a href="{links["privacy"]["ko"]}">개인정보 처리방침</a>']
    if 'en' in links['landing']:
        parts += [f'<a href="{links["landing"]["en"]}" hreflang="en" lang="en">English</a>',
                  f'<a href="{links["support"]["en"]}" hreflang="en" lang="en">Support</a>',
                  f'<a href="{links["privacy"]["en"]}" hreflang="en" lang="en">Privacy Policy</a>']
    return f'''          <li class="as-app">
            <img class="as-icon" src="/{app["slug"]}/img/icon-512.png" width="64" height="64" alt="">
            <h3><a href="{links["landing"]["ko"]}">{AS.esc(name)}</a></h3>
            <p>{AS.esc(app["subtitle"]["ko"])}</p>
            <p class="as-meta-line">{meta}</p>
            <p class="as-links">{" · ".join(parts)}</p>
          </li>'''


def render_hub(data):
    path = ROOT / 'index.html'
    base = data['site']['base']
    checked = max((s['checked'] for a in data['apps'] for s in a['store'].values()), default=None)
    apps = '\n'.join(hub_card(data, a) for a in data['apps'])
    note = (f'\n        <p class="as-src">App Store 정보 확인: <time datetime="{checked}">{AS.fmt_date(checked, "ko")}</time></p>'
            if checked else '')
    items = [{'@type': 'ListItem', 'position': i + 1,
              'item': {'@type': 'MobileApplication', '@id': f'{base}/{a["slug"]}/#app', 'name': AS.page_name(a, a['pages'][0]),
                       'url': base + a['links']['landing']['ko'], 'image': f'{base}/{a["slug"]}/img/icon-512.png'}}
             for i, a in enumerate(data['apps'])]
    ld = {'@context': 'https://schema.org', '@graph': [
        AS.org_node(data),
        {'@type': 'WebPage', '@id': base + '/#page', 'url': base + '/', 'name': 'Team Cumulus - iPhone 앱', 'inLanguage': 'ko',
         'about': {'@id': base + '/#org'}, 'dateModified': data['site']['hubModified']},
        {'@type': 'ItemList', '@id': base + '/#apps', 'name': 'Team Cumulus iPhone 앱', 'numberOfItems': len(items),
         'itemListElement': items}]}
    content = {
        'hub-head': '  <script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False, indent=2) + '\n  </script>',
        'css': AS.block_css(),
        'hub-apps': f'        <ul class="as-apps">\n{apps}\n        </ul>{note}',
    }
    return path, fill(path.read_text(), content, 'index.html')


# ---------- /apps.json (공개 카탈로그) ----------

def catalog(data):
    base = data['site']['base']
    apps = []
    for a in data['apps']:
        kr = (a['store'] or {}).get(a['storeCountries'][0]) if AS.is_live(a) else None
        entry = {
            'slug': a['slug'], 'status': a['status'], 'trackId': a['trackId'],
            'trackName': kr['trackName'] if kr else a['name']['ko'], 'names': a['name'],
            'subtitle': a['subtitle'], 'subtitleSource': a['subtitleSource'],
            'developer': data['site']['developer'],
            'summary': a['summary'],
            'iconUrl': f'{base}/{a["slug"]}/img/icon-512.png',
            'landingUrls': {k: base + v for k, v in a['links']['landing'].items()},
            'supportUrls': {k: base + v for k, v in a['links']['support'].items()},
            'privacyUrls': {k: base + v for k, v in a['links']['privacy'].items()},
        }
        if kr:
            entry['appStoreUrl'] = a['pages'][0]['storeUrl']
            for k in ['bundleId', 'version', 'currentVersionReleaseDate', 'releaseDate', 'releaseNotes', 'genres', 'primaryGenreName',
                      'trackContentRating', 'averageUserRating', 'userRatingCount', 'fileSizeBytes', 'minimumOsVersion',
                      'languageCodesISO2A', 'formattedPrice', 'price', 'currency', 'artworkUrl512', 'checked']:
                entry[k] = kr.get(k)
            entry['storefront'] = a['storeCountries'][0]
            entry['languageCodesISO2A'] = AS.lang_codes(a, kr)
        else:
            entry['minimumOsVersion'] = a['facts']['minimumOsVersion']
            entry['languageCodesISO2A'] = a['facts']['languages']
            entry['price'] = 0
        entry['fit'] = a['fit']
        apps.append(entry)
    return json.dumps({'publisher': data['site']['developer'], 'url': base + '/', 'email': data['site']['email'],
                       'note': 'App Store fields use iTunes Search API (Lookup) names. Ratings are from the storefront noted in "storefront" on the "checked" date.',
                       'apps': apps}, ensure_ascii=False, indent=2) + '\n'


# ---------- llms.txt ----------

def llms_card(data, a):
    s = data['site']
    base = s['base']
    page = a['pages'][0]
    kr = AS.store_for(a, page)
    L = a['llms']
    out = [f'## {L["title"]}', f'![{a["name"]["ko"]} 아이콘]({base}/{a["slug"]}/img/icon-512.png)', '', a['summary']['ko']]
    if 'en' in a['summary']:
        out += ['', a['summary']['en']]
    out += ['', L['intro'], '']
    name = kr['trackName'] if kr else a['name']['ko']
    sub_note = '' if a['subtitleSource'] == 'appstore' else ' (App Store 출시 전, 사이트 표기)'
    out.append(f'- App Store 이름 / 부제: {name} / {a["subtitle"]["ko"]}{sub_note}')
    out.append(f'- 개발자: {s["developer"]}')
    if kr:
        rel = AS.local_date(kr['releaseDate'], 'ko').isoformat()
        upd = AS.local_date(kr['currentVersionReleaseDate'], 'ko').isoformat()
        langs = AS.lang_names(AS.lang_codes(a, kr), 'ko')
        out.append(f'- 상태: App Store 출시 · 카테고리: {", ".join(kr["genres"])} · 가격: {kr["formattedPrice"]} · 연령: {kr["trackContentRating"]}')
        out.append(f'- 버전: {kr["version"]} ({upd}) · 최초 출시: {rel} · iOS {kr["minimumOsVersion"]} 이상 · 언어: {langs} · 크기: {AS.size_mb(kr)}MB')
        if AS.has_rating(kr):
            out.append(f'- 평점: {AS.rating_text(kr)} ({kr["userRatingCount"]}개 평가, 대한민국 App Store, {kr["checked"]} 확인)')
        else:
            out.append(f'- 평점: 아직 표시할 평가 없음 ({kr["checked"]} 확인)')
        out.append(f'- App Store: {page["storeUrl"]}?pt={s["pt"]}&ct=web-llms&mt=8')
    else:
        out.append(f'- 상태: App Store 출시 예정(아직 설치할 수 없음) · 가격: 무료 · iOS {a["facts"]["minimumOsVersion"]} 이상')
    links = a['links']
    en = lambda k: f' (English: {base}{links[k]["en"]})' if 'en' in links[k] else ''
    out.append(f'- 공식 소개·FAQ: {base}{links["landing"]["ko"]}{en("landing")}')
    out.append(f'- 지원: {base}{links["support"]["ko"]}{en("support")}')
    out.append(f'- 개인정보 처리방침: {base}{links["privacy"]["ko"]}{en("privacy")}')
    out += ['', '이런 분께 추천:'] + [f'- {x}' for x in a['fit']['ko']['for']]
    out += ['', '맞지 않는 경우:'] + [f'- {x}' for x in a['fit']['ko']['not']]
    out += ['', L['factsHeading']] + [f'- {x}' for x in L['facts']]
    return '\n'.join(out)


def llms(data):
    s = data['site']
    base = s['base']
    checked = max((st['checked'] for a in data['apps'] for st in a['store'].values()), default='')
    rows = []
    for a in data['apps']:
        page = a['pages'][0]
        kr = AS.store_for(a, page)
        status = f'App Store 출시 ({kr["version"]})' if kr else '출시 예정'
        rows.append(f'| {a["llms"]["title"]} | {a["subtitle"]["ko"]} | {status} | {base}{a["links"]["landing"]["ko"]} |')
    head = [
        f'# {s["developer"]}', '',
        f'> {s["developer"]}가 만든 iPhone 앱의 공식 안내 페이지. 문의: {s["email"]}', '',
        f'모든 앱은 iPhone용이며 무료이고 광고와 회원가입이 없다.',
        f'App Store 등록정보는 {checked}에 iTunes Lookup으로 확인했다. 기계 판독용 카탈로그: {base}/apps.json', '',
        '| 앱 | App Store 부제 | 상태 | 공식 페이지 |', '|---|---|---|---|', *rows, '',
    ]
    return '\n'.join(head) + '\n' + '\n\n'.join(llms_card(data, a) for a in data['apps']) + '\n'


# ---------- sitemap ----------

def sitemap(data, text):
    base = data['site']['base']
    dates = {base + '/': data['site']['hubModified']}
    for a in data['apps']:
        for p in a['pages']:
            dates[base + p['path']] = p['modified']
    for url, d in dates.items():
        text, n = re.subn(rf'(<loc>{re.escape(url)}</loc><lastmod>)[0-9-]+(</lastmod>)', rf'\g<1>{d}\2', text)
        if n != 1:
            raise KeyError(f'sitemap.xml: {url} 항목 없음')
    return text


def main():
    data = AS.load()
    writes = []
    try:
        for app in data['apps']:
            for page in app['pages']:
                if page.get('generator'):
                    continue
                writes.append(render_page(data, app, page))
        writes.append(render_hub(data))
        writes.append((ROOT / 'apps.json', catalog(data)))
        writes.append((ROOT / 'llms.txt', llms(data)))
        writes.append((ROOT / 'sitemap.xml', sitemap(data, (ROOT / 'sitemap.xml').read_text())))
    except (KeyError, ValueError) as e:
        print(f'render 실패, 파일 변경 없음: {e}', file=sys.stderr)
        return 1
    for path, text in writes:
        if not path.exists() or path.read_text() != text:
            path.write_text(text)
            print('updated', path.relative_to(ROOT))
    for app in data['apps']:
        for page in app['pages']:
            if page.get('generator'):
                subprocess.run([sys.executable, page['generator']], cwd=ROOT, check=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
