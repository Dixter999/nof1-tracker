-- NOF1 Tracker Database Initialization
-- This script runs automatically when PostgreSQL container starts fresh
-- Creates enum types used throughout the application

-- Season status enum: tracks the lifecycle of a trading season
CREATE TYPE season_status AS ENUM ('active', 'completed', 'cancelled');

-- Trade side enum: indicates direction of a trade
CREATE TYPE trade_side AS ENUM ('long', 'short');

-- Trade status enum: tracks the lifecycle of individual trades
CREATE TYPE trade_status AS ENUM ('open', 'closed', 'liquidated');

-- Chat decision enum: represents AI/chat-based trading decisions
CREATE TYPE chat_decision AS ENUM ('buy', 'sell', 'hold', 'close', 'none');
