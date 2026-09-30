#!/usr/bin/env python3
"""Static site builder for joseph-hsieh.com.

Reads data/site.json and writes a complete trilingual static site to dist/.
Uses only the Python standard library, so it runs as-is on Cloudflare Pages
(build command: python3 build.py, output directory: dist).
"""
import html
import json
import os
import re
import shutil
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "dist")
DATA = json.load(open(os.path.join(ROOT, "data", "site.json"), encoding="utf-8"))
SITE = (DATA.get("settings", {}).get("siteUrl") or "https://joseph-hsieh.com").rstrip("/")
P = DATA["profile"]

LANGS = ["zh", "en", "ja"]
HTML_LANG = {"zh": "zh-Hant", "en": "en", "ja": "ja"}
HREFLANG = {"zh": "zh-Hant", "en": "en", "ja": "ja"}
OG_LOCALE = {"zh": "zh_TW", "en": "en_US", "ja": "ja_JP"}
PREFIX = {"zh": "/", "en": "/en/", "ja": "/ja/"}
CATS = ["impact", "gvc", "twvc", "fo"]
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

UI = {
    "zh": dict(menu="主選單", about="關於", services="服務與合作", articles="觀點", weekly="每週觀察",
               career="經歷", orgs="所屬機構", orgs_long="所屬機構介紹", contact="聯絡我", contact_h="一起聊聊",
               site="官方網站", kick="致來訪的朋友", letter="寫在前面", home="首頁",
               topics="影響力投資 · 天使投資 · 家族辦公室 · 新創", source="閱讀原文",
               noNews="本週此類別尚無新聞。", newsNote="每週一更新。摘要為整理重點，完整內容與數據請以原文為準。",
               by="文／", share="分享", copyLink="複製連結", linkCopied="已複製連結", copy="複製信箱",
               copied="已複製信箱", withEn="中英對照", allArticles="看全部觀點文章", allNews="看完整每週觀察",
               related="延伸閱讀", archive="過往週次", readMore="閱讀全文",
               title="謝文淵 Joseph Hsieh｜影響力投資・天使投資・家族辦公室・企業轉型",
               desc_home=None,
               ins_title="觀點｜謝文淵 Joseph Hsieh",
               ins_desc="謝文淵對影響力投資、家族辦公室、天使投資與企業轉型的觀點文章。",
               ins_lead="關於影響力投資、家族資本、早期投資與企業轉型的長文觀點。",
               news_title="每週觀察：影響力投資、創投與家族辦公室新聞｜謝文淵",
               news_desc="每週整理全球影響力投資、全球創投、台灣創投與家族辦公室重要新聞，附中英日摘要與原文連結。",
               news_lead="每週整理四類新聞：全球影響力投資、全球創業投資、台灣創投、家族辦公室。摘要附原文連結。",
               cats=dict(impact="全球影響力投資", gvc="全球創業投資", twvc="台灣創投", fo="家族辦公室"),
               zhOnly=None, readZh=None, notfound="找不到這個頁面", back="回到首頁"),
    "en": dict(menu="Main menu", about="About", services="Services", articles="Insights", weekly="Weekly Brief",
               career="Career", orgs="Affiliations", orgs_long="Affiliations", contact="Contact", contact_h="Let’s talk",
               site="Website", kick="To our visitors", letter="A note from Joseph", home="Home",
               topics="Impact investing · Angel investing · Family offices · Startups", source="Read source",
               noNews="No news in this category this week.",
               newsNote="Updated every Monday. Summaries capture the key points; please refer to the original sources for full details and figures.",
               by="By ", share="Share", copyLink="Copy link", linkCopied="Link copied", copy="Copy email",
               copied="Email copied", withEn="", allArticles="All insights", allNews="Full weekly brief",
               related="Related reading", archive="Past weeks", readMore="Read more",
               title="Joseph Hsieh | Impact Investing, Angel Investing, Family Offices & Corporate Transformation",
               desc_home=None,
               ins_title="Insights | Joseph Hsieh",
               ins_desc="Essays by Joseph Hsieh on impact investing, family offices, angel investing and corporate transformation in Taiwan and Asia.",
               ins_lead="Long-form perspectives on impact investing, family capital, early-stage investing and corporate transformation.",
               news_title="Weekly Brief: Impact Investing, Venture Capital & Family Office News | Joseph Hsieh",
               news_desc="A weekly digest of global impact investing, global venture capital, Taiwan VC and family office news, with summaries and source links.",
               news_lead="Four categories every week: global impact investing, global venture capital, Taiwan VC and family offices, each with a link to the source.",
               cats=dict(impact="Global Impact Investing", gvc="Global Venture Capital", twvc="Taiwan VC", fo="Family Offices"),
               zhOnly="The full article is currently published in Traditional Chinese.",
               readZh="Read the full article (Chinese) →", notfound="Page not found", back="Back to home"),
    "ja": dict(menu="メインメニュー", about="プロフィール", services="サービス", articles="論考", weekly="週刊ウォッチ",
               career="経歴", orgs="所属団体", orgs_long="所属団体のご紹介", contact="お問い合わせ", contact_h="お気軽にご相談ください",
               site="公式サイト", kick="ご訪問の皆さまへ", letter="はじめに", home="ホーム",
               topics="インパクト投資 · エンジェル投資 · ファミリーオフィス · スタートアップ", source="原文を読む",
               noNews="今週このカテゴリのニュースはありません。",
               newsNote="毎週月曜日に更新。要約は要点をまとめたものです。詳細やデータは原文をご確認ください。",
               by="文：", share="共有", copyLink="リンクをコピー", linkCopied="リンクをコピーしました", copy="メールをコピー",
               copied="コピーしました", withEn="英語を併記", allArticles="論考一覧へ", allNews="週刊ウォッチを見る",
               related="関連記事", archive="過去の週", readMore="続きを読む",
               title="謝文淵 Joseph Hsieh｜インパクト投資・エンジェル投資・ファミリーオフィス・企業変革",
               desc_home=None,
               ins_title="論考｜謝文淵 Joseph Hsieh",
               ins_desc="謝文淵（Joseph Hsieh）によるインパクト投資、ファミリーオフィス、エンジェル投資、企業変革に関する論考。",
               ins_lead="インパクト投資、ファミリーキャピタル、アーリーステージ投資、企業変革についての論考です。",
               news_title="週刊ウォッチ：インパクト投資・VC・ファミリーオフィスのニュース｜謝文淵",
               news_desc="世界のインパクト投資、グローバルVC、台湾VC、ファミリーオフィスの主要ニュースを毎週要約し、原文リンクとともにお届けします。",
               news_lead="毎週4つのカテゴリ（世界のインパクト投資、グローバルVC、台湾VC、ファミリーオフィス）のニュースを要約し、原文リンクを添えています。",
               cats=dict(impact="グローバル・インパクト投資", gvc="グローバルVC", twvc="台湾VC", fo="ファミリーオフィス"),
               zhOnly="本文は現在、繁体字中国語で掲載しています。",
               readZh="全文を読む（中国語）→", notfound="ページが見つかりません", back="ホームへ戻る"),
}


# ---------------------------------------------------------------- helpers
def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


def T(o, k, L):
    """Field k in language L, falling back to the Chinese field."""
    if not o:
        return ""
    if L == "zh":
        return o.get(k, "")
    lk = k + "_" + L
    if k == "u" and lk in o:
        return o[lk]
    v = o.get(lk)
    return v if v not in (None, "") else o.get(k, "")


def lines(t):
    return [x.strip() for x in str(t or "").split("\n") if x.strip()]


def tags(s):
    return [x.strip() for x in re.split(r"[、,，]", str(s or "")) if x.strip()]


def paras(t):
    return "".join("<p>" + esc(p.strip()) + "</p>" for p in re.split(r"\n\s*\n", str(t or "")) if p.strip())


def inline(s):
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(s))


def md(t):
    out = []
    for b in re.split(r"\n\s*\n", str(t or "")):
        b = b.strip()
        if not b:
            continue
        if re.match(r"^##\s+", b):
            out.append("<h2>" + inline(re.sub(r"^##\s+", "", b)) + "</h2>")
        elif re.match(r"^-\s+", b):
            out.append("<ul>" + "".join("<li>" + inline(re.sub(r"^-\s+", "", l)) + "</li>" for l in b.split("\n")) + "</ul>")
        else:
            out.append("<p>" + inline(b).replace("\n", "<br>") + "</p>")
    return "".join(out)


def plain(t, n=None):
    s = re.sub(r"\s+", " ", re.sub(r"[*#]", "", str(t or ""))).strip()
    if n and len(s) > n:
        s = s[: n - 1].rstrip() + "…"
    return s


def iso_date(s):
    m = re.match(r"(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})", str(s or ""))
    return "%s-%02d-%02d" % (m.group(1), int(m.group(2)), int(m.group(3))) if m else None


def week_label(w, L):
    wk = w.get("week", "")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", wk):
        return w.get("label") or wk
    y, m, d = wk.split("-")
    if L == "zh":
        return w.get("label") or "%s 年 %d 月 %d 日當週" % (y, int(m), int(d))
    if L == "en":
        return "Week of %s %d, %s" % (MON[int(m) - 1], int(d), y)
    return "%s年%d月%d日の週" % (y, int(m), int(d))


def hidden(section):
    return bool(DATA.get("settings", {}).get("hide", {}).get(section))


def name(L):
    return P["name_en"] if L == "en" else P["name_zh"] + " " + P["name_en"]


def abs_url(path):
    return SITE + path


ARTICLES = sorted(DATA.get("articles", []), key=lambda a: iso_date(a.get("date")) or "", reverse=True)
WEEKS = sorted(DATA.get("news", {}).get("weeks", []), key=lambda w: w.get("week", ""), reverse=True)
PERSON_ID = SITE + "/#person"


def art_path(a, L):
    return PREFIX[L] + "insights/" + a["slug"] + "/"


def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>"


def person_ld():
    orgs = []
    for r in P.get("roles", []):
        orgs.append({"@type": "Organization", "name": r.get("org_en") or r.get("org")})
    return {
        "@context": "https://schema.org",
        "@type": "Person",
        "@id": PERSON_ID,
        "name": P["name_en"],
        "alternateName": [P["name_zh"], P["name_zh"] + " " + P["name_en"], "謝文淵 Joseph"],
        "url": SITE + "/",
        "image": SITE + P["photo"],
        "jobTitle": "Chairman, DoublePortion Capital",
        "description": P.get("lead_en"),
        "worksFor": {"@type": "Organization", "name": "DoublePortion Capital", "alternateName": "倍恩資本股份有限公司"},
        "affiliation": orgs,
        "memberOf": [{"@type": "Organization", "name": o.get("name_en") or o.get("name"), "url": o.get("url")} for o in DATA.get("orgs", [])],
        "alumniOf": {"@type": "CollegeOrUniversity", "name": "National Taiwan University", "alternateName": "國立臺灣大學"},
        "knowsAbout": ["Impact investing", "Angel investing", "Family offices", "Corporate transformation",
                       "Venture capital", "Financial inclusion", "影響力投資", "天使投資", "家族辦公室", "企業轉型"],
        "sameAs": [u for u in (P.get("linkedin"), P.get("facebook"), P.get("instagram")) if u],
    }


# ---------------------------------------------------------------- layout
def head(L, title, desc, path, alternates, og_type="website", og_image=None, extra_ld=None):
    alt = "".join('<link rel="alternate" hreflang="%s" href="%s">' % (HREFLANG[l], abs_url(p)) for l, p in alternates.items())
    if "zh" in alternates:
        alt += '<link rel="alternate" hreflang="x-default" href="%s">' % abs_url(alternates["zh"])
    img = abs_url(og_image or "/assets/og-%s.jpg" % L)
    lds = "".join(jsonld(x) for x in (extra_ld or []))
    return f"""<!doctype html>
<html lang="{HTML_LANG[L]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="author" content="{esc(name(L))}">
<link rel="canonical" href="{abs_url(path)}">
{alt}
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{esc(name(L))}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{abs_url(path)}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{OG_LOCALE[L]}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#FD6925">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="alternate" type="application/rss+xml" title="{esc(name(L))}" href="{PREFIX[L]}feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800;900&family=Noto+Sans+JP:wght@400;500;700;900&family=Noto+Sans+TC:wght@400;500;700;900&display=swap">
<link rel="stylesheet" href="/assets/site.css?v={VERSION}">
{lds}
</head>
<body>
<a class="skip" href="#main">{ {"zh": "跳到主要內容", "en": "Skip to content", "ja": "本文へスキップ"}[L] }</a>
"""


def nav(L, alternates, on_home=False):
    U = UI[L]
    home = PREFIX[L]
    a = lambda anchor: ("#" if on_home else home + "#") + anchor
    brand = esc(P["name_en"]) if L == "en" else esc(P["name_zh"]) + "<span>" + esc(P["name_en"]) + "</span>"
    links = [
        (a("about"), U["about"]), (a("services"), U["services"]), (home + "insights/", U["articles"]),
        (home + "news/", U["weekly"]), (a("career"), U["career"]), (a("orgs"), U["orgs"]),
    ]
    nav_html = "".join('<a href="%s">%s</a>' % (h, t) for h, t in links)
    nav_html += '<a class="cta" href="%s">%s</a>' % (a("contact"), U["contact"])
    sw = "".join(
        '<a href="%s" hreflang="%s" lang="%s"%s>%s</a>' % (
            alternates.get(l, PREFIX[l]), HREFLANG[l], HTML_LANG[l],
            ' aria-current="true"' if l == L else "", lab)
        for l, lab in (("zh", "中"), ("en", "EN"), ("ja", "日")))
    return (f'<header class="nav"><div class="wrap"><a class="brand" href="{home}">{brand}</a>'
            f'<nav aria-label="{U["menu"]}">{nav_html}</nav>'
            f'<div class="lang-switch" role="group" aria-label="Language">{sw}</div></div></header>')


def footer(L, alternates):
    U = UI[L]
    langs = "".join('<a href="%s" hreflang="%s" lang="%s">%s</a>' % (alternates.get(l, PREFIX[l]), HREFLANG[l], HTML_LANG[l], lab)
                    for l, lab in (("zh", "繁體中文"), ("en", "English"), ("ja", "日本語")))
    return (f'<footer><span>© {date.today().year} {esc(P["name_zh"])} {esc(P["name_en"])}</span>'
            f'<span>{esc(P.get("motto", ""))}</span><span class="langs-foot">{langs}</span></footer>')


def page(L, title, desc, path, alternates, body, og_type="website", og_image=None, ld=None, on_home=False):
    return (head(L, title, desc, path, alternates, og_type, og_image, ld)
            + nav(L, alternates, on_home)
            + '<main class="wrap" id="main">' + body + footer(L, alternates) + "</main>"
            + '<div id="toast" role="status" aria-live="polite"></div>'
            + '<script src="/assets/site.js?v=%s" defer></script></body></html>\n' % VERSION)


def share_bar(url, title, L, extra=""):
    U = UI[L]
    u = esc(url)
    from urllib.parse import quote
    uq, tq = quote(url, safe=""), quote(title, safe="")
    return (f'<div class="share{extra}"><span class="lbl">{U["share"]}</span>'
            f'<a href="https://www.linkedin.com/sharing/share-offsite/?url={uq}" target="_blank" rel="noopener" aria-label="LinkedIn">in</a>'
            f'<a href="https://www.facebook.com/sharer/sharer.php?u={uq}" target="_blank" rel="noopener" aria-label="Facebook">f</a>'
            f'<a href="https://twitter.com/intent/tweet?url={uq}&amp;text={tq}" target="_blank" rel="noopener" aria-label="X">X</a>'
            f'<a href="https://social-plugins.line.me/lineit/share?url={uq}" target="_blank" rel="noopener" aria-label="LINE">LINE</a>'
            f'<button class="copy" data-url="{u}" data-done="{esc(U["linkCopied"])}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7.07 0l3-3a5 5 0 0 0-7.07-7.07l-1.5 1.5"/><path d="M14 11a5 5 0 0 0-7.07 0l-3 3a5 5 0 0 0 7.07 7.07l1.5-1.5"/></svg>{U["copyLink"]}</button></div>')


def sec_head(L, h2, en, aside="", tag="h2"):
    sub = "" if L == "en" else '<span class="en">%s</span>' % en
    return f'<div class="sec-head"><{tag}>{h2}</{tag}>{sub}{aside}</div>'


# ---------------------------------------------------------------- blocks
def article_cards(L, items):
    out = []
    for i, a in enumerate(items):
        href = art_path(a, L)
        meta = '<span class="mono">%s</span>' % esc(a.get("date")) + "".join('<span class="chip">%s</span>' % esc(t) for t in tags(T(a, "tags", L)))
        thumb = ('<div class="thumb"><img src="%s" alt="" loading="lazy"></div>' % esc(a["image"])) if a.get("image") else \
            '<div class="thumb empty" aria-hidden="true">%s</div>' % esc((a.get("title") or "")[:1])
        out.append(
            f'<div class="art-item"><a class="art" href="{href}">{thumb}<div class="inner"><div class="meta">{meta}</div>'
            f'<h3>{esc(T(a, "title", L))}</h3>'
            + (f'<div class="sub">{esc(T(a, "subtitle", L))}</div>' if a.get("subtitle") else "")
            + f'<p class="sum">{esc(T(a, "summary", L))}</p></div></a>'
            + share_bar(abs_url(href), T(a, "title", L), L) + "</div>")
    return '<div class="articles">' + "".join(out) + "</div>"


def news_items(L, items, bi=True):
    U = UI[L]
    if not items:
        return '<p class="note">%s</p>' % U["noNews"]
    out = []
    for n in items:
        t1 = n.get("title_" + L) or n.get("title_zh")
        s1 = n.get("sum_" + L) or n.get("sum_zh")
        en = ""
        if L != "en" and bi and n.get("title_en"):
            en = '<div class="en" lang="en"><h4>%s</h4><p>%s</p></div>' % (esc(n["title_en"]), esc(n.get("sum_en")))
        link = ('<a class="out" href="%s" target="_blank" rel="noopener">%s ↗</a>' % (esc(n["url"]), U["source"])) if n.get("url") else ""
        out.append(f'<article class="item"><div class="when"><b>{esc(n.get("source"))}</b><span>{esc(n.get("date"))}</span></div>'
                   f'<div><h3>{esc(t1)}</h3><p>{esc(s1)}</p>{en}{link}</div></article>')
    return "".join(out)


def bi_toggle(L):
    if L == "en":
        return ""
    return '<div class="langs"><button class="tab" data-bi aria-pressed="true">%s</button></div>' % UI[L]["withEn"]


# ---------------------------------------------------------------- pages
def build_home(L):
    U = UI[L]
    path = PREFIX[L]
    alts = dict(PREFIX)
    h = '<div class="hero-zone"><section class="hero"><div>'
    h += '<div class="eyebrow">%s</div>' % esc(T(P, "eyebrow", L))
    h += '<h1><span class="h1-name">%s</span>%s</h1>' % (esc(name(L)), esc(T(P, "headline", L)).replace("\n", "<br>"))
    h += '<p class="motto">%s</p>' % esc(P.get("motto", "")).replace(", ", ",<br>", 1)
    h += '<p class="lead">%s</p>' % esc(T(P, "lead", L))
    h += '<div class="hero-tags">' + "".join("<span>%s</span>" % esc(t) for t in tags(T(P, "tags", L))) + "</div></div>"
    h += ('<div class="portrait-wrap"><div class="portrait"><img src="%s" srcset="/assets/joseph-hsieh-400.jpg 400w, %s 800w" '
          'sizes="(max-width:900px) 280px, 360px" width="800" height="1000" alt="%s" fetchpriority="high"></div></div></section>') % (
        P["photo"], P["photo"], esc(name(L)))
    h += '<div class="ledger">' + "".join('<div><b>%s<i>%s</i></b><span>%s</span></div>' % (esc(T(s, "n", L)), esc(T(s, "u", L)), esc(T(s, "l", L))) for s in P.get("stats", [])) + "</div></div>"
    if P.get("letter"):
        h += ('<section class="letter"><div><div class="kick">%s</div><h2>%s</h2></div><div class="body">%s<p class="sig">— %s</p></div></section>'
              % (U["kick"], U["letter"], paras(T(P, "letter", L)), esc(T(P, "signature", L))))
    # about
    intro_en = ""
    if L == "zh" and P.get("intro_en"):
        intro_en = '<div class="intro-en" lang="en"><span class="mono">In English</span>%s</div>' % esc(P["intro_en"]).replace("\n\n", "<br><br>")
    roles = "".join('<div class="role"><b>%s</b><span class="r">%s</span><span class="n">%s</span></div>' % (esc(T(r, "org", L)), esc(T(r, "role", L)), esc(T(r, "note", L))) for r in P.get("roles", []))
    h += ('<section class="block" id="about">' + sec_head(L, U["about"], "About")
          + '<div class="about"><div class="prose">' + paras(T(P, "intro", L)) + intro_en + '</div><div><div class="roles">' + roles + "</div>"
          + ('<p class="faith">%s</p>' % esc(T(P, "faith", L)) if P.get("faith") else "") + "</div></div></section>")
    # services
    svc = ""
    for s in DATA.get("services", []):
        svc += ('<article class="svc">' + ('<span class="tag">%s</span>' % esc(T(s, "tag", L)) if s.get("tag") else "")
                + "<h3>%s</h3>" % esc(T(s, "title", L)) + ("" if L == "en" else '<div class="en">%s</div>' % esc(s.get("en")))
                + "<p>%s</p><ul>%s</ul></article>" % (esc(T(s, "desc", L)), "".join("<li>%s</li>" % esc(x) for x in lines(T(s, "points", L)))))
    h += '<section class="block" id="services">' + sec_head(L, U["services"], "Services") + '<div class="services">' + svc + "</div></section>"
    # articles
    h += ('<section class="block" id="articles">' + sec_head(L, U["articles"], "Perspectives", '<span class="aside mono">%s</span>' % U["topics"])
          + article_cards(L, ARTICLES[:3]) + '<p class="more"><a href="%sinsights/">%s →</a></p></section>' % (PREFIX[L], U["allArticles"]))
    # events
    if not hidden("events"):
        ev = ""
        for v in DATA.get("engagements", []):
            ti = esc(T(v, "title", L))
            if v.get("url"):
                ti = '<a href="%s" target="_blank" rel="noopener" style="color:inherit">%s ↗</a>' % (esc(v["url"]), ti)
            ev += '<div class="ev"><div class="d">%s</div><div><h3>%s</h3><div class="o">%s</div>%s</div></div>' % (
                esc(T(v, "date", L)), ti, esc(T(v, "org", L)), "<p>%s</p>" % esc(T(v, "desc", L)) if v.get("desc") else "")
        h += '<section class="block" id="events">' + sec_head(L, {"zh": "演講與活動", "en": "Speaking & Engagements", "ja": "講演・活動"}[L], "Speaking &amp; Engagements") + '<div class="events">' + ev + "</div></section>"
    # weekly (latest)
    if WEEKS:
        wk = WEEKS[0]
        tabs = "".join('<button class="tab" role="tab" data-cat="%s" aria-selected="%s">%s<small>%d</small></button>' % (
            c, "true" if i == 0 else "false", U["cats"][c], len(wk.get("items", {}).get(c, []))) for i, c in enumerate(CATS))
        panels = "".join('<div class="news panel" data-panel="%s" role="tabpanel" aria-label="%s"%s>%s</div>' % (
            c, U["cats"][c], "" if i == 0 else " data-hide", news_items(L, wk.get("items", {}).get(c, []))) for i, c in enumerate(CATS))
        h += ('<section class="block" id="weekly">' + sec_head(L, U["weekly"], "Weekly Brief", '<span class="aside mono">%s</span>' % esc(week_label(wk, L)))
              + '<div class="weekly-ctl" style="display:flex;gap:12px;flex-wrap:wrap;justify-content:space-between;align-items:center;margin-bottom:8px"><div class="tabs" role="tablist">'
              + tabs + "</div>" + bi_toggle(L) + "</div>" + panels
              + '<p class="note">%s</p><p class="more"><a href="%snews/">%s →</a></p></section>' % (U["newsNote"], PREFIX[L], U["allNews"]))
    # career
    tl = "".join('<div class="tl"><div class="yr">%s</div><div><h3>%s</h3>%s<ul>%s</ul></div></div>' % (
        esc(c.get("years")), esc(T(c, "org", L)), '<div class="rl">%s</div>' % esc(T(c, "role", L)) if c.get("role") else "",
        "".join("<li>%s</li>" % esc(x) for x in lines(T(c, "points", L)))) for c in DATA.get("career", []))
    h += '<section class="block" id="career">' + sec_head(L, U["career"], "Career") + '<div class="timeline">' + tl + "</div></section>"
    # orgs
    og = ""
    for o in DATA.get("orgs", []):
        st = o.get("stats") or []
        link = ""
        if o.get("url"):
            link = '<a class="org-link" href="%s" target="_blank" rel="noopener">%s · %s ↗</a>' % (
                esc(o["url"]), U["site"], esc(re.sub(r"^https?://(www\.)?", "", o["url"]).rstrip("/")))
        grid = ('<div class="sicgrid">' + "".join('<div><b>%s<i>%s</i></b><span>%s</span></div>' % (esc(T(s, "n", L)), esc(T(s, "u", L)), esc(T(s, "l", L))) for s in st) + "</div>") if st else ""
        og += ('<article class="org"><div class="org-head"><div><h3>%s</h3>%s</div>%s</div><div class="org-body%s"><div><p class="desc">%s</p><ul>%s</ul></div>%s</div></article>' % (
            esc(T(o, "name", L)), '<span class="org-role">%s</span>' % esc(T(o, "role", L)) if o.get("role") else "", link,
            "" if st else " solo", esc(T(o, "desc", L)), "".join("<li>%s</li>" % esc(x) for x in lines(T(o, "points", L))), grid))
    if og:
        h += '<section class="block" id="orgs">' + sec_head(L, U["orgs_long"], "Affiliations") + '<div class="orgs">' + og + "</div></section>"
    # contact
    socials = "".join('<a href="%s" target="_blank" rel="noopener me">%s ↗</a>' % (esc(P[k]), lab) for k, lab in (("linkedin", "LinkedIn"), ("facebook", "Facebook"), ("instagram", "Instagram")) if P.get(k))
    h += ('<section class="block" id="contact"><div class="contact-panel"><div><h2>%s</h2><p class="big">%s</p></div><div>'
          '<div class="mailbox"><code id="mail"><a href="mailto:%s" style="color:inherit;text-decoration:none">%s</a></code><button class="btn" data-copymail="%s" data-done="%s">%s</button></div>'
          '<div class="social">%s</div></div></div></section>') % (
        U["contact_h"], esc(T(P, "contact_note", L)), esc(P["email"]), esc(P["email"]), esc(P["email"]), esc(U["copied"]), U["copy"], socials)

    desc = plain(T(P, "lead", L), 160)
    website = {"@context": "https://schema.org", "@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/",
               "name": name(L), "inLanguage": HTML_LANG[L], "publisher": {"@id": PERSON_ID}}
    profile = {"@context": "https://schema.org", "@type": "ProfilePage", "url": abs_url(path), "inLanguage": HTML_LANG[L],
               "mainEntity": {"@id": PERSON_ID}, "name": U["title"]}
    return page(L, U["title"], desc, path, alts, h, ld=[person_ld(), website, profile], on_home=True)


def build_insights(L):
    U = UI[L]
    path = PREFIX[L] + "insights/"
    alts = {l: PREFIX[l] + "insights/" for l in LANGS}
    body = ('<div class="page-head"><nav class="crumbs" aria-label="breadcrumb"><a href="%s">%s</a><span>%s</span></nav>'
            '<h1>%s</h1><p>%s</p></div><section class="block" style="padding-top:40px">%s</section>') % (
        PREFIX[L], U["home"], U["articles"], U["articles"], U["ins_lead"], article_cards(L, ARTICLES))
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": U["ins_title"], "url": abs_url(path),
           "inLanguage": HTML_LANG[L], "author": {"@id": PERSON_ID},
           "hasPart": [{"@type": "Article", "headline": T(a, "title", L), "url": abs_url(art_path(a, L))} for a in ARTICLES]}]
    return page(L, U["ins_title"], U["ins_desc"], path, alts, body, ld=ld)


def build_article(L, a):
    U = UI[L]
    path = art_path(a, L)
    alts = {l: art_path(a, l) for l in LANGS}
    title = T(a, "title", L)
    body_text = a.get("body") if L == "zh" else a.get("body_" + L)
    by = T(a, "byline", L) or name(L)
    head_html = ('<article class="reader"><nav class="crumbs" aria-label="breadcrumb"><a href="%s">%s</a><a href="%sinsights/">%s</a></nav>'
                 '<span class="mono" style="display:block;margin-top:18px">%s · %s</span><h1>%s</h1>%s<div class="by">%s%s</div>%s') % (
        PREFIX[L], U["home"], PREFIX[L], U["articles"], esc(a.get("date")), esc(" · ".join(tags(T(a, "tags", L)))), esc(title),
        '<p class="sub">%s</p>' % esc(T(a, "subtitle", L)) if a.get("subtitle") else "", U["by"], esc(by),
        share_bar(abs_url(path), title, L))
    if body_text:
        content = '<div class="md">%s</div>' % md(body_text)
    else:
        content = ('<p class="lede">%s</p><div class="zh-note">%s <a href="%s" hreflang="zh-Hant">%s</a></div>') % (
            esc(T(a, "summary", L)), U["zhOnly"], art_path(a, "zh"), U["readZh"])
    others = [x for x in ARTICLES if x is not a]
    rel = ""
    if others:
        rel = '<aside class="related"><h2>%s</h2><ul>%s</ul></aside>' % (
            U["related"], "".join('<li><a href="%s">%s</a></li>' % (art_path(x, L), esc(T(x, "title", L))) for x in others[:3]))
    body = head_html + content + share_bar(abs_url(path), title, L, " end") + rel + "</article>"
    pub = iso_date(a.get("date"))
    img = "/assets/og/%s-%s.jpg" % (a["slug"], L)
    if not os.path.exists(os.path.join(ROOT, img.lstrip("/"))):
        img = None
    ld = [{
        "@context": "https://schema.org", "@type": "Article", "headline": title[:110],
        "description": plain(T(a, "summary", L), 300), "inLanguage": HTML_LANG[L] if body_text else "zh-Hant",
        "datePublished": pub, "dateModified": a.get("updated") or pub,
        "author": {"@type": "Person", "@id": PERSON_ID, "name": P["name_en"], "alternateName": P["name_zh"], "url": SITE + "/"},
        "publisher": {"@type": "Person", "@id": PERSON_ID, "name": P["name_en"]},
        "image": abs_url(img or "/assets/og-%s.jpg" % L), "mainEntityOfPage": abs_url(path),
        "keywords": ", ".join(tags(T(a, "tags", L))),
    }, {
        "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": U["home"], "item": abs_url(PREFIX[L])},
            {"@type": "ListItem", "position": 2, "name": U["articles"], "item": abs_url(PREFIX[L] + "insights/")},
            {"@type": "ListItem", "position": 3, "name": title, "item": abs_url(path)}]}]
    extra_meta = ""
    html_out = page(L, "%s｜%s" % (title, name(L)) if L != "en" else "%s | %s" % (title, name(L)),
                    plain(T(a, "summary", L), 160), path, alts, body, og_type="article", og_image=img, ld=ld)
    if pub:
        html_out = html_out.replace('<meta name="twitter:card"',
                                    '<meta property="article:published_time" content="%s">\n<meta property="article:author" content="%s">\n<meta name="twitter:card"' % (pub, SITE + "/"), 1)
    return html_out


def build_news(L, idx):
    U = UI[L]
    wk = WEEKS[idx]
    latest = idx == 0
    path = PREFIX[L] + ("news/" if latest else "news/%s/" % wk["week"])
    alts = {l: PREFIX[l] + ("news/" if latest else "news/%s/" % wk["week"]) for l in LANGS}
    wl = "".join('<a href="%s"%s>%s</a>' % (PREFIX[L] + ("news/" if i == 0 else "news/%s/" % w["week"]),
                                             ' aria-current="page"' if i == idx else "", esc(week_label(w, L))) for i, w in enumerate(WEEKS[:12]))
    cats = "".join('<section class="news-cat" id="%s">%s<div class="news">%s</div></section>' % (
        c, sec_head(L, U["cats"][c], "", tag="h2").replace('<span class="en"></span>', ""), news_items(L, wk.get("items", {}).get(c, []))) for c in CATS)
    body = ('<div class="page-head"><nav class="crumbs" aria-label="breadcrumb"><a href="%s">%s</a><span>%s</span></nav>'
            '<h1>%s</h1><p>%s</p><p class="mono" style="margin-top:18px">%s</p>%s</div>'
            '<div style="margin-top:28px">%s</div>%s<p class="note">%s</p>') % (
        PREFIX[L], U["home"], U["weekly"], U["weekly"], U["news_lead"], esc(week_label(wk, L)),
        ('<nav class="weeklist" aria-label="%s">%s</nav>' % (U["archive"], wl)) if len(WEEKS) > 1 else "", bi_toggle(L), cats, U["newsNote"])
    title = U["news_title"] if latest else "%s｜%s" % (week_label(wk, L), U["news_title"])
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "url": abs_url(path), "inLanguage": HTML_LANG[L],
           "author": {"@id": PERSON_ID}, "datePublished": wk["week"]}]
    return page(L, title, U["news_desc"], path, alts, body, ld=ld)


def build_404():
    body = ('<div class="page-head"><h1>404</h1><p>找不到這個頁面 · Page not found · ページが見つかりません</p>'
            '<p class="more"><a href="/">回到首頁</a> · <a href="/en/">Home (English)</a> · <a href="/ja/">ホーム（日本語）</a></p></div>')
    h = page("zh", "404｜謝文淵 Joseph Hsieh", "Page not found", "/404.html", {"zh": "/"}, body)
    return h.replace('<link rel="canonical"', '<meta name="robots" content="noindex"><link rel="canonical"', 1)


# ---------------------------------------------------------------- feeds & meta files
def sitemap(entries):
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for alts, lastmod in entries:
        for l, p in alts.items():
            out.append("<url><loc>%s</loc>" % esc(abs_url(p)) + (("<lastmod>%s</lastmod>" % lastmod) if lastmod else ""))
            for l2, p2 in alts.items():
                out.append('<xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (HREFLANG[l2], esc(abs_url(p2))))
            if "zh" in alts:
                out.append('<xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % esc(abs_url(alts["zh"])))
            out.append("</url>")
    out.append("</urlset>")
    return "\n".join(out) + "\n"


def rss(L):
    items = []
    for a in ARTICLES:
        link = abs_url(art_path(a, L))
        d = iso_date(a.get("date"))
        pub = ""
        if d:
            y, m, dd = map(int, d.split("-"))
            import email.utils, datetime
            pub = email.utils.format_datetime(datetime.datetime(y, m, dd, 8, 0, tzinfo=datetime.timezone.utc))
        items.append("<item><title>%s</title><link>%s</link><guid>%s</guid><pubDate>%s</pubDate><description>%s</description></item>" % (
            esc(T(a, "title", L)), link, link, pub, esc(T(a, "summary", L))))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>%s</title><link>%s</link>'
            '<description>%s</description><language>%s</language>%s</channel></rss>\n') % (
        esc(name(L)), abs_url(PREFIX[L]), esc(UI[L]["ins_desc"]), HTML_LANG[L], "".join(items))


def llms_txt():
    lines_ = ["# %s %s" % (P["name_zh"], P["name_en"]), "",
              "> " + plain(P.get("lead_en")), "",
              plain(P.get("lead")), "",
              "## Profile",
              "- [About (繁體中文)](%s/#about)" % SITE, "- [About (English)](%s/en/#about)" % SITE, "- [About (日本語)](%s/ja/#about)" % SITE, "",
              "## Insights"]
    for a in ARTICLES:
        lines_.append("- [%s](%s): %s" % (a["title"], abs_url(art_path(a, "zh")), plain(a.get("summary_en") or a.get("summary"), 240)))
        if a.get("body_en"):
            lines_.append("  - English: [%s](%s)" % (a.get("title_en"), abs_url(art_path(a, "en"))))
    lines_ += ["", "## Weekly Brief", "- [Weekly Brief (English)](%s/en/news/)" % SITE, "- [每週觀察](%s/news/)" % SITE, "",
               "## Contact", "- Email: %s" % P["email"]] + ["- %s" % P[k] for k in ("linkedin", "facebook", "instagram") if P.get(k)]
    return "\n".join(lines_) + "\n"


def write(rel, content):
    fp = os.path.join(OUT, rel.lstrip("/"))
    if fp.endswith("/"):
        fp += "index.html"
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(content)


VERSION = str(abs(hash(json.dumps(DATA, sort_keys=True))) % 10**8)


def main():
    global VERSION
    import hashlib
    h = hashlib.sha1()
    for f in ("assets/site.css", "assets/site.js", "data/site.json"):
        h.update(open(os.path.join(ROOT, f), "rb").read())
    VERSION = h.hexdigest()[:10]

    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(OUT, "assets"))
    for f in os.listdir(os.path.join(ROOT, "static")):
        shutil.copy(os.path.join(ROOT, "static", f), os.path.join(OUT, f))

    today = date.today().isoformat()
    newest_article = max([iso_date(a.get("date")) or "" for a in ARTICLES] or [today])
    entries = []
    for L in LANGS:
        write(PREFIX[L], build_home(L))
        write(PREFIX[L] + "insights/", build_insights(L))
        for a in ARTICLES:
            write(art_path(a, L), build_article(L, a))
        for i in range(len(WEEKS)):
            write(PREFIX[L] + ("news/" if i == 0 else "news/%s/" % WEEKS[i]["week"]), build_news(L, i))
        write(PREFIX[L] + "feed.xml", rss(L))
    latest_week = WEEKS[0]["week"] if WEEKS else newest_article
    entries.append((dict(PREFIX), max(latest_week, newest_article)))
    entries.append(({l: PREFIX[l] + "insights/" for l in LANGS}, newest_article))
    for a in ARTICLES:
        entries.append(({l: art_path(a, l) for l in LANGS}, a.get("updated") or iso_date(a.get("date"))))
    for i, w in enumerate(WEEKS):
        entries.append(({l: PREFIX[l] + ("news/" if i == 0 else "news/%s/" % w["week"]) for l in LANGS}, w["week"]))
    write("/sitemap.xml", sitemap(entries))
    write("/robots.txt", "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE)
    write("/llms.txt", llms_txt())
    write("/404.html", build_404())
    n = sum(len(fs) for _, _, fs in os.walk(OUT))
    print("Built %d files into %s" % (n, OUT))


if __name__ == "__main__":
    main()
