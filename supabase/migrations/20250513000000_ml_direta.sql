-- ML Direta: schema for cloud deployment (Supabase PostgreSQL)
-- Run this in Supabase SQL Editor or via supabase db push.

-- JSON documents (categories, fields, questions, greetings) — stored as text
-- so key order matches Python dict iteration (jsonb does not preserve key order).
create table if not exists public.ml_json_docs (
  doc_key text primary key,
  body text not null default '{}',
  updated_at timestamptz not null default now()
);

-- Users (same logical model as users.json: string id as primary key).
create table if not exists public.ml_users (
  id text primary key,
  login text not null unique,
  senha text not null,
  nome_completo text,
  tipo text not null check (tipo in ('admin', 'usuario')),
  matricula text,
  tempo_exibicao text,
  created_at text,
  data_cadastro text,
  ativo boolean default true,
  campos_adicionais jsonb not null default '{}'::jsonb
);

create index if not exists idx_ml_users_matricula on public.ml_users (matricula);
create index if not exists idx_ml_users_tipo on public.ml_users (tipo);

-- Answers (one row per legacy answer id; body mirrors each value in answers.json).
create table if not exists public.ml_answers (
  answer_id text primary key,
  body jsonb not null
);

create index if not exists idx_ml_answers_body_user on public.ml_answers ((body->>'user_id'));

comment on table public.ml_json_docs is 'ML Direta: categories, fields, questions, greetings as JSON text';
comment on table public.ml_users is 'ML Direta: users migrated from users.json';
comment on table public.ml_answers is 'ML Direta: Q&A threads migrated from answers.json';

-- Optional: tighten public access (Flask uses service role and bypasses RLS).
alter table public.ml_json_docs enable row level security;
alter table public.ml_users enable row level security;
alter table public.ml_answers enable row level security;

-- Deny anonymous/authenticated dashboard users direct table API access.
create policy "deny anon all ml_json_docs" on public.ml_json_docs for all to anon using (false) with check (false);
create policy "deny authenticated all ml_json_docs" on public.ml_json_docs for all to authenticated using (false) with check (false);

create policy "deny anon all ml_users" on public.ml_users for all to anon using (false) with check (false);
create policy "deny authenticated all ml_users" on public.ml_users for all to authenticated using (false) with check (false);

create policy "deny anon all ml_answers" on public.ml_answers for all to anon using (false) with check (false);
create policy "deny authenticated all ml_answers" on public.ml_answers for all to authenticated using (false) with check (false);
