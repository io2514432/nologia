-- ============================================================
-- 체스놀로지아 v2.1 · 퍼즐(하이라이트) 구간
-- Supabase SQL Editor에서 실행하세요. (v2.0.sql 이후)
-- ============================================================

alter table public.games add column if not exists puzzle_start int;
alter table public.games add column if not exists puzzle_end   int;

-- 퍼즐 구간은 start < end 이고, 1 이상이어야 합니다.
-- (수 번호는 ply 기준: 1 = 백의 첫 수)
