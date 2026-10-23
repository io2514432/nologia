-- 체스놀로지아 v1.9 서버 스키마 (Supabase SQL Editor에서 1회 실행)
-- 기존 1.8 스키마에 이어서 붙이면 됩니다. 모두 idempotent.

-- 1) 도전 기록: 기기 간 중복 업로드 방지 ------------------------------------
alter table attempts add column if not exists client_ts bigint;

create unique index if not exists attempts_user_game_ts
  on attempts (user_id, game_id, client_ts)
  where user_id is not null and client_ts is not null;

-- 2) 플레이어 프로필(책갈피·설정·연속기록·활동 달력) --------------------------
alter table players add column if not exists data jsonb;

-- 3) 서버에서 추가하는 기보 --------------------------------------------------
create table if not exists games (
  id          text primary key,
  title       text not null,
  white       text not null,
  black       text not null,
  blurb       text,
  year        text,
  event       text,
  opening     text,
  eco         text,
  result      text,
  pgn         text not null,
  plies       int,
  active      boolean default true,
  created_by  uuid references auth.users(id) on delete set null,
  created_at  timestamptz default now()
);
alter table games enable row level security;

drop policy if exists "anyone reads games" on games;
create policy "anyone reads games" on games for select using (true);

-- 4) 날짜별 일일 게임 지정 ---------------------------------------------------
create table if not exists daily_picks (
  day         date primary key,
  game_id     text not null,
  created_by  uuid references auth.users(id) on delete set null,
  created_at  timestamptz default now()
);
alter table daily_picks enable row level security;

drop policy if exists "anyone reads daily" on daily_picks;
create policy "anyone reads daily" on daily_picks for select using (true);

-- 5) 관리자 명단 -------------------------------------------------------------
create table if not exists admins (
  user_id     uuid primary key references auth.users(id) on delete cascade,
  created_at  timestamptz default now()
);
alter table admins enable row level security;

drop policy if exists "self reads admins" on admins;
create policy "self reads admins" on admins for select using (auth.uid() = user_id);

-- 관리자 여부 판정 함수(RLS 재귀 방지용 security definer)
create or replace function public.is_admin()
returns boolean language sql stable security definer set search_path = public as $$
  select exists (select 1 from admins where user_id = auth.uid())
$$;

-- 6) 쓰기 권한: 관리자만 ------------------------------------------------------
drop policy if exists "admin writes games" on games;
create policy "admin writes games" on games for all
  using (public.is_admin()) with check (public.is_admin());

drop policy if exists "admin writes daily" on daily_picks;
create policy "admin writes daily" on daily_picks for all
  using (public.is_admin()) with check (public.is_admin());

-- 7) 관리자 지정 -------------------------------------------------------------
-- (1) 앱에서 평소처럼 회원가입/로그인한 뒤, 아래를 실행:
-- insert into admins (user_id)
-- select id from auth.users where email = 'YOU@EXAMPLE.COM'
-- on conflict do nothing;
--
-- (2) 확인:
-- select u.email, a.created_at from admins a join auth.users u on u.id = a.user_id;
--
-- ※ admins 테이블에는 insert 정책이 없습니다. 즉 앱(anon key)으로는 관리자를
--   늘릴 수 없고, SQL Editor(또는 service_role)에서만 가능합니다. 의도된 설계입니다.

-- 8) 확인 쿼리 ---------------------------------------------------------------
-- select count(*) from attempts;
-- select count(*) from attempts where client_ts is null;
-- select * from daily_picks order by day desc limit 7;
