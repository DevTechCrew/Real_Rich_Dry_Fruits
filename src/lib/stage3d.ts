// Live 3D for the site: the Real Rich pouch, and for the hero the four dry fruits riding a ring round it, lit like the
// Blender studio (blender/rr.py): key light top left, cool fill right, rim behind, Khronos PBR Neutral tone mapping.
// The dry fruits are photographs (blender/cutouts.py) on cards that always face the camera, so they look real from every angle.
// Loaded on demand by components/Stage3D.tsx, so three.js never weighs on the first paint. Models: blender/export_models.py.
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';

type V3 = [number, number, number];
export type NutKind = 'almond' | 'cashew' | 'pistachio' | 'raisin';
export type HeroSpec = {
  camera: { fov: number; position: V3; target: V3 };
  pouch: { slug: string; position: V3; rotationY: number };
  ring: { y: number; tilt: number; period: number };
  cycle: { slugs: string[]; every: number; turn: number; whirl: number };
  nuts: { kind: NutKind; pose: number; r: number; a: number; h: number; roll: number; rock: number; size: number }[];
};
export type StageOptions = { mode: 'hero'; spec: HeroSpec } | { mode: 'pack'; slug: string };
type Hooks = { interactEl: HTMLElement; onReady: () => void; onLost: () => void };

const D = Math.PI / 180;
const loader = new GLTFLoader();
let pouchModel: Promise<THREE.Object3D> | null = null;
const nutArts = new Map<string, Promise<THREE.Texture>>();
const arts = new Map<string, Promise<THREE.Texture>>();

const loadPouch = () => (pouchModel ??= loader.loadAsync('/models/pouch.glb').then(g => g.scene));
const loadNut = (kind: NutKind, pose: number) => {         // the same cut-outs as the floating nuts: photos/fly/{kind}[-pose]
  const name = pose > 1 ? `${kind}-${pose}` : kind;
  if (!nutArts.has(name)) nutArts.set(name, new THREE.TextureLoader().loadAsync(`/images/photos/fly/${name}.webp`).then(t => {
    t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t;
  }));
  return nutArts.get(name)!;
};
const loadArt = (slug: string) => {
  if (!arts.has(slug)) arts.set(slug, new THREE.TextureLoader().loadAsync(`/models/art-${slug}.webp`).then(t => {
    t.colorSpace = THREE.SRGBColorSpace; t.flipY = false; t.anisotropy = 8; return t; // glTF UVs, so no flip
  }));
  return arts.get(slug)!;
};

/** Samples the pack art a mip level finer than WebGL picks by itself, so the small print stays crisp, not soft. */
const crisp = (sh: { fragmentShader: string }) => {
  sh.fragmentShader = sh.fragmentShader.replace('#include <map_fragment>', THREE.ShaderChunk.map_fragment.replace('texture2D( map, vMapUv )', 'texture2D( map, vMapUv, -1.0 )'));
};

/** A soft round contact shadow: a radial gradient on a plane, cheaper and softer than a shadow map. */
function blobShadow(w: number, d: number, opacity: number) {
  const c = document.createElement('canvas'); c.width = c.height = 128;
  const g = c.getContext('2d')!; const grad = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  grad.addColorStop(0, 'rgba(43,30,22,1)'); grad.addColorStop(0.45, 'rgba(43,30,22,.5)'); grad.addColorStop(1, 'rgba(43,30,22,0)');
  g.fillStyle = grad; g.fillRect(0, 0, 128, 128);
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, d), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(c), transparent: true, opacity, depthWrite: false }));
  m.rotation.x = -Math.PI / 2; m.position.y = 0.02; m.renderOrder = -1; m.userData.opacity = opacity;
  return m;
}

/** Mounts a live stage on `canvas`; returns a function that stops and frees it. Calls onReady once the first frame is drawn. */
export function mountStage(canvas: HTMLCanvasElement, opts: StageOptions, hooks: Hooks): () => void {
  let renderer: THREE.WebGLRenderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
  } catch { return () => {}; } // no WebGL: the poster image stays
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.NeutralToneMapping; renderer.toneMappingExposure = 1.15;
  renderer.setClearColor(0x000000, 0);

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture; scene.environmentIntensity = 0.55;
  const light = (color: number, intensity: number, from: V3) => { const l = new THREE.DirectionalLight(color, intensity); l.position.set(...from); scene.add(l); };
  light(0xfff1e2, 2.6, [-34, 42, 26]); light(0xe8efff, 0.55, [40, 14, 18]); light(0xfff6ea, 0.9, [10, 26, -36]);

  const camera = new THREE.PerspectiveCamera(26, 1, 1, 600);
  const pivot = new THREE.Group(); scene.add(pivot);        // the pouch turns inside this
  const ring = new THREE.Group(); scene.add(ring);          // the hero's nuts ride this
  const nuts: { mesh: THREE.Mesh; spec: HeroSpec['nuts'][number]; i: number }[] = [];
  const face = new THREE.Quaternion(), roll = new THREE.Quaternion(), Z = new THREE.Vector3(0, 0, 1);
  let baseYaw = 0, sway = 5, reach = 26, ringSpec: HeroSpec['ring'] | null = null;
  // the hero shows each pack in turn: every few seconds the pouch is tossed up and spun round once, its art swapped while
  // the front faces away, and the ring of nuts whirls along. Its own clock, which waits while the pouch is being dragged.
  let cycle: HeroSpec['cycle'] | null = null, packs: THREE.Texture[] = [], ct = 0, yaw = 0, shadow: THREE.Mesh | null = null;
  const fronts: THREE.MeshStandardMaterial[] = [];

  // interaction: the pouch turns toward the pointer; a drag spins it, then it eases back
  let px = 0, py = 0, spin = 0, vel = 0, dragging = false, lastX = 0;
  let hold = 0.95;                                          // stay on the poster's pose while the canvas fades in over it
  const el = hooks.interactEl;
  const onMove = (e: PointerEvent) => {
    const b = el.getBoundingClientRect();
    px = Math.max(-1, Math.min(1, ((e.clientX - b.left) / b.width) * 2 - 1)); py = Math.max(-1, Math.min(1, ((e.clientY - b.top) / b.height) * 2 - 1));
    if (dragging && hold <= 0) { const dx = e.clientX - lastX; lastX = e.clientX; spin += dx * 0.012; vel = dx * 0.012; }
  };
  const onLeave = () => { px = 0; py = 0; };
  const onDown = (e: PointerEvent) => { dragging = true; lastX = e.clientX; vel = 0; canvas.setPointerCapture(e.pointerId); };
  const onUp = () => { dragging = false; };
  el.addEventListener('pointermove', onMove); el.addEventListener('pointerleave', onLeave);
  canvas.addEventListener('pointerdown', onDown); canvas.addEventListener('pointerup', onUp); canvas.addEventListener('pointercancel', onUp);

  let disposed = false, visible = true, raf = 0, ready = false, t = 0, last = 0;
  const resize = () => {
    const w = canvas.clientWidth, h = canvas.clientHeight; if (!w || !h) return;
    renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 3, Math.sqrt(2.6e6 / (w * h))));   // the screen's own density (3x phones too), within a budget
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
  };
  const ro = new ResizeObserver(resize); ro.observe(canvas);
  const io = new IntersectionObserver(([e]) => { visible = e.isIntersecting; if (visible && ready) loop(performance.now()); });
  io.observe(canvas);

  const frame = (dt: number) => {
    const holding = hold > 0;                                 // the poster's pose: no time, no pointer, nuts at their start
    if (holding) { hold -= dt; dt = 0; } else t += dt;
    if (!dragging && !holding) {                             // inertia, then ease back the short way round
      spin += vel; vel *= Math.pow(0.05, dt);
      if (Math.abs(vel) < 0.002) { spin = Math.atan2(Math.sin(spin), Math.cos(spin)); spin *= Math.pow(0.15, dt); }
    }
    const k = 1 - Math.pow(0.02, dt);                         // smooth pointer follow (0 while holding)
    let turned = 0, lift = 0, whirl = 0;
    if (cycle && packs.length) {
      if (!dragging) ct += dt;
      const n = Math.floor(ct / cycle.every), p = (ct - n * cycle.every) / cycle.turn, on = n > 0 && p < 1;
      const e = on ? (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(2 - 2 * p, 3) / 2) : 0;   // ease in, ease out
      turned = e * Math.PI * 2; lift = on ? Math.sin(p * Math.PI) : 0; whirl = (on ? n - 1 + e : n) * cycle.whirl * D;
      const map = packs[(n - (on && p < 0.5 ? 1 : 0)) % packs.length];
      if (fronts[0]?.map !== map) for (const m of fronts) m.map = map;
    }
    yaw += ((baseYaw + Math.sin(t * 0.45) * sway * D + px * reach * D + spin) - yaw) * k;
    pivot.rotation.y = yaw + turned;
    pivot.rotation.x += (((py * 4 - lift * 6) * D) - pivot.rotation.x) * k;
    pivot.position.y = Math.sin(t * 0.9) * 0.25 + lift * 1.6;
    if (shadow) { shadow.scale.setScalar(1 - 0.2 * lift); (shadow.material as THREE.MeshBasicMaterial).opacity = shadow.userData.opacity * (1 - 0.45 * lift); }
    if (ringSpec) {
      ring.rotation.y += ((px * 5 * D) - ring.rotation.y) * k; ring.rotation.x += ((py * 3 * D) - ring.rotation.x) * k;
      const tilt = ringSpec.tilt * D, turn = (t / ringSpec.period) * Math.PI * 2 + whirl;
      face.copy(ring.quaternion).invert().multiply(camera.quaternion);   // the cards face the camera however the ring leans
      for (const n of nuts) {
        const a = n.spec.a * D + turn;
        n.mesh.position.set(n.spec.r * Math.cos(a), ringSpec.y + n.spec.h - n.spec.r * Math.sin(a) * Math.sin(tilt) + (Math.sin(t * 0.8 + n.i) - Math.sin(n.i)) * 0.35, n.spec.r * Math.sin(a) * Math.cos(tilt));
        n.mesh.quaternion.copy(face).multiply(roll.setFromAxisAngle(Z, (n.spec.roll + (Math.sin(t * 0.5 + n.i * 1.7) - Math.sin(n.i * 1.7)) * n.spec.rock) * D));
      }
    }
    renderer.render(scene, camera);
  };
  const loop = (now: number) => {
    cancelAnimationFrame(raf);
    const step = (ts: number) => {
      if (disposed || !visible || document.hidden) return;
      const dt = Math.min(0.05, (ts - (last || ts)) / 1000); last = ts; frame(dt);
      raf = requestAnimationFrame(step);
    };
    last = now; raf = requestAnimationFrame(step);
  };
  const onVis = () => { if (!document.hidden && visible && ready) loop(performance.now()); };
  document.addEventListener('visibilitychange', onVis);
  canvas.addEventListener('webglcontextlost', hooks.onLost);

  const slug = opts.mode === 'hero' ? opts.spec.pouch.slug : opts.slug;
  Promise.all([loadPouch(), loadArt(slug), opts.mode === 'hero' ? Promise.all(opts.spec.nuts.map(n => loadNut(n.kind, n.pose))) : Promise.resolve(null)]).then(([pouchSrc, art, nutSrc]) => {
    if (disposed) return;
    const pouch = pouchSrc.clone(true);
    pouch.traverse(o => {
      const m = o as THREE.Mesh; if (!m.isMesh) return;
      const mats = (Array.isArray(m.material) ? m.material : [m.material]).map(mt => {
        const s = (mt as THREE.MeshStandardMaterial).clone();
        if (s.name === 'front') { s.map = art; s.color.set(0xffffff); s.onBeforeCompile = crisp; fronts.push(s); }
        s.roughness = 0.55; s.envMapIntensity = 1; return s;
      });
      m.material = Array.isArray(m.material) ? mats : mats[0];
    });
    const box = new THREE.Box3().setFromObject(pouch); const top = box.max.y;
    pivot.add(pouch);
    if (opts.mode === 'pack') {
      // the same framing as the static pack render (blender/render_packs.py): 85 mm, 7 degrees up, pouch 82% of the height
      baseYaw = -10 * D; sway = 4; reach = 28;
      const fov = 2 * Math.atan(18 / 85), frameH = top / 0.82, ty = top + 0.05 * frameH - frameH / 2, dist = frameH / 2 / Math.tan(fov / 2);
      camera.fov = fov / D; camera.position.set(0, ty + Math.sin(7 * D) * dist, Math.cos(7 * D) * dist); camera.lookAt(0, ty, 0);
      scene.add(blobShadow(22, 9, 0.38));
    } else {
      const s = opts.spec;
      baseYaw = s.pouch.rotationY * D; pivot.position.set(...s.pouch.position);
      camera.fov = s.camera.fov; camera.position.set(...s.camera.position); camera.lookAt(...s.camera.target);
      scene.add(shadow = blobShadow(26, 11, 0.32));
      ringSpec = s.ring;
      Promise.all(s.cycle.slugs.map(loadArt)).then(ts => { if (!disposed) { packs = ts; cycle = s.cycle; } }).catch(() => {});
      s.nuts.forEach((spec, i) => {
        const map = nutSrc![i], { width: w, height: h } = map.image as HTMLImageElement, k = spec.size / Math.max(w, h);
        // the photograph as it is (no lighting, no tone mapping), exactly as the poster has it (blender/export_web.py stage)
        const mesh = new THREE.Mesh(new THREE.PlaneGeometry(w * k, h * k), new THREE.MeshBasicMaterial({ map, transparent: true, depthWrite: false, toneMapped: false }));
        ring.add(mesh); nuts.push({ mesh, spec, i });
      });
    }
    pivot.rotation.y = yaw = baseYaw;
    resize(); frame(0); ready = true; hooks.onReady(); loop(performance.now());
  }).catch(e => console.warn('3D stage could not load, keeping the image', e));

  return () => {
    disposed = true; cancelAnimationFrame(raf); ro.disconnect(); io.disconnect();
    document.removeEventListener('visibilitychange', onVis);
    el.removeEventListener('pointermove', onMove); el.removeEventListener('pointerleave', onLeave);
    canvas.removeEventListener('pointerdown', onDown); canvas.removeEventListener('pointerup', onUp); canvas.removeEventListener('pointercancel', onUp);
    canvas.removeEventListener('webglcontextlost', hooks.onLost);
    pmrem.dispose(); renderer.dispose(); renderer.forceContextLoss();   // hand the GPU context back now, not at GC
  };
}
