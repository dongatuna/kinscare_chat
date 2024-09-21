-- Users table
CREATE TABLE IF NOT EXISTS kinscare_chat.users (
    user_id SERIAL PRIMARY KEY,
    ext_user_id TEXT,
    settings JSONB DEFAULT '{"share_emails":[]}'
);


-- Facebook credentials table
CREATE TABLE IF NOT EXISTS kinscare_chat.fb_creds (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES kinscare_chat.users(user_id),
    access_token TEXT NOT NULL,
    token_type VARCHAR(50),
    expires_in INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Instagram credentials table
CREATE TABLE IF NOT EXISTS kinscare_chat.ig_creds (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES kinscare_chat.users(user_id),
    access_token TEXT NOT NULL,
    token_type VARCHAR(50),
    expires_in INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Programs table
CREATE TABLE IF NOT EXISTS kinscare_chat.programs (
    program_id SERIAL PRIMARY KEY,
    program_data JSONB NOT NULL
);

-- Saved programs table
CREATE TABLE IF NOT EXISTS kinscare_chat.saved_programs (
    saved_prog_id SERIAL PRIMARY KEY,
    program_id INT NOT NULL REFERENCES kinscare_chat.programs(program_id)
);

-- Plans table
CREATE TABLE IF NOT EXISTS kinscare_chat.plans (
    plan_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES kinscare_chat.users(user_id),
    saved_prog_id INT NOT NULL REFERENCES kinscare_chat.saved_programs(saved_prog_id),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
