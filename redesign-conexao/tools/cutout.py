"""Remove the studio backdrop from product and kit renders, deterministically.

Usage: python -I tools/cutout.py   (run from redesign-conexao/)
Downloads every product/kit render referenced by the pages into data/img-src/,
writes transparent WebP files to assets/img/ and data/cutouts.json (remote url -> local path).
Exit 1 if any image fails or keeps less than 0.5% / more than 90% of its pixels.

Method: the renders sit on a dark, saturated backdrop (navy radial gradient, one green).
A pixel is "backdrop-like" when it is dark and dominated by the backdrop hue. Only the
backdrop-like region connected to the image border is removed, so dark details inside
the product survive. Edges are feathered and de-tinted to avoid a blue halo.
"""
import glob
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from io import BytesIO

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'data', 'img-src')
OUT = os.path.join(ROOT, 'assets', 'img')
MAP = os.path.join(ROOT, 'data', 'cutouts.json')
UP = 'https://www.conexao.com.br/wp-content/uploads/'
SKIP = re.compile(r'logo|Biblioteca|Conexao_Empresa|thumb_post|Exocad|FRESAGEM|cropped|Icon-|Splash', re.I)


def referenced_images():
    urls = set()
    for f in glob.glob(os.path.join(ROOT, '*.html')):
        src = open(f, encoding='utf-8').read()
        urls.update(re.findall(r'https://www\.conexao\.com\.br/wp-content/uploads/[^"\' )]+?\.(?:webp|png|jpe?g)', src))
    return sorted(u for u in urls if not SKIP.search(u))


def fetch(url):
    name = url[len(UP):].replace('/', '_')
    path = os.path.join(SRC, name)
    if not os.path.exists(path):
        req = urllib.request.Request(urllib.parse.quote(url, safe=':/'), headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            open(path, 'wb').write(r.read())
    return path, name


def light_backdrop(img):
    """Technical diagrams sit on white or pale paper and need no cutout."""
    a = np.asarray(img.convert('L')).astype(np.float32)
    border = np.concatenate([a[:4].ravel(), a[-4:].ravel(), a[:, :4].ravel(), a[:, -4:].ravel()])
    return float(np.median(border)) > 180


def cutout(img):
    rgb = np.asarray(img.convert('RGB')).astype(np.float32)
    h, w, _ = rgb.shape
    border = np.concatenate([rgb[:4].reshape(-1, 3), rgb[-4:].reshape(-1, 3), rgb[:, :4].reshape(-1, 3), rgb[:, -4:].reshape(-1, 3)])
    # backdrop hue = channel that dominates the brightest border pixels (gradient glow)
    bright = border[border.sum(1) >= np.percentile(border.sum(1), 60)]
    hue = int(np.argmax(bright.mean(0)))
    others = [c for c in range(3) if c != hue]
    lum = rgb @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    dom = rgb[..., hue] - rgb[..., others].max(-1)
    chroma = rgb.max(-1) - rgb.min(-1)
    backdrop = ((lum < 34) | ((lum < 52) & (chroma < 24)) | ((dom > 12) & (lum < 125) & (chroma > 18)))
    backdrop = ndimage.binary_opening(backdrop, iterations=1)
    labels, _ = ndimage.label(backdrop)
    edge_labels = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
    bg = np.isin(labels, edge_labels[edge_labels > 0])
    fg = ~bg
    # keep sizeable foreground parts, drop speckles left in the gradient
    flab, n = ndimage.label(fg)
    if n:
        sizes = ndimage.sum(fg, flab, range(1, n + 1))
        fg = np.isin(flab, 1 + np.flatnonzero(sizes >= max(60, 0.0015 * h * w)))
    raw_fg = fg.copy()
    # thread valleys are shaded in the backdrop hue and leak into it: close the silhouette
    r = max(3, int(0.03 * min(h, w)))
    yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
    fg = ndimage.binary_fill_holes(ndimage.binary_closing(fg, structure=(xx * xx + yy * yy) <= r * r, iterations=1))
    # implants are row-convex columns: fill each row between its outermost pixels
    clab, cn = ndimage.label(fg)
    for k, sl in enumerate(ndimage.find_objects(clab), 1):
        ch, cw = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if ch > 1.25 * cw:
            sub = clab[sl] == k
            cols = np.arange(cw)
            for row in range(ch):
                hit = cols[sub[row]]
                if hit.size:
                    sub[row, hit[0]:hit[-1] + 1] = True
            fg[sl] |= sub
    # never recover near-black pixels: those are backdrop seen between neighbouring parts
    fg = raw_fg | (fg & (lum >= 28))
    alpha = ndimage.gaussian_filter(fg.astype(np.float32), 0.9)
    alpha = np.clip((alpha - 0.15) / 0.7, 0, 1)
    out = rgb.copy()
    gray = lum[..., None].repeat(3, -1)
    # recovered valley pixels: keep their shading, drop the backdrop tint
    filled = fg & ~raw_fg
    out[filled] = gray[filled] * 1.15
    # de-tint semi-transparent edge pixels: pull the backdrop hue back to neutral
    edge = (alpha > 0) & (alpha < 0.98)
    neutral = out[..., others].mean(-1)
    out[..., hue] = np.where(edge, np.minimum(out[..., hue], neutral + 6), out[..., hue])
    rgba = np.dstack([np.clip(out, 0, 255), alpha * 255]).astype(np.uint8)
    res = Image.fromarray(rgba, 'RGBA')
    bbox = res.getbbox()
    if bbox:
        pad = int(0.04 * max(w, h))
        bbox = (max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(w, bbox[2] + pad), min(h, bbox[3] + pad))
        res = res.crop(bbox)
    return res, float(fg.mean())


def main():
    os.makedirs(SRC, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    # pages are localized after a run, so keep earlier entries instead of starting empty
    mapping = json.load(open(MAP, encoding='utf-8')) if os.path.exists(MAP) else {}
    errors = []
    for url in referenced_images():
        try:
            path, name = fetch(url)
            img = Image.open(path)
            if light_backdrop(img):
                print('%-70s light backdrop, kept as is' % name[:70])
                continue
            res, cover = cutout(img)
        except Exception as ex:  # network or decode failure: report, do not hide
            errors.append('%s: %s' % (url, ex))
            continue
        if not 0.005 <= cover <= 0.90:
            errors.append('%s: implausible foreground coverage %.2f' % (url, cover))
            continue
        local = 'assets/img/' + os.path.splitext(name)[0] + '.webp'
        res.save(os.path.join(ROOT, local), 'WEBP', quality=90, method=6)
        mapping[url] = local
        print('%-70s fg=%.2f %s' % (name[:70], cover, res.size))
    json.dump(mapping, open(MAP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        sys.exit(1)
    print('ok: %d cutouts' % len(mapping))


if __name__ == '__main__':
    main()
