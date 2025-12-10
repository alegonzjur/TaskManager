-- Migration: Add authentication fields to employees table
-- Run this in your PostgreSQL database

-- Add new columns to employees table
ALTER TABLE employees 
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255),
ADD COLUMN IF NOT EXISTS birth_date DATE,
ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'employee',
ADD COLUMN IF NOT EXISTS last_login TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Update existing employees to have default role
UPDATE employees 
SET role = 'employee' 
WHERE role IS NULL;

-- Create index on email for faster lookups
CREATE INDEX IF NOT EXISTS idx_employees_email ON employees(email);

-- Create index on role
CREATE INDEX IF NOT EXISTS idx_employees_role ON employees(role);

COMMIT;