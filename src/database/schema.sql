-- =============================================
-- CORE TABLES
-- =============================================

-- Heritage Sites Table
CREATE TABLE HERITAGE_SITES (
    id SERIAL PRIMARY KEY,
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

-- Art Forms Table
CREATE TABLE ART_FORMS (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    origin_state VARCHAR(100),
    category VARCHAR(50),
    risk_level VARCHAR(20),
    practitioners_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cultural Events Table
CREATE TABLE CULTURAL_EVENTS (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    location VARCHAR(255),
    event_type VARCHAR(50),
    organizer VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Visitor Statistics Table
CREATE TABLE VISITOR_STATS (
    id SERIAL PRIMARY KEY,
    site_id INTEGER REFERENCES HERITAGE_SITES(id),
    visit_date DATE,
    visitor_count INTEGER,
    revenue DECIMAL(10, 2),
    season VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Interactions Table
CREATE TABLE USER_INTERACTIONS (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50),
    site_id INTEGER REFERENCES HERITAGE_SITES(id),
    interaction_type VARCHAR(50),
    interaction_date TIMESTAMP,
    rating INTEGER,
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Site-Art Form Mappings Table
CREATE TABLE SITE_ART_FORMS (
    id SERIAL PRIMARY KEY,
    site_id INTEGER REFERENCES HERITAGE_SITES(id),
    art_form_id INTEGER REFERENCES ART_FORMS(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- NEW TABLES FOR AI FEATURES
-- =============================================

-- Cultural Heritage Health Score Table
CREATE TABLE HERITAGE_HEALTH_SCORES (
    id SERIAL PRIMARY KEY,
    site_id INTEGER REFERENCES HERITAGE_SITES(id),
    physical_condition_score DECIMAL(3, 2),
    cultural_significance_score DECIMAL(3, 2),
    tourism_impact_score DECIMAL(3, 2),
    community_engagement_score DECIMAL(3, 2),
    overall_health_score DECIMAL(3, 2),
    assessment_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Site Infrastructure Table
CREATE TABLE SITE_INFRASTRUCTURE (
    id SERIAL PRIMARY KEY,
    site_id INTEGER REFERENCES HERITAGE_SITES(id),
    accessibility_score DECIMAL(3, 2),
    accommodation_availability INTEGER,
    transportation_connectivity DECIMAL(3, 2),
    local_community_engagement DECIMAL(3, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cultural Richness Indicators Table
CREATE TABLE CULTURAL_RICHNESS (
    id SERIAL PRIMARY KEY,
    site_id INTEGER REFERENCES HERITAGE_SITES(id),
    local_artisans_count INTEGER,
    traditional_knowledge_preservation DECIMAL(3, 2),
    cultural_event_frequency INTEGER,
    community_participation DECIMAL(3, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tourism Potential Index Table
CREATE TABLE TOURISM_POTENTIAL (
    id SERIAL PRIMARY KEY,
    site_id INTEGER REFERENCES HERITAGE_SITES(id),
    current_visitor_score DECIMAL(3, 2),
    site_significance_score DECIMAL(3, 2),
    infrastructure_readiness DECIMAL(3, 2),
    community_capacity DECIMAL(3, 2),
    preservation_needs DECIMAL(3, 2),
    overall_potential_score DECIMAL(3, 2),
    assessment_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Visitor Profiles Table
CREATE TABLE VISITOR_PROFILES (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50),
    interest_categories JSONB,
    travel_patterns JSONB,
    budget_range JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Site Profiles Table
CREATE TABLE SITE_PROFILES (
    id SERIAL PRIMARY KEY,
    site_id INTEGER REFERENCES HERITAGE_SITES(id),
    cultural_significance_matrix JSONB,
    infrastructure_readiness_score DECIMAL(3, 2),
    community_capacity_assessment DECIMAL(3, 2),
    environmental_impact_rating DECIMAL(3, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Preservation Priorities Table
CREATE TABLE PRESERVATION_PRIORITIES (
    id SERIAL PRIMARY KEY,
    site_id INTEGER REFERENCES HERITAGE_SITES(id),
    risk_assessment_score DECIMAL(3, 2),
    resource_allocation_priority INTEGER,
    implementation_timeline JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- INDEXES
-- =============================================

-- Heritage Sites Indexes
CREATE INDEX idx_heritage_sites_location ON HERITAGE_SITES(location);
CREATE INDEX idx_heritage_sites_state ON HERITAGE_SITES(state);
CREATE INDEX idx_heritage_sites_unesco ON HERITAGE_SITES(unesco_status);

-- Visitor Stats Indexes
CREATE INDEX idx_visitor_stats_site_date ON VISITOR_STATS(site_id, visit_date);
CREATE INDEX idx_visitor_stats_season ON VISITOR_STATS(season);

-- User Interactions Indexes
CREATE INDEX idx_user_interactions_site ON USER_INTERACTIONS(site_id);
CREATE INDEX idx_user_interactions_date ON USER_INTERACTIONS(interaction_date);

-- Health Scores Indexes
CREATE INDEX idx_health_scores_site ON HERITAGE_HEALTH_SCORES(site_id);
CREATE INDEX idx_health_scores_date ON HERITAGE_HEALTH_SCORES(assessment_date);

-- Tourism Potential Indexes
CREATE INDEX idx_tourism_potential_site ON TOURISM_POTENTIAL(site_id);
CREATE INDEX idx_tourism_potential_score ON TOURISM_POTENTIAL(overall_potential_score);

-- Preservation Priorities Indexes
CREATE INDEX idx_preservation_priorities_site ON PRESERVATION_PRIORITIES(site_id);
CREATE INDEX idx_preservation_priorities_risk ON PRESERVATION_PRIORITIES(risk_assessment_score);

-- Add story column to existing HERITAGE_SITES table
ALTER TABLE HERITAGE_SITES ADD COLUMN story TEXT;
