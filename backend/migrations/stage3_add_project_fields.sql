-- Stage 3: Add new fields to projects table
-- Migration: stage3_add_project_fields
-- Date: 2025-11-30
-- Description: Adds color, icon, is_default, and sort_order fields for project customization

-- Add color field (default: blue)
ALTER TABLE projects ADD COLUMN color VARCHAR(20) DEFAULT 'blue' NOT NULL;

-- Add icon field (default: folder)
ALTER TABLE projects ADD COLUMN icon VARCHAR(20) DEFAULT 'folder' NOT NULL;

-- Add is_default flag (default: false)
-- SQLite uses INTEGER for booleans (0 = false, 1 = true)
ALTER TABLE projects ADD COLUMN is_default INTEGER DEFAULT 0 NOT NULL;

-- Add sort_order field (default: 0)
ALTER TABLE projects ADD COLUMN sort_order INTEGER DEFAULT 0 NOT NULL;

-- Create index on sort_order for efficient ordering
CREATE INDEX IF NOT EXISTS idx_projects_sort_order ON projects(sort_order);

-- Ensure default project exists
-- Find first project or create one
INSERT OR IGNORE INTO projects (id, name, description, color, icon, is_default, sort_order, created_at, updated_at)
SELECT 1, 'Default', 'Default project for quick chats', 'gray', 'folder', 1, 0,
       CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM projects WHERE is_default = 1);

-- Update existing "Default Project" to be marked as default
UPDATE projects
SET is_default = 1,
    color = 'gray',
    icon = 'folder'
WHERE name = 'Default Project'
  AND is_default = 0;

-- Backfill sort_order for existing projects (order by created_at)
UPDATE projects
SET sort_order = (
    SELECT COUNT(*)
    FROM projects p2
    WHERE p2.created_at < projects.created_at
      AND p2.deleted_at IS NULL
)
WHERE deleted_at IS NULL;

-- Verify migration
SELECT 'Migration complete. Projects table schema:' AS status;
PRAGMA table_info(projects);
