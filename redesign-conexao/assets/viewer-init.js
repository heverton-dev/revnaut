// Wires every [data-viewer] block: diameter/length pickers driving the 3D implant viewer.
// Without WebGL (or if three.js fails to load) the product photo stays and the pickers stay hidden.
import { webglAvailable, mountViewer } from './implant3d.js';

const fmt = (v) => String(v).replace(/mm$/, '');

document.querySelectorAll('[data-viewer]').forEach((root) => {
  const cfg = JSON.parse(root.dataset.viewer);
  const stage = root.querySelector('.viewer-stage');
  const segD = root.querySelector('[data-role="d"]');
  const segL = root.querySelector('[data-role="L"]');
  const readout = root.querySelector('.viewer-readout');
  if (!webglAvailable()) return;
  let viewer;
  try {
    viewer = mountViewer(stage, cfg);
  } catch (err) {
    console.warn('3D desativado:', err);
    return;
  }
  let d = cfg.dims[0];
  let L = d.lengths[Math.floor(d.lengths.length / 2)];

  const button = (label, pressed, onClick) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.textContent = label;
    b.setAttribute('aria-pressed', String(pressed));
    b.addEventListener('click', onClick);
    return b;
  };
  const press = (seg, el) => seg.querySelectorAll('button').forEach((b) => b.setAttribute('aria-pressed', String(b === el)));

  function renderLengths() {
    segL.replaceChildren(...d.lengths.map((len) => {
      const b = button(fmt(len), len === L, () => { L = len; press(segL, b); update(); });
      return b;
    }));
  }
  function update() {
    viewer.set(d.d, L);
    readout.innerHTML = '<b>⌀' + d.d + '</b> × ' + fmt(L) + 'mm';
  }
  segD.replaceChildren(...cfg.dims.map((dim) => {
    const b = button('⌀' + dim.d, dim === d, () => {
      d = dim;
      if (!d.lengths.includes(L)) L = d.lengths[Math.floor(d.lengths.length / 2)];
      press(segD, b);
      renderLengths();
      update();
    });
    return b;
  }));
  renderLengths();
  update();
  root.classList.add('ready');
});
