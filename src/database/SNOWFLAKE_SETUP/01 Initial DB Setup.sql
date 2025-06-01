-- ---------------------------------------------------------------------------------
-- 1. Create Database and Schema
-- ---------------------------------------------------------------------------------

-- Create and use database
CREATE DATABASE IF NOT EXISTS ROOTS_ROUTES;
USE DATABASE ROOTS_ROUTES;

-- Create and use schema
CREATE SCHEMA IF NOT EXISTS PUBLIC;
USE SCHEMA PUBLIC;

-- Grant privileges
GRANT USAGE ON DATABASE ROOTS_ROUTES TO ROLE PUBLIC;
GRANT USAGE ON SCHEMA PUBLIC TO ROLE PUBLIC;

-- ---------------------------------------------------------------------------------
-- 2. Create Tables and Views (Create Core Tables)
-- ---------------------------------------------------------------------------------

-- Heritage Sites Table: Stores information about heritage sites
CREATE TABLE HERITAGE_SITES (
    site_id NUMBER AUTOINCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    story TEXT,
    location VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    state VARCHAR(100),
    city VARCHAR(100),
    established_year INTEGER,
    heritage_type VARCHAR(50),
    unesco_status BOOLEAN,
    risk_level VARCHAR(20),
    health_index DECIMAL(3, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Art Forms Table: Stores information about traditional art forms
CREATE TABLE IF NOT EXISTS ART_FORMS (
    art_form_id NUMBER AUTOINCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    origin_state VARCHAR(100),
    category VARCHAR(50),
    risk_level VARCHAR(20),
    practitioners_count NUMBER,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Cultural Events Table: Stores information about cultural events
CREATE TABLE IF NOT EXISTS CULTURAL_EVENTS (
    event_id NUMBER AUTOINCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    location VARCHAR(255),
    event_type VARCHAR(50),
    organizer VARCHAR(255),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Visitor Statistics Table: Tracks visitor data for heritage sites
CREATE TABLE IF NOT EXISTS VISITOR_STATS (
    stat_id NUMBER AUTOINCREMENT PRIMARY KEY,
    site_id NUMBER NOT NULL,
    visit_date DATE,
    visitor_count NUMBER,
    revenue FLOAT,
    season VARCHAR(20),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (site_id) REFERENCES HERITAGE_SITES(site_id)
);

-- User Interactions Table: Stores user reviews and interactions
CREATE TABLE IF NOT EXISTS USER_INTERACTIONS (
    interaction_id NUMBER AUTOINCREMENT PRIMARY KEY,
    user_id VARCHAR(100),
    site_id NUMBER NOT NULL,
    interaction_type VARCHAR(50),
    interaction_date TIMESTAMP_NTZ,
    rating NUMBER,
    review TEXT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (site_id) REFERENCES HERITAGE_SITES(site_id)
);

-- Site Art Forms Mapping Table: Links heritage sites with art forms
CREATE TABLE IF NOT EXISTS SITE_ART_FORMS (
    site_id NUMBER NOT NULL,
    art_form_id NUMBER NOT NULL,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (site_id, art_form_id),
    FOREIGN KEY (site_id) REFERENCES HERITAGE_SITES(site_id),
    FOREIGN KEY (art_form_id) REFERENCES ART_FORMS(art_form_id)
);

-- ---------------------------------------------------------------------------------------
-- 3. Create Views for Analytics
-- ---------------------------------------------------------------------------------------

-- Heritage Health Index View: Provides health index and risk level information
CREATE OR REPLACE VIEW HERITAGE_HEALTH_INDEX AS
SELECT
    site_id,
    name,
    health_index,
    risk_level,
    state,
    city
FROM HERITAGE_SITES
ORDER BY health_index DESC;

-- Seasonal Visitor Stats View: Analyzes visitor patterns by season
CREATE OR REPLACE VIEW SEASONAL_VISITOR_STATS AS
SELECT
    hs.site_id,
    hs.name,
    vs.season,
    SUM(vs.visitor_count) as total_visitors,
    AVG(vs.visitor_count) as avg_visitors,
    SUM(vs.revenue) as total_revenue
FROM HERITAGE_SITES hs
JOIN VISITOR_STATS vs ON hs.site_id = vs.site_id
GROUP BY hs.site_id, hs.name, vs.season
ORDER BY total_visitors DESC;

-- ------------------------------------------------------------------------------------
-- 4. Create Stored Procedures
-- ------------------------------------------------------------------------------------

-- Procedure to update health index for a site
CREATE OR REPLACE PROCEDURE UPDATE_HEALTH_INDEX(site_id FLOAT)
RETURNS STRING
LANGUAGE JAVASCRIPT
AS
$$
    // Implementation for health index calculation
    return "Health index updated successfully";
$$;

-- Procedure to calculate risk level for a site
CREATE OR REPLACE PROCEDURE CALCULATE_RISK_LEVEL(site_id FLOAT)
RETURNS STRING
LANGUAGE JAVASCRIPT
AS
$$
    // Implementation for risk level calculation
    return "Risk level calculated successfully";
$$;
