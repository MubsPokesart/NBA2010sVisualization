

-- BCNF-Normalized schema for NBA data

-- Conferences table:
-- Primary key: conference_id 
-- Simple lookup table for conferences (Eastern/Western)

-- Teams table:
-- Primary key: team_id (autoincrementing)
-- Stores team names and their conference affiliations
-- Foreign key to Conferences table


-- TeamStats table:
-- Primary key: stat_id (autoincrementing)
-- Contains all statistical measures for each team per season
-- Foreign keys to both Teams and Seasons tables
-- Unique constraint on team_id + season_id combination


-- Create Seasons table
CREATE TABLE Seasons (
    season_id TEXT PRIMARY KEY,
    start_year INTEGER,
    end_year INTEGER
);

-- Create Conferences table
CREATE TABLE Conferences (
    conference_id TEXT PRIMARY KEY,
    conference_name TEXT NOT NULL
);

-- Create Teams table
CREATE TABLE Teams (
    team_id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT NOT NULL,
    conference_id TEXT,
    FOREIGN KEY (conference_id) REFERENCES Conferences(conference_id)
);

-- Create TeamStats table
CREATE TABLE TeamStats (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER,
    season_id TEXT,
    average_offensive_rating REAL NOT NULL,
    average_defensive_rating REAL NOT NULL,
    average_net_rating REAL NOT NULL,
    average_plus_minus REAL NOT NULL,
    relative_net_rating REAL NOT NULL,
    relative_offensive_rating REAL NOT NULL,
    relative_defensive_rating REAL NOT NULL,
    FOREIGN KEY (team_id) REFERENCES Teams(team_id),
    FOREIGN KEY (season_id) REFERENCES Seasons(season_id),
    UNIQUE(team_id, season_id)
);

-- Insert basic conference data
INSERT INTO Conferences (conference_id, conference_name) VALUES
('W', 'Western'),
('E', 'Eastern');

-- Create indexes for better query performance
CREATE INDEX idx_teamstats_season ON TeamStats(season_id);
CREATE INDEX idx_teamstats_team ON TeamStats(team_id);
CREATE INDEX idx_teams_conference ON Teams(conference_id);
