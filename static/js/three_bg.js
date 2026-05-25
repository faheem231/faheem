/**
 * three_bg.js
 * ───────────
 * Premium SaaS Three.js background:
 * ✔ Subtle particle field with connecting lines
 * ✔ Color-varied particles (indigo / cyan / violet palette)
 * ✔ Floating geometric shapes with wireframe and glass-like opacity
 * ✔ Mouse parallax camera
 * ✔ Smooth animations
 * ✔ Pauses when tab hidden
 * ✔ Reduced motion support
 */

function initThreeBackground(canvasId = 'three-canvas') {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof THREE === 'undefined') return;

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  // ── Renderer ──────────────────────────────────────────────────────────────
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setClearColor(0x000000, 0);

  // ── Scene & Camera ────────────────────────────────────────────────────────
  const scene  = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x050505, 0.002);
  const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.set(0, 0, 90);

  // ── Particles ─────────────────────────────────────────────────────────────
  const COUNT    = 250;
  const positions = new Float32Array(COUNT * 3);
  const colors    = new Float32Array(COUNT * 3);
  const speeds    = [];
  const palette   = [
    new THREE.Color(0x6366F1), // Indigo
    new THREE.Color(0x8B5CF6), // Violet
    new THREE.Color(0x06B6D4), // Cyan
    new THREE.Color(0xA78BFA), // Light Violet
    new THREE.Color(0x3B82F6), // Blue
  ];

  for (let i = 0; i < COUNT; i++) {
    positions[i*3]   = (Math.random() - 0.5) * 240;
    positions[i*3+1] = (Math.random() - 0.5) * 240;
    positions[i*3+2] = (Math.random() - 0.5) * 120;
    const c = palette[Math.floor(Math.random() * palette.length)];
    colors[i*3] = c.r; colors[i*3+1] = c.g; colors[i*3+2] = c.b;
    speeds.push({
      x: (Math.random() - 0.5) * 0.03,
      y: (Math.random() - 0.5) * 0.03,
    });
  }

  const pGeo = new THREE.BufferGeometry();
  pGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  pGeo.setAttribute('color',    new THREE.BufferAttribute(colors, 3));
  
  // Custom texture for soft particles
  const canvas2d = document.createElement('canvas');
  canvas2d.width = 16; canvas2d.height = 16;
  const context = canvas2d.getContext('2d');
  const gradient = context.createRadialGradient(8, 8, 0, 8, 8, 8);
  gradient.addColorStop(0, 'rgba(255,255,255,1)');
  gradient.addColorStop(1, 'rgba(255,255,255,0)');
  context.fillStyle = gradient;
  context.fillRect(0, 0, 16, 16);
  const particleTexture = new THREE.CanvasTexture(canvas2d);

  const pMat = new THREE.PointsMaterial({
    size: 1.5, 
    vertexColors: true, 
    transparent: true, 
    opacity: 0.6, 
    sizeAttenuation: true,
    map: particleTexture,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  });
  scene.add(new THREE.Points(pGeo, pMat));

  // ── Connecting Lines ──────────────────────────────────────────────────────
  const MAX_LINES    = 100;
  const linePos      = new Float32Array(MAX_LINES * 6);
  const lineColors   = new Float32Array(MAX_LINES * 6);
  const lineGeo      = new THREE.BufferGeometry();
  lineGeo.setAttribute('position', new THREE.BufferAttribute(linePos, 3));
  lineGeo.setAttribute('color',    new THREE.BufferAttribute(lineColors, 3));
  const lineSegs = new THREE.LineSegments(lineGeo, new THREE.LineBasicMaterial({
    vertexColors: true, transparent: true, opacity: 0.15, blending: THREE.AdditiveBlending, depthWrite: false
  }));
  scene.add(lineSegs);

  // ── Wireframe Geometries ──────────────────────────────────────────────────
  const meshes = [];
  [
    { geo: new THREE.IcosahedronGeometry(12, 0), x:  40, y:  20, z: -30, color: 0x6366F1 },
    { geo: new THREE.OctahedronGeometry(8, 0),   x: -45, y: -15, z: -40, color: 0x8B5CF6 },
    { geo: new THREE.TetrahedronGeometry(10, 0), x:  20, y: -30, z: -20, color: 0x06B6D4 },
    { geo: new THREE.OctahedronGeometry(6, 0),   x: -30, y:  35, z: -15, color: 0xA78BFA },
    { geo: new THREE.IcosahedronGeometry(8, 0),  x:  55, y: -10, z: -50, color: 0x3B82F6 },
    { geo: new THREE.TetrahedronGeometry(7, 0),  x: -55, y:  25, z: -35, color: 0x8B5CF6 },
  ].forEach(({ geo, x, y, z, color }) => {
    const mat  = new THREE.MeshBasicMaterial({ 
      color, 
      wireframe: true, 
      transparent: true, 
      opacity: 0.15,
      blending: THREE.AdditiveBlending
    });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set(x, y, z);
    mesh.userData = {
      rotX:        (Math.random() - 0.5) * 0.006,
      rotY:        (Math.random() - 0.5) * 0.008,
      floatOffset: Math.random() * Math.PI * 2,
      baseOpacity: 0.05 + Math.random() * 0.1,
    };
    scene.add(mesh);
    meshes.push(mesh);
  });

  // ── Mouse Parallax ────────────────────────────────────────────────────────
  const mouse = { x: 0, y: 0 };
  const target = { x: 0, y: 0 };
  document.addEventListener('mousemove', (e) => {
    target.x = (e.clientX / window.innerWidth  - 0.5) * 2;
    target.y = (e.clientY / window.innerHeight - 0.5) * 2;
  });

  // ── Pause when tab hidden ─────────────────────────────────────────────────
  let paused = false;
  document.addEventListener('visibilitychange', () => {
    paused = document.hidden;
  });

  // ── Animation Loop ────────────────────────────────────────────────────────
  let frame = 0;

  function animate() {
    requestAnimationFrame(animate);
    if (paused) return;
    frame += 0.005;

    // Smooth mouse interpolation
    mouse.x += (target.x - mouse.x) * 0.05;
    mouse.y += (target.y - mouse.y) * 0.05;

    // Move particles
    const pos = pGeo.attributes.position.array;
    for (let i = 0; i < COUNT; i++) {
      pos[i*3]   += speeds[i].x;
      pos[i*3+1] += speeds[i].y;
      if (pos[i*3]   >  120) pos[i*3]   = -120;
      if (pos[i*3]   < -120) pos[i*3]   =  120;
      if (pos[i*3+1] >  120) pos[i*3+1] = -120;
      if (pos[i*3+1] < -120) pos[i*3+1] =  120;
    }
    pGeo.attributes.position.needsUpdate = true;

    // Update connecting lines
    let lineIdx = 0;
    const lp = lineGeo.attributes.position.array;
    const lc = lineGeo.attributes.color.array;
    for (let i = 0; i < COUNT && lineIdx < MAX_LINES; i++) {
      for (let j = i + 1; j < COUNT && lineIdx < MAX_LINES; j++) {
        const dx = pos[i*3]   - pos[j*3];
        const dy = pos[i*3+1] - pos[j*3+1];
        const dz = pos[i*3+2] - pos[j*3+2];
        const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
        if (dist < 25) {
          const li = lineIdx * 6;
          lp[li]   = pos[i*3];   lp[li+1] = pos[i*3+1]; lp[li+2] = pos[i*3+2];
          lp[li+3] = pos[j*3];   lp[li+4] = pos[j*3+1]; lp[li+5] = pos[j*3+2];
          const alpha = Math.pow(1 - dist / 25, 2); // Non-linear fade
          
          // Interpolate color based on distance
          const r = 0.38 + 0.16 * alpha; // 0x63 (99) to 0x8B (139)
          const g = 0.40 + 0.04 * alpha; // 0x66 (102) to 0x5C (92)
          const b = 0.94 - 0.02 * alpha; // 0xF1 (241) to 0xF6 (246)
          
          lc[li]   = r * alpha; lc[li+1] = g * alpha; lc[li+2] = b * alpha;
          lc[li+3] = r * alpha; lc[li+4] = g * alpha; lc[li+5] = b * alpha;
          lineIdx++;
        }
      }
    }
    // Clear unused lines
    for (let i = lineIdx; i < MAX_LINES; i++) {
      const li = i * 6;
      lp[li] = lp[li+1] = lp[li+2] = lp[li+3] = lp[li+4] = lp[li+5] = 0;
    }
    lineGeo.attributes.position.needsUpdate = true;
    lineGeo.attributes.color.needsUpdate    = true;

    // Rotate + float + pulse wireframes
    meshes.forEach((m) => {
      m.rotation.x += m.userData.rotX;
      m.rotation.y += m.userData.rotY;
      m.position.y += Math.sin(frame * 2 + m.userData.floatOffset) * 0.015;
      // Pulse opacity
      m.material.opacity = m.userData.baseOpacity + Math.sin(frame * 3 + m.userData.floatOffset) * 0.04;
    });

    // Camera parallax
    camera.position.x += (mouse.x * 8 - camera.position.x) * 0.05;
    camera.position.y += (-mouse.y * 5  - camera.position.y) * 0.05;
    camera.lookAt(scene.position);

    renderer.render(scene, camera);
  }

  animate();

  // ── Resize ────────────────────────────────────────────────────────────────
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
}