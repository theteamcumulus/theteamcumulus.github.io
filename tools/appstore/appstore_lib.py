"""App Store 스타일 블록 공통 모듈. sync.py·render.py·weatherfit/build_landing.py가 함께 쓴다.

데이터는 tools/appstore/apps.json 하나에서 온다. 이 모듈은 파일을 쓰지 않고 문자열만 만든다.
"""
import html
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = Path(__file__).resolve().parent / 'apps.json'
KST = timezone(timedelta(hours=9))
BASE_URL = 'https://cumulus.team'


def esc(s):
    """본문·속성 공용 이스케이프. 작은따옴표는 그대로 둔다(속성은 모두 큰따옴표)."""
    return html.escape(str(s), quote=False).replace('"', '&quot;')



LANG_NAMES = {
    'ko': {'KO': '한국어', 'EN': '영어', 'JA': '일본어', 'ZH': '중국어', 'ES': '스페인어', 'FR': '프랑스어', 'DE': '독일어',
           'ZH-HANS': '중국어(간체)', 'ZH-HANT': '중국어(번체)'},
    'en': {'KO': 'Korean', 'EN': 'English', 'JA': 'Japanese', 'ZH': 'Chinese', 'ES': 'Spanish', 'FR': 'French', 'DE': 'German',
           'ZH-HANS': 'Chinese (Simplified)', 'ZH-HANT': 'Chinese (Traditional)'},
}

L = {
    'ko': {
        'icon_alt': '{name} 앱 아이콘', 'badge': '/assets/appstore-badge-ko.svg', 'badge_w': 130,
        'badge_alt': 'App Store에서 다운로드', 'soon': 'App Store 출시 예정', 'strip': '앱 요약',
        'ratings': '평가 {n}개', 'stars_vh': '5점 만점에 {r}점', 'age': '연령', 'age_cap': '세', 'category': '카테고리',
        'developer': '개발자', 'language': '언어', 'lang_more': '외 {n}개 언어', 'size': '크기',
        'shots_h': '미리 보기', 'shots_label': '스크린샷 {n}장, 좌우로 넘겨 보기',
        'summary_h': '{name} 한눈에 보기', 'fit_for': '이런 분께 추천', 'fit_not': '이런 경우엔 맞지 않아요',
        'new_h': '새로운 기능', 'version': '버전 {v}',
        'priv_h': '앱 개인정보 보호', 'priv_note': '개인정보 처리방침에서 옮긴 요약입니다.', 'priv_link': '개인정보 처리방침',
        'info_h': '정보', 'info_h_soon': '정보 (출시 예정)', 'seller': '판매자', 'compat': '호환성',
        'compat_val': 'iPhone · iOS {v} 이상 필요', 'languages': '언어', 'age_rating': '연령 등급', 'price': '가격',
        'released': '최초 출시', 'checked': 'App Store 정보 확인', 'updated': '최종 수정', 'app_ver': '(앱 {v} 기준)',
    },
    'en': {
        'icon_alt': '{name} app icon', 'badge': '/assets/appstore-badge-en.svg', 'badge_w': 120,
        'badge_alt': 'Download on the App Store', 'soon': 'Coming soon to the App Store', 'strip': 'App summary',
        'ratings': '{n} Ratings', 'stars_vh': '{r} out of 5', 'age': 'Age', 'age_cap': 'Years Old', 'category': 'Category',
        'developer': 'Developer', 'language': 'Language', 'lang_more': '+ {n} More', 'size': 'Size',
        'shots_h': 'Screenshots', 'shots_label': '{n} screenshots, scroll sideways',
        'summary_h': '{name} at a glance', 'fit_for': 'Great for', 'fit_not': 'Not the right fit if',
        'new_h': "What's New", 'version': 'Version {v}',
        'priv_h': 'App Privacy', 'priv_note': 'Summarized from our privacy policy.', 'priv_link': 'Privacy Policy',
        'info_h': 'Information', 'info_h_soon': 'Information (coming soon)', 'seller': 'Seller', 'compat': 'Compatibility',
        'compat_val': 'iPhone · Requires iOS {v} or later', 'languages': 'Languages', 'age_rating': 'Age Rating',
        'price': 'Price', 'released': 'Released', 'checked': 'App Store information checked', 'updated': 'Last updated',
        'app_ver': '(app {v})',
    },
}

# designer.md §3. 각 페이지의 --bg·--ink·--sub·--line·--soft 변수를 그대로 쓴다.
CSS = """:root{--as-bg:var(--bg);--as-ink:var(--ink);--as-sub:var(--sub);--as-line:var(--line);--as-fill:var(--soft);--as-focus:#0a66d6;--as-edge:rgba(0,0,0,.1);--as-pad:20px;--as-r:16px}
@media (prefers-color-scheme:dark){:root{--as-focus:#8ab8ff;--as-edge:rgba(255,255,255,.16)}}
@media (prefers-contrast:more){:root{--as-sub:var(--ink);--as-line:var(--ink)}}
:focus-visible{outline:3px solid var(--as-focus);outline-offset:2px}
header.hero :focus-visible{outline-color:#fff;box-shadow:0 0 0 6px rgba(0,0,0,.6)}
.as-vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.as-head{display:grid;grid-template-columns:auto 1fr;gap:16px;align-items:start;margin-bottom:20px}
.as-icon{display:block;width:96px;height:96px;border-radius:22.37%;box-shadow:0 0 0 1px var(--as-edge),0 6px 16px rgba(0,0,0,.2)}
.as-name{font-size:1.375rem;line-height:1.25;font-weight:700;margin:0}
.as-sub,.as-dev{margin:2px 0 0;font-size:1rem}.as-dev{font-size:.875rem}.as-dev a{color:inherit}
.as-get{display:inline-block;margin-top:12px;padding:2px 0}.as-get img{display:block;height:40px;width:auto}
.as-soon{display:inline-block;margin:12px 0 0;padding:6px 12px;border:1px solid currentColor;border-radius:8px;font-size:.9375rem;font-weight:600}
.as-tagline{font-size:clamp(1.5rem,4vw,2rem);font-weight:800;line-height:1.3;margin:0 0 10px}
.as-strip{overflow-x:auto;scroll-snap-type:x mandatory;border-bottom:1px solid var(--as-line)}
.as-strip dl{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(104px,1fr);margin:0;padding:14px 0;text-align:center}
.as-strip dl>div{scroll-snap-align:start;padding:0 8px;border-inline-start:1px solid var(--as-line)}
.as-strip dl>div:first-child{border:0}
.as-strip dt,.as-cap{font-size:.75rem;color:var(--as-sub)}
.as-strip dd{margin:0}.as-val{font-size:1.25rem;font-weight:700;color:var(--as-sub);line-height:1.4}
.as-stars{position:relative;display:inline-block;white-space:nowrap;font-size:.75rem;color:var(--as-line)}
.as-stars::before{content:"★★★★★"}
.as-stars::after{content:"★★★★★";position:absolute;left:0;top:0;overflow:hidden;width:calc(var(--r)*20%);color:var(--as-sub)}
.as-shots{display:grid;grid-auto-flow:column;grid-auto-columns:min(62vw,230px);gap:12px;list-style:none;margin:0 calc(-1*var(--as-pad));padding:4px var(--as-pad) 12px;overflow-x:auto;scroll-snap-type:x mandatory;scroll-padding-inline:var(--as-pad);overscroll-behavior-x:contain}
.as-shots li{scroll-snap-align:start;min-width:0}
.as-shots img{display:block;width:100%;height:auto;border-radius:var(--as-r);border:1px solid var(--as-line)}
.as-shots figcaption{font-size:.8125rem;color:var(--as-sub);margin-top:6px}
.as-strip:focus-visible,.as-shots:focus-visible{outline-offset:-3px}
@media (min-width:720px){.as-icon{width:128px;height:128px}.as-name{font-size:1.75rem}.as-shots{grid-auto-columns:250px}}
@media (max-width:360px){.as-icon{width:80px;height:80px}}
.as-meta{display:flex;justify-content:space-between;flex-wrap:wrap;gap:4px 12px;color:var(--as-sub);font-size:.9375rem;margin:0 0 8px}
.as-notes{margin:0;padding-left:1.2em}
.as-info{margin:0}.as-info>div{display:flex;justify-content:space-between;gap:16px;padding:12px 0;border-bottom:1px solid var(--as-line)}
.as-info dt{color:var(--as-sub);flex:none}.as-info dd{margin:0;text-align:end;min-width:0;overflow-wrap:anywhere}
.as-src{font-size:.8125rem;color:var(--as-sub)}
.as-priv{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,220px),1fr));gap:12px;list-style:none;padding:0;margin:0 0 12px}
.as-priv li{background:var(--as-fill);border-radius:var(--as-r);padding:16px}.as-priv strong{display:block}
.as-summary{font-size:1.1875rem;font-weight:600;margin:0 0 20px}
.as-fit{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:12px 24px}
.as-fit h3{font-size:1.0625rem;margin:0 0 6px}.as-fit ul{margin:0;padding-left:1.2em}
.as-apps{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,280px),1fr));gap:0 24px;list-style:none;padding:0;margin:0}
.as-app{position:relative;display:grid;grid-template-columns:64px 1fr;gap:2px 14px;padding:14px 0;border-bottom:1px solid var(--as-line)}
.as-app .as-icon{width:64px;height:64px;grid-row:span 4}.as-app h3{margin:0;font-size:1.0625rem}
.as-app h3 a{color:var(--as-ink);text-decoration:none}.as-app h3 a::after{content:"";position:absolute;inset:0}
.as-app p{margin:0;font-size:.875rem;color:var(--as-sub)}.as-app .as-links{position:relative;z-index:1}
@media (prefers-reduced-motion:no-preference){.as-strip,.as-shots{scroll-behavior:smooth}}"""


def load():
    return json.loads(DATA.read_text())


def app_by_slug(data, slug):
    return next(a for a in data['apps'] if a['slug'] == slug)


def is_live(app):
    return app['status'] == 'live'


def store_for(app, page):
    return (app.get('store') or {}).get(page['storeCountry']) if is_live(app) else None


def _dt(s):
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)


def local_date(iso, lang):
    """App Store 시각을 페이지 기준 날짜로: 한국어는 Asia/Seoul, 영어는 UTC (designer.md §2)."""
    d = _dt(iso)
    return d.astimezone(KST).date() if lang == 'ko' else d.date()


def fmt_date(d, lang):
    if isinstance(d, str):
        d = datetime.strptime(d, '%Y-%m-%d').date()
    return f'{d.year}년 {d.month}월 {d.day}일' if lang == 'ko' else d.strftime('%B ') + f'{d.day}, {d.year}'


def size_mb(store):
    return f"{int(store['fileSizeBytes']) / 1_000_000:.1f}"


def lang_codes(app, store):
    # languageOverride: 앱이 실제로 지원하는 언어가 스토어 표기와 다를 때(예: 출퇴근날씨는 한국어 전용인데 스토어 메타가 EN) 사이트는 이 값을 쓴다.
    codes = app.get('languageOverride') or (store['languageCodesISO2A'] if store else app['facts']['languages'])
    return list(dict.fromkeys(c.upper() for c in codes))


def lang_names(codes, lang):
    return ', '.join(LANG_NAMES[lang].get(c, c) for c in codes)


def min_os(app, store):
    return store['minimumOsVersion'] if store else app['facts']['minimumOsVersion']


def price_text(app, store, lang):
    return store['formattedPrice'] if store else app['facts']['price'][lang]


def has_rating(store):
    return bool(store) and int(store.get('userRatingCount') or 0) >= 1


def rating_text(store):
    return f"{float(store['averageUserRating']):.1f}"


def store_link(page, where, pt):
    ct = f"{page['ct']}-{where}"
    return f"{page['storeUrl']}?pt={pt}&amp;ct={ct}&amp;mt=8"


def icon_path(app):
    """앱 이름이 든 아이콘 경로(이미지 검색·AI가 어느 앱 아이콘인지 알 수 있게). icon-512.png 사본, render.py가 만든다."""
    return f'/{app["slug"]}/img/{app["slug"]}-app-icon.png'


def page_name(app, page):
    store = store_for(app, page)
    return store['trackName'] if store else page['name']


# ---------- HTML blocks ----------

def block_head(app, page, ld_graph):
    out = []
    if is_live(app):
        out.append(f'  <meta name="apple-itunes-app" content="app-id={app["trackId"]}">')
    # 두 번째 og:image: 정사각형 앱 아이콘. 첫 번째(배너)는 SNS 공유용으로 페이지 head에 그대로 둔다.
    icon_url = BASE_URL + icon_path(app)
    alt = esc(L[page['lang']]['icon_alt'].format(name=page_name(app, page)))
    out += [f'  <meta property="og:image" content="{icon_url}">', '  <meta property="og:image:width" content="512">',
            '  <meta property="og:image:height" content="512">', f'  <meta property="og:image:alt" content="{alt}">',
            f'  <link rel="image_src" href="{icon_url}">']
    out.append('  <script type="application/ld+json">')
    out.append(json.dumps(ld_graph, ensure_ascii=False, indent=2))
    out.append('  </script>')
    return '\n'.join(out)


def block_css():
    return '  <style>\n' + CSS + '\n  </style>'


def block_hero(app, page, data):
    lang, t = page['lang'], L[page['lang']]
    name = page_name(app, page)
    sub = app['subtitle'][lang]
    if is_live(app):
        get = (f'      <a class="as-get" href="{store_link(page, "hero", data["site"]["pt"])}">'
               f'<img src="{t["badge"]}" width="{t["badge_w"]}" height="40" alt="{esc(t["badge_alt"])}"></a>')
    else:
        get = f'      <p class="as-soon">{esc(t["soon"])}</p>'
    return '\n'.join([
        '      <div class="as-head">',
        f'        <img class="as-icon" src="{icon_path(app)}" width="128" height="128" alt="{esc(t["icon_alt"].format(name=name))}">',
        '        <div>',
        f'          <h1 class="as-name">{esc(name)}</h1>',
        f'          <p class="as-sub">{esc(sub)}</p>',
        f'          <p class="as-dev"><a href="/">{esc(data["site"]["developer"])}</a></p>',
        '    ' + get,
        '        </div>',
        '      </div>',
    ])


def _strip(app, page, data):
    lang, t = page['lang'], L[page['lang']]
    store = store_for(app, page)
    if not store:
        return ''
    cells = []
    if has_rating(store):
        r = rating_text(store)
        cells.append(f'<div><dt>{t["ratings"].format(n=store["userRatingCount"])}</dt><dd class="as-val">{r}</dd>'
                     f'<dd><span class="as-stars" style="--r:{r}" aria-hidden="true"></span>'
                     f'<span class="as-vh">{t["stars_vh"].format(r=r)}</span></dd></div>')
    cells.append(f'<div><dt>{t["age"]}</dt><dd class="as-val">{esc(store["trackContentRating"])}</dd>'
                 f'<dd class="as-cap">{t["age_cap"]}</dd></div>')
    cells.append(f'<div><dt>{t["category"]}</dt><dd class="as-val">{esc(store["genres"][0])}</dd></div>')
    cells.append(f'<div><dt>{t["developer"]}</dt><dd class="as-cap">{esc(data["site"]["developer"])}</dd></div>')
    codes = lang_codes(app, store)
    here = lang.upper() if lang.upper() in codes else codes[0]
    cap = LANG_NAMES[lang].get(here, here) if len(codes) == 1 else t['lang_more'].format(n=len(codes) - 1)
    cells.append(f'<div><dt>{t["language"]}</dt><dd class="as-val">{here}</dd><dd class="as-cap">{esc(cap)}</dd></div>')
    cells.append(f'<div><dt>{t["size"]}</dt><dd class="as-val">{size_mb(store)}</dd><dd class="as-cap">MB</dd></div>')
    body = '\n'.join('        ' + c for c in cells)
    return (f'    <div class="wrap"><div class="as-strip" role="region" aria-label="{t["strip"]}" tabindex="0"><dl>\n'
            f'{body}\n      </dl></div></div>\n')


def _summary(app, page):
    lang, t = page['lang'], L[page['lang']]
    fit = app['fit'][lang]
    li = lambda xs: '\n'.join(f'            <li>{esc(x)}</li>' for x in xs)
    return f'''    <section id="summary" aria-labelledby="h-summary">
      <div class="wrap">
        <h2 id="h-summary">{esc(t["summary_h"].format(name=page_name(app, page)))}</h2>
        <p class="as-summary">{esc(app["summary"][lang])}</p>
        <div class="as-fit">
          <div><h3>{t["fit_for"]}</h3><ul>
{li(fit["for"])}
          </ul></div>
          <div><h3>{t["fit_not"]}</h3><ul>
{li(fit["not"])}
          </ul></div>
        </div>
      </div>
    </section>
'''


def _shots(page, shots):
    t = L[page['lang']]
    items = '\n'.join(
        f'          <li><figure><img src="{esc(src)}" width="600" height="1304" loading="lazy" alt="{esc(alt)}">'
        f'<figcaption>{esc(cap)}</figcaption></figure></li>' for src, alt, cap in shots)
    return f'''    <section id="screens" aria-labelledby="h-screens">
      <div class="wrap">
        <h2 id="h-screens">{t["shots_h"]}</h2>
        <ul class="as-shots" tabindex="0" aria-label="{t["shots_label"].format(n=len(shots))}">
{items}
        </ul>
      </div>
    </section>
'''


def block_top(app, page, data, shots):
    return (_strip(app, page, data) + _summary(app, page) + _shots(page, shots)).rstrip('\n')


def block_whatsnew(app, page):
    store = store_for(app, page)
    if not store:
        return ''
    lang, t = page['lang'], L[page['lang']]
    iso = store['currentVersionReleaseDate']
    d = local_date(iso, lang)
    notes = []
    items = []
    for line in (store.get('releaseNotes') or '').split('\n'):
        line = line.strip()
        if line.startswith('•'):
            items.append(line.lstrip('•').strip())
            continue
        if items:
            notes.append('        <ul class="as-notes">\n' + '\n'.join(f'          <li>{esc(i)}</li>' for i in items) + '\n        </ul>')
            items = []
        if line:
            notes.append(f'        <p>{esc(line)}</p>')
    if items:
        notes.append('        <ul class="as-notes">\n' + '\n'.join(f'          <li>{esc(i)}</li>' for i in items) + '\n        </ul>')
    body = ('\n' + '\n'.join(notes)) if notes else ''
    return f'''    <section id="whats-new" aria-labelledby="h-new">
      <div class="wrap">
        <h2 id="h-new">{t["new_h"]}</h2>
        <p class="as-meta"><span>{t["version"].format(v=esc(store["version"]))}</span><time datetime="{iso}">{fmt_date(d, lang)}</time></p>{body}
      </div>
    </section>'''


def info_rows(app, page, data):
    """정보 표 행 (라벨, 값). 출시 예정이면 확정된 행만."""
    lang, t = page['lang'], L[page['lang']]
    store = store_for(app, page)
    codes = lang_codes(app, store)
    if not store:
        return [(t['developer'], data['site']['developer']),
                (t['compat'], t['compat_val'].format(v=min_os(app, None))),
                (t['languages'], lang_names(codes, lang)),
                (t['price'], price_text(app, None, lang))]
    return [(t['developer'], data['site']['developer']),
            (t['size'], size_mb(store) + 'MB'),
            (t['category'], ', '.join(store['genres'])),
            (t['compat'], t['compat_val'].format(v=store['minimumOsVersion'])),
            (t['languages'], lang_names(codes, lang)),
            (t['age_rating'], store['trackContentRating']),
            (t['price'], store['formattedPrice']),
            (t['released'], fmt_date(local_date(store['releaseDate'], lang), lang))]


def block_facts(app, page, data):
    lang, t = page['lang'], L[page['lang']]
    store = store_for(app, page)
    priv_link = f'        <p><a href="{app["links"]["privacy"][lang]}">{t["priv_link"]}</a></p>'
    if store:
        items = '\n'.join(f'          <li><strong>{esc(h)}</strong>{esc(x)}</li>' for h, x in app['privacy'][lang])
        priv = (f'        <ul class="as-priv">\n{items}\n        </ul>\n'
                f'        <p class="as-src">{t["priv_note"]}</p>\n{priv_link}')
    else:
        priv = priv_link
    rows = '\n'.join(f'          <div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>' for k, v in info_rows(app, page, data))
    checked = ''
    if store:
        c = store['checked']
        checked = f'\n        <p class="as-src">{t["checked"]}: <time datetime="{c}">{fmt_date(c, lang)}</time></p>'
    return f'''    <section id="privacy" aria-labelledby="h-priv">
      <div class="wrap">
        <h2 id="h-priv">{t["priv_h"]}</h2>
{priv}
      </div>
    </section>

    <section id="info" aria-labelledby="h-info">
      <div class="wrap">
        <h2 id="h-info">{t["info_h"] if store else t["info_h_soon"]}</h2>
        <dl class="as-info">
{rows}
        </dl>{checked}
      </div>
    </section>'''


def block_cta(app, page, data):
    cta = page['cta']
    if is_live(app):
        return (f'        <p>{cta["textLive"]}</p>\n'
                f'        <a class="{cta["class"]}" href="{store_link(page, "bottom", data["site"]["pt"])}">{cta["label"]}</a>')
    return f'        <p>{cta["textSoon"]}</p>\n        <p class="as-soon">{esc(L[page["lang"]]["soon"])}</p>'


def block_updated(app, page):
    lang, t = page['lang'], L[page['lang']]
    m = page['modified']
    s = f'{t["updated"]} <time datetime="{m}">{fmt_date(m, lang)}</time>'
    store = store_for(app, page)
    return s + (' ' + t['app_ver'].format(v=store['version']) if store else '')


def blocks(app, page, data, shots):
    """마커 이름 → 내용. render.py와 build_landing.py가 같은 결과를 쓴다."""
    out = {
        'css': block_css(),
        'hero': block_hero(app, page, data),
        'top': block_top(app, page, data, shots),
        'whatsnew': block_whatsnew(app, page),
        'facts': block_facts(app, page, data),
        'updated': block_updated(app, page),
    }
    if page.get('cta'):  # 출퇴근날씨는 하단 CTA를 템플릿이 직접 갖고 있다
        out['cta'] = block_cta(app, page, data)
    return out


# ---------- JSON-LD ----------

def org_node(data):
    s = data['site']
    node = {'@type': 'Organization', '@id': s['base'] + '/#org', 'name': s['developer'], 'url': s['base'] + '/',
            'email': s['email']}
    if s.get('logo'):
        node['logo'] = s['base'] + s['logo']
    if s.get('representative'):
        node['founder'] = {'@type': 'Person', 'name': s['representative']}
    if s.get('businessNumber'):
        node['taxID'] = s['businessNumber']
    return node


def app_node(app, page, data, shots, extra=None):
    s = data['site']
    lang = page['lang']
    store = store_for(app, page)
    base = s['base']
    node = {'@type': 'MobileApplication', '@id': f'{base}/{app["slug"]}/#app', 'name': page_name(app, page),
            'alternateName': page['alternateName']}
    node.update({k: v for k, v in page.get('ld', {}).items() if k == 'slogan'})
    node['description'] = app['summary'][lang]
    node['url'] = base + page['path']
    if store:
        node['sameAs'] = [page['storeUrl']]
        node['installUrl'] = page['storeUrl']
        node['downloadUrl'] = page['storeUrl']
    node['operatingSystem'] = f'iOS {min_os(app, store)}+'
    node['availableOnDevice'] = 'iPhone'
    node['applicationCategory'] = app['applicationCategory']
    node['applicationSubCategory'] = ', '.join(store['genres']) if store else page['ld']['applicationSubCategory']
    node['inLanguage'] = [c.lower() for c in lang_codes(app, store)]
    if page.get('ld', {}).get('countriesSupported'):
        node['countriesSupported'] = page['ld']['countriesSupported']
    if store:
        node['softwareVersion'] = store['version']
        node['datePublished'] = local_date(store['releaseDate'], lang).isoformat()
        node['dateModified'] = local_date(store['currentVersionReleaseDate'], lang).isoformat()
        node['fileSize'] = size_mb(store) + 'MB'
        node['contentRating'] = store['trackContentRating']
        if store.get('releaseNotes'):
            node['releaseNotes'] = store['releaseNotes']
    node['image'] = {'@type': 'ImageObject', 'url': base + icon_path(app), 'width': 512, 'height': 512,
                     'caption': L[lang]['icon_alt'].format(name=page_name(app, page))}
    node['screenshot'] = [base + src for src, _, _ in shots]
    feats = (extra or {}).get('featureList') or page.get('ld', {}).get('featureList')
    if feats:
        node['featureList'] = feats
    node['offers'] = {'@type': 'Offer', 'price': '0', 'priceCurrency': page['currency']}
    if has_rating(store):
        node['aggregateRating'] = {'@type': 'AggregateRating', 'ratingValue': rating_text(store),
                                   'ratingCount': int(store['userRatingCount']), 'bestRating': '5', 'worstRating': '1'}
    node['author'] = {'@id': base + '/#org'}
    node['publisher'] = {'@id': base + '/#org'}
    return node


def ld_graph(app, page, data, shots, faqs, extra=None):
    base = data['site']['base']
    url = base + page['path']
    graph = [org_node(data), app_node(app, page, data, shots, extra),
             {'@type': 'WebPage', '@id': url + '#page', 'url': url, 'name': page['webpageName'], 'inLanguage': lang_tag(page),
              'about': {'@id': f'{base}/{app["slug"]}/#app'}, 'dateModified': page['modified']}]
    if faqs:
        graph.append({'@type': 'FAQPage', '@id': url + '#faq', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]})
    return {'@context': 'https://schema.org', '@graph': graph}


def lang_tag(page):
    return page['lang']


# ---------- 본문 FAQ → JSON-LD (본문과 같은 문장) ----------

FAQ_RE = re.compile(r'<details(?: open)?><summary>(.*?)</summary>\s*<p>(.*?)</p></details>', re.S)


def text_of(fragment):
    return html.unescape(re.sub(r'<[^>]+>', '', fragment)).strip()


def faqs_from_html(page_html):
    m = re.search(r'<section id="faq">(.*?)</section>', page_html, re.S)
    if not m:
        raise ValueError('FAQ section not found')
    return [(text_of(q), text_of(a)) for q, a in FAQ_RE.findall(m.group(1))]
