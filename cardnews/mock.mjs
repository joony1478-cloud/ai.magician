#!/usr/bin/env node
// 목업 장면(HTML) → GIF/MP4 녹화. 프레임마다 K.seek(t) 후 캡처하므로 끊김 없이 선명하다.
// 사용법: node cardnews/mock.mjs <장면.html> <저장경로.gif|.mp4> [가로x세로=1080x660] [fps=24]
//   길이는 장면 안의 K.dur(초) 값. 크기 기준: body 슬라이드 GIF 띠 1080x660, 표지 1080x1350
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

async function loadPlaywright() {
  try { return await import("playwright"); } catch {}
  const globalRoot = execFileSync("npm", ["root", "-g"]).toString().trim();
  const req = createRequire(path.join(globalRoot, "noop.js"));
  return req(req.resolve("playwright", { paths: [globalRoot, "/opt/node-tools/node_modules"] }));
}

const here = path.dirname(fileURLToPath(import.meta.url));
const [scene, outFile, size = "1080x660", fpsArg = "24"] = process.argv.slice(2);
if (!scene || !outFile) {
  console.error("사용법: node cardnews/mock.mjs <장면.html> <저장경로.gif|.mp4> [1080x660] [fps]");
  process.exit(1);
}
const [width, height] = size.split("x").map(Number);
const fps = Number(fpsArg);

const fontsDir = pathToFileURL(path.join(here, "fonts")).href;
const fontCss = [[900, "Black", "9Black"], [800, "ExtraBold", "8ExtraBold"], [700, "Bold", "6SemiBold"], [500, "Medium", "4Regular"]]
  .map(([w, pre, pap]) => `@font-face{font-family:Brand;font-weight:${w};src:url(${fontsDir}/Paperlogy-${pap}.woff2) format("woff2"),url(${fontsDir}/Pretendard-${pre}.woff2) format("woff2")}`).join("\n");
const css = fontCss + "\n" + fs.readFileSync(path.join(here, "mockup", "kit.css"), "utf8");
const kit = fs.readFileSync(path.join(here, "mockup", "kit.js"), "utf8");

const { chromium } = await loadPlaywright();
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
page.on("pageerror", (e) => console.error("장면 오류:", e.message));
await page.addInitScript(({ kit, css }) => {
  (0, eval)(kit);
  document.addEventListener("DOMContentLoaded", () => {
    const st = document.createElement("style"); st.textContent = css; document.head.prepend(st);
  });
}, { kit, css });
await page.goto(pathToFileURL(path.resolve(scene)).href);
await page.evaluate(() => document.fonts.ready);
const duration = await page.evaluate(() => window.K.duration);

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "mock-"));
const frames = Math.round(duration * fps);
for (let f = 0; f < frames; f++) {
  await page.evaluate((t) => window.K.seek(t), f / fps);
  await page.screenshot({ path: path.join(tmp, `${String(f).padStart(4, "0")}.png`) });
}
await browser.close();

fs.mkdirSync(path.dirname(path.resolve(outFile)), { recursive: true });
const input = ["-hide_banner", "-loglevel", "error", "-y", "-framerate", String(fps), "-i", path.join(tmp, "%04d.png")];
if (outFile.toLowerCase().endsWith(".gif")) {
  execFileSync("ffmpeg", [...input, "-vf", "split[a][b];[a]palettegen=max_colors=192:stats_mode=diff[p];[b][p]paletteuse=dither=sierra2_4a:diff_mode=rectangle", "-loop", "0", outFile], { stdio: "inherit" });
} else {
  execFileSync("ffmpeg", [...input, "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", outFile], { stdio: "inherit" });
}
fs.rmSync(tmp, { recursive: true, force: true });
console.log(`저장: ${outFile}  (${duration}초, ${width}x${height}, ${fps}fps)`);
