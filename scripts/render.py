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


def campaign_one(post, out):
    """Nine distinct editorial layouts; preserve existing POST/STORY formats."""
    n = int(post["id"].split("-")[1])
    story = post.get("format") == "STORY"
    h = 1920 if story else 1350
    im = Image.new("RGB", (1080,h), "#10242A")
    d = ImageDraw.Draw(im)
    # Story-safe layout: 250 px top and bottom, same logical canvas.
    if story:
        canvas = Image.new("RGB", (1080,1350), "#10242A")
        d = ImageDraw.Draw(canvas)
    else:
        canvas = im
    dark="#10242A"; ink="#102D33"; mint="#26E9C5"; ivory="#F4F5EE"
    light = n in (2,5,7,8)
    bg = ivory if light else dark
    fg = ink if light else ivory
    muted = "#42625F" if light else "#A7CBC5"
    d.rectangle((0,0,1080,1350),fill=bg)
    def rr(box,fill,outline=None,r=28,w=2):
        d.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=w)
    def t(s,x,y,sz=42,c=None,right=True,mw=900,bold=True):
        render_text(d,s,x,y,size=sz,color=c or fg,right=right,max_width=mw,bold=bold)
    def line(a,b,c=mint,w=3): d.line((a,b),fill=c,width=w)
    def brand():
        t("NASQIVO",68,54,38,right=False)
        t("WEB STUDIO / OMAN",70,111,17,c=muted,right=False)
        d.rectangle((963,65,1010,112),fill=mint)
        t("N",974,68,29,c=ink,right=False)
    def heading(y=182):
        t(post["headline"],1010,y,69,mw=940)
        t(post["subheading"],1010,y+110,34,c=muted,mw=940)
    def footer():
        line((68,1133),(1012,1133),muted,2)
        t(post["footer"],1010,1160,44,mw=940)
        t("@nasqivo",68,1270,24,c=muted,right=False)
        t("محتوى ترويجي • ناسكيفو",1010,1270,22,c=muted,mw=690)
    def browser(box, theme, label, kind):
        x,y,X,Y=box
        rr(box,"#FFFFFF","#C8D7D1",r=25,w=2)
        rr((x+12,y+12,X-12,y+58),"#E4EBE7",r=12)
        for j,col in enumerate(("#E5A18D","#E9C676","#79BDA6")):
            d.ellipse((x+26+j*22,y+28,x+38+j*22,y+40),fill=col)
        t(label,X-32,y+76,33,c=ink,mw=X-x-64)
        d.rectangle((x+22,y+143,X-22,y+265),fill=theme)
        if kind=="cake":
            cx=(x+X)//2
            rr((cx-65,y+200,cx+65,y+250),"#F9DDC1",r=10)
            rr((cx-48,y+166,cx+48,y+204),"#FFEAD8",r=10)
            d.ellipse((cx-8,y+154,cx+8,y+170),fill="#B9636B")
        elif kind=="perfume":
            cx=(x+X)//2
            rr((cx-39,y+180,cx+39,y+249),"#CFAD69",r=11)
            d.rectangle((cx-20,y+159,cx+20,y+184),fill="#322D2A")
            d.rectangle((cx-27,y+199,cx+27,y+233),fill="#F5E6BE")
        elif kind=="coffee":
            cx=(x+X)//2
            d.ellipse((cx-80,y+226,cx+80,y+250),fill="#CFB594")
            rr((cx-48,y+179,cx+48,y+233),"#F7E4C8",r=20)
            d.arc((cx+26,y+179,cx+78,y+230),0,270,fill="#F7E4C8",width=9)
        else:
            for j in range(3): rr((x+38+j*(X-x-76)//3,y+172,x+78+j*(X-x-76)//3,y+236),"#72D6B9",r=9)
        for j in range(3):
            yy=y+290+j*42
            if yy+14<Y-20: rr((x+26,yy,X-26-j*35,yy+12),"#D6E3DD",r=5)
    brand()
    if n==1:
        heading()
        # Monumental browser hero, no repeated four-box panel.
        rr((69,432,1011,1048),"#1E514F",r=45)
        for i in range(5):
            d.arc((95+i*35,447+i*35,985-i*35,1040-i*35),185,355,fill="#32726A",width=2)
        browser((145,501,933,975),"#1E7769","مشروعك على الويب","generic")
        rr((750,932,980,1013),mint,r=18)
        t("موقع تعريفي",956,946,30,c=ink,mw=190)
    elif n==2:
        heading()
        # Before/after: scattered messages versus structured content.
        for x,label,col in [(69,"قبل","#E5DED4"),(552,"بعد","#D5EEE3")]:
            rr((x,425,x+460,1050),col,r=30)
            t(label,x+420,455,46,c=ink,mw=380)
        for j,s in enumerate(["كم السعر؟","وين الصور؟","كيف أطلب؟"]):
            x=95+(j%2)*50; y=565+j*135
            rr((x,y,x+335,y+100),"#FFFFFF",r=20)
            t(s,x+311,y+20,35,c=ink,mw=285)
        for j,s in enumerate(["المنتجات","الأسعار","طريقة الطلب"]):
            y=555+j*135
            rr((583,y,981,y+99),"#FFFFFF",r=14)
            d.ellipse((600,y+34,628,y+62),fill="#159C78")
            t(s,955,y+18,34,c=ink,mw=305)
        t("تصوّر توضيحي",1010,1060,24,c=muted)
    elif n==3:
        heading()
        # Vertical editorial timeline, large numbers and alternating text.
        line((910,450),(910,1045),"#367870",5)
        for j,s in enumerate(post["features"][:4]):
            y=455+j*155
            d.ellipse((856,y,964,y+108),fill=mint)
            t(str(j+1),885,y+13,52,c=ink,right=False)
            t(s,820,y+23,46,mw=720)
            line((70,y+119),(820,y+119),"#315853",2)
    elif n==4:
        heading()
        # Isometric-style layered information tiles converge into one link.
        for j,s in enumerate(post["features"][:4]):
            x=100+j*190; y=470+(j%2)*70
            d.polygon([(x,y+50),(x+145,y),(x+230,y+45),(x+85,y+95)],fill="#42BBA2")
            d.polygon([(x,y+50),(x+85,y+95),(x+85,y+145),(x,y+100)],fill="#17665E")
            d.polygon([(x+85,y+95),(x+230,y+45),(x+230,y+95),(x+85,y+145)],fill="#258F80")
            t(s,x+218,y+150,30,mw=225)
            line((x+115,y+185),(540,846),"#397E73",4)
        rr((175,842,905,1019),mint,r=72)
        d.ellipse((222,886,310,974),outline=ink,width=8)
        d.ellipse((280,886,368,974),outline=ink,width=8)
        t("رابط مشروعك",860,885,52,c=ink,mw=480)
    elif n in (5,6,7):
        heading()
        themes={5:("#F2C6AB","حلويات منزلية","cake"),6:("#383033","متجر عطور","perfume"),7:("#96755A","مقهى محلي","coffee")}
        col,label,kind=themes[n]
        if n==5:
            rr((67,421,1013,1065),"#E9D2BF",r=44)
            browser((105,466,695,1021),col,label,kind)
            for j,s in enumerate(post["features"][:3]): t(s,977,565+j*128,32,c=ink,mw=252)
        elif n==6:
            rr((68,425,1012,1060),"#443B32",r=38)
            for j in range(7): d.line((75+j*145,433,75+j*145,1052),fill="#655440",width=2)
            browser((235,450,844,1029),col,label,kind)
            rr((80,842,300,953),"#C9AC76",r=18)
            t("كتالوج رقمي",288,865,26,c=ink,mw=196)
        else:
            rr((69,420,1011,1056),"#DCC7AD",r=33)
            browser((392,452,968,1022),col,label,kind)
            for j,s in enumerate(post["features"][:3]):
                y=540+j*150
                rr((95,y,370,y+113),"#F8F0E5",r=16)
                t(s,351,y+25,31,c=ink,mw=235)
        t("نموذج تخيلي وليس عملاً لعميل",1010,1065,23,c=muted)
    elif n==8:
        heading()
        # FAQ problem/solution, alternating customer and site responses.
        for j,(q,a) in enumerate([("متى تفتحون؟","ساعات العمل"),("وين مكانكم؟","موقع النشاط"),("كيف أتواصل؟","طرق التواصل")]):
            y=425+j*215
            rr((380,y,1010,y+91),"#E4DED5",r=24)
            t(q,981,y+15,39,c=ink,mw=565)
            rr((68,y+105,680,y+196),"#C6E9DB",r=24)
            t(a,650,y+120,36,c=ink,mw=550)
    else:
        # Typographic direct-response poster with prominent message.
        d.ellipse((20,240,1060,1280),outline="#255951",width=3)
        d.ellipse((90,310,990,1210),outline="#255951",width=3)
        t("ابدأ",1010,238,164,c=mint,mw=940)
        t("موقع مشروعك",1010,454,100,mw=940)
        t(post["subheading"],1010,650,43,c=muted,mw=940)
        rr((68,820,1012,1030),mint,r=36)
        t("ناقش فكرتك معنا",970,880,67,c=ink,mw=860)
    footer()
    if story:
        im.paste(canvas,(0,285))
    canvas_out=im if story else canvas
    canvas_out.save(out,format="PNG",optimize=True)


def make_one(post, out):
    if post['id'] in {f'post-{i:02d}' for i in range(1,10)}:
        return campaign_one(post, out)
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
