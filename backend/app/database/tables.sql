create extension if not exists "uuid-ossp";

-- 1. THE USERS TABLE
create table public.users (
    user_id text primary key,
    name text not null,
    email text unique not null,
    language_preference text default 'en',
    query_count integer default 0,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 2. SUGGESTED QUESTIONS BANK
create table public.question_bank (
    id uuid default gen_random_uuid() primary key,
    category text not null,
    question text not null,
    language text not null default 'en',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 3. THE HISTORY STORAGE
create table public.chat_history (
    id uuid default gen_random_uuid() primary key,
    user_id text references public.users(user_id) on delete cascade,
    question text not null,
    answer text not null,
    source_type text not null,
    source_name text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 4. MEASUREMENT FOR VISITS
create table public.query_usage (
    id uuid default gen_random_uuid() primary key,
    user_id text references public.users(user_id) on delete cascade,
    action_type text not null,
    tokens_used integer default 0,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 5. FUTURE ROADMAP PAYMENTS
create table public.future_payments (
    id uuid default gen_random_uuid() primary key,
    user_id text references public.users(user_id),
    amount numeric(10, 2) not null,
    currency text default 'INR',
    status text not null,
    razorpay_order_id text,
    razorpay_payment_id text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- TRANSACTION BLOCK: This acts like a ticket counter queue line. 
-- Only one request can step forward at a time, completely removing user query race bugs!
create or replace function public.increment_user_query_count(target_user_id text, max_limit integer)
returns json as $$
declare
    current_count integer;
begin
    select query_count into current_count 
    from public.users 
    where user_id = target_user_id 
    for update;

    if not found then
        return json_build_object('success', false, 'error', 'No registration data matched.');
    end if;

    if current_count >= max_limit then
        return json_build_object('success', true, 'limit_reached', true, 'new_count', current_count);
    else
        update public.users 
        set query_count = query_count + 1 
        where user_id = target_user_id;
        
        return json_build_object('success', true, 'limit_reached', false, 'new_count', current_count + 1);
    end if;
end;
$$ language plpgsql security definer;

-- Insert seed data questions
insert into public.question_bank (category, question, language) values
('banking', 'What is FD?', 'en'),
('banking', 'What is RD?', 'en'),
('banking', 'What is UPI?', 'en'),
('banking', 'फिक्स्ड डिपॉजिट (FD) क्या होता है?', 'hi'),
('banking', 'यूपीआई (UPI) क्या है?', 'hi'),
('government_schemes', 'What is PMJDY?', 'en'),
('government_schemes', 'What is PM Mudra Loan?', 'en'),
('government_schemes', 'What is APY?', 'en'),
('government_schemes', 'पीएम किसान योजना क्या है?', 'hi'),
('stock_market', 'What is SIP?', 'en'),
('stock_market', 'What is IPO?', 'en'),
('stock_market', 'What is NIFTY?', 'en'),
('stock_market', 'एसआईपी (SIP) क्या होता है?', 'hi');
