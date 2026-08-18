-- Лічильники копіювань і переглядів карток для сайту-каталогу powerbi-craft.
-- Запустити один раз у SQL Editor проєкту Supabase (або supabase db push).
--
-- Модель безпеки (least privilege):
--   anon може ЛИШЕ вставляти події (insert-only) і читати агрегат copy_counts;
--   сирі рядки copy_events з клієнта не читаються, не оновлюються, не видаляються.

create table public.copy_events (
  id bigint generated always as identity primary key,
  kind text not null check (kind in
    ('marketplace', 'plugin', 'skill-view', 'skill-prompt', 'all-terminal', 'all-prompt')),
  item text not null check (char_length(item) between 1 and 80),
  created_at timestamptz not null default now()
);

comment on table public.copy_events is
  'Анонімні події сайту-каталогу: копіювання install-команд і перегляди карток скілів';

alter table public.copy_events enable row level security;

create policy copy_events_insert_anon on public.copy_events
  for insert to anon, authenticated
  with check (true);

-- Політик select/update/delete немає — RLS закриває їх за замовчуванням;
-- revoke прибирає й дефолтні гранти Supabase (пояс і підтяжки).
revoke select, update, delete on public.copy_events from anon, authenticated;

-- Індекс під агрегат
create index copy_events_kind_item_idx on public.copy_events (kind, item);

-- Публічний агрегат. security_invoker = off СВІДОМО: вʼю виконується від
-- імені власника і обходить RLS, щоб віддавати лише знеособлені суми.
create view public.copy_counts
  with (security_invoker = off) as
  select kind, item, count(*)::bigint as copies
  from public.copy_events
  group by kind, item;

grant select on public.copy_counts to anon, authenticated;
