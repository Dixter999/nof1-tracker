-- =============================================================================
-- NOF1 Tracker Database Initialization
-- =============================================================================
--
-- This script runs automatically when the PostgreSQL container starts with
-- an empty data volume. It creates the enum types used throughout the
-- application for type-safe status tracking.
--
-- Note: This script is idempotent - it can be run multiple times without error
-- by using IF NOT EXISTS or DO blocks where applicable.
--
-- =============================================================================

-- Create enum types with error handling for idempotency
-- PostgreSQL 9.1+ supports CREATE TYPE IF NOT EXISTS via DO block

-- Season status enum: tracks the lifecycle of a trading season
-- - active: Season is currently running
-- - completed: Season finished normally
-- - cancelled: Season was terminated early
DO $$ BEGIN
    CREATE TYPE season_status AS ENUM ('active', 'completed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- Trade side enum: indicates direction of a trade
-- - long: Betting on price increase
-- - short: Betting on price decrease
DO $$ BEGIN
    CREATE TYPE trade_side AS ENUM ('long', 'short');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- Trade status enum: tracks the lifecycle of individual trades
-- - open: Trade is currently active
-- - closed: Trade was closed normally
-- - liquidated: Trade was force-closed due to margin requirements
DO $$ BEGIN
    CREATE TYPE trade_status AS ENUM ('open', 'closed', 'liquidated');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- Chat decision enum: represents AI/chat-based trading decisions
-- - buy: Open a long position
-- - sell: Open a short position
-- - hold: Maintain current position
-- - close: Close existing position
-- - none: No action recommended
DO $$ BEGIN
    CREATE TYPE chat_decision AS ENUM ('buy', 'sell', 'hold', 'close', 'none');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- Log successful initialization
DO $$ BEGIN
    RAISE NOTICE 'NOF1 Tracker enum types initialized successfully';
END $$;
