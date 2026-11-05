-- ExamForge AI - Cloudflare D1 Database Schema
-- Run this in Cloudflare Dashboard D1 Console or via: npx wrangler d1 execute examforge-db --file=./schema.sql

CREATE TABLE IF NOT EXISTS schools (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    principal_name TEXT DEFAULT 'Principal',
    phone_number TEXT DEFAULT '+923215423874',
    subscription_status TEXT DEFAULT 'active',
    quota TEXT DEFAULT 'Unlimited',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    school_id TEXT REFERENCES schools(id) ON DELETE CASCADE,
    username TEXT UNIQUE NOT NULL,
    email TEXT,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'school_admin',
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed initial default schools
INSERT OR IGNORE INTO schools (id, name, principal_name, phone_number, subscription_status, quota)
VALUES 
('pms-school', 'Peshawar Model School', 'Director Academics', '+923215423874', 'active', 'Unlimited'),
('ics-school', 'Islamia College School & College Peshawar', 'Prof. Tariq Khan', '+923215423874', 'active', 'Unlimited'),
('nomankhan-school', 'Government Primary School Ganapur', 'Headmaster', '+923215423874', 'active', 'Unlimited');

-- Default accounts (passwords hashed or plain fallback)
INSERT OR IGNORE INTO users (id, school_id, username, email, password_hash, role, is_active)
VALUES
('u-pms', 'pms-school', 'pms', 'pms@examforge.pk', '123', 'school_admin', 1),
('u-ics', 'ics-school', 'ics', 'ics@examforge.pk', '456', 'school_admin', 1),
('u-nomankhan', 'nomankhan-school', 'nomankhan', 'nomankhan@examforge.pk', '123', 'school_admin', 1);
