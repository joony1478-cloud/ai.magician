"""send/아티팩트에 있던 주문서 6편을 사이트 디자인(scrolls/claude-x-gpt 기준)으로 다시 만든다.

python _build/build_scrolls.py          # 6편 index.html + cover.png + 파비콘 생성
python _build/build_scrolls.py --cta    # (위 포함) 기존 2편에 CTA 버튼·파비콘만 끼워넣기
_build 폴더는 밑줄로 시작해서 GitHub Pages에 공개되지 않는다.
"""
import html, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://joony1478-cloud.github.io/ai.magician/"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
e = html.escape

# ---------------- 픽셀 마법사 (기존 커버에서 30px 칸 단위로 읽어낸 지도) ----------------
WIZ = """......AA.........
.....ADDA........
....ADDDA........
....ADDDDA.......
...ADDADDA.......
...ADDDDDDA......
..ADDDDADDA......
.ADDDDDDDDDA.....
AAAAAAAAAAAAAA...
..AEEEEEEEEA.....
..AEAEEEEAEA.....
..AEEEEEEEEA.....
..ACCEEEECCA.....
...ACCCCCCA......
.AAACCCCCCAAA....
AAAAACCCCAAAAAB..
AAAAAACCAAAAAABD.
AAAAAAAAAAAAAAB..
.AAAAAAAAAAAA.B..
..AA......AA..B..""".split("\n")
PAL = {"A": "#1f1f1f", "B": "#8a6a45", "C": "#e4e1d8", "D": "#f2e15b", "E": "#f3d2b3"}

def wizard_svg(px=30):
    rects = "".join(f'<rect x="{x*px}" y="{y*px}" width="{px}" height="{px}" fill="{PAL[c]}"/>'
                    for y, row in enumerate(WIZ) for x, c in enumerate(row) if c in PAL)
    w, h = len(WIZ[0]) * px, len(WIZ) * px
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" shape-rendering="crispEdges">{rects}</svg>'

def favicon_svg():
    # 마법사 얼굴+모자만 (위 14줄), 정사각 칸에 맞춤
    rows = WIZ[:14]
    rects = "".join(f'<rect x="{x}" y="{y+1}" width="1" height="1" fill="{PAL[c]}"/>'
                    for y, row in enumerate(rows) for x, c in enumerate(row) if c in PAL)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1 0 16 16" shape-rendering="crispEdges">'
            '<rect x="-1" width="16" height="16" rx="3" fill="#f7f5ef"/>' + rects + '</svg>')

FONTS = """@font-face{font-family:Paperlogy;font-weight:400;font-display:swap;src:url(https://cdn.jsdelivr.net/gh/fonts-archive/Paperlogy/Paperlogy-4Regular.woff2) format("woff2")}
@font-face{font-family:Paperlogy;font-weight:600;font-display:swap;src:url(https://cdn.jsdelivr.net/gh/fonts-archive/Paperlogy/Paperlogy-6SemiBold.woff2) format("woff2")}
@font-face{font-family:Paperlogy;font-weight:800;font-display:swap;src:url(https://cdn.jsdelivr.net/gh/fonts-archive/Paperlogy/Paperlogy-8ExtraBold.woff2) format("woff2")}"""

def cover_html(t1, t2, tiles):
    tl = "".join(f'<span class="t" style="background:{c}">{e(s)}</span>' for s, c in tiles)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1600px;height:1000px;overflow:hidden}}
body{{font-family:Paperlogy,sans-serif;color:#1f1f1f;position:relative;
 background:linear-gradient(rgba(31,31,31,.06) 1px,transparent 1px) 0 0/44px 44px,linear-gradient(90deg,rgba(31,31,31,.06) 1px,transparent 1px) 0 0/44px 44px,#f7f5ef}}
.wiz{{position:absolute;left:170px;top:200px}}
.r{{position:absolute;left:740px;top:282px;width:820px}}
.k{{display:inline-block;background:#f2e15b;font-weight:800;font-size:30px;padding:6px 16px}}
h1{{margin-top:34px;font-weight:800;font-size:92px;line-height:1.14;letter-spacing:-.04em}}
.ts{{margin-top:44px;display:flex;flex-wrap:wrap;gap:22px}}
.t{{font-weight:800;font-size:36px;padding:16px 26px;border:4px solid #1f1f1f;box-shadow:10px 10px 0 #1f1f1f;color:#1f1f1f}}
</style></head><body><div class="wiz">{wizard_svg()}</div>
<div class="r"><span class="k">ai 술사 무료 자료</span><h1>{e(t1)}<br>{e(t2)}</h1><div class="ts">{tl}</div></div></body></html>"""

def render(html_text, out, w, h):
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html_text); src = f.name
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--window-size={w},{h}", "--virtual-time-budget=6000", f"--screenshot={out}", Path(src).as_uri()],
                   check=True, capture_output=True)
    Path(src).unlink()

# ---------------- 페이지 공통 틀 ----------------
CSS = FONTS + """
:root{--paper:#f7f5ef;--card:#fff;--ink:#1f1f1f;--sub:#5f5e5a;--dim:#8e8d88;--line:#dcd9cf;--box:#efede6;--stamp:#f2e15b;--grid:rgba(31,31,31,.045)}
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
html{background:var(--paper);-webkit-text-size-adjust:100%}
body{font-family:Paperlogy,-apple-system,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;color:var(--ink);line-height:1.6;word-break:keep-all;overflow-wrap:anywhere;
  background:linear-gradient(var(--grid) 1px,transparent 1px) 0 0/22px 22px,linear-gradient(90deg,var(--grid) 1px,transparent 1px) 0 0/22px 22px,var(--paper)}
::selection{background:var(--stamp)}
:focus-visible{outline:2px solid var(--ink);outline-offset:2px}
a{color:var(--ink);text-underline-offset:3px}
main{max-width:520px;margin:0 auto;padding:16px 16px calc(56px + env(safe-area-inset-bottom))}
.cover{display:block;width:100%;height:auto;aspect-ratio:16/10;border:1px solid var(--ink)}
.hi{margin-top:28px;font-size:16px;color:var(--sub)}
h1{margin-top:6px;font-weight:800;font-size:clamp(28px,8vw,36px);line-height:1.3;letter-spacing:-.03em}
h1 em{font-style:normal;background:linear-gradient(transparent 58%,var(--stamp) 58%)}
.lead{margin-top:16px;font-size:17px;color:var(--sub)}
.lead b{color:var(--ink);font-weight:600}
h2{margin:44px 0 12px;font-weight:800;font-size:22px;letter-spacing:-.02em}
h2+p{font-size:16px;color:var(--sub);margin-bottom:12px}
ol.prep{list-style:none;display:grid;gap:8px}
ol.prep li{display:flex;gap:12px;align-items:baseline;padding:14px 16px;background:var(--card);border:1px solid var(--line);font-size:16px}
ol.prep li small{display:block;color:var(--sub);font-size:14px}
.n{flex:none;display:inline-grid;place-items:center;width:24px;height:24px;font-weight:800;font-size:13px;background:var(--ink);color:#fff;transform:translateY(-1px)}
.step{margin-top:20px;padding:22px 18px 18px;background:var(--card);border:1px solid var(--ink)}
.badge{display:inline-flex;align-items:center;gap:8px;font-weight:800;font-size:13px;letter-spacing:.04em;padding:4px 10px;background:var(--stamp)}
.badge i{width:10px;height:10px;display:inline-block;border:1.5px solid var(--ink)}
.step h3{margin-top:12px;font-weight:800;font-size:22px;line-height:1.35;letter-spacing:-.02em}
.step h3 small{display:block;font-size:14px;font-weight:600;color:var(--dim);letter-spacing:0}
.step .sub{margin-top:4px;font-size:16px;color:var(--sub)}
.step>p{margin-top:8px;font-size:16px}
.shot{display:block;width:100%;height:auto;margin-top:14px;border:1px solid var(--line)}
ol.do{list-style:none;margin-top:16px;display:grid;gap:10px}
ol.do li{display:flex;gap:10px;align-items:baseline;font-size:16px}
.lbl{margin-top:16px;font-weight:800;font-size:14px;color:var(--dim)}
.copy{position:relative;margin-top:10px;background:var(--box);border:1px solid var(--line)}
.copy pre{margin:0;padding:14px 14px 50px;font-family:ui-monospace,Consolas,"D2Coding",monospace;font-size:13.5px;line-height:1.65;white-space:pre-wrap;word-break:break-all}
.copy pre.ko{font-family:inherit;font-size:15px;word-break:keep-all;overflow-wrap:anywhere}
.copy button{position:absolute;right:8px;bottom:8px;appearance:none;border:1px solid var(--ink);background:#fff;font:800 13px Paperlogy,sans-serif;color:var(--ink);min-height:36px;padding:0 14px;cursor:pointer}
.copy button.ok{background:var(--stamp)}
.copy.line{display:flex;align-items:center}
.copy.line pre{flex:1;min-width:0;padding:12px 10px 12px 14px;word-break:normal;overflow-wrap:anywhere}
.copy.line button{position:static;flex:none;margin:6px}
.k{font-family:Paperlogy,sans-serif;font-weight:600}
.done{margin-top:16px;padding-top:12px;border-top:1px dashed var(--line);font-size:16px;font-weight:600}
.done::before{content:"✓ ";font-weight:800}
.tip{margin-top:12px;font-size:14px;color:var(--dim)}
code{font-family:ui-monospace,Consolas,monospace;font-size:.9em;background:var(--box);padding:1px 5px}
ul.chk{list-style:none;display:grid;gap:8px}
ul.chk li{display:flex;align-items:baseline;gap:10px;padding:12px 14px;background:var(--card);border:1px solid var(--line);font-size:16px}
ul.chk li::before{content:"✓";flex:none;display:inline-grid;place-items:center;width:22px;height:22px;font-weight:800;font-size:13px;background:var(--stamp)}
ul.warn{list-style:none;display:grid;gap:8px}
ul.warn li{padding:12px 14px;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--ink);font-size:16px}
table.num{width:100%;margin-top:12px;border-collapse:collapse;font-size:15px}
table.num td{padding:9px 0;border-bottom:1px dashed var(--line)}
table.num td:last-child{text-align:right;font-weight:800;white-space:nowrap}
.src{margin-top:28px;font-size:14px;color:var(--dim)}
.bye{margin-top:32px;font-size:17px}
.sign{margin-top:20px;font-weight:800;font-size:16px}
.cta{display:flex;align-items:center;justify-content:center;gap:8px;margin-top:28px;min-height:56px;padding:0 20px;background:var(--stamp);border:2px solid var(--ink);
  box-shadow:5px 5px 0 var(--ink);color:var(--ink);font-weight:800;font-size:17px;text-decoration:none;transition:transform .15s,box-shadow .15s}
.cta:hover{transform:translate(-1px,-1px);box-shadow:6px 6px 0 var(--ink)}
.cta:active{transform:translate(3px,3px);box-shadow:2px 2px 0 var(--ink)}
/* 비밀코드 100 */
.pills{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px;position:sticky;top:0;z-index:2;padding:10px 0;background:var(--paper)}
.pills button{appearance:none;border:1px solid var(--ink);background:#fff;font:600 14px Paperlogy,sans-serif;color:var(--ink);min-height:36px;padding:0 12px;cursor:pointer}
.pills button[aria-pressed=true]{background:var(--ink);color:#fff}
.cat h3{margin-top:30px;font-weight:800;font-size:20px}
.cat>p{font-size:15px;color:var(--sub)}
.code{display:block;width:100%;text-align:left;margin-top:8px;padding:14px 14px 12px;background:var(--card);border:1px solid var(--line);font:inherit;color:inherit;cursor:pointer}
.code:hover{border-color:var(--ink)}
.code .top{display:flex;align-items:baseline;gap:8px}
.code b{font-family:ui-monospace,Consolas,monospace;font-size:15px}
.code .w{font-size:13px;color:var(--dim);flex:1}
.code .c{font-weight:800;font-size:13px;border:1px solid var(--ink);padding:2px 8px}
.code.ok .c{background:var(--stamp)}
.code p{margin-top:6px;font-size:15px;color:var(--sub)}
"""

COPY_JS = """document.querySelectorAll('.copy button').forEach(function(b){
  b.addEventListener('click',function(){cp(b.parentNode.querySelector('pre').textContent,function(r){
    b.textContent=r?'복사됨 ✓':'길게 눌러 복사';b.classList.toggle('ok',r);setTimeout(function(){b.textContent='복사';b.classList.remove('ok')},1600)})});
});
function cp(t,cb){function fb(){var a=document.createElement('textarea');a.value=t;a.setAttribute('readonly','');a.style.cssText='position:fixed;top:0;opacity:0';document.body.appendChild(a);a.select();
  var r=false;try{r=document.execCommand('copy')}catch(e){}document.body.removeChild(a);cb(r)}
  if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(t).then(function(){cb(true)},fb)}else fb();}"""

HEAD_EXTRA = ('<link rel="icon" href="../../favicon.svg" type="image/svg+xml">\n'
              '<link rel="icon" href="../../favicon.png" type="image/png">\n'
              '<link rel="apple-touch-icon" href="../../apple-touch-icon.png">')
CTA = f'<a class="cta" href="../../">ai술사의 모든 꿀팁 확인하기!</a>'

def page(slug, title, desc, cover_alt, h1a, h1b, body, js=""):
    url = f"{SITE}scrolls/{slug}/"
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{url}cover.png">
{HEAD_EXTRA}
<style>{CSS}</style>
</head>
<body>
<main>
<img class="cover" src="cover.png" alt="{e(cover_alt)}">

<p class="hi">안녕하세요 ai 술사 성준입니다.</p>
<h1>{h1a}<br><em>{h1b}</em></h1>
{body}

<p class="bye">궁금하신 점은 DM으로 편하게 물어봐 주세요 🪄</p>
<p class="sign">From. ai 술사 | 성준</p>
{CTA}
</main>
<script>
{COPY_JS}
{js}
</script>
</body>
</html>
"""

# ---------------- 본문 조각 ----------------
def line(cmd): return f'<div class="copy line"><pre>{e(cmd)}</pre><button type="button">복사</button></div>'
def block(t, ko=True): return f'<div class="copy"><pre{" class=\"ko\"" if ko else ""}>{e(t)}</pre><button type="button">복사</button></div>'
def do(items, start=1): return '<ol class="do">' + "".join(f'<li><span class="n">{i}</span><span>{t}</span></li>' for i, t in enumerate(items, start)) + "</ol>"
def done(t): return f'<p class="done">{t}</p>'
def tip(t): return f'<p class="tip">{t}</p>'
def lbl(t): return f'<p class="lbl">{t}</p>'
def shot(src, alt): return f'<img class="shot" src="{src}" alt="{e(alt)}" loading="lazy">'
def prep(items): return '<h2>준비물</h2><ol class="prep">' + "".join(f'<li><span class="n">{i}</span><span>{t}</span></li>' for i, t in enumerate(items, 1)) + "</ol>"
def step(badge, title, sub, inner, small=""):
    s = f"<small>{small}</small>" if small else ""
    return f'<section class="step"><span class="badge">{badge}</span><h3>{s}{title}</h3>{f"<p class=sub>{sub}</p>" if sub else ""}{inner}</section>'
def chk(items): return '<ul class="chk">' + "".join(f"<li><span>{t}</span></li>" for t in items) + "</ul>"
def warn(items): return '<ul class="warn">' + "".join(f"<li>{t}</li>" for t in items) + "</ul>"

PAGES = []

# 1. 챗GPT 비밀코드 100개 ------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent))
from codes100 import CATS, D  # 원본 send 페이지 데이터 그대로
lib = []
for ci, (cn, cd) in enumerate(CATS):
    rows = "".join(f'<button type="button" class="code" data-t="{e(p)}"><span class="top"><b>{e(c)}</b><span class="w">{e(w)}</span><span class="c">복사</span></span><p>{e(p)}</p></button>'
                   for k, c, w, p in D if k == ci)
    lib.append(f'<section class="cat" data-c="{ci}"><h3>{e(cn)}</h3><p>{e(cd)}</p>{rows}</section>')
pills = '<button type="button" aria-pressed="true" data-c="-1">전체</button>' + "".join(f'<button type="button" aria-pressed="false" data-c="{i}">{e(c[0])}</button>' for i, c in enumerate(CATS))
PAGES.append(dict(
    slug="gpt-100", title="바로 써먹는 챗GPT 비밀코드 100개", desc="질문 끝에 붙이기만 하면 답이 달라지는 프롬프트 코드 100개",
    cover=("챗GPT 비밀코드", "100개", [("/TLDR", "#19c39a"), ("/human", "#f2e15b"), ("/CRITIQUE", "#fff")]),
    h1=("코드 하나만 붙이면", "챗GPT 답이 달라집니다"),
    body=f"""<p class="lead">릴스에서 소개한 비밀코드 100개를 상황별로 정리했어요.<br><b>카드를 누르면 바로 복사</b>돼요.</p>
<h2>사용법은 딱 3가지</h2><p>코드는 GPT에 원래 있는 명령어가 아니라, 내가 정해 쓰는 단축키예요.</p>
{step("방법 1", "질문 끝에 붙이기", "등록 없이 바로 돼요. 가장 쉬워요.", do(["아래 카드를 눌러 복사해요.", "내 질문 끝에 붙여넣고 보내요."]))}
{step("방법 2", "대화 첫머리에 한 번 등록", "그 대화 안에서는 코드만 써도 알아들어요.", block('앞으로 내가 /TLDR 이라고 쓰면 "위 글의 핵심만 3줄로 요약해줘"라는 뜻이야.'))}
{step("방법 3", "맞춤형 지침에 저장", "모든 대화에서 쓰고 싶을 때요.", do(["자주 쓰는 5~10개만 골라요.", "ChatGPT 설정 「맞춤형 지침」에 방법 2처럼 적어요."]) + tip("글자 수 제한 때문에 100개를 다 넣을 순 없어요."))}
{tip("코드는 이어 붙여도 돼요. /CRITIQUE로 약점 찾고 → /human으로 말투 다듬기.")}
<h2 id="lib">비밀코드 100개</h2>
<div class="pills" id="pills">{pills}</div>
{''.join(lib)}
<p class="bye">코드 써보시고 AI 활용 레벨을 올려보세요!</p>
{tip("2026년 10월 기준이에요. 프롬프트의 [대괄호] 부분은 내 상황에 맞게 바꿔 쓰세요.")}""",
    js="""document.querySelectorAll('.code').forEach(function(b){b.addEventListener('click',function(){cp(b.dataset.t,function(r){
  var c=b.querySelector('.c');c.textContent=r?'복사됨 ✓':'길게 눌러 복사';b.classList.toggle('ok',r);setTimeout(function(){c.textContent='복사';b.classList.remove('ok')},1600)})})});
var ps=document.querySelectorAll('#pills button');ps.forEach(function(p){p.addEventListener('click',function(){
  ps.forEach(function(x){x.setAttribute('aria-pressed',String(x===p))});var c=p.dataset.c;
  document.querySelectorAll('.cat').forEach(function(s){s.hidden=c!=='-1'&&s.dataset.c!==c});})});"""))

# 2. AI 티 나는 글 --------------------------------------------------------------
PROMPT_HEAD_MINE = "너는 내 글쓰기 대필 담당이야.\n이 프로젝트에 올려둔 글은 전부 내가 직접 쓴 글이야."
PROMPT_HEAD_AUTHOR = "너는 글쓰기 대필 담당이야.\n이 프로젝트에 올려둔 글은 내가 닮고 싶은 [작가/크리에이터 이름]의 글이야.\n이 글의 문체를 분석해서 그 느낌으로 써줘. 문장을 그대로 가져오지는 마."
PROMPT_BODY = """[1단계: 내 말투 분석]
처음 한 번만, 올려둔 글을 읽고 아래 항목을 분석해서
"내 말투 규칙표"로 정리해줘.
1. 문장 길이 (짧게 끊는지, 길게 이어 쓰는지)
2. 문장 끝맺음 (~해요 / ~합니다 / ~거든요 / 반말 비율)
3. 자주 쓰는 표현과 말버릇
4. 자주 쓰는 접속사와 문장 시작 단어, 쓰지 않는 것
5. 줄바꿈과 문단 나누기 방식
6. 이모지, 물음표, 느낌표, ㅋㅋ 같은 기호 사용 습관
7. 내가 쓰지 않는 표현 (AI 같은 표현, 번역투 등)
분석 결과를 보여주고, 내가 "맞아"라고 하면
그 규칙을 앞으로의 기준으로 삼아.

[2단계: 글쓰기]
내가 주제를 주면 규칙표대로 써줘.
- 내가 준 사실만 쓰고, 없는 사실이나 숫자는 지어내지 마.
- 모르는 건 [확인 필요]라고 표시해.
- 불필요한 인사말, 마무리 멘트, 설명은 붙이지 마.

[3단계: 스스로 검수]
쓴 글을 보여주기 전에 아래를 확인하고,
하나라도 어기면 고쳐서 다시 확인해.
□ 규칙표의 문장 길이와 끝맺음에 맞나
□ 내가 쓰지 않는 표현이 들어가 있나
□ 번역투(~를 통해, ~에 대한, ~할 수 있습니다,
  ~것으로 보입니다)가 있나
□ 같은 문장 구조가 3번 이상 반복되나
□ 지어낸 사실이 있나
최종 글만 출력해줘. 검수 과정은 보여주지 마."""
PAGES.append(dict(
    slug="writing", title="AI 티 나는 글, 자연스럽게 바꾸는 법", desc="번역투 잡는 스킬 + 내 말투를 학습시키는 복붙 프롬프트",
    cover=("AI 티 나는 글,", "자연스럽게", [("번역투 ✗", "#fff"), ("내 말투 ✓", "#f2e15b")]),
    h1=("AI 티 나는 글,", "자연스럽게 바꾸는 법"),
    body=f"""<p class="lead">"자연스럽게 써줘", "사람이 쓴 것처럼 써줘"<br>라고 해도 똑같이 어색하지 않으셨나요?</p>
<h2>이유는 두 가지예요</h2>
<ol class="prep"><li><span class="n">1</span><span>한국어에 영어 번역투가 남아서<small>단어는 한국어인데 문장 구조가 영어를 옮긴 것 같아요.</small></span></li>
<li><span class="n">2</span><span>AI가 내 말투를 본 적이 없어서<small>"자연스럽게"라고 해도 AI가 받는 건 사실상 주제뿐이에요.</small></span></li></ol>
{prep(["Claude Code (1단계용 · 건너뛰어도 돼요)", "프로젝트 기능이 있는 클로드 또는 ChatGPT (2~3단계)"])}
{tip("클로드 코드가 없어도 STEP 2~3만 해도 효과가 있어요.")}
{step("STEP 1", "번역투 잡는 스킬 설치", "한글 AI 글의 티를 줄여주는 im-not-ai 스킬이에요. 건너뛰어도 돼요.",
  do(["Claude Code에 두 줄을 차례로 입력해요."]) + line("/plugin marketplace add epoko77-ai/im-not-ai") + line("/plugin install humanize-korean@im-not-ai")
  + do(["새 세션을 열고 입력한 뒤, 고칠 글을 붙여넣어요."], 2) + line("/humanize-korean") + lbl("또는 말로 시켜도 돼요") + block("이 글 AI 티 없애줘")
  + done("‘AI 기술을 통해 효율을 높일 수 있다’ → ‘AI로 효율을 높인다’")
  + tip('내용(사실·인용)은 그대로, 문체와 리듬만 바꿔요. 출처 · <a href="https://github.com/epoko77-ai/im-not-ai" target="_blank" rel="noopener">github.com/epoko77-ai/im-not-ai</a>'))}
{step("STEP 2", "샘플 글 3~5개 모으기", "AI가 말투를 배울 재료예요.",
  do(["내가 직접 쓴 글로 골라요. (AI 글이 섞이면 말투가 흐려져요)", "쓰려는 글과 같은 종류로 골라요. (캡션이면 캡션)", "글마다 파일 하나로 저장해요. (예: 인스타캡션_01.txt)", "제목·해시태그·광고 문구는 빼고 본문만 남겨요."])
  + tip("좋아하는 작가·크리에이터 글을 넣어도 돼요. 그 사람 문체로 써줘요."))}
{step("STEP 3", "프로젝트에 넣고 말투 학습", "한 번만 세팅하면 계속 써요.",
  do(["클로드 또는 ChatGPT에서 프로젝트를 새로 만들어요.", "STEP 2 파일들을 프로젝트 파일(지식)에 추가해요.", "아래 프롬프트를 프로젝트 지침(Instructions)에 붙여넣어요."])
  + lbl("내 글을 넣었다면") + block(PROMPT_HEAD_MINE + "\n\n" + PROMPT_BODY)
  + lbl("작가·크리에이터 글을 넣었다면 (이름만 바꿔서)") + block(PROMPT_HEAD_AUTHOR + "\n\n" + PROMPT_BODY)
  + tip("화면 이름과 위치는 업데이트로 바뀔 수 있어요. 안 보이면 ‘프로젝트 → 파일 / 지침’ 메뉴를 찾아주세요."))}
{step("STEP 4", "결과 확인하고 고치기", "아무 주제나 하나 시켜보세요.",
  block("[주제]에 대한 글을 써줘. 분량은 [ ]자 정도로.") + lbl("마음에 안 들면 규칙표를 고치라고 해요")
  + block("방금 글은 문장이 길어. 규칙표의 문장 길이를 더 짧게 고쳐줘.") + block("\"~할 수 있습니다\"는 내가 안 써. 금지 표현에 추가해줘.")
  + done("같은 주제를 프로젝트 밖·안에서 시켜보고 차이가 보이면 세팅 완료!"))}
<h2>주의</h2>
{warn(["‘스스로 검수’는 AI가 자기 글을 다시 보는 방식이라 완벽하지 않아요. 최종본은 꼭 직접 읽어주세요."])}
<h2>이렇게 써먹어요</h2>
{chk(["보고서, 대본, 블로그 글, 이메일 모두 같은 방식", "종류가 다르면 그 종류 글을 샘플로 따로 추가", "저는 콘텐츠 제작·전자책 쓸 때 쓰고 있어요"])}"""))

# 3. 클로드 코드 설치가이드 -------------------------------------------------------
PAGES.append(dict(
    slug="claude-code", title="클로드 코드 설치가이드 & 활용법", desc="앱 설치부터 크롬 확장, 첫 명령까지 초간단 세팅",
    cover=("클로드 코드", "설치가이드", [("Claude", "#d97757"), ("Code", "#fff")]),
    h1=("클로드 코드", "설치가이드 & 활용법"),
    body=f"""<p class="lead">요즘 클로드 코드 활용도가 미친듯이 좋아지고 있어요.<br>근데 '코드'라니까 복잡해 보이죠?<br>제가 초간단으로 알려드릴게요.</p>
{shot("img2.jpg", "클로드 코드 화면")}
{prep(["Claude 유료 계정<small>Pro · Max · Team · Enterprise 중 하나. 무료 요금제는 Claude Code를 못 써요.</small>", "크롬 브라우저"])}
{step("STEP 1", "클로드 앱 설치", "다운로드 → 설치 → 로그인", shot("img3.jpg", "claude.ai/download 화면")
  + do(["크롬에서 <code>claude.ai/download</code> 접속 → 내 컴퓨터(맥/윈도우)에 맞는 파일 다운로드", "파일을 열어 설치 (맥: Claude 아이콘을 Applications 폴더로 끌어넣기)"]) + done("앱을 켜고 Claude 계정으로 로그인하면 끝!"))}
{step("STEP 2", "Git 설치", "있으면 더 편해요", shot("img4.jpg", "Git 다운로드 화면") + shot("img5.jpg", "Git 설치 화면")
  + do(["윈도우: <code>git-scm.com/downloads/win</code> 접속 → 다운로드 → Next만 계속 누르기", "맥: 대부분 이미 깔려 있어요. 'Git이 필요하다'는 안내가 뜰 때만 <code>git-scm.com/downloads</code>에서 설치"]) + done("클로드가 작업을 나눠서 안전하게 할 때 쓰는 도구예요."))}
{step("STEP 3", "앱에서 클로드 코드 켜기", "왼쪽 위 버튼 하나면 돼요", shot("img6.jpg", "클로드 앱의 Code 버튼 위치")
  + do(["클로드 앱 왼쪽 위 &lt;/&gt; 버튼(Code) 클릭", "아래 폴더 버튼에서 작업할 폴더 선택"]) + done("입력창이 열리면 준비 끝!"))}
{step("STEP 4", "크롬 확장 프로그램 설치", "클로드가 웹페이지를 보고 같이 일해요", shot("img7.jpg", "Claude for Chrome 설치 화면")
  + do(["크롬에서 claude.ai에 먼저 로그인", "<code>claude.com/claude-for-chrome</code> 접속 → Chrome에 추가 → 권한 확인", "주소창 옆 퍼즐 아이콘에서 Claude를 고정(핀)"]) + done("Claude 아이콘을 누르면 옆 패널이 열려요!"))}
{step("STEP 5", "이렇게 써보세요", "그냥 말로 시키면 돼요", shot("img8.jpg", "클로드 코드 입력창")
  + do(["입력창에 하고 싶은 일을 말하듯 적고 엔터"]) + block("이 폴더에 뭐가 있는지 쉽게 설명해줘") + block("할 일 목록 웹페이지 하나 만들어줘") + done("입력창에 / 를 치면 쓸 수 있는 명령어가 나와요."))}
{step("STEP 6", "마지막 확인", "클로드에게 직접 물어보면 끝!", shot("img9.jpg", "설치 확인 결과")
  + do(["복사 → 입력창에 붙여넣고 엔터"]) + block("Git, 클로드 코드가 잘 깔렸는지 확인하고 항목 옆에 ✓ 또는 ✗ 로 알려줘.") + done("전부 ✓ 이면 세팅 완료! 🎉"))}
<h2>이제 이런 게 가능해요</h2>
{chk(["웹사이트 디자인", "파일 정리", "업무 자동화", "엑셀 · 문서 작업", "나만의 프로그램 만들기"])}
{tip("각 활용법 자세한 팁은 다른 영상에서 알려드릴게요!")}"""))

# 4. 토큰 아끼는 스킬 3종 ----------------------------------------------------------
PAGES.append(dict(
    slug="token-saving", title="클로드 토큰 아끼는 스킬 3종 설치법 & 사용법", desc="headroom · ponytail · graphify로 토큰 순삭 막기",
    cover=("클로드 토큰", "아끼는 스킬 3종", [("headroom", "#4ea1ff"), ("ponytail", "#f2e15b"), ("graphify", "#3ee08f")]),
    h1=("클로드 토큰 순삭,", "이 스킬 세 개면 해결"),
    body=f"""<p class="lead">작업 몇 번 하고 나면 '사용 한도에 도달했습니다'… 익숙하시죠?<br>원인은 클로드의 <b>'전부 다 읽고, 길게 쓰는'</b> 방식이에요.<br>이 세 가지가 그걸 줄여줘요. 순서대로 해보세요!</p>
{shot("img1.jpg", "사용 한도 도달 vs 스킬 설치 후")}
{prep(["Claude Code<small>데스크톱 앱 Code 탭이나 터미널, 편한 곳에서요.</small>", "Node.js · <a href=\"https://nodejs.org\" target=\"_blank\" rel=\"noopener\">nodejs.org</a> LTS<small>ponytail이 쓰는 작은 훅이 node를 필요로 해요.</small>"])}
{step("STEP 1", "headroom · graphify 설치", "터미널에서 한 줄씩 붙여넣어요.",
  tip("uv가 없다면 먼저 → 맥: <code>brew install uv</code> · 윈도우: <code>winget install astral-sh.uv</code>")
  + line('uv tool install --python 3.13 "headroom-ai[all]"') + line("uv tool install graphifyy") + line("graphify install")
  + tip("graphify는 패키지 이름에 y가 두 개(graphifyy)예요. 비슷한 이름은 다른 프로젝트일 수 있어요."))}
{step("STEP 2", "headroom으로 클로드 코드 켜기", "앞으로 claude 대신 이렇게 켜주세요.", line("headroom wrap claude"))}
{step("STEP 3", "ponytail 설치", "켜진 Claude Code 입력창에 두 줄을 따로 입력해요.", do(["첫 번째 줄"]) + line("/plugin marketplace add DietrichGebert/ponytail") + do(["두 번째 줄"], 2) + line("/plugin install ponytail@ponytail") + done("설치만 해두면 매 세션 자동으로 켜져요."))}
{step("STEP 4", "graphify 실행", "내 프로젝트 폴더에서 한 번요.", line("/graphify .") + done("이제 셋 다 세팅 끝!"))}
<h2>도구별로 뭐가 줄어요?</h2>
{step('<i style="background:#4ea1ff"></i>headroom', "읽는 양 압축", "", "<p>검색 결과·로그·파일·지난 대화를 보내기 전에 내 컴퓨터에서 압축해요. 원본은 저장돼서 필요하면 다시 꺼내 봐요.</p>" + shot("img2.jpg", "headroom")
  + '<table class="num"><tr><td>장애 로그 분석</td><td>-57%</td></tr><tr><td>코드베이스 탐색</td><td>-42%</td></tr><tr><td>GitHub 이슈 정리</td><td>-30%</td></tr><tr><td>코드 검색 결과 100개</td><td>-21%</td></tr></table>', small="헤드룸")}
{step('<i style="background:#f2e15b"></i>ponytail', "쓰는 코드 줄이기", "", "<p>코드를 쓰기 전에 \"이미 있는 걸 재사용할 수 없나?\"부터 따지게 해서 코드를 짧게 만들어요.</p>" + shot("img3.jpg", "ponytail")
  + '<table class="num"><tr><td>작성한 코드 줄 수</td><td>-54%</td></tr><tr><td>시간</td><td>-27%</td></tr><tr><td>토큰</td><td>-22%</td></tr><tr><td>비용</td><td>-20%</td></tr></table>'
  + tip("제작자 측정값이에요. 실제 저장소(FastAPI+React)에서 기능 12개 수정 세션 평균, 모델 Haiku 4.5. 이미 코드가 촘촘한 프로젝트에선 거의 안 줄어요."), small="포니테일")}
{step('<i style="background:#3ee08f"></i>graphify', "찾는 길 미리 만들기", "", "<p>프로젝트를 지식 그래프(개념과 연결 지도)로 한 번 만들어 두고, 파일을 매번 다시 뒤지는 대신 지도로 바로 찾아가게 해요.</p>" + shot("img4.jpg", "graphify"), small="그래피파이")}
{tip("headroom 수치는 제작자 공개 예시 기준이에요.")}
<h2>이 순서로 쓰세요</h2>
{chk(["항상 <code>headroom wrap claude</code>로 켜기", "ponytail은 알아서 켜져요", "큰 프로젝트·자료 폴더에서 <code>/graphify .</code> 한 번"])}
<p class="bye">요금제 올리기 전에, 이 세 개부터 써보세요!</p>
{tip("2026년 10월 기준 설치법이에요. 도구 업데이트에 따라 명령어나 수치가 바뀔 수 있어요.")}"""))

# 5. AI 티 안 나는 웹사이트 (아티팩트 원본) -----------------------------------------
PAGES.append(dict(
    slug="web-design", title="AI 티 안 나는 웹사이트, 스킬 3개로 딸깍", desc="avoid-ai-design · taste · impeccable 설치법과 바로 쓰는 프롬프트",
    cover=("AI 티 안 나는", "웹사이트", [("avoid-ai", "#ff7a59"), ("taste", "#f2e15b"), ("impeccable", "#fff")]),
    h1=("AI 티 안 나는 웹사이트,", "스킬 3개로 딸깍"),
    body=f"""<p class="lead">"웹사이트 만들어줘" 하면 늘 비슷하죠?<br>보라색 그라데이션, 가운데 제목, 똑같은 카드 3개.<br><b>성능 문제가 아니라 디자인 기준을 안 줘서</b> 그래요.</p>
{prep(["Claude 유료 요금제 + Claude Code", "Node.js · <a href=\"https://nodejs.org\" target=\"_blank\" rel=\"noopener\">nodejs.org</a> LTS"])}
{tip("명령어가 어렵다면 Claude Code에 아래 GitHub 링크를 주고 \"이 스킬 설치해줘\"라고 하세요.")}
{step('<i style="background:#ff7a59"></i>STEP 1', "Avoid AI Design", "AI 티 진단기. 흔적을 찾아서 고쳐줘요.",
  do(["터미널에 입력하고 Claude Code를 다시 켜요."]) + line("git clone https://github.com/funboy322/avoid-ai-design.git ~/.claude/skills/avoid-ai-design")
  + lbl("고치기") + block("이 페이지 AI 티 안 나게 고쳐줘") + lbl("진단만 하기") + block("AI 티 나는 부분 진단만 해줘, 수정은 하지 마")
  + done("문제를 심각한 순서(P0 → P2)대로 알려줘요."), small="avoid-ai-design")}
{step('<i style="background:#f2e15b"></i>STEP 2', "Taste", "뻔한 레이아웃 대신 개성 있는 디자인으로.",
  line('npx skills add https://github.com/Leonxlnx/taste-skill --skill "design-taste-frontend"')
  + lbl("핵심은 레퍼런스예요") + block("taste 스킬로 첨부한 이미지 느낌을 살려서 ○○ 랜딩페이지 만들어줘.")
  + block("taste 스킬로 [홈페이지 주소] 분위기를 참고해서 ○○ 랜딩페이지 만들어줘. 똑같이 베끼지 말고 내 브랜드에 맞게.")
  + done("이미지는 Claude Code 입력창에 끌어다 놓으면 첨부돼요."), small="taste-skill")}
{step('<i style="background:#fff"></i>STEP 3', "Impeccable", "명령어 하나로 폰트·여백·색을 부분별로 다듬어요.",
  line("npx skills add https://github.com/pbakaus/impeccable --skill impeccable")
  + do(["처음에 서비스 정보를 알려줘요."]) + line("/impeccable init")
  + lbl("필요할 때마다") + chk(["<code>/impeccable critique</code> 뭐가 별로인지 피드백", "<code>/impeccable typeset</code> 폰트가 어색할 때", "<code>/impeccable layout</code> 여백·배치가 답답할 때", "<code>/impeccable bolder</code> · <code>quieter</code> 밋밋하거나 과할 때", "<code>/impeccable polish</code> 배포 전 마지막 점검"]), small="impeccable")}
<h2>3개 같이 쓰는 순서</h2>
{chk(["Taste로 레퍼런스 넣고 첫 버전 뽑기", "Avoid AI Design으로 AI 티 진단·제거", "Impeccable polish로 디테일 마감"])}
<h2>주의</h2>
{warn(["결과가 이상하면 \"이번엔 ○○ 스킬만 써줘\"처럼 하나만 지정하세요.", "2026년 9월 기준 설치법이에요. 스킬 업데이트에 따라 명령어가 바뀔 수 있어요."])}
<p class="src">출처 · <a href="https://github.com/funboy322/avoid-ai-design" target="_blank" rel="noopener">avoid-ai-design</a> · <a href="https://github.com/Leonxlnx/taste-skill" target="_blank" rel="noopener">taste-skill</a> · <a href="https://github.com/pbakaus/impeccable" target="_blank" rel="noopener">impeccable</a></p>"""))

# 6. 마케팅 팀 스킬 3종 ------------------------------------------------------------
PAGES.append(dict(
    slug="marketing", title="클로드 마케팅 팀 스킬 3종 설치법 & 사용법", desc="기획자 · 카피라이터 · 광고 기획자 스킬을 10분 만에 세팅",
    cover=("클로드가", "마케팅 팀이 된다", [("기획자", "#fff"), ("카피", "#f2e15b"), ("광고", "#ff7a59")]),
    h1=("이 스킬 세 개만 깔면", "클로드가 마케팅 팀이 됩니다"),
    body=f"""<p class="lead">세 스킬이 팀원 한 명씩 역할을 맡아요.<br><b>기획자가 내 제품을 정리</b>해 두면, 카피라이터와 광고 기획자가 그 문서부터 읽고 일해요.<br>순서대로 하면 10분이면 세팅 끝!</p>
<ol class="prep"><li><span class="n">1</span><span>기획자 · product-marketing<small>내 제품·고객·경쟁사를 문서 하나로 정리</small></span></li>
<li><span class="n">2</span><span>카피라이터 · copywriting<small>상세페이지·랜딩 카피 작성</small></span></li>
<li><span class="n">3</span><span>광고 기획자 · ad-creative<small>메타 광고 문구·소재 기획</small></span></li></ol>
{prep(["Claude 유료 플랜 + Claude Code", "Node.js · <a href=\"https://nodejs.org\" target=\"_blank\" rel=\"noopener\">nodejs.org</a> LTS<small>설치 명령어(npx)에 꼭 필요해요.</small>"])}
{step("STEP 1", "한 번에 설치", "터미널에 한 줄만 붙여넣어요.",
  block("npx skills add coreyhaines31/marketingskills --skill product-marketing copywriting ad-creative -a claude-code", ko=False)
  + tip("끝의 <code>-a claude-code</code>는 빼지 마세요. 없으면 Claude Code가 못 찾는 폴더에 깔려요.")
  + lbl("다른 방법: 마케팅 스킬 50개 전부 (Claude Code 입력창)") + line("/plugin marketplace add coreyhaines31/marketingskills") + line("/plugin install marketing-skills")
  + done("설치 후 Claude Code를 한 번 껐다 켜면 인식돼요."))}
{step('<i style="background:#fff"></i>STEP 2', "기획자: 마케팅 기초 문서", "제일 먼저 실행해요. 한 번 만들면 매번 제품 설명할 필요가 없어요.",
  do(["상세페이지·소개글·홈페이지 링크를 주면 초안을 알아서 써요.", "자료가 없으면 하나씩 질문해요. 대답만 하면 돼요.", "결과는 <code>.agents/product-marketing.md</code>에 저장돼요."])
  + line("/product-marketing") + lbl("자료로 초안 만들기")
  + block("/product-marketing 기존 상세페이지 첨부할게. 이걸로 마케팅 기초 문서 초안 만들어줘. 한국어로, 한국 20~30대 고객 기준으로 써줘.")
  + tip("기본 출력이 영어일 수 있어요. 처음에 \"한국어로, 한국 고객 기준으로\"라고 적어 두면 이후 결과물도 한국어로 맞춰져요."), small="product-marketing")}
{step('<i style="background:#f2e15b"></i>STEP 3', "카피라이터: 상세페이지 카피", "페이지 순서대로 쓰고, 문장마다 이유와 대안을 달아줘요.",
  do(["헤드라인·서브카피·버튼 → 후기 → 문제 공감 → 얻는 것 → 이용 방법 → 망설임 해소 → 행동 유도 순서로 써요.", "버튼 문구는 '행동 + 얻는 것'으로. (신청하기 ✗ → 내 피부 타입 확인하기 ✓)"])
  + block("인스타 광고 보고 넘어오는 사람용 상세페이지 첫 화면 카피 써줘. 광고 문구는 '○○○'야.")
  + block("신제품 랜딩페이지 카피 처음부터 끝까지 써줘. 헤드라인이랑 버튼 문구는 대안 3개씩.")
  + tip("없는 통계·가짜 후기는 안 지어내요. 실제 수치와 후기를 같이 주면 훨씬 좋아요."), small="copywriting")}
{step('<i style="background:#ff7a59"></i>STEP 4', "광고 기획자: 메타 광고 문구", "같은 제품을 여러 각도로 뽑고, 글자 수 규격까지 검사해줘요.",
  do(["각도 3~5개 잡기 (고통·결과·사회적 증거·호기심·비교·긴급성·정체성·역발상)", "각도별 헤드라인·본문 여러 개", "규격 검사: 본문 125자 · 헤드라인 40자 · 설명 30자"])
  + block("메타 광고 문구 만들어줘. 각도 5개로 나누고, 각도별로 헤드라인 3개씩. 규격 넘는 건 줄인 버전도.")
  + lbl("광고 돌린 뒤에는") + chk(["\"지난주 광고별 CTR이야. 잘된 패턴 찾아서 새 변형 만들어줘\"", "\"다음에 만들 광고 형식 추천해줘\"", "\"광고 댓글 모아왔어. 고객 말투로 문구 다시 써줘\""])
  + tip("판단은 노출 1,000회는 넘긴 뒤에, 한 번에 하나씩만 바꿔서 테스트하세요."), small="ad-creative")}
<h2>이 순서로 쓰세요</h2>
{chk(["product-marketing으로 기초 문서 (처음 한 번)", "copywriting으로 상세페이지·랜딩 카피", "ad-creative로 각도별 광고 문구", "매주 광고 성과를 넣고 새 변형 만들기"])}
<h2>자주 막히는 곳</h2>
{warn(["<b>npx: command not found</b> → Node.js를 설치하고 터미널을 새로 열어요.", "<b>스킬이 안 보여요</b> → Claude Code를 완전히 껐다 켜고, <code>-a claude-code</code>를 붙였는지 확인해요.", "<b>결과가 영어예요</b> → 요청에 \"한국어로\"를 붙이거나 기초 문서에 적어 두세요."])}
{lbl("보너스: 예산·타깃·캠페인 구조까지 짜는 ads 스킬")}
{block("npx skills add coreyhaines31/marketingskills --skill ads -a claude-code", ko=False)}
<p class="src">출처 · <a href="https://github.com/coreyhaines31/marketingskills" target="_blank" rel="noopener">github.com/coreyhaines31/marketingskills</a> (MIT) · 2026년 10월 기준</p>"""))


def build():
    # 파비콘
    (ROOT / "favicon.svg").write_text(favicon_svg(), encoding="utf-8")
    fav = f'<!doctype html><html><body style="margin:0;background:transparent"><img src="{(ROOT / "favicon.svg").as_uri()}" width="180" height="180"></body></html>'
    render(fav, str(ROOT / "apple-touch-icon.png"), 180, 180)
    render(fav.replace('width="180" height="180"', 'width="64" height="64"'), str(ROOT / "favicon.png"), 64, 64)
    for p in PAGES:
        d = ROOT / "scrolls" / p["slug"]; d.mkdir(parents=True, exist_ok=True)
        t1, t2, tiles = p["cover"]
        render(cover_html(t1, t2, tiles), str(d / "cover.png"), 1600, 1000)
        (d / "index.html").write_text(page(p["slug"], p["title"], p["desc"], f"픽셀 마법사와 {t1} {t2}",
                                           p["h1"][0], p["h1"][1], p["body"], p.get("js", "")), encoding="utf-8")
        assert "—" not in p["body"], p["slug"]
        print("built", p["slug"])

def patch_existing():
    for slug in ["claude-x-gpt", "claude-skills-top5"]:
        f = ROOT / "scrolls" / slug / "index.html"; s = f.read_text(encoding="utf-8")
        if 'class="cta"' not in s:
            s = s.replace("</style>", ".cta{display:flex;align-items:center;justify-content:center;gap:8px;margin-top:28px;min-height:56px;padding:0 20px;background:var(--stamp);border:2px solid var(--ink);box-shadow:5px 5px 0 var(--ink);color:var(--ink);font-weight:800;font-size:17px;text-decoration:none;transition:transform .15s,box-shadow .15s}\n.cta:hover{transform:translate(-1px,-1px);box-shadow:6px 6px 0 var(--ink)}\n.cta:active{transform:translate(3px,3px);box-shadow:2px 2px 0 var(--ink)}\n</style>", 1)
            s = re.sub(r'(<p class="sign">.*?</p>)', r'\1\n' + CTA, s, count=1)
        if "favicon.svg" not in s:
            s = s.replace("<style>", HEAD_EXTRA + "\n<style>", 1)
        f.write_text(s, encoding="utf-8"); print("patched", slug)

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    build()
    if "--cta" in sys.argv: patch_existing()
