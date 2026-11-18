#!/usr/bin/env node
// 실제 웹페이지 시연 장면을 짧은 영상으로 녹화 → 슬라이드 media 로 사용
// 사용법: node cardnews/capture.mjs <URL> <저장경로.mp4> [초=6] [가로=1080] [세로=660]
//   페이지를 열고 천천히 스크롤하며 녹화한다. 로그인 필요한 화면은 직접 화면녹화한 파일을 쓰는 게 낫다.
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

async function loadPlaywright() {
  try { return await import("playwright"); } catch {}
  const globalRoot = execFileSync("npm", ["root", "-g"]).toString().trim();
  const req = createRequire(path.join(globalRoot, "noop.js"));
  return req(req.resolve("playwright", { paths: [globalRoot, "/opt/node-tools/node_modules"] }));
}

const [url, outFile, secArg = "6", wArg = "1080", hArg = "660"] = process.argv.slice(2);
if (!url || !outFile) {
  console.error("사용법: node cardnews/capture.mjs <URL> <저장경로.mp4> [초] [가로] [세로]");
  process.exit(1);
}
const seconds = Number(secArg), width = Number(wArg), height = Number(hArg);
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "capture-"));

const { chromium } = await loadPlaywright();
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width, height }, recordVideo: { dir: tmp, size: { width, height } } });
const page = await ctx.newPage();
await page.goto(url, { waitUntil: "networkidle" }).catch(() => {});
await page.waitForTimeout(800);
for (let i = 0; i < seconds * 10; i++) {
  await page.mouse.wheel(0, Math.round(height / 40));
  await page.waitForTimeout(100);
}
const video = page.video();
await ctx.close();
await browser.close();
const webm = await video.path();

fs.mkdirSync(path.dirname(path.resolve(outFile)), { recursive: true });
// 첫 0.8초(로딩 화면)는 잘라낸다
execFileSync("ffmpeg", ["-hide_banner", "-loglevel", "error", "-y", "-ss", "0.8", "-i", webm, "-t", String(seconds),
  "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an", outFile], { stdio: "inherit" });
fs.rmSync(tmp, { recursive: true, force: true });
console.log(`저장: ${outFile}`);
