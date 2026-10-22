# 체스놀로지아 온라인 연결 가이드 (Supabase) — 초보자용

> 이 가이드만 따라 하면 **전 세계 통계·랭킹**이 켜집니다. 소요 시간 약 15분, 무료예요.
> 연결하지 않아도 앱은 지금처럼 완전히 작동합니다 (연결은 선택사항이에요).

---

## 1. Supabase 가입하고 프로젝트 만들기 (5분)

1. 브라우저에서 `supabase.com` 접속 → 오른쪽 위 **Start your project** (또는 Sign in)
2. **Continue with GitHub** 선택 → 깃허브 로그인 (이미 만든 그 계정이면 끝!)
3. **New project** 클릭
   - Name: `chessnologia`
   - Database Password: 아무거나 강하게 → **잘 적어두세요** (다시 안 보여줘요)
   - Region: `Seoul` 없으면 `Tokyo` 또는 `Singapore`
   - 요금제: **Free** (그대로)
4. 생성까지 2분 정도 기다립니다 (왕관 모양이 로딩됩니다)

## 2. 표 만들기 — SQL 붙여넣기 (3분)

1. 왼쪽 메뉴에서 **SQL** 아이콘 (연필 모양) 클릭 → **New query**
2. 아래 SQL 전체를 복사해서 붙여넣고 → **Run** (또는 Ctrl+Enter)
3. "Success"가 뜨면 끝!

```sql
-- 1) 플레이어
create table if not exists players (
  id uuid primary key references auth.users(id) on delete cascade,
  name text not null,
  created_at timestamptz default now()
);
alter table players enable row level security;
create policy "anyone reads players" on players for select using (true);
create policy "owner inserts players" on players for insert with check (auth.uid() = id);
create policy "owner updates players" on players for update using (auth.uid() = id);

-- 2) 도전 기록 (수별 성공/실패 포함)
create table if not exists attempts (
  id bigint generated always as identity primary key,
  user_id uuid references auth.users(id) on delete cascade,
  game_id text not null,
  acc numeric not null,
  ms bigint not null,
  grade text,
  mode text,
  hint boolean default false,
  moves text,
  created_at timestamptz default now()
);
alter table attempts enable row level security;
create policy "anyone reads attempts" on attempts for select using (true);
create policy "owner inserts attempts" on attempts for insert with check (auth.uid() = user_id);

-- 3) 게임별 요약 (전체 성공률 자동 계산)
create or replace view game_stats as
select game_id,
  count(*) as attempts,
  sum(case when acc >= 100 then 1 else 0 end) as perfects,
  round(100.0 * sum(case when acc >= 100 then 1 else 0 end) / count(*), 1) as success_pct,
  min(case when acc >= 100 then ms end) as best_ms
from attempts
group by game_id;
```

## 3. 주소와 키 복사하기 (2분)

1. 왼쪽 맨 아래 **톱니바퀴(Settings)** → **API**
2. 두 가지를 복사합니다:
   - **Project URL** — `https://abcd1234.supabase.co` 같은 것
   - **anon public** 키 — 아주 긴 문자열 (`Project API Keys` 박스 안에 있어요)

## 4. 앱에 붙여넣기 (2분)

1. 체스놀로지아 앱 → **설정** 탭
2. **온라인 (전체 통계·랭킹)** 카드에 URL과 anon key를 각각 붙여넣기 → **연결**
3. 바로 아래에 이메일/비밀번호/표시 이름 입력 → **회원가입**
   - Supabase가 보내온 **확인 메일**이 오면 메일함에서 링크 클릭 (안 오면 스팸함 확인)
   - 확인 메일 없이 바로 쓰고 싶으면: Supabase 왼쪽 메뉴 **Authentication → Sign In / Providers → Email**에서 "Confirm email" 끄기
4. 다시 **로그인** → 끝! 이제부터 도전 기록이 자동으로 올라갑니다

## 5. 뭘 바뀌는지

- 라이브러리의 성공률 배지가 **"전체 43.2% · 128"** 식으로 바뀝니다 (전체 사용자 기준 + 총 시도 수)
- 기보 검토 화면에 **"가장 많이 틀리는 수: 24.Qb3!! 성공률 45% (7/15)"** 표시 — 사람들이 어디서 넘어지는지 보여줘요
- 랭킹 데이터가 쌓여서, 다음 단계에 진짜 스피드 랭킹으로 연결됩니다

## 문제 해결

| 증상 | 해결 |
|---|---|
| "Invalid API key" | anon 키를 다시 복사 (URL이 아니라 키!) |
| 로그인이 안 돼요 | 이메일 확인을 안 했을 수 있어요 — 메일함/스팸함 확인 |
| 배지가 그대로예요 | 통계는 1시간 간격으로 갱신됩니다. 도전 하나 하고 새로고침해 보세요 |
| 연결 해제하고 싶어요 | 설정 → 연결 해제. 기록은 앱 안에 그대로 남아요 |

## 돈이 나가요?

- 무료(Free) 플랜이면 월 $0. 이 앱 수준(기록 수천 건)에서는 몇 년은 여유롭게 커버됩니다.
- 유저가 아주 많아지면 그때 유료($25/월)로 올리는 식이에요.
