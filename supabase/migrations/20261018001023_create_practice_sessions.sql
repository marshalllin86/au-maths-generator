create table public.practice_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  topic text not null check (topic in (
    'integer_add_subtract',
    'integer_multiply_divide',
    'fraction_add',
    'fraction_subtract',
    'fraction_multiply',
    'fraction_divide',
    'percent_add',
    'percent_subtract',
    'percent_multiply',
    'percent_divide',
    'decimal_add',
    'decimal_subtract',
    'decimal_multiply',
    'decimal_divide'
  )),
  practice_date date not null default current_date,
  score smallint not null,
  total_questions smallint not null default 30,
  created_at timestamptz not null default now(),
  constraint practice_sessions_question_count_check
    check (total_questions = 30),
  constraint practice_sessions_score_check
    check (score >= 0 and score <= total_questions)
);

create index practice_sessions_user_date_idx
  on public.practice_sessions (user_id, practice_date desc, created_at desc);

alter table public.practice_sessions enable row level security;

grant select, insert on table public.practice_sessions to authenticated;

create policy practice_sessions_select_own
  on public.practice_sessions
  for select
  to authenticated
  using ((select auth.uid()) = user_id);

create policy practice_sessions_insert_own
  on public.practice_sessions
  for insert
  to authenticated
  with check ((select auth.uid()) = user_id);
