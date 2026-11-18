#!/usr/bin/env node
// AI술사 카드뉴스 렌더러
// 사용법: node cardnews/render.mjs cardnews/posts/<폴더> [script 파일명=script.json]
//   <폴더>/script.json 을 읽어 <폴더>/out/ 에 슬라이드를 만든다.
//   - media 가 GIF/영상이면  → NN.mp4 (인스타 캐러셀은 GIF 업로드 불가라 MP4로)
//   - media 가 정지 이미지/없음 → NN.png
//   - 확인용 미리보기: out/preview/NN.png (영상은 80% 지점 프레임), out/contact.png (전체 한 장)
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const W = 1080, H = 1350, FPS = 30;
const ANIMATED = new Set([".gif", ".mp4", ".mov", ".webm", ".webp"]);
const here = path.dirname(fileURLToPath(import.meta.url));

async function loadPlaywright() {
  try { return await import("playwright"); } catch {}
  const globalRoot = execFileSync("npm", ["root", "-g"]).toString().trim();
  const req = createRequire(path.join(globalRoot, "noop.js"));
  return req(req.resolve("playwright", { paths: [globalRoot, "/opt/node-tools/node_modules"] }));
}

const ff = (args) => execFileSync("ffmpeg", ["-hide_banner", "-loglevel", "error", "-y", ...args], { stdio: ["ignore", "inherit", "inherit"] });
function probeDuration(file) {
  try {
    const out = execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", file]).toString().trim();
    const d = parseFloat(out);
    return Number.isFinite(d) && d > 0 ? d : null;
  } catch { return null; }
}
function isAnimated(file) {
  const ext = path.extname(file).toLowerCase();
  if (!ANIMATED.has(ext)) return false;
  if (ext === ".gif" || ext === ".webp") {
    try {
      const n = execFileSync("ffprobe", ["-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", file]).toString().trim();
      return parseInt(n, 10) > 1;
    } catch { return true; }
  }
  return true;
}

const postDir = path.resolve(process.argv[2] || "");
const scriptName = process.argv[3] || "script.json";
const scriptPath = path.join(postDir, scriptName);
if (!process.argv[2] || !fs.existsSync(scriptPath)) {
  console.error("사용법: node cardnews/render.mjs cardnews/posts/<폴더> [script.json]");
  process.exit(1);
}
const script = JSON.parse(fs.readFileSync(scriptPath, "utf8"));
const brandCfg = JSON.parse(fs.readFileSync(path.join(here, "brand", "brand.json"), "utf8"));
const slides = script.slides;
const outName = script.meta?.outDir || "out";
const outDir = path.join(postDir, outName), prevDir = path.join(outDir, "preview"), tmpDir = path.join(outDir, ".tmp");
fs.rmSync(outDir, { recursive: true, force: true });
for (const d of [outDir, prevDir, tmpDir]) fs.mkdirSync(d, { recursive: true });

const { chromium } = await loadPlaywright();
const browser = await chromium.launch();
const templateUrl = pathToFileURL(path.join(here, "template", "slide.html")).href;

const results = [];
for (let i = 0; i < slides.length; i++) {
  const slide = slides[i];
  const no = String(i + 1).padStart(2, "0");
  const mediaFile = slide.media ? path.resolve(postDir, slide.media) : null;
  if (mediaFile && !fs.existsSync(mediaFile)) throw new Error(`슬라이드 ${no}: media 파일 없음 → ${slide.media}`);

  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  await page.addInitScript((data) => { window.__SLIDE__ = data; }, {
    slide, index: i, total: slides.length, brand: brandCfg.name, handle: brandCfg.handle, series: brandCfg.series,
  });
  page.on("pageerror", (e) => console.error(`슬라이드 ${no} 템플릿 오류:`, e.message));
  await page.goto(templateUrl);
  await page.evaluate(() => window.__READY__);
  const box = await page.evaluate(() => window.__MEDIA_BOX__);
  const overlay = path.join(tmpDir, `${no}-overlay.png`);
  await page.screenshot({ path: overlay, omitBackground: true });
  await page.close();

  const bg = brandCfg.colors.bg.replace("#", "0x");
  if (!mediaFile || !box) {
    const out = path.join(outDir, `${no}.png`);
    ff(["-f", "lavfi", "-i", `color=c=${bg}:s=${W}x${H}`, "-i", overlay, "-filter_complex", "[0][1]overlay=0:0", "-frames:v", "1", out]);
    fs.copyFileSync(out, path.join(prevDir, `${no}.png`));
    results.push({ no, file: `${no}.png`, kind: "image" });
    continue;
  }

  const fit = `scale=${box.w}:${box.h}:force_original_aspect_ratio=increase,crop=${box.w}:${box.h}${slide.mediaPos === "top" ? ":(in_w-out_w)/2:0" : ""}`;
  if (!isAnimated(mediaFile)) {
    const out = path.join(outDir, `${no}.png`);
    ff(["-f", "lavfi", "-i", `color=c=${bg}:s=${W}x${H}`, "-i", mediaFile, "-i", overlay,
      "-filter_complex", `[1:v]${fit}[m];[0][m]overlay=${box.x}:${box.y}[b];[b][2]overlay=0:0`, "-frames:v", "1", out]);
    fs.copyFileSync(out, path.join(prevDir, `${no}.png`));
    results.push({ no, file: `${no}.png`, kind: "image" });
    continue;
  }

  // 영상 길이: 원본이 짧으면 반복해서 최소 5초, 최대 15초
  const src = probeDuration(mediaFile) || 3;
  const dur = slide.duration || Math.min(15, src >= 5 ? src : src * Math.ceil(5 / src));
  const isGif = path.extname(mediaFile).toLowerCase() === ".gif";
  const out = path.join(outDir, `${no}.mp4`);
  ff([
    "-f", "lavfi", "-i", `color=c=${bg}:s=${W}x${H}:r=${FPS}`,
    ...(isGif ? ["-ignore_loop", "0"] : ["-stream_loop", "-1"]), "-i", mediaFile,
    "-loop", "1", "-i", overlay,
    "-filter_complex", `[1:v]fps=${FPS},${fit},setsar=1[m];[0][m]overlay=${box.x}:${box.y}:shortest=1[b];[b][2]overlay=0:0,format=yuv420p[v]`,
    "-map", "[v]", "-t", String(dur), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high",
    "-movflags", "+faststart", "-an", out,
  ]);
  ff(["-ss", (dur * 0.8).toFixed(2), "-i", out, "-frames:v", "1", path.join(prevDir, `${no}.png`)]);
  results.push({ no, file: `${no}.mp4`, kind: "video", seconds: dur });
}
await browser.close();

// 전체 미리보기 한 장 (검수용)
const previews = results.map((r) => path.join(prevDir, `${r.no}.png`));
const cols = Math.min(5, previews.length);
const inputs = previews.flatMap((p) => ["-i", p]);
const scaled = previews.map((_, k) => `[${k}:v]scale=270:338[s${k}]`).join(";");
const layout = previews.map((_, k) => `${(k % cols) * 270}_${Math.floor(k / cols) * 338}`).join("|");
if (previews.length === 1) fs.copyFileSync(previews[0], path.join(outDir, "contact.png"));
else ff([...inputs, "-filter_complex", `${scaled};${previews.map((_, k) => `[s${k}]`).join("")}xstack=inputs=${previews.length}:layout=${layout}:fill=black`, "-frames:v", "1", path.join(outDir, "contact.png")]);

fs.rmSync(tmpDir, { recursive: true, force: true });
console.log(`완료: ${path.relative(process.cwd(), outDir)}`);
for (const r of results) console.log(`  ${r.file}${r.kind === "video" ? `  (${r.seconds.toFixed(1)}초 영상)` : ""}`);
console.log(`  contact.png  (전체 미리보기)`);
