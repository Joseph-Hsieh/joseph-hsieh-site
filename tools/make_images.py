#!/usr/bin/env python3
"""Regenerate social-share (OG) images. Needs Pillow and Noto Sans CJK fonts.

Run locally after adding or retitling an article:  python3 tools/make_images.py
The generated JPGs are committed, so the Cloudflare build itself needs no Pillow.
"""
import json, os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, "data/site.json"), encoding="utf-8"))
P = D["profile"]
CJK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
CJK_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc"
if not os.path.exists(CJK_R):
    CJK_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
IDX = {"zh": 3, "ja": 0, "en": 3}  # TC / JP face index inside the .ttc
INK, ORANGE, BG, MUTED = (17, 17, 17), (253, 105, 37), (255, 255, 255), (107, 107, 107)
photo = Image.open(os.path.join(ROOT, P["photo"].lstrip("/"))).convert("RGB")


def font(path, size, L):
    return ImageFont.truetype(path, size, index=IDX[L])


def wrap(draw, text, f, width):
    out, cur = [], ""
    latin = all(ord(c) < 0x3000 for c in text)
    tokens = text.split(" ") if latin else list(text)
    for tok in tokens:
        cand = (cur + " " + tok).strip() if latin else cur + tok
        if draw.textlength(cand, font=f) <= width:
            cur = cand
        else:
            out.append(cur); cur = tok
    if cur:
        out.append(cur)
    return out


def card(L, kicker, title, sub, dest):
    im = Image.new("RGB", (1200, 630), BG)
    ph = photo.resize((504, 630))
    im.paste(ph, (696, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([696, 612, 1200, 630], fill=ORANGE)
    d.text((64, 64), kicker, font=font(CJK_R, 24, L), fill=MUTED)
    size = 60 if len(title) < 30 else 50
    f = font(CJK, size, L)
    y = 120
    for ln in wrap(d, title, f, 580)[:4]:
        d.text((64, y), ln, font=f, fill=INK); y += int(size * 1.3)
    d.rectangle([64, y + 18, 224, y + 30], fill=ORANGE)
    fs = font(CJK_R, 26, L)
    y += 60
    for ln in wrap(d, sub, fs, 580)[:3]:
        d.text((64, y), ln, font=fs, fill=MUTED); y += 38
    d.text((64, 552), "joseph-hsieh.com", font=font(CJK, 24, L), fill=INK)
    im.save(os.path.join(ROOT, dest), quality=86, optimize=True, progressive=True)


def T(o, k, L):
    return o.get(k) if L == "zh" else (o.get(k + "_" + L) or o.get(k))


NAME = {"zh": P["name_zh"] + "  " + P["name_en"], "en": P["name_en"], "ja": P["name_zh"] + "  " + P["name_en"]}
HEAD = {"zh": P.get("headline", "").replace("\n", ""), "en": P.get("headline_en", "").replace("\n", " "), "ja": P.get("headline_ja", "").replace("\n", "")}
TAGS = {L: (T(P, "tags", L) or "").replace("、", " · ").replace(", ", " · ") for L in ("zh", "en", "ja")}
for L in ("zh", "en", "ja"):
    card(L, NAME[L], HEAD[L], TAGS[L], "assets/og-%s.jpg" % L)
    for a in D["articles"]:
        card(L, NAME[L], T(a, "title", L), T(a, "subtitle", L) or "", "assets/og/%s-%s.jpg" % (a["slug"], L))

icon = photo.crop((140, 120, 760, 740)).resize((180, 180))
icon.save(os.path.join(ROOT, "assets/apple-touch-icon.png"))
print("images done")
