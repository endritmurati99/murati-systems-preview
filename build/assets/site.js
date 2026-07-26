const canvas = document.getElementById("particle-field");
const context = canvas?.getContext("2d");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const root = document.documentElement;
const pointer = { x: 0.5, y: 0.18, active: false };
let width = 0;
let height = 0;
let pixelRatio = 1;
let dots = [];

function moveLight(x, y) {
  pointer.x = x / Math.max(1, window.innerWidth);
  pointer.y = y / Math.max(1, window.innerHeight);
  pointer.active = true;
  if (reduceMotion) return;

  const dx = pointer.x - 0.5;
  const dy = pointer.y - 0.18;
  root.style.setProperty("--cursor-x", `${x}px`);
  root.style.setProperty("--cursor-y", `${y}px`);
  root.style.setProperty("--orbit-x", `${dx * 22}px`);
  root.style.setProperty("--orbit-y", `${dy * 16}px`);
  root.style.setProperty("--glow-opacity", ".82");
}

function resize() {
  if (!canvas || !context) return;
  pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
  width = canvas.offsetWidth;
  height = canvas.offsetHeight;
  canvas.width = width * pixelRatio;
  canvas.height = height * pixelRatio;
  context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
  dots = Array.from({ length: Math.min(96, Math.floor(width / 11)) }, () => ({
    angle: Math.random() * Math.PI * 2,
    radius: Math.random() * Math.min(width, height) * 0.52 + 40,
    speed: Math.random() * 0.0008 + 0.0002,
  }));
}

function draw() {
  if (!canvas || !context) return;
  context.clearRect(0, 0, width, height);
  const centerX = width * 0.66;
  const centerY = height * 0.08;
  const pointerX = pointer.x * width;
  const pointerY = pointer.y * height;

  dots.forEach((dot) => {
    if (!reduceMotion) dot.angle += dot.speed * 16;
    const baseX = centerX + Math.cos(dot.angle) * dot.radius * 1.18;
    const baseY = centerY + Math.sin(dot.angle) * dot.radius * 0.34 + dot.radius * 0.08;
    const dx = pointerX - baseX;
    const dy = pointerY - baseY;
    const distance = Math.max(1, Math.hypot(dx, dy));
    const influence = pointer.active ? Math.max(0, 1 - distance / 260) : 0;
    const x = baseX - (dx / distance) * influence * 18;
    const y = baseY - (dy / distance) * influence * 10;

    if (y < height * 0.84) {
      context.fillStyle = `rgba(139,238,255,${0.38 + influence * 0.34})`;
      context.fillRect(x, y, 1.4 + influence, 1.4 + influence);
    }
  });
  window.requestAnimationFrame(draw);
}

window.addEventListener("resize", resize, { passive: true });
window.addEventListener("pointermove", (event) => moveLight(event.clientX, event.clientY), { passive: true });
window.addEventListener("pointerleave", () => {
  pointer.active = false;
  root.style.setProperty("--glow-opacity", ".62");
}, { passive: true });

resize();
draw();
