"""Deterministic extraction of conexao.com.br product pages into data/catalogo.json.

Usage: python -I tools/extract.py   (run from redesign-conexao/)
Reads data/raw/p_<slug>.html, writes data/catalogo.json. Exit 1 on any page it cannot parse.
"""
import glob
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data', 'raw')
OUT = os.path.join(ROOT, 'data', 'catalogo.json')

# assets referenced by the site chrome on every page, not by the product itself
CHROME = re.compile(
    r'2025/05/|2025/09/Kit_Expertguide\.webp|2025/09/Conexao_Empresa|cropped-favicon|Icon-|SplashScreen'
    r'|BibliotecaDigital|Conexao-LGPD|Biblioteca-Digital\.pdf|\\u00')
DIAM = re.compile(r'^⌀\s*(\d+(?:[.,]\d+)?)\s*mm$')


def text_lines(src):
    s = re.sub(r'(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>', ' ', src)
    m = re.search(r'(?is)<body.*', s)
    s = m.group(0) if m else s
    s = re.sub(r'(?i)<br\s*/?>', '\n', s)
    t = html.unescape(re.sub(r'(?s)<[^>]+>', '\n', s))
    lines = [re.sub(r'\s+', ' ', l).strip() for l in t.split('\n')]
    lines = [l.replace('Instalaçãо', 'Instalação') for l in lines if l]
    end = next((i for i, l in enumerate(lines) if l.startswith('Líder em soluções')), len(lines))
    return lines[:end]


def uploads(src, exts):
    out = []
    for u in re.findall(r'https://www\.conexao\.com\.br/wp-content/uploads/[^"\' )]+?\.(?:%s)' % exts, src):
        if re.search(r'-\d+x\d+\.', u) or CHROME.search(u) or u in out:
            continue
        out.append(u)
    return out


def norm_num(v):
    return v.replace(',', '.')


def join_fragments(parts):
    s = ' '.join(parts)
    s = re.sub(r'\s+([.,:!])', r'\1', s)
    return s.strip()


def body_after_title(lines, title):
    idx = [i for i, l in enumerate(lines) if l == title]
    if len(idx) < 2:
        raise ValueError('title not found twice: %s' % title)
    return lines[idx[1] + 1:]


def take_until(lines, i, stops):
    out = []
    while i < len(lines) and not any(lines[i].startswith(s) for s in stops):
        out.append(lines[i])
        i += 1
    return out, i


def merge_colon(items):
    merged = []
    for it in items:
        if it in (':',):
            continue
        if it.startswith(':') and merged:
            merged[-1] = merged[-1] + ': ' + it[1:].strip()
        else:
            merged.append(it)
    out = []
    for it in merged:
        # one source line glues two bullets together
        out.extend(p.strip() for p in re.split(r'(?<=implante) (?=Espiras)', it))
    return [o.replace('aumentar a óssea', 'aumentar a espessura óssea') for o in out]


def parse_dimensions(block):
    dims, cur = [], None
    for l in block:
        m = DIAM.match(l)
        if m:
            cur = {'d': norm_num(m.group(1)), 'lengths': []}
            dims.append(cur)
        elif cur is not None and re.search(r'\d\s*mm', l):
            cur['lengths'] = [x.strip() for x in re.split(r'\s+–\s+', l) if x.strip()]
    return dims


def parse_drill_table(lines, i):
    i += 1  # 'Fresagem'
    if i < len(lines) and lines[i].startswith('Densidade'):
        i += 1
    head = []
    while i < len(lines) and lines[i].startswith('⌀'):
        head.append(norm_num(lines[i].lstrip('⌀')))
        i += 1
    rows = []
    while i < len(lines) and lines[i].startswith('Osso'):
        name, i = lines[i], i + 1
        cells = []
        while i < len(lines) and not lines[i].startswith('Osso') and not lines[i].startswith('Fresagem'):
            v = lines[i]
            if v.startswith('(') and cells:
                cells[-1]['alt'] = v
            else:
                cells.append({'v': v})
            i += 1
        rows.append({'name': name, 'cells': cells})
    if not head or not rows or any(len(r['cells']) != len(head) for r in rows):
        raise ValueError('drill table malformed')
    return {'head': head, 'rows': rows}


def parse_implant(body):
    stops = ('Tecnologia', 'Características')
    lede, i = take_until(body, 0, stops)
    p = {'kind': 'implant', 'lede': join_fragments(lede), 'tech': None}
    if body[i] == 'Tecnologia':
        p['tech'] = {'name': body[i + 1], 'spec': body[i + 2]}
        i += 3
    i += 1  # 'Características'
    feats, i = take_until(body, i, ('*Torque',))
    p['features'] = merge_colon(feats)
    p['torque'] = body[i + 1].replace('N.cm', ' N.cm')
    i += 2
    if body[i].startswith('Baixar'):
        p['leaflet_label'] = body[i].replace('Baixar ', '')
        i += 1
    i += 1  # 'Dimensões'
    dim_block, i = take_until(body, i, ('Principais Indica', 'Fresagem'))
    # Flex Gold lists benefit pairs right after the dimensions
    cut = next((k for k, l in enumerate(dim_block) if not (DIAM.match(l) or l in ('Comprimentos', ':') or re.search(r'\d\s*mm', l))), len(dim_block))
    p['dimensions'] = parse_dimensions(dim_block[:cut])
    p['benefits_raw'] = dim_block[cut:]
    p['indications'] = []
    if i < len(body) and body[i].startswith('Principais Indica'):
        p['indications'], i = take_until(body, i + 1, ('Fresagem',))
    p['drill'] = parse_drill_table(body, i) if i < len(body) and body[i] == 'Fresagem' else None
    if not p['dimensions']:
        raise ValueError('no dimensions')
    return p


KIT_LABELS = ('Implantes', 'Sistemas', 'Diâmetros', 'Características')


def parse_kit(body):
    head, i = take_until(body, 0, ('*Código', '* Código', 'Baixar'))
    k = {'kind': 'kit', 'facts': {}, 'features': [], 'paragraphs': [], 'code': None, 'composition': []}
    label = None
    for l in head:
        if l in KIT_LABELS:
            label = l
            if l != 'Características':
                k['facts'][l] = []
            continue
        if label == 'Características':
            k['features'].append(l)
        elif label and len(l) < 70:
            k['facts'][label].append(l.lstrip(':–- ').strip())
        else:
            label = None
            k['paragraphs'].append(l)
    for f in k['facts']:
        k['facts'][f] = join_fragments([v for v in k['facts'][f] if v]).replace(' – ', ', ').strip(' –-')
    m = re.search(r'(\d{6,})', ' '.join(body[i:i + 2]))
    if body[i].startswith('*') and 'Código' in body[i]:
        k['code'] = m.group(1) if m else None
        i += 1 if (m and m.group(1) in body[i]) else 2
    if i < len(body) and body[i].startswith('Baixar'):
        k['leaflet_label'] = body[i].replace('Baixar ', '')
        i += 1
    if i < len(body) and body[i].startswith('COMPOSIÇÃO'):
        i += 1
        while i + 1 < len(body) and re.fullmatch(r'\d{5,}', body[i]):
            k['composition'].append({'code': body[i], 'name': body[i + 1]})
            i += 2
    k['notes'] = [l for l in body[i:] if l.startswith('*')]
    return k


def main():
    cat, errors = {}, []
    for f in sorted(glob.glob(os.path.join(RAW, 'p_*.html'))):
        slug = os.path.basename(f)[2:-5]
        src = open(f, encoding='utf-8', errors='ignore').read()
        h1 = re.search(r'(?is)<h1[^>]*>(.*?)</h1>', src)
        title = html.unescape(re.sub(r'<[^>]+>', '', h1.group(1))).strip()
        try:
            body = body_after_title(text_lines(src), title)
            item = parse_kit(body) if slug.startswith('kit-') else parse_implant(body)
        except (ValueError, IndexError) as e:
            errors.append('%s: %s' % (slug, e))
            continue
        imgs = uploads(src, 'webp|png|jpe?g')
        item['title'] = title
        item['source'] = 'https://www.conexao.com.br/produto/%s/' % slug
        item['image'] = next((u for u in imgs if 'FRESAGEM' not in u), None)
        item['gallery'] = [u for u in imgs if 'FRESAGEM' not in u][1:]
        item['drill_images'] = [u for u in imgs if 'FRESAGEM' in u]
        item['pdfs'] = uploads(src, 'pdf')
        cat[slug] = item
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        sys.exit(1)
    json.dump(cat, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('ok: %d products -> %s' % (len(cat), os.path.relpath(OUT, ROOT)))


if __name__ == '__main__':
    main()
