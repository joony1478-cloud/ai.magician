// AI술사 목업 키트 — 시간 t(초)를 넣으면 화면 상태가 정해지는 결정적 타임라인.
// 장면 HTML 에서 K.type/K.show/K.cursor... 로 동작을 등록하면 mock.mjs 가 프레임마다 K.seek(t) 후 캡처한다.
(() => {
  const ops = [];
  const $ = (sel) => (typeof sel === "string" ? document.querySelectorAll(sel) : [sel]);
  const clamp = (v) => Math.max(0, Math.min(1, v));
  const ease = (p) => 1 - Math.pow(1 - p, 3);
  const easeIO = (p) => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2);
  const prog = (t, t0, d) => clamp((t - t0) / Math.max(d, 1e-6));

  const K = {
    duration: 6,
    dur(s) { K.duration = s; return K; },

    // 글자 타이핑 (한글 포함, 글자 단위). 끝나는 시각을 돌려준다
    type(sel, text, t0, cps = 16, opts = {}) {
      const chars = Array.from(text);
      ops.push((t) => $(sel).forEach((el) => {
        const n = t < t0 ? 0 : Math.min(chars.length, Math.floor((t - t0) * cps) + 1);
        if (n === 0 && opts.placeholder) el.innerHTML = `<span class="k-ph">${opts.placeholder}</span>`;
        else el.textContent = chars.slice(0, n).join("");
        const typing = t >= t0 - 0.6 && (n < chars.length || opts.caretAfter);
        el.classList.toggle("k-caret", typing);
        el.classList.toggle("k-off", typing && Math.floor(t * 2.2) % 2 === 1 && (n === 0 || n === chars.length));
      }));
      return t0 + chars.length / cps;
    },

    // 나타나기: anim = up | fade | pop | left | right | drop
    show(sel, t0, anim = "up", d = 0.4) {
      ops.push((t) => $(sel).forEach((el) => {
        const p = ease(prog(t, t0, d));
        const tr = { up: `translateY(${(1 - p) * 30}px)`, drop: `translateY(${(1 - p) * -60}px)`, left: `translateX(${(1 - p) * -40}px)`,
          right: `translateX(${(1 - p) * 40}px)`, pop: `scale(${0.85 + 0.15 * p})`, fade: "none" }[anim];
        el.style.opacity = p;
        el.style.transform = tr;
      }));
      return t0 + d;
    },
    hide(sel, t0, d = 0.25) {
      ops.push((t) => { if (t >= t0) $(sel).forEach((el) => { el.style.opacity = 1 - prog(t, t0, d); }); });
      return t0 + d;
    },
    // 클래스 켜기 (t0~t1)
    cls(sel, name, t0, t1 = Infinity) {
      ops.push((t) => $(sel).forEach((el) => el.classList.toggle(name, t >= t0 && t < t1)));
    },
    // 형광펜/빨간 표시 쓸기 (.k-hl / .k-bad 에 사용)
    sweep(sel, t0, d = 0.45) {
      ops.push((t) => $(sel).forEach((el) => {
        el.style.backgroundSize = `${ease(prog(t, t0, d)) * 100}% ${el.classList.contains("k-bad") ? "100%" : "45%"}`;
      }));
      return t0 + d;
    },
    // 숫자 올라가기/내려가기
    count(sel, from, to, t0, d = 1, fmt = (v) => Math.round(v).toLocaleString()) {
      ops.push((t) => $(sel).forEach((el) => { el.textContent = fmt(from + (to - from) * ease(prog(t, t0, d))); }));
    },
    // 요소 이동 (드래그 등): [[t,x,y],...]
    move(sel, keys) {
      ops.push((t) => $(sel).forEach((el) => {
        const [x, y] = interp(keys, t);
        el.style.left = x + "px"; el.style.top = y + "px";
      }));
    },
    // 마우스 커서: keys=[[t,x,y],...], clicks=[t,...]
    cursor(keys, clicks = []) {
      const c = document.createElement("div");
      c.className = "k-cursor";
      c.innerHTML = '<svg viewBox="0 0 24 24" width="34" height="34"><path d="M4 2l16 9.5-7 1.6 4.2 7.4-3 1.6-4.2-7.4L5 19z" fill="#111" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>';
      document.body.appendChild(c);
      const ripples = clicks.map(() => { const r = document.createElement("div"); r.className = "k-ripple"; document.body.appendChild(r); return r; });
      ops.push((t) => {
        const [x, y] = interp(keys, t);
        const down = clicks.some((ct) => t >= ct && t < ct + 0.12);
        c.style.transform = `translate(${x}px,${y}px) scale(${down ? 0.86 : 1})`;
        c.style.opacity = t < keys[0][0] - 0.2 ? 0 : 1;
        clicks.forEach((ct, i) => {
          const p = prog(t, ct, 0.5), r = ripples[i], [cx, cy] = interp(keys, ct);
          r.style.left = cx + 6 + "px"; r.style.top = cy + 6 + "px";
          r.style.opacity = t >= ct && p < 1 ? 1 - p : 0;
          r.style.transform = `scale(${0.3 + p * 0.9})`;
        });
      });
    },
    // 자유 함수: (t) => {...}
    at(fn) { ops.push(fn); },

    seek(t) { ops.forEach((f) => f(t)); },
  };
  function interp(keys, t) {
    if (t <= keys[0][0]) return [keys[0][1], keys[0][2]];
    for (let i = 1; i < keys.length; i++) {
      const [t1, x1, y1] = keys[i], [t0, x0, y0] = keys[i - 1];
      if (t <= t1) { const p = easeIO(prog(t, t0, t1 - t0)); return [x0 + (x1 - x0) * p, y0 + (y1 - y0) * p]; }
    }
    const l = keys[keys.length - 1]; return [l[1], l[2]];
  }
  window.K = K;
})();
