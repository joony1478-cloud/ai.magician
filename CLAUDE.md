# AI술사 레포

- `index.html` — AI술사 프로필 링크 사이트(무료 주문서 + 리드 수집). 인스타 CTA의 도착지
- `scrolls/` — 주문서 콘텐츠 페이지
- `cardnews/` — 인스타 카드뉴스 자동화 (리서치 → 글 → 디자인 → 캡션)

## 카드뉴스 만들 때
`/cardnews` 스킬(`.claude/skills/cardnews/SKILL.md`)을 따른다. 이 세션이 **지휘자**이고,
`.claude/agents/` 의 `cardnews-researcher` / `cardnews-writer` / `cardnews-designer` / `cardnews-captioner` 에게 단계별로 맡긴다.
공통 규칙은 `cardnews/brand/guide.md`, 계정 설정은 `cardnews/brand/brand.json`.

- 목업 GIF 녹화: `node cardnews/mock.mjs <장면.html> <저장.gif> [1080x660|1080x1350]`
- 슬라이드 렌더: `node cardnews/render.mjs cardnews/posts/<폴더>` (Playwright + ffmpeg 필요)
