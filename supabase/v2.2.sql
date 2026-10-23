-- ============================================================
-- 체스놀로지아 v2.2 · 퍼즐 푸는 입장
-- Supabase SQL Editor에서 실행하세요. (v2.1.sql 이후)
-- puzzle_start / puzzle_end 는 '수 번호'(1수 = 백+흑 한 세트) 기준입니다.
-- ============================================================

alter table public.games add column if not exists puzzle_side text;

-- 예: 백 입장 17~20수
-- update public.games set puzzle_start=17, puzzle_end=20, puzzle_side='w' where id='...';
-- 예: 흑 입장 17~20수
-- update public.games set puzzle_start=17, puzzle_end=20, puzzle_side='b' where id='...';
