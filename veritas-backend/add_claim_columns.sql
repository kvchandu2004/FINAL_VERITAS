-- Migration: Add claim verification columns to manuscripts table
-- Run this if the table already exists and needs the new columns

ALTER TABLE manuscripts
    ADD COLUMN IF NOT EXISTS claim_verification JSON DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS consistency_score FLOAT DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS claim_flagged TINYINT(1) DEFAULT 0;
