"""Render line and kit pages from data/catalogo.json using produto-torq.html as the chrome model.

Usage: python -I tools/build.py   (run tools/extract.py first)
Exit 1 if a configured product is missing from the catalog.
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = json.load(open(os.path.join(ROOT, 'data', 'catalogo.json'), encoding='utf-8'))
UP = 'https://www.conexao.com.br/wp-content/uploads/'
e = html.escape

LINES = [
    dict(file='produto-flash.html', model3d=dict(profile='conical', leads=2, pitch=1.0), name='Flash®', kicker='Cone Morse NP® 24°', thumb='2025/05/Flash.webp',
         card='Cone Morse NP 24 para instalação ágil e estável.', headline='Inserção rápida. Precisão em cada volta.',
         variants=['flash-cone-morse-np-24'], cat='cm'),
    dict(file='produto-torq.html', model3d=dict(profile='apex', leads=1, pitch=0.8), name='Torq®', kicker='Cone Morse NP® 24°', thumb='2025/05/Torq.webp',
         card='Cone Morse NP 24 com foco em estabilidade primária.', variants=[], cat='cm'),
    dict(file='produto-easygrip-sd.html', model3d=dict(profile='cylindrical', leads=2, pitch=0.7), name='EasyGrip SD®', kicker='Hexágono Externo SD', thumb='2025/05/EasyGripSD.webp',
         card='Hexágono externo, plataforma SD.', headline='Feito para os espaços mais estreitos.',
         variants=['easy-grip-hexagono-externo-sd'], cat='hx'),
    dict(file='produto-easygrip-rd.html', model3d=dict(profile='cylindrical', leads=2, pitch=0.7), name='EasyGrip RD®', kicker='Hexágono Externo RD', thumb='2025/05/EasyGripRD.webp',
         card='Hexágono externo, plataforma RD.', headline='Desempenho e segurança no hexágono externo.',
         variants=['easy-grip-hexagono-externo-rd'], cat='hx'),
    dict(file='produto-conectar.html', model3d=dict(profile='cylindrical', leads=2, pitch=0.7), name='ConectAR®', kicker='Hexágono Interno', thumb='2025/05/ConectAR.webp',
         card='Hexágono interno para soluções protéticas versáteis.', headline='Hexágono interno. Estabilidade em cada caso.',
         variants=['conect-ar-hexagono-interno'], cat='hx'),
    dict(file='produto-slim.html', model3d=dict(profile='cylindrical', leads=2, pitch=0.6), name='Slim®', kicker='Cone Morse ⌀2.9mm', thumb='2025/05/Slim.webp',
         card='Cone Morse de diâmetro reduzido para espaços estreitos.', headline='⌀2,9mm. Para quando o espaço é mínimo.',
         variants=['cone-morse-slim'], cat='cm'),
    dict(file='produto-ptery.html', model3d=dict(profile='conical', leads=2, pitch=1.0), name='Ptery®', kicker='Flash® Cone Morse NP Ptery® 24°', thumb='2025/05/Ptery.webp',
         card='Ancoragem pterigoide para reabilitações posteriores.', headline='Estabilidade onde o acesso é difícil.',
         variants=['flash-cone-morse-np-ptery-24'], cat='cx'),
    dict(file='linha-flex-gold.html', model3d=dict(profile='conical', leads=2, pitch=0.9), name='Flex Gold®', kicker='Linha Flex Gold®', thumb='2025/05/FlexGold.webp',
         card='Versatilidade de conexões para a rotina do implantodontista.', headline='Quatro conexões. A mesma estabilidade primária.',
         variants=['flex-gold-cone-morse-np-24', 'flex-gold-cone-morse-fit-11-5', 'flex-gold-cone-morse-gmf-16', 'flex-gold-hexagono-externo-rd'],
         cat='cm', image='2025/05/FlexGold.webp',
         lede='Projetado para alcançar alta estabilidade primária em todas as densidades ósseas, na maxila e na mandíbula.'),
    dict(file='linha-short.html', model3d=dict(profile='cylindrical', leads=2, pitch=0.7), name='Short®', kicker='Linha Short®', thumb='2025/05/Short.webp',
         card='Implantes curtos para rebordos com altura óssea limitada.', headline='Pensado para casos clínicos com pouco osso.',
         variants=['short-cone-morse-np-blt-24', 'short-hexagono-externo-rd'], cat='cx', image='2025/05/Short.webp',
         lede='Ideal para casos clínicos com pouco osso, nas plataformas Cone Morse NP® BLT 24° e Hexágono Externo RD, com estabilidade e precisão.'),
    dict(file='linha-zigo.html', model3d=dict(profile='cylindrical', leads=1, pitch=0.8, threadTopRatio=0.32), name='Zigo®', kicker='Zigoflat® Hexágono Externo RD', thumb='2025/05/Zigomatico.webp',
         card='Implantes zigomáticos para maxilas severamente reabsorvidas.', headline='Para reabilitações em atrofia óssea severa.',
         variants=['zigoflat-hexagono-externo-rd'], cat='cx'),
]

KITS = [
    dict(file='kit-expertguide.html', name='Kit Expertguide®', slug='kit-expertguide', thumb='2025/09/Kit_Expertguide.webp',
         card='Cirurgia guiada integrada ao planejamento digital.', headline='Cirurgia guiada, do Narrow ao Regular.'),
    dict(file='kit-start-flex.html', name='Kit Start Flex®', slug='kit-startflex', thumb='2025/05/KitStartFlex.webp',
         card='O essencial para começar.', headline='O essencial para começar, sem abrir mão do protocolo.'),
    dict(file='kit-master-flex.html', name='Kit Master Flex®', slug='kit-master-flex', thumb='2025/05/KitMasterFlex.webp',
         card='O kit cirúrgico completo.', headline='Todos os sistemas. Uma só caixa.'),
    dict(file='kit-protetico.html', name='Kit Protético', slug='kit-protetico', thumb='2025/05/KitProtetico.webp',
         card='Torque e componentes protéticos.', headline='Cada chave no lugar certo.'),
    dict(file='kit-zigomatico.html', name='Kit Zigomático®', slug='kit-zigomatico', thumb='2025/05/KitZigomatico.webp',
         card='Para reabilitações complexas.', headline='Alta complexidade, menos perfurações.'),
    dict(file='kit-startguide.html', name='Kit Startguide®', slug='kit-startguide', thumb='2025/05/KitStartguide.webp',
         card='Entrada na cirurgia guiada.', headline='Sua entrada na cirurgia guiada.'),
    dict(file='kit-stop-drill.html', name='Kit Stop Drill®', slug='kit-stop-drill', thumb='2025/05/KitStopDrill.webp',
         card='Controle de profundidade em cada perfuração.', headline='Profundidade sob controle em cada perfuração.'),
]

FLEX_BENEFITS = [
    ('Roscas duplas compactantes progressivas', ['Aumenta a velocidade de instalação', 'Aumenta a estabilidade primária']),
    ('Ápice ativo', ['Câmaras helicoidais autocortantes', 'Ponta suavemente arredondada', 'Estabiliza e harmoniza os tecidos ao redor']),
    ('Superfície Porous', ['Microgeometria com nanotecnologia', 'Estimula a velocidade da osseointegração']),
]

ICONS = {
    'thread': '<path d="M7 4l10 3M7 9l10 3M7 14l10 3M7 19l10 1"/>',
    'collar': '<path d="M8 3h8M9 3v4l-2 3v11h10V10l-2-3V3"/>',
    'web': '<circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M2 12h4M18 12h4M5 5l2.5 2.5M16.5 16.5 19 19M5 19l2.5-2.5M16.5 7.5 19 5"/>',
    'lock': '<rect x="4" y="9" width="16" height="11" rx="2"/><path d="M8 9V6a4 4 0 0 1 8 0v3"/>',
    'hex': '<path d="M12 2.5 20.5 7.3v9.4L12 21.5 3.5 16.7V7.3Z"/><circle cx="12" cy="12" r="3"/>',
    'cyl': '<ellipse cx="12" cy="5" rx="7" ry="2.5"/><path d="M5 5v14c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5V5"/>',
    'layers': '<path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 13 9 5 9-5"/>',
    'drill': '<path d="M12 2v6M9 8h6l-1 13h-4z"/>',
    'gauge': '<path d="M12 13a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z"/><path d="M12 9V4M4.9 19a9 9 0 1 1 14.2 0"/>',
    'dot': '<circle cx="12" cy="12" r="8"/><path d="m8.5 12.5 2.5 2.5 4.5-5"/>',
    'box': '<path d="M3 7.5 12 3l9 4.5v9L12 21l-9-4.5Z"/><path d="m3 7.5 9 4.5 9-4.5M12 12v9"/>',
}
SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">%s</svg>'


def icon_for(text):
    t = text.lower()
    for key, name in (('rosca interna', 'hex'), ('espira', 'thread'), ('rosca', 'thread'), ('colar', 'collar'), ('web', 'web'),
                      ('bioplatform', 'lock'), ('angula', 'hex'), ('cone morse', 'hex'), ('hexágono', 'hex'),
                      ('região', 'cyl'), ('macro', 'cyl'), ('híbrido', 'layers'), ('sub-instrument', 'drill'),
                      ('fresad', 'drill'), ('polissulfona', 'box'), ('autoclav', 'box'), ('protocolo', 'drill')):
        if key in t:
            return SVG % ICONS[name]
    return SVG % ICONS['dot']


def up(path):
    return path if path.startswith('http') else UP + path


def chrome(title, desc):
    src = open(os.path.join(ROOT, 'produto-torq.html'), encoding='utf-8').read()
    head = src[:src.index('<div class="pnav">')]
    head = re.sub(r'<title>.*?</title>', '<title>%s</title>' % e(title), head)
    head = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % e(desc, quote=True), head)
    foot = src[src.index('<footer>'):src.index('<script src="site.js"></script>')]
    return head, foot


def pnav(title, links, cta):
    items = ''.join('<a href="#%s">%s</a>' % (a, e(b)) for a, b in links)
    return ('<div class="pnav">\n  <div class="wrap">\n    <span class="pnav-title">%s</span>\n    <div class="pnav-right">\n      %s\n'
            '      <a class="pill" href="contato.html">%s</a>\n    </div>\n  </div>\n</div>\n') % (e(title), items, e(cta))


def crumb(section_href, section, name):
    return ('<div class="wrap"><p class="crumb"><a href="index.html">Início</a><span>/</span><a href="%s">%s</a><span>/</span>%s</p></div>\n'
            % (section_href, section, e(name)))


def chev():
    return '<svg><use href="#chev"/></svg>'


def short_val(feature):
    return feature.split(':', 1)[1].strip() if ':' in feature else feature


def quick_stats(p):
    stats = []
    ang = next((f for f in p['features'] if re.search(r'Angula|Cone morse \d', f, re.I)), None)
    plat = next((f for f in p['features'] if re.search(r'Hexágono|Cone Morse Indexado', f)), None)
    if ang:
        stats.append((re.search(r'\d+(?:\.\d+)?°', ang).group(0), 'angulação interna'))
    elif plat:
        stats.append((plat.replace('Hexágono Externo', 'HE').replace('Cone Morse Indexado', 'CM'), 'plataforma'))
    rosca = next((f for f in p['features'] if f.lower().startswith('rosca interna')), None)
    if rosca:
        stats.append((re.sub(r'\s+', '', short_val(rosca.replace('Rosca interna M', 'Rosca interna: M'))), 'rosca interna'))
    stats.append((p['torque'], 'torque recomendado'))
    return stats


def drill_diam(url):
    m = re.search(r'(\d)[-.](\d{1,2})mm', url)
    return '%s.%s' % (m.group(1), m.group(2)) if m else None


def range_mm(values):
    nums = sorted({float(v.replace('mm', '').replace(',', '.')) for v in values})
    fmt = lambda n: ('%g' % n)
    return fmt(nums[0]) + ' a ' + fmt(nums[-1]) + 'mm' if len(nums) > 1 else fmt(nums[0]) + 'mm'


def variant_label(title):
    t = re.sub(r'^(FLEX GOLD®|SHORT®|ZIGOFLAT®|FLASH®|EASY GRIP®|CONECT AR®)\s*', '', title)
    return t


def feature_cards(p):
    out = []
    for f in p['features']:
        if ':' in f:
            label, val = f.split(':', 1)
            body = '<h3>%s</h3><p>%s</p>' % (e(label.strip()), e(val.strip()))
        else:
            body = '<h3>%s</h3>' % e(f)
        out.append('<div class="feat reveal"><div class="ico">%s</div>%s</div>' % (icon_for(f), body))
    out.append('<div class="feat dark reveal"><div class="ico">%s</div><span class="big">%s</span><p>Torque de instalação recomendado.</p></div>'
               % (SVG % ICONS['gauge'], e(p['torque'])))
    # last row: stretch the remaining cards so the 6-column grid has no holes
    rem = len(out) % 3
    if rem == 1:
        out[-1] = out[-1].replace('class="feat dark', 'class="feat dark full', 1)
    elif rem == 2:
        out[-1] = out[-1].replace('class="feat dark', 'class="feat dark wide', 1)
        out[-2] = out[-2].replace('class="feat ', 'class="feat wide ', 1)
    return '\n'.join(out)


def spec_rows(p):
    rows = []
    plat = [f for f in p['features'] if re.search(r'Angula|Cone morse|Hexágono|Cone Morse|Rosca', f, re.I)]
    if plat:
        rows.append(('Conexão', '<br>'.join(e(x) for x in plat)))
    dims = ''.join('<tr><td>⌀%smm</td><td><div class="len">%s</div></td></tr>' % (e(d['d']), ''.join('<span>%s</span>' % e(l) for l in d['lengths']))
                   for d in p['dimensions'])
    rows.append(('Diâmetros e comprimentos', '<table class="dim-table">%s</table>' % dims))
    if p.get('tech'):
        rows.append(('Material', '%s<small>%s</small>' % (e(p['tech']['name']), e(p['tech']['spec'].replace('(MPa) 73% +resistente', ' MPa, 73% mais resistente')))))
    rows.append(('Torque de instalação', '%s (recomendado)' % e(p['torque'])))
    return '<table class="spec-table"><tbody>%s</tbody></table>' % ''.join('<tr><th>%s</th><td>%s</td></tr>' % r for r in rows)


def drill_section(p, diam_list):
    table = p.get('drill')
    if not table:
        return ''
    keys = table['head']
    seg = ''.join('<button aria-pressed="%s" data-d="%d">⌀%s</button>' % ('true' if i == 0 else 'false', i, e(k))
                  for i, k in enumerate(keys))
    head = ''.join('<th>⌀%s</th>' % e(h) for h in table['head'])
    body = ''.join('<tr><th scope="row">%s</th>%s</tr>' % (e(r['name'].capitalize()),
                   ''.join('<td>%s%s</td>' % (e(c['v']), '<span>%s</span>' % e(c['alt']) if c.get('alt') else '') for c in r['cells']))
                   for r in table['rows'])
    has_alt = any(c.get('alt') for r in table['rows'] for c in r['cells'])
    note = '<p class="drill-note">*Valores entre parênteses: consulte a lâmina técnica para a indicação de uso.</p>' if has_alt else ''
    t = ('<div class="reveal"><table class="drill-table" id="drillTable"><thead><tr><th scope="col" style="text-align:left;padding-left:24px">Densidade</th>%s</tr></thead>'
         '<tbody>%s</tbody></table>%s</div>') % (head, body, note)
    return ('<section class="band" id="fresagem"><div class="wrap-wide"><div class="head"><h2 class="display-2 reveal">Protocolo de fresagem.</h2>'
            '<p class="lede reveal">Escolha o diâmetro para ver a fresa final por densidade óssea.</p></div><div class="seg-wrap reveal"><div class="seg" id="drillSeg" role="group" aria-label="Diâmetro">%s</div></div>'
            '<div class="drill solo">%s</div></div></section>') % (seg, t)


def docs(pdfs, leaflet):
    if not pdfs:
        return ''
    def label(u):
        if '_EN_' in u:
            return leaflet + ' (English)', 'PDF · English'
        if '_ES_' in u:
            return leaflet + ' (Español)', 'PDF · Español'
        return leaflet, 'PDF · Português'
    cards = ''.join('<a class="reveal" href="%s"><span class="ico"><svg><use href="#file"/></svg></span><span><b>%s</b><span>%s</span></span></a>'
                    % ((e(u),) + tuple(e(x) for x in label(u))) for u in pdfs)
    return ('<section id="documentacao"><div class="wrap-wide"><div class="head-left"><h2 class="feature-heading reveal">Documentação.</h2></div>'
            '<div class="dl">%s</div></div></section>') % cards


def rail(items, title, more_href, more_label):
    tiles = ''.join(('<a class="tile" href="%s"><div class="tile-copy"><h3>%s</h3><p>%s</p></div>'
                     '<div class="tile-media"><img loading="lazy" src="%s" alt="%s"></div></a>')
                    % (e(i['file']), e(i['name']), e(i['card']), e(up(i['thumb'])), e(i['name'])) for i in items)
    return ('<section class="band"><div class="wrap-wide"><div class="head-left"><h2 class="feature-heading reveal">%s</h2>'
            '<a class="tlink reveal" href="%s">%s%s</a></div></div><div class="rail">%s</div></section>') % (title, more_href, more_label, chev(), tiles)


def cta(title, lede, label):
    return ('<section class="contact"><div class="wrap"><h2 class="display-2 reveal">%s</h2><p class="lede reveal">%s</p>'
            '<div class="contact-cta reveal"><a class="pill pill-lg" href="contato.html">%s</a>'
            '<a class="pill pill-lg pill-ghost" href="tel:08007742630">Ligar 0800-774-2630</a></div></div></section>') % (e(title), e(lede), e(label))


PAGE_JS = '''<script>
(function(){
  var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var seg=document.getElementById('drillSeg');
  if(seg){
    var btns=seg.querySelectorAll('button'), table=document.getElementById('drillTable');
    var pick=function(d){
      btns.forEach(function(b){b.setAttribute('aria-pressed',String(+b.dataset.d===d))});
      if(table)table.querySelectorAll('tr').forEach(function(tr){tr.querySelectorAll('th,td').forEach(function(c,k){c.classList.toggle('col-on',k===d+1)})});
    };
    btns.forEach(function(b){b.addEventListener('click',function(){pick(+b.dataset.d)})});
    pick(0);
  }
  var vb=document.querySelectorAll('.variant-seg button'), panels=document.querySelectorAll('[data-variant]');
  vb.forEach(function(b){b.addEventListener('click',function(){
    vb.forEach(function(o){o.setAttribute('aria-pressed',String(o.dataset.v===b.dataset.v))});
    panels.forEach(function(p){p.hidden=p.dataset.variant!==b.dataset.v});
  })});
  var q=document.getElementById('compQuery');
  if(q){
    var rows=document.querySelectorAll('#compTable tbody tr'), count=document.getElementById('compCount'), total=rows.length;
    var norm=function(s){return s.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'')};
    q.addEventListener('input',function(){
      var v=norm(q.value.trim()), n=0;
      rows.forEach(function(r){var ok=!v||norm(r.textContent).indexOf(v)>-1;r.hidden=!ok;if(ok)n++});
      count.textContent=v?n+' de '+total+' itens':total+' itens';
    });
  }
})();
</script>
'''


VIEWER_JS = ('<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",'
             '"three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>\n'
             '<script type="module" src="assets/viewer-init.js"></script>\n')


def viewer_section(cfg, vs, image):
    """Interactive 3D implant for every diameter/length the line actually offers."""
    merged = {}
    for v in vs:
        for d in v['dimensions']:
            lens = merged.setdefault(d['d'], [])
            lens += [l for l in d['lengths'] if l not in lens]
    dims = [{'d': d, 'lengths': sorted(l, key=lambda x: float(x.replace('mm', '')))} for d, l in sorted(merged.items(), key=lambda kv: float(kv[0]))]
    data = dict(cfg['model3d'], dims=dims)
    hint = ('<p class="viewer-hint"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
            'stroke-linejoin="round"><path d="M4 12a8 8 0 0 1 14-5.3M20 12a8 8 0 0 1-14 5.3"/><path d="M18 3v4h-4M6 21v-4h4"/></svg>'
            'Arraste o implante para girar.</p>')
    return ('<section id="em3d"><div class="wrap-wide"><div class="head"><h2 class="display-2 reveal">Veja em 3D.</h2>'
            '<p class="lede reveal">Escolha o diâmetro e o comprimento e veja o implante mudar em tempo real.</p></div>'
            '<div class="viewer reveal" data-viewer="%s"><div class="viewer-stage media-frame"><img src="%s" alt="%s">'
            '<span class="viewer-readout"></span><span class="three-note">Modelo 3D ilustrativo. Geometria e medidas oficiais na lâmina técnica.</span></div>'
            '<div class="viewer-controls"><div><span class="ctl-label">Diâmetro (mm)</span><div class="seg" data-role="d"></div></div>'
            '<div><span class="ctl-label">Comprimento (mm)</span><div class="seg" data-role="L"></div></div>%s</div></div></div></section>\n') % (
        e(json.dumps(data, ensure_ascii=False), quote=True), e(image), e(cfg['name']), hint)


def write(name, title, desc, body, js=True, extra=''):
    head, foot = chrome(title, desc)  # the Torq head already defines #chev, #check and #file
    page = head + body + '\n' + foot + '<script src="site.js"></script>\n' + (PAGE_JS if js else '') + extra + '</body>\n</html>\n'
    open(os.path.join(ROOT, name), 'w', encoding='utf-8').write(page)


def build_line(cfg):
    vs = [CAT[s] for s in cfg['variants']]
    p0 = vs[0]
    multi = len(vs) > 1
    image = up(cfg.get('image') or p0['image'])
    lede = cfg.get('lede') or p0['lede']
    all_d = sorted({d['d'] for v in vs for d in v['dimensions']}, key=float)
    all_len = [l for v in vs for d in v['dimensions'] for l in d['lengths']]
    if multi:
        stats = [(str(len(vs)), 'conexões'), ('⌀' + all_d[0] + ' a ' + all_d[-1], 'diâmetros (mm)'), (range_mm(all_len).replace(' a ', '–'), 'comprimentos')]
    else:
        stats = quick_stats(p0)
    stats_html = ''.join('<div><b>%s</b><span>%s</span></div>' % (e(a), e(b)) for a, b in stats)
    sub = (cfg['kicker'] + '. ' + ', '.join(variant_label(v['title']) for v in vs) + '.') if multi else ('. '.join(p0['indications']) + '.' if p0['indications'] else p0['features'][0] + '.')
    links = [('visao', 'Visão geral'), ('especificacoes', 'Especificações')]
    drill_src = next((v for v in vs if v.get('drill')), None)
    if drill_src:
        links.append(('fresagem', 'Fresagem'))
    links.append(('documentacao', 'Documentação'))

    body = pnav(cfg['name'], links, 'Solicitar orçamento')
    body += '<main>\n' + crumb('index.html#linhas', 'Implantes', cfg['name'])
    body += ('<header class="page-hero" id="visao"><div class="wrap"><span class="launch reveal" style="display:block;margin-bottom:10px">%s</span>'
             '<h1 class="hero-display reveal">%s.</h1><p class="lede reveal">%s</p></div>'
             '<div class="wrap-wide"><div class="p-hero-grid"><div class="media-frame reveal"><img src="%s" alt="%s"></div>'
             '<div class="p-summary"><h2 class="reveal">%s</h2><p class="reveal">%s</p><div class="p-quick reveal">%s</div>'
             '<div class="p-cta reveal"><a class="pill pill-lg" href="contato.html">Falar com consultor</a>%s</div></div></div></div></header>\n') % (
        e(cfg['kicker']), e(cfg['name']), e(lede), e(image), e(cfg['name']), e(cfg['headline']), e(sub.strip()), stats_html,
        '<a class="pill pill-lg pill-ghost" href="%s">Baixar lâmina</a>' % e(p0['pdfs'][0]) if (p0['pdfs'] and not multi) else
        '<a class="pill pill-lg pill-ghost" href="#documentacao">Ver lâminas</a>')

    if p0.get('tech'):
        body += ('<section><div class="wrap-wide"><div class="stat-hero reveal"><p class="kicker">Tecnologia %s</p><div class="num">73%%</div>'
                 '<p><b>Mais resistente.</b> %s com 955 MPa de resistência.</p></div></div></section>\n') % (e(p0['tech']['name']), e(p0['tech']['name']))

    if cfg['file'] == 'linha-flex-gold.html':
        cards = ''.join('<div class="feat wide reveal" style="grid-column:span 2"><div class="ico">%s</div><h3>%s</h3>%s</div>'
                        % (icon_for(t), e(t), ''.join('<p>%s.</p>' % e(x) for x in items)) for t, items in FLEX_BENEFITS)
        body += ('<section class="band"><div class="wrap-wide"><div class="head"><h2 class="display-2 reveal">Engenharia em comum.</h2>'
                 '<p class="lede reveal">As quatro conexões compartilham o mesmo corpo híbrido.</p></div><div class="feat-grid">%s</div></div></section>\n') % cards

    vseg = ''
    if multi:
        vseg = '<div class="seg-wrap reveal"><div class="seg variant-seg" role="group" aria-label="Conexão">%s</div></div>' % ''.join(
            '<button aria-pressed="%s" data-v="%d">%s</button>' % ('true' if i == 0 else 'false', i, e(variant_label(v['title']))) for i, v in enumerate(vs))
    feats = ''
    for i, v in enumerate(vs):
        hidden = ' hidden' if i else ''
        feats += '<div data-variant="%d"%s><div class="feat-grid">%s</div></div>' % (i, hidden, feature_cards(v))
    body += ('<section class="%s"><div class="wrap-wide"><div class="head"><h2 class="display-2 reveal">%s</h2><p class="lede reveal">%s</p></div>%s%s</div></section>\n') % (
        'band' if cfg['file'] != 'linha-flex-gold.html' else '', 'Cada detalhe tem uma função.' if not multi else 'Escolha a sua conexão.',
        e(lede) if not multi else 'Características e especificações de cada variação.', vseg, feats)

    specs = ''
    for i, v in enumerate(vs):
        hidden = ' hidden' if i else ''
        ind = ''
        if v['indications']:
            ind = ('<div class="head" style="margin:72px auto 32px"><h2 class="feature-heading">Principais indicações.</h2></div>'
                   '<ul class="check-list" style="max-width:640px;margin:0 auto">%s</ul>') % ''.join('<li><svg><use href="#check"/></svg>%s</li>' % e(x) for x in v['indications'])
        specs += '<div data-variant="%d"%s>%s%s%s</div>' % (i, hidden, '<h3 class="variant-name">%s</h3>' % e(v['title']) if multi else '', spec_rows(v), ind)
    body += ('<section id="especificacoes"><div class="wrap"><div class="head"><h2 class="display-2 reveal">Especificações.</h2></div>%s<div class="reveal">%s</div></div></section>\n') % (vseg, specs)

    body += viewer_section(cfg, vs, image)
    if drill_src:
        body += drill_section(drill_src, [d['d'] for d in drill_src['dimensions']]) + '\n'
    pdfs = []
    for v in vs:
        pdfs += [(u, v.get('leaflet_label', 'Lâmina técnica').replace('Lâmina ', 'Lâmina ')) for u in v['pdfs']]
    docs_html = ''
    if pdfs:
        cards = ''
        for u, lbl in pdfs:
            lang = 'PDF · English' if '_EN_' in u else 'PDF · Español' if '_ES_' in u else 'PDF · Português'
            cards += '<a class="reveal" href="%s"><span class="ico"><svg><use href="#file"/></svg></span><span><b>%s</b><span>%s</span></span></a>' % (e(u), e(lbl), lang)
        docs_html = ('<section id="documentacao"><div class="wrap-wide"><div class="head-left"><h2 class="feature-heading reveal">Documentação.</h2></div>'
                     '<div class="dl">%s</div></div></section>\n') % cards
    body += docs_html
    others = [l for l in LINES if l['file'] != cfg['file']]
    others.sort(key=lambda l: (l['cat'] != cfg['cat']))
    body += rail(others[:5], 'Conheça também.', 'index.html#linhas', 'Todas as linhas') + '\n'
    body += cta('Pronto para o %s?' % cfg['name'], 'Fale com a equipe comercial para condições, kits compatíveis e disponibilidade.', 'Solicitar orçamento')
    body += '\n</main>\n'
    desc = '%s: %s' % (cfg['name'], lede)
    write(cfg['file'], cfg['name'].replace('®', '') + ' Conexão', desc[:300], body, extra=VIEWER_JS)


def build_kit(cfg):
    k = CAT[cfg['slug']]
    facts = dict(k['facts'])
    if 'Implantes' in facts and facts['Implantes'].startswith('Startguide Sistemas'):
        facts['Sistemas'] = facts.pop('Implantes').replace('Startguide Sistemas ', '')
    for key in list(facts):
        v = re.sub(r'(?<![\w,])0(\d,\d)', r'Ø\1', facts[key])
        v = re.sub(r'\s*-\s*Ø', ', Ø', v).replace(' | ', '; ')
        facts[key] = v.strip(' ,')
    paras = list(k['paragraphs'])
    lede = paras.pop(0) if paras and len(paras[0]) < 90 else cfg['card']
    stats = []
    if k['composition']:
        stats.append((str(len(k['composition'])), 'itens no kit'))
    ds = re.findall(r'Ø\s*(\d+,\d+)', facts.get('Diâmetros', ''))
    if ds:
        stats.append(('Ø%s–%s' % (ds[0], ds[-1]) if len(ds) > 1 else 'Ø' + ds[0], 'diâmetros (mm)'))
    if k['code']:
        stats.append((k['code'], 'código do kit'))
    if not stats:
        stats.append(('Poliacetal', 'polímero técnico'))
    stats_html = ''.join('<div><b>%s</b><span>%s</span></div>' % (e(a), e(b)) for a, b in stats[:3])
    links = [('visao', 'Visão geral')]
    if k['composition']:
        links.append(('composicao', 'Composição'))
    links.append(('documentacao', 'Documentação'))

    body = pnav(cfg['name'], links, 'Solicitar orçamento')
    body += '<main>\n' + crumb('index.html#kits', 'Kits', cfg['name'])
    body += ('<header class="page-hero" id="visao"><div class="wrap"><span class="launch reveal" style="display:block;margin-bottom:10px">Kits Conexão</span>'
             '<h1 class="hero-display reveal">%s.</h1><p class="lede reveal">%s</p></div>'
             '<div class="wrap-wide"><div class="p-hero-grid kit-hero"><div class="media-frame reveal"><img src="%s" alt="%s"></div>'
             '<div class="p-summary"><h2 class="reveal">%s</h2>%s<div class="p-quick reveal">%s</div>'
             '<div class="p-cta reveal"><a class="pill pill-lg" href="contato.html">Falar com consultor</a>%s</div></div></div></div></header>\n') % (
        e(cfg['name']), e(lede), e(up(k['image'])), e(cfg['name']), e(cfg['headline']),
        ''.join('<p class="reveal">%s</p>' % e(x) for x in paras), stats_html,
        '<a class="pill pill-lg pill-ghost" href="%s">Baixar lâmina</a>' % e(k['pdfs'][0]) if k['pdfs'] else '')

    if facts or k['features']:
        rows = ''.join('<tr><th>%s</th><td>%s</td></tr>' % (e(a), e(b)) for a, b in facts.items())
        feats = ''
        if k['features']:
            feats = '<ul class="check-list" style="margin-top:40px">%s</ul>' % ''.join('<li><svg><use href="#check"/></svg>%s</li>' % e(x) for x in k['features'])
        body += ('<section class="band"><div class="wrap"><div class="head"><h2 class="display-2 reveal">Para quais sistemas.</h2></div>'
                 '<div class="reveal">%s%s</div></div></section>\n') % ('<table class="spec-table kit-facts"><tbody>%s</tbody></table>' % rows if rows else '', feats)

    if k['gallery'] or k['notes']:
        imgs = ''.join('<div class="media-frame reveal"><img loading="lazy" src="%s" alt="%s, detalhe"></div>' % (e(u), e(cfg['name'])) for u in k['gallery'])
        notes = ''.join('<p class="drill-note" style="text-align:center">%s</p>' % e(n.lstrip('* ').rstrip(':') + '.') for n in k['notes'])
        body += ('<section><div class="wrap-wide"><div class="head"><h2 class="display-2 reveal">Em detalhes.</h2></div>'
                 '%s<div class="kit-gallery">%s</div></div></section>\n') % (notes, imgs)

    if k['composition']:
        rows = ''.join('<tr><td class="code">%s</td><td>%s</td></tr>' % (e(c['code']), e(c['name'])) for c in k['composition'])
        body += ('<section class="band" id="composicao"><div class="wrap"><div class="head"><h2 class="display-2 reveal">Composição.</h2>'
                 '<p class="lede reveal">Todos os itens do %s%s.</p></div>'
                 '<div class="comp reveal"><div class="comp-bar"><label class="sr" for="compQuery">Buscar item</label>'
                 '<input id="compQuery" type="search" placeholder="Buscar por nome ou código" autocomplete="off">'
                 '<span id="compCount">%d itens</span></div>'
                 '<table class="comp-table" id="compTable"><thead><tr><th>Código</th><th>Item</th></tr></thead><tbody>%s</tbody></table></div></div></section>\n') % (
            e(cfg['name']), ', código do produto explodido %s' % e(k['code']) if k['code'] else '', len(k['composition']), rows)

    if k['pdfs']:
        cards = ''.join('<a class="reveal" href="%s"><span class="ico"><svg><use href="#file"/></svg></span><span><b>%s</b><span>PDF · Português</span></span></a>'
                        % (e(u), e(k.get('leaflet_label', 'Lâmina técnica'))) for u in k['pdfs'])
        body += ('<section id="documentacao"><div class="wrap-wide"><div class="head-left"><h2 class="feature-heading reveal">Documentação.</h2></div>'
                 '<div class="dl">%s</div></div></section>\n') % cards
    body += rail([x for x in KITS if x['file'] != cfg['file']], 'Outros kits.', 'index.html#kits', 'Todos os kits') + '\n'
    body += cta('Monte o seu %s.' % cfg['name'], 'Fale com a equipe comercial para condições e disponibilidade.', 'Solicitar orçamento')
    body += '\n</main>\n'
    write(cfg['file'], cfg['name'].replace('®', '') + ' Conexão', ('%s: %s' % (cfg['name'], lede))[:300], body)


def main():
    missing = [s for c in LINES for s in c['variants'] if s not in CAT] + [c['slug'] for c in KITS if c['slug'] not in CAT]
    if missing:
        print('missing in catalog: %s' % missing, file=sys.stderr)
        sys.exit(1)
    built = []
    for c in LINES:
        if c['variants']:
            build_line(c)
            built.append(c['file'])
    for c in KITS:
        build_kit(c)
        built.append(c['file'])
    print('ok: %d pages\n%s' % (len(built), '\n'.join(built)))


if __name__ == '__main__':
    main()
