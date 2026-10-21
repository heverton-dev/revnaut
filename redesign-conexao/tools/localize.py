"""Point every page at the transparent cutouts produced by tools/cutout.py.

Usage: python -I tools/localize.py   (pipeline: extract -> build -> cutout -> localize)
Replaces remote render URLs with local assets/img paths in all *.html. Exit 1 if a mapped file is missing.
"""
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UP = 'https://www.conexao.com.br/wp-content/uploads/'
# the Zigomatico thumbnail render carries a dark mount that cannot be separated cleanly
OVERRIDES = {UP + '2025/05/Zigomatico.webp': 'assets/img/2025_07_ZIGOFLAT®-Hexagono-Externo-RD.webp'}


def main():
    mapping = json.load(open(os.path.join(ROOT, 'data', 'cutouts.json'), encoding='utf-8'))
    mapping.update(OVERRIDES)
    missing = sorted({p for p in mapping.values() if not os.path.exists(os.path.join(ROOT, p))})
    if missing:
        print('missing cutouts: %s' % missing, file=sys.stderr)
        sys.exit(1)
    total = 0
    for f in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
        src = open(f, encoding='utf-8').read()
        n = 0
        for remote, local in mapping.items():
            n += src.count(remote)
            src = src.replace(remote, local)
        if n:
            open(f, 'w', encoding='utf-8').write(src)
        total += n
    print('ok: %d image references localized' % total)


if __name__ == '__main__':
    main()
