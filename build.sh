#!/usr/bin/env bash
# 체스놀로지아 빌드 스크립트 — build/ 소스를 index.html 한 파일로 조립
# 주의: 이 저장소에는 현재 build/ 소스가 없다. 배포본 index.html을 직접 패치해 운영 중이며,
#       build/ 없이 실행하면 index.html이 손상되므로 아래 가드에서 즉시 중단한다.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -d build ]; then
  echo "중단: build/ 소스가 없습니다." >&2
  echo "  이 저장소는 배포본 index.html 단일 파일을 직접 패치해 운영 중입니다." >&2
  echo "  build/를 복원한 뒤 실행하세요. (그대로 실행하면 index.html이 사라집니다)" >&2
  exit 1
fi

for f in head1.html style.css mid.html pieces.svg chess.esm.js core.js data.js app1.js app2.js app3.js; do
  if [ ! -f "build/$f" ]; then
    echo "중단: build/$f 가 없습니다." >&2
    exit 1
  fi
done

tmp="index.html.tmp"
{
  cat build/head1.html
  cat build/style.css
  cat build/mid.html
  cat build/pieces.svg
  # Supabase 연결 설정은 반드시 모듈 스크립트보다 먼저 로드되어야 한다 (SUPA_CONFIG 전역)
  echo '<script src="./config.js"></script>'
  echo '<script type="module">'
  cat build/chess.esm.js
  echo ''
  cat build/core.js build/data.js build/app1.js build/app2.js build/app3.js
  echo '</script>'
  echo '</body></html>'
} > "$tmp"

if ! grep -q 'src="\./config\.js"' "$tmp"; then
  echo "중단: config.js 참조가 결과물에 없습니다." >&2; rm -f "$tmp"; exit 1
fi
if ! grep -q 'APP_VERSION' "$tmp"; then
  echo "중단: APP_VERSION 이 결과물에 없습니다." >&2; rm -f "$tmp"; exit 1
fi
if ! grep -q 'serviceWorker.register' "$tmp"; then
  echo "중단: 서비스 워커 등록 코드가 결과물에 없습니다." >&2; rm -f "$tmp"; exit 1
fi

mv "$tmp" index.html
echo "built index.html ($(wc -c < index.html) bytes)"
echo
echo "다음 단계:"
echo "  1) index.html 의 APP_VERSION 을 올린다"
echo "  2) sw.js 의 CACHE 이름(chessnologia-vN)을 함께 올린다 — 안 올리면 구버전 캐시가 남는다"
echo "  3) git add index.html sw.js && git commit && git push"
