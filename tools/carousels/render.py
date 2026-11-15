"""Render Instagram carousel slides (1080x1350) from a JSON spec via Playwright.

usage: python3 render.py spec.json outdir
spec: {"slug":..., "tag":..., "slides":[{type, ...}]}
types: cover, text, list, steps, cta, typecover
"""
import json, sys, os, base64, html
import subprocess

W, H = 1080, 1350
CSS = """
*{margin:0;padding:0;box-sizing:border-box}
:root{--ink:#0d0e10;--ink2:#17191c;--paper:#f3f0ea;--y:#ffc83d;--mute:#9a9ea6}
html,body{width:1080px;height:1350px;overflow:hidden}
body{font-family:'Inter Display','Inter',sans-serif;background:var(--ink);color:var(--paper);-webkit-font-smoothing:antialiased}
.s{position:relative;width:1080px;height:1350px;overflow:hidden;padding:84px 84px 0}
.top{position:absolute;top:56px;left:84px;right:84px;display:flex;justify-content:space-between;align-items:center;font-weight:600;font-size:24px;letter-spacing:.14em;text-transform:uppercase;z-index:5}
.logo{font-weight:800;letter-spacing:.04em}
.logo b{color:var(--y)}
.cnt{color:var(--mute);font-variant-numeric:tabular-nums;letter-spacing:.08em}
.bot{position:absolute;bottom:56px;left:84px;right:84px;display:flex;justify-content:space-between;align-items:center;font-size:24px;font-weight:600;z-index:5}
.swipe{display:flex;align-items:center;gap:14px;padding:16px 26px;border:2px solid rgba(243,240,234,.35);border-radius:100px;letter-spacing:.04em}
.swipe i{font-style:normal;color:var(--y);font-size:30px;line-height:0}
.tag{display:inline-block;background:var(--y);color:var(--ink);font-weight:800;font-size:24px;letter-spacing:.12em;text-transform:uppercase;padding:12px 20px;border-radius:8px}
.bg{position:absolute;inset:0;background-size:cover;background-position:center}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(13,14,16,.92) 0%,rgba(13,14,16,.55) 34%,rgba(13,14,16,.05) 58%,rgba(13,14,16,.25) 78%,rgba(13,14,16,.9) 100%)}
.cover .wrap{position:absolute;top:150px;left:84px;right:84px;z-index:4}
.cover h1{font-weight:900;font-size:96px;line-height:1.0;letter-spacing:-.02em;margin-top:30px}
.cover h1 em{font-style:normal;color:var(--y)}
.cover p{text-shadow:0 2px 12px rgba(0,0,0,.8);font-size:34px;line-height:1.3;color:#d9d6cf;margin-top:26px;max-width:820px;font-weight:500}
.num{font-weight:900;font-size:250px;line-height:.8;letter-spacing:-.06em;color:var(--y)}
.text h2,.list h2,.steps h2{font-weight:800;font-size:80px;line-height:1.03;letter-spacing:-.02em;margin-top:40px}
.ghost{position:absolute;right:-40px;bottom:-120px;font-weight:900;font-size:760px;line-height:1;letter-spacing:-.06em;color:transparent;-webkit-text-stroke:3px rgba(255,200,61,.16);z-index:0}
.mid{z-index:3}
.bar{position:absolute;left:84px;right:84px;top:118px;height:4px;background:#24272b;border-radius:4px;z-index:5}.bar i{display:block;height:100%;background:var(--y);border-radius:4px}
.cta .bar{background:rgba(13,14,16,.15)}.cta .bar i{background:var(--ink)}
.text .body{font-size:42px;line-height:1.4;color:#cfccc5;margin-top:36px;font-weight:450}
.text .body b,.list li b,.steps b{color:var(--paper);font-weight:700}
.note{margin-top:44px;display:flex;gap:20px;align-items:flex-start;background:var(--ink2);border:1px solid #2a2d31;border-radius:22px;padding:30px 34px;font-size:31px;line-height:1.35;color:#d9d6cf}
.note .d{flex:none;width:14px;height:14px;border-radius:50%;background:var(--y);margin-top:13px}
.mid{position:absolute;top:150px;left:84px;right:84px;bottom:150px;display:flex;flex-direction:column;justify-content:center}
ul{list-style:none;margin-top:44px;display:flex;flex-direction:column;gap:20px}
.list li{display:flex;gap:26px;align-items:flex-start;font-size:35px;line-height:1.3;color:#cfccc5;background:var(--ink2);border:1px solid #2a2d31;border-radius:22px;padding:26px 30px}
.list li .k{flex:none;width:54px;height:54px;border-radius:14px;background:var(--y);color:var(--ink);font-weight:900;font-size:28px;display:flex;align-items:center;justify-content:center;margin-top:-4px}
.steps li{display:flex;gap:28px;align-items:baseline;font-size:36px;line-height:1.3;color:#cfccc5;padding:26px 0;border-top:2px solid #2a2d31}
.steps li:last-child{border-bottom:2px solid #2a2d31}
.steps li .k{flex:none;font-weight:900;font-size:40px;color:var(--y);width:70px}
.cta{background:var(--y);color:var(--ink)}
.cta .top .logo b{color:var(--ink)}
.cta .cnt{color:rgba(13,14,16,.55)}
.cta h2{font-weight:900;font-size:104px;line-height:1.0;letter-spacing:-.025em}
.cta .body{font-size:38px;line-height:1.35;margin-top:34px;font-weight:550;max-width:860px}
.cta .btn{margin-top:54px;display:inline-flex;align-items:center;gap:18px;background:var(--ink);color:var(--paper);font-weight:800;font-size:40px;padding:30px 44px;border-radius:100px}
.cta .btn i{font-style:normal;color:var(--y)}
.cta .chips{display:flex;gap:16px;margin-top:48px;flex-wrap:wrap}
.cta .chips span{border:2px solid rgba(13,14,16,.85);border-radius:100px;padding:14px 24px;font-size:28px;font-weight:700}
.cta .bot{color:rgba(13,14,16,.7)}
.typecover{background:radial-gradient(1200px 900px at 85% 0%,#2a2410 0%,var(--ink) 55%)}
.typecover .big{font-weight:900;font-size:520px;line-height:.78;letter-spacing:-.07em;color:var(--y);margin-top:40px}
.typecover h1{font-weight:900;font-size:100px;line-height:1.0;letter-spacing:-.02em;margin-top:40px}
.typecover h1 em{font-style:normal;color:var(--y)}
.typecover p{font-size:34px;line-height:1.3;color:#cfccc5;margin-top:28px;font-weight:500;max-width:820px}
.photoband{position:absolute;left:0;right:0;bottom:0;height:560px;background-size:cover;background-position:center 35%}
.photoband:after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,var(--ink) 0%,rgba(13,14,16,0) 35%,rgba(13,14,16,.15) 75%,rgba(13,14,16,.85) 100%)}
.master .mphoto{position:absolute;left:0;right:0;top:0;height:880px;background-size:cover;background-position:center 20%}
.master .mphoto:after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(13,14,16,.85) 0%,rgba(13,14,16,0) 22%,rgba(13,14,16,0) 60%,var(--ink) 100%)}
.master .info{position:absolute;left:84px;right:84px;top:640px;z-index:3}
.master .meta{display:flex;gap:14px;align-items:center}
.master .meta span{font-size:24px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;padding:10px 18px;border-radius:8px;background:rgba(13,14,16,.7);border:1px solid #3a3d42}
.master .meta span.y{background:var(--y);color:var(--ink);border-color:var(--y)}
.master h2{font-weight:900;font-size:104px;line-height:1;letter-spacing:-.025em;margin-top:22px}
.master .addr{font-size:28px;color:var(--mute);margin-top:12px;font-weight:500}
.master .progs{margin-top:28px;border-top:2px solid #2a2d31}
.master .progs div{display:flex;justify-content:space-between;align-items:baseline;font-size:33px;padding:16px 0;border-bottom:2px solid #2a2d31;color:#cfccc5}
.master .progs div b{color:var(--paper);font-weight:800;font-variant-numeric:tabular-nums}
.master .progs small{font-size:24px;color:var(--mute);margin-left:12px}
.master .feats{display:flex;flex-wrap:wrap;gap:12px;margin-top:24px}
.master .feats span{font-size:25px;font-weight:600;color:var(--y);border:2px solid rgba(255,200,61,.45);border-radius:100px;padding:10px 20px}
"""


def img_uri(path):
    with open(path, 'rb') as f:
        return 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode()


def e(t):
    # allow **bold** and *accent*
    t = html.escape(t)
    import re
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t, flags=re.S)
    t = re.sub(r'\*(.+?)\*', r'<em>\1</em>', t, flags=re.S)
    return t.replace('\n', '<br>')


def frame(inner, i, n, cls, swipe=True):
    top = f'<div class="top"><span class="logo">PRO<b>-</b>BODY<b>.</b>KZ</span><span class="cnt">{i:02d} / {n:02d}</span></div>'
    if i == n:
        bot = '<div class="bot"><span>Массаж и SPA · Алматы · Астана</span><span>@probodykz</span></div>'
    elif swipe:
        bot = '<div class="bot"><span style="color:var(--mute)">Сохрани, чтобы не потерять</span><span class="swipe">Листай <i>→</i></span></div>'
    else:
        bot = ''
    bar = f'<div class="bar"><i style="width:{i*100/n:.1f}%"></i></div>'
    return f'<div class="s {cls}">{inner}{top}{bar}{bot}</div>'


def slide_html(sl, i, n, base):
    t = sl['type']
    if t == 'cover':
        inner = (f'<div class="bg" style="background-image:url({img_uri(os.path.join(base, sl["photo"]))});background-position:{sl.get("pos","center")}"></div><div class="shade"></div>'
                 f'<div class="wrap"><span class="tag">{e(sl["tag"])}</span><h1>{e(sl["title"])}</h1>'
                 + (f'<p>{e(sl["sub"])}</p>' if sl.get('sub') else '') + '</div>')
        return frame(inner, i, n, 'cover')
    if t == 'typecover':
        inner = (f'<div class="mid"><span><span class="tag">{e(sl["tag"])}</span></span>'
                 f'<div class="big" style="font-size:{ {1:520,2:400,3:300}.get(len(sl["big"]),250) }px">{e(sl["big"])}</div><h1>{e(sl["title"])}</h1>'
                 + (f'<p>{e(sl["sub"])}</p>' if sl.get('sub') else '') + '</div>')
        return frame(inner, i, n, 'typecover')
    if t == 'text':
        band = ''
        if sl.get('photo'):
            band = f'<div class="photoband" style="background-image:url({img_uri(os.path.join(base, sl["photo"]))});background-position:{sl.get("pos","center 72%")}"></div>'
        note = f'<div class="note"><span class="d"></span><span>{e(sl["note"])}</span></div>' if sl.get('note') else ''
        ghost = f'<div class="ghost">{e(sl["num"])}</div>' if sl.get('num') and not sl.get('photo') else ''
        style = 'justify-content:flex-start;top:190px' if sl.get('photo') else ''
        inner = (band + ghost + f'<div class="mid" style="{style}">'
                 + (f'<div class="num">{e(sl["num"])}</div>' if sl.get('num') else '')
                 + f'<h2>{e(sl["title"])}</h2><div class="body">{e(sl["body"])}</div>{note}</div>')
        return frame(inner, i, n, 'text', swipe=not sl.get('photo'))
    if t in ('list', 'steps'):
        items = ''.join(
            f'<li><span class="k">{e(it.get("k", str(j+1)))}</span><span>{e(it["t"])}</span></li>' for j, it in enumerate(sl['items']))
        inner = (f'<div class="mid">' + (f'<span><span class="tag">{e(sl["tag"])}</span></span>' if sl.get('tag') else '')
                 + f'<h2>{e(sl["title"])}</h2><ul>{items}</ul></div>')
        return frame(inner, i, n, t)
    if t == 'cta':
        chips = ''.join(f'<span>{e(c)}</span>' for c in sl.get('chips', []))
        mx = max(len(x) for x in sl["title"].split("\n"))
        fs = 104 if mx <= 14 else (90 if mx <= 16 else 78)
        inner = (f'<div class="mid"><h2 style="font-size:{fs}px">{e(sl["title"])}</h2><div class="body">{e(sl["body"])}</div>'
                 f'<div><span class="btn">{e(sl.get("btn","pro-body.kz"))} <i>→</i></span></div>'
                 + (f'<div class="chips">{chips}</div>' if chips else '') + '</div>')
        return frame(inner, i, n, 'cta')
    if t == 'master':
        progs = ''.join(f'<div><span>{e(p["n"])}<small>{p["d"]} мин</small></span><b>{p["p"]:,} ₸</b></div>'.replace(',', ' ') for p in sl['progs'])
        feats = ''.join(f'<span>{e(f)}</span>' for f in sl.get('feats', []))
        inner = (f'<div class="mphoto" style="background-image:url({img_uri(os.path.join(base, sl["photo"]))});background-position:{sl.get("pos","center 20%")}"></div>'
                 f'<div class="info"><div class="meta"><span class="y">{e(sl["city"])}</span><span>{e(sl["kind"])}</span></div>'
                 f'<h2>{e(sl["name"])}</h2><div class="addr">{e(sl["addr"])}</div><div class="progs">{progs}</div><div class="feats">{feats}</div></div>')
        return frame(inner, i, n, 'master')
    raise ValueError(t)


def render(spec_path, outdir):
    spec = json.load(open(spec_path))
    base = os.path.dirname(os.path.abspath(spec_path))
    outdir = os.path.abspath(outdir); os.makedirs(outdir, exist_ok=True)
    n = len(spec['slides'])
    files = []
    jobs = []
    for i, sl in enumerate(spec['slides'], 1):
        doc = f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{slide_html(sl, i, n, base)}</body></html>'
        hp = os.path.join(outdir, f'{spec["slug"]}-{i}.html')
        open(hp, 'w').write(doc)
        jobs.append(hp)
    subprocess.run(['node', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shot.js')] + jobs, check=True)
    from PIL import Image
    for hp in jobs:
        png = hp[:-5] + '.png'; jpg = hp[:-5] + '.jpg'
        Image.open(png).convert('RGB').save(jpg, quality=92, optimize=True)
        os.remove(png); os.remove(hp)
        files.append(jpg)
    return files


if __name__ == '__main__':
    for f in render(sys.argv[1], sys.argv[2]):
        print(f)
