#!/usr/bin/env python3
"""Update the photo in the existing CV, preserving the 2-page body and hyperlinks."""
import sys
from io import BytesIO
from PIL import Image, ImageDraw
import fitz

old_pdf, portrait_file, out_pdf = sys.argv[1:4]
doc = fitz.open(old_pdf)
assert len(doc) == 2, "Unexpected CV page count"
page = doc[0]
assert abs(page.rect.width - 595.276) < 3 and abs(page.rect.height - 841.89) < 3, "Unexpected CV page size"
page.add_redact_annot(fitz.Rect(36, 24, 559, 105), fill=(1, 1, 1))
page.apply_redactions(images=0, graphics=0, text=0)
page.draw_rect(fitz.Rect(36, 19, 559, 109), color=None, fill=(1, 1, 1), overlay=True)
blue = (0.1059, 0.3333, 0.4863)
grey = (0.25, 0.28, 0.31)
lightblue = (0.76, 0.82, 0.88)
page.insert_text((41, 46), "Mahdi Mohammadigohari", fontname="hebo", fontsize=19.6, color=blue)
page.insert_text((41, 63), "Machine Learning Theory  |  Functional Analysis", fontname="hebo", fontsize=9.5, color=(0.13, 0.15, 0.17))
page.insert_text((41, 76), "Kernel and Optimization Geometry", fontname="hebo", fontsize=9.4, color=(0.13, 0.15, 0.17))
page.insert_text((41, 89), "Independent Researcher, Bolzano, Italy", fontname="helv", fontsize=8.4, color=grey)
links = [
    ("mahdi.mohammadigohari@gmail.com", "mailto:mahdi.mohammadigohari@gmail.com"),
    ("Google Scholar", "https://scholar.google.com/citations?hl=en&user=xywR8SAAAAAJ&view_op=list_works&sortby=pubdate"),
    ("ORCID", "https://orcid.org/0000-0002-4811-6585"),
    ("GitHub", "https://github.com/mmg1980CS"),
    ("LinkedIn", "https://www.linkedin.com/in/mahdi-mohammadigohari-659b0b254"),
]
x, baseline, fontsize = 41.0, 102.4, 7.6
for i, (label, url) in enumerate(links):
    width = fitz.get_text_length(label, fontname="helv", fontsize=fontsize)
    page.insert_text((x, baseline), label, fontsize=fontsize, fontname="helv", color=blue)
    page.insert_link({"kind": fitz.LINK_URI, "from": fitz.Rect(x, baseline - 8.6, x + width, baseline + 1), "uri": url})
    x += width
    if i + 1 < len(links):
        page.insert_text((x + 5, baseline), "|", fontsize=fontsize, fontname="helv", color=lightblue)
        x += 14
assert x < 463, "Header links collide with photo"
im = Image.open(portrait_file).convert("RGB")
width, height = im.size
side = min(width, height)
im = im.crop(((width - side)//2, (height - side)//2, (width + side)//2, (height + side)//2))
im = im.resize((450, 450), Image.Resampling.LANCZOS).convert("RGBA")
mask = Image.new("L", (450, 450), 0)
ImageDraw.Draw(mask).ellipse((0, 0, 449, 449), fill=255)
im.putalpha(mask)
buf = BytesIO()
im.save(buf, format="PNG", optimize=True)
page.insert_image(fitz.Rect(463, 18, 551, 106), stream=buf.getvalue(), keep_proportion=True, overlay=True)
page.draw_line((41, 109), (555, 109), color=lightblue, width=0.55, overlay=True)
doc.save(out_pdf, garbage=4, deflate=True)
print("Updated two-page CV:", out_pdf)
