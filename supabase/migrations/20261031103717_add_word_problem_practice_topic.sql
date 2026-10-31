alter table public.practice_sessions
  drop constraint if exists practice_sessions_topic_check;

alter table public.practice_sessions
  add constraint practice_sessions_topic_check
  check (topic in (
    'integer_add_subtract',
    'integer_multiply_divide',
    'fraction_add',
    'fraction_subtract',
    'fraction_multiply',
    'fraction_divide',
    'fraction_two_four_operations',
    'fraction_three_multiply_divide',
    'percent_add',
    'percent_subtract',
    'percent_multiply',
    'percent_divide',
    'decimal_add',
    'decimal_subtract',
    'decimal_multiply',
    'decimal_divide',
    'unit_conversion',
    'word_problems'
  ));
