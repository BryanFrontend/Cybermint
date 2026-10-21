"""Small SVG kit: palette, outlined text via HarfBuzz + fontTools, primitives.

Text is converted to outlines so artwork renders identically on GitHub for
every viewer. Each glyph is stored once in <defs> and placed with <use>.
"""
import json
from html import escape

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

# Palette
INK = "#0C0C0E"
PANEL = "#141518"
PANEL2 = "#1B1D21"
LINE = "#2C2F34"
GRAY = "#8A9096"
GRAY_D = "#5D636A"
MINT = "#2AF7BC"
MINT_D = "#038559"
PALE = "#BBF9E6"
WHITE = "#F4F1EA"

import os

F = os.environ.get("CYBERMINT_INTER_DIR", "/usr/share/fonts/opentype/inter").rstrip("/") + "/"
DV = os.environ.get("CYBERMINT_DEJAVU_DIR", "/usr/share/fonts/truetype/dejavu").rstrip("/") + "/"
FONTS = {
    "black": F + "InterDisplay-Black.otf",
    "xbold": F + "InterDisplay-ExtraBold.otf",
    "bold": F + "InterDisplay-Bold.otf",
    "semi": F + "InterDisplay-SemiBold.otf",
    "med": F + "Inter-Medium.otf",
    "reg": F + "Inter-Regular.otf",
    "mono": DV + "DejaVuSansMono.ttf",
    "monob": DV + "DejaVuSansMono-Bold.ttf",
}


class Font:
    def __init__(self, key, path):
        self.key = key
        blob = hb.Blob.from_file_path(path)
        self.hbfont = hb.Font(hb.Face(blob))
        self.tt = TTFont(path)
        self.upem = self.tt["head"].unitsPerEm
        self.glyphset = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()

    def shape(self, text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hbfont, buf, {"kern": True, "liga": False})
        return [(i.codepoint, p.x_advance, p.x_offset, p.y_offset)
                for i, p in zip(buf.glyph_infos, buf.glyph_positions)]

    def glyph_d(self, gid):
        pen = SVGPathPen(self.glyphset)
        self.glyphset[self.order[gid]].draw(pen)
        return pen.getCommands()


_fonts = {}


def font(key):
    if key not in _fonts:
        _fonts[key] = Font(key, FONTS[key])
    return _fonts[key]


class Doc:
    def __init__(self, w, h, title, desc):
        self.w, self.h = w, h
        self.title, self.desc = title, desc
        self.body = []
        self.used = {}  # (fontkey, gid) -> d
        self.texts = []  # bboxes for overlap checks

    def add(self, s):
        self.body.append(s)

    # ---------- text ----------
    def measure(self, text, size, fk="med", track=0):
        f = font(fk)
        adv = sum(a for _, a, _, _ in f.shape(text))
        return adv * size / f.upem + track * max(len(text) - 1, 0)

    def text(self, text, x, y, size, fk="med", fill=WHITE, anchor="start", track=0, opacity=None):
        f = font(fk)
        w = self.measure(text, size, fk, track)
        if anchor == "middle":
            x -= w / 2
        elif anchor == "end":
            x -= w
        s = size / f.upem
        pen_x = 0.0
        uses = []
        for gid, adv, xo, yo in f.shape(text):
            if self.used.setdefault((fk, gid), None) is None:
                self.used[(fk, gid)] = f.glyph_d(gid)
            if self.used[(fk, gid)]:
                uses.append(f'<use href="#{fk}{gid}" x="{(pen_x + xo):.0f}"/>')
            pen_x += adv + track / s
        op = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<g fill="{fill}"{op} transform="translate({x:.1f} {y:.1f}) scale({s:.5f} {-s:.5f})">{"".join(uses)}</g>')
        self.texts.append((text, x, y - size * 0.75, w, size))
        return w

    def wrap(self, text, width, size, fk="med"):
        words, lines, cur = text.split(), [], ""
        for wd in words:
            t = (cur + " " + wd).strip()
            if self.measure(t, size, fk) <= width or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def para(self, text, x, y, width, size, fk="reg", fill=GRAY, lh=1.42, anchor="start"):
        lines = self.wrap(text, width, size, fk)
        for i, ln in enumerate(lines):
            w = self.measure(ln, size, fk)
            assert w <= width + 0.5, (ln, w, width)
            self.text(ln, x, y + i * size * lh, size, fk, fill, anchor)
        return len(lines) * size * lh

    def fit(self, text, width, size, fk):
        w = self.measure(text, size, fk)
        assert w <= width, f"overflow: {text!r} {w:.0f} > {width:.0f}"

    # ---------- shapes ----------
    def rect(self, x, y, w, h, rx=0, fill="none", stroke=None, sw=0, dash=None, opacity=None):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        da = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{st}{da}{op}/>')

    def line(self, x1, y1, x2, y2, stroke=GRAY, sw=2, dash=None, cap="round", opacity=None):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="{cap}"{da}{op}/>')

    def path(self, d, fill="none", stroke=None, sw=0, dash=None, join="round", cap="round", opacity=None):
        st = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="{join}" stroke-linecap="{cap}"' if stroke else ""
        da = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<path d="{d}" fill="{fill}"{st}{da}{op}/>')

    def circle(self, cx, cy, r, fill="none", stroke=None, sw=0, dash=None, opacity=None):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        da = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity is not None else ""
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"{st}{da}{op}/>')

    def arrow(self, pts, stroke=MINT, sw=3, dash=None, head=10):
        d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
        self.path(d, stroke=stroke, sw=sw, dash=dash)
        (x1, y1), (x2, y2) = pts[-2], pts[-1]
        import math
        a = math.atan2(y2 - y1, x2 - x1)
        p1 = (x2 - head * math.cos(a - 0.45), y2 - head * math.sin(a - 0.45))
        p2 = (x2 - head * math.cos(a + 0.45), y2 - head * math.sin(a + 0.45))
        self.path(f"M{p1[0]:.1f} {p1[1]:.1f} L{x2:.1f} {y2:.1f} L{p2[0]:.1f} {p2[1]:.1f}", stroke=stroke, sw=sw)

    def card(self, x, y, w, h, fill=WHITE, shadow=MINT_D, off=8, rx=18, stroke=INK, sw=4):
        if shadow:
            self.rect(x + off, y + off, w, h, rx, fill=shadow)
        self.rect(x, y, w, h, rx, fill=fill, stroke=stroke, sw=sw)

    def logo(self, cx, cy, height):
        L = json.load(open(LOGO_JSON))
        x0, y0, x1, y1 = L["bbox"]
        s = height / (y1 - y0)
        tx = cx - (x0 + x1) / 2 * s
        ty = cy - (y0 + y1) / 2 * s
        self.add(f'<g transform="translate({tx:.1f} {ty:.1f}) scale({s:.5f})">'
                 f'<path d="{L["shadow"]}" fill="{MINT_D}"/>'
                 f'<path d="{L["outline"]}" fill="{INK}"/>'
                 f'<path d="{L["fill"]}" fill="{MINT}"/>'
                 f'<path d="{L["highlight"]}" fill="{PALE}"/></g>')

    def render(self):
        defs = "".join(f'<path id="{fk}{gid}" d="{d}"/>' for (fk, gid), d in self.used.items() if d)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
            f'width="{self.w}" height="{self.h}" role="img" aria-labelledby="t d">'
            f'<title id="t">{escape(self.title)}</title><desc id="d">{escape(self.desc)}</desc>'
            f'<defs>{defs}</defs>' + "".join(self.body) + "</svg>\n"
        )

    def save(self, path):
        open(path, "w").write(self.render())


LOGO_JSON = None
