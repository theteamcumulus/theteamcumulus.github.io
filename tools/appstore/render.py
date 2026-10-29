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
SUPPORT_MARK = re.compile(r'<!-- appstore:faq-ld:start -->.*?<!-- appstore:faq-ld:end -->', re.S)
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
            <img class="as-icon" src="{AS.icon_path(app)}" width="64" height="64" alt="">
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
                       'url': base + a['links']['landing']['ko'], 'image': base + AS.icon_path(a)}}
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
            'iconUrl': base + AS.icon_path(a),
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
    out = [f'## {L["title"]}', f'![{a["name"]["ko"]} 아이콘]({base}{AS.icon_path(a)})', '', a['summary']['ko']]
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
        f'사업자 정보: 상호 {s["developer"]}, 대표자 {s["representative"]}, 사업자등록번호 {s["businessNumber"]}. '
        f'개인정보 처리방침: {base}{s["privacy"]["ko"]} (English: {base}{s["privacy"]["en"]})', '',
        f'모든 앱은 iPhone용이며 무료이고 광고와 회원가입이 없다.',
        f'App Store 등록정보는 {checked}에 iTunes Lookup으로 확인했다. 기계 판독용 카탈로그: {base}/apps.json · 랜딩 본문(기능·사용법·FAQ)까지 담은 전체판: {base}/llms-full.txt', '',
        '| 앱 | App Store 부제 | 상태 | 공식 페이지 |', '|---|---|---|---|', *rows, '',
    ]
    return '\n'.join(head) + '\n' + '\n\n'.join(llms_card(data, a) for a in data['apps']) + '\n'



# ---------- 지원 페이지 FAQPage JSON-LD ----------

def render_support(data, app):
    """<app>/support.md·<app>/en/support.md의 <!-- appstore:faq-ld:start/end --> 사이에 본문 FAQ로 만든 FAQPage JSON-LD를 넣는다. 마커가 없으면 건너뛴다."""
    base = data['site']['base']
    out = []
    for lang, url in app['links']['support'].items():
        path = ROOT / url.strip('/') / '..' / ('support.md' if lang == 'ko' else 'support.md')
        path = (ROOT / app['slug'] / ('support.md' if lang == 'ko' else 'en/support.md'))
        if not path.exists():
            continue
        text = path.read_text()
        if not SUPPORT_MARK.search(text):
            continue
        body = text.split('---', 2)[2]
        faqs = AS.faqs_from_markdown(SUPPORT_MARK.sub('', body))
        if not faqs:
            raise ValueError(f'{path}: FAQ 없음')
        ld = {'@context': 'https://schema.org', '@type': 'FAQPage', '@id': f'{base}{url}#faq', 'inLanguage': lang,
              'about': {'@id': f'{base}/{app["slug"]}/#app'},
              'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]}
        block = ('<!-- appstore:faq-ld:start -->\n<script type="application/ld+json">\n'
                 + json.dumps(ld, ensure_ascii=False, indent=2) + '\n</script>\n<!-- appstore:faq-ld:end -->')
        out.append((path, SUPPORT_MARK.sub(lambda m: block, text)))
    return out


# ---------- llms-full.txt (랜딩 본문까지 담은 전체판) ----------

SECTION_RE = re.compile(r'<section id="(features|how)"[^>]*>(.*?)</section>', re.S)
LI_RE = re.compile(r'<li[^>]*>(.*?)</li>', re.S)


def landing_body(text):
    """랜딩 HTML에서 주요 기능·사용법·FAQ를 글로 뽑는다(본문 문장 그대로)."""
    parts = {}
    for sid, body in SECTION_RE.findall(text):
        h = re.search(r'<h2[^>]*>(.*?)</h2>', body, re.S)
        items = []
        for li in LI_RE.findall(body):
            m = re.match(r'\s*<strong>(.*?)</strong>(.*)', li, re.S)
            items.append(f'{AS.text_of(m.group(1))}: {AS.text_of(m.group(2))}' if m else AS.text_of(li))
        parts[sid] = (AS.text_of(h.group(1)) if h else sid, items)
    try:
        parts['faq'] = ('자주 묻는 질문', AS.faqs_from_html(text))
    except ValueError:
        pass
    return parts


def llms_full(data):
    s = data['site']
    base = s['base']
    out = [f'# {s["developer"]} (전체판)', '',
           f'> {s["developer"]}가 만든 iPhone 앱의 공식 안내 페이지 전체 내용. 요약판: {base}/llms.txt · 카탈로그: {base}/apps.json · 문의: {s["email"]}', '',
           f'사업자 정보: 상호 {s["developer"]}, 대표자 {s["representative"]}, 사업자등록번호 {s["businessNumber"]}. 모든 앱은 iPhone용이며 무료이고 광고와 회원가입이 없다.', '']
    for a in data['apps']:
        out += [llms_card(data, a), '']
        for p in a['pages']:
            if p['lang'] != 'ko':
                continue
            parts = landing_body((ROOT / p['file']).read_text())
            for sid in ('features', 'how', 'faq'):
                if sid not in parts:
                    continue
                title, items = parts[sid]
                out.append(f'### {a["name"]["ko"]} {title} ({base}{p["path"]}#{sid})')
                if sid == 'faq':
                    out += [f'Q. {q}\nA. {ans}\n' for q, ans in items]
                elif sid == 'how':
                    out += [f'{i}. {x}' for i, x in enumerate(items, 1)] + ['']
                else:
                    out += [f'- {x}' for x in items] + ['']
        sp = ROOT / a['slug'] / 'support.md'
        if sp.exists():
            faqs = AS.faqs_from_markdown(SUPPORT_MARK.sub('', sp.read_text().split('---', 2)[2]))
            if faqs:
                out.append(f'### {a["name"]["ko"]} 지원 FAQ ({base}{a["links"]["support"]["ko"]})')
                out += [f'Q. {q}\nA. {ans}\n' for q, ans in faqs]
    return '\n'.join(out).rstrip() + '\n'


# ---------- sitemap ----------

SITEMAP_NS = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
IMAGE_NS = 'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"'


def sitemap(data, text):
    """lastmod 갱신 + 랜딩·허브에 이미지 항목(앱 아이콘·스크린샷·로고)을 붙인다. 이미지 검색·AI가 진짜 아이콘을 찾게 하기 위해."""
    base = data['site']['base']
    entries = {base + '/': (data['site']['hubModified'], [base + data['site']['logo']] if data['site'].get('logo') else [])}
    for a in data['apps']:
        for p in a['pages']:
            # 생성기 페이지(출퇴근날씨)는 스크린샷 목록이 build_landing.py에 있어 img 폴더에서 찾는다.
            shots = [src for src, _, _ in p['shots']] if p.get('shots') else \
                [f'/{a["slug"]}/img/{f.name}' for f in sorted((ROOT / a['slug'] / 'img').glob('screen-*.jpg'))]
            imgs = [base + AS.icon_path(a)] + [base + s for s in shots]
            entries[base + p['path']] = (p['modified'], imgs)
    if IMAGE_NS not in text:
        text = text.replace(SITEMAP_NS, SITEMAP_NS + ' ' + IMAGE_NS, 1)
    for url, (d, imgs) in entries.items():
        images = ''.join(f'\n    <image:image><image:loc>{i}</image:loc></image:image>' for i in imgs)
        tail = (images + '\n  </url>') if imgs else '</url>'
        text, n = re.subn(rf'<url><loc>{re.escape(url)}</loc><lastmod>[0-9-]+</lastmod>(?:\s*<image:image>.*?</image:image>)*\s*</url>',
                          lambda m: f'<url><loc>{url}</loc><lastmod>{d}</lastmod>{tail}', text, flags=re.S)
        if n != 1:
            raise KeyError(f'sitemap.xml: {url} 항목 없음')
    return text


def named_icons(data):
    """<slug>/img/icon-512.png → <slug>-app-icon.png 사본 (바이트가 다를 때만)."""
    out = []
    for a in data['apps']:
        src = ROOT / a['slug'] / 'img' / 'icon-512.png'
        dst = ROOT / AS.icon_path(a).lstrip('/')
        if not dst.exists() or dst.read_bytes() != src.read_bytes():
            dst.write_bytes(src.read_bytes())
            out.append(dst)
    return out


def main():
    data = AS.load()
    for icon in named_icons(data):
        print('updated', icon.relative_to(ROOT))
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
        writes.append((ROOT / 'llms-full.txt', llms_full(data)))
        for app in data['apps']:
            writes += render_support(data, app)
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
