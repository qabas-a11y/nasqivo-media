#!/usr/bin/env python3
"""Render safe, public NASQIVO marketing images from content/posts.json.

Outputs PNG 1080x1350; NO Instagram API, no secrets, no uploads to third parties.
"""
import json
import subprocess
import unicodedata
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, features

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 1080, 1350
BG = "#101820"
BG2 = "#182D35"
TEAL = "#26E9C5"
WHITE = "#F4F8F9"
MUTED = "#A7BBC2"
RTL_READY = features.check("raqm")

def font_path(family, fallback):
    try:
        value = subprocess.check_output(
            ["fc-match", "-f", "%{file}", family],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if value and Path(value).exists():
            return value
    except Exception:
        pass
    return fallback

AR_FONT = font_path("Noto Sans Arabic:style=Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
AR_REG = font_path("Noto Sans Arabic", AR_FONT)
EN_FONT = font_path("DejaVu Sans:style=Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")

def ft(size, bold=True, latin=False):
    return ImageFont.truetype(EN_FONT if latin else AR_FONT if bold else AR_REG, size)

def has_arabic(t):
    return any("\u0600" <= c <= "\u06ff" for c in t)

def render_text(draw, text, x, y, size=42, color=WHITE, bold=True, right=False, max_width=None):
    font = ft(size, bold=bold, latin=not has_arabic(text))
    rtl = has_arabic(text)
    def prepared(s):
        if rtl and not RTL_READY:
            import arabic_reshaper
            from bidi.algorithm import get_display
            return get_display(arabic_reshaper.reshape(s))
        return s
    shaped = prepared(text)
    kwargs = {"direction": "rtl"} if rtl and RTL_READY else {}
    def getwidth(f, s):
        return draw.textbbox((0, 0), s, font=f, **kwargs)[2]
    if max_width:
        while size > 24 and getwidth(font, shaped) > max_width:
            size -= 2
            font = ft(size, bold=bold, latin=not rtl)
    xval = x - getwidth(font, shaped) if right else x
    draw.text((xval, y), shaped, font=font, fill=color, **kwargs)
    return size

def background():
    im = Image.new("RGB", (WIDTH, HEIGHT), BG)
    d = ImageDraw.Draw(im)
    for y in range(HEIGHT):
        f = y / HEIGHT
        d.line([(0, y), (WIDTH, y)], fill=(int(13 + 4*f), int(22 + 8*f), int(29 + 8*f)))
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-180, -240, 380, 330), fill=(19, 214, 181, 75))
    gd.ellipse((850, 930, 1460, 1560), fill=(20, 208, 172, 55))
    glow = glow.filter(ImageFilter.GaussianBlur(130))
    im = Image.alpha_composite(im.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(im)
    d.polygon([(0, 0), (260, 0), (0, 260)], fill="#0F6E64")
    d.line([(0, 220), (220, 0)], fill=TEAL, width=3)
    for row in range(5):
        for col in range(5):
            d.ellipse((977 + 21*col, 74 + 21*row, 981 + 21*col, 78 + 21*row), fill="#28B9A6")
    return im

def logo(draw):
    # Original simplified N motif; not an imported third-party trademark.
    draw.polygon([(66, 58), (89, 58), (113, 95), (113, 143), (90, 143), (90, 105)], fill=TEAL)
    draw.polygon([(91, 58), (112, 58), (140, 101), (140, 58), (162, 58), (162, 143), (141, 143)], fill="#0F9C8D")
    render_text(draw, "NASQIVO", 195, 64, size=53, color=WHITE)
    draw.line((68, 163, 1010, 163), fill="#35616B", width=2)
    render_text(draw, "BUSINESS SYSTEMS  /  OMAN", 70, 185, size=19, color="#53E3CC")

def template_preview(draw):
    outer = (72, 443, 1008, 928)
    draw.rounded_rectangle(outer, radius=34, fill="#162A33", outline="#267A70", width=3)
    # Left: a stylized browser/webpage on a screen.
    draw.rounded_rectangle((100, 493, 511, 865), radius=23, fill="#243B45", outline="#4C8590", width=2)
    draw.rounded_rectangle((112, 505, 499, 852), radius=15, fill="#0F1E27")
    draw.rounded_rectangle((112, 505, 499, 554), radius=15, fill="#263D47")
    for i, col in enumerate(["#FB8B77", "#F4CD6A", "#53DBA9"]):
        draw.ellipse((133 + i*27, 525, 145+i*27, 537), fill=col)
    render_text(draw, "NASQIVO", 275, 518, size=19)
    # Browser content visualization: no fake client screenshots.
    draw.rounded_rectangle((131, 574, 480, 700), radius=18, fill="#204E4B")
    draw.polygon([(140, 690), (220, 614), (265, 657), (328, 596), (465, 689)], fill="#287B73")
    draw.ellipse((415, 601, 444, 630), fill="#6FE2C4")
    render_text(draw, "مشروعك", 467, 713, size=39, right=True, max_width=330)
    render_text(draw, "منتجات وخدمات في مكان واحد", 465, 769, size=22, color=MUTED, bold=False, right=True, max_width=330)
    draw.rounded_rectangle((126, 832, 483, 842), radius=5, fill="#237D75")
    # Phone bezel to communicate mobile support.
    draw.rounded_rectangle((86, 688, 185, 907), radius=21, fill="#070F16", outline="#6CA6AA", width=3)
    draw.rounded_rectangle((96, 707, 174, 892), radius=10, fill="#214E4B")
    draw.rounded_rectangle((115, 850, 153, 866), radius=8, fill=TEAL)

def features_panel(draw, items):
    items = items[:4]
    start_y = 526 if len(items) <= 4 else 508
    step = 87
    for index, item in enumerate(items):
        y = start_y + index * step
        draw.rounded_rectangle((549, y, 980, y+72), radius=18, fill="#0F242A", outline="#26AF9E", width=2)
        draw.rounded_rectangle((922, y+8, 971, y+64), radius=14, fill="#154B48")
        render_text(draw, str(index+1).zfill(2), 933, y+23, size=19, color=TEAL)
        display_item = item.replace("(موقع)", "كلمة موقع")
        render_text(draw, display_item, 908, y+19, size=27, right=True, max_width=320)

def make_one(post, out):
    im = background()
    d = ImageDraw.Draw(im)
    logo(d)
    render_text(d, post["headline"], 1005, 236, size=64, color=WHITE, right=True, max_width=930)
    render_text(d, post["subheading"], 999, 350, size=29, color="#75EEDB", right=True, max_width=920)
    style = post.get("style", "browser")
    if style == "list":
        d.rounded_rectangle((72, 443, 1008, 928), radius=34, fill="#162A33", outline="#267A70", width=3)
        for j, item in enumerate(post["features"][:4]):
            y = 480 + j * 106
            d.rounded_rectangle((104, y, 978, y + 84), radius=22, fill="#223D43" if j % 2 == 0 else "#11282F", outline="#2F736E", width=2)
            d.ellipse((126, y + 15, 183, y + 72), fill="#17564E")
            render_text(d, str(j + 1), 146, y + 29, size=25, color=TEAL)
            render_text(d, item, 930, y + 20, size=37, right=True, max_width=700)
    elif style == "question":
        d.rounded_rectangle((72, 443, 1008, 928), radius=34, fill="#172C38", outline="#267A70", width=3)
        d.ellipse((135, 555, 460, 880), fill="#144B49", outline=TEAL, width=4)
        d.text((233, 596), "?", font=ft(210, latin=True), fill=TEAL)
        features_panel(d, post["features"])
    else:
        template_preview(d)
        features_panel(d, post["features"])
    # Footer labels.
    d.rounded_rectangle((70, 969, 353, 1030), radius=20, fill="#153D3D", outline=TEAL, width=2)
    render_text(d, "GOOGLE SITES", 94, 983, size=24, color=WHITE)
    render_text(d, "مواقع واضحة وسهلة التعديل", 1008, 986, size=28, right=True, max_width=590)
    d.line((70, 1085, 1010, 1085), fill="#2F7B72", width=2)
    d.rounded_rectangle((69, 1135, 1010, 1250), radius=40, fill=TEAL)
    footer = post["footer"].replace("برسالة (موقع)", "برسالة موقع").replace("(موقع)", "كلمة موقع").replace("راسل NASQIVO وابدأ", "راسلنا وابدأ")
    render_text(d, footer, 957, 1168, size=39, color="#08242A", right=True, max_width=830)
    render_text(d, "@nasqivo", 74, 1296, size=22, color=MUTED)
    render_text(d, "تصميم توضيحي لا يمثل موقع عميل فعلي", 1008, 1298, size=18, color=MUTED, right=True, max_width=640)
    im.save(out, format="PNG", optimize=True)
    if post.get("format") == "STORY":
        story = Image.new("RGB", (1080, 1920), BG)
        sd = ImageDraw.Draw(story)
        sd.rounded_rectangle((42, 250, 1038, 1562), radius=36, fill="#173D3C", outline=TEAL, width=3)
        reduced = im.resize((960, 1200), Image.Resampling.LANCZOS)
        story.paste(reduced, (60, 293))
        render_text(sd, "NASQIVO", 72, 158, size=53, color=WHITE)
        render_text(sd, "OMAN / BUSINESS SYSTEMS", 72, 222, size=20, color=TEAL)
        sd.rounded_rectangle((67, 1608, 1013, 1757), radius=45, fill=TEAL)
        render_text(sd, "أرسل كلمة موقع بالخاص", 967, 1653, size=50, color="#09262B", right=True, max_width=845)
        render_text(sd, "@nasqivo", 76, 1810, size=31, color=MUTED)
        story.save(out, format="PNG", optimize=True)

def main():
    data = json.loads((ROOT / "content" / "posts.json").read_text(encoding="utf-8"))
    folder = ROOT / "media"
    folder.mkdir(parents=True, exist_ok=True)
    ids = set()
    for post in data["posts"]:
        key = post["id"]
        if key in ids or not key.startswith("post-") or "/" in key or ".." in key:
            raise ValueError("Invalid or repeated post ID")
        ids.add(key)
        target = folder / f"{key}.png"
        make_one(post, target)
        print(f"Rendered {target.relative_to(ROOT)} [{target.stat().st_size} bytes]")
    (folder / "README.md").write_text(
        "Public NASQIVO media generated from content/posts.json. No private files or secrets.\n",
        encoding="utf-8",
    )

if __name__ == "__main__":
    main()
