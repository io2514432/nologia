-- v2.9: 빌트인 기보 정보 수정(오버라이드) 테이블
create table if not exists game_edits (
  game_id text primary key,
  data jsonb not null default '{}'::jsonb,
  updated_at timestamptz default now()
);

alter table game_edits enable row level security;

drop policy if exists "game_edits read" on game_edits;
create policy "game_edits read" on game_edits for select using (true);

drop policy if exists "game_edits admin write" on game_edits;
create policy "game_edits admin write" on game_edits for all
  using (exists (select 1 from admins a where a.user_id = auth.uid()))
  with check (exists (select 1 from admins a where a.user_id = auth.uid()));
