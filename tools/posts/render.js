// node render.js spec.json outdir — single posts 1620x2025 (4:5), dark/light editorial style
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const [spec,out]=process.argv.slice(2);const posts=JSON.parse(fs.readFileSync(spec,'utf8'));
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
const css=`*{margin:0;padding:0;box-sizing:border-box}
:root{--y:#ffc83d}
.dark{--bg:#0d0e10;--fg:#f3f0ea;--mute:#9a9ea6;--card:#17191c;--line:#2a2d31;--kfg:#ffc83d}
.light{--bg:#f3f0ea;--fg:#0d0e10;--mute:#6b6f76;--card:#ffffff;--line:#e3ded4;--kfg:#0d0e10}
html,body{width:1080px;height:1350px;overflow:hidden}
body{font-family:'Inter Display','Inter',sans-serif;background:var(--bg);color:var(--fg);-webkit-font-smoothing:antialiased;position:relative;padding:0 80px}
.ph{position:absolute;left:0;right:0;top:0;height:520px;background-size:cover;background-position:center}
.ph:after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.45) 0%,rgba(0,0,0,0) 30%,rgba(0,0,0,0) 55%,var(--bg) 100%)}
.top,.kick,h1,ul{position:relative;z-index:2}
.top{padding-top:60px;color:#fff;display:flex;justify-content:space-between;align-items:center;font-weight:800;font-size:24px;letter-spacing:.06em}
.top b{color:var(--y)}
.tag{font-size:21px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;border-radius:100px;padding:11px 20px;background:var(--y);color:#0d0e10}
.kick{margin-top:296px;font-size:24px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--mute);display:flex;align-items:center;gap:16px}
.light .kick{color:var(--fg)}
.kick:before{content:'';width:44px;height:4px;background:var(--y);border-radius:4px}
h1{margin-top:18px;font-weight:900;font-size:72px;line-height:1.02;letter-spacing:-.03em}
h1.s{font-size:62px}
.dark h1 em{font-style:normal;color:var(--y)}
.light h1 em{font-style:normal;background:linear-gradient(transparent 58%,var(--y) 58%,var(--y) 92%,transparent 92%)}
ul{list-style:none;margin-top:28px;display:flex;flex-direction:column;gap:10px}
li{display:flex;gap:26px;align-items:center;background:var(--card);border:1px solid var(--line);border-radius:26px;padding:14px 26px}
.light li{box-shadow:0 6px 20px rgba(13,14,16,.05)}
li .k{flex:none;min-width:60px;height:60px;padding:0 14px;border-radius:18px;background:var(--y);color:#0d0e10;font-weight:900;font-size:26px;display:flex;align-items:center;justify-content:center;letter-spacing:-.01em}
li .k.n{font-size:30px}
li .t{font-weight:800;font-size:30px;line-height:1.15;letter-spacing:-.01em}
li .d{margin-top:4px;font-size:23px;line-height:1.3;color:var(--mute);font-weight:500}
ul.c6{gap:9px}ul.c6 li{padding:11px 24px}ul.c6 li .k{height:50px;min-width:50px}ul.c6 li .t{font-size:28px}ul.c6 li .d{font-size:21px;margin-top:2px}
.bot{position:absolute;left:80px;right:80px;bottom:48px;display:flex;justify-content:space-between;align-items:center;font-size:24px;font-weight:700}
.save{display:flex;align-items:center;gap:12px;background:var(--y);color:#0d0e10;border-radius:100px;padding:14px 26px}
.save svg{width:24px;height:24px}
.url{color:var(--mute);letter-spacing:.04em}`;
const save='<svg viewBox="0 0 24 24" fill="none" stroke="#0d0e10" stroke-width="2.6" stroke-linejoin="round"><path d="M6 3h12v18l-6-4-6 4z"/></svg>';
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:1.5});
for(const p of posts){
const items=p.items.map(([k,t,d])=>`<li><div class="k${/^\d+$|^[✓★]$/.test(k)?' n':''}">${esc(k)}</div><div><div class="t">${esc(t)}</div><div class="d">${esc(d)}</div></div></li>`).join('');
const hlen=p.h.replace(/<[^>]+>/g,'').length;
const html=`<html><head><style>${css}</style></head><body class="${p.theme}"><div class="ph" style="background-image:url('data:image/jpeg;base64,${fs.readFileSync(path.join(path.dirname(spec),'photos',p.image.slice(0,2)+'.jpg')).toString('base64')}');background-position:${p.pos||'center'}"></div><div class="top"><div>PRO-<b>BODY</b>.KZ</div><div class="tag">${esc(p.tag)}</div></div>
<div class="kick">${esc(p.kicker)}</div><h1 class="${hlen>36?'s':''}">${p.h}</h1><ul class="${p.items.length>5?'c6':''}">${items}</ul>
<div class="bot"><div class="save">${save}Сохрани, пригодится</div><div class="url">pro-body.kz</div></div></body></html>`;
await pg.setContent(html);await pg.waitForTimeout(250);await pg.screenshot({path:path.join(out,p.image),type:'jpeg',quality:92});console.log(p.image)}
await b.close()})();
