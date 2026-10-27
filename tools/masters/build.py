"""Рубрика «Знакомство с мастерами»: подбор анкет и сборка карусели.

python3 build.py candidates OUTDIR            — активные анкеты-кандидаты + contact sheet для визуальной проверки
python3 build.py build SLUG DATE OUTDIR s1 s2 …  — собрать карусель из анкет (slug сайта), 4–6 штук

Фото: https://probody-images-kz.s3.ap-south-1.amazonaws.com/<images[].url>
Отбор: только активные анкеты, фото уникальное (не встречается в других анкетах),
нет отзывов с оценкой ≤2, анкета не была в рубрике последние 4 недели (masters.json).
Фото и описание проверять глазами: только рабочая форма, без откровенных поз и намёков.
"""
import json, os, sys, subprocess, urllib.request, datetime
from PIL import Image, ImageDraw

API = 'https://api.pro-body.kz/api/v1/core/search/x/get-other-random?count=100'
S3 = 'https://probody-images-kz.s3.ap-south-1.amazonaws.com/'
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
QUEUE = os.path.join(REPO, 'masters.json')
SKIP_PROGS = {'Аренда сауны', 'Body Massage - массаж тела'}
CACHE = os.path.join(HERE, '.cache')


def listings():
    return json.load(urllib.request.urlopen(API))


def img(url):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, url)
    if not os.path.exists(p):
        urllib.request.urlretrieve(S3 + url, p)
    return p


def ahash(path):
    im = Image.open(path).convert('L').resize((9, 8)); px = list(im.getdata())
    return sum(1 << i for i in range(64) if px[(i // 8) * 9 + i % 8] > px[(i // 8) * 9 + i % 8 + 1])


def recent_slugs(weeks=4):
    if not os.path.exists(QUEUE):
        return set()
    since = (datetime.date.today() - datetime.timedelta(weeks=weeks)).isoformat()
    return {s for e in json.load(open(QUEUE)) if e['date'] >= since for s in e.get('listings', [])}


def candidates(outdir):
    a = listings(); recent = recent_slugs()
    hashes = {}
    for x in a:
        for m in x['images']:
            hashes.setdefault(ahash(img(m['url'])) >> 8, set()).add(x['slug'])
    out = []
    for x in a:
        if x['entityState'] != 'active' or x['slug'] in recent or not x['images']:
            continue
        if any(min(r['rating'].values()) <= 2 for r in x['reviews']):
            continue
        h = ahash(img(x['images'][0]['url'])) >> 8
        if len(hashes[h]) > 1:
            continue
        out.append(x)
    os.makedirs(outdir, exist_ok=True)
    W, Hh = 240, 320
    sheet = Image.new('RGB', (W * 6, Hh * ((len(out) + 5) // 6)), 'white')
    for k, x in enumerate(out):
        im = Image.open(img(x['images'][0]['url'])).convert('RGB'); im.thumbnail((W, Hh - 22))
        sheet.paste(im, ((k % 6) * W, (k // 6) * Hh + 22)); ImageDraw.Draw(sheet).text(((k % 6) * W + 4, (k // 6) * Hh + 4), x['slug'], fill='red')
        progs = ', '.join(f"{n}={p['price']}" for p in x['programs'] if (n := pname(p)) and n not in SKIP_PROGS)
        print(f"{x['slug']}\t{x['kind']}\t{city(x)}\t{x['name']}\t{(x['description'].get('ru') or '')[:120]!r}\t{progs[:160]}")
    sheet.save(os.path.join(outdir, 'candidates.jpg'), quality=85)
    print('sheet:', os.path.join(outdir, 'candidates.jpg'))


def pname(p):
    n = p['name'] if isinstance(p['name'], str) else (p['name'] or {}).get('ru', '')
    return (n or '').strip()


def city(x):
    loc = x['location']['adress']['locality']
    return loc.get('ru', '') if isinstance(loc, dict) else loc


def addr(x):
    st = x['location']['adress'].get('street') or ''
    s = (st.get('ru', '') if isinstance(st, dict) else st).split(',')
    s = [t.strip() for t in s if t.strip() not in ('Казахстан', 'Алматы', 'Астана')]
    a = ', '.join(s[:2]) or city(x)
    for full, short in (('проспект', 'пр.'), ('улица', 'ул.'), (' ул.', '')):
        a = a.replace(full, short)
    return a.strip()


def card(x, base):
    progs = [p for p in x['programs'] if pname(p) and pname(p) not in SKIP_PROGS][:3]
    if len(progs) < 2:
        progs = [p for p in x['programs'] if pname(p) and pname(p) != 'Аренда сауны'][:3]
    feats = []
    if x['workHours'].get('roundclock'): feats.append('Круглосуточно')
    sv = x['services']
    if 'out_call' in sv: feats.append('Выезд')
    if 'kaspi_red' in sv: feats.append('Kaspi Red')
    elif 'card_payment' in sv: feats.append('Оплата картой')
    if 'installment' in sv and x['kind'] == 'salon': feats.append('Рассрочка')
    ph = x['slug'] + '.jpg'
    Image.open(img(x['images'][0]['url'])).convert('RGB').save(os.path.join(base, ph), quality=92)
    return {'type': 'master', 'photo': ph, 'city': city(x), 'kind': 'Салон' if x['kind'] == 'salon' else 'Мастер',
            'name': x['name'], 'addr': addr(x),
            'progs': [{'n': pname(p).replace('Body Massage - массаж тела', 'Массаж тела'), 'd': p.get('duration') or 60, 'p': p['price']} for p in progs],
            'feats': feats[:3]}


def build(slug, date, outdir, slugs):
    a = {x['slug']: x for x in listings()}
    base = os.path.join(outdir, 'spec'); os.makedirs(base, exist_ok=True)
    cards = [card(a[s], base) for s in slugs]
    cover = cards[0]['photo']
    cities = sorted({c['city'] for c in cards})
    slides = [{'type': 'cover', 'photo': cover, 'pos': 'center 25%', 'tag': 'Знакомство с мастерами',
               'title': 'Мастера недели\n*на PRO-BODY.KZ*', 'sub': ' и '.join(cities) + '. Программы и цены — из анкет на сайте.'}]
    slides += cards
    slides.append({'type': 'cta', 'title': 'Выбери\nсвоего мастера', 'body': 'Найди мастера по имени в поиске на сайте — там фото, все программы и контакты для записи.',
                   'btn': 'pro-body.kz', 'chips': ['Алматы', 'Астана', f'{len(a)} анкет онлайн']})
    sp = os.path.join(base, slug + '.json')
    json.dump({'slug': slug, 'slides': slides}, open(sp, 'w'), ensure_ascii=False, indent=1)
    subprocess.run(['python3', os.path.join(REPO, 'tools/carousels/render.py'), sp, outdir], check=True, stdout=subprocess.DEVNULL)
    names = '\n'.join(f"• {c['name']} — {c['city']}" for c in cards)
    caption = (f"Знакомство с мастерами PRO-BODY.KZ 👋\n\nНа этой неделе — {len(cards)} анкет из каталога:\n{names}\n\n"
               "Программы, цены и контакты — в анкетах на сайте. Найдите мастера по имени в поиске.\n\n"
               "👉 pro-body.kz — ссылка в шапке профиля\n\n#массажалматы #массажастана #спаалматы #массаж #probodykz")
    print(json.dumps({'date': date, 'slug': slug, 'listings': slugs, 'caption': caption,
                      'images': [f'{slug}-{i}.jpg' for i in range(1, len(slides) + 1)]}, ensure_ascii=False))


if __name__ == '__main__':
    if sys.argv[1] == 'candidates':
        candidates(sys.argv[2])
    else:
        build(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:])
