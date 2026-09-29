"""품목별 페이지(p/<slug>/index.html)와 sitemap.xml을 site.json에서 만들어요.
site.json을 갱신한 뒤 `python build_pages.py`만 다시 돌리면 돼요."""
import json, html, os, shutil

BASE = "https://wellva3-lab.github.io/lowest-detective/"
ROOT = os.path.dirname(os.path.abspath(__file__))

SLUG = {
    "휴지": "toilet-paper", "키친타월": "kitchen-towel", "물티슈": "wet-wipes", "생수 2L": "water-2l",
    "쌀": "rice", "즉석밥": "instant-rice", "라면": "ramen", "참치캔": "canned-tuna", "계란": "eggs",
    "식용유": "cooking-oil", "커피믹스": "coffee-mix", "세탁세제": "laundry-detergent",
    "섬유유연제": "fabric-softener", "주방세제": "dish-soap", "샴푸": "shampoo", "치약": "toothpaste",
    "지퍼백": "zipper-bag", "고무장갑": "rubber-gloves",
}
DEAL_CAT = {
    "휴지": "세제·위생", "키친타월": "주방·살림", "물티슈": "육아", "생수 2L": "식품", "쌀": "식품",
    "즉석밥": "식품", "라면": "식품", "참치캔": "식품", "계란": "식품", "식용유": "식품", "커피믹스": "식품",
    "세탁세제": "세제·위생", "섬유유연제": "세제·위생", "주방세제": "주방·살림", "샴푸": "뷰티·욕실",
    "치약": "뷰티·욕실", "지퍼백": "주방·살림", "고무장갑": "주방·살림",
}
# 품목별 한두 줄 살림 팁 (검색해서 들어온 사람에게 도움이 되는 본문)
TIP = {
    "휴지": "휴지는 롤 수보다 '롤당 가격'과 길이를 같이 보세요. 3겹 제품은 한 롤이 빨리 줄어서 롤당 가격이 싸도 체감은 비슷할 수 있어요.",
    "키친타월": "키친타월은 롤당 매수(장수)가 제품마다 달라요. 롤당 가격이 비슷하면 장수가 많은 쪽이 이득이에요.",
    "물티슈": "물티슈는 캡형이 덜 마르지만 조금 더 비싸요. 한 번에 많이 사 두면 뚜껑을 연 뒤 마르기 쉬우니 한두 달 쓸 만큼만 사는 게 좋아요.",
    "생수 2L": "생수는 무게 때문에 로켓배송 묶음이 제일 편해요. 병당 1,000원 아래면 싼 편이에요.",
    "쌀": "쌀은 도정일이 최근일수록 맛있어요. 10kg은 2인 가구 기준 한두 달이면 먹으니, 싸다고 20kg을 사기보다 10kg을 자주 사는 게 좋아요.",
    "즉석밥": "즉석밥은 유통기한이 길어서 최저가일 때 두 박스 사 두기 좋은 품목이에요.",
    "라면": "라면은 5개입 묶음 기준 봉당 800원대면 싼 편이에요. 행사 때 멀티팩으로 사 두면 좋아요.",
    "참치캔": "참치캔은 유통기한이 길어서 쌀 때 쟁여 두기 좋아요. 캔당 가격으로 비교해 보세요.",
    "계란": "계란은 알당 가격으로 보세요. 오래 보관하지 못하니 최저가라도 2주 안에 먹을 만큼만 사세요.",
    "식용유": "식용유는 개봉 후 산패가 빨라서, 1인 가구라면 큰 용량보다 작은 병을 추천해요.",
    "커피믹스": "커피믹스는 개입 수가 많을수록 개당 가격이 싸져요. 170개입 이상 대용량이 보통 가장 저렴해요.",
    "세탁세제": "세탁세제는 리필 여러 개 묶음이 L당 가격이 가장 싸요. 드럼·일반 겸용인지 꼭 확인하세요.",
    "섬유유연제": "섬유유연제는 고농축이면 한 번에 쓰는 양이 적어서, L당 가격이 조금 비싸도 오래 써요.",
    "주방세제": "주방세제는 100ml당 가격으로 비교하세요. 대용량 리필을 사서 작은 통에 덜어 쓰면 가장 싸요.",
    "샴푸": "샴푸는 1L 넘는 대용량 2개 묶음이 100ml당 가격이 가장 싸요.",
    "치약": "치약은 3개 이상 묶음이 개당 가격이 싸요. 유통기한이 길어서 쌀 때 사 두기 좋아요.",
    "지퍼백": "지퍼백은 크기별로 섞인 멀티팩이 쓰기 편해요. 냉동용인지 확인하세요.",
    "고무장갑": "고무장갑은 니트릴 소재가 잘 안 찢어지고 오래 가요. 손 크기에 맞는 사이즈를 고르세요.",
}
SIG = {"buy": ("지금 사세요", "최근 2개월 기록 중 가장 싼 가격이에요. 필요하면 지금 사는 게 좋아요."),
       "ok": ("괜찮아요", "최저가보다 5% 안쪽이라 지금 사도 손해는 거의 없어요."),
       "wait": ("기다려 보세요", "최저가보다 5% 넘게 비싸요. 급하지 않다면 조금 기다려 보세요.")}

e = lambda s: html.escape(str(s if s is not None else ""), quote=True)
fmt = lambda n: f"{int(n):,}"


def md(d):
    y, m, dd = d.split("-")
    return f"{int(m)}월 {int(dd)}일"


CSS = """
:root{--bg:#FAF8F3;--card:#fff;--ink:#1E2229;--sub:#5F6670;--muted:#8B919A;--line:#ECE8DF;--soft:#F4F1EA;--brand:#2F5BEA;--hot:#F0654B;--gold:#FFC93C;--gold-soft:#FFF6DA;--buy:#14945F;--buy-soft:#E3F6EC;--ok:#B7790C;--ok-soft:#FFF3D6;--wait:#D9434F;--wait-soft:#FDEBEC;--f:"Pretendard Variable",Pretendard,-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--f);font-size:15px;line-height:1.6;letter-spacing:-.01em;-webkit-font-smoothing:antialiased}
a{color:inherit}.wrap{max-width:760px;margin:0 auto;padding-inline:16px}
.top{position:sticky;top:0;z-index:5;background:rgba(255,255,255,.94);border-bottom:1px solid var(--line)}
.top .wrap{display:flex;align-items:center;gap:10px;min-height:56px}
.brand{display:flex;align-items:center;gap:9px;text-decoration:none;font-weight:800;font-size:16px}
.mark{width:32px;height:32px;border-radius:10px;background:var(--gold);display:grid;place-items:center}
.top .home{margin-left:auto;font-size:13.5px;font-weight:700;color:var(--brand);text-decoration:none}
.adbar{background:var(--gold-soft);border-bottom:1px solid #F6E6B0;font-size:12.5px;font-weight:600;color:#6B5310}
.adbar .wrap{display:flex;gap:8px;align-items:center;padding-block:7px}
.adbar b{flex:none;background:#fff;border:1px solid #EDD58A;font-size:11px;font-weight:800;border-radius:6px;padding:0 6px}
.crumb{font-size:12.5px;color:var(--muted);margin:16px 0 6px}.crumb a{text-decoration:none}
h1{font-size:clamp(26px,6.5vw,34px);font-weight:800;letter-spacing:-.04em;line-height:1.2;margin:0}
.lead{color:var(--sub);margin:8px 0 0}
.card{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:18px;margin-top:14px;box-shadow:0 1px 2px rgba(30,34,41,.04),0 4px 14px rgba(30,34,41,.05)}
.verdict{display:flex;align-items:center;gap:12px}
.pill{display:inline-block;flex:none;white-space:nowrap;font-size:14px;font-weight:800;border-radius:10px;padding:5px 12px}
.pill.buy{background:var(--buy-soft);color:var(--buy)}.pill.ok{background:var(--ok-soft);color:var(--ok)}.pill.wait{background:var(--wait-soft);color:var(--wait)}
.verdict p{margin:0;color:var(--sub);font-size:14px}
.stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:14px}
.stat{background:var(--soft);border-radius:14px;padding:10px 12px;min-width:0}
.stat span{display:block;font-size:12px;font-weight:700;color:var(--muted)}
.stat b{display:block;font-size:clamp(15px,4.4vw,18px);overflow:hidden;text-overflow:ellipsis;font-weight:800;white-space:nowrap}
a.prod{display:grid;grid-template-columns:96px minmax(0,1fr);gap:14px;align-items:center;text-decoration:none;color:inherit}
a.prod img{width:96px;height:96px;object-fit:contain;border-radius:16px;border:1px solid var(--line);background:#fff}
a.prod .nm{font-weight:700;line-height:1.4}
a.prod .pr{font-size:20px;font-weight:800;margin-top:2px}
a.prod .go{display:inline-block;margin-top:6px;font-size:13px;font-weight:800;color:#fff;background:var(--brand);border-radius:10px;padding:6px 12px}
h2{font-size:18px;font-weight:800;margin:0 0 8px}
.tip p{margin:0;color:var(--sub)}
.deals{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
@media(min-width:620px){.deals{grid-template-columns:repeat(4,minmax(0,1fr))}}
a.deal{display:flex;flex-direction:column;border:1px solid var(--line);border-radius:14px;overflow:hidden;text-decoration:none;background:#fff}
a.deal img{width:100%;aspect-ratio:1;object-fit:contain;padding:6px;display:block}
a.deal .b{padding:8px 10px 10px;font-size:12.5px}
a.deal .nm{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:2.8em;line-height:1.4}
a.deal .pr{font-size:15px;font-weight:800}
a.deal .dn{color:var(--hot);font-weight:800}
.others{display:flex;flex-wrap:wrap;gap:6px}
.others a{border:1px solid var(--line);background:#fff;border-radius:999px;padding:6px 12px;font-size:13.5px;font-weight:700;color:var(--sub);text-decoration:none}
.others a:hover{color:var(--ink);border-color:var(--muted)}
footer{padding:26px 0 34px;color:var(--muted);font-size:12.5px}footer p{margin:4px 0}
"""

MARK = '<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="#1E2229" stroke-width="2.6"/><path d="M15.5 15.5l5 5" stroke="#1E2229" stroke-width="3" stroke-linecap="round"/></svg>'


def page(s, data, others):
    cat, slug = s["cat"], SLUG[s["cat"]]
    url = f"{BASE}p/{slug}/"
    label, why = SIG[s["signal"]]
    upd = data["updated"]
    rel = "noopener sponsored"
    gap = "최저가 ✓" if s["signal"] == "buy" else f"+{s['gap']}%"
    unit = f"{s['unitName']}당 {fmt(s['unit'])}원" if s.get("unit") else "-"
    title = f"{cat} 최저가 {md(upd)} 기준 — 지금 사도 될까? | 최저가 탐정"
    desc = (f"{cat} 쿠팡 최저가 시세. 지금 {fmt(s['now'])}원, 최근 2개월 최저 {fmt(s['low'])}원. "
            f"판정: {label}. {md(upd)} 기준으로 매주 업데이트해요.")
    img_abs = BASE + s["img"]
    deals = [d for d in data["deals"] if d["cat"] == DEAL_CAT.get(cat)]
    deals = sorted(deals, key=lambda d: -(d.get("drop") or 0))[:4]
    deal_html = "".join(
        f'<a class="deal" href="{e(d["link"])}" target="_blank" rel="{rel}"><img src="../../{e(d["img"])}" alt="" loading="lazy" width="180" height="180">'
        f'<div class="b"><div class="nm">{e(d["name"])}</div><div class="pr">{fmt(d["price"])}원</div>'
        + (f'<div class="dn">직전보다 {d["drop"]}%↓</div>' if d.get("drop") else "") + "</div></a>"
        for d in deals)
    other_html = "".join(f'<a href="../{SLUG[o["cat"]]}/">{e(o["cat"])} 최저가</a>' for o in others if o["cat"] != cat)
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "최저가 탐정", "item": BASE},
                {"@type": "ListItem", "position": 2, "name": f"{cat} 최저가", "item": url}]},
            {"@type": "Product", "name": s["name"], "image": img_abs, "category": cat,
             "offers": {"@type": "Offer", "price": s["now"], "priceCurrency": "KRW", "url": s["link"],
                        "availability": "https://schema.org/InStock", "priceValidUntil": upd}},
        ]}
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="최저가 탐정">
<meta property="og:title" content="{e(cat)} 최저가 — 지금 사도 될까?">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#FFFFFF">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 34 34'%3E%3Crect width='34' height='34' rx='10' fill='%23FFC93C'/%3E%3Ccircle cx='15' cy='15' r='7.5' fill='none' stroke='%23222' stroke-width='3'/%3E%3Cpath d='M20.5 20.5l6 6' stroke='%23222' stroke-width='3.6' stroke-linecap='round'/%3E%3C/svg%3E">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<header class="top"><div class="wrap"><a class="brand" href="../../"><span class="mark">{MARK}</span>최저가 탐정</a><a class="home" href="../../#board">전체 시세표 →</a></div></header>
<div class="adbar" role="note"><div class="wrap"><b>광고</b><span>이 페이지는 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</span></div></div>
<main class="wrap">
  <p class="crumb"><a href="../../">최저가 탐정</a> › 생필품 시세표 › {e(cat)}</p>
  <h1>{e(cat)} 최저가,<br>지금 사도 될까?</h1>
  <p class="lead">{md(upd)} 기준 쿠팡 가격을 최근 2개월 가격 기록과 비교했어요.</p>

  <div class="card">
    <div class="verdict"><span class="pill {s['signal']}">{label}</span><p>{why}</p></div>
    <div class="stats">
      <div class="stat"><span>지금 가격</span><b>{fmt(s['now'])}원</b></div>
      <div class="stat"><span>2개월 최저</span><b>{fmt(s['low'])}원</b></div>
      <div class="stat"><span>차이</span><b>{gap}</b></div>
    </div>
  </div>

  <div class="card">
    <a class="prod" href="{e(s['link'])}" target="_blank" rel="{rel}">
      <img src="../../{e(s['img'])}" alt="{e(s['name'])}" width="96" height="96">
      <div><div class="nm">{e(s['name'])}</div><div class="pr">{fmt(s['now'])}원</div><div style="font-size:13px;color:var(--sub)">{e(unit)}</div><span class="go">쿠팡에서 가격 확인 →</span></div>
    </a>
  </div>

  <div class="card tip"><h2>살 때 알아 두면 좋아요</h2><p>{e(TIP.get(cat, ''))}</p></div>

  {f'<div class="card"><h2>같이 보면 좋은 최저가 핫딜</h2><div class="deals">{deal_html}</div></div>' if deal_html else ''}

  <div class="card"><h2>다른 생필품 시세</h2><div class="others">{other_html}</div></div>

  <footer>
    <p>가격은 {md(upd)} 기준이에요. 쿠팡 가격은 하루에도 여러 번 바뀌니 구매 전에 최종 가격을 확인해 주세요.</p>
    <p>이 페이지의 상품 링크는 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다. 구매자가 내는 가격은 같아요.</p>
  </footer>
</main>
</body>
</html>
"""


def main():
    data = json.load(open(os.path.join(ROOT, "site.json"), encoding="utf-8"))
    out = os.path.join(ROOT, "p")
    if os.path.isdir(out):
        shutil.rmtree(out)
    urls = [(BASE, "1.0")]
    for s in data["staples"]:
        slug = SLUG.get(s["cat"])
        if not slug:
            print("slug 없음:", s["cat"]); continue
        os.makedirs(os.path.join(out, slug), exist_ok=True)
        with open(os.path.join(out, slug, "index.html"), "w", encoding="utf-8") as f:
            f.write(page(s, data, data["staples"]))
        urls.append((f"{BASE}p/{slug}/", "0.8"))
    # 메인 페이지의 '품목별 시세' 링크 채우기 (검색엔진이 따라 들어올 수 있게 정적 링크로)
    ip = os.path.join(ROOT, "index.html")
    ih = open(ip, encoding="utf-8").read()
    a, b = ih.index("<!--ITEMS-->") + len("<!--ITEMS-->"), ih.index("<!--/ITEMS-->")
    links = "".join(f'<a href="p/{SLUG[s["cat"]]}/">{e(s["cat"])} 최저가</a>' for s in data["staples"] if s["cat"] in SLUG)
    open(ip, "w", encoding="utf-8").write(ih[:a] + links + ih[b:])
    upd = data["updated"]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{u}</loc><lastmod>{upd}</lastmod><changefreq>weekly</changefreq><priority>{p}</priority></url>" for u, p in urls]
    sm.append("</urlset>")
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm) + "\n")
    print(f"{len(urls) - 1}개 품목 페이지, sitemap {len(urls)}개 주소")


if __name__ == "__main__":
    main()
