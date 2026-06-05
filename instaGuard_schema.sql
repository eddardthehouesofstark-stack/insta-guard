-- =============================================
-- InstaGuard: Supabase Schema
-- Run this in: Supabase > SQL Editor > New query
-- =============================================


-- 1. USERS (extends Supabase auth.users)
create table public.users (
  id         uuid primary key references auth.users(id) on delete cascade,
  email      text not null,
  role       text not null default 'user' check (role in ('user', 'admin')),
  created_at timestamptz not null default now()
);

-- Trigger: auto-create profile row on signup
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer as $$
begin
  insert into public.users (id, email)
  values (new.id, new.email);
  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();


-- 2. IMAGE_CHECKS
create table public.image_checks (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid references public.users(id) on delete cascade,
  image_url    text,
  safety_score int not null check (safety_score between 0 and 100),
  status       text not null default 'pending'
               check (status in ('approved', 'manual_review', 'rejected', 'pending')),
  vision_labels jsonb,          -- raw labels/scores from Google Vision API
  checked_at   timestamptz not null default now()
);


-- 3. FEED_ANALYSES
create table public.feed_analyses (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid references public.users(id) on delete cascade,
  feed_snapshot  jsonb,         -- array of post objects from mock/real feed
  overall_score  int not null check (overall_score between 0 and 100),
  status         text not null default 'pending'
                 check (status in ('approved', 'manual_review', 'rejected', 'pending')),
  analysed_at    timestamptz not null default now()
);


-- 4. MODERATION_QUEUE
-- ref_type tells you whether ref_id points to image_checks or feed_analyses
create table public.moderation_queue (
  id            uuid primary key default gen_random_uuid(),
  ref_id        uuid not null,  -- FK to image_checks.id or feed_analyses.id
  ref_type      text not null check (ref_type in ('image', 'feed')),
  score         int not null,
  decision      text check (decision in ('approved', 'rejected', null)),
  reviewer_note text,
  reviewed_at   timestamptz
);


-- 5. THRESHOLDS (admin-configurable; single row)
create table public.thresholds (
  id                uuid primary key default gen_random_uuid(),
  auto_approve_max  int not null default 49,  -- score <= this → auto-approved
  manual_review_min int not null default 50,  -- score >= this → manual review
  auto_reject_min   int not null default 80,  -- score >= this → auto-rejected
  updated_at        timestamptz not null default now()
);

-- Seed the default threshold row
insert into public.thresholds (auto_approve_max, manual_review_min, auto_reject_min)
values (49, 50, 80);


-- 6. ADMIN_LOGS
create table public.admin_logs (
  id         uuid primary key default gen_random_uuid(),
  admin_id   uuid references public.users(id) on delete set null,
  action     text not null,    -- e.g. 'threshold_update', 'manual_review_decision'
  payload    jsonb,
  logged_at  timestamptz not null default now()
);


-- 7. FEED_REBOOT_REQUESTS
create table public.feed_reboot_requests (
  id                 uuid primary key default gen_random_uuid(),
  user_id            uuid references public.users(id) on delete cascade,
  instagram_username text not null,
  post_ids           jsonb,        -- array of flagged post IDs
  flagged_count      int not null,
  status             text not null default 'pending' check (status in ('pending', 'approved', 'rejected')),
  requested_at       timestamptz not null default now(),
  approved_by        uuid references public.users(id) on delete set null,
  approved_at        timestamptz,
  rejected_by        uuid references public.users(id) on delete set null,
  rejected_at        timestamptz
);


-- =============================================
-- ROW LEVEL SECURITY (RLS)
-- =============================================

-- Enable RLS on all tables
alter table public.users             enable row level security;
alter table public.image_checks      enable row level security;
alter table public.feed_analyses     enable row level security;
alter table public.moderation_queue  enable row level security;
alter table public.thresholds        enable row level security;
alter table public.admin_logs        enable row level security;
alter table public.feed_reboot_requests enable row level security;


-- Helper: check if current user is admin
create or replace function public.is_admin()
returns boolean language sql security definer as $$
  select exists (
    select 1 from public.users
    where id = auth.uid() and role = 'admin'
  );
$$;


-- users: users see only themselves; admins see all
create policy "users_select_own"
  on public.users for select
  using (id = auth.uid() or public.is_admin());

create policy "users_insert_self"
  on public.users for insert
  with check (id = auth.uid());


-- image_checks: users see their own; admins see all
create policy "image_checks_select"
  on public.image_checks for select
  using (user_id = auth.uid() or public.is_admin());

create policy "image_checks_insert"
  on public.image_checks for insert
  with check (user_id = auth.uid());


-- feed_analyses: same pattern
create policy "feed_analyses_select"
  on public.feed_analyses for select
  using (user_id = auth.uid() or public.is_admin());

create policy "feed_analyses_insert"
  on public.feed_analyses for insert
  with check (user_id = auth.uid());


-- moderation_queue: only admins can read/write
create policy "moderation_queue_admin"
  on public.moderation_queue for all
  using (public.is_admin());


-- thresholds: everyone can read; only admins can update
create policy "thresholds_select"
  on public.thresholds for select
  using (true);

create policy "thresholds_update"
  on public.thresholds for update
  using (public.is_admin());


-- admin_logs: only admins
create policy "admin_logs_admin"
  on public.admin_logs for all
  using (public.is_admin());


-- feed_reboot_requests: users see their own; admins see all
create policy "feed_reboot_requests_select"
  on public.feed_reboot_requests for select
  using (user_id = auth.uid() or public.is_admin());

create policy "feed_reboot_requests_insert"
  on public.feed_reboot_requests for insert
  with check (user_id = auth.uid());

create policy "feed_reboot_requests_update"
  on public.feed_reboot_requests for update
  using (public.is_admin());


-- =============================================
-- REALTIME
-- Enable on tables that the frontend subscribes to
-- =============================================

-- Run after the schema is created:
-- Supabase Dashboard > Database > Replication > enable for:
--   public.image_checks
--   public.feed_analyses
--   public.moderation_queue
--   public.thresholds

-- Or via SQL:
alter publication supabase_realtime add table public.image_checks;
alter publication supabase_realtime add table public.feed_analyses;
alter publication supabase_realtime add table public.moderation_queue;
alter publication supabase_realtime add table public.thresholds;


-- =============================================
-- SEED ADMIN USER
-- After signup, promote a user to admin manually:
-- update public.users set role = 'admin' where email = 'your@email.com';
-- =============================================
