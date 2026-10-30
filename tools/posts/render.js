// node render.js spec.json outdir — single posts 1620x2025 in the yellow/white style of images/01–21
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const [spec,out]=process.argv.slice(2);const posts=JSON.parse(fs.readFileSync(spec,'utf8'));
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
const css=`*{margin:0;padding:0;box-sizing:border-box}
body{width:1620px;height:2025px;overflow:hidden;background:#ffc83d;font-family:'Inter Display','Inter',sans-serif;color:#1d1d1b;position:relative}
.c{position:absolute;left:-330px;right:-330px;top:110px;height:1810px;border-radius:50%;background:#fff}
.w{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;padding-top:300px}
h1{font-weight:600;font-size:132px;letter-spacing:-.01em;line-height:1.05;text-align:center}
.pill{margin-top:34px;background:#ffc83d;border-radius:200px;padding:30px 70px 40px;font-weight:600;font-size:118px;line-height:1.05;letter-spacing:-.01em;box-shadow:0 18px 40px rgba(255,170,0,.28),inset 0 -6px 0 rgba(0,0,0,.05);text-align:center;max-width:1420px}
.pill.s{font-size:92px}
ul{list-style:none;margin-top:110px;width:1150px;display:flex;flex-direction:column;gap:30px}
li{display:flex;align-items:center;gap:36px;background:#f6f6f6;border-radius:44px;padding:30px 44px;font-size:52px;font-weight:500;box-shadow:0 12px 30px rgba(0,0,0,.06)}
li span{flex:none;width:104px;height:104px;border-radius:50%;background:#fff3cf;display:flex;align-items:center;justify-content:center;font-size:58px}
.b{position:absolute;width:170px;height:170px;border-radius:50%;background:#fff3cf;border:8px solid #ffe08a;display:flex;align-items:center;justify-content:center;font-size:84px;box-shadow:0 14px 34px rgba(255,170,0,.25)}
.b1{right:120px;top:120px}.b2{left:130px;top:1720px}
.logo{position:absolute;bottom:80px;width:100%;text-align:center;font-weight:800;font-size:52px;letter-spacing:.04em}`;
(async()=>{const b=await chromium.launch();const pg=await b.newPage({viewport:{width:1620,height:2025}});
for(const p of posts){const pill=p.pill.length>16?'pill s':'pill';
const html=`<html><head><style>${css}</style></head><body><div class="c"></div><div class="w"><h1 style="font-size:${p.h1.length>13?112:132}px">${esc(p.h1)}</h1><div class="${pill}">${esc(p.pill)}</div><ul>${p.items.map(([e,t])=>`<li><span>${e}</span>${esc(t)}</li>`).join('')}</ul></div><div class="b b1">${p.badges[0]}</div><div class="b b2">${p.badges[1]}</div><div class="logo">PRO-BODY.KZ</div></body></html>`;
await pg.setContent(html);await pg.waitForTimeout(300);await pg.screenshot({path:path.join(out,p.image),type:'jpeg',quality:92});console.log(p.image)}
await b.close()})();
