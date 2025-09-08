-- Initialize the database with some basic setup
-- This file is executed when the PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for better performance
-- These will be created after the tables are created by the application

-- Set timezone
SET timezone = 'UTC';
