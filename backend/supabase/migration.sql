create table if not exists public.current_documents (
  user_id uuid primary key references auth.users(id) on delete cascade,
  document_id text not null,
  filename text not null,
  storage_path text not null,
  document_data jsonb not null,
  updated_at timestamptz not null default now()
);

create table if not exists public.vocabulary (
  id text primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  word text not null,
  lemma text not null,
  part_of_speech text not null,
  plural text not null default '',
  translation text not null,
  example_sentence text not null,
  source_page integer,
  created_at timestamptz not null default now()
);

create unique index if not exists vocabulary_user_word_unique
on public.vocabulary (user_id, lower(lemma), lower(part_of_speech));

create table if not exists public.full_translations (
  user_id uuid primary key references auth.users(id) on delete cascade,
  document_id text not null,
  payload jsonb not null,
  updated_at timestamptz not null default now()
);

alter table public.current_documents enable row level security;
alter table public.vocabulary enable row level security;
alter table public.full_translations enable row level security;

drop policy if exists "Users manage own current document" on public.current_documents;
create policy "Users manage own current document"
on public.current_documents for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists "Users manage own vocabulary" on public.vocabulary;
create policy "Users manage own vocabulary"
on public.vocabulary for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists "Users manage own translations" on public.full_translations;
create policy "Users manage own translations"
on public.full_translations for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

insert into storage.buckets (id, name, public)
values ('pdfs', 'pdfs', false)
on conflict (id) do update set public = false;

drop policy if exists "Users manage own PDFs" on storage.objects;
create policy "Users manage own PDFs"
on storage.objects for all
using (
  bucket_id = 'pdfs'
  and (storage.foldername(name))[1] = auth.uid()::text
)
with check (
  bucket_id = 'pdfs'
  and (storage.foldername(name))[1] = auth.uid()::text
);
