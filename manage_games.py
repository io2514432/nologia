#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""체스놀로지아 기보 관리 도구 (운영자 전용)

사용법 (터미널에서, 프로젝트 루트에서 실행):
  python3 scripts/manage_games.py add 경기1.pgn [경기2.pgn ...]
      --title "표시 제목" --white "백 한글명" --black "흑 한글명" --blurb "한 줄 소개"
  python3 scripts/manage_games.py remove <game_id>
  python3 scripts/manage_games.py list
  python3 scripts/manage_games.py rebuild      # games.json -> data.js 재생성

모든 기보는 python-chess로 전수 검증되며(합법수 아닌 수 하나라도 있으면 거부),
검증을 통과한 것만 build/games.json + build/data.js에 반영됩니다.
마지막으로 `bash build.sh`를 실행해 index.html을 다시 만드세요.
"""
import io, json, os, re, sys, argparse

try:
    import chess, chess.pgn
except ImportError:
    sys.exit("python-chess 필요: pip install python-chess")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES_JSON = os.path.join(ROOT, 'build', 'games.json')
DATA_JS = os.path.join(ROOT, 'build', 'data.js')

OPEN_MAP = {
    'C20':'오픈 게임','C21':'센터 게임','C23':'비숍 오프닝','C25':'비엔나 게임','C30':'킹스 갬빗','C33':'킹스 갬빗','C39':'킹스 갬빗',
    'C40':'킹스 나이트 오프닝','C41':'필리도어 디펜스','C42':'필리도어 디펜스','C44':'폰 게임','C45':'스코틀랜드 게임','C46':'3나이트 게임',
    'C47':'4나이트 게임','C50':'이탈리안 게임','C51':'이탈리안 게임','C52':'이탈리안 게임','C53':'이탈리안 게임','C54':'이탈리안 게임',
    'C55':'이탈리안 게임','C60':'루이 로페즈','C62':'루이 로페즈','C65':'루이 로페즈','C66':'루이 로페즈','C67':'루이 로페즈','C68':'루이 로페즈',
    'C69':'루이 로페즈','C70':'루이 로페즈','C78':'루이 로페즈','C80':'루이 로페즈','C84':'루이 로페즈','C88':'루이 로페즈','C89':'루이 로페즈','C93':'루이 로페즈',
    'B00':'비정통 오프닝','B01':'스칸디나비안 디펜스','B02':'알레킨 디펜스','B04':'알레킨 디펜스','B06':'모던 디펜스','B07':'피르크 디펜스','B08':'피르크 디펜스',
    'B10':'카로칸 디펜스','B12':'카로칸 디펜스','B17':'카로칸 디펜스','B18':'카로칸 디펜스','B20':'시실리안','B21':'시실리안','B22':'시실리안','B23':'시실리안',
    'B27':'시실리안','B30':'시실리안','B32':'시실리안','B33':'시실리안','B40':'시실리안','B50':'시실리안','B53':'시실리안','B54':'시실리안','B70':'시실리안 드래곤','B76':'시실리안 드래곤','B80':'시실리안','B82':'시실리안','B90':'시실리안 나jdorf','B97':'나jdorf',
    'A00':'비정통 오프닝','A04':'레티 오프닝','A05':'레티 오프닝','A08':'레티 오프닝','A10':'잉글리시 오프닝','A15':'잉글리시 오프닝','A20':'잉글리시 오프닝',
    'A45':'인디언 게임','A46':'인디언 게임','A48':'킹스 인디언','A56':'베노니','A80':'네덜란드 디펜스','A81':'네덜란드 디펜스','A84':'네덜란드 디펜스','A87':'네덜란드 디펜스',
    'D02':'퀸스 폰 게임','D06':'퀸스 갬빗','D10':'슬라브 디펜스','D18':'슬라브 디펜스','D20':'수장 갬빗','D27':'수장 갬빗','D30':'퀸스 갬빗 디펜스',
    'D31':'퀸스 갬빗 디펜스','D35':'퀸스 갬빗 디펜스','D37':'퀸스 갬빗 디펜스','D40':'퀸스 갬빗 디펜스','D43':'세미슬라브','D45':'세미슬라브','D50':'퀸스 갬빗 게임',
    'D53':'퀸스 갬빗 게임','D55':'퀸스 갬빗 게임','D58':'퀸스 갬빗 게임','D59':'퀸스 갬빗 게임','D60':'퀸스 갬빗 게임','D80':'그륀펠트 디펜스','D85':'그륀펠트 디펜스','D97':'그륀펠트 디펜스',
    'E00':'카탈란 오프닝','E04':'카탈란 오프닝','E12':'퀸스 인디언','E20':'니임조 인디언','E24':'니임조 인디언','E32':'니임조 인디언','E54':'킹스 인디언','E60':'킹스 인디언','E62':'킹스 인디언','E68':'킹스 인디언','E69':'킹스 인디언','E92':'킹스 인디언',
}
ECO_CAT = {'A':'인디언 게임','B':'시실리안','C':'오픈 게임','D':'퀸스 갬빗','E':'클로즈드 게임'}

def slugify(s):
    s = re.sub(r"[^a-z0-9]+", '-', s.lower()).strip('-')
    return s[:40] or 'game'

def parse_games(path):
    out = []
    with io.open(path, encoding='utf-8', errors='ignore') as f:
        while True:
            try:
                g = chess.pgn.read_game(f)
            except Exception:
                g = None
            if g is None:
                break
            out.append(g)
    return out

def validate(game):
    """전수 검증: 모든 수가 합법인지, 기보가 끝까지 재생되는지"""
    errs = list(game.errors or [])
    board = game.board()
    n = 0
    for mv in game.mainline_moves():
        if mv not in board.legal_moves:
            errs.append(f"illegal move {mv} at ply {n+1}")
            break
        board.push(mv)
        n += 1
    return n, errs

def build_entry(game, gid, title, white_ko, black_ko, blurb, source):
    h = game.headers
    plies, errs = validate(game)
    if errs:
        raise ValueError(' / '.join(str(e) for e in errs[:3]))
    if plies < 4:
        raise ValueError(f"수가 너무 적음 ({plies}수)")
    eco = h.get('ECO', '')
    opening = OPEN_MAP.get(eco, ECO_CAT.get(eco[:1], '기타 오프닝'))
    year = (h.get('Date', '') or '')[:4]
    if not year.isdigit():
        year = ''
    yearn = int(year) if year else 1900
    era = '고전 (1850–1910)' if yearn < 1911 else ('근대 (1950–1980)' if yearn < 1981 else '현대 (1990–)')
    endgame = int(plies * 0.72) // 2 * 2 if plies > 60 else None
    exporter = chess.pgn.StringExporter(headers=True, comments=False, variations=False)
    return {
        'id': gid,
        'title': title or f"{h.get('White','?')} vs {h.get('Black','?')}",
        'white': white_ko or h.get('White', '?'),
        'black': black_ko or h.get('Black', '?'),
        'whiteEn': h.get('White', '?'),
        'blackEn': h.get('Black', '?'),
        'event': h.get('Event', '') or 'Unknown',
        'year': year,
        'blurb': blurb or '',
        'opening': opening,
        'eco': eco,
        'era': era,
        'plies': plies,
        'endgamePly': endgame,
        'result': h.get('Result', '*'),
        'pgn': game.accept(exporter),
        'source': source,
    }

def load_games():
    if os.path.exists(GAMES_JSON):
        return json.load(io.open(GAMES_JSON, encoding='utf-8'))
    return []

def save_all(games):
    games.sort(key=lambda g: g['id'])
    json.dump(games, io.open(GAMES_JSON, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # data.js 재생성 (QUOTES 보존)
    old = io.open(DATA_JS, encoding='utf-8').read() if os.path.exists(DATA_JS) else ''
    m = re.search(r'const QUOTES =.*?;\n', old, flags=re.S)
    quotes = m.group(0) if m else 'const QUOTES = [];'
    io.open(DATA_JS, 'w', encoding='utf-8').write(
        '// 유명 명경기 데이터 (운영자 관리 — 관리 절차는 ADMIN_GAMES.md 참고. 전 기보 python-chess 검증)\n'
        'const GAMES = ' + json.dumps(games, ensure_ascii=False, indent=1) + ';\n\n'
        '// 체스 격언 (일부 항목은 의역 포함)\n' + quotes)
    print(f"saved: {len(games)} games -> {GAMES_JSON}\n        -> {DATA_JS}")

def cmd_add(args):
    games = load_games()
    existing_ids = {g['id'] for g in games}
    added = 0
    for path in args.files:
        if not os.path.exists(path):
            print(f"SKIP (파일 없음): {path}")
            continue
        base = os.path.splitext(os.path.basename(path))[0]
        for gi, game in enumerate(parse_games(path)):
            try:
                gid_base = args.id or slugify(args.title or base)
                gid = gid_base if gi == 0 else f"{gid_base}-{gi+1}"
                k = 2
                while gid in existing_ids:
                    gid = f"{gid_base}-{k}"
                    k += 1
                entry = build_entry(game, gid, args.title if gi == 0 and args.title else None,
                                    args.white, args.black, args.blurb if gi == 0 else '',
                                    os.path.basename(path))
                games.append(entry)
                existing_ids.add(gid)
                added += 1
                cut = f" 엔드게임컷@{entry['endgamePly']}" if entry['endgamePly'] else ''
                print(f"ADD {gid}: {entry['plies']}수{cut} | {entry['opening']} | {entry['whiteEn']} vs {entry['blackEn']} ({entry['year']})")
            except ValueError as e:
                print(f"REJECT (검증 실패): {path}#{gi+1} -> {e}")
    if added:
        save_all(games)
        print(f"\n완료: {added}개 추가. 이제 `bash build.sh` 실행 후 index.html을 배포하세요.")
        print("영어 제목/소개가 필요하면 build/app1.js의 TITLE_EN/BLURB_EN에도 추가하세요 (ADMIN_GAMES.md 5단계).")
    else:
        print("추가된 기보가 없습니다.")

def cmd_remove(args):
    games = load_games()
    before = len(games)
    games = [g for g in games if g['id'] != args.game_id]
    if len(games) == before:
        print(f"해당 id 없음: {args.game_id}")
        return
    save_all(games)
    print(f"제거 완료: {args.game_id}. 이제 `bash build.sh` 실행 후 index.html을 배포하세요.")
    print("주의: build/app1.js의 TITLE_EN/BLURB_EN에 남은 번역 항목도 지우면 깔끔합니다.")

def cmd_list(args):
    games = load_games()
    print(f"총 {len(games)}개:")
    for g in games:
        cut = f" 컷@{g['endgamePly']}" if g.get('endgamePly') else ''
        print(f"  {g['id']:34s} {g['plies']:4d}수{cut:10s} | {g['opening']:14s} | {g['whiteEn']} vs {g['blackEn']} ({g['year']})")

def cmd_rebuild(args):
    save_all(load_games())
    print("`bash build.sh`를 실행해 index.html을 다시 만드세요.")

def main():
    p = argparse.ArgumentParser(description='체스놀로지아 기보 관리 (운영자 전용)')
    sub = p.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('add', help='PGN 파일 추가 (검증 포함)')
    a.add_argument('files', nargs='+')
    a.add_argument('--title', default=None, help='표시 제목 (첫 게임에 적용)')
    a.add_argument('--white', default=None, help='백 선수 한글명')
    a.add_argument('--black', default=None, help='흑 선수 한글명')
    a.add_argument('--blurb', default=None, help='한 줄 소개')
    a.add_argument('--id', default=None, help='game id 직접 지정')
    r = sub.add_parser('remove', help='id로 제거')
    r.add_argument('game_id')
    sub.add_parser('list', help='목록 보기')
    sub.add_parser('rebuild', help='data.js만 재생성')
    args = p.parse_args()
    {'add': cmd_add, 'remove': cmd_remove, 'list': cmd_list, 'rebuild': cmd_rebuild}[args.cmd](args)

if __name__ == '__main__':
    main()
