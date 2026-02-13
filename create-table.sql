-- Create the table for timelog

CREATE TABLE entries (
  id BIGSERIAL PRIMARY KEY,
  project TEXT NOT NULL,
  category TEXT NOT NULL,
  description TEXT,
  hours NUMERIC(6,2) NOT NULL CHECK (hours > 0),
  date DATE NOT NULL DEFAULT CURRENT_DATE
);
