-- ============================================================
-- 체스놀로지아 v2.0 · 폴더 · 기보 숨김(삭제) · 게임별 극한 랭킹
-- Supabase Dashboard → SQL Editor 에서 한 번 실행하세요.
-- 선행 조건: v1.9.sql 실행 완료(is_admin() 함수 필요)
-- ============================================================

-- 1) 기보 메타데이터: 폴더 / 숨김 / 정렬
create table if not exists public.game_meta (
  game_id   text primary key,
  folder    text,
  hidden    boolean not null default false,
  sort      int,
  updated_at timestamptz not null default now()
);

alter table public.game_meta enable row level security;

drop policy if exists "game_meta read" on public.game_meta;
create policy "game_meta read" on public.game_meta
  for select using (true);

drop policy if exists "game_meta admin write" on public.game_meta;
create policy "game_meta admin write" on public.game_meta
  for all using (public.is_admin()) with check (public.is_admin());

grant select on public.game_meta to anon, authenticated;
grant insert, update, delete on public.game_meta to authenticated;

-- 2) 게임별 극한 랭킹 조회용 인덱스 (게임 · 모드 · 시간)
create index if not exists attempts_game_extreme_idx
  on public.attempts (game_id, mode, ms)
  where acc = 100;

-- 3) 확인용
-- select * from public.game_meta order by folder nulls last;
-- select game_id, count(*) from public.attempts where mode='extreme' and acc=100 group by 1;
