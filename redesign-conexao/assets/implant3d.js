// Procedural titanium implant, abutment and crown rendered with three.js.
// Geometry is parametric (diameter, length, pitch, thread leads, body profile) so the same
// code drives the home assembly scene and the per-product viewer. Illustrative, not CAD.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const TAU = Math.PI * 2;
const clamp01 = (v) => Math.min(1, Math.max(0, v));
const smooth = (a, b, v) => { const t = clamp01((v - a) / (b - a)); return t * t * (3 - 2 * t); };
const mix = (a, b, t) => a + (b - a) * t;
const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
// ?motion=1 forces animation on, to review the motion on machines that prefer reduced motion
const reduceMotion = () => !/[?&]motion=1/.test(location.search) && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

export function webglAvailable() {
  try {
    const c = document.createElement('canvas');
    return !!(window.WebGLRenderingContext && (c.getContext('webgl2') || c.getContext('webgl')));
  } catch (_) {
    return false;
  }
}

// Body profiles: how the core radius narrows toward the apex.
const PROFILES = {
  conical: (t) => mix(0.6, 1, smooth(0, 0.6, t)),
  apex: (t) => mix(0.74, 1, smooth(0, 0.26, t)),
  cylindrical: (t) => mix(0.86, 1, smooth(0, 0.1, t)),
};

/**
 * Implant body as one parametric surface: radius(angle, height) = core(height) + helical thread
 * - apical cutting flutes. Height runs from -L (apex) to 0 (platform).
 */
export function implantGeometry({ d = 4, L = 11.5, pitch = 0.8, leads = 1, depthRatio = 0.16, profile = 'apex', flutes = 3, threadTop = null, threadBottom = 0 }) {
  const R = d / 2;
  const depth = R * depthRatio * 2;
  const collar = Math.min(0.9, L * 0.08);
  const top = threadTop == null ? L - collar : threadTop;
  const segU = 144;
  const segV = Math.min(900, Math.max(140, Math.ceil((L / pitch) * 14)));
  const shape = PROFILES[profile] || PROFILES.apex;
  const pos = new Float32Array((segV + 1) * segU * 3 + 3);
  let k = 0;
  for (let j = 0; j <= segV; j++) {
    const y = (L * j) / segV;
    const t = y / L;
    const core = (R - depth) * shape(t);
    const zone = smooth(threadBottom + 0.02 * L, threadBottom + 0.06 * L, y) * (1 - smooth(top - 0.7 * pitch, top, y));
    for (let i = 0; i < segU; i++) {
      const u = (TAU * i) / segU;
      const phase = y / pitch - (leads * u) / TAU;
      const f = phase - Math.floor(phase);
      const tri = 1 - Math.abs(2 * f - 1);
      const ridge = Math.pow(smooth(0.18, 1, tri), 0.8);
      let r = core + depth * ridge * zone * mix(0.75, 1, smooth(0, 0.3, t));
      if (y > top) r = Math.max(r, R * 0.97 * shape(t));
      if (y > L - 0.18) r -= (y - (L - 0.18)) * 0.9;
      if (flutes && t < 0.32) {
        let cut = 0;
        for (let n = 0; n < flutes; n++) {
          let da = Math.abs(((u - (TAU * n) / flutes - 0.4 + TAU * 1.5) % TAU) - Math.PI);
          da = Math.PI - da;
          cut = Math.max(cut, Math.exp(-((da / 0.2) ** 2)));
        }
        r -= cut * (depth + R * 0.12) * (1 - t / 0.32);
      }
      r = Math.max(r, R * 0.2);
      pos[k++] = r * Math.cos(u);
      pos[k++] = y - L;
      pos[k++] = r * Math.sin(u);
    }
  }
  const apex = (segV + 1) * segU;
  pos[k++] = 0; pos[k++] = -L - R * 0.18; pos[k++] = 0;
  const idx = [];
  for (let j = 0; j < segV; j++) {
    for (let i = 0; i < segU; i++) {
      const a = j * segU + i, b = j * segU + ((i + 1) % segU), c = a + segU, e = b + segU;
      idx.push(a, c, b, b, c, e);
    }
  }
  for (let i = 0; i < segU; i++) idx.push(apex, i, (i + 1) % segU);
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setIndex(idx);
  g.computeVertexNormals();
  return g;
}

/** Platform with the internal connection recess. */
function platformGeometry(d) {
  const R = d / 2;
  const pts = [new THREE.Vector2(R * 0.92, -0.02), new THREE.Vector2(R * 0.58, 0), new THREE.Vector2(R * 0.5, -0.5), new THREE.Vector2(R * 0.42, -1.4), new THREE.Vector2(0.001, -1.4)];
  return new THREE.LatheGeometry(pts, 96);
}

/** Cone-morse style abutment: conical insert, gingival collar, tapered post. y=0 is the platform. */
function abutmentGeometry(d) {
  const s = d / 4;
  const p = [[0.001, -3.2], [0.8, -3.2], [1.15, -0.1], [1.85, 0], [2.2, 0.8], [2.2, 1.5], [1.6, 1.8], [1.42, 5.2], [1.2, 5.55], [0.001, 5.6]];
  return new THREE.LatheGeometry(p.map(([x, y]) => new THREE.Vector2(x * s, y)), 96);
}

/** Molar crown from a deformed sphere: narrowed neck, four cusps, central fissures. */
function crownGeometry() {
  const g = new THREE.SphereGeometry(1, 128, 96);
  const p = g.attributes.position;
  const v = new THREE.Vector3();
  const cusps = [[1.9, 1.7], [-1.9, 1.7], [1.9, -1.7], [-1.9, -1.7]];
  for (let i = 0; i < p.count; i++) {
    v.fromBufferAttribute(p, i);
    const s = v.y < 0 ? mix(0.5, 1, smooth(-1, 0.05, v.y)) : 1 - 0.14 * v.y * v.y;
    const X = v.x * s * 4.7;
    const Z = v.z * s * 4.3;
    let Y = v.y > 0 ? v.y * 2.6 : v.y * 4.4;
    if (v.y > 0.15) {
      let bump = 0;
      for (const [cx, cz] of cusps) bump += 0.95 * Math.exp(-((X - cx) ** 2 + (Z - cz) ** 2) / 2.4);
      const fissure = -0.55 * (Math.exp(-(X * X) / 0.35) + Math.exp(-(Z * Z) / 0.35));
      Y += (bump + fissure) * smooth(0.15, 0.85, v.y);
    }
    p.setXYZ(i, X, Y + 4.4 + 1.6, Z);
  }
  g.computeVertexNormals();
  return g;
}

function contactShadow() {
  const c = document.createElement('canvas');
  c.width = c.height = 256;
  const ctx = c.getContext('2d');
  const grd = ctx.createRadialGradient(128, 128, 0, 128, 128, 128);
  grd.addColorStop(0, 'rgba(29,29,31,0.32)');
  grd.addColorStop(0.55, 'rgba(29,29,31,0.10)');
  grd.addColorStop(1, 'rgba(29,29,31,0)');
  ctx.fillStyle = grd;
  ctx.fillRect(0, 0, 256, 256);
  const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false }));
  m.rotation.x = -Math.PI / 2;
  return m;
}

const materials = () => ({
  titanium: new THREE.MeshPhysicalMaterial({ color: 0xc4c8ce, metalness: 1, roughness: 0.34, clearcoat: 0.2, clearcoatRoughness: 0.4 }),
  polished: new THREE.MeshPhysicalMaterial({ color: 0xe4e7ec, metalness: 1, roughness: 0.24, envMapIntensity: 1.4 }),
  recess: new THREE.MeshStandardMaterial({ color: 0x8c9097, metalness: 1, roughness: 0.42, side: THREE.DoubleSide }),
  crown: new THREE.MeshPhysicalMaterial({ color: 0xf4f0e8, roughness: 0.36, clearcoat: 0.85, clearcoatRoughness: 0.22, sheen: 0.5, sheenColor: new THREE.Color(0xffffff), transparent: true }),
  bone: new THREE.MeshPhysicalMaterial({ color: 0xf6efe8, roughness: 0.16, transmission: 0.97, thickness: 1.5, ior: 1.2, transparent: true }),
  gum: new THREE.MeshPhysicalMaterial({ color: 0xeaa29d, roughness: 0.3, transmission: 0.8, thickness: 1.2, ior: 1.3, transparent: true }),
});

function makeRenderer(canvas) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  const key = new THREE.DirectionalLight(0xffffff, 1.6);
  key.position.set(8, 14, 10);
  scene.add(key, new THREE.AmbientLight(0xffffff, 0.25));
  return { renderer, scene };
}

function fit(renderer, camera, host) {
  const w = host.clientWidth, h = host.clientHeight;
  if (!w || !h) return;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}

function whenVisible(el, onChange) {
  const io = new IntersectionObserver((es) => es.forEach((e) => onChange(e.isIntersecting)), { rootMargin: '120px' });
  io.observe(el);
}

/**
 * Home scene: implant screws into translucent bone, abutment seats, crown seats.
 * Desktop: progress comes from the sticky section (story3progress events).
 * Mobile: loops on its own clock. Reduced motion: fully assembled and still.
 */
export function mountAssembly(host, { d = 4, L = 11.5, pitch = 0.8, leads = 2 } = {}) {
  const canvas = document.createElement('canvas');
  canvas.className = 'three-canvas';
  canvas.setAttribute('aria-hidden', 'true');
  host.appendChild(canvas);
  const { renderer, scene } = makeRenderer(canvas);
  const camera = new THREE.PerspectiveCamera(26, 1, 0.1, 400);
  camera.position.set(0, 10, 74);
  camera.lookAt(0, -2, 0);
  const M = materials();

  const rig = new THREE.Group();
  scene.add(rig);
  const implant = new THREE.Group();
  implant.add(new THREE.Mesh(implantGeometry({ d, L, pitch, leads, profile: 'apex' }), M.titanium));
  implant.add(new THREE.Mesh(platformGeometry(d), M.recess));
  const abut = new THREE.Mesh(abutmentGeometry(d), M.polished);
  const crown = new THREE.Mesh(crownGeometry(), M.crown);
  const bone = new THREE.Mesh(new THREE.BoxGeometry(15, L + 3, 9, 1, 1, 1), M.bone);
  bone.position.y = -(L + 3) / 2;
  const gum = new THREE.Mesh(new THREE.BoxGeometry(15, 1.5, 9), M.gum);
  gum.position.y = 0.75;
  const ring = new THREE.Mesh(new THREE.TorusGeometry(2.6, 0.06, 12, 96), new THREE.MeshBasicMaterial({ color: 0x0071e3, transparent: true, opacity: 0 }));
  ring.rotation.x = Math.PI / 2;
  const shadow = contactShadow();
  shadow.scale.set(26, 16, 1);
  shadow.position.y = -L - 3.01;
  rig.add(bone, gum, implant, abut, crown, ring, shadow);

  const turns = 7;
  let target = 0, progress = 0, visible = false, last = performance.now(), pulse = { t: -1, y: 0 }, seated = [false, false];
  const mouse = { x: 0, y: 0, tx: 0, ty: 0 };
  const mobile = window.matchMedia('(max-width: 834px)');
  const still = reduceMotion();

  function apply(p, time) {
    const a = ease(clamp01(p / 0.36)), b = ease(clamp01((p - 0.36) / 0.3)), c = ease(clamp01((p - 0.68) / 0.28));
    implant.position.y = (1 - a) * turns * pitch * leads;
    implant.rotation.y = -(1 - a) * turns * TAU;
    abut.position.y = (1 - b) * 15;
    abut.rotation.y = (1 - b) * (Math.PI / 3);
    abut.visible = p > 0.3;
    crown.position.y = (1 - c) * 17;
    crown.material.opacity = smooth(0.62, 0.74, p);
    crown.visible = p > 0.6;
    [[b, 0, 0], [c, 1, 1.7]].forEach(([v, n, y]) => {
      if (v >= 0.999 && !seated[n]) { seated[n] = true; pulse = { t: time, y }; }
      if (v < 0.95) seated[n] = false;
    });
    rig.rotation.y = 0.55 + p * 0.9 + (still ? 0 : time * 0.00006) + mouse.x * 0.25;
    rig.rotation.x = mouse.y * 0.08;
    camera.position.y = mix(10, 14, p);
    camera.position.z = mix(74, 66, p);
    camera.lookAt(0, mix(-2.5, -1, p), 0);
  }

  function frame(now) {
    const dt = Math.min(64, now - last);
    last = now;
    if (mobile.matches && !still) target = ((now / 9000) % 1.15) / 1.0;
    progress += (Math.min(1, target) - progress) * Math.min(1, dt / 110);
    mouse.x += (mouse.tx - mouse.x) * 0.06;
    mouse.y += (mouse.ty - mouse.y) * 0.06;
    apply(still ? 1 : progress, now);
    if (pulse.t >= 0) {
      const k = (now - pulse.t) / 650;
      ring.position.y = pulse.y;
      ring.scale.setScalar(1 + k * 1.4);
      ring.material.opacity = k < 1 ? 0.55 * (1 - k) : 0;
      if (k >= 1) pulse.t = -1;
    }
    renderer.render(scene, camera);
  }

  window.addEventListener('story3progress', (e) => { target = e.detail; });
  host.addEventListener('pointermove', (e) => {
    const r = host.getBoundingClientRect();
    mouse.tx = (e.clientX - r.left) / r.width - 0.5;
    mouse.ty = (e.clientY - r.top) / r.height - 0.5;
  });
  host.addEventListener('pointerleave', () => { mouse.tx = mouse.ty = 0; });
  const resize = () => fit(renderer, camera, host);
  new ResizeObserver(resize).observe(host);
  resize();
  whenVisible(host, (v) => {
    visible = v;
    renderer.setAnimationLoop(v ? frame : null);
  });
  host.classList.add('has-3d');
  return { setProgress: (p) => { target = p; } };
}

/**
 * Product viewer: rebuilds the implant for the chosen diameter and length, with dimension guides.
 * dims: [{d:'4.0', lengths:['8.5mm', ...]}]
 */
export function mountViewer(host, { dims, profile = 'apex', leads = 1, pitch = 0.8, threadTopRatio = null, onChange }) {
  const canvas = document.createElement('canvas');
  canvas.className = 'three-canvas';
  canvas.setAttribute('aria-hidden', 'true');
  host.appendChild(canvas);
  const { renderer, scene } = makeRenderer(canvas);
  const camera = new THREE.PerspectiveCamera(24, 1, 0.1, 600);
  const M = materials();
  const group = new THREE.Group();
  scene.add(group);
  const body = new THREE.Mesh(new THREE.BufferGeometry(), M.titanium);
  const plat = new THREE.Mesh(new THREE.BufferGeometry(), M.recess);
  group.add(body, plat);
  const guideMat = new THREE.LineBasicMaterial({ color: 0x86868b, transparent: true, opacity: 0.8 });
  const guides = new THREE.LineSegments(new THREE.BufferGeometry(), guideMat);
  scene.add(guides);
  const shadow = contactShadow();
  scene.add(shadow);

  const num = (s) => parseFloat(String(s).replace(',', '.'));
  const state = { d: num(dims[0].d), L: num(dims[0].lengths[Math.floor(dims[0].lengths.length / 2)] || dims[0].lengths[0]) };
  const shown = { ...state };
  let rotY = 0.6, vel = 0, dragging = false, lastX = 0, idle = 0, last = performance.now(), dirty = true;
  const still = reduceMotion();

  function rebuild() {
    const { d, L } = shown;
    body.geometry.dispose();
    plat.geometry.dispose();
    const threadTop = threadTopRatio ? L * threadTopRatio : null;
    body.geometry = implantGeometry({ d, L, pitch, leads, profile, threadTop });
    plat.geometry = platformGeometry(d);
    const R = d / 2, off = R + 1.6;
    const g = [
      // length guide with end ticks
      off, -L / 2, 0, off, L / 2, 0, off - 0.5, -L / 2, 0, off + 0.5, -L / 2, 0, off - 0.5, L / 2, 0, off + 0.5, L / 2, 0,
      // diameter guide above the platform
      -R, L / 2 + 1.4, 0, R, L / 2 + 1.4, 0, -R, L / 2 + 1, 0, -R, L / 2 + 1.8, 0, R, L / 2 + 1, 0, R, L / 2 + 1.8, 0,
    ];
    guides.geometry.dispose();
    guides.geometry = new THREE.BufferGeometry().setAttribute('position', new THREE.Float32BufferAttribute(g, 3));
    shadow.scale.set(d * 4.5, d * 3, 1);
    shadow.position.y = -L / 2 - 0.4;
    const h = Math.max(L + 5, d * 3.2);
    const dist = h / (2 * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2))) * 1.08;
    camera.position.set(0, h * 0.12, dist);
    camera.lookAt(0, 0.3, 0);
    // geometry spans y in [-L, 0]; lift it so the implant is centred on the guides
    body.position.y = plat.position.y = L / 2;
  }

  function frame(now) {
    const dt = Math.min(64, now - last);
    last = now;
    const k = still ? 1 : Math.min(1, dt / 90);
    const before = shown.d + shown.L;
    shown.d += (state.d - shown.d) * k;
    shown.L += (state.L - shown.L) * k;
    if (Math.abs(shown.d - state.d) < 0.004) shown.d = state.d;
    if (Math.abs(shown.L - state.L) < 0.01) shown.L = state.L;
    if (dirty || shown.d + shown.L !== before) { rebuild(); dirty = false; }
    if (!dragging) {
      vel *= 0.94;
      idle += dt;
      rotY += vel + (still || idle < 1800 ? 0 : dt * 0.00025);
    }
    group.rotation.y = rotY;
    renderer.render(scene, camera);
  }

  host.addEventListener('pointerdown', (e) => { dragging = true; lastX = e.clientX; vel = 0; host.setPointerCapture(e.pointerId); });
  host.addEventListener('pointermove', (e) => {
    if (!dragging) return;
    const dx = (e.clientX - lastX) * 0.008;
    lastX = e.clientX;
    rotY += dx;
    vel = dx;
    idle = 0;
  });
  const up = () => { dragging = false; idle = 0; };
  host.addEventListener('pointerup', up);
  host.addEventListener('pointercancel', up);
  const resize = () => fit(renderer, camera, host);
  new ResizeObserver(resize).observe(host);
  resize();
  whenVisible(host, (v) => renderer.setAnimationLoop(v ? frame : null));
  host.classList.add('has-3d');
  return {
    set(d, L) {
      state.d = num(d);
      state.L = num(L);
      if (onChange) onChange(state);
    },
  };
}
