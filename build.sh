#!/usr/bin/env bash
# 체스놀로지아 빌드 스크립트 — build/ 소스를 index.html 한 파일로 조립
set -e
cd "$(dirname "$0")"
{ cat build/head1.html; cat build/style.css; cat build/mid.html; cat build/pieces.svg
  echo '<script type="module">'
  cat build/chess.esm.js; echo ''
  cat build/core.js; cat build/data.js; cat build/app1.js; cat build/app2.js; cat build/app3.js
  echo '</script>'; echo '</body></html>'
} > index.html
echo "built index.html ($(wc -c < index.html) bytes)"
