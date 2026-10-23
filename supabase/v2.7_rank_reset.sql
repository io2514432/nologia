-- v2.7: 기존 랭킹(극한 모드 100% 기록) 일괄 초기화
-- Supabase > SQL Editor 에서 1회 실행하세요.

delete from attempts where mode = 'extreme';
