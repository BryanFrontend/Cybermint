"""Trace the supplied Cybermint logo PNG into layered vector paths.

Writes a JSON file of path data (in a 0..1254 coordinate space) per layer:
shadow, outline, fill, highlight.
"""
import json
import sys

import numpy as np
import potrace
from PIL import Image
from scipy import ndimage

src, out = sys.argv[1], sys.argv[2]
im = np.array(Image.open(src).convert("RGBA")).astype(int)
r, g, b, a = (im[..., i] for i in range(4))

solid = a > 128
shadow_px = solid & (g > 90) & (g < 175) & (r < 60) & (b < 130)
fill_px = solid & (g > 200) & (r < 140)
hi_px = solid & (r > 140) & (g > 225)

outline = solid & ~shadow_px
outline = ndimage.binary_closing(outline, iterations=2)
outline = ndimage.binary_fill_holes(outline) & solid | outline
fill = ndimage.binary_closing(fill_px | hi_px, iterations=2)
hi = ndimage.binary_opening(hi_px, iterations=1)


def trace(mask):
    bm = potrace.Bitmap(~mask)
    plist = bm.trace(turdsize=40, alphamax=1.0, opticurve=True, opttolerance=0.4)
    d = []
    for curve in plist:
        sp = curve.start_point
        d.append(f"M{sp.x:.1f} {sp.y:.1f}")
        for seg in curve.segments:
            if seg.is_corner:
                d.append(f"L{seg.c.x:.1f} {seg.c.y:.1f}L{seg.end_point.x:.1f} {seg.end_point.y:.1f}")
            else:
                d.append(
                    f"C{seg.c1.x:.1f} {seg.c1.y:.1f} {seg.c2.x:.1f} {seg.c2.y:.1f} "
                    f"{seg.end_point.x:.1f} {seg.end_point.y:.1f}"
                )
        d.append("Z")
    return "".join(d)


layers = {
    "shadow": trace(solid),
    "outline": trace(outline),
    "fill": trace(fill),
    "highlight": trace(hi),
}
ys, xs = np.where(solid)
layers["bbox"] = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
json.dump(layers, open(out, "w"))
print({k: len(v) for k, v in layers.items() if k != "bbox"}, layers["bbox"])
